#!/usr/bin/env python3
"""
Extract main figures from a scientific paper PDF as high-resolution PNGs.

Strategy (gap-based growth, robust for Nature/Cell multi-panel figures):
  1. Locate figure captions (text blocks starting with "Fig. N" / "Figure N" / "图N").
  2. Determine the column span of the caption (single column vs full page width).
  3. Collect every content element above the caption inside that column:
     raster images, vector drawings, and text blocks (panel labels, axis ticks,
     axis titles). Text elements carry their font size.
  4. Grow a region upward from the caption: include elements as long as the
     vertical gap to the current region top is <= --gap (default 12 pt). The
     first larger gap is a column break / body-text boundary -> stop.
     This keeps complete panels (including axis labels below/left of a panel)
     while excluding body text above the figure.
  5. Render the region at high DPI (default 300) to PNG.

Outputs:
    <out>/fig1.png, fig2.png, ...   figure images
    <out>/captions.json             manifest: caption text, page, bbox, status

Usage:
    python extract_figures.py <pdf_path> [--out <dir>] [--dpi 300]
                              [--include-ed] [--gap 12] [--max-height 0.55]

Dependencies: pymupdf  (pip install pymupdf)
"""

import argparse
import json
import os
import re
import sys

try:
    import pymupdf as fitz  # PyMuPDF >= 1.24
except ImportError:
    try:
        import fitz  # older PyMuPDF
    except ImportError:
        print("ERROR: pymupdf not installed. Run: pip install pymupdf")
        sys.exit(1)

CAPTION_RE = re.compile(
    r"^(Fig(ure)?s?\.?\s*\d+|图\s*\d+|Supplementary\s+Fig(ure)?\.?\s*\d+)",
    re.IGNORECASE,
)


def caption_blocks(page):
    """Text blocks whose first line looks like a figure caption."""
    captions = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        lines = block.get("lines", [])
        if not lines:
            continue
        first = "".join(sp["text"] for sp in lines[0].get("spans", [])).strip()
        m = CAPTION_RE.match(first)
        if not m:
            continue
        text = " ".join(
            "".join(sp["text"] for sp in ln.get("spans", [])) for ln in lines
        ).strip()
        if len(text) < 30:  # a caption is at least a sentence
            continue
        captions.append({
            "match": m.group(0),
            "text": text,
            "rect": fitz.Rect(block["bbox"]),
        })
    captions.sort(key=lambda c: c["rect"].y0)
    return captions


def page_graphics(page, header_y):
    """All raster-image and vector-drawing rects on the page (excluding header).

    Publons/Cell Press layouts draw a full-width coloured banner at the very top
    of the page (journal logo + "Article"). Such a banner is a vector drawing
    that starts above `header_y` but is tall enough to survive that cutoff, so
    it is filtered explicitly: wide + short + near the page top = decoration.
    """
    rects = []
    pw, ph = page.rect.width, page.rect.height

    def is_decoration(r):
        # Anything that lives entirely inside the top banner band is page
        # furniture: journal logo, coloured banner, "Article" tag, rules.
        if r.y1 < 0.12 * ph:
            return True
        if r.height < 2 and r.width > 0.7 * pw:   # hairline horizontal rule
            return True
        return False

    for info in page.get_image_info():
        r = fitz.Rect(info["bbox"])
        if r.is_empty or r.width < 3 or r.height < 3:
            continue
        if r.y1 < header_y or is_decoration(r):
            continue
        rects.append(r)

    for d in page.get_drawings():
        r = d["rect"]
        if r.is_empty or r.width < 1 or r.height < 1:
            continue
        if r.y1 < header_y or is_decoration(r):
            continue
        rects.append(r)

    return rects


def build_region(page, caption, prev_caption_bottom, graphics, header_y):
    """Region of the figure that belongs to `caption`.

    Journals place captions in three ways; try them in order:
      A. caption below figure  (most common)
      B. caption beside figure (caption at column top, figure in the other column)
      C. caption above figure  (rare; caption directly above the artwork)
    The figure is anchored on graphics (raster images / vector drawings), then
    compact text blocks (axis labels, panel letters, risk tables) are absorbed.
    """
    cap = caption["rect"]
    win_top = max(header_y, prev_caption_bottom or 0)

    # --- candidate graphic sets ---
    above = [r for r in graphics if r.y1 <= cap.y0 + 2 and r.y0 >= win_top - 2]

    beside = []
    for r in graphics:
        gap_left = cap.x0 - r.x1    # graphic left of caption
        gap_right = r.x0 - cap.x1   # graphic right of caption
        if (0 <= gap_left <= 90) or (0 <= gap_right <= 90):
            beside.append(r)

    below = []
    for r in graphics:
        top_gap = r.y0 - cap.y1
        h_ov = min(r.x1, cap.x1) - max(r.x0, cap.x0)
        if 0 <= top_gap <= 40 and h_ov > 0.2 * min(r.width, cap.width):
            below.append(r)

    chosen, mode = None, None
    if above:
        chosen, mode = above, "above"
    elif beside:
        chosen, mode = beside, "beside"
    elif below:
        chosen, mode = below, "below"

    if not chosen or len(chosen) < 1:
        return None, None

    region = fitz.Rect(chosen[0])
    for r in chosen[1:]:
        region |= r

    if region.height < 20 or region.width < 20:
        return None, None

    # --- absorb figure text ---
    text_blocks = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        tr = fitz.Rect(block["bbox"])
        if tr.is_empty:
            continue
        if CAPTION_RE.match("".join(
                sp["text"] for sp in block["lines"][0].get("spans", [])).strip()):
            continue  # never absorb a caption
        if tr.intersects(cap):
            continue
        if tr.y1 <= header_y:
            continue  # running header
        if mode == "above" and (tr.y0 < win_top - 2 or tr.y1 > cap.y0 + 2):
            continue
        if mode == "below" and tr.y1 < cap.y1 - 2:
            continue
        text_blocks.append((tr, len(block.get("lines", []))))

    gfx_bottom = region.y1   # bottom edge of the graphic union, before absorption

    for _ in range(5):
        grown = False
        for tr, n_lines in text_blocks:
            # band around the current region (mode "beside" has no window)
            if mode == "above":
                cy = (tr.y0 + tr.y1) / 2
                if not (region.y0 - 26 <= cy <= region.y1 + 14):
                    continue
            else:
                if tr.y1 < region.y0 - 30 or tr.y0 > region.y1 + 30:
                    continue

            h_overlap = min(tr.x1, region.x1) - max(tr.x0, region.x0)
            left_gap = region.x0 - tr.x1
            right_gap = tr.x0 - region.x1
            near = (0 <= left_gap <= 22) or (0 <= right_gap <= 22)
            overlaps = h_overlap > 0 and h_overlap >= 0.5 * tr.width
            # figure text is short: axis labels / panel letters / a risk table row.
            # body paragraphs are tall, wide and multi-line -> never absorb them.
            compact = (tr.height <= 80 or tr.width <= 22) and n_lines <= 4

            # in "beside" mode body text flows underneath the figure: only accept
            # blocks that start at or above the graphic bottom edge
            if mode == "beside" and tr.y0 > gfx_bottom + 8:
                compact = False

            if (overlaps or near) and compact:
                new = region | tr
                if new != region:
                    region = new
                    grown = True
        if not grown:
            break

    bottom_limit = cap.y0 - 2 if mode == "above" else page.rect.height
    top_limit = 0 if mode != "above" else 0
    region = fitz.Rect(
        max(0, region.x0 - 6),
        max(top_limit, region.y0 - 5),
        min(page.rect.width, region.x1 + 6),
        min(bottom_limit, region.y1 + 5),
    )
    # A real multi-panel main figure is never ~1 cm tall. A thin region means we
    # anchored on incidental strokes / a stray rule -> reject and let the caller
    # fall back to the previous page (Cell Press "legend on next page" layout).
    if region.height < 80:
        return None, None
    return region, mode


def figure_on_previous_page(doc, pno, header_frac):
    """Cell Press / Elsevier style: artwork on page N-1, caption at top of page N
    ("Figure N ... (legend on next page)" -> caption follows artwork).

    Returns (page, region) of the previous page's artwork, or (None, None).
    """
    if pno == 0:
        return None, None
    prev = doc[pno - 1]
    header_y = header_frac * prev.rect.height
    graphics = page_graphics(prev, header_y)
    if not graphics:
        return None, None

    # the artwork occupies the lower part of the page; ignore top decorations
    y_min = 0.20 * prev.rect.height
    gs = [r for r in graphics if r.y1 > y_min]
    if not gs:               # no artwork on the previous page
        return None, None

    region = fitz.Rect(gs[0])
    for r in gs[1:]:
        region |= r
    if region.height < 120 or region.width < 120:
        return None, None

    # absorb compact text on that page (panel letters, axis labels, thresholds)
    blocks = []
    for block in prev.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        tr = fitz.Rect(block["bbox"])
        if tr.is_empty or tr.y1 < header_y:
            continue
        first = "".join(sp["text"] for sp in block["lines"][0].get("spans", [])).strip()
        if CAPTION_RE.match(first):
            continue
        if first.lower().startswith("(legend"):
            continue
        blocks.append(tr)

    for _ in range(5):
        grown = False
        for tr in blocks:
            cy = (tr.y0 + tr.y1) / 2
            if not (region.y0 - 30 <= cy <= region.y1 + 30):
                continue
            h_overlap = min(tr.x1, region.x1) - max(tr.x0, region.x0)
            near = (0 <= region.x0 - tr.x1 <= 25) or (0 <= tr.x0 - region.x1 <= 25)
            if h_overlap <= 0 and not near:
                continue
            if not (tr.height <= 90 or tr.width <= 25):   # skip body paragraphs
                continue
            new = region | tr
            if new != region:
                region = new
                grown = True
        if not grown:
            break

    region = fitz.Rect(
        max(0, region.x0 - 8), max(0, region.y0 - 6),
        min(prev.rect.width, region.x1 + 8), min(prev.rect.height, region.y1 + 8),
    )
    return prev, region


def figure_number(match):
    m = re.search(r"\d+", match)
    return int(m.group()) if m else None


def main():
    ap = argparse.ArgumentParser(description="Extract main figures from a paper PDF")
    ap.add_argument("pdf", help="Path to the paper PDF")
    ap.add_argument("--out", default=None,
                    help="Output directory (default: <pdf_dir>/figures)")
    ap.add_argument("--dpi", type=int, default=300, help="Render DPI (default 300)")
    ap.add_argument("--include-ed", action="store_true",
                    help="Also extract Extended Data / Supplementary figures")
    ap.add_argument("--header-frac", type=float, default=0.055,
                    help="Fraction of page height treated as running header (default 0.055)")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"ERROR: PDF not found: {args.pdf}")
        sys.exit(1)

    out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(args.pdf)), "figures")
    os.makedirs(out_dir, exist_ok=True)

    doc = fitz.open(args.pdf)
    zoom = args.dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    manifest = {}
    seen = set()

    for pno in range(len(doc)):
        page = doc[pno]
        header_y = args.header_frac * page.rect.height
        graphics = page_graphics(page, header_y)
        caps = caption_blocks(page)

        prev_bottom = None
        for cap in caps:
            is_ed = re.search(r"(Extended|Supplementary)", cap["match"], re.IGNORECASE)
            if is_ed and not args.include_ed:
                prev_bottom = cap["rect"].y1
                continue

            num = figure_number(cap["match"])
            key = (f"ed{num}" if is_ed else f"fig{num}") if num else None
            if key is None:
                prev_bottom = cap["rect"].y1
                continue

            region, mode = build_region(page, cap, prev_bottom, graphics, header_y)
            render_page, render_region = page, region
            status = mode or "fallback"
            if region is None:
                # Cell Press style: caption on this page, artwork on the previous one
                ppage, pregion = figure_on_previous_page(doc, pno, args.header_frac)
                if pregion is not None:
                    render_page, render_region, status = ppage, pregion, "prev-page"
                else:
                    # Fallback: everything between the previous caption and this one
                    y0 = max(header_y, prev_bottom or header_y)
                    render_region = fitz.Rect(0.035 * page.rect.width, y0,
                                              page.rect.width - 0.035 * page.rect.width,
                                              cap["rect"].y0 - 2)
                    status = "fallback"
            prev_bottom = cap["rect"].y1

            if key in seen:
                continue
            if render_region.width < 30 or render_region.height < 30:
                print(f"[skip] {key}: degenerate region on page {pno + 1}")
                continue

            seen.add(key)
            fname = f"{key}.png"
            pix = render_page.get_pixmap(matrix=mat, clip=render_region, alpha=False)
            pix.save(os.path.join(out_dir, fname))

            manifest[key] = {
                "file": fname,
                "page": render_page.number + 1,
                "caption_page": pno + 1,
                "caption": cap["text"][:2000],
                "bbox": [round(v, 1) for v in render_region],
                "status": status,
                "dpi": args.dpi,
            }
            print(f"[{status}] {key}: page {render_page.number + 1}, "
                  f"{int(render_region.width)}x{int(render_region.height)} pt -> {fname}")

    with open(os.path.join(out_dir, "captions.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nExtracted {len(manifest)} figures -> {out_dir}")
    print(f"Manifest: {os.path.join(out_dir, 'captions.json')}")


if __name__ == "__main__":
    main()

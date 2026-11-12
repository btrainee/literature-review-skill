---
name: bio-literature-review
description: "Bioinformatics literature systematic review skill. Use when interpreting a scientific paper PDF in bioinformatics, genomics, oncology, or related fields. Extracts full text AND every main figure as high-resolution PNGs (PyMuPDF caption-anchored region rendering), then generates standardized deliverables: a Word deep-reading report (10-section structure with each figure embedded and analyzed: research question / method / key results / interpretation), a Nature/Cell-style PPT for group meeting sharing, and optionally a popular science article for WeChat Official Account. Covers the full workflow from PDF parsing, figure extraction, deep reading, structured analysis, to document generation."
agent_created: true
---

# Bioinformatics Literature Systematic Review

## Purpose

Transform a raw English research paper PDF into a suite of standardized,
high-quality Chinese review materials: Word deep-reading report with every
main figure embedded and explained, PPT sharing slides, and optional popular
science article. Designed for bioinformatics researchers who need
reproducible, depth-first literature interpretation.

## When to Use

Trigger when the user provides a scientific paper PDF (or asks to review a
specific paper) and wants any of:
- Word deep-reading report (10-section structured analysis)
- **Figure extraction** — pull every main figure out of the PDF as an image
  and explain it one by one
- PPT group meeting sharing material
- Popular science article for WeChat Official Account
- All of the above (full pipeline)

Typical user phrases:
- "解读这篇论文" / "解析这篇文章"
- "帮我做个文献精读"
- "把每张主图提取出来讲解" / "每张Figure都要配图解读"
- "生成Word解读 + PPT"
- "整理成科普文章"

## Prerequisites

### Python Environment

Any Python >= 3.9 works. Use the interpreter that ships with your agent
runtime, or your own virtualenv.

Install dependencies (one-time):
```
pip install pdfplumber pymupdf python-docx python-pptx
```

If PyPI is slow (common in mainland China), use a domestic mirror:
```
pip install pymupdf -i https://mirrors.cloud.tencent.com/pypi/simple
```

- `pymupdf` (PyMuPDF) is required for figure extraction — it provides both
  page rendering and coordinate-level text/graphics inspection.
- `pdfplumber` is used for plain text extraction.
- `python-docx` / `python-pptx` generate the deliverables.

### Project Structure Convention

Each paper gets an independent folder under the workspace root:

```
NN_YYYY-Journal-Topic/
  Original_Paper.pdf
  Journal_YYYY_Topic_LiteratureReview.docx
  Journal_YYYY_Topic_ArticleSharing.pptx
  full_text.txt              (extracted text, intermediate)
  figures/                   (extracted main figure PNGs, intermediate)
    fig1.png, fig2.png, ...
    captions.json            (figure number -> caption/page/bbox manifest)
  Topic_PopularScience.html   (optional, for WeChat OA)
```

- `NN`: zero-padded sequence number (01, 02, 03...)
- `YYYY`: publication year
- `Journal`: abbreviated journal name (Nature, Cell, Science...)
- `Topic`: short Chinese topic description

## Workflow

### Step 1: Setup & PDF Text Extraction

1. Create output folder following the naming convention above
2. Copy the source PDF into the new folder
3. Run `scripts/extract_pdf_text.py` to extract full text:
   ```bash
   python scripts/extract_pdf_text.py "<pdf_path>" "<output_txt_path>"
   ```
   This produces `full_text.txt` with page-delimited extracted text.

### Step 2: Extract Main Figures from the PDF

Run `scripts/extract_figures.py` to extract every main figure as a
high-resolution PNG (default 300 DPI):

```bash
python scripts/extract_figures.py "<pdf_path>" --out "<paper_folder>/figures" --dpi 300
```

- Add `--include-ed` to also extract Extended Data / Supplementary figures.
- The script locates captions ("Fig. 1", "Figure 1", "图1"), determines the
  column span, unions the graphics above the caption, and renders the region.
- **Layout variants already handled** (verified on Nature / Cancer Cell PDFs):
  - caption below artwork (most common);
  - caption beside artwork (caption at column top, figure in the other column);
  - caption above artwork;
  - **Cell Press "legend on next page"**: artwork on page N-1, caption at the
    top of page N — the script detects that no graphics sit above the caption
    and renders the previous page's artwork automatically (`status: prev-page`).
  - **journal banner**: the full-width Cell Press / Cancer Cell colour bar at
    the page top is filtered out (`status: above` should never contain it).
- If a figure still contains a header, raise `--header-frac` (e.g. `0.13` for
  Cancer Cell / Cell Genomics, default `0.055` for Nature).
- **Body-text absorption guard**: in the "caption beside artwork" mode a figure
  can bleed into the body paragraph that flows underneath it. Text blocks are
  only absorbed when they are compact (short height or narrow width) **and**
  ≤ 4 lines, and in `beside` mode only when they start at or above the graphic
  bottom edge. If a figure still ends with a paragraph of prose, this is the
  rule to tighten.
- Output: `figures/figN.png` + `figures/captions.json` (caption text, page,
  caption_page, bbox, extraction status per figure).
- **Always verify the extracted PNGs** by viewing them (ViewImage): check each
  image is the complete figure (all panels, not cropped, no body text mixed
  in). If a figure is mis-cropped, re-render that region manually with PyMuPDF
  using the bbox from `captions.json` as a starting point. Do NOT embed a
  broken image silently.

### Step 3: Deep Read the Paper

Read the extracted text in segments (200 lines per read). For EACH main
figure, also view the extracted PNG to understand panels and layout. Focus on
extracting:
- Title, authors, journal, DOI, publication date
- Abstract and key findings
- All Figures (number, title, panels, what each shows) — cross-check the
  caption in `captions.json` against the actual image
- Methods (sequencing platforms, software tools, algorithms, parameters)
- Sample information (cohort size, tissue types, sequencing types)
- Key results and statistical significance
- Limitations mentioned by authors

### Step 4: Generate Word Deep-Reading Report

Follow the 10-section structure defined in `references/word_structure.md`.

Use `scripts/generate_word_report.py` as a template. Copy it into the paper
folder (e.g. `generate_word_report.py`), replace the CONTENT block with the
actual analysis, and run it with the output path:
```bash
python generate_word_report.py "<paper_folder>/Journal_YYYY_Topic_LiteratureReview.docx"
```

The script demonstrates:
- python-docx document creation with styled headings
- Table formatting for basic info and terminology
- Bullet lists for analysis pipelines
- Colored callout boxes for key findings
- `add_figure_block()`: embeds each extracted figure PNG + caption +
  4-part analysis (研究问题 / 方法 / 关键结果 / 解读)

Section 7 (Main Research Content) MUST embed the extracted figure images
(`figures/figN.png`) — one image per figure, each followed by its per-figure
analysis. Image paths and captions come from `figures/` and `captions.json`.

Key formatting rules:
- Headings use Heading 1/2/3 styles with custom formatting
- Tables use "Light Grid Accent 1" **plus an explicit dark header fill**
  (`shade_cell(cell, "1A3A5C")`) — the built-in style leaves the header row
  unfilled when white text is applied, making the header invisible in Word
- Figures are fitted to **width 15.5 cm with a max height of ~18.5 cm**
  (aspect-aware, via PIL). A portrait 4-panel Manhattan at full page width
  (21+ cm tall) overflows the page and gets clipped at the bottom — always
  cap the height
- Tables longer than one page: `keep_rows_together(table)` marks the header row
  as `w:tblHeader` (repeats on every page) and every row as `w:cantSplit`, so a
  table never breaks mid-row or loses its header
- Technical terms keep English abbreviation, followed by Chinese explanation
- No data fabrication: uncertain items marked with "需确认"
- Verify the output by exporting to PDF (Word COM `SaveAs(..., 17)`) and
  viewing 2–3 pages: header row visible, figures complete, no overflow

### Step 5: Generate PPT Sharing Slides

Follow the slide structure defined in `references/ppt_structure.md`.

Use `scripts/generate_ppt_slides.py` as a template:
```bash
python scripts/generate_ppt_slides.py
```

The script demonstrates:
- python-pptx slide creation with custom layouts
- Nature/Cell-style minimalist design (white background, dark text)
- Per-Figure slides: embed the extracted `figures/figN.png` on the slide,
  then Figure title → research question → methods → results → significance
- Final Key Findings + Scientific Impact slide

### Step 6: Generate Popular Science Article (Optional)

When the user wants a WeChat OA article, write an HTML file with:
- Inline CSS (WeChat strips `<style>` tags)
- Mobile-first design (max-width: 680px)
- Metaphor-driven science communication
- Data cards, comparison tables, timelines
- All data must come from the original paper, no fabrication

See `references/popular_science_style.md` for detailed writing guide.

### Step 7: Quality Check

Verify:
- All technical terms have English abbreviation + explanation
- All Figures are covered in both Word and PPT
- Every main figure in the Word report has its embedded image verified
  (complete panels, no cropping, no stray body text)
- No fabricated data or speculative conclusions
- Analysis pipeline is complete (software → algorithm → input/output)
- Statistical values match the original paper

## Interpretation Principles

Follow `references/interpretation_principles.md` for all generated content. Core rules:

1. **Keep English abbreviations** — do NOT simply translate to Chinese
2. **Explain technical principles** — not just what, but why and how
3. **Depth-first** — answer "why this method?", "what does the data show?", "what does it mean?"
4. **Target audience**: bioinformatics engineers, genomics researchers
5. **No fabrication** — uncertain information marked as "需确认"

## File Reference

| File | Purpose |
|------|---------|
| `scripts/extract_pdf_text.py` | Extract full text from PDF using pdfplumber |
| `scripts/extract_figures.py` | Extract main figures as high-res PNGs + captions.json manifest (PyMuPDF) |
| `scripts/generate_word_report.py` | Template script for Word document generation (incl. figure embedding) |
| `scripts/generate_ppt_slides.py` | Template script for PPT slide generation |
| `references/word_structure.md` | 10-section Word report structure specification (incl. per-figure block format) |
| `references/ppt_structure.md` | PPT slide structure specification |
| `references/interpretation_principles.md` | AI interpretation principles and rules |
| `references/popular_science_style.md` | Popular science article writing guide |

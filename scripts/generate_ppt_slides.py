#!/usr/bin/env python3
"""
Template script for generating a Nature/Cell-style PPT using python-pptx.
Follows the slide structure defined in references/ppt_structure.md.

Usage:
    python generate_ppt_slides.py [output_path]

Customize the SLIDES data below before running.
"""

import sys
import os

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu, Cm
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
except ImportError:
    print("ERROR: python-pptx not installed. Run: pip install python-pptx")
    sys.exit(1)


# ============================================================
# COLOR SCHEME (Nature/Cell minimalist style)
# ============================================================

COLOR_PRIMARY = RGBColor(0x1a, 0x3a, 0x5c)
COLOR_ACCENT = RGBColor(0xe8, 0x5d, 0x4a)
COLOR_TEXT = RGBColor(0x2c, 0x2c, 0x2c)
COLOR_LIGHT = RGBColor(0x66, 0x66, 0x66)
COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_BG_LIGHT = RGBColor(0xf5, 0xf7, 0xfa)

# Slide dimensions (16:9)
SLIDE_WIDTH = Cm(33.867)
SLIDE_HEIGHT = Cm(19.05)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_slide(prs):
    """Add a blank slide and return it."""
    layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(layout)
    return slide


def set_slide_bg(slide, color=COLOR_WHITE):
    """Set slide background color."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text_box(slide, left, top, width, height):
    """Add a text box and return the text frame."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    return tf


def add_paragraph(tf, text, font_size=14, color=COLOR_TEXT, bold=False,
                  alignment=PP_ALIGN.LEFT, space_after=Pt(6)):
    """Add a paragraph to a text frame with formatting."""
    p = tf.add_paragraph()
    p.text = text
    p.alignment = alignment
    p.space_after = space_after

    for run in p.runs:
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        run.font.bold = bold
        run.font.name = "Microsoft YaHei"

    return p


def add_title_slide(prs, title, subtitle, author_info):
    """Create slide 1: Article introduction."""
    slide = add_slide(prs)
    set_slide_bg(slide, COLOR_WHITE)

    # Top accent bar
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE.RECTANGLE
        Cm(0), Cm(0),
        SLIDE_WIDTH, Cm(0.8)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_PRIMARY
    shape.line.fill.background()

    # Title
    tf = add_text_box(slide, Cm(2), Cm(4.5), Cm(29), Cm(5))
    p = tf.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(26)
    for run in p.runs:
        run.font.size = Pt(32)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        run.font.name = "Microsoft YaHei"

    # Subtitle
    add_paragraph(tf, subtitle, font_size=17, color=COLOR_ACCENT,
                  bold=True, alignment=PP_ALIGN.CENTER, space_after=Pt(12))

    # Author info
    tf2 = add_text_box(slide, Cm(2), Cm(15), Cm(29), Cm(3))
    add_paragraph(tf2, author_info, font_size=12, color=COLOR_LIGHT,
                  alignment=PP_ALIGN.CENTER)

    return slide


def add_content_slide(prs, title, bullets, subtitle=None):
    """Create a standard content slide with title and bullet points."""
    slide = add_slide(prs)
    set_slide_bg(slide, COLOR_WHITE)

    # Title bar
    shape = slide.shapes.add_shape(
        1, Cm(0), Cm(0), Cm(33.867), Cm(2.5)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_PRIMARY
    shape.line.fill.background()

    # Title text
    tf = shape.text_frame
    tf.margin_left = Cm(2)
    tf.margin_right = Cm(2)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.LEFT
    for run in p.runs:
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = COLOR_WHITE
        run.font.name = "Microsoft YaHei"

    # Subtitle
    if subtitle:
        tf2 = add_text_box(slide, Cm(2), Cm(3), Cm(29), Cm(1.5))
        add_paragraph(tf2, subtitle, font_size=15, color=COLOR_ACCENT,
                      bold=True)

    # Content
    tf3 = add_text_box(slide, Cm(2.2), Cm(4.8), Cm(29), Cm(12.5))
    for i, bullet in enumerate(bullets):
        p = tf3.paragraphs[0] if i == 0 else tf3.add_paragraph()
        p.space_after = Pt(13)
        p.line_spacing = 1.25
        run = p.add_run()
        run.text = ("• " if not bullet[:1].isdigit() else "") + bullet
        run.font.size = Pt(16)
        run.font.color.rgb = COLOR_TEXT
        run.font.name = "Microsoft YaHei"

    return slide


def add_figure_slide(prs, figure_title, question, method, result, significance,
                     image=None):
    """Create a per-figure analysis slide.

    If `image` (path to figures/figN.png from extract_figures.py) is given,
    the figure fills the left side and the analysis text sits on the right.
    """
    slide = add_slide(prs)
    set_slide_bg(slide, COLOR_WHITE)

    # Title
    tf = add_text_box(slide, Cm(2), Cm(0.8), Cm(29), Cm(1.5))
    p = tf.paragraphs[0]
    p.text = figure_title
    for run in p.runs:
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        run.font.name = "Microsoft YaHei"

    # Divider line
    line = slide.shapes.add_shape(
        1, Cm(2), Cm(2.5), Cm(29), Cm(0.05)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(0xe8, 0xe8, 0xe8)
    line.line.fill.background()

    # Content sections
    if image and os.path.exists(image):
        # Figure on the left, analysis on the right
        pic = slide.shapes.add_picture(image, Cm(1.8), Cm(3), width=Cm(16.2))
        if pic.top + pic.height > Cm(17.6) or pic.width > Cm(16.2):
            ratio = pic.width / pic.height
            max_h = Cm(14.2)
            pic.height = max_h
            pic.width = int(max_h * ratio)
            if pic.width > Cm(16.2):
                pic.width = Cm(16.2)
                pic.height = int(Cm(16.2) / ratio)
        # centre the artwork inside the left panel
        pic.left = int(Cm(1.8) + (Cm(16.2) - pic.width) / 2)
        pic.top = int(Cm(3) + (Cm(14.4) - pic.height) / 2)
        tf2 = add_text_box(slide, Cm(19.2), Cm(3.2), Cm(12.9), Cm(13.8))
    else:
        tf2 = add_text_box(slide, Cm(2), Cm(3), Cm(29), Cm(14))

    items = [
        ("Research Question: ", question),
        ("Method: ", method),
        ("Key Result: ", result),
        ("Significance: ", significance),
    ]

    body_pt = Pt(12.5 if image else 14)
    for i, (label, content) in enumerate(items):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
        p.space_after = Pt(11)

        r1 = p.add_run()
        r1.text = label
        r1.font.bold = True
        r1.font.size = Pt(13 if image else 14)
        r1.font.color.rgb = COLOR_ACCENT
        r1.font.name = "Microsoft YaHei"

        r2 = p.add_run()
        r2.text = content
        r2.font.size = body_pt
        r2.font.color.rgb = COLOR_TEXT
        r2.font.name = "Microsoft YaHei"

    return slide


def add_summary_slide(prs, findings, impact):
    """Create the final Key Findings + Scientific Impact slide."""
    slide = add_slide(prs)
    set_slide_bg(slide, COLOR_PRIMARY)

    # Title
    tf = add_text_box(slide, Cm(2), Cm(1), Cm(29), Cm(2))
    p = tf.paragraphs[0]
    p.text = "Key Findings & Scientific Impact"
    for run in p.runs:
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.color.rgb = COLOR_WHITE
        run.font.name = "Microsoft YaHei"

    # Divider
    line = slide.shapes.add_shape(
        1, Cm(2), Cm(3), Cm(29), Cm(0.05)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_ACCENT
    line.line.fill.background()

    # Findings
    tf2 = add_text_box(slide, Cm(2), Cm(4), Cm(29), Cm(10))
    for i, finding in enumerate(findings):
        if i == 0:
            p = tf2.paragraphs[0]
        else:
            p = tf2.add_paragraph()
        p.text = f"{i+1}. {finding}"
        p.space_after = Pt(10)
        for run in p.runs:
            run.font.size = Pt(14)
            run.font.color.rgb = COLOR_WHITE
            run.font.name = "Microsoft YaHei"

    # Impact
    tf3 = add_text_box(slide, Cm(2), Cm(15), Cm(29), Cm(3))
    p = tf3.paragraphs[0]
    p.text = "Scientific Impact: " + impact
    for run in p.runs:
        run.font.size = Pt(14)
        run.font.color.rgb = COLOR_ACCENT
        run.font.bold = True
        run.font.name = "Microsoft YaHei"

    return slide


# ============================================================
# MAIN GENERATION FUNCTION
# ============================================================

def generate_ppt(output_path: str):
    """Generate a complete PPT presentation."""

    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    # ===== SLIDE 1: Article Introduction =====
    add_title_slide(
        prs,
        title="Paper Title (English)",
        subtitle="Chinese Translation",
        author_info="First Author | Corresponding Author | Journal, Year | DOI"
    )

    # ===== SLIDE 2: Research Background =====
    add_content_slide(
        prs,
        title="Research Background",
        bullets=[
            "Bullet 1: Field context",
            "Bullet 2: Current gap",
            "Bullet 3: Why this study is needed",
        ],
        subtitle="Why was this study conducted?"
    )

    # ===== SLIDE 3: Scientific Question =====
    add_content_slide(
        prs,
        title="Scientific Question",
        bullets=[
            "The core question in one sentence",
            "Sub-question 1",
            "Sub-question 2",
        ]
    )

    # ===== SLIDE 4: Study Design =====
    add_content_slide(
        prs,
        title="Study Design",
        bullets=[
            "Cohort: N patients, inclusion criteria",
            "Sequencing: platform, data type, depth",
            "Analysis pipeline overview",
            "Follow-up duration",
        ]
    )

    # ===== SLIDES 5-N: Per-Figure Analysis =====
    # Repeat for each figure in the paper
    add_figure_slide(
        prs,
        figure_title="Figure 1: [Title]",
        question="What does this figure address?",
        method="Software/algorithm used",
        result="Key numbers, P-values",
        significance="Biological meaning"
    )

    # Add more figure slides as needed...

    # ===== FINAL SLIDE: Key Findings & Scientific Impact =====
    add_summary_slide(
        prs,
        findings=[
            "Finding 1 with specific data",
            "Finding 2 with specific data",
            "Finding 3 with specific data",
            "Finding 4 with specific data",
        ],
        impact="Clinical/translational significance + future directions"
    )

    prs.save(output_path)
    print(f"PPT generated: {output_path}")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "output.pptx"
    generate_ppt(output)

#!/usr/bin/env python3
"""
Template script for generating a Word deep-reading report using python-docx.
Follows the 10-section structure defined in references/word_structure.md.

Usage:
    python generate_word_report.py

Customize the content variables below before running.
The script demonstrates all formatting patterns needed for a complete report.
"""

import sys
import os

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
except ImportError:
    print("ERROR: python-docx not installed. Run: pip install python-docx")
    sys.exit(1)


# ============================================================
# CONTENT - Replace these with actual paper analysis
# ============================================================

PAPER_INFO = {
    "english_title": "The evolution of non-small cell lung cancer metastases in TRACERx",
    "chinese_title": "TRACERx研究中非小细胞肺癌转移的演化",
    "journal": "Nature",
    "impact_factor": "64.8",
    "pub_date": "2023-04",
    "first_author": "Al Bakir M",
    "corresponding_author": "Charles Swanton",
    "sequencing_tech": "WES",
    "sample_type": "NSCLC tumor + metastasis + normal blood",
    "sample_size": "421 patients, 126 metastasis cases",
    "data_source": "TRACERx cohort (EGAS00001000825)",
    "doi": "10.1038/s41586-023-05729-x",
}

OUTPUT_PATH = "output.docx"  # Customize to actual output path

# ============================================================
# FORMATTING HELPERS
# ============================================================

COLOR_PRIMARY = RGBColor(0x1a, 0x3a, 0x5c)
COLOR_ACCENT = RGBColor(0xe8, 0x5d, 0x4a)
COLOR_TEXT = RGBColor(0x2c, 0x2c, 0x2c)
COLOR_LIGHT = RGBColor(0x66, 0x66, 0x66)


def add_heading_styled(doc, text, level=1):
    """Add a heading with custom color formatting."""
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = COLOR_PRIMARY
    return heading


def shade_cell(cell, hex_fill):
    """Apply a solid background colour to a table cell (header needs this:
    with the built-in styles the white header text would be invisible)."""
    from docx.oxml import OxmlElement
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def keep_rows_together(table):
    """Repeat the header row on each page; forbid rows splitting across pages."""
    from docx.oxml import OxmlElement
    for idx, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if idx == 0:
            hdr = OxmlElement("w:tblHeader")
            hdr.set(qn("w:val"), "true")
            trPr.append(hdr)


def add_table(doc, headers, rows, style_name="Light Grid Accent 1"):
    """Add a formatted table with headers and data rows."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    try:
        table.style = style_name
    except Exception:
        pass  # style not available in every python-docx build

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        shade_cell(cell, "1A3A5C")
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.size = Pt(10)

    # Data rows
    for row_idx, row_data in enumerate(rows):
        for col_idx, cell_text in enumerate(row_data):
            cell = table.rows[row_idx + 1].cells[col_idx]
            cell.text = str(cell_text)
            if row_idx % 2 == 1:
                shade_cell(cell, "EDF1F6")
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9.5)

    keep_rows_together(table)
    return table


def add_bullet(doc, text, bold_prefix=None):
    """Add a bullet point with optional bold prefix."""
    p = doc.add_paragraph(style="List Bullet")
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.bold = True
        p.add_run(text)
    else:
        p.add_run(text)
    return p


def add_callout(doc, text, bold_text=None):
    """Add a highlighted callout paragraph."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)

    # Add shading via XML
    shading = p.paragraph_format
    run = p.add_run(">> " if bold_text else "")
    run.font.color.rgb = COLOR_ACCENT
    run.bold = True

    if bold_text:
        run2 = p.add_run(bold_text)
        run2.bold = True
        run2.font.color.rgb = COLOR_ACCENT

    run3 = p.add_run(text)
    run3.font.size = Pt(11)
    return p


def add_pipeline_step(doc, step_name, description):
    """Add a pipeline step with arrow formatting."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    run1 = p.add_run(f"{step_name} -> ")
    run1.bold = True
    run1.font.color.rgb = COLOR_PRIMARY
    run1.font.size = Pt(11)

    run2 = p.add_run(description)
    run2.font.size = Pt(11)
    run2.font.color.rgb = COLOR_TEXT
    return p


def add_figure_block(doc, figure):
    """Insert an embedded figure image with its per-figure deep analysis.

    Required keys of `figure` dict:
        image:    path to the extracted figure PNG (from extract_figures.py)
        number:   figure number, e.g. "Figure 1"
        title:    short Chinese title, e.g. "ALPACA 算法概览"

    Optional keys (all recommended, each rendered as a labeled paragraph):
        question:  研究问题 - what question this figure answers
        method:    方法 - software/algorithm/design used
        results:   list of key results with concrete numbers/P-values
        insight:   解读 - why this design matters, what it proves
        caption:   original figure caption (English, truncated as needed)
    """
    # Figure heading
    add_heading_styled(doc, f"{figure['number']}: {figure['title']}", level=2)

    # Embedded image, fitted to page width (A4 ~16.5cm printable)
    if figure.get("image") and os.path.exists(figure["image"]):
        img_p = doc.add_paragraph()
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p.add_run().add_picture(figure["image"], width=Cm(16))
    else:
        add_callout(doc, "(图片缺失：extract_figures.py 未提取到该图，需确认)",
                    bold_text="⚠ ")

    # Original caption
    if figure.get("caption"):
        cap_p = doc.add_paragraph()
        cap_run = cap_p.add_run(f"原文图注: {figure['caption']}")
        cap_run.font.size = Pt(9)
        cap_run.font.color.rgb = COLOR_LIGHT
        cap_run.italic = True

    # Per-figure 4-part analysis
    labels = [
        ("question", "研究问题"),
        ("method", "方法"),
        ("insight", "解读"),
    ]
    for key, label in labels:
        if figure.get(key):
            add_bullet(doc, figure[key], bold_prefix=f"{label}: ")

    if figure.get("results"):
        for r in figure["results"]:
            add_bullet(doc, r, bold_prefix="关键结果: ")

    return doc


# ============================================================
# DOCUMENT GENERATION
# ============================================================

def generate_report(output_path: str):
    doc = Document()

    # Set default font
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Microsoft YaHei"
    font.size = Pt(11)
    font.color.rgb = COLOR_TEXT

    # Set Chinese font
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")

    # ===== TITLE =====
    title = doc.add_heading("Literature Deep-Reading Report", level=0)
    for run in title.runs:
        run.font.color.rgb = COLOR_PRIMARY

    subtitle = doc.add_paragraph(PAPER_INFO["chinese_title"])
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in subtitle.runs:
        run.font.size = Pt(16)
        run.font.color.rgb = COLOR_ACCENT
        run.bold = True

    # ===== SECTION 1: Basic Information =====
    add_heading_styled(doc, "1. Literature Basic Information", level=1)

    info_rows = [
        ["English Title", PAPER_INFO["english_title"]],
        ["Chinese Title", PAPER_INFO["chinese_title"]],
        ["Journal", PAPER_INFO["journal"]],
        ["Impact Factor", PAPER_INFO["impact_factor"]],
        ["Publication Date", PAPER_INFO["pub_date"]],
        ["First Author", PAPER_INFO["first_author"]],
        ["Corresponding Author", PAPER_INFO["corresponding_author"]],
        ["Sequencing Technology", PAPER_INFO["sequencing_tech"]],
        ["Sample Type", PAPER_INFO["sample_type"]],
        ["Sample Size", PAPER_INFO["sample_size"]],
        ["Data Source", PAPER_INFO["data_source"]],
        ["DOI", PAPER_INFO["doi"]],
    ]
    add_table(doc, ["Field", "Content"], info_rows)

    # ===== SECTION 2: Research Background =====
    add_heading_styled(doc, "2. Research Background", level=1)
    doc.add_paragraph("Add research background paragraphs here...")
    # Add 3-5 paragraphs covering: field status, gaps, hypothesis

    # ===== SECTION 3: Research Objectives =====
    add_heading_styled(doc, "3. Research Objectives", level=1)
    doc.add_paragraph("What problem does the author want to solve?")
    doc.add_paragraph("Why is this study needed?")
    doc.add_paragraph("What is the significance?")

    # ===== SECTION 4: Sample & Experimental Design =====
    add_heading_styled(doc, "4. Sample & Experimental Design", level=1)
    design_rows = [
        ["Patient Count", PAPER_INFO["sample_size"]],
        ["Sample Type", PAPER_INFO["sample_type"]],
        ["Sequencing Type", PAPER_INFO["sequencing_tech"]],
        ["Analysis Strategy", "Multi-region sampling + phylogenetic reconstruction"],
    ]
    add_table(doc, ["Parameter", "Value"], design_rows)

    # ===== SECTION 5: Bioinformatics Analysis Pipeline =====
    add_heading_styled(doc, "5. Bioinformatics Analysis Pipeline", level=1)

    add_heading_styled(doc, "Pipeline Overview", level=2)
    add_pipeline_step(doc, "Raw Reads", "FASTQ files from sequencing platform")
    add_pipeline_step(doc, "Alignment", "BWA-MEM to reference genome (GRCh38)")
    add_pipeline_step(doc, "Variant Calling", "Mutect2 for SNV/indel, FACETS for CNV")
    add_pipeline_step(doc, "Phylogenetic Analysis", "CONIPHER for clonal reconstruction")
    add_pipeline_step(doc, "Selection Analysis", "dN/dS analysis for positive selection")
    add_pipeline_step(doc, "Biological Interpretation", "Clinical correlation and survival analysis")

    # ===== SECTION 6: Key Terminology =====
    add_heading_styled(doc, "6. Key Terminology", level=1)
    add_bullet(doc, "Intratumor Heterogeneity (ITH) - Definition here",
               bold_prefix="ITH: ")
    add_bullet(doc, "Cancer Cell Fraction (CCF) - Definition here",
               bold_prefix="CCF: ")
    # Add 8-15 terms

    # ===== SECTION 7: Main Research Content (Per Figure) =====
    add_heading_styled(doc, "7. Main Research Content", level=1)

    # Each figure = one embedded image + 4-part analysis.
    # Image paths come from extract_figures.py output (figures/figN.png);
    # caption text comes from figures/captions.json.
    FIGURES = [
        {
            "image": "figures/fig1.png",  # relative or absolute path
            "number": "Figure 1",
            "title": "示例：算法/研究概览",
            "question": "这张图回答什么问题？",
            "method": "用了什么软件/算法/实验设计？",
            "results": [
                "具体结果1（含数字与P值）",
                "具体结果2（含数字与P值）",
            ],
            "insight": "为什么这样设计？这个结果证明了什么？",
            "caption": "Original English caption from the paper...",
        },
        # ... one entry per main figure
    ]

    for figure in FIGURES:
        add_figure_block(doc, figure)

    # ===== SECTION 8: Innovation Points =====
    add_heading_styled(doc, "8. Innovation Points", level=1)
    add_bullet(doc, "Methodological innovation description")
    add_bullet(doc, "Data scale innovation description")
    add_bullet(doc, "Biological discovery innovation description")
    add_bullet(doc, "Clinical significance description")

    # ===== SECTION 9: Limitations =====
    add_heading_styled(doc, "9. Limitations", level=1)
    add_bullet(doc, "Sample size limitations")
    add_bullet(doc, "Technical limitations")
    add_bullet(doc, "Methodological assumptions")
    add_bullet(doc, "Unaddressed questions")

    # ===== SECTION 10: Summary =====
    add_heading_styled(doc, "10. Summary", level=1)
    add_callout(doc, "One-sentence core contribution",
                bold_text="Core Contribution: ")

    add_heading_styled(doc, "Key Findings", level=2)
    add_bullet(doc, "Finding 1 with specific data")
    add_bullet(doc, "Finding 2 with specific data")
    add_bullet(doc, "Finding 3 with specific data")

    # Save
    doc.save(output_path)
    print(f"Word report generated: {output_path}")


if __name__ == "__main__":
    # Customize output_path and PAPER_INFO before running
    output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_PATH
    generate_report(output)

# PPT Slide Structure Specification

## Design Principles

- **Style**: Nature/Cell minimalist — white background, dark text, minimal decoration
- **Content priority**: Charts/figures > bullet points > paragraph text
- **Text**: Concise, key phrases only, no full sentences on slides
- **Color scheme**: Primary dark blue (#1a3a5c), accent red (#e85d4a), neutral grays
- **Font**: Microsoft YaHei or PingFang SC for Chinese, Arial for English

## Slide-by-Slide Structure

### Slide 1: Article Introduction

Layout: Title slide

Content:
- Paper title (English original + Chinese translation)
- First author + corresponding author
- Journal name + year + volume
- DOI
- Presenter name (bottom right)

### Slide 2: Research Background

Layout: Content slide with left text + right figure (optional)

Content:
- 2-3 bullet points on field context
- The gap this study fills
- Key prior studies referenced (author, year)

### Slide 3: Scientific Question

Layout: Centered question style

Content:
- The core scientific question in one sentence (large font)
- 2-3 sub-questions if applicable

### Slide 4: Study Design

Layout: Flowchart or schematic

Content:
- Cohort overview (patient count, sample types)
- Sequencing strategy (platform, data type, depth)
- Analysis pipeline (simplified flowchart)
- Timeline (recruitment period, follow-up duration)

### Slides 5-N: Per-Figure Analysis

Each figure gets ONE slide (complex figures may get 2 slides).

Layout per slide (figure image on the left, analysis text on the right):
```
┌─────────────────────────────────┐
│ Figure N: [Title]               │
├──────────────────┬──────────────┤
│                  │ Research Q:  │
│  figures/figN.png│ Method:      │
│  (extracted from │ Key Result:  │
│   the PDF)       │ Significance:│
└──────────────────┴──────────────┘
```

Always pass the extracted PNG to `add_figure_slide(..., image="figures/figN.png")`.
A slide without the actual figure wastes the value of a group meeting;
showing the real panel is the point.

Content per slide:
- **Figure title** (top, bold)
- **Research question** this figure addresses
- **Method**: Software/algorithm used (1-2 lines)
- **Key result**: Specific data (numbers, P-values, fold changes)
- **Significance**: What this means biologically

### Final Slide: Key Findings & Scientific Impact

Layout: Two-section summary

Content:
```
Key Findings:
1. [Finding 1 with specific data]
2. [Finding 2 with specific data]
3. [Finding 3 with specific data]
4. [Finding 4 with specific data]

Scientific Impact:
- [Clinical/translational significance]
- [Methodological contribution]
- [Future directions]
```

## Formatting Guidelines

- **Slide dimensions**: 16:9 (33.867 cm x 19.05 cm)
- **Title font**: 28-32pt, bold, dark blue
- **Body font**: 14-18pt
- **Bullet points**: Max 5 per slide, max 2 lines each
- **Figure annotations**: 10-12pt, gray
- **Data emphasis**: Bold + colored for key numbers
- **Transitions**: None (academic style)

## Generation Notes

- Use python-pptx for programmatic generation
- Create blank layout slides, add text boxes and shapes manually for full control
- For figure images: export from PDF or screenshot, then insert as picture
- Keep text minimal — slides support verbal presentation, not replace it

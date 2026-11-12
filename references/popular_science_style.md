# Popular Science Article Writing Guide

Guide for converting a research paper into a WeChat Official Account-friendly popular science article.

## Core Philosophy

- **Metaphor-driven**: Use a central metaphor to anchor complex concepts throughout the article
- **Data-grounded**: Every claim backed by specific numbers from the paper
- **Mobile-first**: All styling inline (WeChat strips `<style>` tags), max-width 680px
- **No fabrication**: All data from original paper, no invented numbers

## Article Structure

```
1. Hero Section (title + key stats + source attribution)
2. Introduction (hook + central question + metaphor setup)
3. Background (the study/trial context, explained simply)
4. Core Findings (one section per major finding)
5. Key Takeaways (summary box with all findings)
6. Clinical Implications (timeline-style "what this means for patients")
7. Limitations (honest, brief)
8. Conclusion (callout box with core message)
9. Footer (paper info, key terms glossary, disclaimer)
```

## Writing Style

### Metaphor Design
Pick ONE central metaphor that runs through the entire article. Past examples:
- Tumor evolution = family tree (树/族谱)
- Metastasis = military expedition (远征/据点)
- Clonal selection = competition (优胜者/内战)

Use metaphor boxes (styled divs with dashed borders) to introduce and reinforce the metaphor.

### Data Presentation
Use data cards for key numbers:
```html
<div style="background: #fff; border: 1px solid #e8e8e8; border-radius: 10px; padding: 20px; margin: 20px 0;">
  <div style="font-size: 36px; font-weight: 800; color: #e85d4a;">75%</div>
  <div style="font-size: 13px; color: #666;">晚期分化比例</div>
  <div style="font-size: 14px; color: #333; margin-top: 10px;">详细说明...</div>
</div>
```

### Comparison Tables
For contrasting categories (early vs late, type A vs type B):
```html
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
  <tr>
    <th style="background: #1a3a5c; color: white; padding: 10px;">类别</th>
    <th style="background: #1a3a5c; color: white; padding: 10px;">特征</th>
  </tr>
  ...
</table>
```

### Highlight Boxes
For critical findings that need emphasis:
```html
<div style="background: #fff0ed; border-left: 4px solid #e85d4a; padding: 16px 20px; margin: 20px 0;">
  <strong>关键发现：</strong> ...
</div>
```

### Concept Boxes
For explaining technical terms in-line:
```html
<div style="background: #f0eaf8; border-radius: 10px; padding: 16px 20px; margin: 20px 0;">
  <strong style="color: #6b3fa0;">WGD (Whole Genome Doubling)</strong><br>
  解释内容...
</div>
```

## Inline CSS Color Palette

```css
--primary: #1a3a5c;       /* Dark blue - headings, table headers */
--accent: #e85d4a;         /* Red-orange - emphasis, key numbers */
--accent-light: #fff0ed;   /* Light red - highlight backgrounds */
--green: #2d8659;          /* Green - callouts, positive findings */
--green-light: #e8f6ef;    /* Light green - callout backgrounds */
--purple: #6b3fa0;          /* Purple - concept boxes */
--purple-light: #f0eaf8;    /* Light purple - concept backgrounds */
--text: #2c2c2c;           /* Main text */
--text-light: #666;        /* Secondary text */
--border: #e8e8e8;         /* Borders */
```

## Conversion Rules (HTML → WeChat)

1. **Remove `<style>` tags** — all styles must be inline `style="..."`
2. **Remove `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`** — only keep `<body>` inner content
3. **No external images** — only `mmbiz.qpic.cn` URLs work in WeChat
4. **No JavaScript** — WeChat strips all scripts
5. **Max content width**: 680px (mobile reading width)
6. **Font**: `-apple-system, "PingFang SC", "Microsoft YaHei", sans-serif`
7. **Line height**: 1.8 for body text

## Title Guidelines

- Max 64 bytes (~21 Chinese characters) for WeChat draft
- Pattern: [Metaphor]: [What the study reveals]
- Example: 癌症转移的"族谱"：追踪肺癌细胞的远征之路

## Digest (Summary) Guidelines

- 1-2 sentences, max 120 characters
- State the most surprising finding
- Example: "迄今最大规模肺癌转移演化图谱：75%转移出发比想象中晚，单区域取样83%会判错"

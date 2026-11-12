# Word Deep-Reading Report Structure (10 Sections)

The Word report follows a strict 10-section structure. Each section has specific content requirements.

## Section 1: Literature Basic Information

Present as a two-column table:

| Field | Content |
|-------|---------|
| English Title | Full title from paper |
| Chinese Title | Translated title (keep key terms in English) |
| Journal | e.g., Nature, Cell, Science |
| Impact Factor | Current IF |
| Publication Date | YYYY-MM |
| First Author | Name, institution |
| Corresponding Author | Name, institution |
| Sequencing Technology | WGS, WES, scRNA-seq, etc. |
| Sample Type | Tumor tissue, blood, FFPE, etc. |
| Sample Size | Number of patients/samples |
| Data Source | GEO, TCGA, dbGaP, in-house, etc. |
| DOI | Full DOI link |

## Section 2: Research Background

Cover:
- Current state of the field (what is known)
- Unresolved scientific questions (what is unknown)
- Research gap (what is missing)
- Core hypothesis of this study

Write 3-5 paragraphs. Reference prior landmark studies by author name and year.

## Section 3: Research Objectives

Answer three questions:
1. What problem does the author want to solve?
2. Why is this study needed? (gap it fills)
3. What is the significance? (clinical/scientific impact)

## Section 4: Sample & Experimental Design

Detail in structured format:
- Patient cohort: size, inclusion/exclusion criteria, staging
- Sample types: primary tumor, metastasis, normal blood, FFPE vs fresh
- Sequencing platform: Illumina NovaSeq, PacBio, Oxford Nanopore, 10x Genomics
- Data types: WGS, WES, RNA-seq, scRNA-seq, scATAC-seq, spatial transcriptomics
- Analysis strategy: multi-region sampling, longitudinal sampling, matched normal
- Key parameters: coverage depth, read length, cell count

## Section 5: Bioinformatics Analysis Pipeline

This is the most important section. Present as a flow diagram followed by detailed explanations.

### Pipeline Overview (flow chart style):
```
Raw reads → Quality Control → Alignment → Variant Calling →
Annotation → Clonal Reconstruction → Evolutionary Analysis →
Statistical Analysis → Biological Interpretation
```

### For each step, explain:
- Software name (e.g., BWA, GATK, Mutect2, PyClone, CONIPHER)
- Algorithm principle (brief, 2-3 sentences)
- Input data → Output data
- Why this method was chosen (advantages over alternatives)
- Key parameters (if mentioned in paper)

### Analysis categories to cover:
- Somatic mutation calling (SNV/indel, CNV, SV)
- Clonal/phylogenetic analysis
- Mutational signature analysis
- Selection analysis (dN/dS)
- Immune/deconvolution analysis (if applicable)
- Survival/clinical correlation (if applicable)

## Section 6: Key Terminology

Format each term as:
> **Term (Abbreviation)**: Definition (1-2 sentences)
> **Biological significance**: Why this matters
> **In this study**: How the paper uses/applies this concept

Cover 8-15 terms depending on paper complexity. Include both common and paper-specific terms.

## Section 7: Main Research Content (Per Figure)

For each Figure (1 through N), the report MUST embed the actual figure image
extracted from the PDF (via `scripts/extract_figures.py`), followed by the
analysis. Structure of each figure block:

### Figure N: [Chinese short title]

1. **Embedded image** — `figures/figN.png` extracted from the PDF, centered,
   page-width. If extraction failed, insert a "⚠ 图片缺失，需确认" callout.
2. **原文图注** — original English caption (small gray italic font).
3. **研究问题**: What question does this figure address?
4. **方法**: Data source, software/algorithm, statistical test
5. **关键结果**: Specific numbers, P-values, effect sizes (one bullet each)
6. **解读**: What the result proves + why the authors designed it this way

Worked example (from the 2025 Nature CCD paper review):

> **Figure 1: ALPACA 算法概览**
> 研究问题: ALPACA 算法如何工作？输入什么、输出什么？核心优化逻辑是什么？
> 方法: 算法示意图。输入三个组件：(1) 每个基因组片段的等位基因特异性分数
> 拷贝数 F̂（来自 ASCAT/Sequenza）；(2) 肿瘤系统发育树（来自 CONIPHER）；
> (3) 每个克隆在每个样本中的比例 U。优化目标通过 MILP 求解。
> 核心逻辑: 两个优化目标：(1) 最小化预测分数拷贝数落在观察置信区间外的样本数；
> (2) 最小化预测值与观察值的 Manhattan 距离。
> 设计意义: ALPACA 将复杂的拷贝数反卷积问题简化为线性优化问题，使大规模
> 队列分析成为可能，还能推断已灭绝克隆的拷贝数。

Must cover ALL main figures in the paper. Extended Data / supplementary figures:
include when they carry key results (use `--include-ed` during extraction).

## Section 8: Innovation Points

Categorize into:
- Methodological innovation (new algorithm, new pipeline, new analysis framework)
- Data scale innovation (largest cohort, most comprehensive sampling)
- Biological discovery innovation (novel findings,颠覆性结论)
- Clinical significance (diagnostic/prognostic/therapeutic implications)

## Section 9: Limitations

Cover:
- Sample size limitations
- Technical limitations (sequencing depth, platform, coverage)
- Methodological assumptions and their validity
- Unaddressed questions
- Author-acknowledged limitations (from Discussion section)

## Section 10: Summary

- One-sentence core contribution
- 3-5 key findings (numbered, each with specific data)
- Future directions (if mentioned by authors)

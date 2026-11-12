# AI Interpretation Principles

All generated content (Word, PPT, popular science article) must follow these principles.

## 1. Professional Accuracy

### Keep English Abbreviations
Do NOT simply translate technical terms to Chinese. Keep the English abbreviation and provide explanation.

**Wrong:**
> SV 就是结构变异。

**Correct:**
> Structural Variation (SV) 是指基因组中长度通常超过 50 bp 的大尺度 DNA 重排事件，包括 Deletion、Duplication、Inversion 和 Translocation 等类型，是驱动肿瘤基因组重塑的重要机制。

### Explain Technical Principles
For every method/tool mentioned, explain:
- What it does (input → output)
- How it works (algorithm principle, 2-3 sentences)
- Why it was chosen (advantages over alternatives)

### No Fabrication
- All data must come from the original paper
- If information is uncertain or not explicitly stated, mark with "需确认"
- Do not infer results or conclusions beyond what the paper presents

## 2. Depth-First Analysis

### Beyond Summary
Do not merely restate what the paper says. Answer:
- **Why this method?** — What does this analysis approach solve that others cannot?
- **What does the data show?** — Specific numbers, statistical tests, effect sizes
- **How does data support the conclusion?** — Trace the logic from data → conclusion
- **What does it mean?** — Biological/clinical significance

### Example Depth Levels

**Surface (NOT acceptable):**
> 作者使用了 PyClone 进行克隆分析。

**Deep (acceptable):**
> 作者使用 PyClone (Roth et al., 2016) 进行克隆亚群重建。PyClone 基于贝叶斯聚类方法，将不同变异等位基因频率 (VAF) 的突变聚为不同的克隆亚群。输入为 VAF 数据和拷贝数信息，输出为克隆亚群组成和癌细胞分数 (CCF)。选择 PyClone 的原因是它能够同时处理拷贝数变异和正常细胞污染，比传统 VAF 阈值方法更准确地重建克隆结构。

## 3. Target Audience

Default readers:
- Bioinformatics engineers
- Genomics researchers
- Oncology researchers

Therefore, include:
- Software names (with citation where applicable)
- Algorithm principles (not just software names)
- Input/output data types
- Analysis parameters (if mentioned)
- Pipeline flow (ordered, with arrows)

## 4. Figure Analysis Requirements

For each figure:
- Identify the research question it addresses
- Explain the analysis method (not just "see Figure X")
- Report specific results (numbers, P-values, fold changes)
- Interpret biological significance
- Explain design rationale ("why did the authors design it this way?")

## 5. Language Style

- **Scientific terms**: English abbreviation + Chinese explanation (first mention), abbreviation only thereafter
- **Data presentation**: Use exact values from paper (percentages, P-values, confidence intervals)
- **Analysis descriptions**: Active voice, process-oriented ("作者首先...然后...最后...")
- **Critical thinking**: Include limitations and alternative interpretations where relevant
- **Cross-references**: Link findings across figures ("这一结果与 Figure 3B 的发现一致")

## 6. Quality Checklist

Before finalizing any deliverable:
- [ ] All technical terms have English + explanation
- [ ] All Figures covered (no skipping)
- [ ] All software/tools named with brief algorithm explanation
- [ ] No fabricated data (verify against original text)
- [ ] Statistical values match the paper
- [ ] Uncertain information marked "需确认"
- [ ] Analysis pipeline is complete and ordered
- [ ] Limitations section included

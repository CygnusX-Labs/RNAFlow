# RNAFlow Development Roadmap

[中文版本](ROADMAP_zh.md) | [Back to README](../README.md)

The following items remain planned work and are not release guarantees for v0.2.0.

## Planned Analysis Extensions
- **Dynamic Web Report Generation**:
    - Implement dynamic generation of web reports for different workflows and modules.
    - **Implementation Logic**:
        1. **Module State Awareness**: Records states of `DEG`, `rMATS`, `Variant`, etc., in `project_summary.json`.
        2. **Dynamic Navigation Construction**: Before Quarto rendering, a Python script dynamically generates `_quarto.yml` based on module states, automatically hiding tabs for unrun analyses.
        3. **Conditional Content Rendering**: Uses Python logic within `.qmd` templates to achieve dynamic loading and display of result chapters.

- **WGCNA (Weighted Gene Co-expression Network Analysis)**:
    - Implement gene module clustering and phenotype association analysis to identify core Hub Genes.
    - Export network files for Cytoscape visualization.
- **GSVA (Gene Set Variation Analysis)**:
    - Calculate pathway activity scores for each sample, enabling differential analysis and visualization (heatmaps/correlations) of pathways.
- **TF Regulatory Network Prediction (Transcription Factor)**:
    - Integrate **PlantRegMap / PlantTFDB** for plants (e.g., Lettuce) to predict upstream transcription factor regulatory logic of differential genes.
- **Cellular Deconvolution**:
    - Introduce CIBERSORTx/MuSiC algorithms using single-cell reference sets to parse cell type proportions in tissue samples.

## Planned LncRNA and Cloud Reference Extensions
- **LncRNA Prediction and Analysis**:
    - Integrate CPAT/CPC2/LncFinder to identify novel LncRNAs and construct LncRNA-mRNA co-expression networks.
- **Cloud-Native Reference Management**:
    - Adopt **BYOC (Bring Your Own Cloud)** strategy, empowering users to build their own biological data centers for "Stateless Portability".
    - **Reference Factory**: Provides an independent Snakemake build process, supporting automatic synchronization to S3/OSS/MinIO.

## Advanced Experimental Design Modules
- To support more complex experimental designs (e.g., time-series analysis, two-factor interactions), the DEG module is planned for refactoring to support custom design formulas (`design_formula`).

## AI Engine Enhancements
Further enhance AI's capabilities in bioinformatics analysis:

1. **Multimodal Analysis**: Combine multiple data types like gene expression, variants, and splicing for comprehensive biological explanations.
2. **Real-time Learning**: Introduce online learning mechanisms for AI models to continuously update knowledge bases with the latest literature.
3. **Personalized Interpretation**: Generate customized analysis report content based on users' professional backgrounds and research interests.

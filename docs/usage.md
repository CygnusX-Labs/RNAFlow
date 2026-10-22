# 💻 Usage Instructions

> Part of the [RNAFlow documentation](../README.md).

## Standard Analysis Workflow

RNAFlow manages project parameters through external YAML configuration files, achieving decoupling between code and configuration.

### 1. Configuration Preparation

Copy `examples/analysisyaml.example.yaml`, then configure project paths and module switches:

```yaml
# === Basic Project Info ===
project_name: 'PRJNA1224991'
Genome_Version: "Lsat_Salinas_v11"
species: 'Lsat Salinas'
client: 'Internal_Test'

# === Data Paths ===
raw_data_path:
  - /path/to/raw_data
sample_csv: /path/to/samples.csv
paired_csv: /path/to/contrasts.csv
workflow: /path/to/analysis_dir
data_deliver: /path/to/deliver_dir

# === Run Parameters ===
execution_mode: local
Library_Types: fr-firststrand

# === Analysis Module Switches (all snake_case) ===
only_qc: false              # Run QC only (skips all downstream analysis if true)
deg: true                   # Differential expression analysis
call_variant: true        # Variant calling
detect_novel_transcripts: true  # Novel transcript detection (formerly noval_Transcripts)
rmats: true                 # Alternative splicing analysis
fastq_screen: true          # Contamination check
deliver: true               # Generate delivery manifests
project_summary: true       # Export project JSON for external BioReport
```

### 2. Running the Analysis Pipeline

```bash
# 1) Dry Run check
snakemake -n \
    --config analysisyaml=/path/to/your_config.yaml

# 2) Execute analysis (Recommended parameters)
snakemake \
    --cores=60 \                           # Use 60 cores
    -p \                                   # Print shell commands
    --conda-frontend=mamba \              # Use mamba to manage conda environments
    --use-conda \                          # Automatically create/use conda environments
    --rerun-triggers mtime \              # Rerun based on modification time
    --logger rich-loguru \                # Use rich-loguru for colored logs
    --config analysisyaml=/path/to/your_config.yaml
```

### 3. Configuration Item Description

| Config Item | Type | Default | Description |
|-------|------|-------|------|
| `only_qc` | bool | false | QC only mode, skips downstream analysis like DEG, variant calling, etc. if true. |
| `deg` | bool | true | Differential expression analysis (DESeq2) |
| `call_variant` | bool | false | Variant calling (GATK) |
| `detect_novel_transcripts` | bool | false | Novel transcript detection (StringTie), formerly `noval_Transcripts` |
| `rmats` | bool | true | Alternative splicing analysis (rMATS) |
| `fastq_screen` | bool | true | Contamination check (FastQ Screen) |
| `deliver` | bool | true | Organize outputs and generate delivery manifests |
| `project_summary` | bool | true | Export the versioned project JSON consumed by external BioReport |

---

## Detailed Post-Configuration Analysis Content

Based on the settings in `config.yaml`, RNAFlow automatically decides which modules to run. Here are details for when items are enabled/disabled:

### 📊 Basic Analysis (Always Runs)
In standard mode, mapping and quantification are enabled by default and can be pulled
in automatically as dependencies. In `only_qc` mode, only the MD5 gate, raw-read QC,
trimming, and merged QC reports are targeted.

| Step | Tool | Output Content |
|------|------|---------|
| **MD5 Check** | md5sum | Raw data integrity verification report |
| **Quality Control (QC)** | FastQC, fastp | Sequencing data quality reports, filtered clean data |
| **Mapping** | STAR | Aligned BAM files, mapping statistics, Qualimap report |
| **Quantification (Count)** | RSEM | Gene/transcript expression levels (TPM/FPKM/Counts) |
| **CRAM Compression** | samtools | Compressed storage in CRAM format |

### 🎛️ Optional Analysis Modules (Configuration Controlled)

#### 1️⃣ `only_qc: true` (QC Only Mode)
- **Effect**: Runs only MD5 validation, raw FastQC, trimming, and merged QC reports.
- **Use Case**: Data screening, rapid quality assessment.
- **Skipped Content**: DEG, variant calling, alternative splicing, novel transcripts, etc.

#### 2️⃣ `fastq_screen: true` (Contamination Check)
- **Tool**: FastQ Screen
- **Output**:
  - Contamination screening reports for R1/R2 of each sample.
  - MultiQC summary report.
- **Purpose**: Detects if samples are contaminated with exogenous species.

#### 3️⃣ `deg: true` (Differential Expression Analysis)
- **Tool**: DESeq2
- **Output**:
  - Differential gene lists for each contrast group (Excel/CSV).
  - Visualizations like volcano plots, MA plots, heatmaps, etc.
  - Gene expression distribution plots.
- **Dependency**: Requires correct setup of the `paired_csv` contrast table.

#### 4️⃣ `call_variant: true` (Variant Calling)
- **Tool**: GATK HaplotypeCaller
- **Output**:
  - Variant VCF files for each sample.
  - bcftools statistical reports.
  - MultiQC summary.
- **Application**: SNP/Indel detection in RNA-seq data.

#### 5️⃣ `detect_novel_transcripts: true` (Novel Transcript Detection)
- **Tool**: StringTie
- **Output**:
  - Novel transcript GTF files.
  - Filtered lists of new isoforms.
- **Old Config Name**: `noval_Transcripts` (Deprecated).

#### 6️⃣ `rmats: true` (Alternative Splicing Analysis)
- **Tool**: rMATS
- **Output**:
  - MATS results for 5 types of splicing events (SE, MXE, etc.).
  - Summary statistical reports.
  - Single sample and paired contrast results.
- **Additional**: Includes junction_annotation and CIRCexplorer2 (circRNA) analysis.

#### 7️⃣ `project_summary: true` (Report Data Export)
- **Output**:
  - `project_summary.json` with separate GO/KEGG results.
- **Purpose**: Provides the versioned JSON contract consumed by the external [BioReport](https://github.com/xsx123123/bioreport) system for HTML/PDF report generation.
- **Interface**: See [the JSON contract](project_summary_json.md).

#### 8️⃣ `gene_fusion: true` (Gene Fusion Detection)
- **Tool**: Arriba
- **Output**:
  - Fusion gene TSV results for each sample (`{sample}_fusions.tsv`).
  - Discarded fusion results (`{sample}_fusions.discarded.tsv`).
  - Optional PDF visualization reports.
- **Application**: Detects inter-chromosomal fusion events, common in cancer research.

---

### 📋 Typical Configuration Scenarios

**Scenario 1: Full Analysis (Recommended Default)**
```yaml
only_qc: false
deg: true
call_variant: true
detect_novel_transcripts: true
rmats: true
fastq_screen: true
project_summary: true  # Export JSON for external BioReport
```

**Scenario 2: Rapid QC Screening**
```yaml
only_qc: true  # Runs only QC and mapping
```

**Scenario 3: Standard Analysis Only (Skips Time-Consuming Modules)**
```yaml
only_qc: false
deg: true
call_variant: false      # Skips variant calling
detect_novel_transcripts: false  # Skips novel transcripts
rmats: false             # Skips alternative splicing
project_summary: true    # Export JSON for external BioReport
```

## Report Generation (External BioReport)

When `project_summary: true` is enabled, RNAFlow exports `project_summary.json` together with result tables and plots. The report itself is generated by [BioReport](https://github.com/xsx123123/bioreport), a separate repository in the CygnusX BioOps ecosystem that renders HTML and PDF deliverables. The interface between the pipeline and the reporting repository is documented in the [JSON contract](project_summary_json.md).

---

[← Back to README](../README.md)

# ⚙️ Configuration Guide

> Part of the [RNAFlow documentation](../README.md).

It is recommended to use external YAML configuration files to manage project parameters, achieving decoupling between code and configuration.

## Configuration Naming Convention

Starting from RNAFlow v0.1.9+, all configuration items uniformly use the **snake_case** (lowercase letters + underscores) naming convention to ensure consistency and readability.

| Old Config Name (Deprecated) | New Config Name (Recommended) | Description |
|----------------|---------------|------|
| `noval_Transcripts` | `detect_novel_transcripts` | Whether to detect novel transcripts |

**Core Configuration Naming Convention:**
```yaml
# Basic Switches (all snake_case)
only_qc: true                       # Run QC only
deliver: true                       # Generate delivery manifests
project_summary: true               # Export project JSON for external BioReport
deg: true                           # Differential expression analysis
fastq_screen: true                  # FastQ Screen contamination check
call_variant: true                 # Variant calling
detect_novel_transcripts: true      # Novel transcript detection [Old: noval_Transcripts]
rmats: true                         # Alternative splicing analysis
```

**Notes:**
1. All configuration items use lowercase letters connected by underscores `_`.
2. Boolean configurations default to `false` (except for some core modules).
3. Configuration names should be consistent with the full English name or common abbreviation of the corresponding analysis module.

## 1. Project Configuration Example

Copy `examples/analysisyaml.example.yaml` into the project workflow directory and
replace all placeholder paths. The repository root no longer stores a machine-specific
project `config.yaml`.

```yaml
project_name: 'PRJNA1224991'   # Project ID
Genome_Version: "Lsat_Salinas_v11" # Genome version (Supports: Lsat_Salinas_v8, Lsat_Salinas_v11, ITAG4.1, GRCm39, etc.)
species: 'Lsat Salinas'        # Species for analysis
client: 'Internal_Test'        # Client ID

# Raw data paths (Supports lists, can include multiple directories)
raw_data_path:
  - /path/to/raw_data

# Key information tables
sample_csv: /path/to/samples.csv    # Sample information table (format below)
paired_csv: /path/to/contrasts.csv  # Sample pairing/contrast info table (format below)

# Path settings
workflow: /path/to/analysis_dir     # Data analysis process directory (Workspace)
data_deliver: /path/to/deliver_dir  # Final result delivery directory

# Run parameters
execution_mode: local               # Run mode: local or cluster
# queue_id: fat_x86                 # Cluster queue name (Only valid in cluster mode), remove if not running on a cluster

# Sequencing library settings
Library_Types: fr-firststrand       # Strand-specificity type (fr-unstranded, fr-firststrand, fr-secondstrand)
                                    # The pipeline will automatically detect and compare settings; warnings will be issued if mismatched.

# Advanced analysis switches (All module switches use snake_case)
# Note: These are Boolean switches controlling the execution of each module.
# - true: Execute the module
# - false: Skip the module
call_variant: true                  # Whether to perform variant calling (GATK)
detect_novel_transcripts: true      # Whether to perform novel transcript assembly (StringTie) [Old: noval_Transcripts]
rmats: true                         # Whether to perform alternative splicing analysis (rMATS)
deg: true                           # Whether to perform differential expression analysis (DESeq2)
fastq_screen: true                  # Whether to perform contamination check (FastQ Screen)
deliver: true                       # Whether to organize deliverables and create manifests
project_summary: true               # Export project JSON for external BioReport

# Optional Configuration
only_qc: true                       # Run mode: qc_only (Only QC), if true skips all downstream analysis
```

## 2. Sample Information Table (sample_csv)
CSV format, containing three columns: `sample` (raw file name keyword), `sample_name` (renamed name), and `group` (grouping):
```csv
sample,sample_name,group
L1MKL2302060-CKX2_23_15_1,CKX2_1,CKX2
L1MKL2302061-CKX2_23_15_2,CKX2_2,CKX2
L1MKL2302062-CKX2_23_15_3,CKX2_3,CKX2
L1MKL2302063-Wo408_1,Wo408_1,Wo408
L1MKL2302064-Wo408_2,Wo408_2,Wo408
L1MKL2302065-Wo408_3,Wo408_3,Wo408
```

## 3. Sample Pairing Information Table (paired_csv)
Used for contrast settings in differential analysis (DEG), containing `Control` and `Treat` columns:
```csv
Control,Treat
Wo408,CKX2
```

## 4. Core Pipeline Configurations (Internal Configs)
Besides project-specific configs, the `config/` directory contains default settings:
- **`config/config.yaml`**: Basic global configurations of the pipeline.
- **`config/reference.yaml`**: Core reference genome configurations. Defines FASTA, GTF, and index paths for various versions (V8, V11, GRCm39, etc.).
  - **Pipeline Migration**: If running in a different environment, modify `reference_path` (e.g., `reference_path: /data/jzhang/reference/RNAFlow_reference`).
  - **Adding Genomes**: To support new species, add configurations in this file following the format.
  - **Automatic Check**: The pipeline automatically checks reference file integrity upon startup to ensure reliable analysis.
  - **FastQ Screen Database**: Added `fastq_screen_db_path`, pointing to the root directory of the contamination source database (must include subdirectories like hg38, GRCm39, fastq_screen_database). For migration, simply copy the directory and update the path in the configuration.
- **`config/run_parameter.yaml`**: Tool execution parameter settings, including specific command-line parameters for various software (e.g., STAR alignment thresholds, RSEM model parameters).
  - **STAR Parameter Details**:
    - `--peOverlapNbasesMin 0` (Default): PE Overlap merging disabled (default behavior).
    - `--peOverlapMMp 0.1` (Current) vs `0.01` (Default): Merging mismatch tolerance relaxed.
    - `--twopassMode Basic` (Current) vs `None` (Default): Two-pass mapping enabled.
    - `--outFilterMismatchNoverLmax 0.04` (Current) vs `0.3` (Default): Mismatch filtering strengthened.
    - `--alignMatesGapMax 1000000` (Current) vs `0` (Default): Cross-intron long gap alignment enabled.
    - `--chimSegmentMin 12` (Current) vs `0` (Default): Chimeric/fusion gene detection enabled.
    - `--quantMode TranscriptomeSAM` (Current) vs `None` (Default): Transcriptome quantification output enabled.
- **`config/cluster_config.yaml`**: Cluster resource definitions, specifying thread and memory allocations for different tasks (Low, Medium, High resource).

## 5. Cluster Configuration (Optional)
If `execution_mode` is set to `cluster`, install the executor plugin for your scheduler, e.g. `snakemake-executor-plugin-slurm` for Slurm or `snakemake_executor_donau` for Huawei Donau. Finer resource allocation (threads, memory) can be edited in `config/cluster_config.yaml`.

---

[← Back to README](../README.md)

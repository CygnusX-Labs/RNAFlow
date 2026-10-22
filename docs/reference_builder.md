# 🧬 Reference Genome Builder

> Part of the [RNAFlow documentation](../README.md).

RNAFlow provides an independent sub-workflow for building reference genome indexes under `build_reference/`. It is also exposed as an AI agent skill in `../skills/SKILL_build_reference.md`. This design decouples index construction from the main analysis pipeline, enabling:

- **Simplified Migration**: Build indexes once and migrate the entire reference directory to other servers.
- **Custom Genomes**: Easily build indexes for any species using your own reference FASTA and annotation files.
- **Auto-Generated Config**: Automatically produces a `reference.yaml` snippet ready to paste into the main pipeline config.

For detailed usage, see `../build_reference/README.md` and `../skills/SKILL_build_reference.md`.

## Directory Structure

```
build_reference/
├── config/
│   └── run_parameter.yaml     # Thread allocation and runtime parameters
├── config.yaml                # Reference genome metadata and file paths
├── envs/
│   ├── rsem.yaml              # Conda env for RSEM/STAR index building
│   └── ucsc_gff.yaml          # Conda env for UCSC annotation tools
├── rules/
│   ├── 00.copy_reference.smk  # Copy original ref files to workflow dir
│   ├── 01.index.smk           # Build STAR + RSEM indexes
│   ├── 02.annotation.smk      # Build bed12 and ref_all tables
│   └── 03.build_yaml.smk      # Generate reference.yaml config snippet
└── snakefile                  # Entry point
```

## Configuration (`build_reference/config.yaml`)

```yaml
# Genome version for validation (must be in can_use_genome_version)
Genome_Version: GRCm39

# Supported genome versions list
can_use_genome_version:
  - GRCm39

# DEG enrichment gene identifier column
gene_col: 'ENSEMBL'

# Genome ploidy for variant calling
ploidy: 2

Reference:
  info:
    name: GRCm39
    prefix: GRCm39_RNAFlow_Index          # Index directory name
    description: Mouse reference genome (GRCm39)
    # Base directory for reference outputs. Must match the main pipeline's
    # reference_path. The workflow creates a subdirectory named after 'name'.
    workflow: /path/to/reference
  data_dir:
    fa: /path/to/GRCm39.genome.fa
    gff: /path/to/gencode.vM38.annotation.gff3
    gtf: /path/to/gencode.vM38.annotation.gtf
    go: /path/to/mgigene_go_annotation.tsv
```

## Running the Builder

```bash
cd build_reference

# Dry run check
snakemake --use-conda --cores 40 --dry-run

# Execute build
snakemake --use-conda --cores 40
```

## Build Outputs

`workflow` is the parent reference directory (e.g. `/home/user/reference/RNAFlow_reference`). The workflow creates a subdirectory named after `name` (e.g. `GRCm39/`) and places all outputs there:

```
/home/user/reference/RNAFlow_reference/GRCm39/
├── GRCm39.genome.fa                    # Copied from data_dir
├── gencode.vM38.annotation.gtf         # Copied from data_dir
├── gencode.vM38.annotation.gff3        # Copied from data_dir
├── mgigene_go_annotation.tsv           # Copied from data_dir
├── GRCm39_RNAFlow_Index/               # STAR + RSEM indexes
│   ├── Genome
│   ├── GRCm39_RNAFlow_Index.transcripts.fa
│   └── GRCm39_RNAFlow_Index.idx.fa
├── GRCm39_RNAFlow_Index.bed12
├── GRCm39_RNAFlow_Index_ref_all.txt
└── GRCm39_RNAFlow_Index_reference.yaml  # Ready to paste into config/reference.yaml
```

## Integrating into the Main Pipeline

1. Ensure `workflow` in `build_reference/config.yaml` matches `reference_path` in `config/reference.yaml`.
2. Open `GRCm39_RNAFlow_Index_reference.yaml` and paste each section into the corresponding area of `config/reference.yaml`.
3. Set `Genome_Version: GRCm39` in your project's `config.yaml`.
4. **(If schema validation is enabled)** Add the new genome version to `schema/config.schema.yaml`:
   - Append the version name to `Genome_Version.enum` (e.g., `"GRCm39"`).
   - Add a corresponding entry under `parameter.star_index.properties` (optional, as `additionalProperties: true` allows extra keys).

---

[← Back to README](../README.md)

# 🐳 Container Image Builder (New in v0.1.9+)

> Part of the [RNAFlow documentation](../README.md).

RNAFlow now provides an automated container image builder that converts Conda environments to Docker images, enabling better portability and reproducibility.

## Quick Start

```bash
cd container_env

# Build single environment
python build_image.py -e ../envs/bwa2.yaml -t rnaflow-bwa:v2

# Batch build all environments
python build_image.py --batch ../envs/ --registry your-registry.io/

# Build and push
python build_image.py -e ../envs/fastqc.yaml -t rnaflow-fastqc:v2 --push --registry registry.io/
```

## Features

- ✅ **Rich Log Output**: Colorful terminal output with progress bars and tables
- ✅ **Auto Environment Activation**: Built images automatically activate the Conda environment
- ✅ **Health Checks**: Automatic verification of key tools in each image
- ✅ **Batch Processing**: Build all environments in one command
- ✅ **Detailed Logging**: All operations logged to `logs/` directory with JSON reports

## Usage in Snakemake

```python
rule bwa_index:
    input:
        ref="genome.fa"
    output:
        "genome.fa.bwt"
    container:
        "rnaflow-bwa:v2"  # Direct command execution, no activation needed
    shell:
        "bwa-mem2 index {input.ref}"
```

## Architecture Decision: Git Submodule for Multi-Pipeline Sharing

> **Current Design**: `container_env/` is designed to be used as a **Git Submodule** for sharing across multiple omics pipelines (RNAFlow, ATACFlow, etc.).

**Why Submodule:**
- **Single Source of Truth**: Update builder logic once, sync to all pipelines
- **Independent Versioning**: Container builder can evolve independently
- **Reusability**: Share between RNAFlow, ATACFlow, and future pipelines
- **Flexibility**: Each pipeline can pin to specific submodule version

**Directory Structure with Submodules:**
```
YourOrg/
├── rnaflow.git              # RNAFlow main repo
│   ├── container_env/ ->    # submodule: container-builder.git
│   └── envs/                # RNAFlow-specific envs
├── atacflow.git             # ATACFlow main repo
│   ├── container_env/ ->    # same submodule
│   └── envs/                # ATACFlow-specific envs
└── container-builder.git    # Shared builder submodule
```

**Setting up as Submodule:**
```bash
# Add to your pipeline repo
git submodule add git@github.com:YourOrg/container-builder.git container_env
git submodule update --init --recursive

# Update to latest version
git submodule update --remote container_env
git add container_env && git commit -m "Update container builder"
```

**Pipeline-Specific Configuration:**
Create `container_env/<pipeline>_config.yaml` to customize:
```yaml
# rnaflow_config.yaml
pipeline_name: "RNAFlow"
version: "0.2.0"
registry_prefix: "rnaflow"
default_envs:
  - bwa2
  - star
  - deseq2
```

See `../container_env/example_snakemake_integration.md` for detailed integration examples.

---

[← Back to README](../README.md)

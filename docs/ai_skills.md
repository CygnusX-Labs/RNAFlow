# 🤖 AI Skills Usage Guide

> Part of the [RNAFlow documentation](../README.md).

RNAFlow provides dedicated AI Skills, allowing you to interact with AI programming assistants like Claude Code and Codex via natural language to easily complete RNA-seq analysis.

## 1. Install Skills
> NOTE: Due to the decoupled architecture of the analysis pipeline and skills, please modify the paths in the `path_config.yaml` file to your actual paths before installing skills. For example: `RNAFLOW_ROOT`, `complete`, `standard_deg`, etc.

RNAFlow Skills are located in the `skills/` directory and support automatic installation to Claude Code or Codex:

```bash
cd /home/zj/pipeline/RNAFlow/skills

# Auto-detect and install (Recommended)
./install_skills.sh

# Install specifically for Claude Code
./install_skills.sh

# Install specifically for Codex
./install_codex_skills.sh
```

## 2. Skills Content

After installation, your AI assistant will gain the following capabilities:

- **SKILL.md**: Complete RNAFlow usage instructions and workflow.
- **path_config.yaml**: Automatically configures the RNAFlow installation path.
- **start_rnaflow.sh**: Enhanced startup script, including:
  - Conda environment auto-detection
  - Snakemake availability verification
  - User confirmation mechanism
  - Complete analysis workflow

## 3. Usage Example

After successful installation, restart your AI assistant and interact via natural language:

```
"Help me set up an RNAFlow analysis project"
"Run RNAFlow's QC-only mode to check data quality"
"Use RNAFlow for differential gene expression analysis"
"Help me configure RNAFlow and run a full analysis"
```

Example AI command for analysis:
"I have a batch of data in `/data/jzhang/project/Temp/rna_skills_analysis/00.raw_data`. Help me analyze it using RNAFlow skills. Use Lettuce v8 for the genome and perform only QC analysis. You can use the `activate_snakemake` `alias` command to activate the pre-configured Snakemake environment."

## 4. Enhanced Startup Script Features

`start_rnaflow.sh` provides a secure analysis startup process:

```
[1/5] Checking if conda is installed...
[2/5] Checking conda environments...
[3/5] Checking Snakemake in the environment...
[4/5] Environment summary, waiting for user confirmation...
[5/5] User confirmed activation of the environment...
```

## 5. Manual Installation (Alternative)

If the automatic installation script is not applicable, you can install manually:

**Claude Code**:
```bash
mkdir -p ~/.claude/skills/RNAFlow
cp -r skills/* ~/.claude/skills/RNAFlow/
chmod +x ~/.claude/skills/RNAFlow/start_rnaflow.sh
```

**Codex**:
```bash
mkdir -p ~/.codex/skills/RNAFlow
cp -r skills/* ~/.codex/skills/RNAFlow/
chmod +x ~/.codex/skills/RNAFlow/start_rnaflow.sh
```

## 6. More Information

For detailed installation and usage instructions, please refer to:
- `skills/INSTALL.md` - Complete installation guide
- `skills/usage-guide.md` - Usage guide
- `skills/README.md` - Skills documentation

---

[← Back to README](../README.md)

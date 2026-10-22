# 🔌 MCP Server Usage Guide

> Part of the [RNAFlow documentation](../README.md).

RNAFlow also provides an MCP server based on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), using **[uv](https://docs.astral.sh/uv/)** for modern environment management.

## MCP Server Features

- **Genome Query**: List reference genomes supported by the system (read from `mcp_genome_version` in `config/reference.yaml`).
- **Configuration Generation**: Automatically generate `config.yaml`, `samples.csv`, and `contrasts.csv`.
- **System Resource Monitoring**: Real-time check of CPU, memory, and disk usage, with warnings before task submission.
- **Project Run Management**: Uses an SQLite database to record information for each run, supporting queries and statistics.
- **Project Conflict Detection**: Checks for project name conflicts before starting tasks to avoid duplication.
- **Asynchronous Execution**: Starts Snakemake in the background without blocking the AI.
- **Detailed Logs**: All operations are recorded in the `mcp/logs/mcp/` directory, with timestamps and detailed execution information.
- **Environment Isolation**: Uses `uv` to ensure that dependency libraries and analysis environments do not interfere with each other.
- **Dual Mode Support**: Local stdio mode + remote deployment capability.

## Prerequisites

Before using the MCP Server, ensure the following are installed on the server:
- Python 3.13+
- **uv (Package Manager)** - Must be installed on the server first
- conda/mamba (for running Snakemake)
- Node.js (Optional, for MCP Inspector testing)

## Install uv (if not installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Start

1. **Install MCP Dependencies**:
```bash
cd /home/zj/pipeline/RNAFlow/mcp
uv sync
```

2. **Optional: Install System Resource Monitoring Dependencies (Recommended)**:
```bash
uv add psutil
```

3. **Test Run**:
```bash
./start.sh test
```

## Usage in AI Clients

For detailed instructions and configuration methods, please refer to: `../mcp/README.md`

- Local Usage Configuration
- Remote SSH Tunneling Configuration
- Production Deployment Plan

---

[← Back to README](../README.md)

# 🚀 Installation Guide

> Part of the [RNAFlow documentation](../README.md).

1.  **Clone the Repository**:
    ```bash
    git clone --recurse-submodules git@github.com:xsx123123/RNAFlow.git
    cd RNAFlow
    ```

2.  **Environment Preparation**:
    Install Snakemake and Mamba:
    ```bash
    conda install -c conda-forge -c bioconda snakemake mamba
    ```

3. The pipeline uses conda environments for dependencies, which will be automatically created during execution.

4. **(Optional) Install Enhanced Logger Plugin**:
   To enable colored console output and structured logging, install `snakemake_logger_plugin_rich_loguru` 0.3.0 or newer:
   ```bash
   pip install snakemake_logger_plugin_rich_loguru>=0.3.0
   ```
   > [!NOTE]
   > **Note**: The enhanced logger plugin is available via PyPI and will be automatically installed with the pipeline.

---

[← Back to README](../README.md)

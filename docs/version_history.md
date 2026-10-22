# 📈 Version History

> Part of the [RNAFlow documentation](../README.md).

## RNAFlow_v0.2.0 (2026-10-20)
- **Version**: Updated the Pipeline version from v0.1.9 to v0.2.0 in the default configuration, report module manifest, workflow headers, and example configurations.
- **Documentation**: Synchronized current-version references and clarified that roadmap features remain planned work. MCP Server and Deliver Tool retain their independent versions.

## RNAFlow_v0.1.9
- **Feature**: Added `container_env/` - Automated Docker image builder for Conda environments.
    - Converts `envs/*.yaml` to production-ready Docker images
    - Rich-loguru powered beautiful CLI output
    - Batch build and auto-push capabilities
    - Auto-activation environment in containers
- **Optimization**: Fixed potential bugs in `call variant`, `enrichments`, and `report` modules.
- **Optimization**: Optimized `reference.yaml` and added `deg_enrich_wrapper` and `ploidy_setting` configs.
- **Debug**: Fixed missing `ref_all` config for `Lsat_Salinas_v8` reference.
- **Optimization**: Reverted `STAR` parameters to defaults.
- **Debug**: Fixed version inconsistency in `snakefile` (v0.1.7 -> v0.1.9).
- **Critical Debug**: Fixed spelling error in STAR index file " Genome" in `judge_star_index` function (extra space).
- **Debug**: Fixed issue in `01.common.smk` where config parameters were not passed during mapping function calls.
- **Optimization**: Updated `config.schema.yaml`, adding hg38 to the Genome_Version enum list.
- **Optimization**: Improved `config.schema.yaml` verification, adding missing config items like loki_url, only_qc, bam_remove, etc.
- **Optimization**: Added missing `ref_all` fields for `TAIR10.1` and `hg38` reference genomes.
- **Cleanup**: Removed duplicate `fastq-screen.yaml` in the `envs/` directory.

## RNAFlow_v0.1.8
- **Feature**: Deprecated the old Seq log monitoring, updated to Loki + Grafana.
- **Feature**: Added `loki_url` config for Loki server address.
- **Feature**: Updated `snakemake_logger_plugin_rich_loguru` to 0.1.4 for Loki log pushing.
- **Documentation**: Added Grafana monitoring example screenshot (see `docs/grafana.png`).
- **Feature**: Added `compress_bg` module for compressing STAR `coverage` files.

## RNAFlow_v0.1.7
- **Feature**: Added `estimate_library_complexity` rule.
- **Feature**: Added `rmats_summary` for merging AS results from paired and single samples.
- **Improvement**: Used `temp()` to mark intermediate BAMs for removal; added `bam2cram` rule to reduce storage overhead.
- **Feature**: Added `CIRCexplorer2_run` for circRNA detection.
- **Feature**: Added `geneBody_coverage` for library coverage assessment.
- **Feature**: Added `read_distribution` for library read distribution detection.
- **Feature**: Integrated customized plugin `snakemake_logger_plugin_rich_loguru` with `seq` for workflow monitoring.

## RNAFlow_v0.1.6
- **Feature**: Modular refactoring of `DataDeliver` function.
- **Feature**: Enhanced configuration verification mechanisms.
- **Improvement**: Optimized AI report generation workflow, supporting more formats.
- **Feature**: Deep integration of **BioReport v2** system.
- **Feature**: Added rules `14.Merge_qc` and `15.deliver` for automated result organization.
- **Feature**: Added **Execution Mode** switch (`run_mode: qc_only`).
- **Improvement**: Updated `11.DEG_Enrichments` to integrate enrichment logic.
- **Optimization**: Refined flow control and fault tolerance for the AI engine.

## RNAFlow_v0.1.5 (2026-01-11)
- **New Feature**: Smart input data identification.
- **Improvement**: Enhanced CLI experience via `rich-loguru`.
- **Documentation**: Updated directory structure and usage examples.

## RNAFlow_v0.1.4 (2026-01-07)
- Added rMATS, gene fusion, enrichment analysis.
- Added support for GRCm39 reference.
- Fixed rMATS rules and workflow source path issues.

## RNAFlow_v0.1.3 (2026-01-03)
- Added DEG, merged RSEM, StringTie, GATK modules.
- Various bug fixes and improvements.

## RNAFlow_v0.1.2 (2025-12-25)
- Fixed mapping module errors.

## RNAFlow_v0.1.1 (2025-12-24)
- Added RSEM quantification module.

## RNAFlow_v0.1 (2025-12-24)
- Initial release.
- Basic RNA-seq analysis workflow (QC, mapping, quantification).

---

[← Back to README](../README.md)

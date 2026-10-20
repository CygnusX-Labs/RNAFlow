"""Build the renderer-independent RNAFlow result exchange document."""

import csv
import datetime
import math
from pathlib import Path


INTEGER_COLUMNS = {
    "Count", "Input_Gene_Count", "Background_Match_Count", "Universe_Gene_Count",
}
FLOAT_COLUMNS = {
    "pvalue", "p.adjust", "qvalue", "FoldEnrichment", "RichFactor", "zScore",
}


def _read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Description", "GeneRatio", "Count", "p.adjust"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Invalid enrichment CSV columns: {path}")
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Invalid enrichment CSV row: {path}")
            for column in INTEGER_COLUMNS | FLOAT_COLUMNS:
                if column not in row:
                    continue
                value = row[column].strip()
                if value in {"", "NA", "NaN", "NULL"}:
                    row[column] = None
                    continue
                number = float(value)
                if not math.isfinite(number):
                    row[column] = None
                elif column in INTEGER_COLUMNS:
                    if not number.is_integer() or number < 0:
                        raise ValueError(f"Invalid {column} in {path}: {value}")
                    row[column] = int(number)
                else:
                    if not 0 <= number <= 1 and column == "p.adjust":
                        raise ValueError(f"Invalid p.adjust in {path}: {value}")
                    row[column] = number
            gene_ratio = row["GeneRatio"].strip()
            if "/" in gene_ratio:
                numerator, denominator = gene_ratio.split("/", 1)
                if float(numerator) < 0 or float(denominator) <= 0:
                    raise ValueError(f"Invalid GeneRatio in {path}: {gene_ratio}")
            elif not math.isfinite(float(gene_ratio)):
                raise ValueError(f"Invalid GeneRatio in {path}: {gene_ratio}")
            if not row["Description"].strip():
                raise ValueError(f"Empty Description in {path}")
            if not isinstance(row["Count"], int):
                raise ValueError(f"Invalid Count in {path}: {row['Count']}")
            if not isinstance(row["p.adjust"], (int, float)):
                raise ValueError(f"Invalid p.adjust in {path}: {row['p.adjust']}")
            rows.append(row)
    return rows


def _relative_path(path):
    return f"data/{Path(path).as_posix()}"


def _direction_result(data_dir, contrast, direction, database, enabled):
    suffix = f"{direction}.csv" if database == "go" else f"{direction}_enrichments.csv"
    relative = Path("res/Enrichments") / f"{contrast}_{database.upper()}_{suffix}"
    result = {"status": "disabled" if not enabled else "unavailable", "messages": []}
    if not enabled:
        return result

    legacy_relative = Path("res/Enrichments") / f"{contrast}_{suffix}"
    if not (data_dir / relative).is_file() and (data_dir / legacy_relative).is_file():
        relative = legacy_relative
        result["messages"].append("Legacy filename: rerun Enrichments for explicit GO/KEGG filenames.")

    if database == "kegg":
        full_relative = relative.with_name(f"{relative.stem}_full.csv")
        if (data_dir / full_relative).is_file():
            result["full_table"] = _relative_path(full_relative)

    table_path = data_dir / relative
    if not table_path.is_file():
        result["messages"].append(f"Expected result not found: {_relative_path(relative)}")
        return result

    rows = _read_rows(table_path)
    placeholders = [row for row in rows if row.get("Count") == 0 or row.get("ID") == "None"]
    terms = [row for row in rows if row.get("Count") != 0 and row.get("ID") != "None"]
    result["table"] = _relative_path(relative)
    result["term_count"] = len(terms)
    result["messages"].extend(row["Description"] for row in placeholders)
    result["status"] = "available" if terms else "no_results"
    if any(message.startswith("Error:") for message in result["messages"]):
        result["status"] = "failed"
    return result


def _software_versions(data_dir, config):
    records = list(config.get("software_versions", []))
    for path in sorted(data_dir.rglob("multiqc_software_versions.txt")):
        with path.open(encoding="utf-8-sig") as handle:
            for line in handle:
                fields = line.rstrip("\n").split("\t")
                if len(fields) >= 2 and fields[0].strip() and fields[1].strip():
                    records.append({"Software": fields[0].strip(), "Version": fields[1].strip()})
    versions = []
    seen = set()
    for record in records:
        software = str(record.get("Software", "")).strip()
        version = str(record.get("Version", "")).strip()
        if not software or not version or software.casefold() in seen:
            continue
        item = {"Software": software, "Version": version}
        if record.get("Link"):
            item["Link"] = str(record["Link"])
        versions.append(item)
        seen.add(software.casefold())
    return versions


def build_project_summary(config, sample_sheet, data_dir, contrasts):
    """Build the BioReport v2 delivery document from delivered files."""
    data_dir = Path(data_dir)
    with Path(sample_sheet).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if "group" not in (reader.fieldnames or []):
            raise ValueError("Sample sheet must contain a group column")
        samples = list(reader)

    parameters = config.get("parameter", {})
    deg_parameters = parameters.get("DEG", {})
    enrichment_parameters = parameters.get("Enrichments", {})
    genome = config.get("Genome_Version")
    genome_config = config.get("deg_enrich_wrapper", {}).get(genome, {})
    kegg = genome_config.get("kegg", {})
    deg_enabled = config.get("deg", True) is not False and not config.get("only_qc", False)
    enrichment = {}
    for database in ("go", "kegg"):
        enabled = deg_enabled and (database == "go" or kegg.get("enabled", False))
        settings = {
            "padj_th": deg_parameters.get("PVAL", 0.05),
            "lfc_th": deg_parameters.get("LFC", 1),
            "cutoff": enrichment_parameters.get("cutoff", 0.05),
        }
        if database == "go":
            settings.update({"gene_col": genome_config.get("gene_col"), "gene_regex": enrichment_parameters.get("gene_regex")})
        else:
            settings.update({
                "organism": kegg.get("organism"),
                "gene_col": kegg.get("gene_col", genome_config.get("gene_col")),
                "id_mapping": "id_map" if kegg.get("id_map") else "identity",
            })
        enrichment[database] = {
            "enabled": bool(enabled),
            "method": "clusterProfiler::enricher" if database == "go" else "clusterProfiler::enrichKEGG",
            "parameters": settings,
            "contrasts": {
                contrast: {direction: _direction_result(data_dir, contrast, direction, database, enabled)
                           for direction in ("UP", "DOWN")}
                for contrast in contrasts
            },
        }

    project_id = config.get("project_id") or config.get("project_name")
    if not project_id:
        raise ValueError("project_id or project_name must be configured")
    project = {
        "project_id": project_id,
        "client": config.get("client"),
        "species": config.get("species"),
        "genome_version": genome,
        "pipeline_version": config.get("pipeline_version"),
        "analysis_date": config.get("analysis_date", datetime.date.today().isoformat()),
    }
    if config.get("report_date"):
        project["report_date"] = config["report_date"]

    return {
        "schema_version": "2.0.0",
        "path_base": ".",
        "project": project,
        "input_files": {
            "data_dir": "data",
            "qc_file": "data/index/multiqc_qc_general_stats.txt",
            "mapping_file": "data/index/multiqc_mapping_general_stats.txt",
            "tpm_file": "data/index/merge_rsem_tpm.tsv",
            "sample_file": "data/index/sample.csv",
            "contrasts_file": "data/index/contrasts.csv",
            "deg_dir": "data/res/DEG",
            "fastp_stats_file": "data/fastp_trim_report/multiqc_general_stats.txt",
            "fastp_report_dir": "data/fastp_trim_report/multiqc_short_read_trim_report_data",
            "fastq_screen_r1_dir": "data/fastq_screen_report/fastq_screen_multiqc_r1/multiqc_r1_fastq_screen_report_data",
            "fastq_screen_r2_dir": "data/fastq_screen_report/fastq_screen_multiqc_r2/multiqc_r2_fastq_screen_report_data",
            "qualimap_dir": "data/QualiMap/multiqc_data",
        },
        "software_versions": _software_versions(data_dir, config),
        "enrichment": enrichment,
        "stats": {
            "total_samples": len(samples),
            "group_count": len({sample["group"] for sample in samples if sample["group"]}),
        },
        "analysis": {
            "enrichment": {"top_n": config.get("analysis", {}).get("enrichment", {}).get("top_n", 12)},
            "deg": {"log2fc_threshold": deg_parameters.get("LFC", 1), "pvalue_threshold": deg_parameters.get("PVAL", 0.05)},
        },
        "report": {"type": "rna-seq", "layout": "single", "output_format": ["pdf", "html"]},
        "ai": {"enabled": False},
    }

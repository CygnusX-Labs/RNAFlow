#!/usr/bin/env python3
"""Batch runner for RNAFlow's shared KEGG enrichment script."""

import argparse
import csv
import os
import subprocess
import sys


def parse_args():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(
        description="Run KEGG ORA for every contrast in a DEG statistics table."
    )
    parser.add_argument("--deg_info", required=True,
                        help="All_Contrast_DEG_Statistics.csv; first column holds contrast names")
    parser.add_argument("--deg_dir", required=True,
                        help="Directory containing per-contrast DEG result tables")
    parser.add_argument("--out_dir", required=True, help="Output directory")
    parser.add_argument("--organism", required=True, help="KEGG organism code, e.g. sly")
    parser.add_argument("--gene_col", default="ENSEMBL",
                        help="Gene ID column in the DEG table (default: ENSEMBL)")
    parser.add_argument("--id_map",
                        help="Headerless two-column TSV: source gene ID <TAB> KEGG gene ID")
    parser.add_argument("--kegg_rscript",
                        default=os.path.abspath(os.path.join(
                            here, "..", "..", "src", "src", "Enrichments", "kegg_enricher.r")),
                        help="Path to kegg_enricher.r (default: RNAFlow src/src/Enrichments)")
    parser.add_argument("--pattern", default="{contrast}_DEG.csv",
                        help="Per-contrast file name pattern (default: {contrast}_DEG.csv)")
    parser.add_argument("--cutoff", default="0.05", help="KEGG adjusted p-value cutoff")
    parser.add_argument("--padj_th", default="0.05", help="DEG adjusted p-value threshold")
    parser.add_argument("--lfc_th", default="1", help="DEG absolute log2 fold-change threshold")
    return parser.parse_args()


def read_contrasts(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return [row[0].strip() for row in reader if row and row[0].strip()]


def main():
    args = parse_args()
    contrasts = read_contrasts(args.deg_info)
    if not contrasts:
        sys.exit("No contrasts found in " + args.deg_info)

    os.makedirs(args.out_dir, exist_ok=True)
    failures = []
    for contrast in contrasts:
        table = os.path.join(args.deg_dir, args.pattern.format(contrast=contrast))
        if not os.path.isfile(table):
            print(f"[skip] missing input: {table}", file=sys.stderr)
            failures.append(contrast)
            continue

        cmd = [
            "Rscript", args.kegg_rscript,
            "--table", table,
            "--name", contrast,
            "--out_dir", args.out_dir,
            "--organism", args.organism,
            "--gene_col", args.gene_col,
            "--cutoff", args.cutoff,
            "--padj_th", args.padj_th,
            "--lfc_th", args.lfc_th,
        ]
        if args.id_map:
            cmd.extend(["--id_map", args.id_map])

        print("[run] " + " ".join(cmd), flush=True)
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            failures.append(contrast)

    if failures:
        sys.exit("KEGG enrichment failed for: " + ", ".join(failures))


if __name__ == "__main__":
    main()

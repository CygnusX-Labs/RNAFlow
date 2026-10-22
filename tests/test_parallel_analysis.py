"""Exercise scheduling, output merging, and failure propagation without R dependencies."""

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEG = ROOT / "src/src/DEG/run_deg_parallel.py"
ENRICH = ROOT / "src/src/Enrichments/deg_enrich_wrapper.py"
FAKE_R = r'''
import csv, json, os, sys, time
from pathlib import Path

script, *args = sys.argv[1:]
def flag(*names, default=None):
    for name in names:
        if name in args:
            return args[args.index(name) + 1]
    return default
def event(kind):
    item = {"kind": kind, "pid": os.getpid(), "time": time.monotonic(),
            "script": script, "name": flag("-n", "--name"),
            "pca": "--skip-pca" not in args, "args": args,
            "blas": os.getenv("OPENBLAS_NUM_THREADS"), "omp": os.getenv("OMP_NUM_THREADS")}
    fd = os.open(os.environ["FAKE_R_EVENTS"], os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    os.write(fd, (json.dumps(item) + "\n").encode())
    os.close(fd)
event("start")
time.sleep(0.25)
if "--counts" in args:
    with open(flag("--pairs"), newline="") as handle:
        pairs = list(csv.DictReader(handle))
    failed = any(pair["Treat"] == "Fail" for pair in pairs)
    output = Path(flag("--outdir"))
    output.mkdir(parents=True, exist_ok=True)
    if not failed:
        with (output / "All_Contrast_DEG_Statistics.csv").open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Contrast", "Control", "Treat", "Total_DEG"])
            for pair in pairs:
                name = pair["Treat"] + "_vs_" + pair["Control"]
                writer.writerow([name, pair["Control"], pair["Treat"], 7])
                (output / (name + "_DEG.csv")).write_text("GeneID,pvalue\ngene1,0.01\n")
        (output / flag("--log_file")).write_text("worker log\n")
        if "--skip-pca" not in args:
            (output / "Global_PCA_Combined.pdf").write_text("PCA\n")
else:
    failed = flag("-n", "--name") == "Fail_vs_C"
    output = Path(flag("-d", "--out_dir"))
    output.mkdir(parents=True, exist_ok=True)
    if not failed:
        (output / (flag("-n", "--name") + "_" + Path(script).stem + ".csv")).write_text("ID,Count\nGO:1,3\n")
event("end")
sys.exit(7 if failed else 0)
'''


class ParallelAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rnaflow-parallel-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        fake = self.base / "Rscript"
        fake.write_text(f"#!{sys.executable}\n" + FAKE_R)
        fake.chmod(0o755)
        self.events = self.base / "events.jsonl"
        self.env = dict(os.environ, PATH=str(self.base) + os.pathsep + os.environ["PATH"],
                        FAKE_R_EVENTS=str(self.events), OPENBLAS_NUM_THREADS="32", OMP_NUM_THREADS="32")
        self.output = self.base / "output"

    def invoke(self, script, args):
        return subprocess.run([sys.executable, str(script), *map(str, args)], env=self.env,
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def make_pairs(self, treats):
        path = self.base / "pairs.csv"
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Control", "Treat"])
            writer.writerows(("C", name) for name in treats)
        return path

    def deg_args(self, treats, threads):
        return ["--counts", "counts.tsv", "--metadata", "samples.csv", "--pairs", self.make_pairs(treats),
                "--outdir", self.output, "--threads", threads]

    def enrich_args(self, names, threads, missing=()):
        info = self.base / "statistics.csv"
        with info.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Contrast"])
            writer.writerows((name,) for name in names)
        tables = self.base / "tables"
        tables.mkdir(exist_ok=True)
        for name in names:
            if name not in missing:
                (tables / f"{name}_DEG.csv").write_text("GeneID,padj,log2FoldChange\ngene1,0.01,2\n")
        kegg = self.base / "kegg.json"
        kegg.write_text(json.dumps({"enabled": True, "organism": "sly"}))
        return ["--rscript", "go.r", "--kegg_rscript", "kegg.r", "--kegg_config", kegg,
                "--deg_info", info, "--deg_dir", tables, "--obo", "go.obo", "--assoc", "assoc.tsv",
                "--out_dir", self.output, "--threads", threads, "--padj_th", "0.02", "--lfc_th", "1.5"]

    def read_events(self):
        return [json.loads(line) for line in self.events.read_text().splitlines()]

    def assert_concurrency(self, expected):
        active = peak = 0
        for event in sorted(self.read_events(), key=lambda item: item["time"]):
            active += 1 if event["kind"] == "start" else -1
            peak = max(peak, active)
            self.assertEqual(event["blas"], "1")
            self.assertEqual(event["omp"], "1")
        self.assertEqual(active, 0)
        self.assertEqual(peak, expected)

    def test_deg_parallel_merges_input_order_and_runs_pca_once(self):
        treats = ["B", "A", "E", "D", "F"]
        result = self.invoke(DEG, self.deg_args(treats, 2))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_concurrency(2)
        starts = [event for event in self.read_events() if event["kind"] == "start"]
        self.assertEqual(sum(event["pca"] for event in starts), 1)
        with (self.output / "All_Contrast_DEG_Statistics.csv").open(newline="") as handle:
            self.assertEqual([row["Treat"] for row in csv.DictReader(handle)], treats)
        self.assertEqual(len(list(self.output.glob("*_DEG.csv"))), 5)
        self.assertTrue((self.output / "Global_PCA_Combined.pdf").exists())
        self.assertEqual(len(list((self.output / "logs").glob("*.console.log"))), 2)

    def test_deg_caps_workers_at_number_of_contrasts(self):
        result = self.invoke(DEG, self.deg_args(["A", "B"], 99))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_concurrency(2)

    def test_deg_serial_and_worker_failure(self):
        args = self.deg_args(["A", "B"], 1)
        result = self.invoke(DEG, args)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_concurrency(1)
        result = self.invoke(DEG, self.deg_args(["A", "Fail"], 2))
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse((self.output / "All_Contrast_DEG_Statistics.csv").exists())
        self.assertTrue(list(self.output.glob(".deg-workers-*")))

    def test_enrichment_parallel_keeps_go_and_kegg_sequential_per_contrast(self):
        names = ["A_vs_C", "B_vs_C", "D_vs_C"]
        result = self.invoke(ENRICH, self.enrich_args(names, 2))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_concurrency(2)
        events = self.read_events()
        for name in names:
            sequence = [(e["script"], e["kind"]) for e in events if e["name"] == name]
            self.assertEqual(sequence, [("go.r", "start"), ("go.r", "end"), ("kegg.r", "start"), ("kegg.r", "end")])
        self.assertEqual(len(list((self.output / "logs").glob("*.console.log"))), 3)
        for event in events:
            if event["kind"] == "start":
                self.assertIn("0.02", event["args"])
                self.assertIn("1.5", event["args"])

    def test_enrichment_fails_for_r_error_and_missing_input(self):
        result = self.invoke(ENRICH, self.enrich_args(["Fail_vs_C", "Missing_vs_C", "A_vs_C"], 2, missing=["Missing_vs_C"]))
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("Fail_vs_C", result.stdout)
        self.assertIn("Missing_vs_C", result.stdout)
        self.assertTrue((self.output / "A_vs_C_kegg.csv").exists())
        self.assertFalse((self.output / "Fail_vs_C_kegg.csv").exists())

    def test_both_wrappers_reject_nonpositive_threads(self):
        for script, args in [(DEG, self.deg_args(["A"], 0)), (ENRICH, self.enrich_args(["A_vs_C"], 0))]:
            with self.subTest(script=script):
                result = self.invoke(script, args)
                self.assertEqual(result.returncode, 2, result.stdout)
        self.assertFalse(self.events.exists())

    def test_deg_skill_manifest_forwards_threads(self):
        manifest = self.base / "deg.json"
        manifest.write_text(json.dumps({"mode": "deseq2", "counts": "counts.tsv", "metadata": "samples.csv",
                                        "pairs": str(self.make_pairs(["A", "B"])), "threads": 2}))
        result = self.invoke(ROOT / "src/skills/deg/scripts/run_deg.py", ["--input", manifest, "--output", self.output])
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_concurrency(2)
        summary = json.loads((self.output / "summary.json").read_text())
        self.assertEqual(summary["status"], "success")
        self.assertIn("--threads", summary["command"])

    def test_enrichment_skill_manifest_forwards_threads_and_failure(self):
        self.enrich_args(["A_vs_C", "Fail_vs_C"], 2)
        manifest = self.base / "enrich.json"
        manifest.write_text(json.dumps({"mode": "batch", "obo": "go.obo", "assoc": "assoc.tsv",
                                        "deg_info": str(self.base / "statistics.csv"),
                                        "deg_dir": str(self.base / "tables"), "threads": 2}))
        result = self.invoke(ROOT / "src/skills/enrichments/scripts/run_enrichment.py", ["--input", manifest, "--output", self.output])
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assert_concurrency(2)
        summary = json.loads((self.output / "summary.json").read_text())
        self.assertEqual(summary["status"], "failed")
        self.assertIn("--threads", summary["command"])

    def test_external_failure_logs_survive_output_cleanup(self):
        logs = self.base / "workflow-logs"
        result = self.invoke(DEG, [*self.deg_args(["A", "Fail"], 2), "--log-dir", logs])
        self.assertNotEqual(result.returncode, 0, result.stdout)
        shutil.rmtree(self.output)
        self.assertTrue(list(logs.glob("*.console.log")))
        self.assertTrue(list(logs.glob(".deg-workers-*")))
        result = self.invoke(ENRICH, [*self.enrich_args(["Fail_vs_C"], 1), "--log-dir", logs])
        self.assertNotEqual(result.returncode, 0, result.stdout)
        shutil.rmtree(self.output)
        self.assertTrue((logs / "Fail_vs_C.console.log").exists())


if __name__ == "__main__":
    unittest.main()

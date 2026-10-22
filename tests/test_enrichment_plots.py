"""Test the Python GO chart independently of optional enrichment packages."""

import ast
import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/src/Enrichments/python/go_enrich.py"


class PythonEnrichmentPlotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rnaflow-go-plot-")
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        env = patch.dict(os.environ, {"MPLCONFIGDIR": str(self.output / "matplotlib")})
        env.start()
        self.addCleanup(env.stop)
        tree = ast.parse(SOURCE.read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "plot_enrichment_top_terms")
        namespace = {"pd": pd, "textwrap": textwrap, "Path": Path}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), "exec"), namespace)
        self.plot = namespace["plot_enrichment_top_terms"]

    def assert_images(self):
        for extension, magic in [("png", b"\x89PNG\r\n\x1a\n"), ("pdf", b"%PDF")]:
            file = self.output / f"GO_enrichment_top10.{extension}"
            self.assertGreater(file.stat().st_size, 1000)
            self.assertTrue(file.read_bytes().startswith(magic))

    def test_top10_ranked_by_adjusted_p_with_duplicate_names(self):
        data = pd.DataFrame({"Term": ["Duplicated pathway"] * 15 + ["Not significant"],
                             "Adjusted P-value": [i / 1000 for i in range(15)] + [0.5],
                             "Overlap": [f"{i + 1}/100" for i in range(16)]}).iloc[::-1]
        selected = self.plot(data, self.output)
        self.assertEqual(len(selected), 10)
        self.assertEqual(selected['Adjusted P-value'].tolist(), [i / 1000 for i in range(10)])
        self.assert_images()

    def test_fewer_than10_and_empty_results_produce_images(self):
        data = pd.DataFrame({"Term": ["Pathway A", "Pathway B"],
                             "Adjusted P-value": [0.001, 0.002], "Overlap": ["3/100", "5/100"]})
        self.assertEqual(len(self.plot(data, self.output)), 2)
        self.assert_images()
        self.assertTrue(self.plot(pd.DataFrame(), self.output).empty)
        self.assert_images()
        data['Adjusted P-value'] = 0.5
        self.assertTrue(self.plot(data, self.output).empty)
        self.assert_images()


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_public_release.py"
SPEC = importlib.util.spec_from_file_location("check_public_release", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicReleaseTests(unittest.TestCase):
    def test_clean_tree_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text("A generic project skill.", encoding="utf-8")
            self.assertEqual(MODULE.findings(Path(directory)), [])

    def test_private_path_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.md"
            path.write_text("See /Users/example/Projects/private", encoding="utf-8")
            result = MODULE.findings(Path(directory))
            self.assertEqual(len(result), 1)
            self.assertIn("macOS user path", result[0])


if __name__ == "__main__":
    unittest.main()

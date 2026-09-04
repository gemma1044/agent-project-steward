from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/project-steward/scripts/render_dashboard.py"
SPEC = importlib.util.spec_from_file_location("render_dashboard", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DashboardTests(unittest.TestCase):
    def test_renders_missions_and_escapes_input(self):
        output = MODULE.render_dashboard(
            {
                "title": "Demo <Project>",
                "missions": [{"name": "Audit", "status": "active", "note": "<script>x</script>"}],
                "resources": [],
                "decisions": [],
            }
        )
        self.assertIn("Demo &lt;Project&gt;", output)
        self.assertIn("&lt;script&gt;x&lt;/script&gt;", output)
        self.assertNotIn("<script>x</script>", output)

    def test_blocks_unsafe_link_schemes(self):
        rendered = MODULE.render_links([{"label": "bad", "href": "javascript:alert(1)"}])
        self.assertEqual(rendered, "<span>bad</span>")

    def test_renders_gates_screenshots_and_self_evolution(self):
        output = MODULE.render_dashboard(
            {
                "title": "Demo",
                "missions": [
                    {
                        "name": "Mission",
                        "gates": {"tests": "pass"},
                        "screenshots": [{"label": "Proof", "href": "evidence/proof.png"}],
                    }
                ],
                "resources": [],
                "decisions": [],
                "self_evolution": [
                    {"failure": "missed callback", "root_cause": "soft rule", "rule_change": "hard callback", "validation": "pass"}
                ],
            }
        )
        self.assertIn("<b>tests:</b> pass", output)
        self.assertIn('src="evidence/proof.png"', output)
        self.assertIn("Self-evolution", output)
        self.assertIn("missed callback", output)

    def test_blocks_unsafe_screenshot_schemes(self):
        rendered = MODULE.render_screenshots(
            [{"label": "bad", "href": "javascript:alert(1)"}]
        )
        self.assertNotIn("<img", rendered)

    def test_example_renders(self):
        state = ROOT / "skills/project-steward/examples/dashboard-state.example.json"
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "dashboard.html"
            data = __import__("json").loads(state.read_text(encoding="utf-8"))
            destination.write_text(MODULE.render_dashboard(data), encoding="utf-8")
            self.assertGreater(destination.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()

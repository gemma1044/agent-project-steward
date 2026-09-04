from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/portfolio-steward/scripts/steward.py"
SPEC = importlib.util.spec_from_file_location("steward", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PortfolioStewardTests(unittest.TestCase):
    def make_template(self, root: Path) -> Path:
        template = root / "template"
        template.mkdir()
        (template / "SKILL.md").write_text(
            "---\nname: project-steward\ndescription: test\n---\n\n# Test\n\n## Discovery\n\nRule\n\n## Callback\n\nRule\n",
            encoding="utf-8",
        )
        (template / "references").mkdir()
        (template / "references/rule.md").write_text("detail\n", encoding="utf-8")
        return template

    def init_child(self, root: Path) -> tuple[Path, Path]:
        template = self.make_template(root)
        child = root / "child"
        child.mkdir()
        args = type(
            "Args",
            (),
            {
                "target": str(child),
                "template": str(template),
                "name": "child-steward",
                "skills_dir": ".codex/skills",
                "control_dir": ".steward",
            },
        )()
        MODULE.command_init(args)
        return child, template

    def test_init_makes_full_copy_core_snapshot_and_local_rules(self):
        with tempfile.TemporaryDirectory() as temporary:
            child, template = self.init_child(Path(temporary))
            skill = child / ".codex/skills/child-steward"
            base = child / ".steward/base/core"
            local = skill / "references/local/repository-rules.md"
            self.assertTrue(local.is_file())
            self.assertEqual(
                MODULE.tree_hash(skill, (Path("references/local"),)), MODULE.tree_hash(base)
            )
            manifest = json.loads((child / ".steward/port-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual([item["disposition"] for item in manifest["sections"]], ["keep", "keep"])
            lineage = json.loads((child / ".steward/lineage.json").read_text(encoding="utf-8"))
            self.assertEqual(lineage["schema_version"], 2)
            self.assertEqual(lineage["local_rules_dir"], "references/local")

    def test_status_reports_child_drift_and_upstream_change(self):
        with tempfile.TemporaryDirectory() as temporary:
            child, template = self.init_child(Path(temporary))
            skill = child / ".codex/skills/child-steward/SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8") + "\n## Local rule\n", encoding="utf-8")
            report = MODULE.status_report(child, template)
            self.assertTrue(report["child_modified"])
            self.assertIn("Local rule", report["added_child_sections"])
            (template / "SKILL.md").write_text(
                (template / "SKILL.md").read_text(encoding="utf-8") + "\n## Upstream rule\n",
                encoding="utf-8",
            )
            self.assertTrue(MODULE.status_report(child, template)["upstream_changed"])

    def test_status_does_not_treat_always_owned_local_rules_as_core_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            child, template = self.init_child(Path(temporary))
            local = child / ".codex/skills/child-steward/references/local/repository-rules.md"
            local.write_text(local.read_text(encoding="utf-8") + "\nLocal test command.\n", encoding="utf-8")
            report = MODULE.status_report(child, template)
            self.assertFalse(report["child_modified"])
            self.assertEqual(report["local_rule_files"], 1)

    def test_evolve_and_harvest_keep_files_as_durable_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            child, _ = self.init_child(root)
            args = type(
                "Args",
                (),
                {
                    "target": str(child),
                    "failure": "worker did not report completion",
                    "root_cause": "callback was optional",
                    "rule_change": "require a terminal callback",
                    "evidence": ["two reproductions"],
                    "validation": ["forward test"],
                    "scope": "upstream_candidate",
                    "privacy_review": "passed",
                    "id": "EV-test",
                },
            )()
            MODULE.command_evolve(args)
            registry = root / "registry.json"
            registry.write_text(
                json.dumps({"schema_version": 1, "children": [{"name": "child", "path": "child"}]}),
                encoding="utf-8",
            )
            report = MODULE.harvest_registry(registry)
            self.assertEqual(report["summary"]["ready_for_review"], 1)
            self.assertEqual(report["proposals"][0]["id"], "EV-test")

    def test_init_refuses_to_overwrite_child_steward(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            child, template = self.init_child(root)
            args = type(
                "Args",
                (),
                {
                    "target": str(child),
                    "template": str(template),
                    "name": "child-steward",
                    "skills_dir": ".codex/skills",
                    "control_dir": ".steward",
                },
            )()
            with self.assertRaises(ValueError):
                MODULE.command_init(args)


if __name__ == "__main__":
    unittest.main()

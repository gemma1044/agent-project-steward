from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillLayoutTests(unittest.TestCase):
    def test_skill_names_match_directories(self):
        for skill_dir in (ROOT / "skills").iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            self.assertTrue(skill_file.exists(), skill_dir.name)
            frontmatter = skill_file.read_text(encoding="utf-8").split("---", 2)[1]
            self.assertIn(f"name: {skill_dir.name}\n", frontmatter)
            self.assertIn("description:", frontmatter)

    def test_repo_view_has_help(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "skills/repo-view/serve.py"), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()

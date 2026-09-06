from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_SKILL = ROOT / "skills/portfolio-steward/SKILL.md"
PROJECTION = ROOT / "skills/portfolio-steward/references/steward-runtime-protocol.md"


class RuntimeProtocolSyncTests(unittest.TestCase):
    def test_projection_is_current(self):
        result = subprocess.run(
            [sys.executable, "scripts/sync_runtime_protocol.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_portfolio_steward_loads_runtime_protocol(self):
        skill = PORTFOLIO_SKILL.read_text(encoding="utf-8")
        self.assertIn("references/steward-runtime-protocol.md", skill)
        self.assertIn("必须完整读取", skill)

    def test_projection_contains_critical_coordination_gates(self):
        text = PROJECTION.read_text(encoding="utf-8")
        for anchor in (
            "伪执行预警与纠偏消息",
            "Session 上下文衰竭与接续",
            "Worktree 与服务来源证据",
            "五门完成标准",
            "复核不能排队停工",
            "终态回传协议",
            "wait_threads",
            "heartbeat 定时巡检",
            "非绿灯与资源申请",
            "每轮巡检的最小收尾",
        ):
            self.assertIn(anchor, text)
        self.assertIn("feishu-portfolio-dashboard.md", text)
        self.assertNotIn("references/dashboard-schema.md", text)


if __name__ == "__main__":
    unittest.main()

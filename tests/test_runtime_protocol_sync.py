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
            "周期巡检必须做双源对账",
            "待办账本 SSOT",
            "登记为“孤儿执行”",
            "<仓库名> 管家",
            "不得因 Mission 状态变化反复重命名",
            "恢复稳定管家标题",
            "非绿灯与资源申请",
            "混合结论必须拆成原子实验记录",
            "不得提供或显示“部分接受”",
            "共享同一 Run",
            "调用数与费用记为 0",
            "用户明确决定暂缓实施",
            "每轮巡检的最小收尾",
        ):
            self.assertIn(anchor, text)
        self.assertIn("feishu-portfolio-dashboard.md", text)
        self.assertNotIn("references/dashboard-schema.md", text)
        self.assertNotIn("### “部分接受”必须继续实施", text)


if __name__ == "__main__":
    unittest.main()

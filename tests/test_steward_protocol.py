from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/project-steward/SKILL.md"


class StewardProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_task_discovery_and_semantic_titles_are_preserved(self):
        self.assertIn("活跃、闲置和归档 Session", self.text)
        self.assertIn("list_threads", self.text)
        self.assertIn("list_archived_threads", self.text)
        self.assertIn("read_thread", self.text)
        self.assertIn("set_thread_title", self.text)
        self.assertIn("【当前状态】语义化目标（可选编号）", self.text)
        self.assertIn("clientThreadId", self.text)

    def test_terminal_callback_protocol_is_hard_requirement(self):
        self.assertIn("send_message_to_thread", self.text)
        self.assertIn("最后一个工具动作", self.text)
        self.assertIn("回传失败时重试一次", self.text)
        self.assertIn("不会仅因另一个 Session 结束就自动", self.text)

    def test_event_wait_and_heartbeat_fallback_are_preserved(self):
        self.assertIn("wait_threads", self.text)
        self.assertIn("automation_update", self.text)
        self.assertIn("heartbeat 定时巡检", self.text)
        self.assertIn("默认可建议 10 分钟", self.text)
        self.assertIn("不能替代终态回传与事件等待", self.text)

    def test_review_handoff_resource_and_self_evolution_are_preserved(self):
        self.assertIn("复核不能排队停工", self.text)
        self.assertIn("Session 上下文衰竭与接续", self.text)
        self.assertIn("同一轮对话显式提出申请", self.text)
        self.assertIn("## 自进化", self.text)

    def test_pseudo_execution_warning_requires_dual_evidence_and_atomic_recovery(self):
        self.assertIn("伪执行预警与纠偏消息", self.text)
        self.assertIn("startedAt`–`completedAt", self.text)
        self.assertIn("共享现场无法归因或证据冲突时，不得记 strike", self.text)
        self.assertIn("下一条可立即执行的原子动作", self.text)
        self.assertIn("阈值由仓库 local rules 配置", self.text)

    def test_worktree_and_service_provenance_are_required_for_ui_acceptance(self):
        self.assertIn("Worktree 与服务来源证据", self.text)
        self.assertIn("任务 cwd、实际 Git worktree、浏览器 URL 背后的服务进程是三种不同身份", self.text)
        self.assertIn("核验监听 PID 的 cwd 或启动命令", self.text)
        self.assertIn("服务来源不明时，它只能作为历史或数据参考", self.text)

    def test_partial_acceptance_requires_implementation_closure(self):
        self.assertIn("“部分接受”必须继续实施", self.text)
        self.assertIn("关联原 Mission 与实验", self.text)
        self.assertIn("未接受语义", self.text)
        self.assertIn("合入正式基线并完成最终验收", self.text)
        self.assertIn("用户明确决定暂缓实施", self.text)
        self.assertIn("不得用“实验已结束”", self.text)


if __name__ == "__main__":
    unittest.main()

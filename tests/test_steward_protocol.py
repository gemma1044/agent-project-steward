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

    def test_steward_identity_titles_are_stable(self):
        self.assertIn("<仓库名> 管家", self.text)
        self.assertIn("Agent Harness Prompt 管家（Sol｜总控）", self.text)
        self.assertIn("标题最前面禁止添加", self.text)
        self.assertIn("READY、REVIEW、BLOCKED、待目检、待用户决策", self.text)
        self.assertIn("不通过改写管家 Session 标题表达", self.text)
        self.assertIn("普通执行 / 评审 Session", self.text)
        self.assertIn("恢复稳定管家标题", self.text)
        self.assertIn("不得因 Mission 状态变化反复重命名", self.text)

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

    def test_periodic_patrol_reconciles_work_ledger_and_sessions(self):
        self.assertIn("周期巡检必须做双源对账", self.text)
        self.assertIn("待办账本 SSOT", self.text)
        self.assertIn("Codex Session 是执行资源", self.text)
        self.assertIn("明确包含“待办”", self.text)
        self.assertIn("优先续推仍可用的原 Session", self.text)
        self.assertIn("登记为“孤儿执行”", self.text)
        self.assertIn("不让执行 Session 空等占用资源", self.text)
        self.assertIn("巡检只扫 Session / 旧 Markdown", self.text)

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

    def test_mixed_experiment_outcomes_are_split_into_atomic_records(self):
        self.assertIn("混合结论必须拆成原子实验记录", self.text)
        self.assertIn("不得提供或显示“部分接受”", self.text)
        self.assertIn("已接受行", self.text)
        self.assertIn("未接受或实验无效行", self.text)
        self.assertIn("共享同一 Run", self.text)
        self.assertIn("调用数与费用记为 0", self.text)
        self.assertIn("用户明确决定暂缓实施", self.text)
        self.assertNotIn("### “部分接受”必须继续实施", self.text)


if __name__ == "__main__":
    unittest.main()

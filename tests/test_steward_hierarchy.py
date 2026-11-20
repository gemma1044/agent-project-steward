from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "skills/project-steward"
CHIEF = ROOT / "skills/chief-steward/SKILL.md"
PORTFOLIO = ROOT / "skills/portfolio-steward/SKILL.md"


class StewardHierarchyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = (PROJECT / "SKILL.md").read_text(encoding="utf-8")
        cls.chief = CHIEF.read_text(encoding="utf-8")

    def test_roles_and_model_tiers(self):
        self.assertIn("三层分工与模型档位", self.project)
        for anchor in ("低成本模型", "强推理模型", "执行档模型"):
            self.assertIn(anchor, self.project)
        self.assertIn("不得把技术或产品细节交给大总管审核或拍板", self.project)
        self.assertIn("不继承自己的强推理模型", self.project)

    def test_escalation_levels_and_project_group(self):
        self.assertIn("## 汇报等级与待审文件", self.project)
        for level in ("L0 自理", "L1 管家审", "L2 上报用户", "L3 提级"):
            self.assertIn(level, self.project)
        self.assertIn("技术细节一律 L1", self.project)
        self.assertIn("### 项目群", self.project)
        self.assertIn("成员只有大总管和项目管家", self.project)

    def test_worker_budget_replaces_per_session_approval(self):
        self.assertIn("员工预算", self.project)
        self.assertIn("不必逐个征求同意", self.project)
        self.assertIn("超出预算或未设预算", self.project)
        self.assertIn("同一轮对话显式提出申请", self.project)

    def test_ledger_handoff_and_runtime_references(self):
        self.assertIn("必须先在待审台账写一条文件记录，再发终态回传", self.project)
        self.assertIn("references/review-ledger.md", self.project)
        self.assertIn("references/runtimes.md", self.project)
        ledger = (PROJECT / "references/review-ledger.md").read_text(encoding="utf-8")
        for anchor in ("pending_manager", "pending_user", "waiting_review", "watch", "decided_by"):
            self.assertIn(anchor, ledger)
        runtimes = (PROJECT / "references/runtimes.md").read_text(encoding="utf-8")
        for anchor in ("Codex", "Claude Code", "Antigravity", "OpenClaw", "未核实", "sub-agent"):
            self.assertIn(anchor, runtimes)

    def test_ledger_example_is_consistent(self):
        data = json.loads((PROJECT / "examples/review-ledger.example.json").read_text(encoding="utf-8"))
        worker_ids = {w["id"] for w in data["workers"]}
        for f in data["files"]:
            self.assertIn(f["worker_id"], worker_ids)
            self.assertIn(f["level"], {"L0", "L1", "L2", "L3"})
        waiting = {w["id"] for w in data["workers"] if w["status"] == "waiting_review"}
        for wid in waiting:
            self.assertTrue(any(f["worker_id"] == wid and f["blocking"] for f in data["files"]))

    def test_items_only_cover_human_steps(self):
        self.assertIn("只把需要人做的步骤列成事项", self.project)
        ledger = (PROJECT / "references/review-ledger.md").read_text(encoding="utf-8")
        self.assertIn("事项拆分门", ledger)
        self.assertIn("why_human", ledger)
        self.assertIn("不区分“里程碑”和“事项”", ledger)
        self.assertIn("不用多维表格或电子表格当用户界面", ledger)
        self.assertIn("不把 AI 的执行步骤列成一二三", self.chief)
        data = json.loads((PROJECT / "examples/review-ledger.example.json").read_text(encoding="utf-8"))
        files = {f["id"]: f for f in data["files"]}
        for item in data["items"]:
            self.assertTrue(item["why_human"])
            if item["source"] == "review":
                self.assertEqual(files[item["file_id"]]["status"], "pending_user")

    def test_chief_steward_boundaries(self):
        for anchor in ("不审专业内容", "不判汇报等级", "不派员工", "不替用户批复", "保留原话", "按需读取"):
            self.assertIn(anchor, self.chief)

    def test_portfolio_is_not_the_chief(self):
        text = PORTFOLIO.read_text(encoding="utf-8")
        self.assertIn("Portfolio Steward（母版管家）", text)
        self.assertIn("不是个人管家体系里的“大总管”", text)


if __name__ == "__main__":
    unittest.main()

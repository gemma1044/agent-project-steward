# 实现层：三层个人管家体系与汇报等级

## 改动范围

| 文件 | 改动 |
|---|---|
| `skills/project-steward/SKILL.md` | 新增“三层分工与模型档位”“汇报等级与待审文件”“项目群”；派单改为员工预算内自主新建；回传增加台账记录 ID 与建议等级；决策边界与每轮收尾同步更新；巡检前读台账并按运行时映射工具 |
| `skills/project-steward/references/review-ledger.md` | 新增：台账三类记录、员工与文件状态机、读写权限 |
| `skills/project-steward/references/runtimes.md` | 新增：Codex / Claude Code / Antigravity / OpenClaw 能力对照，区分已核实与未核实 |
| `skills/project-steward/examples/review-ledger.example.json` | 新增：合成示例 |
| `skills/project-steward/references/local/repository-rules.md` | 追加管家体系配置模板（运行时、项目群、台账、员工预算） |
| `skills/chief-steward/` | 新增大总管 Skill 与 agent 元数据 |
| `skills/portfolio-steward/`、`scripts/sync_runtime_protocol.py`、`README.md` | “大总管”改称“母版管家”；母版管家声明自己不是 `chief-steward` |
| `skills/portfolio-steward/references/steward-runtime-protocol.md` | 由同步脚本重新生成 |
| `tests/test_steward_hierarchy.py` | 新增层级、等级、预算、台账、大总管边界的锚点测试 |

## 兼容性

- `$project-steward` 调用名不变；原有协作协议（任务发现、标题、回传、等待、巡检、五门、伪执行、交接）全部保留，既有测试不改。
- 未在 local rules 设员工预算的仓库，新建 Session 仍需用户同意，与旧行为一致。
- 未配置台账的仓库，“读台账”一步无事可做；管家应建议配置，但不因此停工。
- 已派生的子仓库管家不自动获得这些规则；需要时由母版管家走三方同步。
- `portfolio-steward` 的技术标识与脚本行为不变，只改中文称呼。

## 验收要点

1. 项目管家规则中，大总管不审专业内容、员工用执行档模型、L1/L2 判定标准、员工预算内自主新建均有明确条文。
2. 台账文档能回答：员工等审时写什么、谁能改等级、哪些文件进入用户待审、用户批复由谁转写。
3. 运行时对照表中每项能力都标明已核实或未核实，未核实的不当作可用。
4. 大总管 Skill 明确列出不做的四件事，并给出转交路径。
5. `python3 scripts/sync_runtime_protocol.py --check`、全部单测、公开发布扫描通过。

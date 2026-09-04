# 实现层：组合式 Agent Stud 架构

## 实施方案

保留现有 `project-steward/SKILL.md` 原文作为完整 core，避免拆散已验证的协作协议；新增 `references/local/` 作为子仓库独有规则包。`portfolio-steward` 的初始化脚本仍先完整复制模板，但额外确保 local rule pack 存在，并只为排除 local 后的 core 建立 base snapshot。lineage 标注 core/local 边界；状态检查忽略 local 漂移；演化记录保留 `local` 与 `upstream_candidate` 分类。

## 兜底与边界

- 旧 schema v1 lineage 继续可读，视为整份副本的 legacy 模式；新 init 写 v2。
- local 文件不存在时，管家仍执行完整 core。
- 脚本不自动同步或覆盖目标仓库；冲突只能报告。
- 新建子仓库前如目标路径存在，继续拒绝覆盖。

## 基本数据 schema

- `lineage.json`: `schema_version`、`core_paths`、`local_path`、`base_core`、上游版本。
- `evolution`: 保留失败、根因、规则、证据、验证与脱敏结论；`scope` 仅为 `local` 或 `upstream_candidate`。

## 验收要点

1. 原协作协议逐字保留在 core Skill 本体，入口可路由到 local reference。
2. init 产出完整子 Skill、immutable core base 和 always-owned local rules。
3. 修改 local 不会报告为 core drift；修改 core 会报告。
4. 既有 v1 子仓库的 status 与 harvest 仍可使用。

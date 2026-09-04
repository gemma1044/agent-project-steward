# Agent Project Steward

一个面向 Codex/Agent 工作区的开源工具包：用项目管家协调多个任务，用只读 Repo Viewer 查看代码现状与 Session Diff。

仓库包含两个可独立安装、可组合使用的 Skill：

- `project-steward`：按 Mission 管理多 Session 工作，先盘点与去重，再申请资源、派单、督办和独立验收。
- `repo-view`：在本地浏览器查看源码树、工作区改动、分支相对基线的 Diff 与逐 commit Diff。

两者保持独立是有意设计：浏览代码是低风险只读动作；创建、续推和验收 Session 是项目治理动作。`project-steward` 可以选择调用 `repo-view`，但普通浏览请求不会加载整套调度协议。

## Dashboard

项目看板由结构化 JSON 生成，不手工维护整份 HTML：

```bash
python3 skills/project-steward/scripts/render_dashboard.py \
  skills/project-steward/examples/dashboard-state.example.json \
  /tmp/project-steward-dashboard.html
```

输出是零依赖的单文件 HTML，可直接在浏览器打开。输入字段见 `skills/project-steward/references/dashboard-schema.md`。

## 安装

克隆仓库后，将所需 Skill 目录复制或软链到你的 Agent Skill 目录。不同客户端的 Skill 根目录不同，请以客户端文档为准。

```bash
git clone https://github.com/gemma1044/agent-project-steward.git
ln -s "$PWD/agent-project-steward/skills/project-steward" ~/.codex/skills/project-steward
ln -s "$PWD/agent-project-steward/skills/repo-view" ~/.codex/skills/repo-view
```

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_public_release.py .
python3 scripts/check_public_release.py . --deny private-project --deny private-domain.example
```

## English

Agent Project Steward is a two-skill toolkit for coordinating multi-session engineering work and inspecting repositories through a local, read-only browser. The dashboard is generated deterministically from JSON, and the two skills remain independently invocable.

## License

MIT

# 跨运行时接口

`SKILL.md` 用 Codex 的工具名描述协作协议。项目管家或员工运行在其他编程运行时上时，按本表找等价能力。治理要求不变：派单前查重、正式 Session 标识核验、终态回传作为最后一个动作、台账先于回传、五门验收。

“已核实”表示截至本文件最后修改时，在该运行时的公开文档或本机命令帮助中确认过；“未核实”的能力不得当作已存在使用，先在 local rules 记录实测结果。

## 能力对照

| 能力 | Codex | Claude Code | Antigravity | OpenClaw（大总管常用） |
|---|---|---|---|---|
| 新建 Session 并拿到标识 | App：`create_thread`；CLI：`codex exec --json` 的事件流里有线程 ID（已核实） | CLI：`claude -p --session-id <uuid>` 指定新会话 ID（已核实）；桌面版：新建会话工具 | 未核实 | `sessions_spawn`，`runtime: "acp"` 可指定 `agentId` 为 codex 或 claude（已核实） |
| 向已有 Session 追加一轮 | App：`send_message_to_thread`；CLI：`codex exec resume <SESSION_ID> "<prompt>"`（已核实） | CLI：`claude -p --resume <session-id> "<prompt>"`（已核实）；桌面版：会话间发消息工具 | 未核实 | `sessions_send`；续接旧会话依赖目标支持 `session/load`，Codex 与 Claude Code 支持（已核实） |
| 等待结束或需关注 | App：`wait_threads` | 无内建跨会话等待；用 `-p` 同步运行，或靠会话结束钩子写台账 | 未核实 | `sessions_yield` |
| 发现全部 Session | App：`list_threads` / `list_archived_threads` | 本机会话记录目录；桌面版：会话列表工具 | 未核实 | 会话列表工具 |
| 会话结束钩子 | 配置 `notify` 命令，回合结束时调用 | `settings.json` 的 `Stop` / `SessionEnd` hook | 未核实 | 不适用 |
| 指定模型 | 创建时传模型参数 | `--model` | 未核实 | 由 `agentId` 对应运行时决定 |

## 各运行时注意事项

### Codex

- `clientThreadId` 只是 worktree 初始化句柄，不能用于回传或等待；拿到正式线程 ID 后才算派单完成。
- 一个 Session 结束不会自动通知另一个 Session，必须在任务书里写明回传目标。

### Claude Code

- 员工必须是独立的顶层会话，不能用会话内的 sub-agent 代替：sub-agent 跑完即把结果交回，不能单独续接，也不能挂自己的待审文件。会话内 sub-agent 只适合员工自己的内部并行。
- `-p` 模式每次调用跑一轮后退出；长任务由项目管家用 `--resume` 续接，不要让管家主会话同步阻塞等待。
- 回传可以用两种方式之一：员工最后一个动作是调用 `claude -p --resume <管家会话ID>` 发回传；或员工写台账，由管家巡检读取。前者是主通道，后者是兜底。

### Antigravity

- 本仓库尚未核实其会话创建、续接、跨会话消息和钩子接口。在某个项目首次用作项目管家或员工前，先实测上表各项，把结果写入该项目的 `references/local/repository-rules.md`，再提 upstream candidate 更新本表。
- 实测完成前，Antigravity 上的员工只能用“员工写台账 + 管家巡检”的方式回传，不能声称已有事件通知。

### OpenClaw

- 通过后台命令加系统事件发“完成通知”的做法会被静默丢弃（上游 issue openclaw/openclaw#50398）；要用 `sessions_spawn` 加 `sessions_yield`，或让员工写台账。
- 大总管在 OpenClaw 上运行时只用会话工具传话和读状态，不用它派员工；派员工是项目管家的职责。

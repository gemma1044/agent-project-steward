# 跨运行时接口

`SKILL.md` 用 Codex 的工具名描述协作协议。项目管家或员工运行在其他编程运行时上时，按本表找等价能力。治理要求不变：派单前查重、正式 Session 标识核验、终态回传作为最后一个动作、台账先于回传、五门验收。

“已核实”表示截至本文件最后修改时，在该运行时的公开文档或本机命令帮助中确认过；“未核实”的能力不得当作已存在使用，先在 local rules 记录实测结果。

## 能力对照

| 能力 | Codex | Claude Code | Antigravity | OpenClaw（大总管常用） |
|---|---|---|---|---|
| 新建 Session 并拿到标识 | App：`create_thread`；CLI：`codex exec --json` 的事件流里有线程 ID（已核实） | CLI：`claude -p --session-id <uuid>` 指定新会话 ID（已核实）；桌面版：新建会话工具 | CLI：`agy -p "<任务>" --output-format json`，返回 JSON 含 `conversation_id`、`status`、`response`、`denied_actions`；`agy acp` 提供 ACP stdio 服务，已核实（2026-11-20，agy 1.5.13） | `sessions_spawn`，`runtime: "acp"` 可指定 `agentId` 为 codex 或 claude（已核实） |
| 向已有 Session 追加一轮 | App：`send_message_to_thread`；CLI：`codex exec resume <SESSION_ID> "<prompt>"`（已核实） | CLI：`claude -p --resume <session-id> "<prompt>"`（已核实）；桌面版：会话间发消息工具 | CLI：`agy -p "<追加指令>" --conversation <conversation_id>` 续接同一对话；`-c` / `--continue` 续最近一个对话，已核实（2026-11-20，agy 1.5.13） | `sessions_send`；续接旧会话依赖目标支持 `session/load`，Codex 与 Claude Code 支持（已核实） |
| 等待结束或需关注 | App：`wait_threads` | 无内建跨会话等待；用 `-p` 同步运行，或靠会话结束钩子写台账 | 无内建跨会话等待；`agy -p` 同步执行，进程结束即一轮完成，返回后读 JSON；长任务以“员工写台账 + 管家巡检”为准，已核实（2026-11-20，agy 1.5.13） | `sessions_yield` |
| 发现全部 Session | App：`list_threads` / `list_archived_threads` | 本机会话记录目录；桌面版：会话列表工具 | 未核实列举全部会话命令；派单返回 `conversation_id` 由管家记录，`-c` / `--continue` 续最近对话（2026-11-20，agy 1.5.13） | 会话列表工具 |
| 会话结束钩子 | 配置 `notify` 命令，回合结束时调用 | `settings.json` 的 `Stop` / `SessionEnd` hook | 未核实到会话结束钩子或推送通知；长任务以“员工写台账 + 管家巡检”为准（2026-11-20，agy 1.5.13） | 不适用 |
| 指定模型 | 创建时传模型参数 | `--model` | `--model`（`agy models` 列出可用模型），另支持 `--effort`、`--mode`（`accept-edits` / `auto` / `plan`）、`--add-dir`、`--project`、`--print-timeout`，已核实（2026-11-20，agy 1.5.13） | 由 `agentId` 对应运行时决定 |

## 各运行时注意事项

### Codex

- `clientThreadId` 只是 worktree 初始化句柄，不能用于回传或等待；拿到正式线程 ID 后才算派单完成。
- 一个 Session 结束不会自动通知另一个 Session，必须在任务书里写明回传目标。

### Claude Code

- 员工必须是独立的顶层会话，不能用会话内的 sub-agent 代替：sub-agent 跑完即把结果交回，不能单独续接，也不能挂自己的待审文件。会话内 sub-agent 只适合员工自己的内部并行。
- `-p` 模式每次调用跑一轮后退出；长任务由项目管家用 `--resume` 续接，不要让管家主会话同步阻塞等待。
- 回传可以用两种方式之一：员工最后一个动作是调用 `claude -p --resume <管家会话ID>` 发回传；或员工写台账，由管家巡检读取。前者是主通道，后者是兜底。

### Antigravity

- **派单与参数**：员工统一使用 Homebrew cask `antigravity-cli` 安装的 `agy`（2026-11-20 本机实测版本 1.5.13）。用 `agy -p "<任务>" --output-format json` 无人值守执行一轮，返回 JSON 包含 `conversation_id`、`status`、`response`、`denied_actions`。另支持 `--model`（`agy models` 列出可用模型）、`--effort`、`--mode`（`accept-edits` / `auto` / `plan`）、`--add-dir`、`--project`、`--print-timeout`；`agy acp` 提供 ACP stdio 服务。
- **续接**：用 `agy -p "<追加指令>" --conversation <conversation_id>` 续接同一对话并保留上文；`-c` / `--continue` 续接最近一个对话。
- **按目录放行权限**：无人值守时，需要授权的工具调用（如 `write_file`）会被自动拒绝并列在 `denied_actions`。派单时用 `--settings '{"permissions":{"allow":["write_file(<目录绝对路径>/**)"]}}'` 只对本次会话放行指定目录，不写入全局设置；macOS 上 `/tmp` 要写成解析后的真实路径 `/private/tmp`。`--dangerously-skip-permissions` 会放行全部工具，管家默认不用。
- **回传方式**：`agy -p` 是同步的，进程结束即一轮完成，管家可在命令返回后直接读 JSON；未核实到会话结束钩子或推送通知，长任务仍以“员工写台账 + 管家巡检”为准。
- **不用 `agentapi`**：桌面 App 自带的 `agentapi`（`~/.gemini/antigravity/bin/agentapi`）也能开对话，但对话不绑定工作区，写文件会停在 App 里等人批准，不适合无人值守派单；员工统一用 `agy`。

### OpenClaw

- 通过后台命令加系统事件发“完成通知”的做法会被静默丢弃（上游 issue openclaw/openclaw#50398）；要用 `sessions_spawn` 加 `sessions_yield`，或让员工写台账。
- 大总管在 OpenClaw 上运行时只用会话工具传话和读状态，不用它派员工；派员工是项目管家的职责。

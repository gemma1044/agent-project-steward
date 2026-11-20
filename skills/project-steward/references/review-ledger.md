# 待审台账（Review Ledger）

待审台账是员工、项目管家、大总管和用户共用的唯一事实来源，记录“谁在跑、产出了什么文件、文件现在等谁”。它解决的问题是：长任务里需要审的东西只留在某个 Session 的对话里，没人记得回去看。

台账是逻辑结构，载体由 local rules 指定，同一用户只用一个：

- **本地文件**：一个目录下的 JSON Lines，按记录类型分文件（`workers.jsonl`、`files.jsonl`、`events.jsonl`），只追加不改写，读取时按 `id` 取最新一条。适合单人、单机。
- **飞书多维表格或等价结构化表**：三张表对应三类记录，字段同下。适合多端查看、手机 App 读取。

手机 App、看板和大总管都只读这份台账，不另存一份。

## 记录类型

### 员工（worker）

| 字段 | 含义 |
|---|---|
| `id` | 稳定 ID |
| `project` | 所属项目 |
| `task` | 这个员工负责的任务，一句话 |
| `runtime` | `codex` / `claude-code` / `antigravity` / `openclaw` / 其他 |
| `session_id` | 运行时里的 Session 标识，用于续接 |
| `parent_session_id` | 派它出来的项目管家 Session |
| `model` | 实际使用的模型 |
| `status` | 见下方员工状态机 |
| `watch` | 用户是否提级盯这个员工（布尔） |
| `updated_at` | 最后更新时间 |

### 文件（file）

| 字段 | 含义 |
|---|---|
| `id` | 稳定 ID |
| `project` / `worker_id` | 归属 |
| `title` / `kind` | 标题；类型：方案、文档、PR、交接包、报告 |
| `location` | 文件路径、PR 链接或文档 URL；正文不进台账 |
| `ask` | 要审的人看什么、决定什么，一两句话 |
| `level` | `L0` / `L1` / `L2` / `L3`，含义见 `project-steward/SKILL.md` 的“汇报等级与待审文件” |
| `level_suggested_by_worker` | 员工建议的等级，供项目管家参考 |
| `status` | 见下方文件状态机 |
| `blocking` | 员工是否停着等这份文件的结论 |
| `decision` | 审核结论与意见原文 |
| `decided_by` | `manager` / `user` |
| `created_at` / `updated_at` | 时间 |

### 事件（event）

只追加的流水：谁在什么时间把哪条记录从什么状态改成什么状态，以及原因。用于回放、对账和统计“等了多久”。

## 员工状态机

```text
排队 queued → 执行中 running → 等审 waiting_review → 执行中 running → … → 完成 done
                     ↘ 受阻 blocked（等外部依赖，写明解锁条件）
                     ↘ 失败 failed / 已交接 handed_off
```

- 进入 `waiting_review` 前必须已有至少一条 `blocking: true` 的文件记录；否则这是“丢在对话里”的等审，项目管家巡检时按遗漏回传处理。
- 会话结束钩子只能把状态改成“会话已停止，待核对”，最终状态由项目管家依据回传和五门证据判定。

## 文件状态机

```text
L0：留档 archived（不进入审核）

L1：待管家审 pending_manager → 管家通过 manager_approved
                             → 管家打回 manager_changes → 员工改完重新提交 → 待管家审

L2：待管家审 pending_manager → 已上报 escalated → 待用户审 pending_user
        → 用户通过 user_approved / 用户要改 user_changes → 管家下达给员工

L3（提级员工的文件）：直接进入 待用户审 pending_user；管家可附意见但不拦截
```

- 只有 `pending_user` 状态的文件会在用户的事项列表里生成一条“待审”事项；用户批复后该事项自动完成。
- 项目管家可以把 L1 改判为 L2；大总管不能改等级。
- 被新版本替代的文件标 `superseded` 并指向新记录，不删除。

## 读写权限

| 角色 | 可写 | 只读 |
|---|---|---|
| 员工 | 自己的 worker 记录；自己产出的文件（新建、补充、建议等级） | 自己的文件结论 |
| 项目管家 | 本项目的全部 worker 与 file 记录；等级判定；L1 结论；L2 上报 | 其他项目 |
| 大总管 | 用户的事项、文件的 `decision`（只转写用户原话，标 `decided_by: user`） | 所有项目的 worker 与 file |
| 用户 | 任何记录 | — |

大总管转写用户批复时必须保留原话，不总结、不改写、不补充专业判断；用户只说“同意”时就记“同意”。

## 示例

`examples/review-ledger.example.json` 给出一组合成数据：一个项目、三个员工、四份不同等级和状态的文件。

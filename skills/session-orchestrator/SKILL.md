---
name: session-orchestrator
description: >
  Orchestrate parallel issue execution across Claude Code desktop sessions: the main
  session dispatches one issue per spawn_task chip (user click = approval) into an
  isolated worktree child session, the child runs the project's resolution workflow
  (e.g. subagent-workflow), and every task-level decision is uplinked to the main
  session via SendMessage instead of AskUserQuestion. Use when the user wants multiple
  issues driven from one coordinating session ("主session调度", "开子session处理issues",
  "跨session并行"). Not for single-issue in-session work (run subagent-workflow
  directly), terminal-only environments, or delegating permission approvals.
version: "0.1.0"
---

# Session Orchestrator

The main session (the one loading this skill) is dispatcher, arbiter, and acceptor — it
never implements. Each issue gets its own child desktop session in an isolated git
worktree. Children execute; decisions flow up; artifacts flow down for independent
acceptance.

## Prerequisites

Abort with a clear message if any is missing:

- Claude Code **desktop** session with the cross-session toolset: `ListAgents`,
  `SendMessage`, `mcp__ccd_session__spawn_task`, and the `mcp__ccd_session_mgmt__*`
  tools (`list_sessions`, `list_events`, `send_message`). Headless or plain-terminal
  sessions cannot run this skill.
- A target repository with a concrete issue list and a resolution workflow the child
  can invoke (default: `/subagent-workflow`; any project skill works — name it in the
  spawn prompt).

## Mechanism facts (empirically verified, design around them)

- **Chip = approval gate.** `spawn_task` proposes; only the user's click creates the
  session. There is no zero-click way to create a sidebar session — do not look for one.
- **Wake semantics.** `SendMessage` wakes an idle desktop session in both directions
  (parent→child and child→parent), even after its turn ended. Plain terminal sessions
  sitting at a prompt may never drain the queue — do not route decisions through them.
- **Dialogs are sovereign.** A session blocked on `AskUserQuestion` or a permission
  prompt consumes no peer messages until its own UI unblocks it. Peer messages can
  never answer a dialog. Never attempt it; never relay a denied permission to another
  session (permission laundering).
- **Model is not inheritable.** The chip session uses the desktop's default model
  config. If the user wants a specific model/effort (e.g. opus:high) for children,
  they set the desktop default or switch inside the child after start. State this in
  the dispatch summary so the user can act before children do heavy work.
- **Message-form addressing.** Reply to whatever name appears in the incoming
  `<cross-session-message from="...">` attribute; discover children in `ListAgents`
  by worktree codename after the start notification arrives.

## Lifecycle

1. **Intake.** Collect the issue list from the user (or enumerate with `gh`). Order by
   dependency; pick serial vs parallel; cap concurrent children (default 3) so
   arbitration stays responsive. Present the dispatch plan once — issue → chip mapping,
   the model caveat above — then start dispatching.
2. **Dispatch.** One issue per `spawn_task` chip, prompt from the template below,
   `cwd` = target repo root. The chip runs in a fresh worktree automatically.
3. **Handshake.** On the start notification, find the new peer in `ListAgents` and wait
   for the child's startup report. Record its peer name and worktree path.
4. **Execution & arbitration.** The child runs the resolution workflow. Decision
   uplink replaces dialogs:
   - Child never calls `AskUserQuestion`; it sends the decision request to the main
     session and waits.
   - Main session answers **within the issue's original mandate**: approach choices,
     tie-breaks, interpretation of acceptance criteria.
   - Main session escalates to its own user (here `AskUserQuestion` is legitimate —
     the main session's user is the real approver) for: scope changes, destructive or
     irreversible operations, anything resembling a permission grant, and conflicts
     between children.
5. **Milestones.** Child reports at: started, plan fixed, blocked, done. Silence past
   an expected milestone → read its transcript via `list_events` before assuming
   progress; a child stuck on a permission prompt in its own UI is invisible otherwise —
   tell the user which session needs their click.
6. **Acceptance.** Verify artifacts independently from the main session (read files in
   the child worktree, run tests, check the PR). Never accept on the child's report
   alone.
7. **Teardown.** Summarize per-issue outcomes for the user; the user archives child
   sessions (unchanged worktrees auto-clean). Dismiss stale chips with `dismiss_task`.

## Spawn prompt template

Fill the bracketed slots; keep the numbered discipline verbatim:

```text
你是母 session 派生的执行者。任务：解决 [repo] 的 issue #[N]（[one-line summary]）。

1. 在本 worktree 内用 [/subagent-workflow 或指定 skill] 完成该 issue，遵守项目自身规范。
2. 决策纪律：全程禁止 AskUserQuestion。任何二义性、方案取舍、验收标准解释，用
   SendMessage 上行给母 session（收到过母 session 消息就回复其 from 名字；否则用
   ListAgents 找 [parent peer name]），发完结束轮次安静等待，不要自行拍板。
3. 里程碑上报（SendMessage，单行简报）：开工 / 方案确定 / 受阻 / 完成。
4. 权限提示例外：工具授权类弹窗只能由用户在你的 UI 上处理，弹了就等，不要找母
   session 代批。
5. 完成标准：[tests/validation command] 通过，按项目规范提交；最终报告包含改动
   文件清单与验证结果。
```

## Caveats

- The uplink discipline is prompt-level, not enforced by the harness; a child that
  drifts into `AskUserQuestion` simply blocks on its own UI — detect via milestone
  silence and `list_events`, remind it via `SendMessage` (consumed after the user
  unblocks the dialog).
- Permission prompts always land in the child's UI. Budget for the user clicking
  through them, or have the user pick a laxer permission mode in the child — that is
  the user's call, never the orchestrator's.
- Do not orchestrate through plain terminal peers; their queues may never drain.
- Messages to a busy child queue until its next tool round — expect latency, not loss.

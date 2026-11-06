# Instruction Guard

PreToolUse hook：任何对 `AGENTS.md` / `CLAUDE.md`（任意目录层级）的修改，都必须先经用户审批。覆盖文件编辑类工具和可能写文件的 shell 命令。

## 解决什么问题

根指令文件是 agent 的行为合同。模型在"顺手优化"、自我复盘、或执行 bootstrap 类 skill 时会改写它们，而这类改动一旦漏审，就会悄悄改变之后所有会话的行为。靠"不要改指令文件"的自然语言约束不可靠——本 hook 把它变成机械审批点。

## 各平台的审批方式

三家的 hook API 能力不同，审批方式按平台走最强的那条：

| 平台        | 拦截面                                       | 审批方式                                                                                                                                                                                |
| ----------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code | `Edit\|Write\|MultiEdit\|NotebookEdit\|Bash` | 返回 `permissionDecision: "ask"`，Claude Code 弹出原生权限确认，用户点允许才执行。实测 `bypassPermissions` 下的 `claude -p` 不会自动放行，而是拒绝                                      |
| omp         | `edit` / `write` / `bash`                    | 有 UI 时用 omp 自带确认框（`ctx.ui.confirm`）询问，等待时间不计入 handler 超时；无 UI（`omp -p`）时拦截并给出审批命令                                                                   |
| Codex       | `apply_patch` / `Bash`                       | Codex 0.158 的 PreToolUse 不支持 `ask`（二进制报 `unsupported permissionDecision:ask`），所以先拦截（exit 2），把审批命令写进拒绝原因；用户在自己的终端执行后，模型重试同一改动即可通过 |

Codex 与无 UI omp 的审批命令（拦截信息里会给出完整路径）：

```bash
bash .codex/hooks/instruction-guard/instruction-guard.sh approve AGENTS.md
```

- 一次性：每个文件一张令牌，用一次即作废；一个补丁改多个指令文件时，每个都要批。
- 15 分钟过期（`INSTRUCTION_GUARD_TTL` 秒数可调）。
- 令牌存在项目之外的 `${XDG_STATE_HOME:-~/.local/state}/instruction-guard/approvals/`，不会被提交；Codex 的 workspace-write 沙箱里模型写不到这里。
- 模型自己执行 `approve`、或用编辑工具 / shell 命令写令牌目录，都会被拦下。

## 判定规则

- **文件工具**：目标路径的文件名恰为 `AGENTS.md` 或 `CLAUDE.md` 即拦（`AGENTS.md.bak`、`MY_AGENTS.md` 不拦）。Codex 的 `apply_patch` 解析补丁头 `*** Add/Update/Delete File:` 与 `*** Move to:`。
- **shell 命令**：命令里出现指令文件名，且含任一写入迹象——重定向 `>`/`>>`（`2>&1`、`>/dev/null` 除外）、`tee`、`sed -i`、`perl -i`、`mv/cp/rm/ln/touch/...`、改工作区的 `git checkout/restore/reset/...`、`--write`、`-delete`、`python -c`/heredoc 这类内联脚本。宁可多问：`cp AGENTS.md /tmp/x` 也会触发一次审批。只读命令（`cat`、`grep`、`git diff` 等）直接放行。

## 安装

```bash
npx my-agents install hook instruction-guard            # 全平台
npx my-agents install hook instruction-guard --platform claude
```

安装 = 拷贝脚本到 `<project>/.claude/hooks/instruction-guard/`（及 `.codex/hooks/…`、`.omp/hooks/…`）+ 把配置片段按 hook 命令幂等 merge 进 `.claude/settings.json` / `.codex/hooks.json`；omp 把 `omp.ts` 拷到 `.omp/hooks/pre/instruction-guard.ts`。卸载只摘除本包条目。

与 worktree-guard / review-gate 不同，本 hook **装上即生效**，没有启用清单。安装后紧接着运行 `project-instruction-bootstrap` 写 `CLAUDE.md` / `AGENTS.md` 时，也会经过这道审批——这正是预期行为。

## 限制

- shell 检测是启发式：不点名指令文件就写入的命令（例如 `npm run sync-instructions` 这类由脚本内部生成 `AGENTS.md` 的流程）不拦截。生成型项目的源片段（如 `instructions/root/*.md`）本 hook 不管。
- 无头 Claude Code（`claude -p`）没有审批界面，`ask` 一律被拒；需要在无头流程里改指令文件时，先卸载本 hook 或用 `--permission-prompt-tool`。
- 交互式 Claude Code 在 `bypassPermissions` 模式下的弹窗行为，官方文档没有明确说明；已实测的是无头 bypass 模式下会拒绝，不会放行。
- 需要 `python3`，只用标准库；以 `python3 -I` 隔离模式运行，项目里的同名模块（如 `json.py`）不会让 guard 失效。
- omp 有 UI 时的确认框路径未做交互实测；无 UI 的拦截路径（edit 与 bash 工具）已实测。

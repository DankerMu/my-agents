# Review Gate

PreToolUse hook：`subagent-workflow` 的两轮修复额度用尽后，机械拒绝 `implementer` / `reviewer` 子代理派发（exit 2），把原因喂回给编排器。拦截发生在派发瞬间：第三轮修复根本起不来，而不是事后在 PR 历史里发现又多跑了几轮。

## 解决什么问题

"两轮修复后还有 P0/P1 就停、报给用户"写成散文规则时靠执行模型自律。真实运行中模型会凭"finding 在减少"的印象续跑。本 hook 把这条规则从"记得停"变成"停不下来也派不出去"。

## 工作方式

职责切分：**计数在 CLI，拦截在 hook，零逻辑重复。**

1. 计数器 CLI `fix_gate.py` 随 `subagent-workflow` skill 分发（`<skill>/scripts/fix_gate.py`）。编排器在 cross-review 开始时 `open --pr <N>`，每轮裁定后 `record-round --sha <sha> --clean|--not-clean`。每个 not-clean 轮买一次修复；第三个 not-clean 轮把 `locked: true` 和 `lockReason` 预计算进 `<project>/.review-gate.json`，CLI 同时 exit 2。
2. 本 hook 常驻但**默认 no-op**：只有 `.review-gate.json` 存在时才启用。它只读 `enabled` / `locked` / `lockReason` / `blockedSubagents` 四个字段，不含任何 gate 逻辑。
3. `locked: true` 时，子代理派发调用（Claude Code：`Task`，按 `subagent_type`；Codex：`collaboration.spawn_agent` / `followup_task`，按 payload 中的 agent 名字段；omp：`task`，按 `agent` 字段）命中 `blockedSubagents`（默认 `implementer`、`reviewer`）即被拒绝。`verifier`、`explorer`、`monitor`、`issue-scribe` 不受影响。
4. 解锁唯一路径：用户拍板后 `fix_gate.py extend --user-approved "<一行决定>"`，额度 +1、决定记入状态文件。
5. PR 合并或放弃后 `fix_gate.py close` 删除状态文件，hook 回到 no-op。

```text
编排器                       CLI (skill 分发)             hook (本包)
record-round --not-clean ──▶ 第 3 次 → locked ──▶ .review-gate.json
                                                        │
spawn implementer/reviewer ─────────────────────────────┴──▶ locked? → exit 2 拒绝
```

## 安装

```bash
npx my-agents install hook review-gate            # 全平台
npx my-agents install hook review-gate --platform claude
npx my-agents install hook review-gate --platform omp
```

安装动作 = 拷贝脚本到 `<project>/.claude/hooks/review-gate/`（及 `.codex/hooks/…`）+ 把配置片段幂等 merge 进 `<project>/.claude/settings.json`（及 `.codex/hooks.json`）。merge 以 hook 命令为单位：同 `matcher` 的既有块里只补缺失的 `command`；卸载只摘除本包的 `command`，用户手写的 hooks 原样保留。

omp 平台没有 hooks 配置文件：安装时把 `omp.ts` 工厂拷到 `<project>/.omp/hooks/pre/review-gate.ts`（脚本拷到 `.omp/hooks/review-gate/`），omp 启动时作为扩展模块加载，在 `tool_call` 事件里匹配 `task` 工具并调用同一份 shell 脚本；退出码 2 翻译为 `{ block, reason }`。

## 限制

- Codex matcher 从 payload 的常见字段（`agent`/`agent_type`/`name`/`role`/`target_agent` 等）提取 agent 名；字段名不在候选集内时放行（fail-open），此时靠 CLI 的 exit 2 兜底。
- 用自定义 agent 名跑 implementer 职能可绕过；那是故意违规，状态文件里的轮次记录仍在。
- 编排器从不运行 CLI 时状态文件不存在，hook 无从拦截；"每轮必须 `record-round`"是 skill 的硬规则，`.review-gate.json` 缺失时 merge 前检查视为跳过了 review 记账。
- 需要 `python3`（仅标准库）。

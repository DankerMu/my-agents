# Review Gate

PreToolUse hook：`subagent-workflow` 三轮硬门锁定期间，机械拒绝 `implementer` / `reviewer` 子代理派发（exit 2），把原因喂回给编排器自我纠正。拦截点在浪费发生之前——第 4 轮评审或 retro 前的修复任务在**派发瞬间**被挡下，而不是在 pre-merge 末端检查才发现违规、回头重走流程。

## 解决什么问题

三轮硬门（第 3 个 comprehensive cross-review 轮不 clean → 必须先持久化 Review Failure Retro）此前是散文条件，靠执行模型自律。真实运行中执行模型会凭"finding 数在下降"的印象续跑普通循环，跳过 retro 直接修复+第四轮评审。本 hook 把这条规则从"记得检查"变成"违规动作直接失败"。

## 工作方式

职责切分：**逻辑在 CLI，拦截在 hook，零重复**。

1. 状态机 CLI `review_gate.py` 随 `subagent-workflow` skill 分发（`<skill>/scripts/review_gate.py`），编排器每轮评审后用它记账（`record-round`）。CLI 重算 gate 状态并把 `locked` / `lockReason` **预计算**进 `<project>/.review-gate.json`，同时向 `<REVIEW_DIR>/round-ledger.log` 追加人类可读的 ledger 行。
2. 本 hook 常驻但**默认 no-op**：只有 `.review-gate.json` 存在时才启用。它只读 `locked` 字段，不含任何 gate 逻辑。
3. `locked: true` 时，子代理派发调用（Claude Code：`Task`，按 `subagent_type` 匹配；Codex：`collaboration.spawn_agent` / `followup_task`，按 payload 中的 agent 名字段匹配；omp：`task`，按 `agent` 字段匹配）命中 `blockedSubagents`（默认 `implementer`、`reviewer`）即被拒绝；`verifier` 及其他辅助子代理（explorer、monitor、issue-scribe）不受影响——裁决刚结束的轮次仍需要它们。
4. 解锁唯一路径：持久化 retro 后运行 `record-retro --path <retro.md> --shape <breadth|depth|noise|converging>`。CLI 在此处机械校验 `converging` 资格（任一轮同类复发、第 3 轮及以后出现 critical/major、逐轮数字非单调、每 PR 已用过一次、到达第 5 轮，任一条即拒绝），并按 shape 设定 post-gate 预算（converging 2 轮，pivot 1 轮）——预算耗尽仍不 clean 则重新锁定。
5. PR 合并或放弃后 `close` 删除状态文件，hook 回到 no-op。

```text
编排器                    CLI (skill 分发)              hook (本包)
record-round  ──────────▶ 重算 locked ──▶ .review-gate.json
                                              │
spawn implementer/reviewer ───────────────────┴──▶ locked? → exit 2 拒绝
```

## 安装

```bash
npx my-agents install hook review-gate            # 全平台
npx my-agents install hook review-gate --platform claude
npx my-agents install hook review-gate --platform omp
```

安装动作 = 拷贝脚本到 `<project>/.claude/hooks/review-gate/`（及 `.codex/hooks/…`）+ 把配置片段幂等 merge 进 `<project>/.claude/settings.json`（及 `.codex/hooks.json`）。卸载按 deep-equal 摘除本包写入的条目。

omp 平台没有 hooks 配置文件：安装时把 `omp.ts` 工厂拷到 `<project>/.omp/hooks/pre/review-gate.ts`（脚本拷到 `.omp/hooks/review-gate/`），omp 启动时将其作为扩展模块加载，在 `tool_call` 事件里匹配 `task` 工具并调用同一份 shell 脚本；退出码 2 翻译为 `{ block, reason }`。卸载删除这两处文件。

## 与 subagent-workflow 的配合

`subagent-workflow` 0.21.0 起，Phase 4/6.5 的 Round Ledger 簿记在 CLI 可用时通过 `record-round` 完成，Phase 5 的 retro 持久化后通过 `record-retro` 注册，Phase 8 合并后 `close`。hook 未安装时纪律仍由编排器自持（与 `worktree-guard`/`monitor`/`issue-scribe` 同一可选模式）；hook 安装后，跳过 retro 的普通派发从"不该做"变成"做不了"。

## 限制

- Codex matcher 覆盖 `collaboration.spawn_agent` / `followup_task`（兼容带/不带 `collaboration.` 前缀），agent 名从 payload 的常见字段（`agent`/`agent_type`/`name`/`role`/`target_agent` 等）中提取；字段名不在候选集内时放行（fail-open）——此时 Codex 侧机械层退回 CLI 当场拒绝 + 违规 ledger 行 + pre-merge 确定性兜底。确认真实 payload 字段后应收紧候选集。
- 拦截依赖 agent 类型命名与 `blockedSubagents` 匹配；用自定义 agent 名跑 implementer 职能可绕过——那属于故意违规，由 ledger 违规行 + accountability log 兜底。
- 编排器完全不记账（从不运行 CLI）时状态文件不存在，hook 无从拦截；"每轮必须记 ledger 行"本身是 skill 0.20.0 起的硬规则，缺行在 pre-merge 硬门是 skip block。
- 需要 `python3`（仅标准库）。

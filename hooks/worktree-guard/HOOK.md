# Worktree Guard

PreToolUse hook：文件写入前校验目标路径是否在声明的 worktree 根之内，越界即拒绝（exit 2），并把原因喂回给模型自我纠正。

## 解决什么问题

多 worktree 并行开发时，编排器/模型会在会话重启、compact、cwd 复位后把改动写回主仓库而不是声明的 worktree。这类漂移靠自然语言约束不可靠——本 hook 把它变成机械拦截。

## 工作方式

1. 安装后 hook 常驻，但**默认是 no-op**：只有项目根存在 `.worktree-guard.json` 时才启用，所以可以安全地装到所有项目。
2. 进入 worktree 模式时，由编排器（或你手动）在项目根写入清单：

```json
{
  "enabled": true,
  "allowedRoots": [".worktrees/issue-42"]
}
```

3. 此后所有 `Edit|Write|MultiEdit|NotebookEdit`（Claude Code）/ `apply_patch`（Codex）调用都会被校验：目标路径不在任何 `allowedRoots` 之内 → 拒绝，stderr 提示写回模型。
4. 退出 worktree 模式时删除该清单文件（或置 `"enabled": false`）。

## 安装

```bash
npx my-agents install hook worktree-guard            # 双平台
npx my-agents install hook worktree-guard --platform claude
```

安装动作 = 拷贝脚本到 `<project>/.claude/hooks/worktree-guard/`（及 `.codex/hooks/…`）+ 把配置片段幂等 merge 进 `<project>/.claude/settings.json`（及 `.codex/hooks.json`）。卸载按 deep-equal 摘除本包写入的条目，不碰用户手写的 hooks。

## 与 subagent-workflow 的配合

`subagent-workflow` 的并行 worktree 委派要求 orchestrator 维护 worktree manifest 并拒绝越界 diff。本 hook 是该纪律的机械底座：orchestrator 在 Phase 1/6 创建 worktree 时同步写 `.worktree-guard.json`，收尾时删除。

## 限制

- 只守文件写入类工具；Bash 里的 `mv`/`cp`/重定向不在 v1 覆盖范围。
- 需要 `python3`（仅用标准库解析 JSON，不装任何包、不改系统环境）。
- 清单里的相对路径相对项目根解析；符号链接按 realpath 归一后比较。

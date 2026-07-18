# Large File Guard

PreToolUse hook：拦截 `git commit`，当本次提交包含超过行数阈值（默认 1000 行）的文本文件时拒绝（exit 2），并把违规文件清单喂回给模型自我纠正。

## 解决什么问题

熵治理中反复出现的头号问题是大文件：模块越写越长，没人在写入时刹车，等 `repo-entropy-audit` 体检时已经是既成事实。本 hook 把"大文件该拆"从审计报告里的事后建议，变成提交时的机械前置——在债务进入 git 历史之前拦下。

## 工作方式

1. 只在工具调用命令里含 `git commit` 时激活，其余 shell 命令零开销放行。
2. 检查**本次提交会带入的文件**：暂存区文件按暂存内容计行；命令带 `-a`/`--all` 时，已跟踪且有改动的文件按工作区内容计行。二进制文件（numstat 标记）自动跳过。
3. 任一文件超过 `maxLines` → 拒绝提交，stderr 列出 `文件 (行数)` 清单和处置建议，模型可据此先拆分再提交。
4. **增量棘轮语义**：只检查本次提交触碰的文件。仓库里既有的大文件不会阻塞无关提交——直到某次提交改到它，才要求处理。这与 `control-plane-auditor` 的 metric 口径（1000+ 行是 informational 信号，单独不构成 red flag）不冲突：hook 不判定"这个文件是坏的"，只在**继续加码**的时刻强制一次显式决策（拆分或 allowlist）。

## 配置

项目根可选放置 `.large-file-guard.json`（没有该文件时按默认值运行，即装即生效）：

```json
{
  "enabled": true,
  "maxLines": 1000,
  "exclude": ["docs/data/*.csv", "src/generated/**"]
}
```

- `enabled: false` 整体关闭。
- `maxLines` 自定义阈值。
- `exclude` 追加 glob（对全路径和 basename 都匹配）。内置排除：lockfile（`*.lock`、`package-lock.json`、`pnpm-lock.yaml`、`yarn.lock`）、`*.min.*`、`*.svg`、`*.map`、`*.snap`、`dist/**`、`build/**`、`vendor/**`、`node_modules/**`。

## 安装

```bash
npx my-agents install hook large-file-guard            # 全平台
npx my-agents install hook large-file-guard --platform claude
npx my-agents install hook large-file-guard --platform omp
```

安装动作 = 拷贝脚本到 `<project>/.claude/hooks/large-file-guard/`（及 `.codex/hooks/…`）+ 把配置片段幂等 merge 进 `<project>/.claude/settings.json`（及 `.codex/hooks.json`）。Claude Code 侧 matcher 为 `Bash`，Codex 侧为 `exec_command`。卸载按 deep-equal 摘除本包写入的条目，不碰用户手写的 hooks。

omp 平台没有 hooks 配置文件：安装时把 `omp.ts` 工厂拷到 `<project>/.omp/hooks/pre/large-file-guard.ts`（脚本拷到 `.omp/hooks/large-file-guard/`），omp 启动时将其作为扩展模块加载，在 `tool_call` 事件里匹配 `bash` 工具并调用同一份 shell 脚本；退出码 2 翻译为 `{ block, reason }`。卸载删除这两处文件。

## 与熵治理的配合

- `repo-entropy-audit` / `control-plane-auditor` 负责**存量**：找出已经过大的模块并出治理清单。
- 本 hook 负责**增量**：新债务在提交时就被拦住，存量治理的成果不被回填。
- 被拦后的两条正路：拆分文件（模型收到 stderr 后可直接执行），或确认合法大文件（生成物/数据/vendored）加入 `exclude`——第二条路要求显式改配置文件，留下可审计的决策痕迹。

## 限制

- 命令检测是 `git commit` 子串匹配：`echo "git commit"` 之类会误触发检查（但只在暂存区确有超限文件时才会误拦，实际影响极小）；`cd subdir && git commit` 场景下按会话 cwd 解析仓库，跨目录提交可能漏检。
- 只守 Claude Code `Bash` / Codex `exec_command` / omp `bash` 工具发起的提交；终端里人工 `git commit` 不经过本 hook（要全覆盖可另配 git 原生 pre-commit，v1 不代管）。
- 行数按暂存/工作区文本内容计；`errors="ignore"` 解码，异常编码文件不会导致 hook 崩溃。
- 需要 `python3`（仅标准库）与 `git`。

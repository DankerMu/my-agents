# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-08

### Added

- 从 `subagent-workflow` 0.31.0 派生：相位骨架、gate 体系（round ledger / 三轮 gate / 五轮天花板 / 跨 PR 记忆）、fixture 契约、finding 契约、Phase 4.5 verdict+disposition、pre-merge 硬闸、cross-run loop log 与打包的 Python 校验脚本全部原样继承，只替换执行基座。
- `references/omp-delegation.md`（新增，本 skill 的核心差异）：codeagent-wrapper `--backend omp` 的调用契约（实测 `omp -p --mode json --auto-approve --no-title --no-skills --no-rules --model <pin>`）、模型钉死表、role contract 注入顺序、omp delegation boundary、`--parallel` 批量任务 DSL、超时与失败分类（tooling failure 不计 review round）。
- Phase 7 显式保留为原生 cc/cx `reviewer` subagent，并写明理由：Phase 0.5–6.5 全部跑在同一引擎上，合并前最后一道闸必须换引擎，否则同源盲区会让 loop 收敛到"clean"。跑到 omp 上判为 gate failure。

### Changed

- Phase 0.5 fixture review、Phase 1 实现、Phase 4/6.5 交叉评审、Phase 4.5 验证、Phase 6 修复与诊断、Phase 6.2 不变量审计：全部改为 omp 会话委派，briefs 增加 role header + 契约条目 + operating-guide 路径指针。
- `phase-4-cross-review.md`：reviewer/verifier 模板改为 omp `--parallel` 形态；verifier 明确禁止 `resume` 产出候选的会话。
- `parallel-worktree-delegation.md`：worker 通过 `workdir:` 绑定到 orchestrator 建好的 `.worktrees/`，禁用 wrapper 自带的 `--worktree`；补充 worktree-guard hook 管不到委派进程内部的作用域说明。
- `skill-map.md`：新增 Substrate 节，标注与 `subagent-workflow`（全原生兄弟）和 `codeagent`（wrapper 契约来源）的关系。

### Known limitations

- 委派会话带 `--no-skills --no-rules`，不加载任何项目 skill、`AGENTS.md`/`CLAUDE.md` 规则或 agent 定义；角色定义完全依赖 brief 注入与 operating-guide 文件路径。
- reasoning effort 只能写进 model 串（`provider/model:effort`），`--reasoning-effort` 对 omp 后端被静默丢弃；且 `:effort` 后缀仅对本地 omp 模型缓存中权威列出的模型可解析，缓存为空的 provider 需退回裸 pin。

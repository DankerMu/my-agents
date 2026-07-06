# Changelog

All notable changes to this pack will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-07-06

- 新增 `blind-spot-pass` skill：动手改陌生模块前的盲区侦察——代码库考古（历史/范式/隐形约定/危险区/邻接面）挖 unknown unknowns，产出带证据的盲区清单与更好的任务 prompt。与审计套件互补：`repo-entropy-audit` 面向全仓体检，本 skill 面向单任务开工前；发现的决策点喂 `grill-me`，值得沉淀的约定走 `grill-with-docs`。

## [0.3.0] - 2026-07-06

- 新增 `large-file-guard` hook：提交前拦截超过行数阈值（默认 1000）的文本文件——熵治理从"审计报告里的事后建议"补上"提交时的机械前置"。增量棘轮语义（只查本次提交触碰的文件）+ `.large-file-guard.json` 显式逃生口，与 `control-plane-auditor` 的 informational metric 口径不冲突。
- README 补充 Included Hooks 节。

## [0.2.0] - 2026-07-02

- Add `gh-create-issue`: the in-pack findings-to-delivery exit. `improve-codebase-architecture` (0.2.0) and `repo-entropy-audit` (0.2.0) now offer to turn confirmed audit targets into tracked issues instead of stopping at report-only recommendations; design-level targets route to `stage-change-pipeline` (installed with `agentic-issue-delivery`).
- Make the "unified persistence" claim real instead of aspirational: `future-aware-architecture` (0.3.0) ADR seeds now default to `docs/adr/`; `repo-entropy-audit` (0.2.0) and `entropy-review` (0.1.1) recognize `openspec/glossary.md` as the canonical domain glossary. The README now also states plainly that the entropy suite's quantitative baseline lives in `.entropy-baseline/`, outside the domain-persistence contract.
- Correct the `clarify` membership rationale: the `explorer` agent's declared dependency was metadata-only and has been removed (explorer 1.2.2); `clarify` stays as the shared pre-grill convergence step and the audit skills' when-not-to-use routing target.

## [0.1.0] - 2026-06-15

- Initial codebase stewardship pack: periodic/on-demand code-health governance, separate from the one-shot issue-delivery pipeline.
- Bundles `improve-codebase-architecture` (newly ported from `mattpocock/skills`), the entropy suite (`repo-entropy-audit`, `entropy-review`, `control-plane-auditor`), `future-aware-architecture`, and the shared grill base (`grill-with-docs`, `grill-me`, `clarify`), plus the `explorer` agent.
- Persistence is unified on this repo's stack: domain glossary at `openspec/glossary.md`, long-lived decisions at `docs/adr/`.
- Members intentionally overlap with `agentic-issue-delivery`; skills are references, not copies.
- README cross-links the delivery pairing overview (`docs/architecture/delivery-and-stewardship.md`) and `agentic-issue-delivery`.

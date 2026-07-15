# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2026-07-14

### Changed
- 继承铁律 #3 的事实来源措辞与 `grill-me` 0.3.2 对齐：从"codebase/文档"泛化为**环境**（codebase/文档/数据）。本 skill 的领域沉淀职责（glossary/ADR）保持仓库绑定不变。对应 `mattpocock/skills` 未发布 changeset `grilling-general-use` 对共享 grilling 基座的泛化。

## [0.2.1] - 2026-07-11

- Remove the body invocation-posture restatement; posture lives in frontmatter/description.

## [0.2.0] - 2026-07-11
- Backport the upstream `mattpocock/skills` v1.1.0 `grilling` hardening, matching `grill-me` 0.3.0. Inherited rule #3 now splits facts (look them up) from decisions (put to the user, wait for the answer — never self-answer, even when running inside `stage-change-pipeline` Stage 2).
- New inherited rule #6: confirmation stop-gate — no enacting the plan, and no `design.md`/`specs/` finalization in the convergence step, until the user confirms shared understanding has been reached. Persistence-discipline rules renumbered 6-8 → 7-9.

## [0.1.1] - 2026-07-02
- Fix a circular claim in the convergence step: this skill runs **inside** `stage-change-pipeline` Stage 2, so its round summary cannot be "Stage 2 的输入". Rephrased to say the summary feeds Stage 2 `design.md`/`specs/` finalization and Stage 3 review.

## [0.1.0] - 2026-06-15
- Initial port of `grill-with-docs`, the domain-aware variant of `grill-me`, adapted from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`).
- Adds glossary alignment, fuzzy-language sharpening, concrete-scenario boundary probing, and code cross-referencing on top of `grill-me`'s decision-tree interrogation.
- Localizes persistence to this repo's stack instead of the upstream `CONTEXT.md`/`docs/adr/` pair: ubiquitous-language glossary lives at `openspec/glossary.md` (single source of truth), long-lived decisions at `docs/adr/NNNN-slug.md`, with the upstream ADR three-gate test retained.
- Documents the division of labor between project-level ADRs and per-change OpenSpec `design.md`, and keeps `openspec/project-profile.md` lean by referencing the glossary rather than embedding terms.
- Wired into `stage-change-pipeline` Stage 2 as the domain-modeling pass.

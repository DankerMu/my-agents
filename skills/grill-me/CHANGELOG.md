# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.2] - 2026-07-14

### Changed
- 泛化适用范围：压测靶子从软件 plan/design 放宽到**任何计划、决策或想法**（description 与开篇明确"不限软件"）；事实来源措辞从 codebase 泛化为**环境**（codebase、文档、数据、其它已有产物），铁律 #3、锚定靶子、交叉核对步骤同步改写，审讯技法不变。Adapted from `mattpocock/skills` 未发布 changeset `grilling-general-use`（post-v1.1.0）。

## [0.3.1] - 2026-07-11

- Remove the body invocation-posture restatement; posture lives in frontmatter/description.

## [0.3.0] - 2026-07-11
- Backport the upstream `mattpocock/skills` v1.1.0 `grilling` hardening. Non-negotiable #3 now splits **facts** (look them up in the codebase/docs) from **decisions** (put each one to the user and wait — never answer them yourself), closing the failure mode where grill-me running inside another workflow (e.g. `stage-change-pipeline`) treated "能查就别问" as license to decide autonomously.
- New non-negotiable #7: an explicit confirmation stop-gate — the plan is not enacted until the user confirms shared understanding has been reached. The convergence summary is a proposal, not a release; the Output section names this gate for downstream stages.
- Frontmatter description updated to carry the facts-vs-decisions split.

## [0.2.0] - 2026-07-06
- New non-negotiable #6 "说不清就要 reference": when the user can't articulate a preference on a branch (unknown knowns), switch to asking for a reference (doc / screenshot / source directory — source code is best) or suggest a disposable fake-data prototype, instead of asking a third time. Adapted from Thariq's "A Field Guide to Fable: Finding Your Unknowns".
- Branch-ordering criterion added to the decision-tree step: branches whose answer would change architecture, interfaces, data models, or user-visible flows are grilled first; pure implementation-detail branches go last or are skipped.
- Cross-referenced the new sibling `blind-spot-pass` (When Not To Use + relations): it digs the territory (codebase → questions) before a plan exists; grill-me interrogates the map (plan → questions). Run blind-spot-pass first in unfamiliar territory and feed its decision points in as grill branches.

## [0.1.1] - 2026-07-02
- Fix stale persistence path in `When Not To Use`: the sibling `grill-with-docs` writes `openspec/glossary.md` (+ `docs/adr/`), not `CONTEXT.md`.
- Correct wording that called `grill-with-docs` "上游": it is a same-repo sibling (`同仓的`); the true upstream is `mattpocock/skills`. Kept the genuine upstream reference where it describes the mattpocock original.

## [0.1.0] - 2026-06-15
- Initial port of the `grill-me` skill, adapted from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`) and localized to this repo's skill conventions.
- Adversarial plan/design stress-testing: walk the decision tree branch by branch, one question at a time, each question carrying a recommended answer; resolve from the codebase instead of asking the user when possible.
- Integrated into the `stage-change-pipeline` workflow as a pre-OpenSpec design stress-test gate between Stage 1 and Stage 2.
- Scoped to conversation only: no document writes. The CONTEXT.md/ADR persistence of the upstream `grill-with-docs` variant is intentionally excluded.

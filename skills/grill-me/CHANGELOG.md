# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

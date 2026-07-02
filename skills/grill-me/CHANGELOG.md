# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-02
- Fix stale persistence path in `When Not To Use`: the sibling `grill-with-docs` writes `openspec/glossary.md` (+ `docs/adr/`), not `CONTEXT.md`.
- Correct wording that called `grill-with-docs` "上游": it is a same-repo sibling (`同仓的`); the true upstream is `mattpocock/skills`. Kept the genuine upstream reference where it describes the mattpocock original.

## [0.1.0] - 2026-06-15
- Initial port of the `grill-me` skill, adapted from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`) and localized to this repo's skill conventions.
- Adversarial plan/design stress-testing: walk the decision tree branch by branch, one question at a time, each question carrying a recommended answer; resolve from the codebase instead of asking the user when possible.
- Integrated into the `stage-change-pipeline` workflow as a pre-OpenSpec design stress-test gate between Stage 1 and Stage 2.
- Scoped to conversation only: no document writes. The CONTEXT.md/ADR persistence of the upstream `grill-with-docs` variant is intentionally excluded.

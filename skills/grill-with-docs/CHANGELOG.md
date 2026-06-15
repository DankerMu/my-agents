# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-15
- Initial port of `grill-with-docs`, the domain-aware variant of `grill-me`, adapted from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`).
- Adds glossary alignment, fuzzy-language sharpening, concrete-scenario boundary probing, and code cross-referencing on top of `grill-me`'s decision-tree interrogation.
- Localizes persistence to this repo's stack instead of the upstream `CONTEXT.md`/`docs/adr/` pair: ubiquitous-language glossary lives at `openspec/glossary.md` (single source of truth), long-lived decisions at `docs/adr/NNNN-slug.md`, with the upstream ADR three-gate test retained.
- Documents the division of labor between project-level ADRs and per-change OpenSpec `design.md`, and keeps `openspec/project-profile.md` lean by referencing the glossary rather than embedding terms.
- Wired into `stage-change-pipeline` Stage 2 as the domain-modeling pass.

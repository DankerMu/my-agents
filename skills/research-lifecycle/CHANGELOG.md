# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-07-10

- Add `scripts/provenance.py`: mechanical freeze/run/index/verify for study provenance — protocol lock digests, run records with exit codes and git identity, output checksums, and a verify gate that fails on silent protocol drift or evidence tampering.
- Wire Phase 5/6/7 to the provenance tooling and document the CLI in `references/artifact-model.md`.
- Add canonical-only `tests/` (excluded from projection) wired into the shared `npm test` validation path; declare the python>=3.9 runtime requirement.

## [0.2.0] - 2026-07-10

- Add `references/pressure-test-contract.md` as the canonical pressure-test gate shared by all research skills; Phase 5 now references it.
- Define `DECISION_RECORDED` and declare the artifact-state list the canonical study-level state vocabulary; artifact-level enums stay in their own templates and use uppercase values.
- Add one-way promotion rules from the optional `research/glossary.md` and `research/decisions/` ledgers into `openspec/glossary.md` and `docs/adr/`.
- Route `project-documentation` in Phase 9 to realign durable repository documentation after a study closes or hands off.

## [0.1.0] - 2026-07-10

- Initial lifecycle router for open-ended scientific research and research-driven capability development.
- Adds project-local research profiles, artifact states, delegated skill routing, scientific human gates, and explicit handoffs to product and engineering packs.

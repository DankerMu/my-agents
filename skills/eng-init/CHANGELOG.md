# Changelog

## [3.6.0] - 2026-09-05

### Added

- **Root instruction file ownership** (ported from the retired `control-plane-auditor` playbook): eng-init owns control-plane content; `project-instruction-bootstrap` owns write mechanics for projects that generate their root instruction files. Stage 0 records the case; generated projects get eng-init's sections written into `instructions/agents/shared.md` and regenerated, everything else gets `AGENTS.md` written directly.
- **`CLAUDE.md` bridge**: when Claude Code is named at Q1.5, `CLAUDE.md` must carry the one-line `@AGENTS.md` import — Claude Code loads `CLAUDE.md`, not `AGENTS.md`, so an eng-init control plane was invisible to that harness. New readiness criterion `claude_md_bridge` (Memory, level 2, skippable when Claude Code is not in use) with a fix recipe; the "never touch CLAUDE.md" rule narrows to "nothing beyond the import line".
- `scripts/run_unit_tests.py`; the suite now runs in the monorepo's `npm test` and `selfcheck.sh` goes through `uv run` (uv is the single prerequisite).

### Changed

- **Glossary home unified with the rest of this repo**: domain-term definitions live in `openspec/glossary.md` (`grill-me` GLOSSARY-FORMAT; one file, `## Context Map` for multi-context repos), created lazily. `CONTEXT.md` keeps project identity, bounded contexts, invariants, forbidden logic, and open terminology questions and links to the glossary; its `## Domain Language` table is retired (existing tables are proposed for migration under the retired-section rule, never silently dropped). `context_md` validator, Q1.6 capture, fix recipe, AGENTS.md header/identity lines, DDD clauses, and `.cursorrules` pointer updated accordingly.
- Skill version literal in the Stage 0 schema-gap check moves to 3.6.0: repos initialized with an older `constraints.yaml` will be offered the (value-preserving) schema migration on the next run.
- Content invariants R58/R59 pin the bridge and the glossary home.

## [3.5.8] - 2026-08-28

- Imported from stellarlink-skills into the my-agents monorepo as part of the `stellarlink` pack.
- Cross-skill references remapped to this repo's skills where the original target is not bundled.

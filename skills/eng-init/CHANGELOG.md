# Changelog

## [3.8.1] - 2026-11-07

### Changed

- `references/aux-file-templates.md` CI notes: docs-only commits are sped up by skipping steps inside each job behind a diff-based `docs_only` flag, never by `paths:` / `paths-ignore:` filters or job-level `if:` skips, which leave required checks pending or fail the aggregator. Shipped Markdown and empty diffs are never exempt, and the Q6.11 doc gate never takes the fast path.

## [3.8.0] - 2026-11-06

### Added

- **Byte budget for rendered instruction files.** Every `AGENTS.md` / `CLAUDE.md` eng-init renders, root or module-level, stays within 32768 bytes per file and 307 bytes per line, counted in UTF-8. These are the limits the my-agents `instruction-guard` hook enforces. The rule is in `references/agents-md-sections.md` (next to the 320-line budget, with the same relocate-then-condense order) and in the SKILL.md AGENTS.md repair style, which is the slimming route the hook points to.
- `scripts/check_rendered_harness.py` enforces it with `--max-agents-bytes` (default 32768) and `--max-line-bytes` (default 307), on `AGENTS.md` and, when present, `CLAUDE.md`. Unit tests cover the file budget, UTF-8 line width (CJK) and `CLAUDE.md`; content check `FIELD-agents-md-byte-budget` pins the reference, SKILL.md and checker defaults together.

### Changed

- Six template lines that render into `AGENTS.md` were over 307 bytes. Five are in `agents-md-sections.md` (forbidden suffixes, CLI verify wiring, stacked PRs, verify-the-world, trust-but-verify delegation) and one in `agent-harness-templates.md` (legacy violation baseline). They are now split at sentence boundaries into indented continuation lines, so the rendered Markdown and every word are unchanged.

## [3.7.0] - 2026-11-05

Cherry-picked from upstream harness-init 4.4.x (4.3.1 → 4.4.4 release notes): validator fixes only, adapted to the 3.6.1 code. Nothing was re-imported wholesale; local patches (root-instruction ownership split, `CLAUDE.md` `@AGENTS.md` bridge and `claude_md_bridge`, `openspec/glossary.md`, process-fixture reaping, uv + `run_unit_tests.py`, L1–L4 profiles) are unchanged.

### Added

- **`constraints.yaml` schema version is decoupled from the skill version** (upstream 4.4.3). SKILL.md frontmatter declares `metadata.constraints_schema_version: "1"`; the template renders `{{CONSTRAINTS_SCHEMA_VERSION}}` into `strictness_profile.schema_version` and `{{SKILL_VERSION}}` into `generated_sections.*.template_version` (previously one `{{SCHEMA_VERSION}}` placeholder for both). A skill release that leaves the template unchanged no longer flags every initialized repo as outdated.
- **Legacy-literal compatibility rule** (local; upstream only says "rewrite `4.x.y` once"). Repos initialized by eng-init 3.6.1 and earlier carry the skill release (`"3.6.0"`, `"3.6.1"`) as `schema_version`. A legacy `X.Y.Z` literal `>= 3.6.0` denotes schema `1`: no gap, no migration prompt, and it is rewritten to `"1"` only when the run writes `constraints.yaml` for another reason (listed as a fact, every other value preserved). A literal `< 3.6.0` is a gap and gets the existing value-preserving migration. A non-numeric value or an integer newer than the skill's is reported and asked about, never migrated or downgraded. Legacy `template_version` values already carry the new meaning and are not migrated. The Stage 0 schema-gap literal (3.6.0 since 3.6.0) is replaced by this classification.
- Content invariant R61 pins the split and the legacy rule; eval case-57 covers the 3.6.1 / 3.4.0 / unrecognized variants; case-49's fixture now names a pre-3.6.0 literal so it stays a real gap.

### Fixed

- `check_rendered_harness.py` (upstream 4.4.2, 4.4.4): `section()` returns `None` for an absent heading and `""` for an empty one; `--require-section` now matches the exact `## Title` heading (it was a substring test, so `## Verification Matrix (draft)` satisfied it while every matrix check, which already used the exact match, skipped that section), and a required heading with no body fails; an empty `## Verification Matrix` no longer returns before `--require-generated-section-registry`, `--require-rehabilitation-state` and `--require-enforcement-index` run; an empty Enforcement Index, a row with fewer than four columns, and a level outside `advice`/`review-only`/`warn`/`block`/`gate` are violations (a misspelled level used to skip the row); a zero-byte `AGENTS.md` and a zero-byte `constraints.yaml` (under the registry flag) are violations instead of silent passes; an empty `## Source of Truth & Refactor Contract` fails when the contract is required.
- `score_readiness_report.py` (upstream 4.3.0/4.3.1, 4.4.2, 4.4.4): the CLI executes `readiness-report-schema.json` before scoring (fail closed without jsonschema), rejects duplicate JSON keys, `NaN`/`Infinity`, malformed RFC 3339 `generated_at`, and duplicate application paths after normalization, and reports unreadable input instead of a traceback. `score()` rejects unknown status, `true` as a number, non-finite values, a row `scope` that contradicts the registry, status/credit contradictions (zero credit must be failing or pending_external, full credit passing, anything between partial), non-passing rows without `evidence_locations`, malformed `configured_but_not_blocking`, and a `score.level` outside the published bands (L4 60–79, L5 80–100; a boundary belongs to the higher band). Non-object `report`/`score`/`id` shapes are reported, not crashed on. Default `--registry` resolves from the script, not the cwd.
- `validate_readiness_repair.py` (upstream 4.3.1): `validate()` executes `readiness-repair-schema.json`; pre/post `score` must agree with `status`; `allowed_files` must be canonical repo-relative paths without duplicates, `..`, `.git`, absolute or backslash forms; `exit_code: false` no longer counts as 0; `no_op_already_passing` needs a green validator; `pending_external` needs a `pending_external` post state; `skipped` needs a skippable criterion; duplicate keys and non-finite constants are rejected; malformed shapes report instead of crashing (including an unhashable `matched_criterion`).
- Schemas: repair `requested_signal`/`semantic_match_evidence`/`change_summary`/`allowed_files[]` non-empty, `allowed_files` unique, scores in `0..1`; report `generated_at` is `date-time`, `applications[].path` non-empty, `evidence_locations` required on failing/partial/pending_external rows. Both `schema_version` values stay `const 1`.
- `check_readiness_registry.py` (upstream 4.4.2): `schema_version` is parsed and must be supported; `schema_version: 999` used to validate clean.
- `mutation_sweep.py` (upstream 4.4.2): only pytest exit 1 counts as a killed mutant; 2–5 (collection error, internal error, usage error, no tests collected) are reported as UNMEASURED and fail the sweep.
- `run_unit_tests.py` and `selfcheck.sh` attach `jsonschema` through `uv run --with`.
- **`agent-readiness-criteria.md` JSON companion example now matches the report schema** (local; pre-existing drift). The old example used keys the schema never allowed (`level`, `failing_criteria`, `readiness_gaps`, ...), so an agent copying it got a rejection from the now-schema-checking scorer. It is replaced by a complete report that passes `score_readiness_report.py`, and `test_documented_json_companion_example_is_a_valid_report` pins it through the same schema and scorer.

### Deliberately not ported

- Strictness profiles 一般/严格 (L1–L4 kept), SKILL.md progressive-disclosure split and `workflow-*.md`, rename to harness-init, `CLAUDE.md` non-writing policy, Domain Language table, new criteria (`error_hygiene_lint`, `behavior_snapshot_pinning`, CRAP, `mutation_testing`), `gate-templates/`, `evidence_runner`, `compare_findings`, `build_release`, `RELEASE_MANIFEST`, `check_skill_package.py` (its reference-definition link fix has no local counterpart script).
- Entangled with out-of-scope changes, so only the standalone part was taken: report schema v2 / `debt_metrics` (kept `const 1`); `--allowed-tools` evidence-citation allowlist; full-registry coverage and 0.5-step/registry-authorized partial-credit rules in the scorer (they change what a valid report is); Class-D `external_permission` grant and local-runner detection in the repair validator (a new handoff field; the local "authenticated external evidence" rule stays); `mutation_sweep.py` AST span detection and ungradable-mutant handling (local sites are single-line, so every mutant parses); the PyYAML canonical CI-aggregator rewrite; `--max-agents-words`, `doc_budgets`, `--exclude-dir`, and the backtick-span command extraction change in `check_rendered_harness.py`.

## [3.6.1] - 2026-09-24

### Fixed

- **Self-test process fixtures are owned and reaped by the self-test** (issue #15). The gate quality contract only required filesystem fixtures to be removed, so a downstream `test-guardrails` harness legally leaked resident busy-poll fake upstreams (shared pidfile, delete-only cleanup, guard under test killed before its own cleanup ran) — 130 orphans and ~2400 forks/s on the host while the suite stayed green. `gate-quality-contract.md` gains "Process fixtures": the self-test reaps what it starts (own process group, TERM → polled deadline → KILL from the EXIT trap), one pid record per fixture, a leftover process naming the fixture root FAILs the run, and resident stubs block in one call instead of polling.
- `agent-harness-templates.md` § Guardrail self-test demonstrates it: `spawn_fixture` / `reap_fixtures` / `fixture_strays` helpers, a canonicalized temp root, per-fixture output logs (a leaked process cannot hold the caller's stdout pipe), cleanup that reaps before deleting, and a verdict-bearing residue case. The residue sweep matches command lines, so a descendant tied to the fixture only by its cwd stays invisible to it; the group reap is the primary mechanism. Verified under bash 3.2 and 5.x on macOS and bash on Debian.
- `guardrail_self_test` (criteria, registry validator, fix recipe) now audits for leaks by comparing `ps` snapshots before and after one run; eval case-56 and content invariant R60 pin the behavior.
- The Stage 0 schema-gap literal stays at 3.6.0: `constraints.yaml` schema is unchanged, so 3.6.0 repos are not offered a migration.

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

# Changelog

## [0.2.0] - 2026-11-05

### Added

Absorbed from the upstream stellarlink `to-spec` 2026-11 snapshot, text rules only (its `publish.py` needs the external `swerobot` codec and `git-forge`, neither present here):

- Acceptance-criterion ids are append-only, with `(withdrawn)` / `(superseded_by AC-NNN)` retirement instead of deletion or renumbering.
- Slices carry a stable `Key` and a `Covers:` line claiming the AC ids they implement (replaces the free-form `User stories covered`); `Blocked by` names keys.
- New step 7, acceptance coverage check: every live criterion claimed, no retired id claimed, claims name declared ids only, no duplicates; any gap keeps Readiness at `Draft`.
- New step 8, one combined confirmation (spec summary, seams, slices, defaults, coverage) before publishing.
- Spec template gains a `Default decisions` table, bounded by the user's authorization.
- Slice rules: prefactor slice first, shared entry points in the earliest consuming slice, disjoint file ownership for parallel slices, only real blocking edges with a cycle check.
- GitHub publication goes through `gh-create-issue` so the `Depends on #NN` convention read by `subagent-workflow` holds.

### Not absorbed

- The forge/GitHub publisher and its `swerobot` markers; removal of PRD, questionnaire, and mission-handoff modes (`ask-danker` routes compact PRD requests here).

## [0.1.1] - 2026-09-05

- Project-memory inputs name `openspec/glossary.md` for domain terms (this repo's glossary home) alongside `CONTEXT.md` for bounded contexts and invariants.

## [0.1.0] - 2026-08-28

- Imported from stellarlink-skills into the my-agents monorepo as part of the `stellarlink` pack.
- Cross-skill references remapped to this repo's skills where the original target is not bundled.

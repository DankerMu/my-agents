# Changelog

## [0.2.0] - 2026-11-05

### Added

Absorbed from the upstream stellarlink `rsi` skill (2026-11 snapshot), as prose — its `rsi_ledger.py` is not ported:

- **Measured noise band.** Baseline (0.6) runs twice and records the spread as `noise_band`, per independent unit; the fixed "changes <2% are not meaningful" rule becomes the default when nothing was measured, so existing runs keep their behavior.
- **Progress gate uses the noise band** (`references/gate.md`): a KEEP must beat the previous best by more than `noise_band`, or tie within it while buying simplification or cost; nothing below `previous_best − noise_band` is ever kept (no small steps downhill).
- **Resolution check** before every iteration and as a stop condition (`references/evaluation.md`): skip or redesign an iteration whose best-case gain cannot exceed `noise_band`; stop when the remaining headroom cannot.
- **Pre-evaluation critic** (`references/critic.md`, Phase 5 before L2): an isolated subagent rejects sample leakage, judge gaming, degenerate edits, undeclared bundling, unbounded loops, and re-proposed falsified hypotheses before any oracle run is spent.

### Not absorbed

- `harness-refine` (session-log ingest, about 13k lines, no Codex support) and the `rsi` L0/L2 levels (L2 overlaps `meta-loop`).

## [0.1.0] - 2026-08-28

- Imported from stellarlink-skills into the my-agents monorepo as part of the `stellarlink` pack.
- Cross-skill references remapped to this repo's skills where the original target is not bundled.

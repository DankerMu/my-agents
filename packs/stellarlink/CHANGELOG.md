# Changelog

## [0.2.0] - 2026-08-28

- Added `visual-design` (stellarlink `design`), a visual design-engineering methodology: page-shape routing, task-local design contract, state completeness, and four-layer evidence before delivery.
- Renamed on import to avoid colliding with Claude Code's built-in `design` canvas skill; also flagged `disable-model-invocation: true`.

## [0.1.0] - 2026-08-28

- Initial pack: nine skills imported from stellarlink-skills (`architecture-design`, `to-spec`, `implement`, `tdd`, `vdd`, `code-migration`, `eng-init`, `self-evolution`, `reverse-skill`).
- All skills flagged `disable-model-invocation: true` except `tdd` and `vdd`, which are invoked mid-run by `implement` and `code-migration` and therefore must stay model-invocable.
- Cross-skill references remapped: `/grill` → `/grill-me`, `/wayfinder` → `/implementation-planning`, `/code-review` → `review`, `review-fix-loop` references dropped (not bundled).

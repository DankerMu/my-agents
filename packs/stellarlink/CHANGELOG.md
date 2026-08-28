# Changelog

## [0.1.0] - 2026-08-28

- Initial pack: nine skills imported from stellarlink-skills (`architecture-design`, `to-spec`, `implement`, `tdd`, `vdd`, `code-migration`, `eng-init`, `self-evolution`, `reverse-skill`).
- All skills flagged `disable-model-invocation: true` except `tdd` and `vdd`, which are invoked mid-run by `implement` and `code-migration` and therefore must stay model-invocable.
- Cross-skill references remapped: `/grill` → `/grill-me`, `/wayfinder` → `/implementation-planning`, `/code-review` → `review`, `review-fix-loop` references dropped (not bundled).

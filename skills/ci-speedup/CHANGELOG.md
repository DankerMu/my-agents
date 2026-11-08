# Changelog

## [0.1.0] - 2026-11-07

### Added

- Initial release (issue #23), distilled from DankerMu/open-webui#758, where the CI wall-clock median went from 24.9 min to 9.3 min with every check kept.
- The method has eight steps: check inventory, measurement, diagnosis, simulation, implementation behind guardrails, warm-cache verification, iteration, and before/after delivery. Its non-negotiables cover required checks, main-branch cancellation, and dependency changes.
- `scripts/ci_timings.py`: `fetch` pulls the last N runs, their jobs and steps, and the cache list through `gh`. `report` works offline and prints the wall clock, each job's queue/setup/test medians, the slowest steps, the critical path through `needs`, the `needs` edges that pass no data, and stale cache candidates.
- `scripts/shard_sim.py`: Playwright's `filterForShard` partition with a fixed cost per shard, and `parse-log` for list-reporter output.
- `references/`: the slow-CI pattern catalog, required-check and skip semantics with the docs-only fast path, the sharding method and per-runner algorithms, and caching.
- `templates/`: the delegated `ci-gate.py` verdict with its pin tests and matching workflow, and the `setup-toolchain` composite action.
- Tests run on the frozen open-webui runs. They reproduce the baseline (35 successful runs, 24.9 min median), the critical path and dataless `needs`, the result that 3 shards beat 4, and a template set that passes its own pin tests.

---
name: ci-speedup
description: >-
  Measured GitHub Actions speed-up without dropping any required check: inventory every check,
  baseline the last N runs into queue/setup/test per job and the critical path, diagnose against a
  slow-CI pattern catalog, simulate sharding, implement behind required-check guardrails, verify on
  warm-cache reruns, iterate, and deliver a before/after comparison. Manual (/ci-speedup); the
  model never triggers it, because it pushes several rounds and spends CI minutes. Not for fixing
  a failing CI (diagnosing-bugs) or building CI from scratch (eng-init).
disable-model-invocation: true
version: 0.1.0
argument-hint: "OWNER/REPO and workflow file (optional: run count, round limit)"
---

# ci-speedup — measured GitHub Actions acceleration

Make CI faster with evidence. Measure first, cut the critical path, prove every required check still runs, and judge only on warm-cache reruns. The deliverable is a before/after table, not a feeling.

v1 covers GitHub Actions. The platform-specific facts live in `references/`, and the method in this file carries over to other CI platforms.

## Non-negotiables

- **No required check is dropped.** A check may move, merge or shard. It is removed only when another step already covers it, and the inventory names that step.
- **A required check is never stuck pending, and never passes because it was skipped.** No workflow-level `paths` / `paths-ignore` on gating workflows. Skips pass only through the aggregator rules in `references/required-checks.md`.
- **Main is never cancelled.** `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`. Every commit on main gets a complete run.
- **Conclusions come from warm-cache reruns only, at least two.** A first run after a cache-key change is cold by definition.
- **No hand-edited lockfiles, and no dependency added or upgraded without the user's OK.**
- **Every non-default setting carries a comment naming the failure it prevents.** Examples: `shell: bash` for pipefail, and `fail-fast: false` on shards.
- **Out-of-scope findings are reported, not fixed in the speed-up PR.** Examples: a slow app import, flaky tests, an upstream bug.

## Flow

### 0. Check inventory (gate: written before any change)

List every workflow, then every job and step, then every make/npm target each one calls, with what it checks: format, lint, types, unit, coverage, integration, browser, secrets, docs, lockfile, diff size. This is the baseline set. At the end each row maps to a step in the new structure. A row with no mapping blocks delivery.

### 1. Measure (gate: no proposals without the baseline)

```bash
python3 <skill>/scripts/ci_timings.py fetch --repo OWNER/NAME --workflow ci.yml --limit 50 --out .ci-speedup/before
python3 <skill>/scripts/ci_timings.py report .ci-speedup/before --workflow-file .github/workflows/ci.yml
```

- **Wall clock:** median and p90 over successful runs.
- **Per job:** queue, setup and test medians.
- **Slowest steps.**
- **Critical path:** walked back through `needs` from the last job to finish.
- **`needs` that pass no data.**
- **Caches:** size, and stale candidates.

Keep `.ci-speedup/` out of the commit, for example through `.git/info/exclude`.

Use `--before <ISO>` to freeze the baseline window. The definitions are in the script header; keep them identical for the after measurement. If setup steps are named differently in this repo, pass `--setup-pattern`.

### 2. Diagnose

Go through every entry in `references/patterns.md`. Each hit gets its evidence: the step and its median, or the edge.

- **Build twice in a row (repos with a build or Docker image only).** The second build should be close to a no-op. Whatever is not points at a pattern in the "Build reuse" section.
- **Missing time:** if the slowest job's steps don't add up to its duration, look for unnamed post steps and service containers.

### 3. Plan and simulate

- **Rank candidates by how much they cut the critical path.** Total minutes don't count.
- **A change off the critical path is worth doing only if it is free.** Removing a duplicate run is free; adding a job is not.
- **Before choosing a shard count, simulate it:** `scripts/shard_sim.py` on measured per-file times, with the per-shard fixed cost. Pick the n with the shortest longest shard. Don't pick by "more is faster". See `references/sharding.md`.
- **Show the plan to the user before editing:** expected critical path, what moves where, and what each change risks.

### 4. Implement behind guardrails

- **Required checks:** an aggregator with `if: always()`, which branch protection requires as its only check.
  - When skips are by design (docs-only PRs, PR-only jobs on push), the aggregator delegates to a verdict script that has tests.
  - Start from `templates/ci-gate.py`, `templates/test_ci_gate.py` and `templates/ci-docs-only.yml`. Replace the CONFIG block with this repo's facts, and grep for every Markdown file the app reads or ships.
- **Toolchain sized to each job:** start from `templates/setup-toolchain.yml`. Cache the installed tree, give lint-only jobs a dev-only environment, and use a partial clone where history is needed but old blobs are not.
- **Script rewrites (parallel lint and similar):** diff-test the old and new versions on the same inputs, including an injected violation. The output must match byte for byte.
- **New gate logic:** write its failing tests first.
- **Tools:** prebuilt, pinned binaries. No `go install` / `cargo install` in CI.
- **`actionlint`:** if the repo uses it, run it from its prebuilt release.

### 5. Verify on real runs (gate: every round records the table)

- **Push and wait for at least two warm-cache runs.** The first run after a key change is reference only.
- **Record each round:**
  - wall clock;
  - critical-path job;
  - setup and test time for each job;
  - shard times against the simulation.
- **Report runner variance.** On hosted runners it reaches ±30%, so compare medians.
- **A first-run failure after sharding is usually an order dependency, not flakiness.** Read `sharding.md`.

### 6. Iterate

Find the critical path again and pick the next lever. Stop when any of these holds:

- the critical path is at its floor, meaning setup plus the largest unit that cannot be split;
- the round limit is reached (default 3);
- the user stops.

### 7. Deliver

1. **Before/after table:** median and p90 wall clock, critical path, and each job's setup and test time. Name the baseline window and the warm runs it uses.
2. **Check inventory mapping:** each old check next to its new step.
3. **Remaining levers,** each with its estimated cut to the critical path.
4. **Out-of-scope findings.**
5. **Cost notes:** runner minutes added by the new parallel jobs; cache entries deleted, which only happens after the user confirms.

## Files

| Path | Use |
|---|---|
| `scripts/ci_timings.py` | `fetch` (gh api → trimmed JSON) and offline `report` (baseline tables, critical path, dataless needs, caches) |
| `scripts/shard_sim.py` | `parse-log` (Playwright list reporter → per-test times) and `simulate` (Playwright's real partition, fixed cost per shard) |
| `references/patterns.md` | Slow-CI catalog: signal → fix → risk |
| `references/required-checks.md` | Skip semantics, aggregator shapes, docs-only fast path, cancellation |
| `references/sharding.md` | Simulation method, per-runner partition algorithms, order dependencies |
| `references/caching.md` | setup-* caches, installed-tree caching, sizing, the 10 GB quota, honest measurement |
| `templates/ci-gate.py`, `templates/test_ci_gate.py`, `templates/ci-docs-only.yml` | Delegated verdict: classification, verdict, pin tests, matching workflow |
| `templates/setup-toolchain.yml` | Composite action that sizes the toolchain to each job |

The scripts need python3 ≥ 3.9 and `gh` (for `fetch` only); they use the standard library only.

Worked example and fixtures: DankerMu/open-webui#758. The wall-clock median went from 24.9 min to 9.3 min, with the critical path moving from fast checks → unit tests to the slowest browser shard. `tests/fixtures/open-webui/` holds the frozen runs.

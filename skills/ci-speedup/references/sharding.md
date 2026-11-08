# Sharding: pick the count by simulation, not by "more is faster"

A shard's time is its fixed cost plus the time of the test groups its runner assigns it. The fixed cost is setup, plus server and stack start, plus warm-up, and it is paid again by every shard. Because whole groups cannot be split, the longest shard has a floor of fixed cost plus the heaviest group. Adding shards past the point where that floor binds makes the longest shard longer.

## Method

1. **Get per-file times from a real CI run**, not from local runs: runner CPUs and caches differ. For Playwright, the `list` reporter prints one line per finished test with its duration. Run `scripts/shard_sim.py parse-log <job log> --suite-names a,b > suites.json`.
2. **Measure the fixed cost.** In the current job, measure the time from job start to the first test line, and add the warm-up. On open-webui it was about 3.5 min per browser shard.
3. **Simulate:** `scripts/shard_sim.py simulate suites.json --fixed-cost <s> --max-shards 8`. Take the n with the shortest longest shard; ties go to the smaller n, which costs less in setup.
4. **Check the floor line.** If the best n is already at the floor, the next lever is splitting the heaviest group, such as a big spec file, or cutting the fixed cost. A further shard won't help.
5. **After shipping, compare the measured shard times with the simulation.** A shard that is far slower than predicted usually has an order dependency (see below).

The open-webui#758 case, with fixtures in `tests/fixtures/open-webui/`:

| shards | longest (simulated) |
|---|---|
| 1 | 804 s |
| 2 | 520 s |
| 3 | **423 s** |
| 4 | 444 s |

Four shards lose to three. Playwright splits by test count, so the 4-way split puts `ocu-resources` and `ocu-tree` (133 s together) in the same shard as `skins` (82 s). Every added shard also pays the fixed cost again.

## Runner partition algorithms

### Playwright (implemented in `shard_sim.py`)

Source: `filterForShard` and `createTestGroups` in `playwright/lib/runner/testGroups.js` (1.59).

- **Groups.** Without `fullyParallel`, a file is one group. With `fullyParallel` or `test.describe.configure({ mode: 'parallel' })`, each test is a group. Files are taken in Playwright's file order.
- **Partition.** Let `total` be the number of tests. Each shard size is `floor(total / n)`, and the remainder goes one each to the first shards. A group joins the shard whose index range contains the group's first test. The split counts tests, not time.
- **Weights.** `PWTEST_SHARD_WEIGHTS` scales the sizes. `shard_sim.py` does not model weights. If the user wants weights, extend the simulation first, and don't guess.
- **Within a shard.** Groups go in order to the first free worker.
- **Several suites in one job** (two `playwright test` invocations, each with `--shard i/n`): each is partitioned on its own, and the job runs them one after the other.

### Jest

`--shard=i/n`: the default `TestSequencer.shard` sorts test paths by a hash of the path, then slices them into equal counts. The split is effectively random with respect to duration. A custom sequencer can balance by recorded duration. Not simulated; if Jest is the critical path, write the simulation before choosing n.

### Vitest

`--shard=i/n` sorts files by a hash of their path and slices them into equal counts. The split counts files, not time. Not simulated.

### pytest

There is no built-in sharding.

- `pytest-split` uses recorded durations (`.test_durations`) and greedy bin-packing, `least_duration` by default. It needs the durations file to be kept up to date.
- `pytest-xdist` parallelizes within one runner and does not shard across runners.
- Cross-runner coverage needs `coverage combine` in an extra job.

Don't shard pytest when the job is already off the critical path (open-webui: the backend tests finish before the slowest browser shard). A large one-time cost, such as importing a heavy app (about 100 s on open-webui), is paid once per shard and sets a floor no shard count removes. Report it rather than fixing it in the speed-up PR.

## Order dependencies that sharding exposes

Unsharded, the first spec warms caches for everything after it, such as Vite's cold compile of a route, a database migration or a login state. Sharded, another spec runs first and times out.

- **Fix:** an explicit warm-up in `globalSetup`, or a fixture that does the work.
- **Not a fix:** raising timeouts. That hides the dependency and slows every run.
- **First-run failures are evidence of this, not flakiness.** Read which spec failed and what it ran first.

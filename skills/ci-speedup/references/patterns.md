# Slow-CI pattern catalog

Check every row against the baseline from `scripts/ci_timings.py report`. A hit needs evidence: the step and its median seconds, or the `needs` edge. A row with no evidence is not a hit, however likely it looks.

Each entry gives the signal in the measurements, the fix, and the risk the fix must not create.

## Graph

### `needs` that passes no data
- **Signal:** `report` lists the edge under "needs that pass no data". The dependent job's start time sits right after the dependency's end, and the edge is on the critical path.
- **Fix:** Delete the edge. Ordering by itself buys nothing: a failure in either job still fails the aggregator.
- **Risk:** Some edges exist to save runner minutes ("don't run the 15-minute suite if lint fails"). If the user wants that trade, keep the edge and record it as a decision. It is not a correctness requirement.

### Independent jobs serialized inside one job
- **Signal:** One job's steps cover unrelated suites, for example smoke, then baseline browser, then OCU browser. The job is the critical path, and its steps share nothing beyond setup.
- **Fix:** Split the job along the seam. Each piece pays setup once, so split only where the saved test time exceeds the added setup.
- **Risk:** Hidden coupling between the pieces, such as a server started in step 3 that step 7 uses. Make each new job start whatever it needs.

### Longest suite unsharded
- **Signal:** One test step dominates the critical path, and it consists of many independent files.
- **Fix:** Shard it. Pick the count with `scripts/shard_sim.py` on measured per-file times, including the per-shard fixed cost. See `sharding.md`.
- **Risk:** Order dependence. A spec that passed only because an earlier spec warmed something now runs first in its shard and fails. Fix the dependency explicitly, for example with a `globalSetup` warm-up. Never fix it by raising timeouts.

## Duplicated work

### The same suite runs twice
- **Signal:** Two steps with similar medians run the same tests, for example `make test` and then `make coverage-gate`, which reruns pytest under coverage.
- **Fix:** Keep the run that produces the strictest evidence (coverage) as the only run. Make sure that run prints the full failure log, so dropping the other run loses no diagnostics.
- **Risk:** The two runs differ in a flag or environment that matters, such as an extra marker or a different `-k`. Diff the exact commands before deleting one.

### Duplicate upstream workflow
- **Signal:** A second workflow, often an inherited upstream one, re-runs a check the canonical gate already runs, for example `ruff format --check` on two Python versions.
- **Fix:** First fold any scope the duplicate covers and the gate does not into the gate. Only then disable the duplicate. Its coverage must never be missing in between.
- **Risk:** The duplicate covers something real, such as a second Python version. If so, it stays.

### Tools built from source in CI
- **Signal:** `go install`, `cargo install`, `pip install` of a CLI tool, or `npm i -g` takes tens of seconds in a setup step.
- **Fix:** Download a pinned prebuilt release binary, or use the tool's official action. Verify the checksum when the project publishes one.
- **Risk:** A floating "latest" download. Pin the version.

## Setup

### Every job cold-installs dependencies
- **Signal:** `npm ci`, `pnpm install` or `uv sync` takes 40–60 s in every job, even on warm-cache runs.
- **Fix:** Cache the installed tree (`node_modules`) instead of the download cache, and run the install only on a cache miss. See `caching.md` and `templates/setup-toolchain.yml`.
- **Risk:** A key that misses an input to the tree (OS, runtime version, lockfile), which serves a stale tree.

### Cache larger than the job needs
- **Signal:** A lint-only job restores a multi-GB environment cache, for example a 3 GB uv cache with CUDA torch, to run ruff.
- **Fix:** Size the toolchain to the job: install only the dev group, from its own small cache.
- **Risk:** None beyond the key; the job still runs the same tools.

### Full clone where a partial clone works
- **Signal:** checkout takes 15–20 s with `fetch-depth: 0` on a large history.
- **Fix:** Use `filter: blob:none` for jobs that need history but not old blobs. Keep the full clone only where a step reads old file contents, such as linting the baseline revision.
- **Risk:** A step that runs `git show <old>:<path>` and now fetches lazily. That is slower, not wrong; measure it.

### macOS or Windows runners for OS-independent work
- **Signal:** Formatting, lint, dependency audits or doc checks run on `macos-*`. Free accounts get at most 5 concurrent macOS jobs, shared across every workflow.
- **Fix:** Move OS-independent jobs to `ubuntu-latest`. Keep only the OS-specific build and test on macOS.
- **Risk:** A check that is genuinely OS-specific, such as case-sensitive paths or line endings. Leave it where it is.

### Irrelevant caches pulled by narrow jobs
- **Signal:** A frontend-only build job restores a Rust or Python cache.
- **Fix:** Drop the restore from that job.
- **Risk:** None.

## Change scope

### Documentation changes run the full suite
- **Signal:** Pull requests that touch only Markdown run every job.
- **Fix:** Use the docs-only fast path in `required-checks.md`. Never use a workflow-level `paths` filter.
- **Risk:** Mistaking for documentation the Markdown that ships or that the app reads at runtime. The classification fails closed.

### Superseded runs keep running
- **Signal:** Cancelled-by-newer runs are rare, while several pushes to one PR all run to completion.
- **Fix:** `concurrency` with `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`. Main is never cancelled, so every commit on main gets a complete run.
- **Risk:** Labelling a PR also triggers a run and cancels the one in progress. Say so to the user, so a label added mid-run is not mistaken for a failure.

## Serial loops inside a step

### One process per file, one file at a time
- **Signal:** A lint or check script loops over files and starts the tool once per file (`eslint`, `tsc` and similar). The step takes minutes.
- **Fix:** Pass all files in one invocation if the tool supports it. Otherwise run one worker per CPU, with each worker writing only its own output slot, and print the results in the original order.
- **Risk:** Interleaved or reordered output, or a worker that dies and counts as a pass. Diff-test the old and new script on the same inputs, including an injected violation and two files with the same basename; the report must match byte for byte. A dead worker counts as a failed file.

## Build reuse (when the repo has a build or Docker image)

Build twice in a row locally. The second build should be close to a no-op. Whatever still takes time points at one of these:

- **Dockerfile copies the whole repo before installing dependencies.** Every source change invalidates the dependency layer. Copy the lockfiles first, install, then copy the source.
- **A build target depends on a file that never exists**, such as a misspelled output or a phony target, so it rebuilds every time. Fix the target.
- **A cache key includes something volatile**, such as a timestamp, a commit SHA or the run id, so nothing is ever reused. Key on the inputs.

Skip this section when the repository has no build step or image.

## Mechanical traps to check while editing

- GitHub's default `run` shell is `bash -e` without `pipefail`, so `cmd | tee file` swallows `cmd`'s failure. Set `shell: bash`, which adds `-o pipefail`, on every step that pipes.
- Inline `jq` or `grep` gate logic in YAML can't be tested and is easy to get wrong on precedence. Move any decision logic into a script that has tests.
- In a fork, `gh` may default to the upstream repository. Pass `--repo OWNER/NAME` explicitly for `gh pr create` and `gh run`.
- Each added job adds a setup. Judge a change by the critical path in wall-clock time, not by total runner minutes. Minutes are free on public repositories; report the rise anyway.

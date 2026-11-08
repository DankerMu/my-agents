# Required checks, skips, and the docs-only fast path

Speeding up CI changes which jobs run. Branch protection decides what a missing or skipped job means, so every structural change gets checked against this page first.

## The two facts everything rests on

1. **GitHub counts a skipped required check as passing.** If branch protection lists individual jobs, a job skipped because its dependency failed, or because of an `if:`, waves the PR through.
2. **A required check that never reports blocks the PR forever.** A workflow that a `paths` / `paths-ignore` filter keeps from starting never reports its checks. The PR shows "Expected — waiting for status" and cannot merge.

So branch protection requires exactly one check: an aggregator job, `All checks passed`, with `if: always()`, whose `needs` lists every blocking job. That aggregator decides what each dependency's result means.

## Aggregator shapes

**Inline**, used when nothing is skipped by design:

```yaml
all-checks-passed:
  name: All checks passed
  if: always()
  needs: [fast-checks, unit-tests, browser, secret-scan]
  runs-on: ubuntu-latest
  steps:
    - env:
        NEEDS: ${{ toJSON(needs) }}
      run: |
        echo "$NEEDS"
        if echo "$NEEDS" | grep -Eq '"result": "(failure|cancelled|skipped)"'; then exit 1; fi
```

**Delegated**, used when some skips are legitimate: a PR-only job on push, or code jobs on a docs-only PR. The step hands `toJSON(needs)` to a script that has tests, and the script enumerates exactly the skips that pass. See `templates/ci-gate.py`, `templates/test_ci_gate.py` and `templates/ci-docs-only.yml`.

- The script takes the docs-only classification from a required `changes` job. A missing or garbled classification fails the verdict.
- Every other skip fails, and so does any failure, cancellation, unknown job, or required job missing from `needs`.
- Its tests pin `REQUIRED_JOBS`, `CODE_JOBS` and `PR_ONLY_JOBS` to the workflow: aggregator `needs`, jobs whose `if:` reads `needs.changes.outputs.code`, and jobs whose `if:` reads `github.event_name == 'pull_request'`. A renamed job then fails a test instead of silently dropping out of the gate.
- Never excuse skips inline in the YAML, for example with a `grep` that ignores `skipped` for certain names. That cannot be tested, and it reopens the hole.

eng-init's `check_rendered_harness.py --require-ci-aggregator` accepts both shapes.

## Docs-only fast path

Two shapes work. Both keep every workflow triggered.

| Shape | How | Saves | Use when |
|---|---|---|---|
| In-job | An early step diffs the change and sets `docs_only=true`; the expensive steps carry `if: steps.scope.outputs.docs_only != 'true'`. The job still reports success. | Test time only; the runner and checkout still start | The inline aggregator stays, and setup is cheap |
| Job-level | A required `changes` job classifies; code jobs carry `if: needs.changes.outputs.code == 'true'`; the aggregator is delegated | Runner, setup and test time of every skipped job | Setup is a large share of each job (the common case) |

The range to diff:

| Mechanism | Pull request | Push |
|---|---|---|
| In-job | `git diff --no-renames --name-only "${base.sha}...HEAD"`, with `fetch-depth: 0` | `before..after` |
| Job-level | PR files API with `previous_filename` | no push skips: pushes run everything |

**The classification fails closed.** Each of these counts as code:

- Markdown that ships: packaged plugins, templates, images, docs bundled into the app.
- Markdown the app reads at runtime, such as a `CHANGELOG.md` parsed for a version or "what's new". Grep the code for every Markdown filename it opens before writing the rules.
- Markdown under a code directory, unless you have checked that nothing reads it. Safest rule: only top-level Markdown and the docs directory count as documentation.
- The old path of a rename, which `--no-renames` or `previous_filename` exposes. Moving code into `docs/` is a code change.
- An empty diff.
- A truncated listing: the PR files API stops at 3000 entries, so a listing whose length is not `changed_files` is code.

**What still runs on a docs-only change:** formatting (prettier covers Markdown), doc gates, link checks, decision-record verification, the secret scan, and the PR guards. A doc gate never takes the fast path: docs-only changes are exactly what it checks.

## Cancellation

```yaml
concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

- A newer push to the same PR cancels the older run. Main is never cancelled, because releases depend on every commit on main having a complete run.
- A cancelled run's aggregator reports `cancelled`, and the newer run's aggregator is the one that counts.
- Adding a label to a PR triggers a new run, which cancels the run in progress. Expect it.

## Changing what is required

- Adding or renaming a job: update the aggregator's `needs` and, if delegated, `REQUIRED_JOBS`. The pin tests fail until both agree.
- Never edit branch protection to "unblock" a faster CI. If a structural change needs a protection change, name the exact setting and let the user make it.

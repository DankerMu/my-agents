# Critic Checklist

Run in Phase 5 after the L1 quick gate and before L2, so a candidate that cheats or degenerates never spends oracle runs. The critic is a subagent with its own context: it sees only the committed diff (`git show HEAD`), the declared hypothesis and prediction from Phase 2, and this checklist — not the proposer's reasoning.

Output:

```json
{"verdict": "accept" | "reject", "reasons": ["..."], "risk_notes": ["..."]}
```

On `reject`, the proposer may fix the diff using the reasons, at most twice. If it still fails, `git revert HEAD`, log the iteration as DISCARD with `critic_reject: <first reason>` in the description, and move to Phase 8. A critic reject is a failed experiment, not a broken run; a scope violation found by L1 stays a broken run.

## Reject when the diff

1. **Leaks or specializes to samples** — hard-codes names, IDs, entities, or answers from dev cases, constants that hold for one case, or "if the input contains X" branches. Litmus test: swap in unseen cases of the same kind; does the edit still make sense and still help?
2. **Degenerates** — an empty edit (dead code, comment-only change, a toggle nothing reads) that claims a mechanism, or removes a safety mechanism (truncation, error handling, timeout, termination condition) without a replacement.
3. **Games the judge** — reads or probes the oracle, GT files, or rubric; rewords output to please the judge; hard-codes thresholds that could only come from the evaluator.
4. **Bundles undeclared changes** — the diff contains independent changes outside the declared hypothesis, or one declaration hides several mechanisms (the atomicity test in Phase 2).
5. **Persists sample data** — new memory, example libraries, or few-shot blocks that store case-specific content; only entity-free patterns may be stored.
6. **Adds unbounded work** — retry, self-check, or "keep improving" loops with no exit condition or count limit.
7. **Oversteps scope** — touches forbidden paths, holdout data, the oracle, or tests to make them pass.
8. **Repeats a falsified hypothesis** — re-proposes a mechanism already discarded in `experiments.jsonl` without stating a substantive difference.
9. **Copies the evaluation** — examples, numbers, or wording in the artifact that replicate dev cases or the rubric's phrasing.

## Artifact-specific signals

- **Prompt / skill text** — per-case constants that belong in variables; negative-instruction lists growing by dozens of items (usually noise fitting); buying score by raising sampling or output length without declaring it.
- **Code / ops fixes** — swallowing exceptions, broadening `try/except`, lowering log levels or raising alert thresholds (removing the signal, not the error); no failing reproduction test written first; loosened assertions; unrelated refactors or dependency upgrades riding along.
- **Agent harness** — reading test or grader paths; changing the externally injected contract (interface, output schema, model, temperature, timeouts); sub-calls or retries with no limit.
- **Experiments** — tuning on holdout; changing the metric definition or protocol; cherry-picking seeds.

Adapted from the `critic-checklist.md` of the upstream stellarlink `rsi` skill (2026-11 snapshot).

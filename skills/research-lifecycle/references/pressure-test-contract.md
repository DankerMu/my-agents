# Pressure-Test Contract

Canonical gate rule for every research-engineering artifact (question brief,
study protocol, traceability contract, research profile, engineering handoff).
Skills restate only the one-paragraph summary; this file owns the detail.

## Gate Decision

Record exactly one explicit decision per artifact before it is frozen,
approved, or handed off:

- `grill-me` — adversarial pressure-test when the terminology and durable
  project decisions are already stable; nothing needs persistence.
- `grill-with-docs` — pressure-test when scientific terms, process boundaries,
  or long-lived decisions must be reconciled and persisted to
  `openspec/glossary.md` and `docs/adr/` (see the terminology and decision
  ledger rules in [artifact-model.md](artifact-model.md)).
- `skipped:<reason>` — allowed only for genuinely narrow, low-impact work.
  Medium/high-impact artifacts (physical equations, process representation,
  scientific state, data semantics, benchmark authority, operational claims)
  must not skip.

## Record Format

Write the decision into the artifact's pressure-test field:

```text
Mode: grill-me | grill-with-docs | skipped:<reason>
Closed decisions:
Open questions:
```

## Delegated Conduct

A delegated grill keeps its own contract: it is interactive, asks one material
question at a time, and offers a recommended answer per question. Do not
simulate the dialogue; if the conversation did not happen, the gate did not
pass. Answers that resolve project-wide terms are persisted inline by
`grill-with-docs`, not batched to the end.

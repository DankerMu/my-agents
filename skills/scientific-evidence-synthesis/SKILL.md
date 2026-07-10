---
name: scientific-evidence-synthesis
description: >
  Synthesize completed scientific study evidence into a claim-evidence matrix
  that separates support, counter-evidence, uncertainty, applicability,
  protocol deviations, and unsupported conclusions. Use after study execution
  or when reviewing an evidence package. Do not replace domain-expert judgment,
  perform implementation review, or turn calibration gains into mechanistic
  validation.
invocation_posture: manual-first
version: 0.1.2
---

# Scientific Evidence Synthesis

Turn study outputs into bounded, auditable evidence rather than a persuasive
narrative assembled after seeing results. This skill judges the relationship
between the approved protocol, the produced evidence, and the intended claims;
it does not declare a scientific conclusion accepted on behalf of the PI or
domain owner.

## When To Use

Use after a study has produced enough artifacts to assess one or more claims,
alternatives, capability criteria, qualification gates, or no-go decisions.
Examples include:

- deciding whether a numerical anomaly is physical dynamics or an implementation
  defect
- assessing whether a new snow representation passes component verification and
  is ready for observational evaluation
- comparing datasets or forecast systems within a declared domain
- evaluating whether a new method meets accuracy, conservation, robustness and
  cost criteria
- closing a negative-result or no-go branch with reusable evidence

## When Not To Use

- Do not synthesize incomplete runs as though the protocol were completed.
- Do not perform ordinary code review; use `review` or
  `risk-adaptive-cross-review`.
- Do not invent missing evidence, silently remove failed cases, or move thresholds
  after seeing results.
- Do not label calibration improvement as mechanistic verification.
- Do not make the final human scientific or operational decision.

## Inputs and Output

Read, when present:

- `research/project-profile.md`
- question/capability brief
- frozen protocol and amendments
- theory-to-code traceability package
- code/data/environment/run manifests
- logs, raw outputs, derived analyses and excluded-run records
- declared claims, alternatives, gates and decision owner

Produce under the active study directory:

```text
research/studies/<study-id>/evidence/
  evidence-index.json or evidence-index.md
  claim-evidence.md
research/studies/<study-id>/decision.md
```

Use [claim-evidence-template.md](references/claim-evidence-template.md). The
`decision.md` may be drafted by the agent but remains pending until the named
human authority records a verdict.

## Delegated Skills and Agents

- Use `explorer` for read-only artifact and provenance mapping.
- Use `researcher` or `docs-researcher` only when interpretation depends on an
  external source or official contract not already captured.
- Use `grill-me` when the evidence interpretation or proposed decision needs an
  adversarial conversation but terminology is stable.
- Use `grill-with-docs` when evidence exposes ambiguous process terms or a
  project-wide decision that must be reconciled with the glossary/ADR system.
- Use `meta-loop` to audit an expensive or safety-critical evidence loop where
  producer/checker independence, stopping rules, or evaluator reliability are in
  doubt.
- Use `reviewer` only as an independent read-only evidence reviewer when the
  orchestration environment supports it; the `reviewer` agent ships with the
  `agentic-issue-delivery` pack, not this one. Reviewer findings remain
  candidates for the human decision owner.

## Workflow

### 1. Establish Protocol Conformance

When the study used the `research-lifecycle` provenance tooling, run its
`verify` subcommand first: protocol-digest and output-checksum conformance is
then machine-established, and this step judges only what remains.

Before interpreting results, compare execution against the frozen protocol:

- required cases/runs completed
- baselines and controls used as declared
- code, data, configuration and environment identities captured
- thresholds and metrics unchanged or covered by an approved amendment
- failures, retries, exclusions and deviations recorded
- exploratory analyses clearly separated from confirmatory analyses

Classify conformance as:

- `CONFORMANT`
- `CONFORMANT_WITH_AMENDMENTS`
- `PARTIAL`
- `NONCONFORMANT`

A nonconformant study may still produce exploratory evidence, but it cannot be
presented as confirmatory evidence for the original claim.

### 2. Inventory Evidence by Oracle

Index every load-bearing artifact and state which oracle owns the fact:

- theory/derivation
- observation or instrument
- reference dataset
- software test or independently computed result
- target hardware/performance run
- live operational environment
- human expert assessment

Do not let a convenient oracle impersonate another. Local unit tests cannot prove
live operational readiness; a good fit to observations cannot prove the code
implements the intended equation.

### 3. Reconstruct the Intended Claims

Use the predeclared claims, alternatives, capability criteria and gates. For each
claim, record:

- exact wording and claim class
- required evidence
- falsifier or no-go condition
- intended spatial, temporal, regime and population scope
- whether it was confirmatory or exploratory

If no claims or criteria were declared, state that the synthesis is exploratory
and route back to `research-question-framing` before making a strong decision.

### 4. Build the Claim-Evidence Matrix

For each claim or alternative, record:

- supporting evidence
- counter-evidence and failed cases
- protocol deviations affecting it
- uncertainty and sensitivity
- assumptions and dependencies
- applicability boundary
- missing evidence
- status

Allowed agent-proposed statuses are:

- `SUPPORTED_WITHIN_SCOPE`
- `CONTRADICTED`
- `INCONCLUSIVE`
- `NOT_TESTABLE_WITH_CURRENT_DESIGN`
- `REQUIRES_INDEPENDENT_VALIDATION`
- `NOT_EVALUATED`

Avoid `PROVED`, `UNIVERSALLY_VALID`, `MECHANISM_CONFIRMED`, or
`PRODUCTION_READY` unless the project profile defines those terms and the named
human authority applies them after the corresponding gate.

### 5. Check Robustness and Alternative Explanations

Use relevant checks, not a universal checklist:

- sensitivity to cases, windows, scales, thresholds and aggregation
- observation/data uncertainty and representativeness
- parameter compensation and equifinality
- data leakage or result-aware selection
- solver/numerical artifacts and conservation failures
- unchanged sibling regimes and negative controls
- external validity and domain shift
- runtime/hardware variability for performance claims
- operational failure and rollback evidence for qualification claims

When evidence cannot discriminate alternatives, record `INCONCLUSIVE`; do not
choose the most convenient story.

### 6. Preserve Negative and No-Go Results

A no-go branch is a successful research outcome when the gate was predeclared and
executed correctly. Record:

- the closed route
- gate values and evidence
- why the route should not be reopened without new evidence
- reusable diagnostics, datasets or tools that remain valuable

Do not create implementation work merely to show progress.

### 7. Draft the Decision Record

Draft a concise decision package containing:

- protocol conformance
- claim-evidence summary
- supported and unsupported statements
- limits and unresolved questions
- recommended outcome: close, revise, follow-up study, product handoff, or
  engineering handoff
- required human approver

The decision owner may accept, reject, narrow or request more evidence. Record the
human verdict separately from the agent recommendation.

### 8. Route the Outcome

- Scientific close or negative result: preserve the study and evidence.
- Insufficient discrimination: return to framing/design with an amendment or new
  study ID.
- Approved product/operational requirement: hand to the `product-manager` pack.
- Approved scientific/model/software change: invoke
  `research-engineering-handoff`.

## Hard Rules

1. Never hide failed, excluded, or contradictory cases.
2. Never move the oracle, metric, threshold, or baseline silently after results.
3. Separate confirmatory and exploratory evidence.
4. State what the evidence does **not** support.
5. Preserve scope and uncertainty in every proposed claim.
6. The final scientific verdict belongs to the named human authority.

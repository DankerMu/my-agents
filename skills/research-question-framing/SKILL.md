---
name: research-question-framing
description: >
  Turn a phenomenon, scientific uncertainty, capability gap, method idea, data
  problem, or operational decision into a bounded research contract with
  explicit objects, intended claims, alternatives, evidence needs, scope, risks
  and downstream route. Use before study design when the problem is not yet
  decision-ready. Do not force every scientific project into a hypothesis-only
  template or use this for ordinary implementation requirements.
invocation_posture: hybrid
version: 0.1.2
---

# Research Question Framing

Create a research contract that is strong enough to design evidence against. The
contract may be centered on a question, a capability gap, a method, a dataset, a
measurement, an intervention, or a qualification decision. Hypotheses are one
possible structure, not the universal structure.

## When To Activate

- an observed pattern or anomaly needs a researchable question
- a model lacks a process or capability, such as snow accumulation and melt
- a proposed method or dataset lacks a clear claim and benchmark
- a team is mixing scientific, product and implementation questions
- the requested conclusion is broader than the available evidence
- `research-lifecycle` cannot yet choose a study design

## When Not To Use

- the question, claim, scope and decision criteria are already approved; use
  `study-design`
- the task is only external literature research; use `deep-research`
- the direction is open-ended ideation with no bounded decision yet; use
  `brainstorming` first
- the user already has implementation-ready requirements; use the delivery flow

## Inputs

Load:

- `research/project-profile.md`
- relevant glossary, prior studies, ADRs and research decision records
- code/data/documentation anchors when the active project is the target
- any observation, anomaly, proposal or requested capability from the user

Use `blind-spot-pass` before framing long work in unfamiliar code, data or domain
territory. Use `researcher` or `docs-researcher` when external or official sources
can materially change the frame.

## Framing Axes

Record the same open axes used by `research-lifecycle`:

- research object
- intended interaction/change
- intended claim class
- current evidence maturity
- engineering impact

Add custom values rather than bending the work into a preset category.

## Workflow

### 1. Separate the Trigger From the Research Problem

Distinguish:

- what was observed or requested
- why it matters scientifically or operationally
- what decision the study must enable
- what is currently unknown

A request such as “add snow to SHUD” is not yet a research contract. The frame
must establish the regimes and scales where missing snow processes matter, which
scientific behavior is required, what simpler status-quo alternatives exist, and
what evidence would justify the added complexity.

### 2. Choose the Appropriate Reasoning Structure

Use whichever structure fits the intended claim:

- **explanatory** — competing hypotheses plus discriminating predictions
- **capability/representation** — missing capability, candidate representations,
  invariants, required regimes and qualification criteria
- **method/measurement** — objective, competing methods, reference truth,
  identifiability and performance/uncertainty criteria
- **data product** — source authority, transformation semantics, quality,
  uncertainty, lineage and use claims
- **decision/qualification** — alternatives, decision thresholds, target
  environment, failure modes and rollback

These are patterns, not exclusive types. Combine or extend them when needed.

### 3. Bound the Intended Claims

For each intended claim, record:

- exact wording
- claim class
- population/domain/scale/time range
- evidence required
- evidence that would contradict it
- decision owner

Reject silent escalation from “works for this case” to “is generally valid,” or
from calibration improvement to mechanistic correctness.

### 4. Build the Alternative Space

Include the status quo and no-go/defer option. Depending on the frame, alternatives
may be hypotheses, process formulations, datasets, methods, model structures,
observational explanations, or operational choices.

Invoke `brainstorming` when the alternative space is still immature. Do not use
`grill-me` until there is an actual draft to pressure-test.

### 5. Identify Discriminating Evidence

For each alternative, identify observations or experiments that produce different
predictions. When alternatives are not empirically distinguishable with the
available data or compute, state that explicitly and narrow the claim or design a
measurement/data acquisition step.

### 6. Define Scope and Non-Goals

Name:

- included and excluded processes, variables, scales, regimes and systems
- what the study will not conclude
- what may become a separate study
- constraints imposed by data, compute, licensing, instruments or operations

### 7. Set Risk and Human Gates

Mark work high-impact when it changes physical equations, process representation,
scientific state, data semantics, benchmark authority, observational lineage, or
operational release claims. Name the PI/domain owner who must accept those
choices.

### 8. Pressure-Test the Draft

Record one explicit gate decision on the draft contract: `grill-me` when
terminology is stable, `grill-with-docs` when terms, process boundaries or
durable decisions must persist to `openspec/glossary.md` / `docs/adr/`, or
`skipped:<reason>` — only for genuinely narrow, low-impact work. A delegated
grill stays interactive (one question at a time) and must not be simulated.
The canonical gate contract lives in `research-lifecycle`
(`references/pressure-test-contract.md`).

## Output: Research Contract

Write the contract using the exact section template in [references/research-contract.md](references/research-contract.md) (includes a worked snow-module example).

The downstream route is one of:

- more grounding/research
- `study-design`
- `theory-to-code-traceability` followed by `study-design`
- product discovery
- stop/defer because the question is not currently testable

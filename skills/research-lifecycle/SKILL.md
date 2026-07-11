---
name: research-lifecycle
description: >
  Research control-plane router: frames a phenomenon, capability gap, or decision need, then orchestrates question framing, study design, evidence synthesis, traceability, and engineering handoff. Invoke explicitly for substantive scientific work.
invocation_posture: manual-first
version: 0.3.1
---

# Research Lifecycle

Treat research as a governed evidence process, not as a closed list of task types.
The lifecycle must accommodate observational inquiry, theory and mechanism work,
new process representation, numerical-method development, model evaluation,
data-product construction, field or laboratory work, operational qualification,
and combinations not known in advance.

The top-level router therefore classifies work on independent axes rather than
forcing it into an exhaustive menu:

1. **Research object** — phenomenon, theory, process representation, observation,
   dataset, numerical method, model, coupled system, software, instrument,
   workflow, product, or another explicitly named object.
2. **Intended interaction** — observe, explain, compare, perturb, add/remove a
   capability, replace a representation, measure, reconstruct, predict,
   qualify, publish, or another stated intervention.
3. **Claim class** — descriptive, comparative, predictive, mechanistic,
   methodological, generalization, or operational.
4. **Evidence maturity** — exploratory, discriminating, confirmatory,
   qualification, or decision-ready.
5. **Engineering impact** — no code, analysis-only, data pipeline, model/process
   contract, numerical method, software architecture, or operational system.

A request such as “add a snow module to SHUD” is not an edge case. It is a
high-impact process-representation and software-capability change that needs
scientific framing, theory-to-code traceability, a staged study protocol, and an
engineering handoff after human approval.

## Outputs

Depending on the route, produce one or more durable artifacts defined in
[artifact-model.md](references/artifact-model.md):

- `research/project-profile.md`
- a research question or capability-gap brief
- a claim, hypothesis, alternative, or decision matrix
- a study protocol with baselines, controls, evidence and stop/go branches
- a theory-to-code traceability package
- run manifests and protocol amendments
- a claim-evidence matrix and research decision record
- `research/studies/<study-id>/engineering-handoff.md`

The lifecycle may end in `STUDY_CLOSED`, `INCONCLUSIVE`,
`DECISION_RECORDED`, `PRODUCT_HANDOFF_READY`, or
`ENGINEERING_HANDOFF_READY`. Code output is not required for success.

## When Not To Use

Do not use this skill for:

- a quick factual lookup or ordinary literature question; use direct research or
  `deep-research`
- a one-off plot, descriptive calculation, or already-specified analysis with no
  research decision
- ordinary implementation after scope and acceptance criteria are already fixed;
  use the delivery workflow
- product requirements that have already left the scientific-decision stage;
  use `prd-authoring` or the `product-manager` pack
- claims that ask an agent to replace domain-expert or PI judgment

## Profile Gate

Before substantive work, load `research/project-profile.md`.

- If it is missing, invoke `research-profile-bootstrap` and do not invent a
  domain profile from generic assumptions.
- The research profile is separate from `openspec/project-profile.md`.
  `research/project-profile.md` governs scientific objects, authorities,
  invariants, evidence and human gates. `openspec/project-profile.md` governs
  implementation risk surfaces, commands and software verification.
- When an approved research result crosses into engineering, the handoff maps
  scientific invariants into the OpenSpec fixture and updates the engineering
  profile only if a genuinely new implementation risk surface appears.

## Delegated Skills

Delegate deep work instead of duplicating it. A delegated workflow's pauses,
required confirmations and artifacts remain binding.

- `research-profile-bootstrap` — create or update the project-local research profile.
- `research-question-framing` — turn an observation, gap or proposed capability
  into a bounded research contract.
- `clarify` — resolve direct contradictions or missing acceptance conditions.
- `brainstorming` — explore competing directions before one is chosen.
- `blind-spot-pass` — investigate unfamiliar code, data, literature, conventions
  and adjacent surfaces before committing to a plan.
- `deep-research`, `researcher`, `docs-researcher` — gather source-backed external
  evidence and official documentation.
- `study-design` — produce a study protocol and evidence matrix.
- `theory-to-code-traceability` — govern changes to equations,
  parameterizations, scientific state, coupling or numerical representation.
- `grill-me` — pressure-test an existing question brief or protocol without
  persistent terminology work.
- `grill-with-docs` — pressure-test plans whose scientific terms or durable
  project decisions must be aligned with `openspec/glossary.md` and `docs/adr/`.
  Use it when the research terminology will govern implementation; keep
  research-only decision records under the study directory.
- `meta-loop` — audit whether the proposed produce/check/fix/recheck loop is
  credible for a high-cost or high-risk study.
- `scientific-evidence-synthesis` — assess what completed evidence supports,
  contradicts or leaves unresolved.
- `research-engineering-handoff` — convert an approved scientific decision into
  an implementation-ready upstream contract.
- `project-documentation` — realign durable repository documentation when a
  closed or handed-off study changes it.

## Lifecycle

### Phase 0: Resolve Context and State

1. Load the research profile and any existing study directory.
2. Identify the current artifact state rather than assuming a fresh study.
3. Record the five routing axes and the human decision owner.
4. State the chosen route in one concise paragraph before doing deep work.

### Phase 1: Frame the Research Contract

Invoke `research-question-framing` when the question, capability gap, intended
claim, alternatives, scope or decision rule is not already explicit.

For new scientific capability work, frame both:

- **scientific need** — what process, regime, scale or observable is missing
- **capability contract** — what the new representation must and must not do

Do not force every task into a hypothesis template. Hypotheses are appropriate
for explanatory claims; capability, method and data-product work may instead use
alternatives, invariants and qualification criteria.

### Phase 2: Ground the Work

Gather only evidence that can change the study design or decision:

- prior literature and accepted theory
- existing model/data/instrument behavior
- code and data lineage
- previous experiments, failures and decisions
- authoritative standards or operational constraints

Use `blind-spot-pass` before long work in unfamiliar territory. Use external
research agents when source-backed evidence is material. Keep facts, assumptions
and open uncertainties distinguishable.

### Phase 3: Build the Decision Space

Create the appropriate comparison object:

- competing hypotheses and discriminating predictions
- alternative process representations or parameterizations
- alternative datasets, measurements or algorithms
- status quo / do-less / defer / no-go options

Use `brainstorming` when the direction is still open. Use
`future-aware-architecture` only for genuine architecture or technology choices,
not as a substitute for scientific reasoning.

### Phase 4: Design the Study

Invoke `study-design`. The protocol must define:

- research units, cases, scales and regimes
- baselines, controls and unchanged sibling surfaces
- interventions, factors, ensembles or comparison arms
- observables, metrics, units and uncertainty treatment
- evidence oracles and where each fact can actually be validated
- stop, branch, go and no-go conditions
- compute/data budget and execution environment
- what is confirmatory versus exploratory
- amendment and deviation rules

If the work changes physical equations, process representation, scientific
state, units, coupling or numerics, invoke `theory-to-code-traceability` before
freezing the protocol.

### Phase 5: Pressure-Test and Freeze

Apply the shared gate in
[pressure-test-contract.md](references/pressure-test-contract.md): record one
explicit decision — `grill-me`, `grill-with-docs`, or `skipped:<reason>` (only
for genuinely narrow, low-impact work) — before freezing.

Freeze the approved protocol before result-aware execution. Freeze
mechanically — `scripts/provenance.py freeze <study-dir> --approver <name>`
computes the lock digest and refuses re-freezing. Later changes become
protocol amendments with what/why/when/claim impact; never silently rewrite the
original plan after seeing results.

### Phase 6: Execute and Observe

Execute only the approved protocol. Preserve:

- code, data, configuration and environment identities
- commands, logs, outputs and checksums where practical
- failures, retries and excluded runs
- every deviation from the protocol

Record runs mechanically where possible:
`scripts/provenance.py run <study-dir> --id <run-id> -- <command…>` captures
the command, logs, exit code and frozen-protocol binding, and refuses to run
against a silently modified protocol; `index` checksums the outputs
(see [artifact-model.md](references/artifact-model.md)).

Use `monitor` for harness-external long jobs such as Slurm runs. Monitoring does
not authorize changing the experiment or interpreting results.

### Phase 7: Analyze and Synthesize

Run `scripts/provenance.py verify <study-dir>` first so protocol-digest and
output-checksum conformance is machine-checked rather than narrated.

Separate predeclared analysis from result-driven exploration. Invoke
`scientific-evidence-synthesis` to produce:

- evidence supporting each claim or alternative
- counter-evidence and failed cases
- assumptions and uncertainty
- domain and scale of applicability
- what the evidence does not support
- status: supported-within-scope, contradicted, inconclusive,
  not-testable-with-current-design, or requires-independent-validation

### Phase 8: Human Decision

The PI, domain owner or named decision authority records the scientific decision.
Agents may organize evidence, challenge overclaims and suggest next steps, but
must not mark a mechanistic, validation or operational claim as accepted without
that human gate.

### Phase 9: Close or Handoff

Choose one explicit outcome:

- close and preserve the study
- revise the question or protocol
- create a follow-up research study
- hand an approved product/operational requirement to `product-manager`
- invoke `research-engineering-handoff`, then pass the result to
  `stage-change-pipeline` from `agentic-issue-delivery`

When the chosen outcome changes durable repository documentation (READMEs,
docs indexes, examples), delegate the realignment to `project-documentation`.

After implementation, use the delivery pack for reviewed PRs and
`codebase-stewardship` for long-term entropy and architecture governance. The
research profile and evidence remain the scientific oracle; implementation
artifacts must not rewrite them merely to clear a software gate.

## Hard Rules

1. Do not use a closed task taxonomy as the research ontology.
2. Do not equate calibration improvement with theory verification.
3. Do not equate software tests with scientific validation.
4. Preserve negative, no-go and “no code change” outcomes.
5. Define evidence and stop/branch conditions before interpreting primary results.
6. Keep result-aware amendments explicit and traceable.
7. Use the oracle that owns each fact: theory, observation, target hardware,
   production environment, or software test surface.
8. Keep human scientific judgment explicit and named.

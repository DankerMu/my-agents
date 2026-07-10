# Research Engineering Pack

## Purpose

This pack installs a scientific research control plane for substantive research
and research-driven system development. It accepts an initial phenomenon,
scientific uncertainty, capability gap, method idea, model-process change, data
need, instrument/workflow need, or operational decision and turns it into
traceable research artifacts, reviewed evidence, a named human decision, and—only
when authorized—an engineering handoff.

The pack deliberately does **not** define an exhaustive list of research task
types. It routes work on independent axes: research object, intended interaction,
claim class, evidence maturity, and engineering impact. Therefore a request such
as “add a snow module to SHUD” is first-class: it combines a new process
representation, model capability development, scientific verification and
high-impact software change.

## Backbone

```text
research/project-profile.md
        ↓
research-lifecycle
        ├─ research-question-framing
        ├─ theory-to-code-traceability (when scientific semantics change)
        ├─ study-design
        ├─ execution / manifests / amendments
        ├─ scientific-evidence-synthesis
        └─ human decision
              ├─ close / revise / next study
              ├─ product-manager handoff
              └─ research-engineering-handoff
                       ↓
                agentic-issue-delivery
                       ↓
                codebase-stewardship
```

Research success does not require code. Negative evidence, no-go decisions,
inconclusive studies and “do not change the model” are valid outcomes.

## Included Research Skills

- `research-lifecycle` — top-level router and artifact/state owner. It uses open
  routing axes rather than a closed taxonomy and delegates each deep phase.
- `research-profile-bootstrap` — scans a project and creates the living
  `research/project-profile.md` with scientific objects, authorities, recurring
  risk lenses, benchmark regimes, evidence oracles and human gates.
- `research-question-framing` — converts a phenomenon, gap or proposed capability
  into a bounded research contract without forcing every project into a
  hypothesis-only template.
- `study-design` — creates a protocol for observational, modeling, method,
  field/lab, data-product, forecast, capability-development or mixed studies,
  including baselines, controls, uncertainty, evidence oracles and branch gates.
- `theory-to-code-traceability` — maps approved assumptions, equations, process
  rules, state, units, invariants and numerics into code surfaces and verification
  cases. This is the core bridge for new scientific modules and parameterizations.
- `scientific-evidence-synthesis` — produces protocol-conformance and
  claim-evidence matrices, preserving counter-evidence, uncertainty, negative
  results and applicability limits before a human verdict.
- `research-engineering-handoff` — translates an approved scientific decision
  into a bounded upstream contract for OpenSpec and issue delivery while
  preserving scientific invariants and oracle separation.

## Included Support Skills

- `clarify` — resolves direct contradictions and material missing conditions.
- `brainstorming` — explores competing scientific, method or architecture directions.
- `blind-spot-pass` — investigates unknown code, data, literature, conventions,
  history and adjacent surfaces before committing to a study or design.
- `deep-research` — source-backed external research; also satisfies the bundled
  `researcher` agent dependency.
- `grill-me` — adversarially pressure-tests an existing question, protocol,
  traceability package or handoff when terminology is already stable.
- `grill-with-docs` — pressure-tests domain-heavy artifacts while reconciling
  project-wide terminology and long-lived decisions with
  `openspec/glossary.md` and `docs/adr/`.
- `future-aware-architecture` — handles real architecture/technology choices after
  scientific intent is framed; it does not choose scientific equations.
- `implementation-planning` — produces deep staged execution plans only after the
  scientific direction is approved.
- `meta-loop` — audits costly produce/check/fix/recheck loops and evaluator design.
- `project-documentation` — keeps the repository documentation set aligned with
  research and engineering evolution.

## Included Agents

- `explorer` — read-only mapping of code, data flows, study artifacts and impact surfaces.
- `researcher` — web-backed multi-source research using `deep-research`.
- `docs-researcher` — official documentation and contract verification; its
  `clarify` dependency is explicitly included.
- `monitor` — quiet, read-only monitoring for Slurm, remote PIDs, CI and other
  harness-external long-running jobs. It never changes the protocol or interprets results.

No new broad “research coordinator” agent is added. The main orchestrator follows
`research-lifecycle`; specialist agents stay narrow and permission-bounded.

## Research Profile Generation

The active scientific profile is project-local at:

```text
research/project-profile.md
```

`research-profile-bootstrap` creates it the first time the pack is used and
updates it only when the project gains a recurring scientific surface. It scans
repository evidence, then composes whichever lenses apply—for example scientific
process/model, observations/instruments, data product, forecast/ensemble,
numerical/performance, coupled system and operational qualification. Lenses are
composable, not mutually exclusive task categories.

The research profile records scientific objects, authorities, invariants,
benchmark regimes, evidence oracles, recurrent hazards and human gates. It must
stay lean and cite project evidence rather than becoming a textbook.

This file is intentionally separate from:

```text
openspec/project-profile.md
```

The OpenSpec profile belongs to `subagent-workflow` and governs software entry
surfaces, implementation contracts, risk packs, commands and verification
matrix. `research-engineering-handoff` maps approved scientific invariants into
an OpenSpec change and requests an engineering-profile update only when a new
recurring software risk surface appears. The two profiles reference each other;
they are not merged or duplicated.

## Pack Coupling

### `agentic-issue-delivery`

Use after `research-engineering-handoff` reaches
`ENGINEERING_HANDOFF_READY`. `stage-change-pipeline` turns the approved handoff
into a reviewed OpenSpec change and implementation-ready issue DAG;
`subagent-workflow` implements, reviews, verifies and human-gates the PRs.
Scientific uncertainty must not be delegated to implementers.

### `product-manager`

Use when research produces an approved user-facing, operational or product
requirement. The research evidence remains the source; the product pack owns PRD,
prioritization and backlog semantics.

### `codebase-stewardship`

Use after or alongside implementation to govern module depth, architecture,
control-plane health and entropy. It may propose refactoring but must preserve the
scientific invariants and evidence authorities carried by the handoff.

The complete coupling is documented in
[`docs/architecture/research-engineering-flow.md`](../../docs/architecture/research-engineering-flow.md).

## Install

```bash
npx my-agents install pack research-engineering
npx my-agents install pack research-engineering --platform codex --scope project
```

For a full research-to-delivery environment, use a project manifest:

```json
{
  "schemaVersion": 1,
  "platforms": ["claude", "codex"],
  "packs": ["research-engineering", "agentic-issue-delivery", "codebase-stewardship"]
}
```

Add `product-manager` when research outcomes also feed product planning.

## External Requirements

The pack does not install domain software, data, compilers, schedulers or
scientific models. A project supplies its real toolchain and evidence oracles.
External research sources require network access; long-running workflows may
require authenticated HPC/Slurm or other project-specific systems.

---
name: theory-to-code-traceability
description: >
  Build and review a traceability contract from scientific assumptions,
  equations, process representations, units, invariants, and numerical choices
  to code surfaces and verification cases. Use for new or changed scientific
  model capabilities such as adding a snow module, changing a parameterization,
  coupling processes, or altering numerical methods. Do not use for ordinary
  feature implementation or scientific validation by itself.
invocation_posture: manual-first
version: 0.1.0
---

# Theory to Code Traceability

Use this skill when a research decision changes what a scientific system means,
not merely how its software is organized. The output is a reviewed contract that
lets a domain expert, model developer, implementer, and reviewer point to the
same assumptions, equations, state variables, code boundaries, invariants, and
verification evidence.

This workflow covers more than equation edits. Activate it for:

- a new process representation, such as snow accumulation, melt, refreezing,
  sublimation, or snow-soil energy coupling
- changed constitutive relations, parameterizations, thresholds, source/sink
  terms, closures, or boundary conditions
- new scientific state, diagnostics, units, sign conventions, or output meaning
- altered spatial/temporal discretization, solver coupling, numerical precision,
  parallel reductions, conservation treatment, or timestep policy
- changes that preserve equations but alter how scientific meaning is encoded or
  exchanged across model components

## When Not To Use

Do not use this skill for:

- ordinary UI, API, build, documentation, or infrastructure features with no
  scientific semantic change
- a pure literature review before a concrete representation is being designed;
  use `deep-research`
- implementation sequencing after the scientific and numerical contract is
  already fixed; use `implementation-planning`
- claims that a model is valid in reality; this workflow establishes
  **verification traceability**, not observational validation

## Inputs and Outputs

Inputs may include theory papers, equations, existing model docs, source code,
reference implementations, data contracts, prior ADRs, benchmarks, and an
approved research question or capability-gap brief.

Produce a package under the active study directory using
[traceability-template.md](references/traceability-template.md), normally:

```text
research/studies/<study-id>/traceability/
  scientific-contract.md
  equation-code-matrix.md
  verification-ladder.md
```

The package must name:

- scientific intent and non-goals
- assumptions, regimes and excluded physics
- symbols, units, sign conventions and coordinate/time bases
- governing equations or algorithmic process rules
- conserved quantities, invariants and admissible state bounds
- continuous-to-discrete choices and expected numerical behavior
- code producers, state holders, update order, consumers and output surfaces
- verification cases and the evidence oracle for each claim
- unresolved scientific or numerical decisions

## Delegated Skills

- Use `deep-research`, `researcher`, or `docs-researcher` when equations,
  parameterizations, standards, libraries, or reference implementations require
  source-backed verification.
- Use `explorer` to map the current code and data path before proposing a new
  mapping.
- Use `blind-spot-pass` when changing an unfamiliar model process or numerical
  surface; feed discovered hazards into the traceability matrix.
- Use `brainstorming` when multiple scientific representations remain viable.
- Use `grill-me` to pressure-test a stable traceability draft when terminology is
  already settled.
- Use `grill-with-docs` when process names, state semantics, coupling boundaries,
  or long-lived implementation decisions must be reconciled with
  `openspec/glossary.md` and `docs/adr/`.
- Use `future-aware-architecture` only for genuine system-architecture choices,
  such as whether a process belongs inside the solver core or behind a plug-in
  boundary. It does not decide scientific equations.
- Use `study-design` to turn the completed contract into staged verification and
  scientific evaluation studies.

Delegated workflows keep their own confirmation gates and required artifacts.

## Workflow

### 1. Establish the Scientific Contract

State the capability or representation without embedding implementation details.
For a snow module, define at least:

- which snow states exist: SWE, liquid water, temperature, density, albedo, or a
  deliberately smaller state set
- which processes are in scope: accumulation, phase partition, melt,
  refreezing, sublimation, compaction, canopy interception, soil coupling
- spatial and temporal support
- forcing variables and their authority
- intended outputs and downstream consumers
- excluded processes and the regime where those exclusions are acceptable

Separate **must represent**, **may approximate**, and **out of scope**.

### 2. Inventory Alternatives and Assumptions

Record plausible representations and the assumptions each introduces. Include the
status quo and a simpler representation when they are scientifically defensible.
For each option, identify:

- required input data and parameter identifiability
- process coverage and known failure regimes
- conservation and stability implications
- observables that can discriminate the option
- computational and maintenance cost

Do not select an option merely because it is easiest to code.

### 3. Normalize Symbols and Semantics

Create one canonical vocabulary for symbols, state variables, flux directions,
units, missing values, coordinate systems, calendars, and update timing.

- Reuse existing project terminology where it is correct.
- Resolve overloaded or conflicting terms before code mapping.
- Use `grill-with-docs` when the terminology will govern future OpenSpec and code
  work; persist project-wide terms in `openspec/glossary.md`.
- Keep study-specific derivation detail in the study traceability package, not in
  the project glossary.

### 4. Map Theory to Numerical Representation

For each governing relation or process rule, document:

- continuous or conceptual form
- discretized/algorithmic form
- source and sink signs
- update order and coupling sequence
- bounds, conservation expectations and failure states
- solver or timestep interaction
- approximation and truncation choices

A scientific contract is incomplete if a reviewer cannot tell which choices are
physics, which are numerical method, and which are implementation convenience.

### 5. Map Numerical Representation to Code

Trace every scientific responsibility across the implementation surface:

```text
forcing / parameters
  -> parser and validation
  -> state initialization
  -> process update / RHS / operator
  -> coupling and aggregation
  -> solver or time integration
  -> diagnostics and outputs
  -> downstream readers / products
```

For each row in the equation-code matrix name:

- scientific term or rule
- source-of-truth document
- code producer and state owner
- all consumers and sibling surfaces
- expected unit and sign
- verification case
- current status: existing / modify / new / unresolved

Do not treat a single function pointer as the whole mapping when state, I/O,
restart, coupling, or downstream consumers also carry the meaning.

### 6. Design the Verification Ladder

Verification precedes observational validation and calibration. Select only
levels that are relevant, but make the progression explicit:

1. dimensional, sign and range checks
2. unit tests of individual relations and branch boundaries
3. zero/limit/symmetry cases
4. conservation or invariant checks
5. analytic, manufactured, or independently computed reference cases
6. component integration and update-order tests
7. restart, serialization, backward-compatibility and output-contract tests
8. small controlled model cases
9. regression against unchanged processes and sibling regimes
10. observational or intercomparison studies designed in `study-design`

For each case, state input, expected result, tolerance, oracle, and what failure
would mean. A passing observational metric cannot substitute for a missing
formula-level verification case.

### 7. Pressure-Test the Contract

Before approval, record one of:

- `grill-me`: used when terms and project decisions are already stable
- `grill-with-docs`: used when terminology, process boundaries, or durable
  decisions need persistence
- `skipped:<reason>`: only for a genuinely narrow, low-impact semantic change

Challenge at least:

- missing states or fluxes
- double counting and omitted coupling
- unit, calendar and temporal-support ambiguity
- hidden parameter compensation
- conservation and boundary failures
- restart and backward-compatibility behavior
- data availability and identifiability
- whether the selected representation can be falsified or qualified

### 8. Human Approval and Downstream Route

A named scientific owner approves the contract or records unresolved questions.
The approved package becomes an input to `study-design` and, after a research
decision, `research-engineering-handoff`.

Do not write implementation issues directly from an unapproved traceability
draft. The handoff must carry the governing scientific invariants into the
OpenSpec fixture, and later software changes must not weaken the scientific
oracle merely to pass tests.

## Hard Rules

1. Verification, validation, and calibration remain distinct.
2. Every scientific symbol and state has one explicit unit and meaning.
3. Conservation, admissible bounds, and update order are first-class contracts.
4. A code mapping covers producers, state, coupling, I/O, restart and consumers,
   not only the central equation function.
5. Negative and no-go outcomes are acceptable.
6. Human domain approval is required before engineering handoff.

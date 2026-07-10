---
name: research-profile-bootstrap
description: >
  Create or update a lean project-local research profile at
  research/project-profile.md by scanning repository evidence, scientific
  objects, data/model surfaces, authority sources, invariants, study practices,
  execution environments and human gates. Use when installing
  research-engineering or when a project gains a recurring scientific surface.
  Do not use for per-study protocols or the software-risk profile at
  openspec/project-profile.md.
invocation_posture: hybrid
version: 0.1.0
---

# Research Profile Bootstrap

Create a living profile that tells research workflows what this project studies,
which artifacts are authoritative, what must remain scientifically true, and
what evidence can support which claims. The profile is generated from repository
evidence and explicit human decisions, not from a generic domain stereotype.

## Canonical Location and Separation

The active research profile lives at:

```text
research/project-profile.md
```

It is not the same artifact as `openspec/project-profile.md`:

- `research/project-profile.md` governs scientific objects, process/model/data
  authority, invariants, evidence standards, benchmark cases and human gates.
- `openspec/project-profile.md` is owned by `subagent-workflow` and governs code
  surfaces, software risk packs, commands and the implementation verification
  matrix.

Do not merge the two files. They have different readers and change at different
rates. Link them through `research-engineering-handoff` when research becomes
software work.

## When To Activate

- `research-lifecycle` starts and the research profile is missing.
- A project adopts the `research-engineering` pack.
- A project adds a recurring scientific surface: a new process family, sensor,
  dataset class, model, instrument, observation network, experiment facility,
  forecast system, or evidence oracle.
- The existing profile is stale or contradicted by repository facts.

## When Not To Use

- Do not update the profile for every study or issue.
- Do not put study-specific hypotheses, parameter ranges, results or task lists
  in the profile.
- Do not restate an entire glossary, design document, literature review or
  software command guide.
- Do not guess domain facts that lack repository evidence or human confirmation.

## Generation Method

### Step 1: Scan Existing Authorities

Use `explorer` or direct read-only inspection to map:

- root README and documentation indexes
- existing `research/`, `docs/`, `openspec/`, ADR and glossary artifacts
- model/process code, scientific schemas, variable registries and configuration
- data manifests, catalogs, input/output formats and provenance records
- notebooks, analysis packages, benchmarks, fixtures and validation datasets
- CI, Makefiles, workflow scripts, HPC/Slurm entrypoints and target environments
- published or release-frozen baselines

If `openspec/project-profile.md` exists, read it for engineering surfaces and
commands, but do not copy it wholesale into the research profile.

### Step 2: Run a Blind-Spot Pass When Needed

Invoke `blind-spot-pass` when the project is unfamiliar or its scientific
surfaces span multiple repositories. Focus the pass on hidden authorities,
legacy formats, benchmark lineage, tacit process assumptions, dangerous data
transformations, and downstream consumers.

### Step 3: Compose Lenses, Do Not Select One Exclusive Type

Use the reusable lenses in [profile-template.md](references/profile-template.md)
as prompts, not as a taxonomy. A project can combine any number of lenses:

- process/model representation
- observation/instrument/field or laboratory evidence
- data product and transformation pipeline
- forecast/ensemble/operational qualification
- numerical method and performance
- cross-system or coupled-model integration

Add a new lens when repository evidence requires it. Never force a project into
one category.

### Step 4: Draft the Profile From Evidence

Fill the profile fields with short bullets and file/path anchors:

1. identity and research scope
2. research objects and recurring surfaces
3. canonical sources and authority order
4. scientific invariants and claim boundaries
5. data, space, time, units and missing/QC conventions
6. default baselines, controls and benchmark cases
7. evidence-oracle matrix
8. execution environments and run identity requirements
9. human decision gates and forbidden autonomous conclusions
10. engineering handoff mapping
11. unresolved assumptions and confidence

Every non-obvious profile statement should point to a repository artifact or be
marked `human-confirmed`, `inferred`, or `unknown`.

### Step 5: Resolve Material Ambiguity

Use `grill-me` when the draft has an unresolved decision but no terminology needs
persistence. Use `grill-with-docs` when a term, process boundary or durable
project decision will govern later OpenSpec and code work. Ask one material
question at a time and provide a recommended answer.

### Step 6: Write and Validate

Write `research/project-profile.md` using the template. Keep it lean:

- simple/single-system project: target under about 50 lines
- broad multi-model or multi-observation system: target under about 100 lines
- use links and anchors instead of prose duplication
- split subsystem appendices only when a single profile becomes unreadable

Before finishing, verify:

- every canonical authority actually exists or is explicitly planned
- benchmark and evidence claims name a real oracle
- human gates name a role, not “the user” generically
- the profile does not contain study-specific results
- the separation from `openspec/project-profile.md` is stated

## Maintenance Rules

Update the profile only when a recurring project-level surface changes. A study
that merely uses an existing surface should not edit it. When a study discovers a
new persistent invariant, data authority or evidence oracle, update the profile
and record the evidence anchor.

## Output

Return:

- created/updated profile path
- lenses applied
- evidence anchors inspected
- unresolved profile gaps
- whether `openspec/project-profile.md` exists and what the later handoff must map

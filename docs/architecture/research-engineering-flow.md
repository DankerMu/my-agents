# Research Engineering: Scientific Control Plane and Pack Coupling

## Purpose

`research-engineering` governs how a project moves from an uncertain scientific
or technical situation to evidence and a human decision. It is broader than a
study runner: it also covers new model processes, scientific software
capabilities, numerical methods, data products, instruments/workflows, coupled
systems and operational qualification.

The pack avoids a closed task taxonomy. Work is classified on independent axes:

- research object
- intended observation/intervention/change
- intended claim
- evidence maturity
- engineering impact

This is why “add a snow module to SHUD” is naturally represented: the research
object is the land-surface/hydrologic process model, the interaction is to add a
process capability, the likely claims include methodological and predictive
ones, evidence progresses from verification to scientific evaluation, and the
engineering impact spans state, forcing, solver/coupling, output and downstream
consumers.

## Four Pack Responsibilities

```text
research-engineering
  owns: question/capability framing, research profile, theory-to-code contract,
        study protocol, evidence synthesis, human research decision
        │
        ├── product/operational requirement ──> product-manager
        │
        └── approved engineering change ──────> agentic-issue-delivery
                                                   │
                                                   └── merged code
                                                          ↓
                                                   codebase-stewardship
```

### Research Engineering

Answers:

- What object, process, method, data or capability is under study?
- What exactly is uncertain or missing?
- What scientific meaning and invariants must hold?
- What study can discriminate alternatives or qualify the capability?
- What evidence supports, contradicts or fails to test each claim?
- What did the named human authority decide?

It may terminate without code.

### Product Manager

Answers:

- Which approved research result becomes a user-facing or operational requirement?
- How is it prioritized, communicated and converted into a product backlog?

It does not reinterpret scientific evidence.

### Agentic Issue Delivery

Answers:

- How is an approved engineering handoff converted into OpenSpec, small issues,
  reviewed implementation, independent finding verification, CI evidence and a
  human-gated merge?

It treats the handoff's scientific invariants as an upstream oracle and does not
send unresolved scientific choices to implementers.

### Codebase Stewardship

Answers:

- Does the evolving implementation remain understandable, deep, testable and
  governed?
- Where are architecture, naming, dependency, protocol and control-plane entropy
  accumulating?

Refactoring may change structure, not scientific meaning without a new research decision.

## Two Project Profiles

### `research/project-profile.md`

Owned by `research-profile-bootstrap` and `research-lifecycle`. It records:

- recurring scientific objects and project boundaries
- theory, data, model, instrument and product authorities
- scientific state, units, time/space semantics and invariants
- benchmark regimes and unchanged sibling cases
- evidence oracles and qualification stages
- recurrent research hazards and human gates
- applicable composable profile lenses

The profile is generated from repository evidence and updated only when the
project gains a recurring scientific surface. Study-specific detail stays under
`research/studies/<study-id>/`.

### `openspec/project-profile.md`

Owned by `subagent-workflow`. It records:

- software entry surfaces and public contracts
- implementation risk axes and domain risk packs
- setup/lint/test/build commands
- verification matrix and evidence types

### Synchronization Rule

`research-engineering-handoff` carries only the approved scientific invariants,
relevant authorities and required evidence into OpenSpec. During delivery, update
`openspec/project-profile.md` only for a genuinely new recurring software risk
surface. Never duplicate the entire research profile into the software profile,
and never let a software gate rewrite the research evidence record.

## Example: Adding a Snow Module

```text
1. research-profile-bootstrap
   identify existing process/state/forcing/output authorities and benchmark regimes

2. research-question-framing
   define the missing snow capability, regimes, alternatives, claims and non-goals

3. blind-spot-pass + deep-research + explorer
   inspect accepted theory, existing process order, forcing/data availability,
   restart/output consumers and prior decisions

4. theory-to-code-traceability
   map snow states, units, phase partition, energy/mass terms, coupling, bounds,
   update order, code surfaces and verification ladder

5. study-design
   define idealized tests, conservation cases, no-snow regression, multi-climate
   observational evaluation, uncertainty and go/no-go branches

6. grill-me or grill-with-docs
   pressure-test the scientific contract and persist project terminology/ADRs when needed

7. execute + scientific-evidence-synthesis + human decision
   decide whether representation is rejected, revised, approved for implementation,
   or approved only for a limited domain

8. research-engineering-handoff
   preserve invariants, verification, scientific evaluation and rollback

9. stage-change-pipeline -> subagent-workflow
   OpenSpec, issue DAG, implementation, review, verifier, CI, human merge

10. codebase-stewardship
    audit whether the new module creates shallow boundaries, duplicated state,
    drifted terminology or unverifiable coupling
```

## Shared Skills Without Duplicated Workflows

The research skills delegate instead of embedding copies:

- `clarify` for direct ambiguity and contradictions
- `brainstorming` for open option spaces
- `blind-spot-pass` for unknown unknowns
- `deep-research` and research agents for external evidence
- `grill-me` for adversarial pressure-testing without persistence
- `grill-with-docs` for pressure-testing plus project glossary/ADR persistence
- `future-aware-architecture` for architecture decisions
- `implementation-planning` for post-decision execution planning
- `meta-loop` for checking expensive verification/evaluation loops

Delegated pauses, confirmations and outputs remain binding.

## Adoption Baseline

A research project normally installs:

```json
{
  "schemaVersion": 1,
  "platforms": ["claude", "codex"],
  "packs": ["research-engineering", "agentic-issue-delivery", "codebase-stewardship"]
}
```

This composition creates one connected flow while keeping scientific judgment,
software delivery and long-term code governance under separate contracts.

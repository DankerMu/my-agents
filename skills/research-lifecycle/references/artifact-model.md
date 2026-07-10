# Research Artifact Model

Use this model as a portable default; adapt names only when the project already
has an equivalent source of truth.

```text
research/
├── project-profile.md
├── glossary.md                         # optional research-only terminology
├── studies/
│   └── <study-id>/
│       ├── question.md
│       ├── protocol.md
│       ├── protocol.lock.json
│       ├── amendments/
│       ├── manifests/
│       │   ├── data.json
│       │   ├── software.json
│       │   └── environment.json
│       ├── runs/<run-id>/
│       │   ├── run.json
│       │   ├── command.txt
│       │   ├── logs/
│       │   └── outputs.index.json
│       ├── analysis/
│       ├── evidence/
│       │   ├── evidence-index.json
│       │   └── claim-evidence.md
│       ├── decision.md
│       └── engineering-handoff.md
└── decisions/                          # optional cross-study research decisions
```

## Artifact states

This list is the canonical study-level state vocabulary; do not invent study
states elsewhere. Artifact-level status enums (protocol, traceability package,
engineering handoff) are defined in their own templates and use UPPERCASE
values.

- `FRAMING`: question/capability contract is being formed.
- `DESIGNING`: protocol and traceability are being drafted.
- `PROTOCOL_FROZEN`: execution may begin; changes require amendments.
- `EXECUTING`: approved runs are in progress.
- `ANALYZING`: results exist but claims are not yet accepted.
- `DECISION_PENDING`: evidence package is ready for a human gate.
- `DECISION_RECORDED`: the named human authority has recorded a verdict; a
  Phase 9 outcome (close, revise, follow-up study, product or engineering
  handoff) is being selected.
- `STUDY_CLOSED`: study is complete, including negative/no-go outcomes.
- `INCONCLUSIVE`: current design cannot distinguish the alternatives.
- `PRODUCT_HANDOFF_READY`: approved result may become a product requirement.
- `ENGINEERING_HANDOFF_READY`: approved result may enter OpenSpec delivery.

## Profile separation

`research/project-profile.md` and `openspec/project-profile.md` are deliberately
separate living files:

- research profile: scientific objects, authorities, invariants, data semantics,
  evidence standards, benchmark cases and human gates
- engineering profile: code entry surfaces, contracts, risk axes, commands and
  verification matrix used by implementation review

The engineering handoff binds them. It copies only the relevant scientific
contracts into OpenSpec and updates the engineering profile when the new work
introduces a recurring software risk surface.

## Terminology and decision ledgers

`openspec/glossary.md` remains the single source for project-wide ubiquitous
language, and `docs/adr/` remains the ledger for long-lived project decisions
(both owned by the `grill-with-docs` conventions). The optional research
ledgers are subordinate staging areas with one-way promotion rules:

- `research/glossary.md` may hold research-only terms (working symbols,
  study-internal shorthand). The moment a term is used by a traceability
  package, an engineering handoff, or any artifact that will govern OpenSpec
  or code work, move its definition to `openspec/glossary.md` and leave only a
  pointer here. Never keep two definitions of the same term.
- `research/decisions/` may hold cross-study research decisions that do not
  meet the `docs/adr/` thresholds. When such a decision starts governing
  long-lived implementation behavior, record it in `docs/adr/` and leave a
  pointer. Promotion is one-way; do not copy ADR or glossary content back into
  the research ledgers.

## Protocol amendments

Each amendment records:

```text
Amendment ID:
Changed artifact/section:
Reason:
Results visible before the change:
Affected claims:
Required reruns or relabeling:
Approved by:
```

Never overwrite the frozen protocol without retaining the original and the
amendment trail.

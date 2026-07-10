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

- `FRAMING`: question/capability contract is being formed.
- `DESIGNING`: protocol and traceability are being drafted.
- `PROTOCOL_FROZEN`: execution may begin; changes require amendments.
- `EXECUTING`: approved runs are in progress.
- `ANALYZING`: results exist but claims are not yet accepted.
- `DECISION_PENDING`: evidence package is ready for a human gate.
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

# Research Engineering Handoff Template

```markdown
# Engineering Handoff: <study-id> / <change>

## Status and Authority
- Status: DRAFT | REVIEWED | ENGINEERING_HANDOFF_READY | REJECTED
- Study ID:
- Research profile:
- Scientific owner / approver:
- Approval record and date:
- Source protocol / amendments:
- Source evidence synthesis:
- Theory-to-code package:

## Accepted Decision
- Evidence-supported decision:
- Intended claim/capability:
- Applicability scope:
- Known limits:

## Required Behavioral Change
- New / changed behavior:
- Disabled/default/fallback behavior:
- User-visible or downstream effects:

## Scientific and Numerical Invariants
| Invariant | Authority | Affected surfaces | Engineering verification | Later scientific evaluation |
|---|---|---|---|---|

## Data and Model Authorities
- Input datasets / forcing / observations:
- Versions, lineage and checksums:
- Units, calendars, coordinate/grid/vertical references (if applicable):
- State, parameter and output schema authorities:

## Scope Map
| Surface | In scope / regression / later / out | Owner | Reason |
|---|---|---|---|

## Verification Requirements
- Formula/process unit and boundary cases:
- Conservation / admissible-state checks:
- Reference / manufactured / independent calculations:
- Restart / serialization / compatibility:
- Build / target platform / performance:
- Unchanged sibling regressions:

## Scientific Evaluation After Implementation
- Cases / observations / holdout:
- Metrics and uncertainty:
- Go / no-go / qualification gate:
- Calibration allowed only after:

## Forbidden Shortcuts
- ...

## Delivery Strategy
- OpenSpec change name seed:
- Dependencies and PR boundaries:
- Feature flag / inactive asset / staged rollout:
- Rollback target:
- Post-merge study obligations:

## Profile Synchronization
- New recurring software risk surface: yes | no
- Required `openspec/project-profile.md` update:
- Research profile remains authoritative for:

## Pressure-Test
- Mode: grill-me | grill-with-docs | skipped:<reason>
- Closed decisions:
- Open human questions:

## Downstream Route
- `stage-change-pipeline` input package:
- Product-manager handoff also required: yes | no
```

# Theory-to-Code Traceability Template

Use only the sections relevant to the proposed scientific change. Keep equations
and derivations as detailed as necessary, but keep the mapping tables explicit.

```markdown
# Scientific Contract: <capability or process>

## Identity
- Study ID:
- Scientific owner:
- Status: DRAFT | REVIEWED | APPROVED | REJECTED
- Source profile: `research/project-profile.md`

## Scientific Intent
- Need / capability gap:
- Intended regimes and scales:
- Must represent:
- May approximate:
- Non-goals / excluded physics:

## Alternatives
| Option | Assumptions | Required data | Failure regimes | Discriminating evidence | Status |
|---|---|---|---|---|---|

## Symbols and State
| Symbol / canonical term | Meaning | Unit | Sign / direction | Spatial-temporal support | Bounds |
|---|---|---|---|---|---|

## Governing Relations or Process Rules
### <relation/process>
- Source / authority:
- Continuous or conceptual form:
- Assumptions:
- Boundary / initial conditions:
- Conservation or invariant:

## Numerical Representation
- Discrete form / algorithm:
- Update order:
- Coupling:
- Timestep / solver interaction:
- Approximation and expected error:
- Failure / fallback behavior:

## Equation-to-Code Matrix
| Scientific responsibility | Authority | Producer / owner | Consumers / sibling surfaces | Unit / invariant | Change | Verification |
|---|---|---|---|---|---|---|

## Verification Ladder
| Level | Case | Input | Expected result / tolerance | Oracle | Failure meaning |
|---|---|---|---|---|---|

## Pressure-Test
- Mode: grill-me | grill-with-docs | skipped:<reason>
- Decisions closed:
- Open questions:
- Glossary / ADR changes:

## Approval
- Scientific owner verdict:
- Conditions / limits:
- Approved downstream studies:
- Engineering handoff allowed: yes | no
```

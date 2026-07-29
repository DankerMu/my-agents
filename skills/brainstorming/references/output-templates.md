# Output Templates

Output scales to scope. Do not produce documents nobody will read. Quick scope produces no artifact — the conversation is the record.

## Standard — Decision Brief (inline in chat, or saved to file on request)

```
## Decision Brief: [Topic]

**Problem**: [1–2 sentences on what we're solving and why]

**Approach**: [Chosen direction and key design elements]

**Key decisions**:
- [Decision]: [rationale]
- [Decision]: [rationale]

**Not doing**: [Explicit exclusions that might otherwise be assumed in scope]

**Assumptions**: [Things we believe to be true but haven't verified]

**Next step**: [proceed to planning / implementation / other]
```

## Deep — Design Decision Record (saved to file)

```markdown
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
scope: deep
---

# [Topic]

## Problem
[Who is affected, what is changing, and why it matters]

## Approach
[Description of the chosen design direction and its rationale]

## Design Overview
[Architecture, components, data flow — as detailed as the complexity warrants]

## Decisions

| # | Decision | Alternatives Considered | Rationale |
|---|----------|------------------------|-----------|
| 1 | ... | ... | ... |

## Assumptions
- [Assumption 1]

## Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ... | ... | ... | ... |

## Non-Goals
- [Explicit exclusion 1]

## Open Questions
- [Questions deferred to planning or implementation]

## Next Steps
[Recommended path forward]
```

Save to a sensible location in the project (e.g., `docs/decisions/`, `docs/brainstorms/`, or the project's existing convention). Ask the user if unsure about location.

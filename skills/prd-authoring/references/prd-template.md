# PRD Template

> Moved from SKILL.md. Lean PRDs use sections 1, 2, 4, 7, 9 only; the quality bar and self-review checklist stay in SKILL.md.

```markdown
# PRD: [Product/Feature Name]

- Status: Draft | In review | Approved
- Owner: [name]  ·  Last updated: [date]
- Links: [research, designs, related PRDs/ADRs]

## 1. Problem
[Who hurts, when, and the evidence. 2-4 sentences, no solution language.]

## 2. Goals & Non-goals
- Goals: [outcomes, not features — max 3-5]
- Non-goals: [explicitly out of scope, with one-line reasons]

## 3. Users & Jobs
[Primary user segments and the job-to-be-done each hires this product for.]

## 4. Requirements
| # | Requirement | Priority | Acceptance criteria |
|---|-------------|----------|---------------------|
| R1 | [user-visible behavior] | Must / Should / Could | Given/When/Then, testable |

## 5. UX Notes
[Key flows, states, and edge cases. Link designs; do not restate them.]

## 6. Non-functional Requirements
[Performance, reliability, security, privacy, accessibility, i18n — only those that
constrain this work, each with a threshold.]

## 7. Success Metrics
| Metric | Baseline | Target | When measured |

## 8. Rollout
[Phases, guardrails, kill criteria, migration/compat notes if any.]

## 9. Risks & Open Questions
| Item | Type (risk/question) | Owner | Resolve by |
```

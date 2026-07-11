---
name: prd-authoring
description: >
  Write a review-ready PRD — prioritized requirements, testable acceptance criteria, success
  metrics — from validated discovery output once a direction is already chosen. Triggers: "write
  a PRD", "product spec", "requirements doc", "写PRD", "需求文档", "产品规格". Not for open-ended
  ideation (brainstorming), requirement disambiguation (clarify), fresh cited research
  (deep-research), business-model work (business-plan), or execution planning
  (implementation-planning).
invocation_posture: hybrid
version: 0.1.3
---

# PRD Authoring

Produce a Product Requirements Document that an engineer can build from and a reviewer can
verify against. The PRD is the bridge between product discovery and delivery: upstream skills
converge on *what problem and which direction*; this skill pins down *what exactly to build
and how to know it works*; downstream skills turn the result into tracked work items.

## When Not To Use

- The user is still comparing directions or ideating → `brainstorming` first.
- The request itself is ambiguous or contradictory → `clarify` first.
- The main need is fresh, cited market/competitor/user research → `deep-research` first.
- The deliverable is a business plan, financial model, or pitch narrative → `business-plan`.
- The product scope is settled and the question is technical execution (phasing, rollback,
  dependency ordering) → `implementation-planning`.
- The user wants issues in a tracker, not a document → `gh-create-issue` (a PRD can feed it,
  but is not required for simple work).

## Intake Gate

Before drafting, confirm three inputs exist. If any is missing, name the gap and route
upstream instead of inventing content:

1. **A chosen direction** — one candidate solution, not a menu. Missing → `brainstorming`.
2. **A named user and problem** — who has the problem and what evidence says it is real.
   Missing → `clarify` or `deep-research`.
3. **A definition-of-success sketch** — what changes for the user or the business if this
   ships. Missing → ask one focused question; do not proceed on "we'll figure out metrics
   later".

State assumptions explicitly when the user tells you to proceed with gaps; put them in the
PRD's Open Questions with an owner.

## Process

1. **Scope the document.** Ask (or infer from context) which depth fits:
   - **Lean** (~1-2 pages): single feature, one team, low coordination cost. Sections:
     Problem, Goals/Non-goals, Requirements with acceptance criteria, Metrics, Open questions.
   - **Full** (~3-6 pages): multi-team, external dependencies, or irreversible choices.
     All template sections below.
   Default to Lean; upgrade only when coordination or risk justifies it.
2. **Draft the skeleton first.** Lay out all section headers with one-line intent each and
   confirm the structure with the user before filling long-form content.
3. **Fill sections against the quality bar** (below). Pull real evidence from the
   conversation, linked research, and the codebase where relevant; never fabricate data,
   quotes, or metrics baselines.
4. **Self-review** with the checklist (below) and fix failures before presenting.
5. **Handoff.** Offer the natural next step: `gh-create-issue` to decompose the PRD into an
   epic and sub-issues; `implementation-planning` when the build needs a phased technical
   plan; `stage-change-pipeline` when the project runs the OpenSpec delivery flow.

## PRD Template

Full template: [references/prd-template.md](references/prd-template.md) — read it before drafting.

Lean PRDs use sections 1, 2, 4, 7, 9 only.

## Quality Bar

- Every **Must** requirement has acceptance criteria a tester could run without asking
  anything. "Works well" and "fast" fail this bar; thresholds and observable behavior pass.
- **Non-goals are real decisions**, not filler — each one should disappoint someone.
- **Metrics are measurable as written**: a metric with no baseline needs a plan to get one;
  a target with no date is a wish.
- **Problem section contains zero solution language.** If the problem can only be stated in
  terms of the feature, the discovery work upstream is not done.
- **Open questions have owners and dates.** An unowned question is a risk mislabeled.
- Requirements describe **user-visible behavior**, not implementation. "Store sessions in
  Redis" belongs in the engineering plan; "user stays signed in across restarts for 30 days"
  belongs here.

## Self-review Checklist

Run before presenting the draft; fix failures rather than shipping caveats:

- [ ] Could an engineer scope this without a meeting? (If not, which section is vague?)
- [ ] Could QA derive test cases from section 4 alone?
- [ ] Does every goal have at least one metric, and every metric trace to a goal?
- [ ] Would cutting each Should/Could requirement still leave the Must set coherent?
- [ ] Is anything stated as fact that is actually an assumption? Move it to section 9.

## Output Contract

- A single Markdown document. Default location `docs/prd/<kebab-case-name>.md` when the user
  wants it in the repo (create the directory lazily); otherwise deliver inline in chat.
- When the project maintains `openspec/glossary.md`, use its canonical terms for domain
  concepts; flag new terms the PRD introduces so they can be added.
- Keep the document self-contained: a reader should not need the chat transcript.

## Examples

- "把我们讨论的这个方向写成 PRD" → intake gate passes (direction chosen in conversation) →
  Lean PRD inline, offer `gh-create-issue` decomposition.
- "Write a PRD for the notification-preferences feature, research is in docs/research/" →
  read the linked research, Full PRD to `docs/prd/notification-preferences.md`.
- "写个 PRD 看看做哪个方向好" → fails the intake gate (no chosen direction) → route to
  `brainstorming`, do not draft.

## Caveats

- This skill structures and sharpens content the discovery process produced; it does not
  replace discovery. A well-formatted PRD over a weak problem statement is still a weak PRD.
- Do not fabricate baselines, user quotes, or market numbers. Missing evidence goes in Open
  Questions, not in confident prose.
- PRD approval is a human decision. The skill drafts and self-reviews; it does not mark its
  own output Approved.

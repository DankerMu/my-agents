---
name: brainstorming
description: >
  Turn ambiguous ideas or competing directions into one approved decision before planning or implementation. Invoke explicitly, or via routing from other skills when direction is still unchosen.
invocation_posture: manual-first
version: 0.3.0
---

# Brainstorming

Transform ideas into validated decisions through structured dialogue before committing to a direction. Brainstorming answers **WHAT** to do and **WHY** — not HOW; leave execution details to planning and implementation. Applies equally to software features, business strategies, product designs, market approaches, and any domain requiring structured thinking before action.

## Hard Gate

Do NOT write code, scaffold files, create deliverables, or take any action toward execution until the user has explicitly approved a direction. This applies regardless of perceived simplicity — "simple" problems are exactly where unexamined assumptions waste the most effort. The brainstorm can be brief, but it must happen and the direction must be approved.

## When Not To Use

- Clarification only (missing facts, contradictions, acceptance criteria) → `clarify`
- Review of existing work (code, documents, diffs) → `review`
- Detailed execution planning after the direction is decided → `implementation-planning` for complex work, or a lighter planning flow
- Straightforward execution — the user knows what they want and just wants to start
- Architecture direction, technology selection, or hard-to-reverse structural bets → `future-aware-architecture` (it cedes open-ended ideation back to this skill)

If the request begins with ambiguity but quickly resolves into a concrete chosen direction, finish the brainstorm cleanly and hand off instead of dragging the user through more ideation.

## Scope Classification

Assess scope before starting; announce the selected scope and your reasoning. If unclear, ask one targeted question; when in doubt, start Standard and escalate if complexity emerges.

| Scope | Signals | Process Weight | Output |
|-------|---------|----------------|--------|
| **Quick** | Small, well-bounded, low ambiguity. Config change, minor feature, clear tactical question. | 1–2 messages. Batch questions. | Approved direction in chat. No document. |
| **Standard** | Normal feature, bounded problem, moderate ambiguity. | Full flow. One question at a time. 2–3 approaches. | Decision Brief. |
| **Deep** | Cross-cutting, strategic, high ambiguity, novel territory; multiple subsystems, stakeholders, or long-term consequences. | Full flow + thinking moves + domain frameworks + decision log + review gate. | Design Decision Record (saved to file). |

## Process

Phase-by-phase procedures, interaction styles, the five thinking moves, and domain-framework routing live in [references/process-playbook.md](references/process-playbook.md); output templates in [references/output-templates.md](references/output-templates.md). The skeleton:

1. **Phase 0 — Orient**: resume check; context scan proportional to scope; announce scope. Multi-subsystem requests get decomposed first.
2. **Phase 1 — Understand**: purpose, constraints, success criteria, non-goals; surface unvolunteered constraint dimensions; mark defaults as assumptions. **Understanding Lock** (Standard/Deep): present summary + assumptions + open questions, and do not proceed until the user explicitly confirms.
3. **Phase 2 — Explore**: challenge the framing first (right problem? do-nothing cost? simpler framing?), then propose 2–3 approaches with trade-offs, leading with a recommendation. Apply thinking moves (invert, analogize, pre-mortem, second-order effects, temporal lens) proportional to scope; offer domain frameworks from [references/thinking-frameworks.md](references/thinking-frameworks.md) when the domain warrants. Work within existing context and patterns.
4. **Phase 3 — Converge**: present the chosen direction in digestible sections with per-section confirmation; bounded revision rounds (Quick 1, Standard 2 per section). Deep additionally keeps a Decision Log and designs for decomposability.
5. **Phase 4 — Capture**: output per scope — nothing for Quick, Decision Brief for Standard, Design Decision Record for Deep (templates in the reference).
6. **Phase 5 — Handoff**: offer planning / implementation / continue refining / park; execute the user's choice without ceremony.

## Exit Criteria

Before handoff, explicitly verify ALL of the following (state them in the conversation for Deep scope):

- [ ] Understanding of the problem is confirmed (Understanding Lock for Standard/Deep)
- [ ] At least one approach is explicitly approved by the user
- [ ] Key assumptions are documented (Standard/Deep)
- [ ] The user has chosen a next step from the handoff options

If any criterion is unmet, continue refining. Do not silently proceed to execution.

## Principles

- **Proportional ceremony** — match process weight to task weight; every piece of process must earn its place.
- **Decisions over documents** — the value is clarity of thought, not volume of artifacts.
- **Thinking partner, not interviewer** — bring ideas, challenge assumptions boldly, say directly when the user's framing has a flaw; the simpler approach may be 80% as good at 20% of the cost.
- **Ground with numbers** — back-of-envelope calculations make abstract problems concrete; rough math beats no math.
- **Bias toward action** — when two options are close, pick one and go; classify decisions as reversible (move fast) or irreversible (deliberate carefully).
- **Solve the confirmed problem** — no speculative abstractions; validate the core before building for edge cases.
- **Assumptions must be explicit** — silent assumptions are the primary source of wasted work.
- **One question at a time** (Standard/Deep) — each question should build on the last answer; batching is fine for Quick.

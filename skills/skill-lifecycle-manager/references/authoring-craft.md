# Authoring Craft: The Predictability Vocabulary

Writing-quality bar for Phase 3 (Create Or Update) and diagnostic vocabulary for Phase 8 (Audit).
Condensed and adapted from `mattpocock/skills` `writing-great-skills` + `GLOSSARY.md` (v1.1.0).

A skill exists to wrangle determinism out of a stochastic system. The root virtue is
**predictability** — the agent taking the same *process* every run, not producing the same
output. Every rule below serves it.

## The two loads

Every skill spends one of two budgets; posture (see
[invocation-posture.md](invocation-posture.md)) is a load decision, not a taste decision:

- **Context load** — tokens always in the window. `auto-first` / `hybrid` skills pay it: their
  description rides in context every turn, so it earns the hardest pruning in the package.
- **Cognitive load** — what the human must remember. `manual-first` skills pay it: zero context
  cost, but the user is the index. When manual skills multiply past what a user can recall, the
  cure is a router skill that names them and when to reach for each — not more descriptions.

## Information hierarchy

Skill content is **steps** (ordered actions) or **reference** (rules consulted on demand), and
each piece sits on a ladder ranked by how immediately the agent needs it:

1. **In-skill step** — each ends on a *checkable* completion criterion ("every modified module
   accounted for", not "produce a change list"). A vague criterion invites premature completion.
2. **In-skill reference** — a flat peer-set of rules in `SKILL.md` is fine; not every skill needs
   steps.
3. **External reference** — `references/*.md` behind a context pointer, loaded only when the
   pointer fires. The pointer's *wording* decides whether the agent actually reaches it.

**Progressive disclosure** is the move down the ladder. The cleanest test is branching: inline
what every run needs; push behind a pointer what only some branches reach. **Co-location** decides
what sits together once placed: one concept's definition, rules, and caveats under one heading,
not scattered.

## Leading words

A **leading word** is a compact concept already in the model's pretraining that the agent thinks
with while running the skill — *tracer bullet*, *seam*, *fog of war*, *relentless*. It anchors
execution in the body and invocation in the description, buying a whole region of behaviour for
one token. Hunt for collapse opportunities: a triad restated at three sites, a sentence gesturing
at one idea — each wants to become a single pretrained word.

Description rules that follow: front-load the leading word; one trigger per branch (synonyms
renaming the same branch are duplication); cut identity the body already states.

## Pruning discipline

- **Single source of truth**: one authoritative place per meaning; changing behaviour is a
  one-place edit.
- **Relevance**: every line must still bear on what the skill does.
- **No-op test, per sentence**: does this sentence change behaviour versus the agent's default?
  When a sentence fails, delete the whole sentence — don't trim words from it. "Be thorough" is a
  no-op; *relentless* might not be.

## Failure modes

Use these as audit vocabulary (Phase 8) and as a pre-release sweep (Phase 3):

- **Premature completion** — a step ends before it's genuinely done. Cure in order: sharpen the
  completion criterion first (cheap, local); split the sequence only if the criterion is
  irreducibly fuzzy *and* the rush is observed.
- **Duplication** — the same meaning in more than one place; costs tokens and inflates the
  meaning's apparent rank on the ladder.
- **Sediment** — stale layers that settle because adding feels safe and removing feels risky. The
  default fate of any skill without a pruning pass per release.
- **Sprawl** — every line live and unique, but the skill is simply too long. Cure is the ladder:
  disclose reference outward, split by branch or sequence.
- **No-op** — a line the model already obeys; paying load to say nothing.
- **Negation** — steering by prohibition backfires: naming the forbidden behaviour drags it into
  context and makes it *more* available (*don't think of an elephant*). Prompt the positive; keep
  a prohibition only as a hard guardrail you can't phrase positively, and pair it with the
  do-instead.
- **Negative space** — what a skill *omits* still steers: every decision it declines is delegated
  to the model's priors, not left neutral. Read a draft for its silences and decide each omission
  deliberately — fill it, or leave it open as a real branch.

## Phase 3 exit sweep

Before Phase 4 validation, pass the draft through: completion criteria checkable → no-op test per
sentence → duplication/sediment hunt → negation flipped to positives → silences read and decided.

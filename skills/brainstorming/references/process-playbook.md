# Process Playbook (phase-by-phase detail)

Full procedures for the phases outlined in SKILL.md. Read the phase you are entering.

## Question handling

Use the platform's native user-input mechanism when one is available and appropriate for the current environment. If the surface does not expose a structured question tool, ask concise questions directly in chat and wait for the user's reply. Do not make the workflow depend on one specific tool name.

## Phase 0: Orient

**0.1 Resume check** — If the user references an existing brainstorm, or a recent decision record exists in the project: read it, then confirm: "Found an existing brainstorm for [topic]. Continue from here, or start fresh?" If resuming, summarize current state and continue from existing decisions.

**0.2 Context scan** — depth matches scope, sources match domain:
- **Quick**: glance at the most relevant context. Move on.
- **Standard**: scan what already exists — for code projects: structure, patterns, recent commits, instruction files; for business/strategy: existing plans, market data, prior decisions, competitive context.
- **Deep**: thorough scan of all relevant context. Identify what already exists vs. what is proposed. Surface constraints that appear implicit but unconfirmed.

**0.3 Scope announcement** — State the scope you selected and why. If the request describes multiple independent subsystems, flag this immediately — help the user decompose into sub-projects before brainstorming the first one.

## Phase 1: Understand

**Interaction style by scope:**
- **Quick**: Batch 2–3 questions in one message. Prefer multiple choice. If the request is already clear, skip straight to Phase 2.
- **Standard**: One question at a time. Prefer single-select multiple choice. Open-ended when the design space is genuinely unconstrained.
- **Deep**: One question at a time. Explore thoroughly. Use multi-select only for compatible sets (goals, constraints) that can coexist.

**What to understand:**
- **Purpose** — What problem does this solve? For whom? What outcome actually matters?
- **Constraints** — Technical, time, resource, organizational limitations
- **Success criteria** — How will we know this worked?
- **Non-goals** — What are we explicitly NOT doing? (Prevents scope creep later)

**Constraints beyond the core ask** (Standard and Deep) — surface dimensions the user might not volunteer:
- **Technical**: performance, scale, security, reliability, maintenance burden
- **Business**: budget, timeline, team capacity, regulatory/legal, competitive pressure
- **Product**: target users, success metrics, adoption barriers, maintenance expectations
- **Strategy**: risk tolerance, reversibility, organizational alignment, time horizon

If the user is unsure, propose reasonable defaults and clearly mark them as **assumptions**.

**Understanding Lock** (Standard and Deep) — before proposing any design, present: a 3–5 bullet summary of what is being built and why; assumptions listed explicitly; open questions. Ask: *"Does this accurately capture your intent? Please confirm or correct before we move to design."* Do NOT proceed until explicit confirmation.

## Phase 2: Explore

**2.1 Challenge the framing** (all scopes, depth proportional): Is this the right problem, or a proxy for a more important one? What happens if we do nothing? Are we duplicating something that already exists? Is there a simpler framing that delivers the same value? For Quick scope this can be a single sentence; for Deep, spend real time here — reframing often matters more than choosing between solutions. Ground the problem with rough quantitative estimates when possible.

**2.2 Propose approaches** — Present 2–3 viable approaches with trade-offs. Lead with your recommendation and explain why. For each: brief description (a short paragraph), pros and cons, key risks or unknowns, when it's best suited. If one approach is clearly best, state the recommendation directly — don't manufacture fake options. Eliminate speculative complexity: solve the confirmed problem, not hypothetical future ones.

**2.3 Thinking Moves** (Standard: pick 1–2 naturally; Deep: apply all five). Domain-agnostic cognitive tools — practice them naturally, the goal is better thinking, not process theater:

- **Invert** — What if we solved the opposite problem? Removed this constraint entirely? What would make the problem disappear? Surfaces hidden assumptions; often reveals radically simpler solutions.
- **Analogize** — What other system, domain, or product has solved a structurally similar problem? The best answers are non-obvious transfers — import the mechanism, not the surface similarity.
- **Pre-mortem** — Imagine it is one year from now and this decision has completely failed. What caused the failure? Retrieving causes of a known outcome produces a more comprehensive risk list than "what might go wrong". Empirically one of the strongest debiasing techniques.
- **Second-order effects** — What happens after the first consequence? A pricing change affects not just revenue but customer perception, competitive response, sales behavior, support volume. Trace at least two levels before committing.
- **Temporal lens** — How does this decision look in 1 month vs. 1 year vs. 5 years? Short-term and long-term optimal often conflict; name the tension explicitly.

**2.4 Domain frameworks** (Deep scope, optional for Standard) — When a brainstorm enters a recognized domain, suggest 1–2 relevant frameworks from `thinking-frameworks.md` and offer to apply them; don't force them. Quick domain detection:
- Business model / pricing / revenue → Business Model Canvas, First Principles on cost structure
- Market entry / competition → Porter's Five Forces lens, Wardley Map evolution check
- Product design / user needs → Jobs-to-be-Done, Desirability/Feasibility/Viability check
- Technical architecture → trade-off analysis, constraint-driven design
- Strategy / major decision → Type 1/Type 2 classification, Pre-mortem, scenario planning
- Research direction → Hypothesis-Led approach, Abstraction Ladder

**2.5 Working within existing context** — Explore what already exists before proposing changes; follow existing patterns. Where existing work has problems that affect the current goal, include targeted improvements in the design. Don't propose unrelated improvements.

## Phase 3: Converge

**Quick**: State the recommended direction. Get approval. Move on. Max 1 revision round.

**Standard**: Present the chosen direction in digestible sections (a few sentences if straightforward, up to 200–300 words if nuanced). After each section, check: *"Does this look right so far?"* Cover what is relevant to the domain: architecture and data flow for technical work; value chain and go-to-market for business; user experience and success metrics for product. Max 2 revision rounds per section — if still misaligned, ask the user to state what they want directly. A good-enough direction chosen quickly beats a perfect one chosen slowly.

**Deep**: Same incremental presentation, plus:
- **Design for clarity**: break the design into parts that each have one clear purpose and can be understood independently. Complexity that cannot be decomposed cannot be managed.
- **Maintain a Decision Log**: for each significant decision, record what was decided, alternatives considered, and why. Feeds the final Design Decision Record.

## Phase 5: Handoff

Present next-step options appropriate to context (use the platform's question tool when available); present only those that apply:
- **Proceed to planning** — create a detailed implementation plan
- **Proceed to implementation** — only when scope is Quick or Standard with clear requirements and no meaningful open questions
- **Continue refining** — dig deeper into unresolved areas or revisit decisions
- **Park for later** — save current state and return when ready

Execute the user's choice. Do not add ceremony to the handoff.

## Evaluating changes to this skill

When changing trigger wording or process shape, evaluate with a small prompt mix before calling the update complete:
- **Should trigger**: explicit ideation asks ("Let's brainstorm the rollout options", "Help me think through whether we should build A or B first")
- **Should not trigger**: direct execution asks ("Implement this API change", "Write the migration plan for the chosen design")
- **Adjacent handoff cases**: requests belonging to neighboring skills ("Clarify the missing requirements", "Review this draft", "Break the approved direction into tasks")

Healthy only if the skill stays quiet on clarification, review, planning, and straightforward execution prompts while remaining helpful on explicit direction-setting requests.

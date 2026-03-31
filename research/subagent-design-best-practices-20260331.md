# Subagent Design Best Practices: Official Guidance & Community Patterns

> Research date: 2026-03-31 | Depth: Standard | Sources: 25+ official and first-party sources
> Scope: Instruction design, creation gates, context isolation, architectural value, community patterns

## Executive Summary

Official documentation from Anthropic, OpenAI, and major agent frameworks converges on three principles: (1) start with a single agent and split only when evaluation shows degradation; (2) keep instructions concise, focused, and opinionated — one agent = one job; (3) the primary architectural value of subagents is context isolation, not behavioral specialization. Quantitative thresholds exist but are sparse: Anthropic recommends CLAUDE.md under 200 lines and SKILL.md bodies under 500 lines; OpenAI Codex hard-caps AGENTS.md at 32 KiB; community consensus suggests agent system prompts over ~1000 words lose effectiveness, and spawning a subagent costs ~2-3K tokens overhead before useful work begins. The strongest anti-pattern across all sources is premature multi-agent decomposition — the overhead of coordination, error amplification, and token waste outweighs any benefit unless tasks are genuinely parallel, context-heavy, or require model/permission specialization.

---

## 1. Instruction Length and Complexity Guidance

### 1.1 Claude Code — Official

**CLAUDE.md files:**
- "Keep it concise. For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it. Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" [1]
- "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost." [1]
- **Quantitative target**: Official docs now recommend keeping CLAUDE.md "under 200 lines" with reference material moved to skills. [10]
- The features overview recommends "Keep CLAUDE.md under ~500 lines" as an absolute ceiling, with the 200-line mark as the working target. [10]

**Skills (SKILL.md):**
- "Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds this, split it into separate files using progressive disclosure patterns." [8]
- "The context window is a public good. Your Skill shares the context window with everything else Claude needs to know." [8]
- "Default assumption: Claude is already very smart. Only add context Claude doesn't already have." [8]
- Skill descriptions: max 1024 characters, must include what-it-does AND when-to-use. [8]

**Subagent system prompts:**
- No official line count, but the agent creation system prompt emphasizes: "Balance comprehensiveness with clarity — every instruction should add value." [4]
- Subagents receive only their own system prompt (plus basic environment details), NOT the full Claude Code system prompt. [3]

**Prompting best practices (Claude 4.6):**
- "Claude Opus 4.5 and Claude Opus 4.6 are also more responsive to the system prompt than previous models. If your prompts were designed to reduce undertriggering on tools or skills, these models may now overtrigger. The fix is to dial back any aggressive language." [7]
- No explicit token or word count ceiling for system prompts, but the guidance is clear: specificity over length, and remove over-prompting. [7]

### 1.2 OpenAI Codex — Official

**AGENTS.md files:**
- Hard limit: `project_doc_max_bytes` defaults to **32 KiB**. Files are silently truncated beyond this. [6][16]
- "A short, accurate AGENTS.md is more useful than a long file full of vague rules." [9]
- Discovery walks from repo root to working directory; files concatenate root-down. [6]

**Custom agent instructions (`developer_instructions`):**
- Example from official docs: "Review code like an owner. Prioritize correctness, security, behavior regressions, and missing test coverage." — a single sentence. [2]
- "The best custom agents are narrow and opinionated. Give each one clear job, a tool surface that matches that job, and instructions that keep it from drifting into adjacent work." [2]

### 1.3 Community & Cross-Platform

- HumanLayer analysis: "Frontier thinking LLMs can follow ~150-200 instructions with reasonable consistency." Smaller models show exponential decay; larger models show linear decay as instruction count increases. [11]
- HumanLayer's own root CLAUDE.md is under 60 lines. [11]
- Community consensus: "< 300 lines is best, and shorter is even better" for CLAUDE.md. [11]

### 1.4 Synthesis: Instruction Length Thresholds

| Artifact | Platform | Recommended Ceiling | Source Type |
|---|---|---|---|
| CLAUDE.md | Claude Code | ~200 lines (500 absolute max) | Official [1][10] |
| SKILL.md body | Claude Code | 500 lines | Official [8] |
| Skill description | Claude Code | 1024 characters | Official [8] |
| AGENTS.md | Codex | 32 KiB (configurable) | Official [6] |
| Agent system prompt | Claude Code | No official limit; "every instruction should add value" | Official [4] |
| Agent `developer_instructions` | Codex | No official limit; examples are 1-2 sentences | Official [2] |
| Total instruction count | Cross-platform | ~150-200 instructions before degradation | Community [11] |

---

## 2. When to Create vs Not Create a Subagent

### 2.1 Official Decision Criteria

**Claude Code official guidance** provides the clearest decision framework [3]:

Use **main conversation** when:
- The task needs frequent back-and-forth or iterative refinement
- Multiple phases share significant context (planning -> implementation -> testing)
- You are making a quick, targeted change
- Latency matters (subagents start fresh and may need time to gather context)

Use **subagents** when:
- The task produces verbose output you do not need in your main context
- You want to enforce specific tool restrictions or permissions
- The work is self-contained and can return a summary

Use **skills instead** when you want reusable prompts or workflows that run in the main conversation context rather than isolated subagent context. [3]

**Claude 4.6 specific caution**: "Claude Opus 4.6 has a strong predilection for subagents and may spawn them in situations where a simpler, direct approach would suffice. For example, the model may spawn subagents for code exploration when a direct grep call is faster and sufficient." [7]

**OpenAI Codex**: "Codex only spawns a new agent when you explicitly ask it to do so." No automatic delegation. [2]

**OpenAI Practical Guide**: "Start with a single agent and evolve to multi-agent systems only when needed... Teams usually do better by starting with one agent, adding tools, and splitting only when evaluations show the single agent struggling." [13]

### 2.2 Quantitative Spawn Decision Framework

From community analysis (single-source, cross-referenced with official patterns) [14]:

| Criterion | Inline | Spawn |
|---|---|---|
| Task token cost | < 500 tokens | > 50K tokens |
| Task duration | < 30 seconds | > 2-5 minutes |
| Spawn overhead | N/A | ~2-3K tokens before useful work |
| Model specialization needed | No | Yes (different model/effort) |
| Isolation benefit | None | High (dangerous/messy/state-heavy) |
| Restart tolerance | N/A | Task survives interruption |

**Break-even rule**: "If your task takes 500 tokens inline, spawning makes no sense, but if your task takes 50K tokens and benefits from a different model, spawning is a bargain." [14]

### 2.3 OpenAI Tool-Count Threshold

From the OpenAI practical guide: Split into multiple agents when a single agent has **>15 tools** and struggles to select the right one. Also split when prompt logic resembles "spaghetti code" (nested if/then/else), or when the agent has conflicting objectives. [13][15]

### 2.4 Google Cloud Decision Criteria

Google's agentic architecture guide identifies three dominant effects in multi-agent systems [18]:
- **Tool-coordination trade-off**: Tasks requiring many tools perform worse with multi-agent overhead
- **Capability saturation**: Adding agents yields diminishing returns when single-agent baseline exceeds a threshold
- **Topology-dependent error amplification**: Centralized orchestration reduces error propagation

---

## 3. Context Passing and Isolation

### 3.1 Claude Code — Context Isolation Model

**What subagents receive** [3][10]:
- Their own system prompt (NOT the full Claude Code system prompt)
- Basic environment details (working directory)
- Any skills listed in their `skills:` field (fully preloaded, not on-demand)
- CLAUDE.md and git status (inherited from parent)
- Whatever context the lead agent passes in the prompt

**What subagents do NOT receive** [3][10]:
- Parent conversation history
- Skills invoked during the parent session
- Other subagents' results (unless explicitly chained)

**Result compression**: Subagents explore, read files, and reason in their own context window, then return only a summary to the parent. "The subagent explores the codebase, reads relevant files, and reports back with findings, all without cluttering your main conversation." [1]

**Nesting prohibition**: "Subagents cannot spawn other subagents." If recursive delegation is needed, chain from the main conversation. [3]

**Auto-compaction**: Subagents support auto-compaction at ~95% capacity (configurable via `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`). [3]

**Resumption**: Each subagent invocation creates a new instance with fresh context by default, but can be resumed with full conversation history via `SendMessage`. Transcripts persist at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`. [3]

### 3.2 OpenAI Codex — Context Model

**Agent isolation**: Each custom agent gets its own session. Optional fields (`model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`) inherit from parent when omitted. [2]

**Nesting control**: `agents.max_depth` defaults to 1. "Increasing max_depth can turn broad delegation instructions into repeated fan-out, which increases token usage, latency, and local resource consumption." [2]

**Concurrency control**: `agents.max_threads` defaults to 6 concurrent open agent threads. [2]

### 3.3 LangChain — Context Model

- Each subagent invocation operates in a "clean context window, preventing context bloat in the main conversation." [5]
- Supervisor maintains conversation context across turns, dynamically routing tasks. [5]
- Output strategy choice: "final message only" vs "enriched state returns." [5]

---

## 4. Architectural Value of Subagents

### 4.1 Context Window Preservation (Primary Value)

All official sources agree this is the number one benefit:

- **Claude Code**: "Since context is your fundamental constraint, subagents are one of the most powerful tools available." [1]
- **Claude Code best practices**: "One of the most effective uses for subagents is isolating operations that produce large amounts of output. Running tests, fetching documentation, or processing log files can consume significant context." [3]

### 4.2 Permission and Tool Scoping

- **Claude Code**: Each subagent can restrict tools via `tools` (allowlist) or `disallowedTools` (denylist). Permission modes (`default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`) scope permissions per-agent. [3]
- **Codex**: Custom agents specify their own `sandbox_mode` and tool surface. [2]
- Both platforms agree: "Grant only necessary permissions for security and focus." [2][3]

### 4.3 Model and Cost Optimization

- **Claude Code**: Use `CLAUDE_CODE_SUBAGENT_MODEL` or per-agent `model` field. Common pattern: "run your main session on Opus for complex reasoning while sub-agents handle focused tasks on Sonnet." [1][3]
- **Codex**: Per-agent `model` and `model_reasoning_effort` fields enable tiered model selection. PR review example uses different models for explorer (spark), reviewer (gpt-5.4), and docs researcher (mini). [2]

### 4.4 Parallelism

- **Claude Code**: "For independent investigations, spawn multiple subagents to work simultaneously." Works best when research paths do not depend on each other. [3]
- Warning: "When subagents complete, their results return to your main conversation. Running many subagents that each return detailed results can consume significant context." [3]
- **Codex**: Batch processing via `spawn_agents_on_csv` for one-worker-per-row parallelism. [2]

### 4.5 Worktree Isolation (Claude Code Specific)

- Set `isolation: worktree` to run the subagent in a temporary git worktree, giving it an isolated copy of the repository. Auto-cleaned if no changes made. [3]

### 4.6 Persistent Memory (Claude Code Specific)

- `memory: user|project|local` gives subagents persistent directories that survive across conversations. First 200 lines / 25KB of MEMORY.md injected into the subagent's context. [3]

---

## 5. Community Framework Best Practices

### 5.1 OpenAI Agents SDK

**Orchestration patterns** [17]:
- **Agents as Tools**: Manager calls specialists via `Agent.as_tool()`. Best when a single agent owns the final answer and combines outputs.
- **Handoffs**: Triage routes conversation to a specialist who becomes the active agent. Best when routing is the core workflow and specialists should own interactions.

**Key distinction**: "Use agents-as-tools for bounded subtasks where specialists should not control user-facing responses. Use handoffs when routing itself is workflow-critical." [17]

**Five tactics for LLM orchestration**: (1) Prompt investment with clear tool definitions, (2) Monitoring and iteration, (3) Agent introspection / self-critique, (4) Specialization over generalism, (5) Evaluation-driven improvement. [17]

### 5.2 CrewAI

**The 80/20 Rule**: "80% of your effort should go into designing tasks, and only 20% into defining agents. Well-designed tasks elevate even simple agents, while poorly designed tasks undermine excellent agents." [19]

**Agent definition patterns** [19]:
- Roles: 1-2 sentences with domain specialization
- Goals: 1-2 sentences emphasizing outcomes
- Backstories: 2-4 sentences establishing expertise and working style

**Anti-patterns**: Vague instructions, "god tasks" attempting multiple complex operations, misaligned descriptions, generic agent definitions, unnecessary hierarchical structures when sequential workflows suffice. [19]

### 5.3 AutoGen / Microsoft Agent Framework

**Instruction design** (community-sourced) [20]:
- "Negative constraints are often more powerful than positive instructions in preventing hallucinations."
- "Define roles based on Separation of Concerns: specialists like 'Fact Checker' have narrow scope that reduces cognitive load on the LLM."

### 5.4 Google Cloud Agentic Patterns

Eight patterns with decision criteria [18]:
1. **Sequential**: Highly structured, repeatable processes with fixed order
2. **Parallel**: Independent sub-tasks that can run concurrently
3. **Loop**: Iterative refinement requiring self-correction
4. **Dispatcher**: Central agent analyzes intent and routes to specialists
5. **Hierarchical**: Multi-level decomposition for open-ended problems
6. **Swarm**: Ambiguous problems benefiting from debate and convergence

**Key finding**: "The best coordination strategy is task-dependent: financial reasoning benefits from centralized orchestration, while web navigation does better with a decentralized strategy." [18]

---

## 6. Consolidated Recommendations

### 6.1 Decision Gate: When to Create a Subagent

Create a subagent when ALL of the following are true:
1. **Context isolation benefit**: The task reads many files, produces verbose output, or would pollute the main context
2. **Self-contained**: The work can return a useful summary without requiring iterative back-and-forth
3. **Overhead justified**: Expected task complexity exceeds ~2-3K token spawn overhead (roughly >500 tokens of inline work)

Do NOT create a subagent when:
- A single tool call (grep, read) accomplishes the task
- The task requires iterative refinement with the user
- Multiple phases share significant context
- Latency is critical (subagents start cold)

### 6.2 Instruction Design Rules

1. **One agent = one job**: "Narrow and opinionated" (Codex) / "Design focused subagents: each subagent should excel at one specific task" (Claude Code)
2. **Concise over comprehensive**: Every instruction must justify its token cost. Remove anything Claude already knows.
3. **Description is king**: The description field is the primary routing signal. Include what-it-does AND when-to-use-it with trigger examples.
4. **Limit tools explicitly**: Default inheritance grants everything. Always set `tools` or `disallowedTools`.
5. **Progressive disclosure**: Put overview in the system prompt; link to detailed references that load on demand.
6. **Test with target model**: What works for Opus may over-explain for Haiku. Match instruction density to model capability.

### 6.3 Architecture Patterns

| Pattern | When to Use | Platform Support |
|---|---|---|
| Single agent + tools | Default starting point; most tasks | Both |
| Parallel subagents | Independent research, disjoint code reviews | Both |
| Sequential chaining | Multi-step workflows with dependencies | Both |
| Writer/Reviewer split | Code quality via fresh-context review | Claude Code (multi-session) |
| Tiered model delegation | Cost optimization: Opus lead, Sonnet workers, Haiku explorers | Both |
| Worktree isolation | Subagents that may modify files in parallel | Claude Code only |

---

## 7. Gaps and Limitations

1. **No official token budgets for agent system prompts**: Neither Claude Code nor Codex provides a numeric ceiling for subagent instruction length. The ~1000 word threshold comes from community observation, not official docs.
2. **Spawn cost data is community-sourced**: The 2-3K token overhead and 500-token inline threshold come from a single community article [14], not official benchmarks.
3. **Codex subagent documentation is newer**: Codex subagent support launched in March 2026 and the documentation is still evolving. Some patterns may change.
4. **AutoGen guidance is scattered**: Microsoft Agent Framework (AutoGen + Semantic Kernel merge) is in public preview with a Q1 2026 GA target. Best practices are fragmented across blog posts.
5. **No controlled studies on instruction length vs performance**: The HumanLayer "150-200 instructions" finding is an observation, not a peer-reviewed benchmark.
6. **Claude 4.6 subagent overuse**: Official docs explicitly warn that Opus 4.6 "may spawn subagents in situations where a simpler, direct approach would suffice" — this is a known model-level behavior, not a configuration issue.

---

## Sources

1. [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) — Anthropic official docs
2. [Subagents — Codex](https://developers.openai.com/codex/subagents) — OpenAI official docs
3. [Create Custom Subagents — Claude Code](https://code.claude.com/docs/en/sub-agents) — Anthropic official docs
4. [Agent Creation System Prompt — Claude Code](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/agent-development/references/agent-creation-system-prompt.md) — Anthropic GitHub
5. [Subagents — LangChain](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents) — LangChain official docs
6. [Custom Instructions with AGENTS.md — Codex](https://developers.openai.com/codex/guides/agents-md) — OpenAI official docs
7. [Prompting Best Practices — Claude 4.6](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices) — Anthropic official docs
8. [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Anthropic official docs
9. [Best Practices — Codex](https://developers.openai.com/codex/learn/best-practices) — OpenAI official docs
10. [Extend Claude Code — Features Overview](https://code.claude.com/docs/en/features-overview) — Anthropic official docs
11. [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — HumanLayer (community, well-sourced)
12. [Using CLAUDE.md Files](https://claude.com/blog/using-claude-md-files) — Anthropic blog
13. [A Practical Guide to Building Agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) — OpenAI official guide
14. [AI Agent Subagent Orchestration: When to Spawn vs When to Do It Yourself](https://dev.to/bobrenze/ai-agent-subagent-orchestration-when-to-spawn-vs-when-to-do-it-yourself-4opg) — Community (single-source for quantitative thresholds)
15. [OpenAI Practical Guide Summary](https://medium.com/data-science-in-your-pocket/openais-practical-guide-to-building-ai-agents-summary-3e3df468aeb3) — Summary of [13]
16. [AGENTS.md Truncation Issue #7138](https://github.com/openai/codex/issues/7138) — OpenAI Codex GitHub
17. [Multi-Agent Orchestration — OpenAI Agents SDK](https://openai.github.io/openai-agents-python/multi_agent/) — OpenAI official docs
18. [Choose a Design Pattern for Agentic AI — Google Cloud](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system) — Google official docs
19. [Crafting Effective Agents — CrewAI](https://docs.crewai.com/en/guides/agents/crafting-effective-agents) — CrewAI official docs
20. [AutoGen — Microsoft Research](https://www.microsoft.com/en-us/research/project/autogen/) — Microsoft official
21. [Claude Code Sub-Agents: Parallel vs Sequential Patterns](https://claudefa.st/blog/guide/agents/sub-agent-best-practices) — Community
22. [Codex Subagent Support Issue #2604](https://github.com/openai/codex/issues/2604) — OpenAI Codex GitHub
23. [Agent Design Patterns](https://rlancemartin.github.io/2026/01/09/agent_design/) — LangChain community (Lance Martin)
24. [Google's Eight Multi-Agent Design Patterns](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/) — InfoQ coverage of Google research
25. [Orchestrator and Subagent Patterns — Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/multi-agent-orchestrator-sub-agent) — Microsoft official docs

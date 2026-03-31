---
name: agent-lifecycle-manager
description: >
  Manage the lifecycle of sub-agents: create or update agent packages, validate
  cross-surface agent contracts, evaluate routing behavior, tighten invocation
  boundaries, tune Codex runtime defaults, install or publish agents, or audit
  an agent library. Use only when the request is explicitly about agents or
  agent libraries, not for ordinary coding, implementation, or general project
  planning.
version: 0.5.0
---

# Agent Lifecycle Manager

Manage agent packages (`agent.json`, `claude-code.md`, `codex.toml`, `CHANGELOG.md`) as a lifecycle, not isolated file edits. This skill routes the request to the right stage, runs it, and closes the loop.

## Route First

Classify the request before doing anything:

| Stage | When | Key action |
| --- | --- | --- |
| **Create / Update** | New agent or material revision | Write the 3 authored files with minimal instructions |
| **Validate** | After any change | `npm test` + `quick_validate_agent.py` |
| **Evaluate** | Test on realistic prompts | `seed_eval_workspace.py` + `run_surface_eval.py` |
| **Optimize** | Under/over-triggering | Tighten description wording |
| **Install** | Activate on a surface | `npm run install-agent` |
| **Audit** | Library health check | `audit_agent_inventory.py` |

Summarize the chosen route in one sentence before proceeding.

## Creation Gate

Before creating a new agent, answer these questions honestly. If most answers are "no", don't create it.

1. **Does a dedicated agent add value beyond inline execution?** Value can come from behavioral differences (the model wouldn't do this by default), context isolation (keeps the main agent's window clean), result compression (returns a summary instead of raw process), parallelism (can run alongside other agents), or permission narrowing (read-only scope). At least one must apply.
2. **Can you name the behavioral contract?** An agent needs to enforce something specific — an output format, a safety boundary, a collaboration protocol, a workflow the model wouldn't follow unprompted. If you can't articulate it, there's no agent here.
3. **Is there an existing agent that could be slightly adjusted instead?** Prefer tightening an existing agent over creating a new one with overlapping scope.
4. **Will this be spawned frequently enough to justify its existence?** One-off workflows don't need agents. Agents are for recurring patterns.
5. **Can you write the instructions concisely?** Official examples use 1-5 sentences. If you need 50+ lines, you're probably teaching the model things it already knows — strip to behavioral contract only, or split the scope.

If the agent passes the gate, proceed to Create / Update.

## Create / Update

Agent instructions should be **narrow and opinionated** — 5-8 lines of behavioral contract, not a teaching manual. The model already knows how to search, review, plan, and debug. Only specify:

- Role boundary (read-only? write? what scope?)
- Output contract (what to return, in what shape)
- Safety rails (what to never do)

Use `npm run new -- --agent <name>` for a fresh scaffold. Keep semantics aligned across `agent.json`, `claude-code.md`, and `codex.toml` — one routing boundary, one role, same instructions.

For Codex agents, set `sandbox_mode`, `model`, and `model_reasoning_effort` explicitly rather than inheriting from the parent session.

Read [platform-surfaces.md](references/platform-surfaces.md) for the authored file layout and install targets. Read [invocation-posture.md](references/invocation-posture.md) before writing or tuning descriptions.

## Validate

Run in order:

1. `npm run build`
2. `npm test`
3. `uv run python "$ALM_DIR/scripts/quick_validate_agent.py" agents/<name>`

The agent-specific validator checks cross-surface alignment, archetype-capability consistency, runtime defaults, and tools alignment. Fix structural issues before deeper evaluation.

When validating this skill package itself (not a target agent), use the canonical repo source only:

```
uv run python "$ALM_CANONICAL_DIR/scripts/quick_validate.py" "$ALM_CANONICAL_DIR"
uv run python "$ALM_CANONICAL_DIR/scripts/validate_eval_suite.py" "$ALM_EVAL_FILE"
```

## Evaluate

Use realistic prompts, not toy examples. Mix: `should-handle`, `should-stretch`, `should-not-handle`, `near-miss`.

Read [evaluation-loop.md](references/evaluation-loop.md) for the eval harness commands and benchmark setup.

## Optimize Invocation

Only when triggering is wrong. Draft `should-trigger` / `should-not-trigger` prompts, tighten descriptions, record before/after.

## Install

```
npm run install-agent -- <name> --platform claude|codex|all --scope project
```

Validate before installing. Confirm installed copies exist under `.claude/agents/` and/or `.codex/agents/`.

## Audit

```
uv run python "$ALM_DIR/scripts/audit_agent_inventory.py" --root agents
```

Read [audit-rubric.md](references/audit-rubric.md) for the 11-dimension rubric and scoring formula. Prioritize dangerous overreach and structural breakage before polish.

## Close

After any stage, report: what was done, what changed, what was validated vs not, and the next step if work remains.

## Script Paths

- **Runtime**: `ALM_DIR=skills/agent-lifecycle-manager` (canonical), `.agents/skills/agent-lifecycle-manager` (Codex), `.claude/skills/agent-lifecycle-manager` (Claude Code)
- **Self-validation**: always use `ALM_CANONICAL_DIR=skills/agent-lifecycle-manager` and `ALM_EVAL_FILE=skills/agent-lifecycle-manager/eval/eval-cases.json`

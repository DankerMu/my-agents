# Platform Surfaces

Use this reference when the user wants one agent package to work across more than one surface. The key distinction is not only "what files exist?" but "what part of the contract is canonical, what is platform-specific, and where do installed copies land?"

## Authored Package

In this repository, the canonical source of truth for an agent lives under:

```text
agents/<name>/
```

That package includes:

- `agent.json` for metadata and indexing
- `AGENT.md` for the single canonical 5-8 bullet behavior contract
- optional `references/operating-guide.md` for on-demand workflow detail and templates
- `claude-code.md` for Claude Code metadata plus the generated contract body
- `codex.toml` for Codex runtime metadata plus generated `developer_instructions`
- `CHANGELOG.md`

Run `npm run sync-agents` after changing `AGENT.md`. Do not hand-edit the generated behavior body in either platform file.

## Where Surfaces Differ

| Dimension | `agent.json` | Claude Code | Codex | Lifecycle implication |
| --- | --- | --- | --- | --- |
| Role | canonical metadata | generated from `AGENT.md` | generated from `AGENT.md` | edit behavior once and validate projection freshness |
| Discovery | catalog generation, schema validation | `claude-code.md` in repo, installed as `.claude/agents/<name>.md` | `codex.toml` in repo, installed as `.codex/agents/<name>.toml` | authoring and install are different stages |
| Schema expectations | JSON schema + repo validation | frontmatter + generated concise contract | TOML metadata + generated concise contract | extended guidance belongs in installable references |
| Trigger boundary | short description in metadata | frontmatter `description` | top-level `description` | keep the short boundary aligned |
| Runtime controls | none directly | tool list and Claude-specific fields | `sandbox_mode`, `model`, `model_reasoning_effort`, `web_search`, and other Codex-specific fields | platform details may differ, but not the agent's mission or permission budget |

## Practical Rule

Treat the agent package as one contract with platform-specific wrappers:

- `agent.json` says what the agent is in repository terms.
- `AGENT.md` is the only authored behavior contract.
- `claude-code.md` and `codex.toml` keep platform metadata while their behavior regions are generated.
- `references/operating-guide.md` preserves detailed procedures without paying their context cost on every invocation.

The installer copies references beside each installed platform definition and replaces `{{agent_references}}` with that concrete support path.

## Codex Runtime Defaults

For reusable repo agents, treat Codex runtime controls as part of the authored contract, not as an afterthought:

- `sandbox_mode` should reflect the agent's actual permission budget.
- `model_reasoning_effort` should usually be explicit when consistency matters across sessions.
- `web_search` should be enabled only when live web access is core to the job.
- `model` should match the role's latency and depth needs.

Inheritance still exists at runtime, so these fields are stable defaults rather than an absolute guarantee. The important design question is whether the reusable agent should behave predictably when invoked from different parent sessions. If yes, prefer explicit defaults.

## Install Surfaces

After authoring and validation, runtime installation copies land here:

- Claude Code: `.claude/agents/<name>.md`
- Codex: `.codex/agents/<name>.toml`

Use `npm run install-agent -- <name>` with `--platform` and `--scope` to manage those copies.

## When Surface Reasoning Matters

Reason about surfaces explicitly when:

- the user asks for Claude Code and Codex support together
- one surface needs stronger tool restrictions or different metadata
- one surface inherits runtime defaults that should really be explicit
- the descriptions or behavior have drifted
- install or publish steps are part of the request

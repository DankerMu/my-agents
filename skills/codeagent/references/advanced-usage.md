# Codeagent Advanced Usage

> Detail moved out of SKILL.md: backend selection, agent presets, skill injection, session resume, worktree isolation, and the parallel task DSL.

## Backend Selection Guide

**Codex** (default):

- Deep code understanding and complex logic implementation
- Large-scale refactoring with precise dependency tracking
- Algorithm optimization and performance tuning
- Example: "Analyze the call graph of @src/core and refactor the module dependency structure"

**Claude**:

- Quick feature implementation with clear requirements
- Technical documentation, API specs, README generation
- Professional prompt engineering (e.g., product requirements, design specs)
- Example: "Generate a comprehensive README for @package.json with installation, usage, and API docs"

**Gemini**:

- UI component scaffolding and layout prototyping
- Design system implementation with style consistency
- Interactive element generation with accessibility support

**OpenCode**:

- Lightweight tasks where a minimal feature set is enough

**OMP** (oh-my-pi):

- Multi-provider routing — mixing models from several providers across one orchestration
- The only backend where reasoning effort is expressed in the model string; see SKILL.md → OMP backend specifics before pinning a model

**Backend switching**: start with Codex for analysis, switch to Claude for documentation, then Gemini for UI implementation. In parallel mode, set `backend` per task so each stage runs on its strength.

## Agent Presets

An agent preset bundles backend, model, prompt, and tool control under one reusable name. Select with `--agent <name>`.

Sources, checked in order:

1. `~/.codeagent/models.json` → `agents.<name>` object
2. `~/.codeagent/agents/<name>.md` → the markdown file becomes the prompt

```json
{
  "agents": {
    "develop": {
      "backend": "codex",
      "model": "gpt-4.1",
      "prompt_file": "~/.codeagent/prompts/develop.md",
      "reasoning": "high",
      "yolo": true,
      "allowed_tools": ["Read", "Write", "Bash"],
      "disallowed_tools": ["WebFetch"]
    }
  }
}
```

Common presets:

| Agent | Purpose | Read-only |
|-------|---------|-----------|
| `code-explorer` | Trace code, map architecture, find patterns | Yes |
| `code-architect` | Design approaches, file plans, build sequences | Yes |
| `code-reviewer` | Review for bugs, simplicity, conventions | Yes |
| `develop` | Implement code, run tests, make changes | No |

Tool control is explicit enumeration only — no wildcards. Claude receives `--allowedTools`/`--disallowedTools`; OMP receives `--tools` (lowercase names) and ignores `disallowed_tools`.

## Skill Injection

Skills are read from `~/.claude/skills/<name>/SKILL.md`, stripped of YAML frontmatter, and injected into the task prompt.

When `--skills` is omitted, skills are auto-detected from the working directory:

| Detected files | Injected skills |
|---|---|
| `go.mod` / `go.sum` | `golang-base-practices` |
| `Cargo.toml` | `rust-best-practices` |
| `pyproject.toml` / `setup.py` / `requirements.txt` | `python-best-practices` |
| `package.json` | `vercel-react-best-practices`, `frontend-design` |
| `vue.config.js` / `vite.config.ts` / `nuxt.config.ts` | `vue-web-app` |

Override explicitly when auto-detection would inject the wrong set:

```bash
codeagent-wrapper --agent develop --skills golang-base-practices,frontend-design - . <<'EOF'
Implement full-stack feature...
EOF
```

Note: injection happens on the wrapper side. It does not apply to the OMP backend's own skill discovery, which is disabled (`--no-skills`).

## Resume Session

```bash
codeagent-wrapper --backend codex resume <session_id> - <<'EOF'
<follow-up task>
EOF

# With an agent preset
codeagent-wrapper --agent develop resume <session_id> - <<'EOF'
<follow-up task>
EOF
```

The `session_id` comes from the `SESSION_ID:` trailer or the `--output` JSON. Resuming carries the prior session's context — do not resume a session across a producer/judge boundary (e.g. reusing a session that produced review findings to verify those same findings).

## Worktree Isolation

```bash
codeagent-wrapper --agent develop --worktree - . <<'EOF'
Implement feature in isolation...
EOF
```

- Read-only agents (`code-explorer`, `code-architect`, `code-reviewer`) do not need a worktree.
- `--worktree` auto-generates a `do/{task_id}` branch. When a caller needs worktrees on paths it controls (a manifest with disjoint write sets), create them itself and pass each worker its own `workdir` instead.

## Parallel Execution

Prefer `--parallel` for multi-step or multi-agent work. Fall back to single-task mode only when the work is truly linear or the next step needs the full output of the current one.

### Task config format

```bash
codeagent-wrapper --parallel --output results.json <<'EOF'
---TASK---
id: <unique_id>
agent: <agent_name>
workdir: <path>
backend: <name>
model: <model_name>
reasoning_effort: <low|medium|high>
skills: <skill1>, <skill2>
dependencies: <id1>, <id2>
session_id: <id>
skip_permissions: true|false
worktree: true|false
---CONTENT---
<task content>
EOF
```

All header fields are optional except `id`. `backend` and `model` are per-task overrides of the global flags — set them on every block when the global default (`codex`) is not what you want. `reasoning_effort` is ignored by the omp backend; put the effort in the `model` value instead.

### Dependency resolution

- Tasks are topologically sorted (Kahn's algorithm); circular dependencies are detected and reported.
- A failed parent task causes its dependents to be skipped.
- Independent tasks at the same level run concurrently, bounded by `CODEAGENT_MAX_PARALLEL_WORKERS`.

### Multi-agent orchestration example

```bash
codeagent-wrapper --parallel <<'EOF'
---TASK---
id: p1_architecture
agent: code-explorer
workdir: .
---CONTENT---
Map architecture for the authentication subsystem. Return: module map + key files with line numbers.

---TASK---
id: p2_design
agent: code-architect
workdir: .
dependencies: p1_architecture
---CONTENT---
Design a minimal-change implementation plan based on the architecture analysis.

---TASK---
id: p3_backend
agent: develop
workdir: .
skills: golang-base-practices
dependencies: p2_design
---CONTENT---
Implement backend changes following the design plan.

---TASK---
id: p4_review
agent: code-reviewer
workdir: .
dependencies: p3_backend
---CONTENT---
Review all changes for correctness, edge cases, and KISS compliance. Classify each issue as BLOCKING or MINOR.
EOF
```

### Output modes

**Summary (default)** — one structured block per task:

```text
=== Execution Report ===
3 tasks | 2 passed | 1 failed

### task_id PASS 92%
Did: Brief description of work done
Files: file1.ts, file2.ts
Tests: 12 passed
Log: /tmp/codeagent-xxx.log

### task_id FAIL
Exit code: 1
Error: Assertion failed
Log: /tmp/codeagent-zzz.log
```

**Full (`--full-output`)** — complete task messages; use only when debugging a specific failure.

**Structured JSON (`--output`)** — the authoritative form for automation:

```json
{
  "results": [
    {
      "task_id": "task_1",
      "exit_code": 0,
      "message": "...",
      "session_id": "...",
      "coverage": "92%",
      "files_changed": ["file.ts"],
      "tests_passed": 12,
      "log_path": "/tmp/..."
    }
  ],
  "summary": { "total": 3, "success": 2, "failed": 1 }
}
```

### Parallel invocation pattern (Bash tool)

```text
Bash tool parameters:
- command: codeagent-wrapper --parallel --output <json> <<'EOF'
  ---TASK---
  id: task_id
  backend: <backend>
  model: <model>
  workdir: /path
  dependencies: dep1, dep2
  ---CONTENT---
  task content
  EOF
- background: true
- description: <brief description>
```

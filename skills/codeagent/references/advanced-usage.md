# Codeagent Advanced Usage

> Moved from SKILL.md: backend selection detail, session resume, and parallel execution.

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
- Example: "Create a responsive dashboard layout with sidebar navigation and data visualization cards"

**Backend Switching**:
- Start with Codex for analysis, switch to Claude for documentation, then Gemini for UI implementation
- Use per-task backend selection in parallel mode to optimize for each task's strengths

## Resume Session

```bash
# Resume with codex backend
codeagent-wrapper --backend codex resume <session_id> - <<'EOF'
<follow-up task>
EOF

# Resume with specific backend
codeagent-wrapper --backend claude resume <session_id> - <<'EOF'
<follow-up task>
EOF
```

## Parallel Execution

**Default (summary mode - context-efficient):**
```bash
codeagent-wrapper --parallel <<'EOF'
---TASK---
id: task1
backend: codex
workdir: /path/to/dir
---CONTENT---
task content
---TASK---
id: task2
dependencies: task1
---CONTENT---
dependent task
EOF
```

**Full output mode (for debugging):**
```bash
codeagent-wrapper --parallel --full-output <<'EOF'
...
EOF
```

**Output Modes:**
- **Summary (default)**: Structured report with changes, output, verification, and review summary.
- **Full (`--full-output`)**: Complete task messages. Use only when debugging specific failures.

**With per-task backend**:
```bash
codeagent-wrapper --parallel <<'EOF'
---TASK---
id: task1
backend: codex
workdir: /path/to/dir
---CONTENT---
analyze code structure
---TASK---
id: task2
backend: claude
dependencies: task1
---CONTENT---
design architecture based on analysis
---TASK---
id: task3
backend: gemini
dependencies: task2
---CONTENT---
generate implementation code
EOF
```

**Concurrency Control**:
Set `CODEAGENT_MAX_PARALLEL_WORKERS` to limit concurrent tasks (default: unlimited).

## Parallel Invocation Pattern (Bash tool)

```
Bash tool parameters:
- command: codeagent-wrapper --parallel --backend <backend> <<'EOF'
  ---TASK---
  id: task_id
  backend: <backend>  # Optional, overrides global
  workdir: /path
  dependencies: dep1, dep2
  ---CONTENT---
  task content
  EOF
- timeout: <timeout_ms>  # simple: 1800000, medium: 3600000, complex: 7200000
- description: <brief description>

Note: Global --backend is required; per-task backend is optional
```

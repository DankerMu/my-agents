# Codex CLI Hook Reference

Complete reference for Codex hooks. For cross-platform concepts, see the main SKILL.md.

## Configuration Locations

Codex discovers hooks in this order (most specific wins):

1. `<repo>/.codex/hooks.json` — project-level
2. `<repo>/.codex/config.toml` — project-level (inline hooks)
3. `~/.codex/hooks.json` — user-level
4. `~/.codex/config.toml` — user-level

### JSON Format (`.codex/hooks.json`)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash tools/validate-bash.sh",
            "timeout": 30,
            "statusMessage": "Checking command safety"
          }
        ]
      }
    ]
  }
}
```

### TOML Format (`.codex/config.toml`)

```toml
[[hooks.PreToolUse]]
matcher = "Bash"

[[hooks.PreToolUse.hooks]]
type = "command"
command = "bash tools/validate-bash.sh"
timeout = 30
statusMessage = "Checking command safety"
```

## All 6 Hook Events

### PreToolUse

Fires before tool execution.

**Input fields:** `tool_name`, `tool_input`

**Output support:**
- `systemMessage`: Yes — injected into agent context
- `continue`: No — not supported
- `stopReason`: No — not supported

**Exit codes:**
- 0: Allow (stdout shown)
- 2: Block (stderr fed to agent)

**Matcher:** Matches against `tool_name`. Tool name `apply_patch` matches both `Edit` and `Write` calls.

### PostToolUse

Fires after tool completes.

**Input fields:** `tool_name`, `tool_input`, `tool_output`

**Output support:**
- `systemMessage`: Yes
- `stopReason`: Yes
- `suppressOutput`: Parsed but not enforced

### PermissionRequest

**Codex-only event.** Fires when agent needs approval before tool execution.

**Input fields:** `tool_name`, `tool_input`

**Output support:**
- `systemMessage`: Yes
- `continue`: No
- `stopReason`: No

Use this to add context when Codex asks for permission — for example, warning about risky operations before the user decides.

### UserPromptSubmit

Fires when user submits a prompt.

**Input fields:** `user_prompt`, `previous_messages_count`

**Output support:**
- `continue`: Yes — set false to block the prompt
- `stopReason`: Yes

**Matcher:** Ignored (hook fires for all prompts regardless of matcher).

### SessionStart

Fires when session begins, resumes, or clears.

**Input fields:** `start_source` (`"startup"`, `"resume"`, or `"clear"`)

**Output support:**
- `continue`: Yes
- `stopReason`: Yes

**Matcher:** Filters by `start_source` value, not tool name.

**Note:** Codex does NOT have `$CLAUDE_ENV_FILE`. To persist environment, your script must use other mechanisms (write to a temp file and source it, etc.).

### Stop

Fires when conversation turn ends.

**Output support:**
- `continue`: Yes — set false to block the stop
- `stopReason`: Yes

**Matcher:** Ignored.

## Output Field Support Matrix

| Event | `continue` | `stopReason` | `systemMessage` | `suppressOutput` |
|-------|:----------:|:------------:|:----------------:|:-----------------:|
| PreToolUse | No | No | Yes | No |
| PostToolUse | No | Yes | Yes | Parsed, not enforced |
| PermissionRequest | No | No | Yes | No |
| UserPromptSubmit | Yes | Yes | No | No |
| SessionStart | Yes | Yes | No | No |
| Stop | Yes | Yes | No | No |

## Hook Command Properties

```json
{
  "type": "command",
  "command": "script or shell command",
  "timeout": 600,
  "statusMessage": "Shown in UI while hook runs"
}
```

- `command` (required): Shell command or script path
- `timeout` (optional): Seconds, default 600 (10 minutes)
- `statusMessage` (optional): User-visible progress message — not available in Claude Code

## Input Delivery

Codex delivers hook input as **single-line JSON on stdin**. Read it with:

```bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
```

**Common input fields (all events):**
```json
{
  "session_id": "unique-id",
  "transcript_path": "/path/to/transcript",
  "cwd": "/current/dir",
  "hook_event_name": "PreToolUse",
  "model": "model-identifier",
  "permission_mode": "ask|allow"
}
```

**Turn-scoped events** additionally include `turn_id`.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `$PLUGIN_ROOT` | Plugin root directory (native) |
| `$PLUGIN_DATA` | Writable plugin data directory |
| `$CLAUDE_PLUGIN_ROOT` | Compatibility alias for `$PLUGIN_ROOT` |
| `$CLAUDE_PLUGIN_DATA` | Compatibility alias for `$PLUGIN_DATA` |

Standard shell environment (`$PATH`, `$HOME`, git vars) is also available.

**Note:** `$CLAUDE_PROJECT_DIR` and `$CLAUDE_ENV_FILE` are NOT available. Use `git rev-parse --show-toplevel` for project root.

## Handler Types

Codex **only executes command hooks**:

- `"type": "command"` — Executed normally
- `"type": "prompt"` — Parsed but **silently skipped**
- `"type": "agent"` — Parsed but **silently skipped**

This is the most important cross-platform difference. If you need LLM-powered validation on Codex, implement it as a command hook that calls an LLM API directly (via curl or a script).

## Matcher Details

**Tool-based events** (PreToolUse, PostToolUse, PermissionRequest):
- Match against `tool_name`
- Regex syntax: `"Bash"`, `"Edit|Write"`, `"mcp__.*__delete.*"`
- Omit matcher or use `"*"` or `""` for all tools
- `apply_patch` matches both Edit and Write tool calls

**SessionStart:**
- Match against `start_source`: `"startup"`, `"resume"`, `"clear"`

**UserPromptSubmit and Stop:**
- Matchers are **ignored** — hook always fires

## Known Limitations

1. **No prompt hooks** — `type: "prompt"` is parsed but not executed
2. **No SubagentStop** — cannot validate subagent task completion
3. **No SessionEnd** — cannot hook into session cleanup
4. **No PreCompact** — cannot preserve info before compaction
5. **No Notification** — cannot react to notifications
6. **No `$CLAUDE_ENV_FILE`** — cannot persist env vars through SessionStart
7. **PreToolUse output limited** — only `systemMessage` is supported (no `continue`, `stopReason`, `permissionDecision`, or `updatedInput`)
8. **PostToolUse `suppressOutput`** — parsed but not enforced
9. **PreToolUse for apply_patch** — may not consistently fire for file patches

## Subagent Configuration

Codex supports multi-agent via `.codex/config.toml`:

```toml
[features]
multi_agent = true

[agents]
max_threads = 12
max_depth = 2

[agents.explorer]
description = "Read-only repo explorer"
config_file = "agents/explorer.toml"
```

Hooks fire for all agents, not just the main agent. There is no SubagentStop equivalent — use the Stop event instead.

## Debugging

- Validate JSON: `jq . .codex/hooks.json`
- Test scripts directly: `echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | bash tools/validate.sh`
- Invalid JSON in hooks.json causes load failure at startup
- Hook changes require session restart

# Claude Code Hook Reference

Complete reference for Claude Code hooks. For cross-platform concepts, see the main SKILL.md.

## Configuration Location

Hooks are defined in the `"hooks"` key of `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...]
  },
  "enabledPlugins": { ... }
}
```

Plugin hooks use a wrapper format in `hooks/hooks.json`:

```json
{
  "description": "Optional description",
  "hooks": {
    "PreToolUse": [...],
    "Stop": [...]
  }
}
```

Plugin hooks merge with user hooks and run in parallel.

## All 9 Hook Events

### PreToolUse

Fires before any tool executes. Can approve, deny, modify, or ask for confirmation.

**Input fields:** `tool_name`, `tool_input`

**Output (command hook):**
- Exit 0: allow (stdout shown in transcript)
- Exit 2: deny (stderr fed back to agent)

**Output (prompt hook):** Return structured decision:
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {"file_path": "/modified/path"}
  },
  "systemMessage": "Explanation for Claude"
}
```

`updatedInput` lets you modify tool parameters before execution — powerful for path rewriting, input sanitization, or adding defaults.

**Supports:** command hooks, prompt hooks

### PostToolUse

Fires after tool completes. Use for feedback, quality checks, logging.

**Input fields:** `tool_name`, `tool_input`, `tool_result`

**Output behavior:**
- Exit 0: stdout shown in transcript
- Exit 2: stderr fed back to Claude as context
- `systemMessage` included in Claude's context

**Supports:** command hooks, prompt hooks

### Stop

Fires when the main agent considers stopping. Can block the stop to enforce completeness.

**Input fields:** `reason`

**Decision output:**
```json
{
  "decision": "approve|block",
  "reason": "Tests must run after code changes",
  "systemMessage": "Additional context"
}
```

**Supports:** command hooks, prompt hooks

### SubagentStop

Fires when a subagent considers stopping. Ensures subagent completed its assigned task.

Same interface as Stop, scoped to subagents.

**Supports:** command hooks, prompt hooks

**Note:** Codex does not have this event.

### UserPromptSubmit

Fires when user submits a prompt. Add context, validate, or block prompts.

**Input fields:** `user_prompt`

**Supports:** command hooks, prompt hooks

### SessionStart

Fires when session begins. Load context and set environment.

**Special capability:** Persist environment variables via `$CLAUDE_ENV_FILE`:
```bash
#!/bin/bash
cd "$CLAUDE_PROJECT_DIR" || exit 1

if [ -f "package.json" ]; then
  echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
fi

if [ -f ".nvmrc" ]; then
  NODE_VERSION=$(cat .nvmrc)
  echo "export NODE_VERSION=$NODE_VERSION" >> "$CLAUDE_ENV_FILE"
fi
```

Variables written to `$CLAUDE_ENV_FILE` are available in all subsequent hooks for the session.

**Supports:** command hooks only (prompt hooks not available for SessionStart)

### SessionEnd

Fires when session ends. Use for cleanup, analytics, state persistence.

**Supports:** command hooks only

### PreCompact

Fires before context compaction. Output is preserved through compaction — use to inject critical information that must survive context reduction.

**Supports:** command hooks only

### Notification

Fires when Claude sends notifications. Matchers filter by notification type.

**Common matchers:**
- `permission_prompt` — user needs to approve something
- `idle_prompt` — agent is waiting for input

**Example — desktop notification on idle:**
```json
{
  "Notification": [
    {
      "matcher": "idle_prompt",
      "hooks": [
        {
          "type": "command",
          "command": "osascript -e 'display notification \"Claude is waiting\" with title \"Claude Code\"'"
        }
      ]
    }
  ]
}
```

**Supports:** command hooks only

## Prompt Hook API

Prompt hooks are Claude Code's distinguishing feature. The LLM evaluates the prompt and returns a decision.

**Supported events:** PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit

**Format:**
```json
{
  "type": "prompt",
  "prompt": "Your evaluation instructions. Use $TOOL_INPUT, $TOOL_RESULT, $USER_PROMPT for variable substitution.",
  "timeout": 30
}
```

**Variable substitution in prompts:**
- `$TOOL_INPUT` — the tool's input JSON
- `$TOOL_RESULT` — the tool's output (PostToolUse only)
- `$USER_PROMPT` — user's prompt text (UserPromptSubmit only)
- `$TRANSCRIPT_PATH` — path to conversation transcript

**When to use prompt hooks over command hooks:**
- Validation requires understanding intent, not just patterns
- Edge cases are too numerous to enumerate in regex
- You want natural language explanations in denials
- The check involves reasoning about code semantics

**When to stick with command hooks:**
- Deterministic checks (file size, path patterns, exact string match)
- Performance-critical paths (prompt hooks add 5-30s latency)
- External tool integration (linters, scanners)
- The logic is simple enough for a bash script

## Environment Variables

| Variable | Available In | Purpose |
|----------|-------------|---------|
| `$CLAUDE_PROJECT_DIR` | All hooks | Project root directory |
| `$CLAUDE_PLUGIN_ROOT` | Plugin hooks | Plugin installation directory |
| `$CLAUDE_ENV_FILE` | SessionStart only | Write env vars here to persist them |
| `$CLAUDE_TOOL_INPUT` | PreToolUse, PostToolUse | Tool input JSON (also available via stdin) |
| `$CLAUDE_CODE_REMOTE` | All hooks | Set if running in remote/headless context |

**Always use `${CLAUDE_PLUGIN_ROOT}` in plugin hook commands for portability:**
```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
}
```

## Hook Execution Model

- All matching hooks for an event run **in parallel**
- Hooks don't see each other's output
- Execution order is non-deterministic
- Design each hook to be independent
- Hooks load at **session start** — changes require restart
- Use `/hooks` command to inspect loaded hooks
- Use `claude --debug` for detailed execution logs

## Timeout Defaults

- Command hooks: 60 seconds
- Prompt hooks: 30 seconds
- Override with `"timeout": <seconds>` in hook config

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Plugin hooks vs settings hooks format confusion | Plugin uses `{"description": "...", "hooks": {...}}` wrapper; settings uses direct `{"hooks": {...}}` |
| Prompt hook returns unexpected format | Be explicit in prompt: "Return 'approve' or 'deny'" |
| `$CLAUDE_ENV_FILE` doesn't work | Only available in SessionStart hooks |
| Hook modifies tool input but change ignored | Use `hookSpecificOutput.updatedInput` in PreToolUse |
| Multiple hooks conflict on permissionDecision | Most restrictive wins (deny > ask > allow) |

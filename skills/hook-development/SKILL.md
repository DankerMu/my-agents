---
name: hook-development
description: Cross-platform guidance for designing, configuring, debugging, and validating Claude Code and Codex hooks. Use for agent hook events, configuration, scripts, matchers, exit codes, and dual-platform setups; not for React hooks, webhooks, or GitHub Actions.
version: 0.1.1
---

# Cross-Platform Hook Development

## Overview

Hooks are event-driven automation that execute when an AI coding agent takes specific actions — before a tool runs, after a file edit, when the agent tries to stop, or when a session starts. They enforce policies, validate operations, inject context, and integrate external tools.

Both Claude Code and Codex CLI support hooks with the same core model: a **hook script receives JSON on stdin, does its work, and communicates back via exit code and stdout/stderr**. The differences are in configuration format, supported events, and some advanced capabilities.

This skill teaches you to design hooks that work on both platforms, and to handle the gaps where they diverge.

## Platform Detection

Before writing hooks, identify which platform(s) the project uses:

| Signal | Platform |
|--------|----------|
| `.claude/settings.json` exists with `"hooks"` key | Claude Code |
| `.codex/hooks.json` exists | Codex |
| `.codex/config.toml` has `[[hooks]]` blocks | Codex |
| Both `.claude/` and `.codex/` directories exist | Dual-platform project |

For dual-platform projects, write hook **scripts** once and reference them from both config files. The configs differ but the scripts can be shared.

## Hook Types

### Command Hooks (Both Platforms)

Execute a shell command. The workhorse hook type — deterministic, fast, works everywhere:

```json
{
  "type": "command",
  "command": "bash path/to/validate.sh",
  "timeout": 60
}
```

Use for: input validation, path safety checks, file size limits, external tool integration, linting, anything with clear yes/no logic.

### Prompt-Based Hooks (Claude Code Only)

Use an LLM to make context-aware decisions with natural language reasoning:

```json
{
  "type": "prompt",
  "prompt": "Evaluate if this bash command is safe: $TOOL_INPUT. Check for destructive operations, privilege escalation, and network access. Return 'approve' or 'deny'.",
  "timeout": 30
}
```

Prompt hooks catch edge cases that regex can't — they understand intent, not just patterns. But they cost tokens and add latency.

**Codex does not support prompt hooks.** It parses the `"type": "prompt"` field but silently skips execution. For dual-platform projects, always provide a command hook equivalent. See "Prompt Hook Degradation" below.

## Hook Events

Not every event exists on both platforms. Design around the intersection, then add platform-specific hooks where valuable.

| Event | Claude Code | Codex | Primary Use |
|-------|:-----------:|:-----:|-------------|
| **PreToolUse** | Yes | Yes | Validate/block/modify tool calls before execution |
| **PostToolUse** | Yes | Yes | React to results, provide feedback, log |
| **Stop** | Yes | Yes | Verify task completeness before agent stops |
| **UserPromptSubmit** | Yes | Yes | Add context, validate, or block user prompts |
| **SessionStart** | Yes | Yes | Load project context, set environment |
| **SubagentStop** | Yes | No | Validate subagent task completion |
| **SessionEnd** | Yes | No | Cleanup, logging, state preservation |
| **PreCompact** | Yes | No | Preserve critical info before context compaction |
| **Notification** | Yes | No | React to user notifications |
| **PermissionRequest** | No | Yes | Intercept permission approval requests |

**Safe cross-platform set:** PreToolUse, PostToolUse, Stop, UserPromptSubmit, SessionStart — these five work on both.

## Configuration Formats

Claude Code wires hooks under a top-level `"hooks"` key in `.claude/settings.json`. Codex uses a hooks-only `.codex/hooks.json` (same structure, plus `statusMessage`) or `[[hooks]]` blocks in `.codex/config.toml`. Full formats, examples, the dual-platform template, and environment variables: [references/configuration.md](references/configuration.md).

For dual-platform projects, point both configs at the same shared scripts (e.g. `tools/hooks/`) — configs differ, scripts don't.

## Matchers

Matchers filter which tools trigger a hook. Both platforms use regex against tool names.

```json
"matcher": "Bash"              // Exact tool name
"matcher": "Write|Edit"        // Multiple tools (OR)
"matcher": "mcp__.*__delete.*" // Regex for MCP delete operations
"matcher": "*"                 // Wildcard — all tools
```

Matchers are **case-sensitive**. Common tool names: `Bash`, `Read`, `Write`, `Edit`, `Agent`.

For MCP tools, the naming pattern is `mcp__<server>__<tool>`:
```json
"matcher": "mcp__.*"                    // All MCP tools
"matcher": "mcp__plugin_asana_.*"       // Specific MCP server
```

**Codex note:** For SessionStart, matcher filters by start source (`startup`, `resume`, `clear`). For UserPromptSubmit and Stop, matchers are ignored.

## Hook Input/Output

All hooks receive a JSON object on stdin — `session_id`, `cwd`, `hook_event_name`, plus event-specific fields such as `tool_name`/`tool_input` or `user_prompt`. Claude Code also mirrors input into `$CLAUDE_TOOL_INPUT`; Codex is stdin-only. **Always read from stdin** (`input=$(cat)`) so scripts work on both platforms.

Exit codes (both platforms): `0` — success, stdout shown in transcript; `2` — blocking error, stderr fed back to the agent. Richer JSON output (`continue`/`systemMessage`, PreToolUse `permissionDecision`/`updatedInput`, Stop `decision`) is platform- and event-specific — see [references/claude-code.md](references/claude-code.md) and the output support matrix in [references/codex.md](references/codex.md).

## Common Patterns (Quick Reference)

These patterns work on **both platforms** using command hooks:

| Pattern | Event | What It Does |
|---------|-------|--------------|
| **Path Safety** | PreToolUse (Write/Edit) | Block writes to system paths, .env, credentials |
| **Dangerous Command** | PreToolUse (Bash) | Block rm -rf, sudo, dd, mkfs |
| **Test Enforcement** | Stop | Block stop if code changed but no tests ran |
| **Context Loading** | SessionStart | Detect project type, set env vars |
| **Code Quality** | PostToolUse (Write/Edit) | Run linter after file edits |
| **Completion Check** | Stop | Verify build succeeded and questions answered |

For complete implementations of each pattern with dual-platform configs, see `references/patterns.md`.

## Security Best Practices

These apply to command hooks on both platforms:

**Always validate input:**
```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

if [[ ! "$tool_name" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo '{"decision": "deny", "reason": "Invalid tool name"}' >&2
  exit 2
fi
```

**Check for path traversal:**
```bash
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
  exit 2
fi
```

**Quote all variables** — unquoted variables are injection vectors:
```bash
echo "$file_path"       # GOOD
echo $file_path         # BAD — word splitting + globbing
```

**Set timeouts** — prevent hooks from blocking the agent indefinitely. Default: 60s for command hooks, 30s for prompt hooks.

## Prompt Hook Degradation Strategy

When a project uses both platforms and you want prompt hook intelligence on Claude Code with a command hook fallback on Codex:

**Claude Code** — use the prompt hook for nuanced reasoning:
```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "prompt",
      "prompt": "Analyze command for destructive ops, privilege escalation, network access without consent. Return 'approve' or 'deny'."
    }
  ]
}
```

**Codex** — use a command hook with equivalent deterministic logic:
```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "bash tools/hooks/validate-bash.sh",
      "statusMessage": "Checking command safety"
    }
  ]
}
```

The command hook won't catch as many edge cases as the prompt hook, but it covers the common dangerous patterns. This is an acceptable tradeoff — prompt hooks are a bonus, not a requirement.

## Debugging

Platform debug commands (`claude --debug`, `jq` config checks), direct script testing with piped JSON, and the common-issues table: [references/debugging.md](references/debugging.md).

## Dual-Platform Workflow

When maintaining hooks for both platforms in one project:

1. **Write scripts first** — put reusable logic in `tools/hooks/` or similar
2. **Scripts read stdin** — use `input=$(cat)` so they work on both platforms
3. **Derive project root portably** — `git rev-parse --show-toplevel` works everywhere
4. **Generate both configs** — or maintain them manually with the same script references
5. **Test on both** — run script directly with piped JSON, then test in each runtime

## Implementation Workflow

To add hooks to a project:

1. Identify which events you need (start with the cross-platform five)
2. Choose hook type: command for deterministic checks, prompt for reasoning (Claude Code only)
3. Write hook scripts in a shared location
4. Add configuration for your platform(s)
5. Test scripts directly with piped JSON
6. Test in runtime (`claude --debug` or Codex startup)
7. Document hooks in project README or AGENTS.md

## Additional Resources

For detailed platform-specific reference and extended patterns, consult:

- **`references/claude-code.md`** — Complete Claude Code hook reference: all 9 events, prompt hook API, plugin hooks.json format, env vars
- **`references/codex.md`** — Complete Codex hook reference: all 6 events, config.toml format, output field support matrix, limitations
- **`references/patterns.md`** — 10+ proven cross-platform patterns with dual-config examples
- **`references/advanced.md`** — Advanced: multi-stage validation, cross-event state, caching, external integrations, rate limiting, testing
- **`references/configuration.md`** — Config file formats for both platforms, dual-platform template, environment variables
- **`references/debugging.md`** — Debug commands, direct script testing, common-issues table

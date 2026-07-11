# Hook Configuration Formats & Environment Variables

> Moved from SKILL.md: full config examples for both platforms, the dual-platform template, and environment variables.

### Claude Code — `.claude/settings.json`

Hooks live inside a top-level `"hooks"` key:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash tools/validate-bash.sh"
          }
        ]
      }
    ]
  }
}
```

### Codex — `.codex/hooks.json`

Same structure, but the file is hooks-only (no other settings mixed in). Codex also supports a `statusMessage` field:

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
            "statusMessage": "Checking bash command safety"
          }
        ]
      }
    ]
  }
}
```

### Codex Alternative — `.codex/config.toml`

Codex also accepts hooks inline in TOML format. Less common but useful for simple setups.

### Dual-Platform Template

For projects using both, point both configs at the **same scripts**:

```
project/
  .claude/settings.json    # Claude Code hooks config
  .codex/hooks.json        # Codex hooks config
  tools/hooks/             # Shared hook scripts (both configs reference these)
    validate-bash.sh
    validate-write.sh
    load-context.sh
```

## Environment Variables

| Variable | Claude Code | Codex | Purpose |
|----------|:-----------:|:-----:|---------|
| `$CLAUDE_PROJECT_DIR` | Yes | No | Project root |
| `$CLAUDE_PLUGIN_ROOT` | Yes | Yes (compat alias) | Plugin directory |
| `$CLAUDE_ENV_FILE` | Yes | No | SessionStart: persist env vars here |
| `$PLUGIN_ROOT` | No | Yes | Plugin directory (native) |
| `$PLUGIN_DATA` | No | Yes | Writable plugin data directory |

**Cross-platform script pattern:**
```bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
```

# Hook Debugging

> Moved from SKILL.md: platform debug commands, direct script testing, and the common-issues table.

### Claude Code

```bash
claude --debug    # Verbose hook execution logs
```

Use `/hooks` in-session to review loaded hooks. Changes to hooks require session restart.

### Codex

Check `.codex/hooks.json` syntax:
```bash
jq . .codex/hooks.json    # Validates JSON
```

Codex logs hook execution to its standard output. Invalid JSON causes load failure at startup.

### Testing Hook Scripts Directly

Test any hook script by piping sample JSON:
```bash
echo '{"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}}' | \
  bash tools/hooks/validate-bash.sh
echo "Exit code: $?"
```

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hook never fires | Wrong matcher (case-sensitive) | Check exact tool name |
| Hook fires but no effect | Script exits 0 with no output | Use exit 2 + stderr for blocking |
| "Invalid JSON" at startup | Syntax error in config | Run `jq .` on the config file |
| Changes not taking effect | Hooks load at session start | Restart the session |
| Codex prompt hook silently skipped | Codex doesn't execute prompt hooks | Use command hook instead |

# Advanced Hook Techniques

Patterns for sophisticated hook automation. These work on both platforms unless noted.

## Multi-Stage Validation

Combine fast deterministic checks with deeper analysis. On Claude Code, the second stage can be a prompt hook; on Codex, use a more thorough command hook.

**Claude Code — command + prompt in parallel:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "bash tools/hooks/quick-check.sh",
          "timeout": 5
        },
        {
          "type": "prompt",
          "prompt": "Deep analysis of bash command safety: $TOOL_INPUT",
          "timeout": 15
        }
      ]
    }
  ]
}
```

**Codex — command hooks only:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash tools/hooks/quick-check.sh",
            "timeout": 5,
            "statusMessage": "Quick safety check"
          },
          {
            "type": "command",
            "command": "bash tools/hooks/deep-check.sh",
            "timeout": 15,
            "statusMessage": "Deep safety analysis"
          }
        ]
      }
    ]
  }
}
```

**Quick check script** — approve obviously safe commands immediately:
```bash
#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command')

# Immediate pass for safe read-only commands
if [[ "$command" =~ ^(ls|pwd|echo|date|whoami|cat|head|tail|wc|file)(\s|$) ]]; then
  exit 0
fi

# Let the next hook handle complex cases
exit 0
```

## Cross-Event State Tracking

Coordinate across events using temporary files. This works because PreToolUse → PostToolUse → Stop happen sequentially within a session.

**SessionStart — initialize tracking:**
```bash
#!/bin/bash
TRACK_DIR="/tmp/hook-session-$$"
mkdir -p "$TRACK_DIR"
echo "0" > "$TRACK_DIR/test-count"
echo "0" > "$TRACK_DIR/edit-count"
```

**PostToolUse — record events:**
```bash
#!/bin/bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
TRACK_DIR="/tmp/hook-session-$$"

[ ! -d "$TRACK_DIR" ] && exit 0

if [[ "$tool_name" == "Write" ]] || [[ "$tool_name" == "Edit" ]]; then
  count=$(cat "$TRACK_DIR/edit-count" 2>/dev/null || echo "0")
  echo $((count + 1)) > "$TRACK_DIR/edit-count"
fi

if [[ "$tool_name" == "Bash" ]]; then
  result=$(echo "$input" | jq -r '.tool_result // .tool_output // empty')
  if echo "$result" | grep -qiE '(test|spec|jest|vitest|pytest)'; then
    count=$(cat "$TRACK_DIR/test-count" 2>/dev/null || echo "0")
    echo $((count + 1)) > "$TRACK_DIR/test-count"
  fi
fi

exit 0
```

**Stop — enforce based on tracked state:**
```bash
#!/bin/bash
TRACK_DIR="/tmp/hook-session-$$"

[ ! -d "$TRACK_DIR" ] && exit 0

edits=$(cat "$TRACK_DIR/edit-count" 2>/dev/null || echo "0")
tests=$(cat "$TRACK_DIR/test-count" 2>/dev/null || echo "0")

if [ "$edits" -gt 0 ] && [ "$tests" -eq 0 ]; then
  echo "$edits files edited but 0 test runs detected. Run tests before stopping." >&2
  exit 2
fi

exit 0
```

**Caveat:** `$$` (PID) differs per hook invocation. Use a fixed session identifier instead — derive from `session_id` in the input JSON, or use a temp dir keyed by working directory:
```bash
TRACK_DIR="/tmp/hook-$(echo "$PWD" | md5sum | cut -c1-8)"
```

## Caching Validation Results

Avoid re-validating the same file within a time window:

```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
cache_key=$(echo -n "$file_path" | md5sum | cut -d' ' -f1)
cache_file="/tmp/hook-cache-$cache_key"

# Check cache (5 minute TTL)
if [ -f "$cache_file" ]; then
  cache_age=$(($(date +%s) - $(stat -f%m "$cache_file" 2>/dev/null || stat -c%Y "$cache_file")))
  if [ "$cache_age" -lt 300 ]; then
    cat "$cache_file"
    exit 0
  fi
fi

# Perform validation
result='{"continue": true}'
# ... actual validation logic ...

echo "$result" > "$cache_file"
echo "$result"
exit 0
```

## Rate Limiting

Prevent rapid-fire operations that could indicate runaway behavior:

```bash
#!/bin/bash
rate_file="/tmp/hook-rate-$(echo "$PWD" | md5sum | cut -c1-8)"
current_minute=$(date +%Y%m%d%H%M)
max_ops_per_minute=20

if [ -f "$rate_file" ]; then
  last_minute=$(head -1 "$rate_file")
  count=$(tail -1 "$rate_file")
  if [ "$current_minute" = "$last_minute" ]; then
    if [ "$count" -ge "$max_ops_per_minute" ]; then
      echo "Rate limit: $count operations this minute (max $max_ops_per_minute)" >&2
      exit 2
    fi
    count=$((count + 1))
  else
    count=1
  fi
else
  count=1
fi

printf '%s\n%s\n' "$current_minute" "$count" > "$rate_file"
exit 0
```

## External System Integration

### Slack Notification on Blocked Operations

```bash
#!/bin/bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
command=$(echo "$input" | jq -r '.tool_input.command // "N/A"')

# Only notify if actually blocking
if echo "$command" | grep -qE '(rm\s+-rf|sudo|dd\s+if=)'; then
  # Send to Slack (non-blocking)
  curl -s -X POST "${SLACK_WEBHOOK_URL:-}" \
    -H 'Content-Type: application/json' \
    -d "{\"text\": \"Hook blocked ${tool_name}: ${command:0:100}\"}" \
    2>/dev/null &

  echo "Blocked: $command" >&2
  exit 2
fi

exit 0
```

### Audit Logging

```bash
#!/bin/bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
timestamp=$(date -Iseconds)

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
LOG_FILE="$PROJECT_DIR/.hook-audit.log"

echo "$timestamp | $USER | $tool_name" >> "$LOG_FILE"
exit 0
```

### Secret Detection in Written Content

```bash
#!/bin/bash
input=$(cat)
content=$(echo "$input" | jq -r '.tool_input.content // empty')

[ -z "$content" ] && exit 0

# Common secret patterns
if echo "$content" | grep -qE "(api[_-]?key|password|secret|token|private[_-]?key).{0,20}['\"]?[A-Za-z0-9/+=]{20,}"; then
  echo "Potential secret detected in file content. Review before proceeding." >&2
  exit 2
fi

# AWS keys
if echo "$content" | grep -qE "AKIA[0-9A-Z]{16}"; then
  echo "AWS access key detected in content." >&2
  exit 2
fi

exit 0
```

## Performance Optimization

### Design for Parallel Execution

All matching hooks run in parallel. Implications:
- Hooks cannot see each other's output
- Execution order is non-deterministic
- Each hook must be self-contained

**Good:** Three independent checks that each take 2s = 2s total
**Bad:** Hook B depends on Hook A's output = race condition

### Minimize I/O in Hot Paths

PreToolUse fires on **every** tool call. Keep these hooks fast:
- Avoid network calls in PreToolUse unless critical
- Use in-memory checks (regex, string matching) over file system scans
- Cache results for repeated validations
- Set tight timeouts (5-10s for quick checks)

### Fast-Path Exit

Check the cheapest conditions first:
```bash
#!/bin/bash
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

# Fast exit for tools we don't care about
[[ "$tool_name" != "Bash" ]] && exit 0

command=$(echo "$input" | jq -r '.tool_input.command')

# Fast exit for safe commands
[[ "$command" =~ ^(ls|pwd|echo) ]] && exit 0

# Expensive validation only for remaining commands
# ...
```

## Testing Hooks

### Unit Testing Hook Scripts

```bash
#!/bin/bash
# test-hooks.sh — run this to verify hook behavior

PASS=0
FAIL=0

test_hook() {
  local name="$1" input="$2" script="$3" expected_exit="$4"
  actual_exit=0
  echo "$input" | bash "$script" >/dev/null 2>&1 || actual_exit=$?
  if [ "$actual_exit" -eq "$expected_exit" ]; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name (expected exit $expected_exit, got $actual_exit)"
    FAIL=$((FAIL + 1))
  fi
}

# Test path safety
test_hook "Allow normal path" \
  '{"tool_input":{"file_path":"/home/user/project/src/main.ts"}}' \
  "tools/hooks/validate-write.sh" 0

test_hook "Block path traversal" \
  '{"tool_input":{"file_path":"/home/user/../etc/passwd"}}' \
  "tools/hooks/validate-write.sh" 2

test_hook "Block .env file" \
  '{"tool_input":{"file_path":"/project/.env"}}' \
  "tools/hooks/validate-write.sh" 2

# Test bash safety
test_hook "Allow ls" \
  '{"tool_input":{"command":"ls -la"}}' \
  "tools/hooks/validate-bash.sh" 0

test_hook "Block rm -rf" \
  '{"tool_input":{"command":"rm -rf /"}}' \
  "tools/hooks/validate-bash.sh" 2

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
```

### Integration Testing

Test the full hook lifecycle by simulating events:

```bash
# Simulate a PreToolUse → PostToolUse → Stop sequence
echo '{"hook_event_name":"SessionStart","cwd":"/project"}' | bash tools/hooks/load-context.sh

echo '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"src/app.ts"}}' | \
  bash tools/hooks/validate-write.sh

echo '{"hook_event_name":"PostToolUse","tool_name":"Write","tool_input":{"file_path":"src/app.ts"}}' | \
  bash tools/hooks/check-quality.sh

echo '{"hook_event_name":"Stop","transcript_path":"/tmp/test-transcript"}' | \
  bash tools/hooks/check-tests-ran.sh
```

## Writing Cross-Platform Hook Scripts

Checklist for scripts that work on both Claude Code and Codex:

1. **Read input from stdin:** `input=$(cat)` — works everywhere
2. **Derive project root portably:** `PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"`
3. **Guard optional env vars:** `[ -n "${CLAUDE_ENV_FILE:-}" ] && echo "..." >> "$CLAUDE_ENV_FILE"`
4. **Use jq for JSON parsing:** Both platforms deliver JSON
5. **Exit 0 for allow, exit 2 for block:** Universal convention
6. **Handle missing fields gracefully:** Use `// empty` or `// "default"` in jq
7. **No platform-specific assumptions:** Don't assume `$CLAUDE_TOOL_INPUT` exists (Codex doesn't set it)
8. **Use `set -euo pipefail`:** Fail fast on errors
9. **Keep scripts POSIX-compatible where possible:** Avoid bashisms if targeting diverse environments

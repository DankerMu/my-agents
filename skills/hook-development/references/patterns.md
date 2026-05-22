# Cross-Platform Hook Patterns

Proven patterns with dual-platform configuration. Each pattern shows the shared script and both config formats.

## Pattern 1: Path Safety Validation

Block writes to system directories, credentials, and path traversal.

**Script (`tools/hooks/validate-write.sh`):**
```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.content // empty')

[ -z "$file_path" ] && exit 0

# Path traversal
if [[ "$file_path" == *".."* ]]; then
  echo "Path traversal detected: $file_path" >&2
  exit 2
fi

# System directories
if [[ "$file_path" =~ ^/(etc|sys|usr|boot|proc)/ ]]; then
  echo "System path blocked: $file_path" >&2
  exit 2
fi

# Credentials and secrets
if [[ "$file_path" =~ \.(env|pem|key|secret|credentials)$ ]]; then
  echo "Sensitive file blocked: $file_path" >&2
  exit 2
fi

exit 0
```

**Claude Code (`.claude/settings.json`):**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "bash tools/hooks/validate-write.sh"}
        ]
      }
    ]
  }
}
```

**Codex (`.codex/hooks.json`):**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash tools/hooks/validate-write.sh",
            "statusMessage": "Checking file path safety"
          }
        ]
      }
    ]
  }
}
```

## Pattern 2: Dangerous Command Blocking

Block destructive bash commands.

**Script (`tools/hooks/validate-bash.sh`):**
```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

[ -z "$command" ] && exit 0

# Destructive operations
if echo "$command" | grep -qE '(^|\s)(rm\s+-[rR]f|dd\s+if=|mkfs|format\s+|fdisk)(\s|$)'; then
  echo "Destructive command blocked: $command" >&2
  exit 2
fi

# Privilege escalation
if echo "$command" | grep -qE '(^|\s)sudo\s+'; then
  echo "Privilege escalation blocked: $command" >&2
  exit 2
fi

exit 0
```

**Claude Code — enhanced with prompt hook:**
```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {"type": "command", "command": "bash tools/hooks/validate-bash.sh"},
        {
          "type": "prompt",
          "prompt": "Command: $TOOL_INPUT.command. Check for: 1) Destructive operations the regex might miss 2) Data exfiltration 3) Unintended network access. Return 'approve' or 'deny'.",
          "timeout": 15
        }
      ]
    }
  ]
}
```

**Codex — command hook only:**
```json
{
  "hooks": {
    "PreToolUse": [
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
    ]
  }
}
```

## Pattern 3: Test Enforcement

Block the agent from stopping if code was changed but no tests ran.

**Script (`tools/hooks/check-tests-ran.sh`):**
```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
transcript=$(echo "$input" | jq -r '.transcript_path // empty')

[ -z "$transcript" ] || [ ! -f "$transcript" ] && exit 0

# Check if code was modified
if grep -qE '(Write|Edit|apply_patch)' "$transcript" 2>/dev/null; then
  # Check if tests were executed
  if ! grep -qE '(npm test|pnpm test|jest|vitest|pytest|cargo test|go test)' "$transcript" 2>/dev/null; then
    echo "Code was modified but no tests were run. Please run tests before stopping." >&2
    exit 2
  fi
fi

exit 0
```

**Claude Code:**
```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {"type": "command", "command": "bash tools/hooks/check-tests-ran.sh"}
      ]
    }
  ]
}
```

**Codex:**
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash tools/hooks/check-tests-ran.sh",
            "statusMessage": "Verifying tests were run"
          }
        ]
      }
    ]
  }
}
```

## Pattern 4: Context Loading at Session Start

Detect project type and inject environment.

**Script (`tools/hooks/load-context.sh`):**
```bash
#!/bin/bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$PROJECT_DIR" || exit 1

context=""

if [ -f "package.json" ]; then
  context="Node.js project. "
  if [ -f "pnpm-workspace.yaml" ]; then
    context="${context}pnpm monorepo. "
  fi
fi

if [ -f "Cargo.toml" ]; then
  context="${context}Rust project. "
fi

if [ -f "go.mod" ]; then
  context="${context}Go project. "
fi

if [ -f ".env.example" ] && [ ! -f ".env" ]; then
  context="${context}WARNING: .env.example exists but .env is missing. "
fi

# Claude Code: persist to env file if available
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  [ -f "package.json" ] && echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
fi

[ -n "$context" ] && echo "$context"
exit 0
```

**Claude Code:**
```json
{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {"type": "command", "command": "bash tools/hooks/load-context.sh", "timeout": 10}
      ]
    }
  ]
}
```

**Codex:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash tools/hooks/load-context.sh",
            "timeout": 10,
            "statusMessage": "Loading project context"
          }
        ]
      }
    ]
  }
}
```

## Pattern 5: Code Quality After Edits

Run linter after file modifications.

**Script (`tools/hooks/check-quality.sh`):**
```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

[ -z "$file_path" ] && exit 0

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

if [[ "$file_path" == *.ts ]] || [[ "$file_path" == *.tsx ]]; then
  if [ -f "$PROJECT_DIR/node_modules/.bin/eslint" ]; then
    "$PROJECT_DIR/node_modules/.bin/eslint" "$file_path" 2>&1 || true
  fi
elif [[ "$file_path" == *.py ]]; then
  if command -v ruff &>/dev/null; then
    ruff check "$file_path" 2>&1 || true
  fi
fi

exit 0
```

**Both platforms** — same config structure, Codex adds `statusMessage`:
```json
{
  "PostToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {"type": "command", "command": "bash tools/hooks/check-quality.sh"}
      ]
    }
  ]
}
```

## Pattern 6: MCP Tool Monitoring

Guard against destructive MCP operations.

**Script (`tools/hooks/guard-mcp-delete.sh`):**
```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // empty')

if echo "$tool_name" | grep -qiE '(delete|remove|drop|destroy)'; then
  echo "Destructive MCP operation detected: $tool_name. Requires explicit confirmation." >&2
  exit 2
fi

exit 0
```

**Config (both platforms):**
```json
{
  "PreToolUse": [
    {
      "matcher": "mcp__.*__delete.*",
      "hooks": [
        {"type": "command", "command": "bash tools/hooks/guard-mcp-delete.sh"}
      ]
    }
  ]
}
```

## Pattern 7: Build Verification Before Stop

Ensure project builds after code changes.

**Script (`tools/hooks/check-build.sh`):**
```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
transcript=$(echo "$input" | jq -r '.transcript_path // empty')

[ -z "$transcript" ] || [ ! -f "$transcript" ] && exit 0

if grep -qE '(Write|Edit|apply_patch)' "$transcript" 2>/dev/null; then
  if ! grep -qE '(npm run build|pnpm build|cargo build|go build|make)' "$transcript" 2>/dev/null; then
    echo "Code was modified but project was not built. Consider running build before stopping." >&2
    # Exit 0 (warning) not 2 (block) — build isn't always required
    exit 0
  fi
fi

exit 0
```

## Pattern 8: Protected Path Policy

Prevent modification of readonly or generated files.

**Script (`tools/hooks/protected-paths.sh`):**
```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

[ -z "$file_path" ] && exit 0

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PROTECTED_FILE="$PROJECT_DIR/.protected-paths"

if [ ! -f "$PROTECTED_FILE" ]; then
  exit 0
fi

while IFS= read -r pattern; do
  [ -z "$pattern" ] && continue
  [[ "$pattern" == \#* ]] && continue
  if echo "$file_path" | grep -qE "$pattern"; then
    echo "Protected path: $file_path matches pattern '$pattern'" >&2
    exit 2
  fi
done < "$PROTECTED_FILE"

exit 0
```

**`.protected-paths` file example:**
```
node_modules/
dist/
generated/
\.lock$
schema\.prisma$
```

## Pattern 9: Temporarily Active Hooks

Hooks that activate only when a flag file exists.

**Script (`tools/hooks/strict-validation.sh`):**
```bash
#!/bin/bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
FLAG_FILE="$PROJECT_DIR/.enable-strict-validation"

if [ ! -f "$FLAG_FILE" ]; then
  exit 0  # Skip when flag absent
fi

# Flag present — run strict checks
input=$(cat)
# ... validation logic ...
```

**Activate/deactivate:**
```bash
touch .enable-strict-validation    # Enable
rm .enable-strict-validation       # Disable
```

Remember: hooks load at session start, so restart the session after toggling.

## Pattern 10: Configuration-Driven Hooks

Read per-project config to control hook behavior.

**Script (`tools/hooks/configurable-check.sh`):**
```bash
#!/bin/bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
CONFIG="$PROJECT_DIR/.hooks-config.json"

if [ -f "$CONFIG" ]; then
  strict_mode=$(jq -r '.strictMode // false' "$CONFIG")
  max_file_size=$(jq -r '.maxFileSize // 1000000' "$CONFIG")
else
  strict_mode=false
  max_file_size=1000000
fi

[ "$strict_mode" != "true" ] && exit 0

input=$(cat)
# Apply configured limits...
```

**`.hooks-config.json`:**
```json
{
  "strictMode": true,
  "maxFileSize": 500000,
  "blockedPaths": ["/tmp", "/var"]
}
```

## Pattern 11: TypeScript/Frontend Change Reminder

Nudge agent to run typecheck after modifying TS files.

**Script (`tools/hooks/ts-reminder.sh`):**
```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if echo "$file_path" | grep -qE '\.(ts|tsx)$'; then
  if echo "$file_path" | grep -qvE '(node_modules|dist|generated)'; then
    echo "TypeScript file modified. Consider running typecheck to verify."
  fi
fi

exit 0
```

## Combining Patterns

A production setup typically combines several patterns:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "bash tools/hooks/validate-write.sh"},
          {"type": "command", "command": "bash tools/hooks/protected-paths.sh"}
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": "bash tools/hooks/validate-bash.sh"}
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {"type": "command", "command": "bash tools/hooks/check-quality.sh"}
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {"type": "command", "command": "bash tools/hooks/check-tests-ran.sh"}
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {"type": "command", "command": "bash tools/hooks/load-context.sh", "timeout": 10}
        ]
      }
    ]
  }
}
```

This config works on **both platforms** — add `statusMessage` fields for Codex.

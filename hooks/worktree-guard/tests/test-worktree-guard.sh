#!/usr/bin/env bash
# Shell-level tests for worktree-guard.sh with the payload shapes Claude Code,
# Codex (apply_patch carries its targets inside tool_input.command, captured
# from codex-cli 0.158) and the omp shim send. Run:
#   bash hooks/worktree-guard/tests/test-worktree-guard.sh
# (also wired into `npm test` via scripts/tests/worktree-guard.test.js)
set -euo pipefail

HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" && pwd)/worktree-guard.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PROJ="$TMP/proj"
mkdir -p "$PROJ/.worktrees/issue-42/src" "$PROJ/src"
PROJ=$(cd "$PROJ" && pwd -P)
WT="$PROJ/.worktrees/issue-42"

fail=0
passes=0
ERR="$TMP/err.txt"

json() { # <tool_name> <key> <value>
    python3 -c 'import json,sys; print(json.dumps({"tool_name": sys.argv[1], "tool_input": {sys.argv[2]: sys.argv[3]}, "cwd": sys.argv[4]}))' "$1" "$2" "$3" "$PROJ"
}

check() { # <name> <expected rc> <json>
    local rc=0
    printf '%s' "$3" | CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" >/dev/null 2>"$ERR" || rc=$?
    if [ "$rc" = "$2" ]; then
        echo "PASS: $1"
        passes=$((passes + 1))
    else
        echo "FAIL: $1 (expected exit $2, got $rc: $(cat "$ERR"))"
        fail=1
    fi
}

patch() { # <header lines...> -> apply_patch text
    printf '*** Begin Patch\n'
    for line in "$@"; do printf '%s\n' "$line"; done
    printf '*** End Patch'
}

# No manifest: inert everywhere.
check "no manifest is a no-op" 0 "$(json Write file_path "$PROJ/src/a.py")"

printf '{"enabled": true, "allowedRoots": [".worktrees/issue-42"]}' > "$PROJ/.worktree-guard.json"

# Claude Code file tools.
check "claude write inside the worktree passes" 0 "$(json Write file_path "$WT/src/a.py")"
check "claude write outside the worktree is blocked" 2 "$(json Edit file_path "$PROJ/src/a.py")"
check "claude relative path outside is blocked" 2 "$(json Write file_path "src/a.py")"
check "sibling prefix is not inside (issue-420)" 2 "$(json Write file_path "$PROJ/.worktrees/issue-420/a.py")"

# Codex apply_patch: targets live in the patch headers.
check "codex add inside the worktree passes" 0 \
    "$(json apply_patch command "$(patch "*** Add File: $WT/src/new.py" "+x")")"
check "codex add outside the worktree is blocked" 2 \
    "$(json apply_patch command "$(patch "*** Add File: $PROJ/src/new.py" "+x")")"
check "codex relative update outside is blocked" 2 \
    "$(json apply_patch command "$(patch "*** Update File: src/a.py" "@@" "-a" "+b")")"
check "codex delete outside is blocked" 2 \
    "$(json apply_patch command "$(patch "*** Delete File: $PROJ/src/a.py")")"
check "codex move out of the worktree is blocked" 2 \
    "$(json apply_patch command "$(patch "*** Update File: $WT/src/a.py" "*** Move to: $PROJ/src/a.py")")"
check "codex multi-file patch with one outside target is blocked" 2 \
    "$(json apply_patch command "$(patch "*** Update File: $WT/src/a.py" "@@" "-a" "+b" "*** Add File: $PROJ/b.py" "+y")")"
check "codex multi-file patch fully inside passes" 0 \
    "$(json apply_patch command "$(patch "*** Update File: $WT/src/a.py" "@@" "-a" "+b" "*** Add File: $WT/b.py" "+y")")"
check "codex non-patch command is ignored" 0 "$(json Bash command "echo x > $PROJ/src/a.py")"

# omp shim sends one candidate per call under file_path.
check "omp edit outside is blocked" 2 "$(json edit file_path "$PROJ/src/a.py")"

# A stray json.py in the tool cwd must not disable the guard (python3 -I).
mkdir -p "$PROJ/shadow" && printf 'raise SystemExit(0)\n' > "$PROJ/shadow/json.py"
rc=0
printf '%s' "$(json Write file_path "$PROJ/src/a.py")" | (cd "$PROJ/shadow" && CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK") >/dev/null 2>&1 || rc=$?
if [ "$rc" = 2 ]; then echo "PASS: stray json.py cannot disable the guard"; passes=$((passes + 1)); else echo "FAIL: stray json.py cannot disable the guard (rc=$rc)"; fail=1; fi

printf '{"enabled": false, "allowedRoots": [".worktrees/issue-42"]}' > "$PROJ/.worktree-guard.json"
check "disabled manifest is a no-op" 0 "$(json Write file_path "$PROJ/src/a.py")"

echo "passes: $passes"
if [ "$fail" = 0 ]; then
    echo "summary: ALL CHECKS PASSED"
else
    echo "summary: FAILURES"
    exit 1
fi

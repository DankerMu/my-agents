#!/usr/bin/env bash
# Shell-level tests for instruction-guard.sh. Feeds the hook the tool-call JSON
# shapes Claude Code, Codex (captured from codex-cli 0.158 apply_patch / Bash
# calls) and the omp shim send. Run:
#   bash hooks/instruction-guard/tests/test-instruction-guard.sh
# (also wired into `npm test` via scripts/tests/instruction-guard.test.js)
set -euo pipefail

HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" && pwd)/instruction-guard.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
export XDG_STATE_HOME="$TMP/state"
PROJ="$TMP/proj"
mkdir -p "$PROJ/docs"
PROJ=$(cd "$PROJ" && pwd -P)

fail=0
passes=0
OUT="$TMP/out.txt"
ERR="$TMP/err.txt"

# run <platform> <json>; sets rc, leaves stdout/stderr in $OUT/$ERR
run() {
    rc=0
    printf '%s' "$2" | CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" --platform "$1" >"$OUT" 2>"$ERR" || rc=$?
}

json() { # <tool_name> <key> <value> -> tool-call JSON with cwd=$PROJ
    python3 -c 'import json,sys; print(json.dumps({"tool_name": sys.argv[1], "tool_input": {sys.argv[2]: sys.argv[3]}, "cwd": sys.argv[4]}))' "$1" "$2" "$3" "$PROJ"
}

ok() { echo "PASS: $1"; passes=$((passes + 1)); }
bad() { echo "FAIL: $1"; fail=1; }

expect_ask() { # <name> <json>
    run claude "$2"
    if [ "$rc" = 0 ] && grep -q '"permissionDecision": "ask"' "$OUT"; then ok "$1"; else bad "$1 (rc=$rc out=$(cat "$OUT"))"; fi
}
expect_allow() { # <platform> <name> <json>
    run "$1" "$3"
    if [ "$rc" = 0 ] && [ ! -s "$OUT" ]; then ok "$2"; else bad "$2 (rc=$rc out=$(cat "$OUT") err=$(cat "$ERR"))"; fi
}
expect_deny() { # <platform> <name> <json> [stderr substring]
    run "$1" "$3"
    if [ "$rc" = 2 ] && grep -q -- "${4:-instruction-guard: blocked}" "$ERR"; then ok "$2"; else bad "$2 (rc=$rc err=$(cat "$ERR"))"; fi
}

# --- Claude Code: native approval prompt -----------------------------------
expect_ask "claude Write AGENTS.md asks" "$(json Write file_path "$PROJ/AGENTS.md")"
expect_ask "claude Edit nested docs/CLAUDE.md asks" "$(json Edit file_path "docs/CLAUDE.md")"
expect_ask "claude MultiEdit relative ./AGENTS.md asks" "$(json MultiEdit file_path "./AGENTS.md")"
expect_ask "claude Bash heredoc into CLAUDE.md asks" "$(json Bash command "cat > CLAUDE.md <<'EOF'
x
EOF")"
expect_ask "claude Bash append to AGENTS.md asks" "$(json Bash command "echo rule >> AGENTS.md")"
expect_ask "claude Bash sed -i asks" "$(json Bash command "sed -i '' 's/a/b/' docs/AGENTS.md")"
expect_ask "claude Bash git checkout asks" "$(json Bash command "git checkout -- CLAUDE.md")"
expect_ask "claude Bash python heredoc asks" "$(json Bash command "python3 - <<'EOF'
open('AGENTS.md','w').write('x')
EOF")"
expect_ask "claude Bash prettier --write asks" "$(json Bash command "npx prettier --write AGENTS.md")"
expect_allow claude "claude Write README.md passes" "$(json Write file_path "$PROJ/README.md")"
expect_allow claude "claude Write AGENTS.md.bak passes" "$(json Write file_path "$PROJ/AGENTS.md.bak")"
expect_allow claude "claude Write MY_AGENTS.md passes" "$(json Write file_path "$PROJ/MY_AGENTS.md")"
expect_allow claude "claude Bash cat AGENTS.md passes" "$(json Bash command "cat AGENTS.md | head -20")"
expect_allow claude "claude Bash grep with 2>/dev/null passes" "$(json Bash command "grep -n rule CLAUDE.md 2>/dev/null")"
expect_allow claude "claude Bash git diff passes" "$(json Bash command "git diff -- AGENTS.md")"
expect_allow claude "claude Bash write elsewhere passes" "$(json Bash command "echo x > notes.txt")"
expect_allow claude "claude malformed JSON passes" "not json"

# --- Codex: apply_patch payload shape captured from codex-cli 0.158 --------
patch_add="*** Begin Patch
*** Add File: $PROJ/AGENTS.md
+probe
*** End Patch"
patch_two="*** Begin Patch
*** Update File: docs/CLAUDE.md
@@
-a
+b
*** Update File: AGENTS.md
@@
-a
+b
*** End Patch"
patch_other="*** Begin Patch
*** Update File: src/main.py
@@
-a
+b
*** End Patch"
patch_move="*** Begin Patch
*** Update File: notes.md
*** Move to: AGENTS.md
*** End Patch"
expect_deny codex "codex apply_patch Add AGENTS.md denied" "$(json apply_patch command "$patch_add")" "approve"
expect_deny codex "codex apply_patch Move to AGENTS.md denied" "$(json apply_patch command "$patch_move")"
expect_allow codex "codex apply_patch other file passes" "$(json apply_patch command "$patch_other")"
expect_deny codex "codex Bash redirect into AGENTS.md denied" "$(json Bash command "echo x > AGENTS.md")"
expect_allow codex "codex Bash read passes" "$(json Bash command "cat AGENTS.md")"
expect_deny codex "codex self-approval command denied" \
    "$(json Bash command "bash .codex/hooks/instruction-guard/instruction-guard.sh approve AGENTS.md")" "only the user"

# --- one-shot approvals ----------------------------------------------------
(cd "$PROJ" && bash "$HOOK" approve AGENTS.md >/dev/null)
expect_allow codex "codex apply_patch allowed after user approval" "$(json apply_patch command "$patch_add")"
expect_deny codex "approval is consumed after one use" "$(json apply_patch command "$patch_add")"

(cd "$PROJ" && bash "$HOOK" approve AGENTS.md >/dev/null)
expect_deny codex "multi-file patch needs every target approved" "$(json apply_patch command "$patch_two")"
(cd "$PROJ" && bash "$HOOK" approve docs/CLAUDE.md >/dev/null)
expect_allow codex "multi-file patch passes once all targets approved" "$(json apply_patch command "$patch_two")"

(cd "$PROJ" && bash "$HOOK" approve AGENTS.md >/dev/null)
sleep 1
rc=0
printf '%s' "$(json apply_patch command "$patch_add")" | INSTRUCTION_GUARD_TTL=0 CLAUDE_PROJECT_DIR="$PROJ" \
    bash "$HOOK" --platform codex >/dev/null 2>"$ERR" || rc=$?
if [ "$rc" = 2 ]; then ok "expired approval is refused"; else bad "expired approval is refused (rc=$rc)"; fi

rc=0
(cd "$PROJ" && bash "$HOOK" approve README.md >/dev/null 2>&1) || rc=$?
if [ "$rc" = 1 ]; then ok "approve rejects non-instruction files"; else bad "approve rejects non-instruction files (rc=$rc)"; fi

expect_deny codex "writing into the approval store is denied" \
    "$(json Write file_path "$XDG_STATE_HOME/instruction-guard/approvals/forged")" "approval store"

expect_deny codex "shell write into the approval store is denied" \
    "$(json Bash command "echo '{}' > ~/.local/state/instruction-guard/approvals/forged")" "approval store"
mkdir -p "$PROJ/shadow" && printf 'raise SystemExit(0)\n' > "$PROJ/shadow/json.py"
rc=0
printf '%s' "$(json Write file_path "$PROJ/shadow/CLAUDE.md")" | (cd "$PROJ/shadow" && CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" --platform codex) >/dev/null 2>&1 || rc=$?
if [ "$rc" = 2 ]; then ok "a stray json.py in cwd cannot disable the guard"; else bad "a stray json.py in cwd cannot disable the guard (rc=$rc)"; fi

# --- omp shim payloads -----------------------------------------------------
omp_edit=$(python3 -c 'import json,sys; print(json.dumps({"tool_name": "edit", "tool_input": {"paths": [sys.argv[1]]}, "cwd": sys.argv[2]}))' "CLAUDE.md" "$PROJ")
expect_deny omp "omp edit CLAUDE.md denied (shim turns this into confirm)" "$omp_edit"
omp_other=$(python3 -c 'import json,sys; print(json.dumps({"tool_name": "write", "tool_input": {"paths": ["a.txt"]}, "cwd": sys.argv[1]}))' "$PROJ")
expect_allow omp "omp write other file passes" "$omp_other"

echo "passes: $passes"
if [ "$fail" = 0 ]; then
    echo "summary: ALL CHECKS PASSED"
else
    echo "summary: FAILURES"
    exit 1
fi

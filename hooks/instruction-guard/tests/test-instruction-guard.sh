#!/usr/bin/env bash
# Shell-level tests for instruction-guard.sh, the AGENTS.md / CLAUDE.md size gate.
# Feeds the hook the tool-call JSON shapes Claude Code, Codex (captured from
# codex-cli 0.158 apply_patch / Bash calls) and the omp shim (omp 18.13) send. Run:
#   bash hooks/instruction-guard/tests/test-instruction-guard.sh
# (also wired into `npm test` via scripts/tests/instruction-guard.test.js)
set -euo pipefail

HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" && pwd)/instruction-guard.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PROJ="$TMP/proj"
mkdir -p "$PROJ"
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

# pj <tool_name> key=value... -> tool-call JSON with cwd=$PROJ; a value prefixed
# with json: is parsed as JSON (lists, booleans).
pj() {
    python3 -c '
import json, sys
tool, cwd, pairs = sys.argv[1], sys.argv[2], sys.argv[3:]
ti = {}
for pair in pairs:
    k, v = pair.split("=", 1)
    ti[k] = json.loads(v[5:]) if v.startswith("json:") else v
print(json.dumps({"tool_name": tool, "tool_input": ti, "cwd": cwd}))' "$1" "$PROJ" "${@:2}"
}

ok() { echo "PASS: $1"; passes=$((passes + 1)); }
bad() { echo "FAIL: $1"; fail=1; }

expect_allow() { # <platform> <name> <json>
    run "$1" "$3"
    if [ "$rc" = 0 ] && [ ! -s "$OUT" ]; then ok "$2"; else bad "$2 (rc=$rc out=$(cat "$OUT") err=$(cat "$ERR"))"; fi
}
expect_deny() { # <platform> <name> <json>: denied with the size-limit reason and the eng-init hint
    run "$1" "$3"
    if [ "$1" = claude ]; then
        if [ "$rc" = 0 ] && grep -q '"permissionDecision": "deny"' "$OUT" && grep -q "size limit" "$OUT" && grep -q "eng-init" "$OUT"; then
            ok "$2"
        else bad "$2 (rc=$rc out=$(cat "$OUT"))"; fi
    elif [ "$rc" = 2 ] && grep -q "size limit" "$ERR" && grep -q "eng-init" "$ERR"; then
        ok "$2"
    else bad "$2 (rc=$rc err=$(cat "$ERR"))"; fi
}

long_ascii=$(printf 'x%.0s' $(seq 1 400))
long_ascii2=$(printf 'w%.0s' $(seq 1 400))
ok_ascii=$(printf 'y%.0s' $(seq 1 300))
long_cjk=$(printf '规%.0s' $(seq 1 110)) # 110 chars, 330 bytes

# Root instruction files are over the line limit, so any write the guard cannot
# compute is denied there: that makes the shell parser observable.
printf '# Rules\n%s\n' "$long_ascii" > "$PROJ/AGENTS.md"
printf '# Rules\n%s\n' "$long_ascii" > "$PROJ/CLAUDE.md"
mkdir -p "$PROJ/docs" "$PROJ/other" "$PROJ/clean"
printf '# Rules\n%s\n' "$long_ascii" > "$PROJ/docs/AGENTS.md"
printf '# Rules\nAlways write tests.\n- src/a.ts\n' > "$PROJ/clean/AGENTS.md"
C=clean/AGENTS.md

# --- shell: reads pass ------------------------------------------------------
expect_allow claude "cat | head passes" "$(json Bash command 'cat AGENTS.md | head -20')"
expect_allow claude "grep with 2>/dev/null passes" "$(json Bash command 'grep -n rule CLAUDE.md 2>/dev/null')"
expect_allow claude "git diff passes" "$(json Bash command 'git diff -- AGENTS.md')"
expect_allow claude "sed -n passes" "$(json Bash command "sed -n '1,20p' AGENTS.md")"
expect_allow claude "grep for the word install passes" "$(json Bash command 'grep -n "install" AGENTS.md')"
expect_allow claude "grep for a quoted => passes" "$(json Bash command 'grep -rn "=>" CLAUDE.md')"
expect_allow claude "rg for rm -rf passes" "$(json Bash command 'rg "rm -rf" AGENTS.md')"
expect_allow claude "grep piped to head passes" "$(json Bash command 'grep -n "cp " AGENTS.md | head')"
expect_allow claude "grep -c touch passes" "$(json Bash command 'grep -c touch AGENTS.md')"
expect_allow claude "awk print passes" "$(json Bash command "awk '{print \$1}' AGENTS.md")"
expect_allow claude "cp AGENTS.md elsewhere passes" "$(json Bash command 'cp AGENTS.md /tmp/agents-copy.md')"
expect_allow claude "interpreter without inline code passes" "$(json Bash command 'node --version && cat AGENTS.md')"
expect_allow claude "find -exec cat passes" "$(json Bash command 'find . -name AGENTS.md -exec cat {} \;')"
expect_allow claude "read inside command substitution passes" "$(json Bash command 'echo "$(cat AGENTS.md)" | wc -l')"
expect_allow claude "write elsewhere passes" "$(json Bash command 'echo x > notes.txt')"
expect_allow claude "AGENTS.md.bak is not guarded" "$(json Bash command 'echo x > AGENTS.md.bak')"
expect_allow claude "MY_AGENTS.md is not guarded" "$(json Bash command 'echo x > MY_AGENTS.md')"
expect_allow claude "shell write to a file within the limits passes" "$(json Bash command "echo x >> $C")"

# --- shell: writes to an over-limit file are denied --------------------------
expect_deny claude "heredoc into CLAUDE.md" "$(json Bash command "cat > CLAUDE.md <<'EOF'
x
EOF")"
expect_deny claude "append to AGENTS.md" "$(json Bash command 'echo rule >> AGENTS.md')"
expect_deny claude "append without spaces" "$(json Bash command 'echo x>>AGENTS.md')"
expect_deny claude "sed -i" "$(json Bash command "sed -i '' 's/a/b/' AGENTS.md")"
expect_deny claude "git checkout of CLAUDE.md" "$(json Bash command 'git checkout -- CLAUDE.md')"
expect_deny claude "python heredoc naming AGENTS.md" "$(json Bash command "python3 - <<'EOF'
open('AGENTS.md','w').write('x')
EOF")"
expect_deny claude "prettier --write" "$(json Bash command 'npx prettier --write AGENTS.md')"
expect_deny claude "tee -a after 2>&1" "$(json Bash command 'make 2>&1 | tee -a CLAUDE.md')"
expect_deny claude "cp onto AGENTS.md" "$(json Bash command 'cp README.md docs/AGENTS.md')"
expect_deny claude "cp into a directory as AGENTS.md" "$(json Bash command 'cp other/AGENTS.md .')"
expect_deny claude "mv AGENTS.md away" "$(json Bash command 'mv AGENTS.md old.md')"
expect_deny claude "rm with a glob matching AGENTS.md" "$(json Bash command 'rm *.md')"
expect_deny claude "loop variable write" "$(json Bash command 'for f in AGENTS.md CLAUDE.md; do echo x >> "$f"; done')"
expect_deny claude "bash -c write" "$(json Bash command 'bash -c "echo x > AGENTS.md"')"
expect_deny claude "write inside quoted command substitution" "$(json Bash command "echo \"\$(sed -i '' s/a/b/ AGENTS.md)\"")"
expect_deny claude "find -delete" "$(json Bash command 'find . -name CLAUDE.md -delete')"
expect_deny claude "find -exec sed -i" "$(json Bash command "find . -name AGENTS.md -exec sed -i '' s/a/b/ {} +")"
expect_deny claude "process substitution tee" "$(json Bash command 'cat notes > >(tee AGENTS.md)')"
expect_deny claude "python -c naming AGENTS.md" "$(json Bash command "python3 -c \"open('AGENTS.md','w')\"")"
expect_deny claude "patch on AGENTS.md" "$(json Bash command 'diff -u a b | patch AGENTS.md')"
expect_deny claude "unbalanced quote falls back to the coarse check" "$(json Bash command 'echo "x > AGENTS.md')"
run claude "$(json Bash command 'cd docs && echo x > AGENTS.md')"
if grep -q "$PROJ/docs/AGENTS.md" "$OUT"; then ok "cd is followed when resolving the target"; else bad "cd is followed when resolving the target (out=$(cat "$OUT"))"; fi

# --- file tools: the resulting file is checked --------------------------------
expect_allow claude "Edit adding a short line passes" "$(pj Edit file_path=$C 'old_string=- src/a.ts' $'new_string=- src/a.ts\n- src/b.ts')"
expect_deny claude "Edit adding a 400-byte line" "$(pj Edit file_path=$C 'old_string=- src/a.ts' "new_string=- $long_ascii")"
expect_deny claude "Edit adding a CJK line over 307 bytes" "$(pj Edit file_path=$C 'old_string=- src/a.ts' "new_string=- $long_cjk")"
expect_allow claude "Edit adding a 302-byte line passes" "$(pj Edit file_path=$C 'old_string=- src/a.ts' "new_string=- $ok_ascii")"
expect_allow claude "Edit with a missing old_string passes (the tool fails by itself)" "$(pj Edit file_path=$C 'old_string=not there' 'new_string=x')"
expect_deny claude "Write of a new AGENTS.md over 32768 bytes" \
    "$(pj Write file_path=fresh/AGENTS.md "content=$(head -c 40000 /dev/zero | tr '\0' 'a' | fold -w 200)")"
expect_allow claude "Write within the limits passes" "$(pj Write file_path=fresh/CLAUDE.md $'content=@AGENTS.md\n')"
expect_deny claude "MultiEdit with one long line" \
    "$(pj MultiEdit file_path=$C "edits=json:[{\"old_string\": \"- src/a.ts\", \"new_string\": \"- $long_ascii\"}]")"
expect_allow claude "Write to README.md is not guarded" "$(pj Write file_path=README.md "content=$long_ascii")"

# --- old content counts: a file already over must be fixed first ---------------
mkdir -p "$PROJ/limits" "$PROJ/big"
printf '# Rules\n%s\n- a.md\n' "$long_ascii" > "$PROJ/limits/AGENTS.md"
printf '# Rules\n%s\n%s\n' "$long_ascii" "$long_ascii2" > "$PROJ/limits/CLAUDE.md"
L=limits/AGENTS.md
expect_deny claude "an old long line blocks an unrelated edit" "$(pj Edit file_path=$L 'old_string=- a.md' 'new_string=- b.md')"
expect_deny claude "rewriting the old long line still too long" "$(pj Edit file_path=$L "old_string=$long_ascii" "new_string=${long_ascii}z")"
expect_allow claude "splitting the old long line passes" "$(pj Edit file_path=$L "old_string=$long_ascii" $'new_string=short one\nshort two')"
expect_allow claude "fixing one of two old long lines is progress" "$(pj Edit file_path=limits/CLAUDE.md "old_string=$long_ascii" 'new_string=short')"
expect_deny claude "swapping an old long line for a new long line" \
    "$(pj Edit file_path=limits/CLAUDE.md "old_string=$long_ascii" "new_string=$ok_ascii$ok_ascii")"
python3 -c 'import sys; open(sys.argv[1], "w").write("".join(f"{i:05d} " + "b" * 94 + "\n" for i in range(330)))' "$PROJ/big/AGENTS.md"
first=$(head -1 "$PROJ/big/AGENTS.md")
expect_deny claude "growing a file already over 32768 bytes" "$(pj Edit file_path=big/AGENTS.md "old_string=$first" "new_string=${first}c")"
expect_allow claude "shrinking an oversize file is progress" "$(pj Edit file_path=big/AGENTS.md "old_string=$first" 'new_string=short')"

# --- Codex: apply_patch payload shape captured from codex-cli 0.158 -----------
patch_ok="*** Begin Patch
*** Update File: $C
@@
 Always write tests.
 - src/a.ts
+- src/c.ts
*** End Patch"
patch_long="*** Begin Patch
*** Update File: $C
@@
-- src/a.ts
+- $long_ascii
*** End Patch"
patch_old="*** Begin Patch
*** Update File: $L
@@
-- a.md
+- b.md
*** End Patch"
patch_insert_only="*** Begin Patch
*** Update File: $L
@@
+- b.md
*** End Patch"
patch_add_long="*** Begin Patch
*** Add File: newdir/AGENTS.md
+$long_ascii
*** End Patch"
patch_delete="*** Begin Patch
*** Delete File: $L
*** End Patch"
expect_allow codex "codex apply_patch within the limits passes" "$(json apply_patch command "$patch_ok")"
expect_deny codex "codex apply_patch adding a long line" "$(json apply_patch command "$patch_long")"
expect_deny codex "codex apply_patch on a file with an old long line" "$(json apply_patch command "$patch_old")"
expect_deny codex "codex insertion-only hunk on an over-limit file (not computable)" "$(json apply_patch command "$patch_insert_only")"
expect_deny codex "codex Add File with a long line" "$(json apply_patch command "$patch_add_long")"
expect_allow codex "codex Delete File of an over-limit file passes" "$(json apply_patch command "$patch_delete")"
expect_deny codex "codex Bash redirect into an over-limit AGENTS.md" "$(json Bash command 'echo x > AGENTS.md')"
expect_allow codex "codex Bash read passes" "$(json Bash command 'cat AGENTS.md')"

# --- omp: shim payloads (full tool input) --------------------------------------
expect_allow omp "omp write within the limits passes" "$(pj write path=$C $'content=# Rules\n- a\n')"
expect_deny omp "omp write with a long line" "$(pj write path=$C "content=$long_ascii")"
expect_deny omp "omp replace-mode edit adding a long line" "$(pj edit path=$C 'old_string=- src/a.ts' "new_string=- $long_ascii")"
expect_deny omp "omp apply_patch-mode edit adding a long line" "$(pj edit "input=$patch_long")"
expect_allow omp "omp hashline edit of a file within the limits passes" "$(pj edit "input=[$C#AB12]"$'\n''~3 replace')"
expect_deny omp "omp hashline edit of an over-limit file" "$(pj edit "input=[$L#AB12]"$'\n''~3 replace')"
# captured from omp 18.13.1: hashline edit wrapped in a patch envelope
expect_deny omp "omp hashline edit inside a Begin Patch envelope" \
    "$(pj edit $'input=*** Begin Patch\n[AGENTS.md#5F31]\nPUT 6.=6:\n+Never push to main or release.\n*** End Patch\n' path=AGENTS.md 'paths=json:["AGENTS.md"]')"
expect_deny omp "omp edit naming the target only in path" "$(pj edit $'input=~3 replace' path=AGENTS.md)"
expect_deny omp "omp legacy paths list" "$(pj edit 'paths=json:["CLAUDE.md"]')"
expect_allow omp "omp edit of another file passes" "$(pj edit $'input=[README.md#AB12]\n~3 replace')"

# --- configuration, check, robustness ---------------------------------------
rc=0
printf '%s' "$(pj Edit file_path=$C 'old_string=- src/a.ts' "new_string=- $long_ascii")" | INSTRUCTION_GUARD_MAX_LINE_BYTES=1000 \
    CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" --platform claude >"$OUT" 2>"$ERR" || rc=$?
if [ "$rc" = 0 ] && [ ! -s "$OUT" ]; then ok "INSTRUCTION_GUARD_MAX_LINE_BYTES raises the line limit"; else bad "INSTRUCTION_GUARD_MAX_LINE_BYTES raises the line limit (out=$(cat "$OUT"))"; fi
rc=0
printf '%s' "$(pj Write file_path=fresh3/AGENTS.md $'content=0123456789\n')" | INSTRUCTION_GUARD_MAX_BYTES=5 \
    CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" --platform claude >"$OUT" 2>"$ERR" || rc=$?
if grep -q '"permissionDecision": "deny"' "$OUT"; then ok "INSTRUCTION_GUARD_MAX_BYTES lowers the file limit"; else bad "INSTRUCTION_GUARD_MAX_BYTES lowers the file limit (out=$(cat "$OUT"))"; fi

rc=0
bash "$HOOK" check "$PROJ/limits" "$PROJ/big" >"$OUT" 2>&1 || rc=$?
if [ "$rc" = 1 ] && grep -q "limits/AGENTS.md: line 2 is 400 bytes" "$OUT" && grep -q "big/AGENTS.md: 33330 bytes" "$OUT" \
    && grep -q "3 file(s), 3 over the limits" "$OUT"; then ok "check reports old violations"; else bad "check reports old violations (rc=$rc out=$(cat "$OUT"))"; fi
rc=0
(cd "$PROJ/clean" && bash "$HOOK" check) >"$OUT" 2>&1 || rc=$?
if [ "$rc" = 0 ] && grep -q "1 file(s), 0 over the limits" "$OUT"; then ok "check passes clean files"; else bad "check passes clean files (rc=$rc out=$(cat "$OUT"))"; fi

expect_allow claude "malformed JSON passes" "not json"
mkdir -p "$PROJ/shadow" && printf 'raise SystemExit(0)\n' > "$PROJ/shadow/json.py"
printf '%s\n' "$long_ascii" > "$PROJ/shadow/CLAUDE.md"
rc=0
printf '%s' "$(json Bash command 'echo x >> shadow/CLAUDE.md')" \
    | (cd "$PROJ/shadow" && CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" --platform codex) >/dev/null 2>&1 || rc=$?
if [ "$rc" = 2 ]; then ok "a stray json.py in cwd cannot disable the guard"; else bad "a stray json.py in cwd cannot disable the guard (rc=$rc)"; fi

echo "passes: $passes"
if [ "$fail" = 0 ]; then
    echo "summary: ALL CHECKS PASSED"
else
    echo "summary: FAILURES"
    exit 1
fi

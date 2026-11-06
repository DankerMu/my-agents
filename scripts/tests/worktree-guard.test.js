const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");

const suitePath = path.join(
  __dirname,
  "..",
  "..",
  "hooks",
  "worktree-guard",
  "tests",
  "test-worktree-guard.sh"
);

test("worktree-guard shell suite passes (claude file tools, codex apply_patch headers, omp)", () => {
  const result = spawnSync("bash", [suitePath], {
    cwd: path.join(__dirname, "..", ".."),
    encoding: "utf8",
    timeout: 120000
  });

  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.match(result.stdout, /summary: ALL CHECKS PASSED/);
  assert.doesNotMatch(result.stdout, /^FAIL:/m);
});

const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");

const suitePath = path.join(
  __dirname,
  "..",
  "..",
  "hooks",
  "instruction-guard",
  "tests",
  "test-instruction-guard.sh"
);

test("instruction-guard shell suite passes (claude ask, codex/omp deny + one-shot approval)", () => {
  const result = spawnSync("bash", [suitePath], {
    cwd: path.join(__dirname, "..", ".."),
    encoding: "utf8",
    timeout: 120000
  });

  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.match(result.stdout, /summary: ALL CHECKS PASSED/);
  assert.doesNotMatch(result.stdout, /^FAIL:/m);
});

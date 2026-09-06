const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");

const suitePath = path.join(
  __dirname,
  "..",
  "..",
  "hooks",
  "large-file-guard",
  "tests",
  "test-large-file-guard.sh"
);

test("large-file-guard shell suite passes (commit, merge --continue, cwd root, path bytes)", () => {
  const result = spawnSync("bash", [suitePath], {
    cwd: path.join(__dirname, "..", ".."),
    encoding: "utf8",
    timeout: 120000
  });

  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.match(result.stdout, /summary: ALL CHECKS PASSED/);
  assert.doesNotMatch(result.stdout, /^FAIL:/m);
});

const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");

const { getSkillTargets } = require("../lib/runtime-targets");

function destFor(targets, platformKey) {
  const target = targets.find((entry) => entry.platformKey === platformKey);
  assert.ok(target, `expected a ${platformKey} target`);
  return target.destDir;
}

test("codex skill target defaults to .agents/skills", () => {
  const targets = getSkillTargets("demo", ["claude", "codex"], "project");
  assert.equal(destFor(targets, "codex"), path.join(process.cwd(), ".agents", "skills", "demo"));
  assert.equal(destFor(targets, "claude"), path.join(process.cwd(), ".claude", "skills", "demo"));
});

test("user-invoked skills route codex to .agents/skills-manual", () => {
  const targets = getSkillTargets("demo", ["claude", "codex"], "project", {
    userInvoked: true
  });
  assert.equal(
    destFor(targets, "codex"),
    path.join(process.cwd(), ".agents", "skills-manual", "demo")
  );
  assert.equal(
    destFor(targets, "claude"),
    path.join(process.cwd(), ".claude", "skills", "demo"),
    "claude target must not change: disable-model-invocation is honored natively"
  );
});

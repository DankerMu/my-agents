const test = require("node:test");
const assert = require("node:assert/strict");
const os = require("node:os");
const path = require("node:path");

const { getSkillTargets, getAgentTargets } = require("../lib/runtime-targets");

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

test("omp skill target is scope-shaped: project .omp/skills, user ~/.omp/agent/skills", () => {
  const projectTargets = getSkillTargets("demo", ["omp"], "project");
  assert.equal(destFor(projectTargets, "omp"), path.join(process.cwd(), ".omp", "skills", "demo"));

  const userTargets = getSkillTargets("demo", ["omp"], "user");
  assert.equal(
    destFor(userTargets, "omp"),
    path.join(os.homedir(), ".omp", "agent", "skills", "demo")
  );
});

test("omp skill target ignores the user-invoked flag: omp honors the frontmatter natively", () => {
  const targets = getSkillTargets("demo", ["omp"], "project", { userInvoked: true });
  assert.equal(destFor(targets, "omp"), path.join(process.cwd(), ".omp", "skills", "demo"));
});

test("omp agent target lands in .omp/agents with references support dir", () => {
  const [target] = getAgentTargets("demo", ["omp"], "project");
  assert.equal(target.srcFile, "omp.md");
  assert.equal(target.destPath, path.join(process.cwd(), ".omp", "agents", "demo.md"));
  assert.equal(
    target.referencesDestDir,
    path.join(process.cwd(), ".omp", "agents", "demo", "references")
  );

  const [userTarget] = getAgentTargets("demo", ["omp"], "user");
  assert.equal(userTarget.destPath, path.join(os.homedir(), ".omp", "agent", "agents", "demo.md"));
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

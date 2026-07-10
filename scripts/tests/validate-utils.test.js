const test = require("node:test");
const assert = require("node:assert/strict");

const {
  collectNestedPlatformAgentWarnings,
  getPlatformAgentRefs,
  validateEmbeddedSkillVersion
} = require("../lib/validate-utils");

test("validateEmbeddedSkillVersion accepts top-level and nested versions", () => {
  const topLevel = `---\nname: demo\nversion: 1.2.3\n---\n# Demo\n`;
  const nested = `---\nname: demo\nmetadata:\n  version: "1.2.3"\n---\n# Demo\n`;

  assert.deepEqual(validateEmbeddedSkillVersion(topLevel, "1.2.3"), []);
  assert.deepEqual(validateEmbeddedSkillVersion(nested, "1.2.3"), []);
});

test("validateEmbeddedSkillVersion rejects missing, duplicate, and stale versions", () => {
  const missing = `---\nname: demo\n---\n# Demo\n`;
  const duplicate = `---\nname: demo\nversion: 1.2.3\nmetadata:\n  version: 1.2.3\n---\n# Demo\n`;
  const stale = `---\nname: demo\nmetadata:\n  version: 1.2.2\n---\n# Demo\n`;

  assert.match(validateEmbeddedSkillVersion(missing, "1.2.3")[0], /must declare version/);
  assert.match(validateEmbeddedSkillVersion(duplicate, "1.2.3")[0], /multiple versions/);
  assert.match(validateEmbeddedSkillVersion(stale, "1.2.3")[0], /does not match/);
});

test("getPlatformAgentRefs returns explicit platform-specific agent refs", () => {
  const agent = {
    agents: ["reviewer"],
    platformDependencies: {
      "claude-code": {
        agents: ["triager", "coder"]
      }
    }
  };

  assert.deepEqual(getPlatformAgentRefs(agent, "claude-code"), ["triager", "coder"]);
  assert.deepEqual(getPlatformAgentRefs(agent, "codex"), []);
});

test("collectNestedPlatformAgentWarnings only warns on nested refs declared for that platform", () => {
  const claudeGraph = new Map([
    ["controller", ["reviewer", "planner"]],
    ["reviewer", []],
    ["planner", []],
    ["explorer", []]
  ]);

  assert.deepEqual(
    collectNestedPlatformAgentWarnings(claudeGraph, {
      platformKey: "claude-code",
      platformLabel: "Claude Code"
    }),
    []
  );
});

test("collectNestedPlatformAgentWarnings reports second-level Claude Code agent graphs", () => {
  const claudeGraph = new Map([
    ["controller", ["reviewer"]],
    ["reviewer", ["explorer"]],
    ["explorer", []]
  ]);

  const warnings = collectNestedPlatformAgentWarnings(claudeGraph, {
    platformKey: "claude-code",
    platformLabel: "Claude Code"
  });

  assert.equal(warnings.length, 1);
  assert.match(
    warnings[0],
    /agents\/controller\/agent\.json: platformDependencies\["claude-code"\]\.agents references agent "reviewer".*Claude Code only supports one level of subagent nesting/
  );
});

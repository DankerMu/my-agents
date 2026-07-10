const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const { expectedAgentProjections, validateContractContent } = require("../lib/agent-contract");
const { scaffoldAgent } = require("../new");

test("agent scaffold creates fresh Claude and Codex contract projections", async () => {
  const repoRoot = await fs.mkdtemp(path.join(os.tmpdir(), "agent-scaffold-test-"));

  try {
    await scaffoldAgent(repoRoot, "demo-agent");

    const agentDir = path.join(repoRoot, "agents", "demo-agent");
    const expected = await expectedAgentProjections(agentDir);
    assert.deepEqual(validateContractContent(expected.contractContent), []);

    for (const [projectionPath, projectedContent] of expected.projections) {
      assert.equal(await fs.readFile(projectionPath, "utf8"), projectedContent);
    }
  } finally {
    await fs.rm(repoRoot, { recursive: true, force: true });
  }
});

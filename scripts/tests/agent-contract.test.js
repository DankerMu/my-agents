const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const {
  renderClaudeProjection,
  renderCodexProjection,
  validateAgentContractPackage,
  validateContractContent
} = require("../lib/agent-contract");

const contract = `# demo Contract

- Handle only the assigned read-only investigation and keep the scope narrow.
- Inspect repository evidence before drawing conclusions or reporting findings.
- Cite concrete files and distinguish confirmed facts from unresolved hypotheses.
- Return a concise evidence map, risks, and open questions for the parent agent.
- Never edit files, run destructive commands, or claim evidence that was not inspected.
- For exact templates, read {{agent_references}}/operating-guide.md.
`;

test("agent contract renders identical behavior into Claude and Codex projections", () => {
  const claude = renderClaudeProjection(
    `---\nname: demo\ndescription: Demo agent.\ntools: Read\n---\n\nOld body.\n`,
    contract
  );
  const codex = renderCodexProjection(
    `name = "demo"\ndescription = "Demo agent."\ndeveloper_instructions = """\nOld body.\n"""\n`,
    contract
  );

  assert.equal(
    claude,
    `---\nname: demo\ndescription: Demo agent.\ntools: Read\n---\n\n${contract}`
  );
  assert.match(
    codex,
    /developer_instructions = """\n# demo Contract[\s\S]*operating-guide\.md\.\n"""/
  );
});

test("agent contract enforces the concise 5-8 bullet budget", () => {
  assert.deepEqual(validateContractContent(contract), []);
  assert.match(validateContractContent("# Demo\n\n- one\n- two\n")[0], /too short|5-8/);
});

test("agent package validation detects stale projections and missing references", async () => {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "agent-contract-test-"));
  const agentDir = path.join(tmp, "agents", "demo");

  try {
    await fs.mkdir(agentDir, { recursive: true });
    await fs.writeFile(
      path.join(agentDir, "agent.json"),
      '{"entrypoints":{"contract":"AGENT.md"}}\n',
      "utf8"
    );
    await fs.writeFile(path.join(agentDir, "AGENT.md"), contract, "utf8");
    await fs.writeFile(
      path.join(agentDir, "claude-code.md"),
      `---\nname: demo\ndescription: Demo agent.\ntools: Read\n---\n\nStale body.\n`,
      "utf8"
    );

    const errors = await validateAgentContractPackage(agentDir);

    assert.ok(
      errors.some((error) => /operating-guide\.md is missing/.test(error)),
      errors
    );
    assert.ok(
      errors.some((error) => /projection is out of date/.test(error)),
      errors
    );
  } finally {
    await fs.rm(tmp, { recursive: true, force: true });
  }
});

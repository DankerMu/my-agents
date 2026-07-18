const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const { installAgent, uninstallAgent } = require("../lib/install-runtime");

test("agent install materializes reference paths and uninstall removes support files", async () => {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "agent-install-test-"));
  const repoRoot = path.join(tmp, "repo");
  const projectRoot = path.join(tmp, "project");
  const agentDir = path.join(repoRoot, "agents", "demo");
  const originalCwd = process.cwd();

  try {
    await fs.mkdir(path.join(agentDir, "references"), { recursive: true });
    await fs.mkdir(projectRoot, { recursive: true });
    await fs.writeFile(
      path.join(agentDir, "claude-code.md"),
      "---\nname: demo\n---\n\nRead {{agent_references}}/operating-guide.md.\n",
      "utf8"
    );
    await fs.writeFile(
      path.join(agentDir, "codex.toml"),
      'name = "demo"\ndeveloper_instructions = """\nRead {{agent_references}}/operating-guide.md.\n"""\n',
      "utf8"
    );
    await fs.writeFile(
      path.join(agentDir, "omp.md"),
      "---\nname: demo\ndescription: Demo.\ntools: read\n---\n\nRead {{agent_references}}/operating-guide.md.\n",
      "utf8"
    );
    await fs.writeFile(
      path.join(agentDir, "references", "operating-guide.md"),
      "# Guide\n\nInstalled reference content.\n",
      "utf8"
    );

    process.chdir(projectRoot);
    assert.equal(await installAgent(repoRoot, "demo", ["claude", "codex", "omp"], "project"), true);

    const claudeDefinition = await fs.readFile(
      path.join(projectRoot, ".claude", "agents", "demo.md"),
      "utf8"
    );
    const codexDefinition = await fs.readFile(
      path.join(projectRoot, ".codex", "agents", "demo.toml"),
      "utf8"
    );
    const ompDefinition = await fs.readFile(
      path.join(projectRoot, ".omp", "agents", "demo.md"),
      "utf8"
    );
    assert.doesNotMatch(claudeDefinition, /\{\{agent_references\}\}/);
    assert.doesNotMatch(codexDefinition, /\{\{agent_references\}\}/);
    assert.doesNotMatch(ompDefinition, /\{\{agent_references\}\}/);
    await fs.access(
      path.join(projectRoot, ".claude", "agents", "demo", "references", "operating-guide.md")
    );
    await fs.access(
      path.join(projectRoot, ".codex", "agents", "demo", "references", "operating-guide.md")
    );
    await fs.access(
      path.join(projectRoot, ".omp", "agents", "demo", "references", "operating-guide.md")
    );

    assert.equal(await uninstallAgent("demo", ["claude", "codex", "omp"], "project"), true);
    await assert.rejects(fs.access(path.join(projectRoot, ".claude", "agents", "demo.md")));
    await assert.rejects(fs.access(path.join(projectRoot, ".claude", "agents", "demo")));
    await assert.rejects(fs.access(path.join(projectRoot, ".codex", "agents", "demo.toml")));
    await assert.rejects(fs.access(path.join(projectRoot, ".codex", "agents", "demo")));
    await assert.rejects(fs.access(path.join(projectRoot, ".omp", "agents", "demo.md")));
    await assert.rejects(fs.access(path.join(projectRoot, ".omp", "agents", "demo")));
  } finally {
    process.chdir(originalCwd);
    await fs.rm(tmp, { recursive: true, force: true });
  }
});

const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const { generateCatalogSnapshot, renderAgentsMarkdown } = require("../lib/catalog");

test("renderAgentsMarkdown links to the canonical agent contract", () => {
  const markdown = renderAgentsMarkdown([
    {
      name: "demo-agent",
      path: "agents/demo-agent",
      version: "0.1.0",
      maturity: "experimental",
      archetype: "custom",
      platforms: ["claude-code", "codex"],
      categories: ["workflow"],
      description: "Demo agent."
    }
  ]);

  assert.match(markdown, /\[demo-agent\]\(\.\.\/\.\.\/agents\/demo-agent\/AGENT\.md\)/);
});

test("renderAgentsMarkdown uses the canonical contract for a Codex-only agent", () => {
  const markdown = renderAgentsMarkdown([
    {
      name: "codex-only-agent",
      path: "agents/codex-only-agent",
      version: "0.1.0",
      maturity: "experimental",
      archetype: "custom",
      platforms: ["codex"],
      categories: ["workflow"],
      description: "Codex-only demo agent."
    }
  ]);

  assert.match(markdown, /\[codex-only-agent\]\(\.\.\/\.\.\/agents\/codex-only-agent\/AGENT\.md\)/);
});

test("catalog generation rejects canonical package directories without metadata", async () => {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "catalog-metadata-test-"));

  try {
    for (const root of ["skills", "agents", "hooks", "packs"]) {
      await fs.mkdir(path.join(tmp, root), { recursive: true });
    }
    await fs.mkdir(path.join(tmp, "skills", "metadata-less"), { recursive: true });

    await assert.rejects(
      generateCatalogSnapshot(tmp),
      /Missing skill metadata: skills\/metadata-less\/skill\.json/
    );
  } finally {
    await fs.rm(tmp, { recursive: true, force: true });
  }
});

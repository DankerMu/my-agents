const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const {
  appendProjectManifestEntry,
  readWritableProjectManifest
} = require("../lib/project-manifest-write");

async function createTempManifestPath() {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "my-agents-manifest-test-"));
  return {
    tempDir,
    manifestPath: path.join(tempDir, "my-agents.project.json")
  };
}

test("creates a project manifest when adding the first external entry", async () => {
  const { tempDir, manifestPath } = await createTempManifestPath();

  try {
    await appendProjectManifestEntry(
      "skills",
      {
        source: "official",
        provider: "github",
        platform: "claude",
        name: "agentic-engineering",
        repo: "affaan-m/everything-claude-code",
        declaredRef: "main",
        resolvedCommit: "0123456789abcdef0123456789abcdef01234567",
        path: "skills/agentic-engineering",
        sourceUrl:
          "https://github.com/affaan-m/everything-claude-code/tree/main/skills/agentic-engineering"
      },
      manifestPath
    );

    const { manifest } = await readWritableProjectManifest(manifestPath);
    assert.equal(manifest.schemaVersion, 1);
    assert.deepEqual(manifest.packs, []);
    assert.equal(manifest.skills.length, 1);
    assert.deepEqual(manifest.agents, []);
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
});

test("preserves existing local entries when appending an external entry", async () => {
  const { tempDir, manifestPath } = await createTempManifestPath();

  try {
    await fs.writeFile(
      manifestPath,
      `${JSON.stringify(
        {
          schemaVersion: 1,
          packs: [],
          skills: ["brainstorming"],
          agents: []
        },
        null,
        2
      )}\n`,
      "utf8"
    );

    await appendProjectManifestEntry(
      "agents",
      {
        source: "official",
        provider: "github",
        platform: "codex",
        name: "api-designer",
        repo: "VoltAgent/awesome-codex-subagents",
        declaredRef: "main",
        resolvedCommit: "0123456789abcdef0123456789abcdef01234567",
        path: "categories/01-core-development/api-designer.toml",
        sourceUrl:
          "https://github.com/VoltAgent/awesome-codex-subagents/blob/main/categories/01-core-development/api-designer.toml"
      },
      manifestPath
    );

    const { manifest } = await readWritableProjectManifest(manifestPath);
    assert.deepEqual(manifest.skills, ["brainstorming"]);
    assert.equal(manifest.agents.length, 1);
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
});

test("rejects duplicate external entries by canonical identity", async () => {
  const { tempDir, manifestPath } = await createTempManifestPath();

  const entry = {
    source: "official",
    provider: "github",
    platform: "claude",
    name: "agentic-engineering",
    repo: "affaan-m/everything-claude-code",
    declaredRef: "main",
    resolvedCommit: "0123456789abcdef0123456789abcdef01234567",
    path: "skills/agentic-engineering",
    sourceUrl:
      "https://github.com/affaan-m/everything-claude-code/tree/main/skills/agentic-engineering"
  };

  try {
    await appendProjectManifestEntry("skills", entry, manifestPath);
    await assert.rejects(
      () => appendProjectManifestEntry("skills", entry, manifestPath),
      /already contains/
    );
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
});

test("an external skill can be added once per platform", async () => {
  const { tempDir, manifestPath } = await createTempManifestPath();
  const entry = {
    source: "official",
    provider: "github",
    platform: "claude",
    name: "remotion-best-practices",
    repo: "remotion-dev/skills",
    declaredRef: "main",
    resolvedCommit: "0123456789abcdef0123456789abcdef01234567",
    path: "skills/remotion-best-practices",
    sourceUrl: "https://github.com/remotion-dev/skills/tree/main/skills/remotion-best-practices"
  };

  try {
    await appendProjectManifestEntry("skills", entry, manifestPath);
    await appendProjectManifestEntry("skills", { ...entry, platform: "codex" }, manifestPath);
    await assert.rejects(
      appendProjectManifestEntry("skills", { ...entry, platform: "codex" }, manifestPath),
      /already contains this skill entry/
    );

    const { manifest } = await readWritableProjectManifest(manifestPath);
    assert.deepEqual(
      manifest.skills.map((item) => item.platform),
      ["claude", "codex"]
    );
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
});

test("the manifest schema accepts claude and codex external skills, not omp", async () => {
  const { readProjectManifest } = require("../lib/project-manifest");
  const repoRoot = path.join(__dirname, "..", "..");
  const { tempDir, manifestPath } = await createTempManifestPath();
  const entry = {
    source: "official",
    provider: "github",
    name: "remotion-best-practices",
    repo: "remotion-dev/skills",
    declaredRef: "main",
    resolvedCommit: "0123456789abcdef0123456789abcdef01234567",
    path: "skills/remotion-best-practices",
    sourceUrl: "https://github.com/remotion-dev/skills/tree/main/skills/remotion-best-practices"
  };
  const write = (platform) =>
    fs.writeFile(
      manifestPath,
      JSON.stringify({ schemaVersion: 1, skills: [{ ...entry, platform }] })
    );
  const originalError = console.error;
  console.error = () => {};

  try {
    for (const platform of ["claude", "codex"]) {
      await write(platform);
      const { manifest } = await readProjectManifest(repoRoot, manifestPath);
      assert.ok(manifest, `${platform} external skill must validate`);
    }

    await write("omp");
    const { manifest } = await readProjectManifest(repoRoot, manifestPath);
    assert.equal(manifest, null, "omp external skill must be rejected");
  } finally {
    console.error = originalError;
    await fs.rm(tempDir, { recursive: true, force: true });
  }
});

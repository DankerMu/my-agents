const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const { installHook, uninstallHook } = require("../lib/install-runtime");

const OMP_FACTORY = [
  "export default function hook(pi: any): void {",
  '  pi.on("tool_call", async () => {});',
  "}",
  ""
].join("\n");

test("omp hook install copies the factory and scripts; uninstall removes both", async () => {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "hook-install-test-"));
  const repoRoot = path.join(tmp, "repo");
  const projectRoot = path.join(tmp, "project");
  const hookDir = path.join(repoRoot, "hooks", "demo-guard");
  const originalCwd = process.cwd();

  try {
    await fs.mkdir(path.join(hookDir, "scripts"), { recursive: true });
    await fs.mkdir(projectRoot, { recursive: true });
    await fs.writeFile(path.join(hookDir, "omp.ts"), OMP_FACTORY, "utf8");
    await fs.writeFile(
      path.join(hookDir, "scripts", "demo-guard.sh"),
      "#!/usr/bin/env bash\nexit 0\n",
      "utf8"
    );

    process.chdir(projectRoot);
    assert.equal(await installHook(repoRoot, "demo-guard", ["omp"], "project"), true);

    const factory = await fs.readFile(
      path.join(projectRoot, ".omp", "hooks", "pre", "demo-guard.ts"),
      "utf8"
    );
    assert.equal(factory, OMP_FACTORY);
    await fs.access(path.join(projectRoot, ".omp", "hooks", "demo-guard", "demo-guard.sh"));

    assert.equal(await uninstallHook(repoRoot, "demo-guard", ["omp"], "project"), true);
    await assert.rejects(
      fs.access(path.join(projectRoot, ".omp", "hooks", "pre", "demo-guard.ts"))
    );
    await assert.rejects(fs.access(path.join(projectRoot, ".omp", "hooks", "demo-guard")));
  } finally {
    process.chdir(originalCwd);
    await fs.rm(tmp, { recursive: true, force: true });
  }
});

test("hook without an omp fragment fails an omp-only install", async () => {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "hook-install-test-"));
  const repoRoot = path.join(tmp, "repo");
  const projectRoot = path.join(tmp, "project");
  const hookDir = path.join(repoRoot, "hooks", "json-only");
  const originalCwd = process.cwd();

  try {
    await fs.mkdir(hookDir, { recursive: true });
    await fs.mkdir(projectRoot, { recursive: true });
    await fs.writeFile(
      path.join(hookDir, "claude-code.json"),
      '{"hooks":{"PreToolUse":[]}}\n',
      "utf8"
    );

    process.chdir(projectRoot);
    assert.equal(await installHook(repoRoot, "json-only", ["omp"], "project"), false);
    await assert.rejects(fs.access(path.join(projectRoot, ".omp")));
  } finally {
    process.chdir(originalCwd);
    await fs.rm(tmp, { recursive: true, force: true });
  }
});

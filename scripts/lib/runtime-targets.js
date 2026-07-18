const os = require("node:os");
const path = require("node:path");

function getScopeBase(scope) {
  return scope === "user" ? os.homedir() : process.cwd();
}

// omp keeps user-scope files under ~/.omp/agent/ but project-scope files under
// <project>/.omp/, so the omp base is scope-shaped instead of a plain prefix.
function getOmpBase(scope) {
  return scope === "user"
    ? path.join(os.homedir(), ".omp", "agent")
    : path.join(process.cwd(), ".omp");
}

// Skills flagged `disable-model-invocation: true` are user-invoked only. Codex
// has no such frontmatter key, so their Codex copy lands in `.agents/skills-manual/`
// (outside the scanned skills directory) instead of `.agents/skills/`.
function getSkillTargets(name, platforms, scope, options = {}) {
  const targets = [];
  const base = getScopeBase(scope);
  const codexDirName = options.userInvoked ? "skills-manual" : "skills";

  if (platforms.includes("claude")) {
    targets.push({
      platformKey: "claude",
      platform: "Claude Code",
      destDir: path.join(base, ".claude", "skills", name)
    });
  }

  if (platforms.includes("codex")) {
    targets.push({
      platformKey: "codex",
      platform: "Codex",
      destDir: path.join(base, ".agents", codexDirName, name)
    });
  }

  // omp honors `disable-model-invocation` natively (hidden from the system
  // prompt, still reachable via /skill:<name>), so user-invoked skills stay in
  // the scanned skills directory.
  if (platforms.includes("omp")) {
    targets.push({
      platformKey: "omp",
      platform: "omp",
      destDir: path.join(getOmpBase(scope), "skills", name)
    });
  }

  return targets;
}

function getAgentTargets(name, platforms, scope) {
  const targets = [];
  const base = getScopeBase(scope);

  if (platforms.includes("claude")) {
    targets.push({
      platform: "Claude Code",
      srcFile: "claude-code.md",
      destDir: path.join(base, ".claude", "agents"),
      destPath: path.join(base, ".claude", "agents", `${name}.md`),
      supportDestDir: path.join(base, ".claude", "agents", name),
      referencesDestDir: path.join(base, ".claude", "agents", name, "references")
    });
  }

  if (platforms.includes("codex")) {
    targets.push({
      platform: "Codex",
      srcFile: "codex.toml",
      destDir: path.join(base, ".codex", "agents"),
      destPath: path.join(base, ".codex", "agents", `${name}.toml`),
      supportDestDir: path.join(base, ".codex", "agents", name),
      referencesDestDir: path.join(base, ".codex", "agents", name, "references")
    });
  }

  if (platforms.includes("omp")) {
    const ompBase = getOmpBase(scope);
    targets.push({
      platform: "omp",
      srcFile: "omp.md",
      destDir: path.join(ompBase, "agents"),
      destPath: path.join(ompBase, "agents", `${name}.md`),
      supportDestDir: path.join(ompBase, "agents", name),
      referencesDestDir: path.join(ompBase, "agents", name, "references")
    });
  }

  return targets;
}

function getHookTargets(name, platforms, scope) {
  const targets = [];
  const base = getScopeBase(scope);

  if (platforms.includes("claude")) {
    targets.push({
      platformKey: "claude",
      platform: "Claude Code",
      fragmentFile: "claude-code.json",
      scriptsDestDir: path.join(base, ".claude", "hooks", name),
      configPath: path.join(base, ".claude", "settings.json")
    });
  }

  if (platforms.includes("codex")) {
    targets.push({
      platformKey: "codex",
      platform: "Codex",
      fragmentFile: "codex.json",
      scriptsDestDir: path.join(base, ".codex", "hooks", name),
      configPath: path.join(base, ".codex", "hooks.json")
    });
  }

  // omp has no hooks config file: it imports .ts/.js extension factories from
  // <config>/hooks/pre|post/. The omp.ts fragment is copied there verbatim and
  // resolves the shell scripts at ../<name>/ relative to itself. Directories
  // under hooks/ are never scanned, so the scripts dir is inert.
  if (platforms.includes("omp")) {
    const ompBase = getOmpBase(scope);
    targets.push({
      platformKey: "omp",
      platform: "omp",
      fragmentFile: "omp.ts",
      factoryDestPath: path.join(ompBase, "hooks", "pre", `${name}.ts`),
      scriptsDestDir: path.join(ompBase, "hooks", name)
    });
  }

  return targets;
}

function getExternalAssetTarget(kind, entry, scope) {
  const base = getScopeBase(scope);

  if (kind === "skills" && entry.platform === "claude") {
    return {
      platformKey: "claude",
      platform: "Claude Code",
      kind: "skills",
      destType: "directory",
      destPath: path.join(base, ".claude", "skills", entry.name)
    };
  }

  if (kind === "agents" && entry.platform === "claude") {
    return {
      platformKey: "claude",
      platform: "Claude Code",
      kind: "agents",
      destType: "file",
      destPath: path.join(base, ".claude", "agents", `${entry.name}.md`)
    };
  }

  if (kind === "agents" && entry.platform === "codex") {
    return {
      platformKey: "codex",
      platform: "Codex",
      kind: "agents",
      destType: "file",
      destPath: path.join(base, ".codex", "agents", `${entry.name}.toml`)
    };
  }

  throw new Error(`Unsupported external ${kind.slice(0, -1)} platform: ${entry.platform}`);
}

module.exports = {
  getExternalAssetTarget,
  getSkillTargets,
  getAgentTargets,
  getHookTargets
};

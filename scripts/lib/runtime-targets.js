const os = require("node:os");
const path = require("node:path");

function getScopeBase(scope) {
  return scope === "user" ? os.homedir() : process.cwd();
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

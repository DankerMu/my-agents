const path = require("node:path");

const { fileExists, readJson, listDirs } = require("./fs-utils");

const SKILLS_CATALOG_PATH = path.join("docs", "catalog", "skills.md");
const AGENTS_CATALOG_PATH = path.join("docs", "catalog", "agents.md");
const HOOKS_CATALOG_PATH = path.join("docs", "catalog", "hooks.md");
const PACKS_CATALOG_PATH = path.join("docs", "catalog", "packs.md");
const MACHINE_CATALOG_PATH = path.join("dist", "catalog.json");

function hasSuppressedCatalogTag(metadata) {
  return (metadata.tags ?? []).includes("issue-agent-os");
}

function isCatalogVisible(dirName, metadata) {
  return !hasSuppressedCatalogTag(metadata);
}

async function detectPlatforms(agentDir) {
  const platforms = [];
  if (await fileExists(path.join(agentDir, "claude-code.md"))) {
    platforms.push("claude-code");
  }
  if (await fileExists(path.join(agentDir, "codex.toml"))) {
    platforms.push("codex");
  }
  return platforms.sort();
}

async function detectHookPlatforms(hookDir) {
  const platforms = [];
  if (await fileExists(path.join(hookDir, "claude-code.json"))) {
    platforms.push("claude-code");
  }
  if (await fileExists(path.join(hookDir, "codex.json"))) {
    platforms.push("codex");
  }
  return platforms.sort();
}

function toSkillCatalogItem(skill, dirName) {
  return {
    name: skill.name,
    path: `skills/${dirName}`,
    displayName: skill.displayName,
    description: skill.description,
    version: skill.version,
    maturity: skill.maturity,
    categories: skill.categories,
    tags: skill.tags ?? []
  };
}

function toAgentCatalogItem(agent, dirName, platforms) {
  return {
    name: agent.name,
    path: `agents/${dirName}`,
    displayName: agent.displayName,
    description: agent.description,
    version: agent.version,
    maturity: agent.maturity,
    categories: agent.categories,
    tags: agent.tags ?? [],
    archetype: agent.archetype,
    skills: agent.skills ?? [],
    agents: agent.agents ?? [],
    platforms
  };
}

function toHookCatalogItem(hook, dirName, platforms) {
  return {
    name: hook.name,
    path: `hooks/${dirName}`,
    displayName: hook.displayName,
    description: hook.description,
    version: hook.version,
    maturity: hook.maturity,
    categories: hook.categories,
    tags: hook.tags ?? [],
    events: hook.events,
    platforms
  };
}

function toPackCatalogItem(pack, dirName) {
  return {
    name: pack.name,
    path: `packs/${dirName}`,
    displayName: pack.displayName,
    description: pack.description,
    version: pack.version,
    maturity: pack.maturity,
    packType: pack.packType,
    persona: pack.persona,
    categories: pack.categories,
    tags: pack.tags ?? [],
    skills: pack.skills ?? [],
    agents: pack.agents ?? [],
    hooks: pack.hooks ?? [],
    leadAgent: pack.leadAgent
  };
}

function renderSkillsMarkdown(items) {
  const header = [
    "# Skills Catalog",
    "",
    "> This file is generated. Run `npm run build`.",
    "",
    "| Name | Version | Maturity | Categories | Description |",
    "| --- | --- | --- | --- | --- |"
  ];

  const rows = items.map((item) => {
    const link = `[${item.name}](../../${item.path}/SKILL.md)`;
    const categories = (item.categories ?? []).join(", ");
    const desc = (item.description ?? "").replace(/\r?\n/g, " ");
    return `| ${link} | ${item.version} | ${item.maturity} | ${categories} | ${desc} |`;
  });

  return [...header, ...rows, ""].join("\n");
}

function renderAgentsMarkdown(items) {
  const header = [
    "# Agents Catalog",
    "",
    "> This file is generated. Run `npm run build`.",
    "",
    "| Name | Version | Maturity | Archetype | Platforms | Categories | Description |",
    "| --- | --- | --- | --- | --- | --- | --- |"
  ];

  const rows = items.map((item) => {
    const link = `[${item.name}](../../${item.path}/AGENT.md)`;
    const platforms = (item.platforms ?? []).join(", ");
    const categories = (item.categories ?? []).join(", ");
    const desc = (item.description ?? "").replace(/\r?\n/g, " ");
    return `| ${link} | ${item.version} | ${item.maturity} | ${item.archetype} | ${platforms} | ${categories} | ${desc} |`;
  });

  return [...header, ...rows, ""].join("\n");
}

function renderHooksMarkdown(items) {
  const header = [
    "# Hooks Catalog",
    "",
    "> This file is generated. Run `npm run build`.",
    "",
    "| Name | Version | Maturity | Events | Platforms | Categories | Description |",
    "| --- | --- | --- | --- | --- | --- | --- |"
  ];

  const rows = items.map((item) => {
    const link = `[${item.name}](../../${item.path}/HOOK.md)`;
    const events = (item.events ?? []).join(", ");
    const platforms = (item.platforms ?? []).join(", ");
    const categories = (item.categories ?? []).join(", ");
    const desc = (item.description ?? "").replace(/\r?\n/g, " ");
    return `| ${link} | ${item.version} | ${item.maturity} | ${events} | ${platforms} | ${categories} | ${desc} |`;
  });

  return [...header, ...rows, ""].join("\n");
}

function renderPacksMarkdown(items) {
  const header = [
    "# Packs Catalog",
    "",
    "> This file is generated. Run `npm run build`.",
    "",
    "| Name | Type | Version | Maturity | Categories | Members | Description |",
    "| --- | --- | --- | --- | --- | --- | --- |"
  ];

  const rows = items.map((item) => {
    const link = `[${item.name}](../../${item.path}/README.md)`;
    const categories = (item.categories ?? []).join(", ");
    const desc = (item.description ?? "").replace(/\r?\n/g, " ");
    const members = `${(item.skills ?? []).length} skills, ${(item.agents ?? []).length} agents, ${(item.hooks ?? []).length} hooks`;
    return `| ${link} | ${item.packType} | ${item.version} | ${item.maturity} | ${categories} | ${members} | ${desc} |`;
  });

  return [...header, ...rows, ""].join("\n");
}

async function collectSkillItems(repoRoot) {
  const skillDirs = await listDirs(path.join(repoRoot, "skills"));
  const skillItems = [];

  for (const dirName of skillDirs) {
    const skillJsonPath = path.join(repoRoot, "skills", dirName, "skill.json");
    if (!(await fileExists(skillJsonPath))) {
      throw new Error(`Missing skill metadata: skills/${dirName}/skill.json`);
    }
    const skill = await readJson(skillJsonPath);
    if (!isCatalogVisible(dirName, skill)) continue;
    skillItems.push(toSkillCatalogItem(skill, dirName));
  }

  return skillItems.sort((left, right) => left.name.localeCompare(right.name));
}

async function collectAgentItems(repoRoot) {
  const agentDirs = await listDirs(path.join(repoRoot, "agents"));
  const agentItems = [];

  for (const dirName of agentDirs) {
    const agentJsonPath = path.join(repoRoot, "agents", dirName, "agent.json");
    if (!(await fileExists(agentJsonPath))) {
      throw new Error(`Missing agent metadata: agents/${dirName}/agent.json`);
    }
    const agent = await readJson(agentJsonPath);
    if (!isCatalogVisible(dirName, agent)) continue;
    const platforms = await detectPlatforms(path.join(repoRoot, "agents", dirName));
    agentItems.push(toAgentCatalogItem(agent, dirName, platforms));
  }

  return agentItems.sort((left, right) => left.name.localeCompare(right.name));
}

async function collectHookItems(repoRoot) {
  const hookDirs = await listDirs(path.join(repoRoot, "hooks"));
  const hookItems = [];

  for (const dirName of hookDirs) {
    const hookJsonPath = path.join(repoRoot, "hooks", dirName, "hook.json");
    if (!(await fileExists(hookJsonPath))) {
      throw new Error(`Missing hook metadata: hooks/${dirName}/hook.json`);
    }
    const hook = await readJson(hookJsonPath);
    if (!isCatalogVisible(dirName, hook)) continue;
    const platforms = await detectHookPlatforms(path.join(repoRoot, "hooks", dirName));
    hookItems.push(toHookCatalogItem(hook, dirName, platforms));
  }

  return hookItems.sort((left, right) => left.name.localeCompare(right.name));
}

async function collectPackItems(repoRoot) {
  const packDirs = await listDirs(path.join(repoRoot, "packs"));
  const packItems = [];

  for (const dirName of packDirs) {
    const packJsonPath = path.join(repoRoot, "packs", dirName, "pack.json");
    if (!(await fileExists(packJsonPath))) {
      throw new Error(`Missing pack metadata: packs/${dirName}/pack.json`);
    }
    const pack = await readJson(packJsonPath);
    packItems.push(toPackCatalogItem(pack, dirName));
  }

  return packItems.sort((left, right) => left.name.localeCompare(right.name));
}

async function generateCatalogSnapshot(repoRoot) {
  const skills = await collectSkillItems(repoRoot);
  const agents = await collectAgentItems(repoRoot);
  const hooks = await collectHookItems(repoRoot);
  const packs = await collectPackItems(repoRoot);

  const catalogBase = {
    schemaVersion: 1,
    skills,
    agents,
    hooks,
    packs
  };

  return {
    catalogBase,
    skillsMarkdown: renderSkillsMarkdown(skills),
    agentsMarkdown: renderAgentsMarkdown(agents),
    hooksMarkdown: renderHooksMarkdown(hooks),
    packsMarkdown: renderPacksMarkdown(packs)
  };
}

module.exports = {
  SKILLS_CATALOG_PATH,
  AGENTS_CATALOG_PATH,
  HOOKS_CATALOG_PATH,
  PACKS_CATALOG_PATH,
  MACHINE_CATALOG_PATH,
  detectPlatforms,
  detectHookPlatforms,
  generateCatalogSnapshot,
  renderSkillsMarkdown,
  renderAgentsMarkdown,
  renderHooksMarkdown,
  renderPacksMarkdown,
  toSkillCatalogItem,
  toAgentCatalogItem,
  toHookCatalogItem,
  toPackCatalogItem
};

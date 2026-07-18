const fs = require("node:fs/promises");
const path = require("node:path");

const { fileExists } = require("./lib/fs-utils");

function isValidName(name) {
  return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name);
}

function todayISODate() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function parseArgs(argv) {
  const args = argv.slice(2);
  let type = "skill"; // default
  let name = null;

  for (const arg of args) {
    if (arg === "--agent" || arg === "-a") {
      type = "agent";
    } else if (arg === "--pack" || arg === "-p") {
      type = "pack";
    } else if (arg === "--hook") {
      type = "hook";
    } else if (arg === "--skill" || arg === "-s") {
      type = "skill";
    } else if (!arg.startsWith("-")) {
      name = arg;
    }
  }

  return { type, name };
}

async function scaffoldSkill(repoRoot, name) {
  const skillDir = path.join(repoRoot, "skills", name);
  if (await fileExists(skillDir)) {
    console.error(`Skill already exists: skills/${name}`);
    process.exitCode = 2;
    return;
  }

  // Warn if an agent with the same name exists
  if (await fileExists(path.join(repoRoot, "agents", name))) {
    console.warn(`Warning: an agent named "${name}" already exists. Names may cause confusion.`);
  }

  await fs.mkdir(skillDir, { recursive: true });

  const skillJson = {
    schemaVersion: 1,
    name,
    displayName: name,
    description: "TODO: one-line description",
    version: "0.1.0",
    maturity: "experimental",
    categories: ["general"],
    tags: [],
    authors: [{ name: "TODO: your name" }],
    entrypoints: {
      skillDoc: "SKILL.md",
      changelog: "CHANGELOG.md"
    }
  };

  await fs.writeFile(
    path.join(skillDir, "skill.json"),
    `${JSON.stringify(skillJson, null, 2)}\n`,
    "utf8"
  );

  await fs.writeFile(
    path.join(skillDir, "SKILL.md"),
    [
      "---",
      `name: ${name}`,
      "description: TODO: describe what this skill does and when to use it",
      'version: "0.1.0"',
      "---",
      "",
      `# ${name}`,
      "",
      "## Trigger",
      "",
      "<!-- When should this skill be activated? Describe the conditions, keywords, or user intents that trigger it. -->",
      "",
      "TODO",
      "",
      "## Instructions",
      "",
      "<!-- Core prompt / behavioral instructions for the agent. This is the main content of the skill. -->",
      "",
      "TODO",
      "",
      "## Examples",
      "",
      "<!-- Provide concrete input/output examples showing the skill in action. -->",
      "",
      "TODO",
      "",
      "## Caveats",
      "",
      "<!-- Known limitations, edge cases, or situations where this skill should NOT be used. -->",
      "",
      "TODO",
      ""
    ].join("\n"),
    "utf8"
  );

  await fs.writeFile(
    path.join(skillDir, "CHANGELOG.md"),
    [
      "# Changelog",
      "",
      "All notable changes to this skill will be documented in this file.",
      "This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
      "",
      "## [Unreleased]",
      "",
      `## [0.1.0] - ${todayISODate()}`,
      "- Initial release.",
      ""
    ].join("\n"),
    "utf8"
  );

  console.log(`Created skills/${name}`);
  console.log("Next:");
  console.log("  npm run build");
  console.log("  npm test");
}

async function scaffoldAgent(repoRoot, name) {
  const agentDir = path.join(repoRoot, "agents", name);
  if (await fileExists(agentDir)) {
    console.error(`Agent already exists: agents/${name}`);
    process.exitCode = 2;
    return;
  }

  // Warn if a skill with the same name exists
  if (await fileExists(path.join(repoRoot, "skills", name))) {
    console.warn(`Warning: a skill named "${name}" already exists. Names may cause confusion.`);
  }

  await fs.mkdir(agentDir, { recursive: true });

  const agentJson = {
    schemaVersion: 1,
    name,
    displayName: name,
    description: "TODO: one-line description",
    version: "0.1.0",
    maturity: "experimental",
    categories: ["general"],
    tags: [],
    authors: [{ name: "TODO: your name" }],
    archetype: "custom",
    skills: [],
    entrypoints: {
      contract: "AGENT.md",
      changelog: "CHANGELOG.md"
    }
  };
  const contractLines = [
    `# ${name} Contract`,
    "",
    `- Handle only work that belongs to the narrowly defined ${name} role.`,
    "- Inspect relevant evidence before drawing conclusions or taking action.",
    "- Follow repository instructions and preserve unrelated user changes.",
    "- Return a concise result with evidence, verification status, and unresolved limits.",
    "- Do not expand scope, weaken safety boundaries, or claim unverified completion.",
    ""
  ];

  await fs.writeFile(
    path.join(agentDir, "agent.json"),
    `${JSON.stringify(agentJson, null, 2)}\n`,
    "utf8"
  );

  await fs.writeFile(path.join(agentDir, "AGENT.md"), contractLines.join("\n"), "utf8");

  await fs.writeFile(
    path.join(agentDir, "claude-code.md"),
    [
      "---",
      `name: ${name}`,
      "description: TODO: describe when to use this agent",
      "tools: Read, Grep, Glob",
      "---",
      "",
      ...contractLines
    ].join("\n"),
    "utf8"
  );

  await fs.writeFile(
    path.join(agentDir, "codex.toml"),
    [
      `# Codex agent configuration for ${name}`,
      "",
      `name = "${name}"`,
      `description = "TODO: describe when to use this agent"`,
      "",
      `developer_instructions = """`,
      ...contractLines.slice(0, -1),
      `"""`,
      ""
    ].join("\n"),
    "utf8"
  );

  await fs.writeFile(
    path.join(agentDir, "omp.md"),
    [
      "---",
      `name: ${name}`,
      "description: TODO: describe when to use this agent",
      "tools: read, grep, glob",
      "---",
      "",
      ...contractLines
    ].join("\n"),
    "utf8"
  );

  await fs.writeFile(
    path.join(agentDir, "CHANGELOG.md"),
    [
      "# Changelog",
      "",
      "All notable changes to this agent will be documented in this file.",
      "This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
      "",
      "## [Unreleased]",
      "",
      `## [0.1.0] - ${todayISODate()}`,
      "- Initial release.",
      ""
    ].join("\n"),
    "utf8"
  );

  console.log(`Created agents/${name}`);
  console.log("Next:");
  console.log("  npm run build");
  console.log("  npm test");
}

async function scaffoldPack(repoRoot, name) {
  const packDir = path.join(repoRoot, "packs", name);
  if (await fileExists(packDir)) {
    console.error(`Pack already exists: packs/${name}`);
    process.exitCode = 2;
    return;
  }

  if (await fileExists(path.join(repoRoot, "skills", name))) {
    console.warn(`Warning: a skill named "${name}" already exists. Names may cause confusion.`);
  }

  if (await fileExists(path.join(repoRoot, "agents", name))) {
    console.warn(`Warning: an agent named "${name}" already exists. Names may cause confusion.`);
  }

  await fs.mkdir(packDir, { recursive: true });

  const packJson = {
    schemaVersion: 1,
    name,
    displayName: name,
    description: "TODO: one-line description",
    version: "0.1.0",
    maturity: "experimental",
    packType: "role-pack",
    categories: ["general"],
    skills: [],
    agents: [],
    tags: [],
    authors: [{ name: "TODO: your name" }]
  };

  await fs.writeFile(
    path.join(packDir, "pack.json"),
    `${JSON.stringify(packJson, null, 2)}\n`,
    "utf8"
  );

  await fs.writeFile(
    path.join(packDir, "README.md"),
    [
      `# ${name}`,
      "",
      "## Purpose",
      "",
      "<!-- Describe who this pack is for and what workflow it bundles. -->",
      "",
      "TODO",
      "",
      "## Included Skills",
      "",
      "<!-- List the skills that this pack installs. -->",
      "",
      "- TODO",
      "",
      "## Included Agents",
      "",
      "<!-- List the agents that this pack installs. -->",
      "",
      "- TODO",
      "",
      "## Install",
      "",
      "```bash",
      `npx my-agents install pack ${name}`,
      `npx my-agents install pack ${name} --platform codex --scope project`,
      "```",
      "",
      "## Notes",
      "",
      "<!-- Explain assumptions, dependency choices, and any platform caveats. -->",
      "",
      "TODO",
      ""
    ].join("\n"),
    "utf8"
  );

  await fs.writeFile(
    path.join(packDir, "CHANGELOG.md"),
    [
      "# Changelog",
      "",
      "All notable changes to this pack will be documented in this file.",
      "This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
      "",
      "## [Unreleased]",
      "",
      `## [0.1.0] - ${todayISODate()}`,
      "- Initial release.",
      ""
    ].join("\n"),
    "utf8"
  );

  console.log(`Created packs/${name}`);
  console.log("Next:");
  console.log("  npm run build");
  console.log("  npm test");
}

async function scaffoldHook(repoRoot, name) {
  const hookDir = path.join(repoRoot, "hooks", name);
  if (await fileExists(hookDir)) {
    console.error(`Hook already exists: hooks/${name}`);
    process.exitCode = 2;
    return;
  }

  await fs.mkdir(path.join(hookDir, "scripts"), { recursive: true });

  const hookJson = {
    schemaVersion: 1,
    name,
    displayName: name,
    description: "TODO: one-line description",
    version: "0.1.0",
    maturity: "experimental",
    categories: ["general"],
    tags: [],
    authors: [{ name: "TODO: your name" }],
    events: ["PreToolUse"]
  };

  await fs.writeFile(
    path.join(hookDir, "hook.json"),
    `${JSON.stringify(hookJson, null, 2)}\n`,
    "utf8"
  );

  const claudeFragment = {
    hooks: {
      PreToolUse: [
        {
          matcher: "TODO-tool-matcher",
          hooks: [
            {
              type: "command",
              command: `bash "$CLAUDE_PROJECT_DIR/.claude/hooks/${name}/${name}.sh"`,
              timeout: 15
            }
          ]
        }
      ]
    }
  };

  await fs.writeFile(
    path.join(hookDir, "claude-code.json"),
    `${JSON.stringify(claudeFragment, null, 2)}\n`,
    "utf8"
  );

  await fs.writeFile(
    path.join(hookDir, "scripts", `${name}.sh`),
    [
      "#!/usr/bin/env bash",
      `# ${name}: TODO describe what this hook enforces.`,
      "# Receives the tool-call JSON on stdin; exit 2 with stderr to deny.",
      "set -euo pipefail",
      "",
      "input=$(cat)",
      "# TODO: implement the check against $input",
      "exit 0",
      ""
    ].join("\n"),
    "utf8"
  );

  await fs.writeFile(
    path.join(hookDir, "HOOK.md"),
    [
      `# ${name}`,
      "",
      "## Purpose",
      "",
      "<!-- What policy does this hook enforce, and why mechanically instead of via prompts? -->",
      "",
      "TODO",
      "",
      "## Behavior",
      "",
      "<!-- Which events/tools it intercepts, when it allows vs denies, safe-by-default story. -->",
      "",
      "TODO",
      "",
      "## Install",
      "",
      "```bash",
      `npx my-agents install hook ${name}`,
      "```",
      "",
      "## Limitations",
      "",
      "TODO",
      ""
    ].join("\n"),
    "utf8"
  );

  await fs.writeFile(
    path.join(hookDir, "CHANGELOG.md"),
    [
      "# Changelog",
      "",
      "All notable changes to this hook will be documented in this file.",
      "This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
      "",
      "## [Unreleased]",
      "",
      `## [0.1.0] - ${todayISODate()}`,
      "- Initial release.",
      ""
    ].join("\n"),
    "utf8"
  );

  console.log(`Created hooks/${name}`);
  console.log("Next:");
  console.log("  npm run build");
  console.log("  npm test");
}

async function main() {
  const repoRoot = path.resolve(__dirname, "..");
  const { type, name } = parseArgs(process.argv);

  if (!name) {
    console.error("Usage: npm run new -- [--skill | --agent | --hook | --pack] <name>");
    console.error("");
    console.error("  --skill, -s   Create a new skill (default)");
    console.error("  --agent, -a   Create a new agent");
    console.error("  --hook        Create a new hook");
    console.error("  --pack,  -p   Create a new pack");
    process.exitCode = 2;
    return;
  }

  if (!isValidName(name)) {
    console.error(`Invalid name: ${name}. Expected kebab-case (e.g. "my-${type}").`);
    process.exitCode = 2;
    return;
  }

  if (type === "agent") {
    await scaffoldAgent(repoRoot, name);
  } else if (type === "pack") {
    await scaffoldPack(repoRoot, name);
  } else if (type === "hook") {
    await scaffoldHook(repoRoot, name);
  } else {
    await scaffoldSkill(repoRoot, name);
  }
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err);
    process.exitCode = 1;
  });
}

module.exports = {
  isValidName,
  parseArgs,
  scaffoldAgent,
  scaffoldHook,
  scaffoldPack,
  scaffoldSkill
};

const fs = require("node:fs/promises");
const path = require("node:path");

const { fileExists, readJson } = require("./fs-utils");

// Hook fragments are merged into JSON config files that users also edit by
// hand (.claude/settings.json, .codex/hooks.json). Entries are matched by
// deep equality so merge stays idempotent and removal never touches entries
// the user added themselves.

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(",")}]`;
  }
  if (value && typeof value === "object") {
    const keys = Object.keys(value).sort();
    return `{${keys.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function entriesEqual(left, right) {
  return stableStringify(left) === stableStringify(right);
}

async function readConfigFile(configPath) {
  if (!(await fileExists(configPath))) {
    return {};
  }
  return readJson(configPath);
}

async function writeConfigFile(configPath, config) {
  await fs.mkdir(path.dirname(configPath), { recursive: true });
  await fs.writeFile(configPath, `${JSON.stringify(config, null, 2)}\n`, "utf8");
}

async function mergeHooksConfig(configPath, fragmentHooks) {
  const config = await readConfigFile(configPath);
  if (!config.hooks || typeof config.hooks !== "object" || Array.isArray(config.hooks)) {
    config.hooks = {};
  }

  let added = 0;
  for (const [event, entries] of Object.entries(fragmentHooks ?? {})) {
    if (!Array.isArray(config.hooks[event])) {
      config.hooks[event] = [];
    }
    for (const entry of entries ?? []) {
      const exists = config.hooks[event].some((existing) => entriesEqual(existing, entry));
      if (!exists) {
        config.hooks[event].push(entry);
        added += 1;
      }
    }
  }

  await writeConfigFile(configPath, config);
  return added;
}

async function removeHooksConfig(configPath, fragmentHooks) {
  if (!(await fileExists(configPath))) {
    return 0;
  }

  let config;
  try {
    config = await readJson(configPath);
  } catch {
    return 0;
  }

  if (!config.hooks || typeof config.hooks !== "object" || Array.isArray(config.hooks)) {
    return 0;
  }

  let removed = 0;
  for (const [event, entries] of Object.entries(fragmentHooks ?? {})) {
    if (!Array.isArray(config.hooks[event])) {
      continue;
    }
    const kept = config.hooks[event].filter(
      (existing) => !(entries ?? []).some((entry) => entriesEqual(existing, entry))
    );
    removed += config.hooks[event].length - kept.length;
    if (kept.length > 0) {
      config.hooks[event] = kept;
    } else {
      delete config.hooks[event];
    }
  }

  if (Object.keys(config.hooks).length === 0) {
    delete config.hooks;
  }

  await writeConfigFile(configPath, config);
  return removed;
}

module.exports = {
  entriesEqual,
  mergeHooksConfig,
  removeHooksConfig
};

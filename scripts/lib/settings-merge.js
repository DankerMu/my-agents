const fs = require("node:fs/promises");
const path = require("node:path");

const { fileExists, readJson } = require("./fs-utils");

// Hook fragments are merged into JSON config files that users also edit by
// hand (.claude/settings.json, .codex/hooks.json). Identity is the tuple
// (event, matcher, hook.command): a fragment hook is added into the existing
// block with the same matcher (creating the block only when none exists), and
// removal drops only those commands from same-matcher blocks. Whole-block
// deep equality would duplicate the block whenever the user hand-added an
// extra hook next to ours, running the managed command twice.

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

function isObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function hookCommand(hook) {
  return isObject(hook) && typeof hook.command === "string" ? hook.command : null;
}

// A fragment entry is command-addressable only when every hook has a string
// command; anything else falls back to whole-entry deep equality.
function entryCommands(entry) {
  if (!isObject(entry) || !Array.isArray(entry.hooks) || entry.hooks.length === 0) {
    return null;
  }
  const commands = entry.hooks.map(hookCommand);
  return commands.every((command) => command !== null) ? commands : null;
}

function sameMatcher(left, right) {
  return (
    isObject(left) && isObject(right) && entriesEqual(left.matcher ?? null, right.matcher ?? null)
  );
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

function mergeEntry(existingEntries, entry) {
  const commands = entryCommands(entry);
  if (commands === null) {
    if (existingEntries.some((existing) => entriesEqual(existing, entry))) {
      return 0;
    }
    existingEntries.push(entry);
    return 1;
  }

  const block = existingEntries.find(
    (existing) => sameMatcher(existing, entry) && Array.isArray(existing.hooks)
  );
  if (!block) {
    existingEntries.push(entry);
    return commands.length;
  }

  let added = 0;
  entry.hooks.forEach((hook, index) => {
    const present = block.hooks.some((existing) => hookCommand(existing) === commands[index]);
    if (!present) {
      block.hooks.push(hook);
      added += 1;
    }
  });
  return added;
}

async function mergeHooksConfig(configPath, fragmentHooks) {
  const config = await readConfigFile(configPath);
  if (!isObject(config.hooks)) {
    config.hooks = {};
  }

  let added = 0;
  for (const [event, entries] of Object.entries(fragmentHooks ?? {})) {
    if (!Array.isArray(config.hooks[event])) {
      config.hooks[event] = [];
    }
    for (const entry of entries ?? []) {
      added += mergeEntry(config.hooks[event], entry);
    }
  }

  await writeConfigFile(configPath, config);
  return added;
}

// Returns the entry with the fragment's commands stripped (null when nothing
// is left), plus how many hooks were removed.
function removeFromEntry(existing, entry) {
  const commands = entryCommands(entry);
  if (commands === null) {
    return entriesEqual(existing, entry)
      ? { kept: null, removed: 1 }
      : { kept: existing, removed: 0 };
  }
  if (!sameMatcher(existing, entry) || !Array.isArray(existing.hooks)) {
    return { kept: existing, removed: 0 };
  }
  const hooks = existing.hooks.filter((hook) => !commands.includes(hookCommand(hook)));
  const removed = existing.hooks.length - hooks.length;
  if (removed === 0) {
    return { kept: existing, removed: 0 };
  }
  if (hooks.length === 0) {
    return { kept: null, removed };
  }
  return { kept: { ...existing, hooks }, removed };
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

  if (!isObject(config.hooks)) {
    return 0;
  }

  let removed = 0;
  for (const [event, entries] of Object.entries(fragmentHooks ?? {})) {
    if (!Array.isArray(config.hooks[event])) {
      continue;
    }
    const kept = [];
    for (let existing of config.hooks[event]) {
      for (const entry of entries ?? []) {
        if (existing === null) {
          break;
        }
        const result = removeFromEntry(existing, entry);
        removed += result.removed;
        existing = result.kept;
      }
      if (existing !== null) {
        kept.push(existing);
      }
    }
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

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");

const { mergeHooksConfig, removeHooksConfig } = require("../lib/settings-merge");

const FRAGMENT = {
  PreToolUse: [
    {
      matcher: "Edit|Write",
      hooks: [{ type: "command", command: "bash guard.sh", timeout: 15 }]
    }
  ]
};

const USER_ENTRY = {
  matcher: "Bash",
  hooks: [{ type: "command", command: "bash user-own.sh" }]
};

async function makeTmpConfigPath() {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), "settings-merge-"));
  return path.join(dir, "settings.json");
}

async function readConfig(configPath) {
  return JSON.parse(await fs.readFile(configPath, "utf8"));
}

test("merge creates the config file and adds fragment entries", async () => {
  const configPath = await makeTmpConfigPath();
  const added = await mergeHooksConfig(configPath, FRAGMENT);

  assert.equal(added, 1);
  const config = await readConfig(configPath);
  assert.deepEqual(config.hooks.PreToolUse, FRAGMENT.PreToolUse);
});

test("merge is idempotent across repeated installs", async () => {
  const configPath = await makeTmpConfigPath();
  await mergeHooksConfig(configPath, FRAGMENT);
  const addedAgain = await mergeHooksConfig(configPath, FRAGMENT);

  assert.equal(addedAgain, 0);
  const config = await readConfig(configPath);
  assert.equal(config.hooks.PreToolUse.length, 1);
});

test("merge preserves unrelated user settings and hook entries", async () => {
  const configPath = await makeTmpConfigPath();
  await fs.writeFile(
    configPath,
    `${JSON.stringify({ model: "opus", hooks: { PreToolUse: [USER_ENTRY] } }, null, 2)}\n`,
    "utf8"
  );

  await mergeHooksConfig(configPath, FRAGMENT);

  const config = await readConfig(configPath);
  assert.equal(config.model, "opus");
  assert.equal(config.hooks.PreToolUse.length, 2);
  assert.deepEqual(config.hooks.PreToolUse[0], USER_ENTRY);
});

test("remove deletes only deep-equal managed entries and cleans empty keys", async () => {
  const configPath = await makeTmpConfigPath();
  await fs.writeFile(
    configPath,
    `${JSON.stringify({ hooks: { PreToolUse: [USER_ENTRY] } }, null, 2)}\n`,
    "utf8"
  );
  await mergeHooksConfig(configPath, FRAGMENT);

  const removed = await removeHooksConfig(configPath, FRAGMENT);

  assert.equal(removed, 1);
  const config = await readConfig(configPath);
  assert.deepEqual(config.hooks.PreToolUse, [USER_ENTRY]);

  const removedAgain = await removeHooksConfig(configPath, FRAGMENT);
  assert.equal(removedAgain, 0);
});

test("remove drops the hooks key entirely when no entries remain", async () => {
  const configPath = await makeTmpConfigPath();
  await mergeHooksConfig(configPath, FRAGMENT);
  await removeHooksConfig(configPath, FRAGMENT);

  const config = await readConfig(configPath);
  assert.equal(config.hooks, undefined);
});

test("entries with reordered keys still match on removal", async () => {
  const configPath = await makeTmpConfigPath();
  await mergeHooksConfig(configPath, FRAGMENT);

  const reordered = {
    PreToolUse: [
      {
        hooks: [{ timeout: 15, command: "bash guard.sh", type: "command" }],
        matcher: "Edit|Write"
      }
    ]
  };
  const removed = await removeHooksConfig(configPath, reordered);
  assert.equal(removed, 1);
});

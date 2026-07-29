# User-Invoked Skill 标记

User-invoked skill 在 SKILL.md frontmatter 中设置 `disable-model-invocation: true`。新增、改名、删除或重新标记 skill 时查阅本文件。

该标记在各平台的行为：

- **Claude Code** 将其从常驻上下文中剔除——只有 `/name` 能触达。
- **Codex** 的安装/投影落在 `.agents/skills-manual/` 而非 `.agents/skills/`。
- **omp** 原生支持该标记，副本保留在 `.omp/skills/`。

路由契约：

- `ask-danker` 路由 skill 是被标记 skill 的发现面。新增、改名、删除、重新标记任何 skill，或改动任何流的走向时，必须在同一变更中更新路由表。
- 任何 skill（尤其 user-invoked）缺席路由表时，校验会失败。
- 绝不标记会被其它 skill 或流水线中途调用的 skill——标记会在流水线最需要它时把它藏起来。

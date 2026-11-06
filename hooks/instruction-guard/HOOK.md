# Instruction Guard

PreToolUse 体积闸：任意目录层级的 `AGENTS.md` / `CLAUDE.md` 不得超过 **32768 字节**（32 KiB），每一行不得超过 **307 字节**（0.3 KiB）。超限的改动直接拒绝，并提示按 `eng-init` skill 瘦身。修改本身不需要审批。

## 解决什么问题

这两个文件每次会话都会整份进入上下文，长度直接变成每一轮的 token 成本，而且越长越难被模型完整遵守。它们又是最容易被“顺手补一句”撑大的文件。靠自然语言约束控制不住长度，本 hook 把上限变成机械检查。

## 判定规则

按 UTF-8 字节计数：一个汉字 3 字节，单行约 100 个汉字。旧内容也算在内。

**能算出改后内容的调用**（文件工具与补丁）检查改后的整份文件：

- 达标就放行。
- 文件已经超限时，只放行“正在修”的改动：不引入新的超长行，且总超出量比改前少（总超出量 = 文件超出的字节数 + 每个超长行超出的字节数）。可以分几次逐步修完。
- 往一个仍有超长行的文件里做任何别的改动，都会被拒，拒绝信息会列出前几处超限位置。

能算出改后内容的工具：

| 平台        | 工具                                                                                  |
| ----------- | ------------------------------------------------------------------------------------- |
| Claude Code | `Edit` / `Write` / `MultiEdit`                                                        |
| Codex       | `apply_patch`（`Add` / `Update` / `Delete File`；只有新增行的 hunk 落点不确定，不算） |
| omp         | `write`；`edit` 的 replace 与 apply_patch 模式                                        |

**算不出改后内容的调用**看当前文件：当前文件已超限就拒绝，否则放行。这类调用包括：

- shell 写入。
- omp `edit` 的 hashline（默认）与 patch 模式。
- `NotebookEdit`。

拒绝信息会要求改用能检查结果的文件工具。

**shell 命令**先按 shell 语法切分，再按命令名找写入目标，只读命令一律放行，例如 `grep install AGENTS.md`、`rg "=>"`、`cp AGENTS.md /tmp/x`。识别的写入方式：

- 重定向 `>` / `>>` / `&>`。
- `rm` / `touch` / `tee` / `chmod`。
- `cp` / `ln` / `install` / `rsync` 的目标；目标是目录时会拼上源文件名。
- `mv` 的源和目标。
- `sed -i` / `perl -i` / `dd of=`。
- `git checkout/restore/...` 的路径参数。
- 带 `--write` / `--fix` 的命令。

还会递归分析 `bash -c`、`$(…)`、反引号、`find -exec`，跟随 `cd` 之后的相对路径，glob 按文件名匹配。写入目标无法确定时（内联代码、`xargs`、`find -delete`、`$变量`），只要命令点名了指令文件，就按“写入该文件”处理。

**拒绝方式**：Claude Code 返回 `permissionDecision: "deny"`；Codex 与 omp 以 exit 2 拦截。拒绝原因里写明超限位置和瘦身指引：

- 用 `eng-init` skill 的 incremental 模式瘦身，让 AGENTS.md 只保留高频要用的索引，细节放到链接文档。
- AGENTS.md / CLAUDE.md 是由源片段生成的，就改源片段再重新渲染。

## 扫描已有文件

模型一直不碰的文件，hook 发现不了，可以用 `check` 扫描。有超限时退出码为 1，可以接进 CI：

```bash
bash .claude/hooks/instruction-guard/instruction-guard.sh check                  # 当前目录下所有 AGENTS.md / CLAUDE.md
bash .claude/hooks/instruction-guard/instruction-guard.sh check docs/AGENTS.md
```

## 配置

上限可用环境变量调整，在 hook 进程的环境里设置：

- `INSTRUCTION_GUARD_MAX_BYTES`：单个文件的字节上限，默认 `32768`。
- `INSTRUCTION_GUARD_MAX_LINE_BYTES`：单行的字节上限，默认 `307`。

## 安装

```bash
npx my-agents install hook instruction-guard            # 全平台
npx my-agents install hook instruction-guard --platform claude
```

安装做三件事：

- 把脚本拷到 `<project>/.claude/hooks/instruction-guard/`、`.codex/hooks/…`、`.omp/hooks/…`。
- 把配置片段按 hook 命令幂等合并进 `.claude/settings.json` / `.codex/hooks.json`。
- omp 把 `omp.ts` 拷到 `.omp/hooks/pre/instruction-guard.ts`。

卸载只摘除本包的条目。本 hook 装上即生效，没有启用清单。在已有超限文件的项目里装上后，第一次修改这些文件就会被要求先瘦身。建议先跑 `check`，把现有文件瘦身后再推广。

## 限制

- **脚本内部的写入看不见**：没点名指令文件就写入的命令不会被拦，例如 `npm run sync-instructions` 这类由脚本生成 AGENTS.md 的流程、`python3 scripts/x.py`。生成型项目的源片段（如 `instructions/root/*.md`）也不在检查范围内，渲染出的结果要靠 `check` 兜底。
- **内联代码可能被误拦**：`python -c`、`perl -ne` 这类内联代码即使只读，只要点名了一个已超限的指令文件，也会被拒，因为代码内容不做分析。
- **删除受限**：用 shell 删除一个已超限的指令文件会被拒；Codex 用 `apply_patch` 删除可以。
- **运行依赖**：需要 `python3`，只用标准库，以 `python3 -I` 隔离模式运行，项目里的同名模块（如 `json.py`）不会让 guard 失效。guard 自身出错时，只要输入点名了指令文件，就按拒绝处理。
- **omp hashline 编辑**：默认的 hashline 模式算不出改后内容。文件达标时放行，文件超限时会被拒，需要改用 `write` 工具。

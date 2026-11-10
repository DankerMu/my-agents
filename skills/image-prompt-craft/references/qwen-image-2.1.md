# Qwen-Image-2.1 适配规则（供 Agent 内部读取）

适配对象：**Qwen-Image-2.1** 本地权重；兼顾其 Turbo 及兼容后端，但**不能假设**所有后端/API/工作流支持同一批参数。此 Skill 是文本层，不要求安装官方提示词增强模型。

## 1. 已核实的官方事实

- Qwen-Image-2.1 是统一的文生图与图像编辑模型，支持原生透明图（RGBA）与最多十张参考图进行编辑；实际限制取决于加载模型、可用显存和前端实现。
- 官方提供两套**独立的** Prompt Enhancer 模型：`Qwen/Qwen-Image-2.1-PE-T2I` 用于文生图，`Qwen/Qwen-Image-2.1-PE-I2I` 用于图像编辑，基于经微调的 Qwen3.5-VL 9B。
- 官方 T2I 改写系统采用**一段英文成图观察描述**，明确画幅、主体、空间、字串、材质、光线和整体构图；复杂内容可写很长。
- 官方 I2I 改写系统侧重**精确修改和避免保留部分漂移**；对于需要保留的人物身份或产品原貌，引用参考图本身，不要详尽复述其外貌。
- ModelScope/QwenCloud 的云 API 功能与 Diffusers/ComfyUI 的本地推理参数可能不同。特别是云端文生图文档指出 `qwen-image-2.1` 系列不支持独立的 `negative_prompt` 参数；因此本 Skill **不默认生成单独负面提示词**。

## 2. 交互后的 Qwen 输出顺序

Qwen-Image-2.1 的提示词增强规则用于**表达已经确定的视觉意图**，不用于替用户决定艺术方向。顺序应为：

`用户口语需求 →（必要时交互选定方案）→ 明确已确认约束 → 生成精确 prompt → Qwen 本地推理 → 对比成图并最小化修订`

- 用户尚在选择风格/构图时，不急着输出数百词的完整英文 prompt；先用中文给他看懂的对比选项。
- 用户说“只要最终 prompt”“别问”时跳过交互，直接按已给定条件生成。
- 角色设定、位置、原文字串和参考图锚点以**用户已确认的视觉方案**为准；官方 PE-T2I/PE-I2I 也不应改变它们。如串接官方 PE，应人工或自动核对改写后的硬约束。
- 后端不能仅凭文本保证精确构图、角色身份或字符零错误；不要以提问代替实际抽样验证。

## 3. 文生图 T2I 的写作方法

**默认语言**：英文自然语言；用户明确指定中文则改为中文。画面里真实应出现的中文必须原样保留，比如汉字 `"福"`，不能转译为 `"luck"`。

**叙述立场**：像在观察一幅已完成的图片，而不是对生成器说命令。推荐开头：

`A wide 2D anime illustration shows ...`

或 `A documentary-style photograph of ...`、`A clean scientific cutaway illustration depicts ...`。

**组织逻辑**：

1. 用首句声明**绘画媒介 + 唯一主风格 + 主体 + 场景**；明确宽画幅/竖画幅。
2. 对有多个区块的画面，沿“背景→顶部→左→中→右→前景”描述；对人像沿“姿态→脸→服饰→道具→背景”描述。
3. 每个必须存在的物件尽量交代相对位置，尤其用户已指定的左右关系、远近关系、数量。
4. 给关键材料具体质感：`glossy translucent amber sugar` 比 `beautiful candy` 可执行。
5. 单独交代主光源如何照亮主体，并与背景阴影自洽。
6. 用一句整体构图/色彩总结结尾；不重复罗列“masterpiece, best quality, 8K”一类空话。
7. 建议把图片比例同时交付给前端作为**参数**，不要以提示词代替尺寸控制。

**长度策略**：官方 PE-T2I 的参考风格倾向长段（约 400–500 英文词）以描述复杂布局。本 Skill 在简单画面允许更短的成图段落，避免用户只要一个茶杯却被塞满无关细节。可以对复杂海报、分镜、信息图采用更详细的官方式“区域遍历”描述；此策略是实用性取舍，不宣称短提示词必然优于官方 PE。

## 4. 图像编辑 I2I 的写作方法

- 首句写**明确的变化**：`Replace only...`, `Remove...`, `Change the scarf...`, `Keep the original subject identity...`。
- 明确目标图像编号和位置。若有多张参考图，绑定各图职责，避免反过来改错底图。
- 仅描述**要修改**的对象的具体外观；对不修改部分只写一句 `Keep all other elements of <image1> unchanged.`。
- 原人脸、身份、产品标记等通过图像锚定；不要重写成一整段新的人像生成提示词。
- 不更改画幅时跟随底图；若用户明确指定 16:9、重新构图或从参照人物生成新场景，则应遵守新画幅与场景需求。
- 场景融合需要声明光线/透视/阴影匹配，但不因此添加新元素。

**模板**：

`In <image1>, [single precise change, object, location, new appearance]. [How it matches the original light/material/perspective]. Preserve [identity or critical non-target details] and keep everything else unchanged.`

这份模板仅表达结构，实际输出不要保留方括号占位符。

## 5. 原生透明图

如用户需要透明贴纸、图标、单角色立绘，可采用清晰的透明要求：

`This is an RGBA image with transparency. A single [subject], clean fully visible silhouette, no scene or background. The image has an alpha channel and the background is transparent.`

**注意**：显式要求保存 Alpha 通道；不要把棋盘纹作为背景绘制进去。若前端把输出转存成 JPEG，提示词无力恢复透明。

## 6. 使用官方 PE 模型时的关系

存在三种实际工作流：

1. **本 Skill → 生图模型**：无需额外模型，最简单。
2. **用户原话 → 官方 PE → 生图模型**：官方原生链路。
3. **本 Skill → 官方 PE → 生图模型**：可能重复扩写，引入与用户无关的细节。只有实际 A/B 对比显示有改进时才启用。

推荐用相同 seed（若后端有）、相同画幅、相同步数，在 PE 开/关之间只更改一个变量；否则无法确定哪一步导致改善。不要假设本地 ComfyUI 存在云 API 的 `prompt_extend` 参数。

## 7. 画幅、参数与推理后端

本 Skill 只提供 `aspect_ratio` **建议值**，不写死分辨率、采样步数、CFG、guidance、scheduler、seed 等参数，因为它们取决于本地后端和模型变体。若用户给出工作流 JSON、节点名或实际后端参数，再用其真实可用字段适配。不要用假想参数名直接调用接口。

## 8. 官方资料（可在联网环境中核验，离线使用不依赖）

- 官方仓库：https://github.com/QwenLM/Qwen-Image-2.1
- Prompt Enhancer 说明：https://github.com/QwenLM/Qwen-Image-2.1/tree/main/prompt_rewrite
- T2I 官方规则：https://github.com/QwenLM/Qwen-Image-2.1/blob/main/prompt_rewrite/prompts/system_prompt_t2i.txt
- 编辑官方规则：https://github.com/QwenLM/Qwen-Image-2.1/blob/main/prompt_rewrite/prompts/system_prompt_edit.txt
- Diffusers 模型卡：https://huggingface.co/Qwen/Qwen-Image-2.1
- 云端 negative_prompt 支持情况（不等于所有本地后端）：https://docs.qwencloud.com/developer-guides/image-generation/text-to-image

本 Skill 是**独立创作的指导规则**，仅提炼官方文档的适配要点，不复制官方 PE 权重/系统提示词，也不保证可以替代官方 PE 的训练能力。
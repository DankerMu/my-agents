# 跨风格示例与回归检查

这些示例展示**如何选词**，不是固定提示词模板。输出按默认 Qwen-Image-2.1：文生图用英文成图描述，编辑用简短英文指令；用户改为中文时整体转换，但画中原文必须保持。

## 示例 1：动漫节日复杂场景（保留所有硬约束）

**用户输入（压缩示例）**：橙色双马尾猫娘，虎斑猫耳、橙白猫尾，小猫发饰、彩虹眼、笑脸；橙色绗缝羽绒服、绣白猫的红围巾，蹲在糖画摊前举糖葫芦。摊上虎形糖画和吹糖人，带红绳的米色福袋。除夕雪夜庙会，左上红底黑字“福”挂饰、红灯笼、孔明灯、右侧舞龙、远处雪中古镇牌楼。日系 2D 赛璐璐 + 柔和厚涂，16:9。

**推荐输出**：

```text
A wide 16:9 Japanese 2D anime illustration depicts a joyful orange-haired cat-girl crouching in front of a traditional Chinese sugar-art stall at a snowy Lunar New Year's Eve temple fair. She has two short orange twin ponytails, one pair of orange tabby cat ears, a single fluffy orange-and-white striped tail, and a tiny sleeping orange kitten hair clip. Her oversized eyes blend blue, green, and orange in a vivid rainbow gradient; her cheeks are flushed, and she laughs with an open mouth. She wears a thick, warmly quilted orange down jacket with visibly padded baffles and a hood gathered at the collar, plus a chunky red knitted scarf whose hanging end bears a small embroidered white cat. One hand clearly holds up a skewer of glossy red candied hawthorns. In the lower-left foreground, a weathered wooden stall displays a translucent golden tiger-shaped sugar painting and several hand-blown sugar figurines, next to a beige cloth lucky pouch tied with red cord and bearing the Chinese character "福". In the upper-left hangs a red diamond-shaped charm printed with the single upright black character "福". Strings of glowing red lanterns illuminate the snow-dusted market street; sky lanterns and a few snowflakes float in the deep winter-blue night. On the right, performers in traditional red costumes carry a sweeping golden dragon dance. Beyond them stands a softly lit ancient-town ceremonial archway with snow on its roof. Crisp clean anime line art and cel-shaded base colors define the character, while localized soft painterly shading gives the coat, knit scarf and warm lantern glow gentle dimensionality. The girl remains the unmistakable focal point, with rich festive reds and golds contrasting against cool blue snow shadows.
```

**检查**：没有把人物变成 3D、没有加摄影真实皮肤、没有把“福”翻译成英文；“赛璐璐+厚涂”通过材质局部化协调；避免舞龙遮挡人物面部。画幅作为后端参数同步设置为 16:9。

## 示例 2：含专业主题、无真实数据的科研配图

**用户输入**：给研究报告做一张“冰川退缩后冰湖扩张，引发溃决洪水并向下游演进”的解释图，严肃，不要 AI 炫酷感，16:9。

**推荐输出**：

```text
A wide 16:9 scientific explanatory illustration presents a conceptual mountain-to-valley sequence showing glacier retreat, expanding proglacial lake water, a possible moraine-dam breach, and downstream flood propagation. The scene uses a coherent elevated cutaway perspective: a retreating alpine glacier and its rocky moraine appear in the upper left, the turquoise glacial lake occupies the middle mountain basin, and the connected river channel leads toward a lower valley on the right. Water motion and changing terrain form a legible upstream-to-downstream progression without exaggerated explosions or fantasy effects. Restrained glacier blue, slate gray, muted earth brown and selective amber emphasis separate ice, water, unstable sediment and potential impact zones. Clean, precise edges and even lighting keep the full terrain and flow path readable. The illustration is explicitly schematic rather than a measured map, with open margins reserved for verified labels and data to be added later. No invented place names, numerical measurements or decorative interface overlays appear in the image.
```

**检查**：不声称具体真实地理位置、不制造伪监测数值；图中流域关系是概念示意。

## 示例 3：纪实科研场景

**用户输入**：一个科研人员在野外测水，像真实新闻照片，不要摆拍。

**推荐输出**：

```text
A documentary-style environmental photograph shows a field hydrologist taking a river measurement from the safe bank of a mountain stream. The subject wears practical outdoor workwear and focuses on the handheld measuring equipment rather than posing for the camera. Wet stones, low riparian vegetation and a fast-flowing but believable stream establish the field setting. Soft overcast daylight produces even, natural tones and realistic reflections on the water. The composition is a medium-wide eye-level view with the person clearly visible and the surrounding river environment providing context. Clothing folds, equipment surfaces and river turbulence have credible real-world textures. The image is restrained, observational and free of staged hero lighting, fake data labels and decorative sci-fi graphics.
```

**检查**：纪录片质感 ≠ 高清滤镜；不编造设备品牌、站点编号和地点。

## 示例 4：极简平面设计

**用户输入**：给一款读书 App 做简洁高级的插画，米白和墨绿，不要字。

**推荐输出**：

```text
A minimalist flat-vector editorial illustration for a reading app shows an open book as the main focal shape, with a single stylized leaf emerging from the center fold. The image uses refined geometric silhouettes, consistent edge treatment, balanced asymmetry and generous negative space. A warm off-white background contrasts with deep forest-green shapes and one subtle lighter green accent. The paper and leaf remain visually distinct without photorealistic surface texture, 3D extrusion or dramatic cinematic lighting. The overall design feels calm, elegant and quietly modern, with no lettering, logo, numbers or interface text.
```

**检查**：没有因为“高级”就加入金属镀铬、黑金渐变或故意加文字。

## 示例 5：图像编辑，保持原脸

**用户输入**：把图1里人物衣服换成橙色羽绒服，脸、动作、背景别变。

**推荐输出**：

```text
In <image1>, replace only the person's current outer jacket with a warm orange, thickly quilted down jacket with realistic padded seams and natural folds. Fit the replacement to the original body pose and match the existing lighting, shadows and occlusion. Preserve the person's exact facial identity, hair, expression, hands, pose, framing and background; leave every other element unchanged.
```

**检查**：没有重新描述人物长相，不改面部风格，不擅自替换背景；如局部区域仍漂移，建议使用编辑遮罩。

## 示例 6：透明贴纸

**用户输入**：生成一只圆滚滚的橘猫贴纸，要透明背景。

**推荐输出**：

```text
This is an RGBA image with transparency. A single rounded orange tabby cat sticker with a playful seated pose, clear warm-orange stripe patterns, simple expressive eyes, a clean continuous silhouette and softly controlled 2D cel shading. The cat is entirely visible, centered and isolated, with no props, scenery, floor, cast-shadow card, border text or other characters. The image has an alpha channel and the background is genuinely transparent.
```

**检查**：后端导出 PNG/RGBA，不能让显示棋盘格的预览误判为真正 Alpha。

---

## 快速回归用例（把输入交给 Agent，按预期性质检查）

| 用户原话 | 应触发的策略 | 失败判定 |
| --- | --- | --- |
| “赛璐璐、厚涂都要，但别像 3D” | 动漫主体平涂，阴影与布料局部柔化 | 出现 3D、PBR 皮肤和镜面塑料 |
| “给论文配一个简明示意图，不要图中文字” | 科研概念图，清晰全局，不造数 | 自行写图注、地名和伪坐标 |
| “福字必须是‘福’，别写英文” | 保留原字，明确位置与朝向 | 译成 luck / fortune |
| “图1的脸、图2的衣服、图3的室内背景” | 多参考图角色分配；保留图1身份；图3作为场景画布 | 脸被换成图2模特，或背景错误 |
| “这张图我只想改成 16:9，主体别变” | 构图延展或裁切策略；除画幅外尽量保真 | 整体变风格或重画脸 |
| “图片太 AI 了” | 诊断具体可见问题，减少泛化光效 | 只补“photorealistic, 8K” |
| “请只给可复制的提示词” | 仅 prompt，不附标题解释 | 加一长篇分析或三版备选 |
| “海报主标题写‘雪域观测’，不要其他字” | 原字串准确、层级明确、其余无文字 | 新增标语、英文缩写、拼错原文 |
| “不要人物，只要流水和岩石” | 固定 `no people`, 清晰地貌焦点 | 擅自加游客或航拍无人机 |
| “用一张图画出这组精确流量曲线” | 说明需真实数据可视化工具，不冒充生成图精确 | 幻造曲线数值、伪造坐标刻度 |
| “和参考图一样，只换背景” | 保留身份与前景结构，精准换背景 | 改变人脸、衣服、姿势 |
| “做一张官网横幅，右侧留白排字” | 主体偏左、右侧足够清洁空白 | 装饰物/文字占据右侧 |

## 评估量规（供自检或批量测试）

对每一项评分 0/1/2；总分 10 分：

1. **硬约束完整度**：主体、数量、原文、动作、位置、画幅是否保留。
2. **风格一致性**：是否存在唯一主媒介与一致的材质、光线表现。
3. **视觉可执行性**：是否有清晰焦点、空间关系、关键材料、可用的光照设定。
4. **简洁性**：冗余是否受控，没有无用流行词或过度扩写。
5. **任务匹配性**：编辑时保留原图；科研图不造数；文本保真；透明确有 Alpha 意图。

**门槛**：硬约束或任务匹配有 0 分时直接退回修订；否则建议总分至少 8/10 才交付。

---

## v2.0 交互行为回归

本文件中的 6 组「推荐输出」用于**方向已确定时**的最终 prompt 检查；不能由此推断 Agent 一收到任何模糊输入就应该立即扩写。对用户仍在探索风格、构图或用途的情形，请同时测试 [interactive-dialogues.md](interactive-dialogues.md)：其中包含 7 组多轮对话和 14 项交互验收，重点验证**问得少但问得准、已确认约束可追踪、用户要求直接出稿后不再追问、只改用户要求的部分**。

新的综合评分可增加两个维度：

6. **交互适度性**：该问时提问、已清楚时直接出稿；问题能帮助普通用户完成视觉选择。
7. **跨轮稳定性**：忠实记录用户已确认项与 Agent 建议项的区别；反馈后最小化变更。

交互模式的评分只用于内部自查，不要求每个回答把评分表展示给用户。
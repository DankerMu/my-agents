# 视觉风格图谱（按需选择，不可当作堆词清单）

> 目的：把普通语言转换成能观察到的造型、工艺、线条、纹理、布光和构图。每次选择 **1 个主风格 + 1–3 个兼容技法**；表中英文词用于英文模型提示词。风格不是越多越好。用户明确指定风格时优先尊重原意。

## 一、动画、漫画、角色插画

| 主风格 | 关键视觉特性与适用术语 | 优先用于 | 避免 |
| --- | --- | --- | --- |
| 日系 2D 赛璐璐 | anime illustration, crisp clean line art, flat color blocks, cel shading, controlled highlight shapes, expressive facial design | 角色、轻叙事、动漫场景 | skin pores、photorealistic face、PBR 材质 |
| 日系厚涂插画 | painterly anime illustration, soft-edged brushwork, layered shading, selective textured strokes, richly modeled fabric | 氛围插画、封面 | 过度平面矢量化、完全均匀的边缘 |
| 赛璐璐 + 局部厚涂 | clean anime outlines and cel-shaded base colors, with softly painted shadow transitions and textured material accents | 想要“清晰线稿 + 柔和质感” | 让整个画面同时写实渲染与纯矢量，破坏统一 |
| Q 版萌系 | chibi proportions, large head-to-body ratio, compact limbs, simplified shapes, playful gestures | 表情包、周边、贴纸 | 在没有要求时改掉角色既有年龄/身体结构 |
| 少年漫画黑白 | manga ink, expressive black-and-white linework, screen tones, hatching, dynamic speed lines | 单格漫画、分镜 | 强行加入彩色摄影光效 |
| 美式漫画 | bold contour ink, halftone dots, high-contrast flat colors, dramatic perspective, graphic action framing | 封面、英雄叙事 | 滥用会抢戏的对白泡泡 |
| 现代绘本 | soft gouache washes, subtle paper grain, simplified shapes, warm storybook palette, gentle edges | 亲子、儿童叙事 | 无故加入文字、过度拟真光泽 |
| 动画背景美术 | hand-painted environment, atmospheric depth, quiet color gradation, richly designed setting | 建筑、自然、故事背景 | 抢夺本应属于人物的焦点 |

**角色约束优先规则**：用户明确的发色、发型、耳朵、尾巴、配饰、衣服、表情、手持物必须保持；不要把两只耳朵变成四只、手持物变悬浮道具。脸、手和尾巴同时复杂时可简化遮挡与姿势，而不是添加“完美手指”魔法词。

## 二、绘画、传统艺术、工艺感

| 主风格 | 关键视觉特性与适用术语 | 避免 |
| --- | --- | --- |
| 水彩 | transparent watercolor washes, wet-on-wet bleed, soft pigment blooms, cold-pressed paper texture, reserved highlights | 油画式厚重塑料光泽 |
| 水粉/丙烯插画 | opaque gouache, matte pigment, bold painted shapes, visible brush textures | 通透水晶效果和强烈镜面反射 |
| 油画 | oil paint on canvas, layered brush strokes, controlled impasto, warm-cool pigment mixing, tactile paint surface | 无条件叠加摄影镜头术语 |
| 色铅笔/素描 | colored-pencil strokes, fine hatch marks, textured drawing paper, subdued shading | 完全光滑无颗粒材质 |
| 木刻/版画 | woodcut print, expressive carved linework, rough ink edges, limited color registration | 逼真 3D 阴影 |
| 中国工笔 | meticulous gongbi linework, controlled mineral pigments, silk-or-paper texture, precise contour, elegant negative space | 自动添加与时代/题材无关的宫廷服装 |
| 中国水墨 | Chinese ink wash painting, expressive ink gradients, dry-brush texture, rice-paper absorption, generous blank space | 把山水变成黑白摄影 |
| 敦煌壁画风 | mural pigments, mineral-color layering, flowing ornament, weathered plaster surface, stylized historical motifs | 虚构壁画来源与史实考证结论 |
| 复古海报 | screen-printed texture, reduced palette, aged paper, limited-color illustration, vintage typography | 未请求的年代或政治标志 |
| 像素艺术 | pixel art, deliberate low-resolution pixel clusters, limited palette, crisp hard edges, no anti-aliasing | 浅景深、细腻渐变、油画笔触 |
| 剪纸/拼贴 | cut-paper silhouettes, layered paper edges, tactile collage texture, carefully arranged overlapping forms | 模糊边缘使剪纸不成立 |

## 三、摄影、电影画面与写实表现

| 主风格 | 关键视觉特性与适用术语 | 适用边界 |
| --- | --- | --- |
| 纪实摄影 | documentary photograph, natural available light, candid gesture, plausible environment, restrained grading | 不得暗示虚构照片为真实新闻证据 |
| 电影剧照 | cinematic still, motivated practical lighting, coherent production design, foreground-background staging, controlled contrast | “电影感”不等于所有场景加蓝橙色、烟雾和横幅 |
| 环境人像 | environmental portrait, subject grounded in workplace, natural posture, context-rich background, believable skin/fabric texture | 避免不真实磨皮和过度商业摆拍 |
| 商业棚拍 | studio product photography, seamless backdrop, softbox reflections, clean silhouette, controlled specular highlights | 不要虚构商品 logo、功能、标签 |
| 美食摄影 | appetizing natural food texture, side-light, realistic glaze and steam, shallow focus where appropriate | 不把食品拍成玻璃/塑料 |
| 风光摄影 | landscape photograph, layered atmospheric perspective, natural terrain geometry, realistic clouds, coherent weather | 不必每次加入 HDR、超饱和或不真实地理地形 |
| 微距摄影 | macro photograph, close focusing distance, fine surface structure, narrow focus plane, natural bokeh | 不适合必须全图等清晰的信息设计 |
| 建筑摄影 | architectural photograph, corrected verticals, credible building geometry, daylight balance, unobstructed structural lines | 避免广角畸变影响结构准确性 |

**判断依据**：写实需要*物理可信*而不只是“照片级”：光源方向一致、皮肤和布料差异明显、建筑与人物比例可信、动作受重力约束、反射和积雪形成真实接触关系。

## 四、三维、材质、模型和产品可视化

| 主风格 | 关键视觉特性与适用术语 | 避免 |
| --- | --- | --- |
| 高品质 3D 角色 | stylized 3D character render, clean topology appearance, soft global illumination, tactile fabric, controlled subsurface scattering | 与明确“纯 2D 平涂”冲突 |
| PBR 产品渲染 | physically based materials, accurate roughness, soft studio reflections, measured geometry, clean product staging | 错误 logo、随意发明端口细节 |
| 黏土定格 | claymation aesthetic, handmade clay fingerprints, miniature set, soft tactile forms | 完美反光金属表面 |
| 微缩模型 | miniature diorama, crafted materials, scale-consistent props, tilt-shift impression when appropriate | 无目的夸张微距和失真的比例 |
| 低多边形 | low-poly 3D, faceted shapes, simplified polygon planes, matte shading | 真实皮肤毛孔与高细节毛发 |
| 等距轴测 | isometric illustration, parallel projection, consistent angle, layered miniature environment, clear object hierarchy | 使用强烈透视消失点 |

## 五、平面设计、信息可视化、科技与学术

| 主风格 | 关键视觉特性与适用术语 | 核心目标 |
| --- | --- | --- |
| 扁平矢量 | flat vector illustration, clean geometric shapes, limited palette, consistent strokes, clear negative space | 可识别、可扩展、不依赖复杂光影 |
| 极简品牌设计 | minimalist graphic design, distinctive silhouette, disciplined spacing, restrained palette, strong figure-ground contrast | 简洁而不是空白无内容 |
| 瑞士平面排版 | Swiss editorial design, asymmetric grid, strong typographic hierarchy, clean alignment, generous whitespace | 文本必须准确，勿乱造字母 |
| 科研机制示意 | scientific explanatory illustration, spatially accurate conceptual layers, clear arrows, simple legend, neutral background | 把机制关系讲清楚而不是炫酷 |
| 地理与灾害概念图 | terrain cutaway, stylized topography, glacier/lake/river relationships, restrained earth-tone palette, annotation-safe zones | **不**假定模型生成精确行政边界、经纬度和危险区 |
| 气象/水文信息图 | synoptic schematic, coherent weather fronts or water cycle, readable flow hierarchy, clean line encoding | 无数据时勿制作看似精确的天气图和洪水淹没图 |
| 工业技术爆炸图 | exploded technical illustration, clearly separated components, consistent projection, neutral background, alignment guides | 严禁随意增加零件与伪尺寸标注 |
| UI/仪表盘概念稿 | interface mockup, systematic grid, clear card hierarchy, high legibility, restrained shadows, coherent spacing | 不能替代可用代码/真实数据表 |
| 信息海报 | editorial poster, strong focal image, headline zone, deliberate text hierarchy, balanced negative space | 复杂字内容可后期人工排版 |

**科研/业务会议的默认处理**：主风格选“写实纪录 / 科研示意 / 简洁技术图”之一；使信息、结构、严肃性优先于酷炫气氛。缺少来源数据时在说明中注明“概念示意”，不得让提示词冒充验证过的真实卫星影像或分析结果。

## 六、当用户给出模糊风格词时

| 用户说法 | 可落地为（非固定配方） |
| --- | --- |
| “高级但不土” | limited and coordinated palette, material-specific highlights, considered negative space, uncluttered visual hierarchy |
| “可爱但不幼稚” | rounded but proportionate forms, playful pose, expressive eyes, selective decorative accents |
| “专业、适合公务或学术汇报” | restrained color coding, stable horizon, faithful forms, quiet lighting, low decorative noise, text-free focal area |
| “梦幻” | luminous haze, gentle gradients, atmospheric depth, coherent soft lighting, light particulate accents |
| “有力量” | dynamic diagonals, low viewpoint where appropriate, powerful silhouette, clear motion direction |
| “手绘感” | visible medium-specific texture, slight edge variation, imperfect hand-made strokes; select **one** real medium |
| “写实但不 AI 味” | believable light, natural imperfections, restrained saturation, authentic materials, credible gestures, no gratuitous glow |
| “干净清爽” | clear subject separation, few colors, even light, low clutter, consistent edges |

## 七、冲突消解速查

- `anime + photorealistic` → 选其一为主：可写“2D anime illustration with believable fabric construction”，不要在同一脸上同时要求真实毛孔与扁平面部。
- `cel shading + painterly` → 定义作用区域：“cel-shaded shapes and localized soft painterly shadows”。
- `flat vector + volumetric lighting` → 极少量渐变可服务于层次，但不再要求油画质地和电影烟雾。
- `scientific diagram + shallow DoF` → 改用 even sharp focus / precise linework，必要时仅将背景视觉弱化而非模糊关键信息。
- `night scene + bright warm lighting` → warm local lights on the subject, cooler blue shadows and sky；不是把整幅深夜画成正午。
- `transparent background + detailed environment` → 区分主体剪贴素材和背景成图两个交付，除非用户明确要求兼有。
- `real historical artifact + made-up ornamental detail` → 坚持参考资料；无法核实时避免声称为历史复原。
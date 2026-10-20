---
name: social-content-studio
version: 1.7.0
author: changjiashuai
license: "AGPL-3.0（见 LICENSE 与 references/THIRD-PARTY.md）"
description: "社交内容工坊：两级路由驱动的多平台多形式内容生产。先选平台（微信 / 小红书 / 通用），再选该平台的内容形式。微信支持图文（图片消息 / 小绿书）、公众号长文、视频号视频；小红书支持图文笔记、视频笔记；通用承载代码驱动的产品宣传片与版本更新片。产出前强制先问平台再问形式（均支持多选），再进对应流水线；多选时按「事实源 → 静态切片 → 动态切片」串行执行以保证口径一致。通用平台自带完整制作体系：19 个方法论分册 + 6 个工程脚本 + 起步工程 + 默认样式 + 手法样例 + 原创音效，全部原生内置，无外部 skill 依赖。触发词：微信图文、小绿书、公众号文章、公众号排版、视频号、小红书图文、小红书笔记、小红书视频、多平台分发、产品宣传片、版本更新片、changelog、social content、product promo。"
---

# 社交内容工坊 social-content-studio

**一个自带全部能力的独立 skill。** 通用平台（影片）的完整制作体系——19 个方法论分册、6 个工程脚本、起步工程、默认样式、手法样例、配乐示例与原创音效——全部原生在本 skill 内；微信与小红书两个平台包在此之上按**两级路由**组织：**先选平台，再选该平台下的内容形式**。本 skill 不依赖任何外部 skill，可独立分发。

- **为什么平台优先**：平台决定硬规格（画幅、字数、体积、封面比例、审核红线），形式决定叙事骨架。两者正交。平台优先之后，新增一个平台只是叠加一个平台包——不动共用底座、不动已有平台包、不动通用平台的影片体系。
- **基线在哪**：已跑通的能力固化在 [references/BASELINE.md](references/BASELINE.md)（能力清单 + 规格版本 + 三条校验命令）。**扩平台先看基线。**
- **作者**：changjiashuai｜**授权**：AGPL-3.0（见 [LICENSE](LICENSE)）｜**来源与授权范围**：[references/THIRD-PARTY.md](references/THIRD-PARTY.md)

---

## 0. 两级内容路由（强制前置交互）

**在任何内容产出动作之前，先问平台，再问形式。** 没有这两次选择，不要写 `DIRECTION.md`、不要初始化工程、不要生成任何素材。
唯一例外：用户在同一条消息里已经写清了平台与形式（例如"做一条小红书视频笔记"），把该指定当作回答，确认一句后直接执行。

**第一级 · 投放平台（多选）**

| 序号 | 平台 ID | 标签 | 覆盖的形式 |
|---|---|---|---|
| 1 | `wechat` | `1 微信` | 图文（图片消息 / 小绿书）、公众号长文、视频号视频 |
| 2 | `xiaohongshu` | `2 小红书` | 图文笔记、视频笔记 |
| 3 | `generic` | `3 通用（自有渠道）` | 产品宣传片 / 版本更新片（可发官网、社群、其他渠道） |
| 4 | `x` | `4 X（Twitter）` | 文章（长文） |

**第二级 · 内容形式（对每个已选平台各选一次，均可多选）**

- **微信** → `1 图文（图片+文案）` / `2 公众号（长文）` / `3 视频号（视频）`
- **小红书** → `1 图文笔记` / `2 视频笔记`
- **通用** → `1 影片（片型由内容定：产品片 / 科普 / 数据 / 叙事）`
- **X** → `1 文章（长文）`

**多选时的执行顺序**：先定**事实源**（承载最完整论证与数据出处的那个形式），再做其余**静态形式**，最后做**动态形式** —— 即「事实源 → 图文切片 → 视频切片」。
事实源判定规则、追问话术、边界情况与 `plan.json` 契约见 [两级内容路由](references/core/routing.md)。

**选择结果写入 `plan.json`**，**后续所有步骤只从 `plan.json` 读形式，不允许中途静默改**；确需变更时改 `plan.json` 并在 `BRIEF.md` 记一条理由。

> 第 3 项 `通用` 必须存在：产品宣传片与版本更新片由它承载。**去掉它等于削减已有能力。**

---

## 目录结构

```
social-content-studio/
├── SKILL.md                        # 主入口：两级路由 + 影片总纲（7 步流程 / 片型 / 硬约束 / 工程入口）+ 平台包要点
├── README.md                       # 能力总表、组织原则、扩展指引、版本记录
├── LICENSE                         # AGPL-3.0（作者 changjiashuai）
├── agents/openai.yaml              # Agent 界面描述
├── .github/workflows/regression.yml # CI：离线回归 + 模板探测 + 可选集成回归
├── references/
│   ├── BASELINE.md                 # ★ 基线：能力清单、规格版本、校验命令、扩展契约
│   ├── THIRD-PARTY.md              # 本包授权范围 + 平台规则引用质量 + 素材版权约束
│   ├── core/                       # ── 平台无关的共用底座 ──
│   │   ├── routing.md              # ① 两级路由协议、事实源判定、plan.json 契约、执行顺序
│   │   ├── pipeline.md             # ② 生产管线：取材/方向/渲染/编码/媒体标准/验收纪律
│   │   ├── cross-platform.md       # ③ 跨平台一致性、素材复用、发布与挂载
│   │   └── platform-schema.md      # ④ 平台接入契约：新增平台要做哪 5 件事
│   └── platforms/                  # ── 平台包（彼此独立，可单独增删）──
│       ├── wechat/
│       │   ├── PLATFORM.md         # 平台入口：形式索引 + 平台共性 + 红线
│       │   ├── specs.md            # 微信官方规格总表（含正文 HTML / CSS 白名单）
│       │   ├── image-text.md       # 图文（图片消息 / 小绿书）
│       │   ├── mp-article.md       # 公众号长文
│       │   └── channels.md         # 视频号视频
│       ├── xiaohongshu/
│       │   ├── PLATFORM.md         # 平台入口：形式索引 + 平台共性 + 红线
│       │   ├── specs.md            # 小红书规格总表（含来源质量提示与平台红线）
│       │   ├── image-text.md       # 图文笔记
│       │   └── video.md            # 视频笔记
│       ├── generic/
│       │   ├── PLATFORM.md         # 平台入口 + 分册索引 + 工程与资产 + 红线
│       │   ├── specs.md            # 兜底规格 + 片型 + 两层自检覆盖范围
│       │   └── motion-film/        # ── 影片 19 个分册（细则）──
│       │       ├── direction.md            影片方向（定标杆 → 推导 → 固化 → 镜头表）
│       │       ├── web-first.md            网址优先（只有官网时怎么调查；三级证据源）
│       │       ├── research-brief.md       调研摘要（RESEARCH.md 契约，B/C 级必写）
│       │       ├── style-derivation.md     风格推导（信息形状 → 运动语言 → 滑块 → 不变量与禁令）
│       │       ├── rhythm-brief.md         节奏单（路线 / 能量曲线 / 密度 / 死时间）
│       │       ├── story-and-copy.md       分镜、文案与节奏
│       │       ├── visual-vocabulary.md    视觉手法词汇
│       │       ├── component-pipeline.md   真实组件到可渲染画面
│       │       ├── starter.md              起步工程运行时结构
│       │       ├── repo-and-style.md       仓库与风格审计
│       │       ├── onboarding.md           依赖安装（仅缺项时读）
│       │       ├── voiceover.md            配音（edge-tts 优先、按气质选音色、禁用系统机器音）
│       │       ├── audio-sourcing.md       配乐与音效来源、编曲与对位
│       │       ├── audio-and-qa.md         声音与成片检查
│       │       ├── review.md               审片（含独立审片与反馈定位）
│       │       ├── cover.md                封面 3:4 / 4:3 / 16:9
│       │       ├── case-study.md           案例复盘
│       │       ├── provenance.md           内部溯源（FACTS 底账，不随片交付）
│       │       └── pipeline-notes.md       本机实测管线与环境坑 28 条
│       └── x/
│           ├── PLATFORM.md         # 平台入口：长帖 vs Article 的分界 + 红线
│           ├── specs.md            # X 规格总表（Article 长度/标题/封面/内容能力，含来源质量）
│           └── article.md          # X 文章（长文）
├── assets/
│   └── platforms/
│       ├── wechat/
│       │   ├── image-text/card.template.html       # 3:4 图卡（1080×1440）
│       │   ├── article/article.template.html       # 公众号正文片段（全内联样式）
│       │   ├── article/cover-235.template.html     # 头条封面 2.35:1（900×383）
│       │   ├── article/cover-11.template.html      # 次条封面 1:1（500×500）
│       │   └── channels/cover-67.template.html     # 视频号封面 6:7（1080×1260）
│       ├── xiaohongshu/
│       │   ├── image-text/note.template.html       # 图集页 3:4（1080×1440）
│       │   └── video/cover-34.template.html        # 视频封面 3:4（1080×1440）
│       └── generic/
│           ├── starter/            # 起步工程：运行时/构建/预览/渲染/封面/静帧/适配器/fixture
│           ├── fallback/           # 默认样式「纸墨」（纸白 / 墨黑）；本包原创，AGPL-3.0
│           ├── fx-lab/             # 6 个可改写的手法样例
│           └── audio/             # 代码合成配乐示例 + sfx/（11 个原创 WAV）+ manifest.json
├── scripts/
│   ├── social_specs.json           # ★ 规格单一事实来源：platforms.<平台>.forms.<形式>
│   ├── check_social_delivery.py    # 平台线产出物自检（尺寸/比例/体积/字数/禁用项/风险词）
│   ├── render_social_assets.mjs    # 无头 Chrome 批量导出图卡与封面 + 模板尺寸探测
│   └── video-line/                 # ── 影片工程脚本 ──
│       ├── init_project.py         初始化隔离的视频工程
│       ├── check_environment.py    环境预检（只报告缺项）
│       ├── sfx_landmarks.py        实测音效起音点/峰值时间/峰值电平
│       ├── mix_audio.py            混音、音乐让位、独立音轨与证据报告
│       ├── make_sfx.py             改变音色时重新生成内置音效
│       ├── make_voiceover.py       生成配音与字幕（edge-tts；无可用 TTS 时退出码 3）
│       └── check_delivery.py       ★ 影片结构与媒体自检（按片型分派）（见 generic/specs.md §3）
└── tests/
    ├── test_check_social_delivery.py   平台线回归（纯标准库）
    ├── test_video_line_regressions.py  视频线回归（纯标准库；混音/落点项需 ffmpeg）
    └── integration.mjs                 真实构建 + 无头浏览器集成回归（可选，需 node_modules）
```

**分层的三条原则**（后续扩展请遵守）：

1. **平台优先，平台包互不依赖。** 跨平台的关注点进 `core/`，平台专属的关注点进 `references/platforms/<平台>/` 与 `assets/platforms/<平台>/`。
2. **新增平台只做 5 件事**（详见 [平台接入契约](references/core/platform-schema.md)）：加 `references/platforms/<p>/`、加 `assets/platforms/<p>/`、规格 JSON 加一个节点、自检脚本登记一个检查函数、路由表加一行。**不动 `core/` 语义、不动已有平台包、不动通用平台的影片体系。**
3. **规格只有一个事实来源**（`scripts/social_specs.json`）。模板画布尺寸、自检阈值都从它读；平台改规则只改这一处。

---

## 平台与形式总表

| 平台 | 形式 ID | 产出目录 | 规格 |
|---|---|---|---|
| 微信 | `wechat/image-text` | `export/wechat/image-text/` | [wechat/specs.md](references/platforms/wechat/specs.md) §2 |
| 微信 | `wechat/mp-article` | `export/wechat/mp-article/` | 同上 §1（含 HTML 白名单） |
| 微信 | `wechat/channels` | `export/wechat/channels/` | 同上 §3 |
| 小红书 | `xiaohongshu/image-text` | `export/xiaohongshu/image-text/` | [xiaohongshu/specs.md](references/platforms/xiaohongshu/specs.md) §1 |
| 小红书 | `xiaohongshu/video` | `export/xiaohongshu/video/` | 同上 §2 |
| 通用 | `generic/motion-film` | `export/generic/motion-film/` | [generic/specs.md](references/platforms/generic/specs.md)（兜底）+ 下方总纲与分册 |
| X | `x/article` | `export/x/article/` | [x/specs.md](references/platforms/x/specs.md) §1 |

---

## 通用平台 · 影片

代码驱动的**产品宣传片**与**版本更新片**，对应形式 `generic/motion-film`。
**本章是总纲**（术语 + 7 步流程 + 硬约束 + 工程入口）；**细则是 `references/platforms/generic/motion-film/` 下的 19 个分册**，每一步都链到对应分册。平台包入口见 [generic/PLATFORM.md](references/platforms/generic/PLATFORM.md)。

用真实组件讲清楚一个软件产品或一次更新，让画面、文案和声音一起推进。本文术语：**默认样式**指 `assets/platforms/generic/fallback/`（「纸墨」，纸白 / 墨黑双色调）；**起步工程**指 `assets/platforms/generic/starter/`，初始产物称**技术样片**；**方向文件**指视频工程里的 `DIRECTION.md`；音效事件统一保存在 `audio.cues`。

### 流程

1. **确认范围、平台与风格。** 已有工程沿用 brief 和用户决定，只处理本次修改。新片补齐：产品/仓库、发布渠道、时长与画幅、语言、是否允许链接，以及用户有没有参考视频。**范围与产品平台面必须由用户拍板**，仓库只能说明有哪些版本，说明不了用户想宣传什么：覆盖全量产品、最新一个版本周期，还是指定版本区间？覆盖哪些平台面（桌面端／CLI·TUI／移动端／服务端 API）？没指定时问一次，答案写入 `plan.json` 的 `scope`（如 `{"versions":"v0.10.12..v0.11.0","platforms":["cli-tui"]}`）并同步进 BRIEF。风格没定时问一次："沿用代码库自己的设计风格（推荐），还是默认的纸白／墨黑风格？"`repo` 用产品设计；`default` 用默认样式包装；`hybrid` 保留产品识别、调整外层排版。**只有网址时**还要确认官网地址与「能不能用公开截图」，并说明由此片子会走主张/证据路线而非功能演示。常见起点：横版、45–60 秒、中文。
2. **初始化并检查环境。** 按下方[工程入口](#工程入口)初始化独立视频目录，再运行环境检查；只对报告的缺项加载 [依赖安装](references/platforms/generic/motion-film/onboarding.md)，装完复查。已有工程直接检查，不重新初始化。
3. **调查产品，接通组件。** **先判证据级别**：有源码走 [仓库与风格审计](references/platforms/generic/motion-film/repo-and-style.md)；只有截图录屏或只有官网，走 [网址优先](references/platforms/generic/motion-film/web-first.md)，并**先写 `RESEARCH.md`**（[调研摘要](references/platforms/generic/motion-film/research-brief.md)，B/C 级必写，`check_delivery.py` 会校验）。级别写进 `plan.json.evidenceLevel`，它决定能做什么形状——**只有网址时不做功能演示镜头，也不画假界面**。按审计确定功能、发布状态和证据，记下设计语言、暗色主题和可做母题的产品元素。在浏览器里挂载真实业务组件：补 provider，接口用 fixture，交互用真实点击和输入，放大到视频尺度（[起步工程](references/platforms/generic/motion-film/starter.md)、[组件接入](references/platforms/generic/motion-film/component-pipeline.md)）。先接通一个功能镜头并出静帧。
4. **定方向，写 `DIRECTION.md`。** 按 [影片方向](references/platforms/generic/motion-film/direction.md)：先定标杆（学什么 / 绝不拿什么），拆解参考，提炼产品气质；按 [风格推导](references/platforms/generic/motion-film/style-derivation.md) 从内容推出三个**表达逻辑不同**的方向，选一个并写出理由；列出 3–5 个"因为产品有 X、所以用 Y"的专属手法，并避开本工作区上一支片子的手法；把画面规范写成具体数字；写到每一秒的镜头表（文案写法见 [分镜、文案与节奏](references/platforms/generic/motion-film/story-and-copy.md)）。用户想先看方向时，给三个方向和 3–6 张关键静帧，等反馈；否则继续。
5. **逐镜头搭建。** 每个镜头 = 视图组件 + builder（GSAP 主时间轴、`onRender` 画布层、`onDrive` 真实交互），时间只从 `plan.json` 读。手法从 [视觉手法词汇](references/platforms/generic/motion-film/visual-vocabulary.md) 里选能从产品推导的，`assets/platforms/generic/fx-lab/` 的样例改写后再用。每搭完一个镜头就出静帧，对照镜头表（[审片](references/platforms/generic/motion-film/review.md)）。
6. **配音、配乐与音效。** 需要口播时按 [配音](references/platforms/generic/motion-film/voiceover.md)：用户给了录音或音色就直接用；否则**优先 edge-tts**，按片子气质选音色并把理由写进 `plan.json.voiceover`；edge-tts 不可用再找其他免费 TTS；**都没有时停下来问用户，绝不用系统机器音**（`say` / SAPI / eSpeak 一律禁用）。生成后必须试听并核对转写（多音字、数字读法是高频错误）。再按 [配乐与音效](references/platforms/generic/motion-film/audio-sourcing.md) 选音乐来源（用户提供 → 本机可用的生成模型 → 代码合成），编曲从镜头边界推出来，音色从产品气质推出来；音效先用录音素材，缺项再用内置 WAV。用 `sfx_landmarks.py` 实测落点和电平，按 [混音与验收](references/platforms/generic/motion-film/audio-and-qa.md) 对位、让位、混音。
7. **审片并交付。** 导出全片，看 2 fps 联系表、每个转场的 10 fps 条带和信息密集镜头的全尺寸帧，按 [审片](references/platforms/generic/motion-film/review.md) 修改后重新导出（有条件时让独立审片人看一次，并问「哪一段开始走神」）。运行 `check_delivery.py`（`pacing` 只提示该去看哪一段）。交付 MP4、可复现工程和少量预览；说清哪些是自动检查、哪些实际看过/听过、哪些仍未验证。要发布时按 [封面](references/platforms/generic/motion-film/cover.md) 做 3:4 / 4:3 / 16:9 封面，用户没提就用一句话问一下。历史问题查 [案例复盘](references/platforms/generic/motion-film/case-study.md)。

### 硬约束

- **真实功能。** 正式片至少一项可追溯的主张；每项记录发布状态、来源和白话解释。演示数据可以固定，功能效果与数字要有证据。上屏的每个数字在 `evidence/FACTS.md` 有一行出处（见 [内部溯源](references/platforms/generic/motion-film/provenance.md)）。**FACTS 是内控底账：不随片交付、不主动展示**；用户问起来源时如实回答，证据链断裂时用一句话说明结论。范围与平台以 `plan.scope` 为准，交付时声明没有覆盖的平台面，避免观众以为片子讲的是产品全貌。
- **原组件，视频尺度。** 功能镜头接入实际业务组件、原样式及状态，界面正文在成片里 ≥ 22px（1080p）。抽象化只用于取景、布局和外层动画。平台确实无法接入时，记录阻碍和替代方式，遵从已有授权。
- **先推导，再写代码。** 正式片必须有 `DIRECTION.md`：标杆、信息形状与运动语言、五轴性格、五条不变量与三条禁令（推导方法见 [风格推导](references/platforms/generic/motion-film/style-derivation.md)）、专属手法、节奏单（[节奏单](references/platforms/generic/motion-film/rhythm-brief.md)）、画面规范、镜头表。**风格是推导结果，不是从菜单里挑的。**
- **不套模板。** 每个视觉手法都要能说出它对应产品的哪一点。案例和 fx-lab 是推导示范，不是风格包；同一工作区连续做片，不原样复用上一支的开场、章节和背景手法。片内也要避免所有元素同一种入场、同一种转场。
- **清楚排版。** 宣传标题默认英文、中文各一个 span，分别指定字体，中文无衬线；中文说明交代对象、动作和结果。产品内部字体保持原设计；用户指定的语言/字体优先。
- **首帧就是完整画面。** 没有单独上传封面时，X / Threads 等平台会直接抓第一帧当缩略图。所以片子的前 5–10 帧要放一个完整画面，通常是开场段落的完成态；之后再淡出，开场动画照常播放。第一帧不能是空白底色，也不能是等待入场的背景。`check_delivery.py` 会测前 5 帧。
- **完整声音。** 默认音乐与独立动作音效都进音轨，关键反馈听得见、音画同步。用户要求静音或省略音效时，记录 `audioExceptionReason`。
- **隔离工程。** 源码适配、展示依赖和构建配置放在视频工程；原产品代码和依赖不动。
- **授权与真实验收。** 素材保留来源和许可。包内全部内容（含默认样式「纸墨」与起步工程）均为本包原创，随 [AGPL-3.0](assets/platforms/generic/fallback/SOURCE.md) 提供，**无商用限制、无第三方组件**（见 [references/THIRD-PARTY.md](references/THIRD-PARTY.md)）。内置音效与配乐示例的来源见 [音频来源](assets/platforms/generic/audio/SOURCE.md)。自动检查只证明结构与文件一致；视觉、语义和听感靠实际审阅，没有试听就如实说明。

### 工程入口

先确认风格，再初始化；三种风格都可以传 `--repo`，其中 repo/hybrid 必填：

```sh
python3 <skill-dir>/scripts/video-line/init_project.py --output <video-dir> --style repo --repo <repo-dir>
python3 <skill-dir>/scripts/video-line/check_environment.py --project <video-dir> --engine browser
# 缺项 → 按 references/platforms/generic/motion-film/onboarding.md 补装 → 使用 --force 复查。

# 出片之后（结构与媒体自检）
python3 <skill-dir>/scripts/video-line/check_delivery.py <video-dir>/plan.json \
  --video <video-dir>/renders/final.mp4 --mix-report <video-dir>/evidence/audio-mix.json
```

HyperFrames 工程使用 `--engine hyperframes`。新工程附 10 秒技术样片（刻意没有风格，只验证链路）和一份只有问题的 `DIRECTION.md`。

**投放预设 `--preset`**（默认 `generic`，与 v1.0.x 行为一致）：影片体系是同一套，但不同渠道的画幅与节奏要求相反，预设把它们一次定好，并写进 `plan.json.preset` 与 `BRIEF.md`。

| 预设 | 画幅 | 预设带来的硬要求 |
|---|---|---|
| `generic` | 1920×1080 | 默认横版，画幅按渠道自定 |
| `xhs-vertical` | 1080×1920 | 前 3 秒即钩子（不要片头/问候/空镜）；封面单独做 3:4，不用首帧；30s–3min 最稳 |
| `channels-horizontal` | 1920×1080 | 第 1 帧即默认封面，必须完整；横版封面会被主页裁成 6:7；短标题 ≤16 字 |
| `channels-vertical` | 1080×1920 | 同上，封面按 1080×1260（6:7） |

预设只定画幅与文字要求，**不替你写方向**——`DIRECTION.md` 仍然要回答产品推导那几问。

**分册索引**（细则都在 `references/platforms/generic/motion-film/`）：

| 分册 | 讲什么 |
|---|---|
| [影片方向](references/platforms/generic/motion-film/direction.md) | 定标杆 → 提炼气质 → 推导三个方向 → 专属手法 → 反重复（六项四差异）→ 画面规范 → 镜头表 |
| [网址优先](references/platforms/generic/motion-film/web-first.md) | 只有官网/文档时怎么调查：A/B/C 三级证据源、公开可引用来源、三条硬线（不假造界面） |
| [调研摘要](references/platforms/generic/motion-film/research-brief.md) | `RESEARCH.md` 契约：四问、证据级别与边界、与 FACTS/推导的关系；B/C 级必写 |
| [风格推导](references/platforms/generic/motion-film/style-derivation.md) | 给主题/数据后自行推出风格：8 种信息形状 → 10 种运动语言 → 5 个性格滑块 → 单帧主构成 → 5 条不变量 + 3 条禁令 |
| [节奏单](references/platforms/generic/motion-film/rhythm-brief.md) | 先画能量曲线再排镜头：连续/蒙太奇/混合、爆点位置、每小节事件密度、死时间判据、文字停留 |
| [分镜、文案与节奏](references/platforms/generic/motion-film/story-and-copy.md) | 从更新清单到故事、中文文案说人话、标题中英分工、文案试读、动作与停留 |
| [视觉手法词汇](references/platforms/generic/motion-film/visual-vocabulary.md) | 按作用分组的手法：表达什么、从哪里推导、怎么实现、何时不用 |
| [起步工程](references/platforms/generic/motion-film/starter.md) | 运行时结构（seek、GSAP 主时间轴、`onRender`、`onDrive`）、接入仓库、样式链、plan 字段 |
| [组件接入](references/platforms/generic/motion-film/component-pipeline.md) | 真实业务组件到可渲染画面：找入口、补 provider、fixture、状态与动画、复用证据 |
| [仓库与风格审计](references/platforms/generic/motion-film/repo-and-style.md) | 更新事实与证据、原组件及设计依赖审计、默认样式的范围 |
| [依赖安装](references/platforms/generic/motion-film/onboarding.md) | 仅有缺项时读：按报告装，装完 `--force` 复查 |
| [配音](references/platforms/generic/motion-film/voiceover.md) | edge-tts 优先、按气质选音色与参数、禁用系统机器音、无可用 TTS 时怎么问用户 |
| [配乐与音效](references/platforms/generic/motion-film/audio-sourcing.md) | 音乐来源优先级、先编曲再合成、音效先找录音素材、对位、来源留存 |
| [混音与验收](references/platforms/generic/motion-film/audio-and-qa.md) | 从"写了音效"到"真的听得见"、音乐让位、卡点、混音、自动与人工检查 |
| [审片](references/platforms/generic/motion-film/review.md) | 三个审片节点、独立审片与「哪段走神」、反馈定位四件套、联系表与转场条带、常见问题对照表 |
| [封面](references/platforms/generic/motion-film/cover.md) | 3:4 / 4:3 / 16:9 三种比例的布局思路、选图、文案与导出（起步工程的 `cover.mjs`） |
| [案例复盘](references/platforms/generic/motion-film/case-study.md) | 原案例复盘：有效做法、真正修过的问题、第二个/第三个项目的经验 |
| [内部溯源](references/platforms/generic/motion-film/provenance.md) | `evidence/FACTS.md` 底账：上屏数字的出处与状态。**内部核查用，不随片交付、不主动展示** |
| [本机实测管线与环境坑](references/platforms/generic/motion-film/pipeline-notes.md) | 已实跑验证的渲染/编码/音频管线 + 28 条环境坑（全平台共用） |

**配套资产**：

| 资产 | 讲什么 |
|---|---|
| `assets/platforms/generic/fx-lab/` | 流线场、粒子汇聚、字符场、发光地平线、切片、环绕的可改写样例 |
| `assets/platforms/generic/audio/score-example-keys.py`、`score-example-cinematic.py` | 两种气质的代码合成配乐示例，借手法，不照搬曲子 |
| [内置音效](assets/platforms/generic/audio/SOURCE.md) | 11 个原创 WAV；需要改音色时运行 `scripts/video-line/make_sfx.py --output <new-sfx-dir>` |
| `assets/platforms/generic/starter/` | 起步工程（`init_project.py` 的复制源），含构建/预览/渲染/封面/静帧脚本 |

**维护自检**（改了脚本、规格表或模板之后跑）：

```sh
python3 -m unittest discover -s <skill-dir>/tests                          # 全部离线回归
node <skill-dir>/tests/integration.mjs --modules <video-dir>/node_modules   # 可选：真实构建 + 无头浏览器
```

---

## 平台包要点

各平台包**共用同一套取材与判据**（见 [生产管线](references/core/pipeline.md)），只在「载体形态」上分叉。共用底座四条纪律：

- **取材同源。** 不做第二套产品调研——沿用影片第 3 步的仓库审计结果（真实功能、发布状态、证据）。**没有可追溯主张的内容不许发布**，这条从影片继承，不因平台是图文而放松。
- **方向先行。** 影片的 `DIRECTION.md` 同样适用于全部平台包：跨平台共用同一份主视觉规范（主色、字体、图形母题、口号），只在画幅与信息密度上分叉。多平台时这一点是强制项。
- **规格必须机器校验。** 每个形式交付前跑 `scripts/check_social_delivery.py`，逐项对照 `scripts/social_specs.json`。**尺寸、比例、字数、文件大小一律不靠肉眼**——这与产品片第 18/20/27 条的精神一致（版面自检脚本化，见 [pipeline-notes](references/platforms/generic/motion-film/pipeline-notes.md)）。
- **中文字体与排版不靠自定义字体。** 各平台都不保证加载外部字体，正文一律用系统字体栈（`-apple-system` / `PingFang SC` / `Microsoft YaHei`）。需要特殊字体时，把那一段做成图。

### 微信（[平台包](references/platforms/wechat/PLATFORM.md)）

三条形式的形态、流程、要点、红线与交付清单见平台包。**完整参数以 [wechat/specs.md](references/platforms/wechat/specs.md) 为唯一事实源**，自检脚本也从同一个 `social_specs.json` 读——这里不复制参数，只列**做错了要返工**的三条：

- **公众号 HTML 白名单是最大的坑**：`<style>`、`<script>`、外链 CSS、`position`、`@media` 全被清洗，`class` 保留却不生效 → 样式**只能全内联**，图片 `src` 必须换成 `mmbiz.qpic.cn` 素材库地址。
- **摘要不填会被抓成正文前 54 字**，必须手写；发多条时头条标题压在封面上，标题区要留低干扰。
- **图片数量官方口径不一致**（订阅号助手端 20 张 / 部分入口 9 张）→ 推荐 6–9 张，脚本对 10–20 张只报警告，交付时写"以编辑器实际提示为准"。

细则 → [image-text.md](references/platforms/wechat/image-text.md) ｜ [mp-article.md](references/platforms/wechat/mp-article.md) ｜ [channels.md](references/platforms/wechat/channels.md)

### 小红书（[平台包](references/platforms/xiaohongshu/PLATFORM.md)）

> ⚠️ 小红书**未公开**完整素材规格文档，`social_specs.json` 里相关条目全部标了 `uncertainty` + `safeMax`。**凡标 uncertainty 的都不是确定值**：脚本只按 `safeMax` 报 WARN，交付时写成"以编辑器实际提示为准"。参数与来源质量见 [xiaohongshu/specs.md](references/platforms/xiaohongshu/specs.md)。

只列必须动手前知道的三条：

- **整篇笔记只能用一种比例**（推荐 3:4 1080×1440）；**首图即封面**，关键信息压在中心安全区。
- **视频封面必须单独做 3:4**，不要拿视频首帧；前 3 秒即钩子，不要片头与问候。
- **平台红线比微信严**：严禁站外导流（微信号 / "vx" / "加我" / 二维码 / 其他平台链接）、禁用绝对化用语、禁止搬运或带其他平台水印。自检脚本会扫 `meta.json` 与 `copy.md` 的风险词，但语境要人工复核。

细则 → [image-text.md](references/platforms/xiaohongshu/image-text.md) ｜ [video.md](references/platforms/xiaohongshu/video.md)

### 通用（[平台包](references/platforms/generic/PLATFORM.md)）

形式 `generic/motion-film`：**片型由内容决定，不预设**。走上文「通用平台 · 影片」的 1–7 步（画幅按渠道定、时长自定）。
它不绑定投放平台，所以**没有平台侧硬规格**。

**四种片型**（`plan.json` 的 `filmKind`；不填等于 `product`）：

| 片型 | 什么时候用 | 专属验收 |
|---|---|---|
| `product` | 讲某个产品的功能、价值或更新 | **必须有可追溯的功能主张 + 原组件**（默认值，最严格） |
| `evidence` | 以数据或事实为主 | 必须有 `evidence/FACTS.md` 或 `RESEARCH.md` |
| `explainer` | 讲清一个概念、机理、原理 | 同上；不要求功能主张 |
| `story` | 以情感、人物、叙事为主 | 不要求主张；虚构内容建议写 `fictionNote` |

判据是**内容本身**：讲土星环怎么形成 → `explainer`；讲某公司 Q3 数据 → `evidence`；讲一个创始人的故事 → `story`；讲产品新功能 → `product`。
**不声明片型时按 `product` 验收**，所以放宽永远是主动选择，不是默认漏洞。

无论哪种片型，**都不许假造界面**：没有产品组件时不画"像但不准"的 UI（见 [网址优先](references/platforms/generic/motion-film/web-first.md) §3）。

自检分两层：影片有**自带的结构与媒体自检**（`scripts/video-line/check_delivery.py`，按片型分派：方向文件、主张/溯源、时间线、媒体参数、节奏、首帧）；平台线自检 `check_social_delivery.py` 只做兜底（文件存在、可探测、时长 >0）。**两层都不能替代人工审片**——覆盖范围与「它不证明什么」逐条写在 [generic/specs.md](references/platforms/generic/specs.md) §3。

### X（[平台包](references/platforms/x/PLATFORM.md)）

形式 `x/article`：长篇公开写作。**只做 Article**；「一条说清」的长帖（约 2.5 万字符、无标题无分节）不属于本形式，判据是**有没有结构**，不是字数。

动手前必须知道的三条：

- **需要注意付费订阅**（Premium 级，非 Premium+）。没有权限就无法发布，先确认。
- **入口即点击**：Article 不在时间线内展开，用户先看到标题 + 封面 + 第一段 → **第一段同时是摘要**，必须 2–3 句说清，不放「最近很多人问我」这类铺垫。
- **长度上限口径不一**：约 10 万字符来自第三方汇总，X 未在公开帮助页给出固定数字 → 脚本按稳妥上限 75,000 字符判 WARN，交付时写「以编辑器实际计数为准」。

格式支持标题、粗体、列表、图片、视频、嵌入帖子，但**支持不等于都用**：粗体全文 ≤10 处，列表只用于步骤与并列项（讲不了因果）。

细则 → [article.md](references/platforms/x/article.md) ｜ 规格与来源 → [x/specs.md](references/platforms/x/specs.md)

---

## 跨平台硬约束

除影片的全部硬约束外，平台化之后追加：

- **先问后做。** 未取得平台与形式的选择（或用户已明确指定）之前，不得开始产出。选择写入 `plan.json`，不允许静默变更。
- **规格即红线。** 尺寸/比例/字数/体积一律脚本校验并给出实测数值，不许口头声称"符合规范"。用户提供的既有素材不达标时，先报告不达标项与影响，再给修复方案，不擅自改用户原始素材。各形式的字数类元数据写进 `export/<平台>/<形式>/meta.json`（契约见各平台文档「交付清单」），否则字数项只报警告。
- **不伪造平台规则。** 规格参数以各平台包的 `specs.md` 里标注了来源的条目为准；官方未明确或口径不一致的（如"图片消息到底 9 张还是 20 张""小红书 15 分钟还是 60 分钟"），必须写成"以编辑器实际提示为准"，**不得编造确定值**。
- **公众号正文不许夹带平台不支持的东西。** 交付的正文片段里不得出现 `<style>`、`<script>`、外链 CSS、`position`、`@media`、外链图片地址——自检脚本会检。
- **小红书文案不许越平台红线。** 不得出现站外导流与绝对化用语——自检脚本会扫，人工复核语境。
- **口径一致。** 同一主张在所有形式里必须同一口径；同步的免责 / 口径说明不得为了传播力删减。数据类主张在事实源里给来源，在其他形式里给可核对的简称。
- **跨平台不设计互相导流。** 微信与小红书是隔离生态：图片消息不支持外链，小红书严打站外导流。多平台同做时改成「同一主视觉 + 同一口号 + 各平台各说各的」，让用户认出是同一主体，而不是让内容互相跳转（见 [core/cross-platform.md](references/core/cross-platform.md) §4.3）。
- **图片版权与真实素材。** 沿用影片的「素材保留来源和许可」。产品截图要使用真实产品界面，不用重绘冒充。

---

## 工具入口

```sh
SKILL=~/.workbuddy/skills/social-content-studio

# 0) 先做两级路由：先选平台，再选形式，写入 plan.json（见第 0 章与 core/routing.md）
#    写完立刻校验契约：形式是否登记、factSource/order/selection 是否自洽、「先静后动」是否被破坏
python3 $SKILL/scripts/check_social_delivery.py --check-plan <content-dir>/plan.json

# ── 影片（generic/motion-film）──
# --preset 决定画幅与节奏基准：generic（默认 16:9）/ xhs-vertical（9:16）/ channels-horizontal / channels-vertical
python3 $SKILL/scripts/video-line/init_project.py --output <video-dir> --style repo --repo <repo-dir> [--preset xhs-vertical]
python3 $SKILL/scripts/video-line/check_environment.py --project <video-dir> --engine browser
python3 $SKILL/scripts/video-line/sfx_landmarks.py <video-dir>/assets/sfx/*.wav
python3 $SKILL/scripts/video-line/mix_audio.py    <video-dir>/plan.json
python3 $SKILL/scripts/video-line/make_sfx.py     --output <new-sfx-dir>
python3 $SKILL/scripts/video-line/make_voiceover.py <video-dir>/plan.json   # 配音：先 --doctor 体检
python3 $SKILL/scripts/video-line/check_delivery.py <video-dir>/plan.json \
  --video <video-dir>/renders/final.mp4 --mix-report <video-dir>/evidence/audio-mix.json

# ── 平台线（微信 / 小红书 / 通用兜底）──
# 1) 列出全部平台与形式（含产出目录与已登记自检的形式）
python3 $SKILL/scripts/check_social_delivery.py --list

# 2) 查某个形式的规格（脚本与模板都从这里读，不要在别处硬编码）
python3 $SKILL/scripts/check_social_delivery.py --print-specs --form xiaohongshu/image-text

# 3) 产出物就位后自检（--strict 把警告也当失败；不指定 --forms 则自动发现 export/ 下的形式）
python3 $SKILL/scripts/check_social_delivery.py --project <content-dir> \
  --forms wechat/mp-article,xiaohongshu/image-text --strict --json <content-dir>/export/check.json

# 4) 批量导出图卡与封面（无头 Chrome；沿用影片的沙箱 / headless 坑，见 pipeline-notes 第 1/13/14 条）
node $SKILL/scripts/render_social_assets.mjs --manifest <content-dir>/work/social-render.json --out <content-dir>/export

# 5) 只探测模板画布尺寸是否与规格表一致（不需要 puppeteer）
node $SKILL/scripts/render_social_assets.mjs --probe $SKILL/assets/platforms

# ── 维护自检 ──
python3 -m unittest discover -s $SKILL/tests                            # 平台线 + 视频线离线回归
node    $SKILL/tests/integration.mjs --modules <video-dir>/node_modules # 可选：真实构建 + 无头浏览器
```

- [两级内容路由](references/core/routing.md)：平台 / 形式两级交互形状、事实源判定、追问话术、`plan.json` 契约、边界情况。
- [生产管线](references/core/pipeline.md)：七步管线、渲染与编码底座、跨平台媒体标准、验收纪律。
- [跨平台一致性](references/core/cross-platform.md)：事实源派生、一致性清单、素材复用、发布顺序与挂载。
- [平台接入契约](references/core/platform-schema.md)：新增平台要做哪 5 件事、检查函数契约、反模式清单。
- [基线 BASELINE](references/BASELINE.md)：能力清单、规格版本、校验命令、扩展契约。
- [通用平台包](references/platforms/generic/PLATFORM.md)：影片分册索引、片型、工程与资产、红线、两层自检。
- [微信规格总表](references/platforms/wechat/specs.md)：三类内容的硬参数 + 官方来源链接 + HTML/CSS 白名单。
- [小红书规格总表](references/platforms/xiaohongshu/specs.md)：两类形式的硬参数 + 来源质量提示 + 平台红线 + 与微信的对照表。
- [X 规格总表](references/platforms/x/specs.md)：Article 长度/标题/封面/内容能力 + 来源质量分级；[X 文章分册](references/platforms/x/article.md) 讲流程与写作要点。
- `assets/platforms/`：六套可直接改的模板（微信图卡 / 正文片段 / 头条封面 / 次条封面 / 视频号封面 / 小红书图集页 / 小红书视频封面）+ 影片的起步工程、默认样式、手法样例与音频资产。
- [来源与授权范围](references/THIRD-PARTY.md)：本包授权、平台规则引用质量、素材版权约束。
- [LICENSE](LICENSE) 是本包自身的完整授权声明。

---

## 本机实测管线

影片体系有一套**已实跑验证**的渲染 / 编码 / 音频管线与 28 条环境坑，全部平台包共用同一条底座，因此那些坑**对微信与小红书两包同样适用**（沙箱、`headless: true`、zsh 通配符、`loudnorm` 两遍、`mask-image` 等）。

**完整清单见** [本机实测管线与环境坑](references/platforms/generic/motion-film/pipeline-notes.md)。平台化之后追加的几条：

- **图卡与封面一次渲染多画幅。** 把各画幅的卡片放进同一页并排，用 `viewport` 放大到容纳全部卡片，再对每个元素 `el.screenshot()` 分别出图——改一处即所有画幅同步。做法与坑见 pipeline-notes 第 25–28 条与分册 `cover.md`。
- **像素尺寸必须实测，不要信 CSS。** 导出后用 `check_social_delivery.py` 读真实图片头拿宽高；CSS 写的 `1080px` 在 `deviceScaleFactor` 不为 1 时会翻倍（`el.screenshot()` 也受 DPR 影响），这是所有平台线最容易踩的一条。
- **模板尺寸与规格表必须同步校验。** `render_social_assets.mjs --probe` 一次比对全部平台的模板画布与 `social_specs.json`；改了规格或模板后必跑，回归测试里也有一项守着这件事。
- **正文 HTML 片段要过"白名单体检"。** 交付前扫一遍禁用标签 / 属性（`<style`、`<script`、`position:`、`@media`、外链 img src、Base64 img）——这些在浏览器预览里全都正常，只有粘贴进公众号后台才暴露。
- **小红书文案要过"风险词体检"。** 导流词与绝对化用语在本地预览里毫无异常，发出去才限流。
- **短标题单独打磨。** 视频号短标题 ≤16 字会进搜索与订阅号消息列表，写法比视频描述更接近"标题党也要准"：必须有具体对象 + 具体结果。
- **长文的"手机预览"不可跳过。** 后台只看桌面预览看不出字号与图片换行问题；公众号后台有手机预览入口，把预览二维码扫一次再发。
- **改了脚本或规格表后跑回归。** `python3 -m unittest discover -s <skill-dir>/tests`（纯标准库，不需要 ffmpeg / Pillow / 网络；其中混音与落点两项在缺 ffmpeg 时自动跳过）。

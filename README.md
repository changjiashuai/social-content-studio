# social-content-studio · 社交内容工坊

**一个自带全部能力的独立 skill。** 把一次内容生产按 **「先选平台，再选内容形式」** 的两级结构组织起来，覆盖微信、小红书与自有渠道，并按平台渐进扩展。

- 版本：**1.5.0**
- 作者：**changjiashuai**
- 授权：**AGPL-3.0**（见 [LICENSE](LICENSE)；包内全部内容均为作者原创，无第三方组件，见 [references/THIRD-PARTY.md](references/THIRD-PARTY.md)）
- 基线：**`references/BASELINE.md`**（能力清单 + 校验命令 + 基线指纹 + 扩展契约）
- 依赖：**无外部 skill 依赖**。影片的 19 个方法论分册、6 个工程脚本、起步工程、默认样式、手法样例、配乐示例与原创音效全部原生内置，可独立分发。

---

## 1. 能力总表

| 能力 | 形式 ID | 位置 |
|---|---|---|
| **两级路由（先平台后形式，均可多选）** | — | `references/core/routing.md` |
| **代码驱动的影片**（产品片 / 科普 / 数据 / 叙事，片型由内容定） | `generic/motion-film` | `SKILL.md` →「通用平台 · 影片」（总纲）+ `references/platforms/generic/motion-film/`（19 个分册） |
| **风格推导**（给主题/数据后自行推出风格与叙事） | `generic/motion-film` | `motion-film/style-derivation.md` + `rhythm-brief.md` |
| **只有网址也能开工**（三级证据源，不假造界面） | `generic/motion-film` | `motion-film/web-first.md` + `research-brief.md` |
| **内部溯源**（上屏数字底账，六形式共用） | 全部形式 | `evidence/FACTS.md` + `motion-film/provenance.md` |
| **配音**（edge-tts 优先，按内容选音色，禁用系统机器音） | `generic/motion-film` | `motion-film/voiceover.md` + `video-line/make_voiceover.py` |
| **微信图文（图片消息 / 小绿书）** | `wechat/image-text` | `references/platforms/wechat/image-text.md` |
| **公众号长文** | `wechat/mp-article` | `references/platforms/wechat/mp-article.md` |
| **视频号视频** | `wechat/channels` | `references/platforms/wechat/channels.md` |
| **小红书图文笔记** | `xiaohongshu/image-text` | `references/platforms/xiaohongshu/image-text.md` |
| **小红书视频笔记** | `xiaohongshu/video` | `references/platforms/xiaohongshu/video.md` |
| 产品取材、`DIRECTION.md`、镜头表、专属手法推导 | 全部形式共用 | `SKILL.md` 影片第 1–7 步 + `references/core/pipeline.md` |
| 工程初始化 / 环境预检 / 无头渲染 / 编码 / 混音 / 结构自检 | `generic/motion-film` | `scripts/video-line/`（6 个脚本） |
| 起步工程 + 默认样式 + 手法样例 + 配乐示例 + 11 个原创音效 | `generic/motion-film` | `assets/platforms/generic/` |
| 跨平台口径一致性与素材复用 | — | `references/core/cross-platform.md` |
| 规格机器校验（尺寸 / 比例 / 字数 / 体积 / 禁用项 / 风险词） | — | `scripts/check_social_delivery.py` + `scripts/social_specs.json` |
| **`plan.json` 契约校验**（形式登记 / 事实源 / 执行顺序 / 先静后动） | — | `check_social_delivery.py --check-plan` |
| **投放预设**（竖版 9:16 / 横版 6:7 封面的画幅与首帧要求） | `generic/motion-film` | `video-line/init_project.py --preset` |
| 模板画布尺寸探测 + 离线回归 + 集成回归 | — | `scripts/render_social_assets.mjs --probe` + `tests/` |
| 平台接入契约（渐进扩展） | — | `references/core/platform-schema.md` |

---

## 2. 怎么触发

说"用社交内容工坊做一份内容"，或直接用触发词：微信图文、小绿书、公众号文章、公众号排版、视频号、小红书图文、小红书笔记、小红书视频、多平台分发、产品宣传片、版本更新片、changelog、social content、product promo。

**它做的第一件事一定是问你两次**（都可多选）：

1. **投放哪些平台**：`1 微信` / `2 小红书` / `3 通用（自有渠道）`
2. **每个平台要哪种形式**：
   - 微信 → `1 图文（图片+文案）` / `2 公众号（长文）` / `3 视频号（视频）`
   - 小红书 → `1 图文笔记` / `2 视频笔记`
   - 通用 → `1 影片`（片型由内容定：产品片 / 科普 / 数据 / 叙事）

多选时按「**事实源 → 静态切片 → 动态切片**」串行执行（先长后短、先静后动），保证各端口径一致。

---

## 2.1 使用示例

**核心变化（v1.2.0 起）：你不用先选风格。** 给出主题、数据或更新内容，它会按 [风格推导](references/platforms/generic/motion-film/style-derivation.md) 自行推出适合的表达方式，并说明理由。

### 示例 A · 只给数据 → 自动推导「证据驱动」

> 用社交内容工坊做一支 45 秒的产品片。这是 Q3 数据 `data/funnel.csv`：访客 240 万、注册 9.6 万、付费 3200。重点讲清「注册率为什么从 4% 涨到 8.9%」。

它会判定**信息形状 = Evidence**（不是 Claim），因此选**数据叙事**而不是动态排版，理由写入 `plan.json`：

```json
"styleDerivation": {
  "logic": "evidence",
  "languages": ["data-story", "modular-grid"],
  "compositionModel": "negative-space-small-subject",
  "personality": {"precise": 2, "calm": -1, "premium": 2, "technical": 1, "new": 1},
  "invariants": ["底色近黑偏冷", "强调色只给被测量到的东西", "数字只出现一次", "网格 8% 对比", "每屏一个结论"],
  "prohibitions": ["不用弹跳缓动", "不出现多色渐变", "不用无出处的大数字"],
  "benchmarks": [{"title": "<参照作品>", "learn": "切点密度", "avoid": "配乐旋律"}]
}
```

再写**节奏单**：混合路线 / BPM 112 / 0–4s 钩子 / **26–31s 爆点（8 刀各一拍）** / 31–38s 主角时刻 / 38–45s 收尾。`--check-plan` 校验通过后才开工。

### 示例 B · 一句话主题 → 自动选叙事结构

> 我们做了个 AI 笔记工具，帮人把零散想法连成体系。做条 30 秒的。

判定 **Transformation**（零散 → 体系），选**连续变形** + **单一物件隐喻**，结构用**前后对比**；禁令里会自动加一条「不连通概念粒子假装有界面」。

**同一个产品，换个说法结果就不同**：若你说的是「我们做了个更好的笔记工具」（Claim），它会选动态排版 + 生成场。这是推导链的价值——不是套模板。

### 示例 C · 更新片 → 触发反重复闸门

> v2.3 更新，五个新功能，做条更新片。上次那条是星空开场那支。

判定 **List** → 章节化排版 + 卡牌蒙太奇 → 倒数清单结构。同时比对上一支的 `DIRECTION.md` 六项（结构 / 开场 / 签名镜头 / 镜头路线 / 配乐形状 / 结尾），**不足四项不同会被拦下重做**。

### 示例 D · 多平台分发（事实源 → 静态 → 动态）

> 这条内容微信和小红书都要，论证在公众号长文里。

选 `wechat/mp-article` + `xiaohongshu/image-text` + `xiaohongshu/video`；**事实源自动判定为公众号长文**（论证空间最大），执行顺序固定为「长文 → 图集 → 视频」。把视频排到长文前面的 `plan.json` 会被 `--check-plan` 直接拦下。

三个产出共用**同一份** `evidence/FACTS.md`——改数字先改底账，再改三处产出。

### 示例 E · 同一支片发两个渠道

```sh
# 小红书竖版：1080×1920，BRIEF 自动写入「前 3 秒即钩子、封面单独做 3:4」
python3 $SKILL/scripts/video-line/init_project.py --output film-xhs --style default --preset xhs-vertical

# 视频号横版：1920×1080，BRIEF 自动写入「第 1 帧即封面、短标题 ≤16 字」
python3 $SKILL/scripts/video-line/init_project.py --output film-ch --style default --preset channels-horizontal
```

### 示例 F · 想核对某个数字的来源

**FACTS 是内控底账，默认不展示**（见 [内部溯源](references/platforms/generic/motion-film/provenance.md)）。只在两种情况出现：

- **你主动问**：「那个 8.9% 哪来的？」→ 只回答你问的那一条。
- **证据链断裂** → 用一句话说明结论，不贴整张表：「『每天省 40 分钟』来自 6 人访谈自报，已标为示意，片子里没有配『实测』字样。」

### 示例 G · 只给一个网址

> 帮我给 https://example.com 做一支 40 秒的产品片。

**它先判证据级别 = web（C 级）**，然后按 [网址优先](references/platforms/generic/motion-film/web-first.md) 去挖官网、文档站、定价页、changelog，并**先写 `RESEARCH.md`**（[调研摘要](references/platforms/generic/motion-film/research-brief.md)）：

```markdown
- 证据级别：web（C 级）
## 1. 产品是什么
用官网自己的话：……
## 2. 可引用的公开事实
| 事实 | 数字 / 断言 | 来源 URL | 抓取日期 |
## 3. 证据级别与边界
- 不做：功能演示镜头、可点击界面、前后对比的真实状态
- 可以做：官网主张、文档里的机理、公开数字、版本清单
## 4. 一句话结论
```

**关键约束**（也是和以前最大的差别）：

| 想表达 | C 级允许的做法 | 不允许 |
|---|---|---|
| 界面长什么样 | 用官方公开截图并标明来源 | 自己画一个「像但不准」的界面 |
| 功能怎么用 | 讲机理或价值 | 摆出可点击的假 UI |
| 数据表现 | 引用公开数字 + 出处 | 造一组「示意但看起来像真的」曲线 |

所以片子会自动落到 **Claim / Evidence / Mechanism / List** 这些形状，**不做 Workflow（真交互）**——因为那需要真实界面。缺 `RESEARCH.md` 时 `check_delivery.py` 会直接报错。

如果你后来又给了源码，可以随时升级到 A 级：能接原组件就替换，替换不了的保留并说明，**变更记进 `BRIEF.md`，不默默改口径**。

### 改前改后对照

| 场景 | 之前 | 现在 |
|---|---|---|
| 给主题 | 需要先选风格，容易落进「暗色科技风」 | 从信息形状推导，同一产品不同说法得到不同片子 |
| 给数据 | 数字滚动 + 图表 | 先判 Evidence，再选数据叙事结构 + 节奏单 |
| **只给网址** | 硬套仓库流程，或手画假界面 | 判 C 级 → 写 `RESEARCH.md` → 走主张/证据/机理路线，**不假造界面** |
| 连做两支 | 容易复用开场 | 六项四差异，不达标拦下 |
| 审片 | 自己看 | 可选独立审片人，必问「哪段走神」 |
| 数字来源 | 凭记忆 | 内部底账 + 分级校验，不打扰用户 |

---

## 3. 目录结构

```
social-content-studio/
├── SKILL.md                        # 主入口：两级路由 + 影片总纲 + 平台包要点 + 跨平台约束 + 工具入口
├── README.md                       # 本文件
├── LICENSE                         # AGPL-3.0
├── agents/openai.yaml              # Agent 界面描述
├── .github/workflows/regression.yml # CI：离线回归 + 模板探测 + 可选集成回归
├── references/
│   ├── BASELINE.md                 # ★ 基线：能力清单、校验命令、基线指纹、扩展契约
│   ├── THIRD-PARTY.md              # 授权范围（全包统一 AGPL-3.0）+ 平台规则来源质量 + 素材版权约束
│   ├── core/                       # 平台无关的共用底座
│   │   ├── routing.md              #   两级路由协议 / 事实源 / plan.json 契约
│   │   ├── pipeline.md             #   生产管线 / 渲染编码底座 / 媒体标准 / 验收纪律
│   │   ├── cross-platform.md       #   跨平台一致性 / 素材复用 / 发布挂载
│   │   └── platform-schema.md      #   平台接入契约（新增平台做哪 5 件事）
│   └── platforms/                  # 平台包（彼此独立）
│       ├── wechat/{PLATFORM,specs,image-text,mp-article,channels}.md
│       ├── xiaohongshu/{PLATFORM,specs,image-text,video}.md
│       └── generic/{PLATFORM,specs}.md + motion-film/（18 个分册）
├── assets/platforms/
│   ├── wechat/…                    # 5 套模板（图卡 / 正文片段 / 头条封面 / 次条封面 / 视频号封面）
│   ├── xiaohongshu/…               # 2 套模板（图集页 / 视频封面）
│   └── generic/                    # starter（起步工程）/ fallback（默认样式「纸墨」）/ fx-lab（手法样例）/ audio（配乐示例 + 音效）
├── scripts/
│   ├── social_specs.json           # ★ 规格单一事实来源（platforms.<平台>.forms.<形式>）
│   ├── check_social_delivery.py    # 平台线自检（规格校验 + plan.json 契约 + 内部溯源分级）
│   ├── render_social_assets.mjs    # 无头 Chrome 批量导出 + 模板尺寸探测
│   └── video-line/                 # 影片工程脚本（init_project / check_environment / sfx_landmarks /
│                                   #   mix_audio / make_sfx / check_delivery）
└── tests/
    ├── test_check_social_delivery.py    # 平台线回归
    ├── test_video_line_regressions.py   # 视频线回归
    └── integration.mjs                  # 真实构建 + 无头浏览器集成回归（可选）
```

---

## 4. 组织方式的三个原则

1. **影片是原生能力，不是外挂。**
   总纲（7 步流程 + 硬约束 + 工程入口）在 `SKILL.md`，**细则是 `references/platforms/generic/motion-film/` 下的 19 个分册**。两者分工明确：总纲不复制分册正文，分册不改写总纲结论，因此不存在"两份正文不一致"。

2. **共用底座上提，平台专属下沉。**
   `references/core/` 放平台无关的东西（路由、管线、跨平台一致性、接入契约）；
   `references/platforms/<平台>/` 与 `assets/platforms/<平台>/` 放平台专属的东西（规格、形式流程、红线、模板、资产）。
   所以加一个平台只需加一个平台包 + 一份模板目录 + 规格 JSON 一个节点 + 自检脚本一个函数，**影片体系与其他平台包永远不动**。

3. **规格只有一个事实来源。**
   所有平台硬参数集中在 `scripts/social_specs.json`。模板 HTML 的画布尺寸、自检脚本的阈值都从它读——
   平台规则变更时只改这一个文件，不会出现"模板改了但检查没改"或反之。

---

## 5. 扩展一个新平台（渐进扩展的标准动作）

按 `references/core/platform-schema.md` 的契约，只需 5 步：

| # | 动作 | 位置 |
|---|---|---|
| 1 | 建平台包（`PLATFORM.md` + `specs.md` + 每种形式一个 `.md`） | `references/platforms/<平台>/` |
| 2 | 建模板资产目录（纯文案类形式可省略） | `assets/platforms/<平台>/` |
| 3 | 规格 JSON 加一个 `platforms.<平台>` 节点 | `scripts/social_specs.json` |
| 4 | 自检脚本加一个检查函数并登记进 `FORM_CHECKS` | `scripts/check_social_delivery.py` |
| 5 | 路由表加一行 | `references/core/routing.md` 第二级 + `SKILL.md` 平台表 |

新增平台**不需要**改 `core/` 的语义、不需要改其他平台包、不需要改影片体系、不需要新建渲染脚本。跑 [BASELINE.md](references/BASELINE.md) §3 的校验命令全绿即可交付。

---

## 6. 授权（分发前必读）

本 skill 以 **AGPL-3.0** 发布。**包内全部内容都是作者原创，没有任何第三方组件，也没有任何限制商业使用的条款。**

| 范围 | 授权 | 关键约束 |
|---|---|---|
| 包内全部内容（起步工程 `starter/`、默认样式「纸墨」`fallback/`、平台模板、脚本、文档） | **AGPL-3.0**（作者 changjiashuai） | 可自由用于收费产品、白标与商业平台；分发时履行 AGPL 的许可保留与源码开放义务 |

**分发时把 `LICENSE` 带上就够了**——全包只有一个许可层级，不存在某个子目录另有条款的情况。`starter/LICENSE` 与 `starter/NOTICE.md` 是为复制出去的影片工程准备的，保留即可。细节见 [references/THIRD-PARTY.md](references/THIRD-PARTY.md)。

---

## 7. 快速上手

```sh
SKILL=~/.workbuddy/skills/social-content-studio

# 0) 先做两级路由（平台 → 形式），写入 plan.json，再校验契约
python3 $SKILL/scripts/check_social_delivery.py --check-plan <content-dir>/plan.json

# ── 影片 ──（--preset: generic / xhs-vertical / channels-horizontal / channels-vertical）
python3 $SKILL/scripts/video-line/init_project.py --output <video-dir> --style repo --repo <repo-dir>
python3 $SKILL/scripts/video-line/check_environment.py --project <video-dir> --engine browser
python3 $SKILL/scripts/video-line/check_delivery.py <video-dir>/plan.json \
  --video <video-dir>/renders/final.mp4 --mix-report <video-dir>/evidence/audio-mix.json

# ── 平台线 ──
python3 $SKILL/scripts/check_social_delivery.py --list                       # 1) 看有哪些平台与形式
python3 $SKILL/scripts/check_social_delivery.py --print-specs --form wechat/channels   # 2) 查规格
python3 $SKILL/scripts/check_social_delivery.py --project <content-dir> \
  --forms wechat/mp-article,xiaohongshu/image-text --strict --json <content-dir>/export/check.json   # 3) 自检
node $SKILL/scripts/render_social_assets.mjs --probe $SKILL/assets/platforms  # 4) 探测模板尺寸

# ── 维护自检 ──
python3 -m unittest discover -s $SKILL/tests
```

---

## 8. 版本记录

| 版本 | 说明 |
|---|---|
| **v1.5.0** | **补上配音能力。** 新增 `voiceover.md` 与 `make_voiceover.py`：用户未指定时优先 **edge-tts**（免费、无需 key），按片子气质选音色并记录理由；edge-tts 不可用再找其他免费 TTS；**都没有则停下来问用户**。`say` / SAPI / eSpeak 等系统机器音**一律禁用**——没有配音优于机器音。环境预检增加 TTS 探测但不阻塞渲染。分册 18 → 19，回归测试 131 → 137 项。 |
| **v1.4.0** | **影片形式通用化：片型由内容决定，不再一律做成产品片。** 形式改名为 `generic/motion-film`（目录同步），**旧 ID 不再兼容**；新增 `filmKind`（`product` / `evidence` / `explainer` / `story`），`check_delivery.py` 按片型分派必备项；**不声明时等于 `product`**，默认严格度不变；任何片型都不许假造界面。回归测试 122 → 131 项。 |
| **v1.3.0** | **补上「只给网址」这条最常见路径。** 新增 `web-first.md`（A/B/C 三级证据源 + 公开来源清单 + 三条硬线）与 `research-brief.md`（`RESEARCH.md` 四问契约，B/C 级必写）；`direction.md` 加「证据级别 → 允许的信息形状」约束；`check_delivery.py` 新增 `evidenceLevel` 与 `research_checks`（缺调研摘要阻断，原组件要求在非仓库级别降级为警告但不放开伪造）。分册 15 → 18，回归测试 116 → 122 项。 |
| **v1.2.0** | **风格从「挑」改为「推导」。** 新增 `style-derivation.md`（8 信息形状 → 10 运动语言 → 5 性格滑块 → 主构成 → 5 不变量 + 3 禁令）与 `rhythm-brief.md`（路线 / 能量曲线 / 密度 / 死时间）；`direction.md` 加定标杆、改为推导、反重复改六项四差异；`review.md` 加独立审片与「哪段走神」；新增内部溯源契约（FACTS 底账，六形式共用，**不随片交付**）；`plan.json` 加 `styleDerivation` 并校验。回归测试 98 → 116 项。README 新增「§2.1 使用示例」六个场景与改前改后对照。 |
| **v1.1.0** | **把文档纪律变成机器守卫**（能力面不变，不新增平台）。`--check-plan` 校验 `plan.json` 契约；`uncertainty` 升级为 `max` + `safeMax` + 原文的可执行约定，落在稳妥与官方之间报 WARN；`init_project.py --preset` 提供 `generic` / `xhs-vertical` / `channels-horizontal` / `channels-vertical`；ffprobe 失败不再静默；新增 GitHub Actions 回归；SKILL.md 平台要点改为指向 `specs.md` 单一事实源。回归测试 73 → 98 项。 |
| **v1.0.3** | **补充第三方名称的使用说明**：`references/THIRD-PARTY.md` 新增 §2.3，逐类列出包内出现的第三方名称（案例对象 / 外部运行时依赖 / 素材来源标注 / 本机他 skill 名）及其性质，说明它们属**叙述性使用**、不是随包分发的第三方组件，并写明案例复盘保留产品实名的理由。**案例对象名一处未动**，仅新增说明。同版修正 `motion-film/audio-and-qa.md` 内置音效目录的链接为包内相对路径（原写法为包根相对路径，在按文件位置解析的渲染器下会断链）。 |
| **v1.0.2** | **起步工程改为完全原创**：`assets/platforms/generic/starter/` 的 29 个文件（运行时 `engine.js` / `film-store.js` / `client.jsx` / `film.jsx`、`kit/` 四件、`shots/` 两件、`presentations.jsx`、`product-context.jsx`、`fixtures/api.js`、`film.css`、六个工程脚本、`integration.config.mjs`、`package.json`、`adapters/` 四件）按同一对外契约重新实现。该目录由第三方代码改为本包原创，**包内自此没有任何第三方组件**；`NOTICE.md` 的版权行改为 changjiashuai。对外契约（文件名、导出名、DOM 契约、CLI 参数、`window.*` API）全部保持不变，既有影片工程无需改动。 |
| **v1.0.1** | **默认样式改为完全原创**：`fallback/` 的 `tokens.css` 与 `primitives.jsx` 重写为「纸墨」样式（纸白 / 墨黑双色调，纸面 + 纸叠结构，新增 `ghost` 按钮与 `accent` 徽标变体），随包两张预览图按新样式重新渲染。该目录由第三方 BSL 1.1 组件改为本包原创 AGPL-3.0，**包内自此没有任何限制商业使用的组件**。对外契约（类名、`--film-*` 变量名、四个组件导出名）保持不变，既有影片工程无需改动。 |
| **v1.0.0** | **首个独立发布版**。两级路由（先平台后形式，均可多选）＋ 3 个平台包 6 个形式：微信（图文 / 公众号长文 / 视频号）、小红书（图文笔记 / 视频笔记）、通用（产品片）。产品片体系完整内置：13 个方法论分册、6 个工程脚本、起步工程、默认样式、6 个手法样例、2 个配乐示例、11 个原创音效；规格单一事实来源 `social_specs.json`；平台线自检（含公众号 HTML 白名单体检与小红书风险词扫描）+ 产品片结构与媒体自检；7 套模板 + 模板画布尺寸探测；平台线 + 视频线离线回归测试；基线文档与平台接入契约。**无外部 skill 依赖。** |

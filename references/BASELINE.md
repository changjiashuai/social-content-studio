# 基线 BASELINE

本文件是 `social-content-studio` **v1.6.0 的基线快照**：把"已经跑通的能力"在平台化结构中固定下来，
明确哪些是共用底座、哪些是平台专属、规格版本是什么、怎么校验。
**后续每新增一个平台，都在此基线上叠加；基线本身只增不改。**

一句话：**基线 = 平台无关的共用底座（`core/`）+ 已固化的平台包（`references/platforms/` 与 `assets/platforms/`）+ 原生影片体系（`SKILL.md` 总纲 + `motion-film/` 分册 + `scripts/video-line/`）。**

---

## 1. 基线的三条约束

1. **可比对。** 基线里的每一项能力都必须能被一个具体文件 + 一条校验命令指认，不许"口头声称支持"。
2. **不漂移。** 影片体系有**两个明确的事实源**：**流程总纲**在 `SKILL.md` 的「通用平台 · 影片」章节（7 步 + 硬约束 + 工程入口），**细则**在 `references/platforms/generic/motion-film/` 的 19 个分册；总纲不复制分册正文，分册不改写总纲结论，分册之间也不互相复制。规格以 `scripts/social_specs.json` 单一事实源保存，模板与自检都从它读。§4 的基线指纹可用于逐文件核对。
3. **不缩减。** 新增平台只能**叠加**，不得删改已有平台包与 `core/` 的既有语义。产品宣传片 / 版本更新片必须始终可被选中（路由第 3 项 `通用`）。

---

## 2. 基线组成（v1.6.0，本版冻结）

| 层 | 位置 | 内容 | 说明 |
|---|---|---|---|
| 影片·总纲 | `SKILL.md` →「通用平台 · 影片」 | 术语、7 步流程、硬约束、工程入口 | **流程的唯一事实源**；分册不改写其结论 |
| 影片·细则 | `references/platforms/generic/motion-film/` | 19 个分册（方向 / **网址优先** / **调研摘要** / 风格推导 / 节奏单 / 文案节奏 / 手法词汇 / 组件接入 / 起步工程 / 仓库审计 / 依赖安装 / 配音 / 配乐 / 混音验收 / 审片 / 封面 / 案例复盘 / 本机实测管线；另有内部溯源 `provenance.md`） | **细则的唯一事实源**；总纲不复制其正文 |
| 影片·工程 | `scripts/video-line/` | 初始化、环境预检、音效落点、混音、音效生成、结构与媒体自检 | 7 个脚本，纯标准库；混音与落点需 ffmpeg |
| 影片·资产 | `assets/platforms/generic/` | `starter/`（起步工程：运行时 / 构建 / 预览 / 渲染 / 封面 / 静帧 / 适配器 / fixture）、`fallback/`（默认样式「纸墨」）、`fx-lab/`（6 个手法样例）、`audio/`（2 个配乐示例 + 11 个音效 + manifest） | **全部本包原创** |
| 共用底座 | `references/core/` | 路由协议、生产管线、跨平台一致性、平台接入契约 | 平台无关，被所有平台包共用 |
| 平台包·通用 | `references/platforms/generic/` | `PLATFORM.md`（入口 + 分册索引 + 工程与资产 + 红线）+ `specs.md`（兜底规格 + 两层自检覆盖范围） | 方法论正文在总纲与分册（见 `core/platform-schema.md` §2 的例外约定） |
| 平台包·微信 | `references/platforms/wechat/` | 图文 / 公众号长文 / 视频号三条线 + 官方规格总表 | v1.0.0 全覆盖 |
| 平台包·小红书 | `references/platforms/xiaohongshu/` | 图文笔记 / 视频笔记两条线 + 规格总表（含来源质量提示） | v1.0.0 全覆盖 |
| 规格事实源 | `scripts/social_specs.json` | `shared` + `platforms.<平台>.forms.<形式>` | 模板画布尺寸与自检阈值都从这里读 |
| 校验·平台线 | `scripts/check_social_delivery.py` + `scripts/render_social_assets.mjs` + `tests/test_check_social_delivery.py` | 产出物自检 + 模板尺寸探测 + 平台线回归 | 纯标准库，不依赖 ffmpeg / Pillow / 网络 |
| 校验·影片 | `scripts/video-line/check_delivery.py` + `tests/test_video_line_regressions.py` + `tests/integration.mjs` | 结构与媒体自检 + 视频线回归 + 可选集成回归 | 混音/落点两项需 ffmpeg，缺则自动跳过 |
| 授权 | `LICENSE` + `references/THIRD-PARTY.md` | 作者 changjiashuai，AGPL-3.0；**包内无第三方组件** | 无外部运行时依赖；**无限制商用的组件** |

---

## 3. 基线能力清单（不得削减）

### 3.1 影片能力（`generic/motion-film`）

| 能力 | 位置 |
|---|---|
| 代码驱动的影片（产品片 / 科普 / 数据 / 叙事，片型由内容定） | 路由 → `通用` 平台 → `generic/motion-film` |
| 产品取材、`DIRECTION.md`、镜头表、专属手法推导（流程 1–7 步） | `SKILL.md` 总纲；被所有平台包共用 |
| 分镜与文案、视觉手法词汇、组件接入、审片、封面 | `motion-film/` 对应分册 |
| **风格推导**（8 形状 → 10 语言 → 5 滑块 → 5 不变量 + 3 禁令） | `motion-film/style-derivation.md` |
| **节奏单**（路线 / 能量曲线 / 密度 / 死时间） | `motion-film/rhythm-brief.md` |
| **配音**（edge-tts 优先、按气质选音色、禁用系统机器音） | `motion-film/voiceover.md` + `scripts/video-line/make_voiceover.py` |
| **网址优先调查**（A/B/C 三级证据源，只有官网也能开工） | `motion-film/web-first.md` |
| **调研摘要**（`RESEARCH.md`，B/C 级必写） | `motion-film/research-brief.md` |
| 工程初始化 / 环境预检 / 无头渲染 / 编码 / 混音 / 结构自检 | `scripts/video-line/` 六个脚本 |
| 起步工程、默认样式、手法样例、配乐示例、11 个原创音效 | `assets/platforms/generic/` |
| 已实跑验证的本机管线与 28 条环境坑 | `motion-film/pipeline-notes.md` |

### 3.2 平台能力（`references/platforms/`）

| 平台 | 形式 | 自检函数 |
|---|---|---|
| 通用 | `generic/motion-film` | `check_generic_motion_film`（兜底结构检查）+ `video-line/check_delivery.py`（强检查） |
| 微信 | `wechat/image-text` | `check_wechat_image_text` |
| 微信 | `wechat/mp-article` | `check_wechat_mp_article` |
| 微信 | `wechat/channels` | `check_wechat_channels` |
| 小红书 | `xiaohongshu/image-text` | `check_xhs_image_text` |
| 小红书 | `xiaohongshu/video` | `check_xhs_video` |
| X | `x/article` | `check_x_article` |

### 3.2.1 契约与纪律的机器化（v1.1.0 新增）

| 能力 | 位置 | 为什么要有 |
|---|---|---|
| `plan.json` 契约校验（`--check-plan`） | `scripts/check_social_delivery.py` | 路由契约此前只有文档、没有机器守卫；`factSource` / `order` / 「先静后动」写错无人拦 |
| 口径不一参数的统一降级（`uncertainty` + `safeMax`） | `social_specs.json` + `uncertain_of` / `judge_count` | `uncertainty` 此前只是注释，检查器从不读；现在超过稳妥值报 WARN 并附原文 |
| 投放预设（`--preset`） | `scripts/video-line/init_project.py` | 小红书竖版与视频号横版节奏要求相反，此前只写在文档里 |
| CI 回归（`.github/workflows/regression.yml`） | 仓库根 | 基线纪律「改完必跑」此前靠人自觉 |
| ffprobe 失败不再静默 | `probe_video` + 报告末尾 | 探测失败此前看起来像「文件没问题」 |
| **内部溯源**（`evidence/FACTS.md`，六形式共用） | `check_social_delivery.py` 的 `check_facts` | 上屏数字此前无底账；现在「宣称事实却无出处」会阻断，示意数据本身不惩罚 |
| `styleDerivation` 契约 | `--check-plan` | 风格推导从「对话里的一句话」变成 `plan.json` 里可验收的字段 |
| **证据级别**（`plan.evidenceLevel`）+ `RESEARCH.md` 校验 | `check_delivery.py` | 只有网址时不再假装能演示交互；B/C 级缺调研摘要直接阻断 |

### 3.3 基线校验（改完必跑）

```sh
SKILL=~/.workbuddy/skills/social-content-studio

# ── 平台线三条（缺一不可）──
# ① 模板画布尺寸必须与规格表一致（不需要浏览器）
node $SKILL/scripts/render_social_assets.mjs --probe $SKILL/assets/platforms

# ② 离线回归（平台线 + 视频线一次跑完；纯标准库，缺 ffmpeg 时自动跳过混音/落点两项）
python3 -m unittest discover -s $SKILL/tests

# ③ 规格自检（对真实或样本产出物跑；--strict 把 warning 也算失败）
python3 $SKILL/scripts/check_social_delivery.py --project <content-dir> --strict

# ④ plan.json 契约（路由写错=静默改形式，必须在产出前就挡住）
python3 $SKILL/scripts/check_social_delivery.py --check-plan <content-dir>/plan.json

# ── 影片（改了 video-line 或影片产出物后跑）──
python3 $SKILL/scripts/video-line/check_delivery.py <video-dir>/plan.json \
  --video <video-dir>/renders/final.mp4 --mix-report <video-dir>/evidence/audio-mix.json

# ── 可选：真实构建 + 无头浏览器（需要已安装的 video/node_modules）──
node $SKILL/tests/integration.mjs --modules <video-dir>/node_modules
```

①②③ 全绿，才算"平台线基线未漂移"。

---

## 4. 基线指纹（v1.6.0）

用于核对基线是否被改动。完整 SHA-256 可用 `shasum -a 256 <file>` 复算（下表取前 16 位）。
二进制资产（音效 WAV、预览 PNG）、`LICENSE` 与 `BASELINE.md` 自身不入表（自身无法自洽）。

### 4.1 入口与项目文件

| 文件 | SHA-256 前 16 位 |
|---|---|
| `.gitignore` | `6e0cb83e04db8cd4` |
| `README.md` | `53fd6d479ec9fa52` |
| `SKILL.md` | `dd1af9cb1135b199` |
| `agents/openai.yaml` | `ecbfa04409b23ee2` |
| `.github/workflows/regression.yml` | `99cf617225cb1ab7` |

### 4.2 文档与基线

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/THIRD-PARTY.md` | `6d1fd1515ff52817` |

### 4.3 共用底座（core）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/core/cross-platform.md` | `c41bc2b3187c2105` |
| `references/core/pipeline.md` | `05ab7a24b42afd5a` |
| `references/core/platform-schema.md` | `081d8bf5bfe26889` |
| `references/core/routing.md` | `34509ea35c0b6e6b` |

### 4.4 平台包 · 微信

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/platforms/wechat/PLATFORM.md` | `30f75b455c1b93f7` |
| `references/platforms/wechat/channels.md` | `68125b8056a11451` |
| `references/platforms/wechat/image-text.md` | `5898947f13a77a2a` |
| `references/platforms/wechat/mp-article.md` | `8a091cd155972a1a` |
| `references/platforms/wechat/specs.md` | `2a1f126708916602` |

### 4.5 平台包 · 小红书

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/platforms/xiaohongshu/PLATFORM.md` | `492b52a073ced4fc` |
| `references/platforms/xiaohongshu/image-text.md` | `aa1512be5aca90e8` |
| `references/platforms/xiaohongshu/specs.md` | `78396ca6430be1c6` |
| `references/platforms/x/PLATFORM.md` | `5ea9be2f4ae79f6d` |
| `references/platforms/x/specs.md` | `15772ee1bdda7c85` |
| `references/platforms/x/article.md` | `a285bf820871d527` |
| `references/platforms/xiaohongshu/video.md` | `503b6b518ec2f991` |

### 4.6 平台包 · 通用（影片）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/platforms/generic/PLATFORM.md` | `6a5a13cf65ccd529` |
| `references/platforms/generic/motion-film/audio-and-qa.md` | `a55ef57ad10f5e40` |
| `references/platforms/generic/motion-film/audio-sourcing.md` | `935d9f7861af2871` |
| `references/platforms/generic/motion-film/case-study.md` | `2e2268183a8793cb` |
| `references/platforms/generic/motion-film/component-pipeline.md` | `d9c9feb24b7ffb0c` |
| `references/platforms/generic/motion-film/cover.md` | `7cf9f6a5ee3a5342` |
| `references/platforms/generic/motion-film/direction.md` | `951754ab270e283c` |
| `references/platforms/generic/motion-film/onboarding.md` | `1ac708ea4ccf47cf` |
| `references/platforms/generic/motion-film/pipeline-notes.md` | `e5a555454ff6af81` |
| `references/platforms/generic/motion-film/repo-and-style.md` | `d11f65f4e92508ed` |
| `references/platforms/generic/motion-film/review.md` | `2a8017343cc84f72` |
| `references/platforms/generic/motion-film/starter.md` | `3ab3bd3426e90ba0` |
| `references/platforms/generic/motion-film/story-and-copy.md` | `b276335346bd8cb3` |
| `references/platforms/generic/motion-film/visual-vocabulary.md` | `09d7fea454bd4d71` |
| `references/platforms/generic/motion-film/voiceover.md` | `13e3c28c58fc1739` |
| `scripts/video-line/make_voiceover.py` | `6c5b18bd61f6df06` |
| `references/platforms/generic/specs.md` | `842363069e8489ca` |
| `references/platforms/generic/motion-film/style-derivation.md` | `ce5310aedf7cfa7b` |
| `references/platforms/generic/motion-film/web-first.md` | `1768c3eb235366af` |
| `references/platforms/generic/motion-film/research-brief.md` | `638da98f56b7d705` |
| `references/platforms/generic/motion-film/rhythm-brief.md` | `5fd54dc157ae9236` |
| `references/platforms/generic/motion-film/provenance.md` | `8065132655cfb533` |

### 4.7 平台线脚本

| 文件 | SHA-256 前 16 位 |
|---|---|
| `scripts/check_social_delivery.py` | `f63fbdaf119c55b6` |
| `scripts/render_social_assets.mjs` | `93c51823b86a0ddd` |
| `scripts/social_specs.json` | `bc245c26b603c68b` |

### 4.8 影片脚本

| 文件 | SHA-256 前 16 位 |
|---|---|
| `scripts/video-line/check_delivery.py` | `99de3a28591a1fb9` |
| `scripts/video-line/check_environment.py` | `bce54accd2e30c7b` |
| `scripts/video-line/init_project.py` | `66699e69a3260bd8` |
| `scripts/video-line/make_sfx.py` | `7c4cb127d93096ea` |
| `scripts/video-line/mix_audio.py` | `3f0a3e4f51ab917c` |
| `scripts/video-line/sfx_landmarks.py` | `1d9059653fa7b10d` |

### 4.9 回归测试

| 文件 | SHA-256 前 16 位 |
|---|---|
| `tests/integration.mjs` | `f717acf428b04b08` |
| `tests/test_check_social_delivery.py` | `fe75e1af1a8bfe57` |
| `tests/test_video_line_regressions.py` | `ee0333c604ee4036` |

### 4.10 平台模板 · 微信

| 文件 | SHA-256 前 16 位 |
|---|---|
| `assets/platforms/wechat/article/article.template.html` | `a17173654cc3b295` |
| `assets/platforms/wechat/article/cover-11.template.html` | `1334be24831fb2fb` |
| `assets/platforms/wechat/article/cover-235.template.html` | `ed6757698acf0f7b` |
| `assets/platforms/wechat/channels/cover-67.template.html` | `0094452bbfeb8ac2` |
| `assets/platforms/wechat/image-text/card.template.html` | `a156851743bd0c5d` |

### 4.11 平台模板 · 小红书

| 文件 | SHA-256 前 16 位 |
|---|---|
| `assets/platforms/xiaohongshu/image-text/note.template.html` | `7e5f69396706fc9e` |
| `assets/platforms/xiaohongshu/video/cover-34.template.html` | `0da74b2eda895972` |

### 4.12 默认样式（fallback）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `assets/platforms/generic/fallback/SOURCE.md` | `78c0fcaaf96f9bac` |
| `assets/platforms/generic/fallback/primitives.jsx` | `94ca601fa836c640` |
| `assets/platforms/generic/fallback/tokens.css` | `61154417775bbc80` |

### 4.13 起步工程（starter）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `assets/platforms/generic/starter/NOTICE.md` | `fdd3fbc1d342042f` |
| `assets/platforms/generic/starter/build.mjs` | `a76c0dd61d58006d` |
| `assets/platforms/generic/starter/cover.mjs` | `0611804a9f7f8346` |
| `assets/platforms/generic/starter/integration.config.mjs` | `35be18da630df871` |
| `assets/platforms/generic/starter/package.json` | `9561a9f8fcda1824` |
| `assets/platforms/generic/starter/preview.mjs` | `b3377d12b3c3e5d0` |
| `assets/platforms/generic/starter/render.mjs` | `3bd8554bad5e9a2a` |
| `assets/platforms/generic/starter/server.mjs` | `922169b9a7907cf6` |
| `assets/platforms/generic/starter/src/adapters/README.md` | `23bbead59c8b2e38` |
| `assets/platforms/generic/starter/src/adapters/next-dynamic.jsx` | `21a19ef4f4ae0f2b` |
| `assets/platforms/generic/starter/src/adapters/next-image.jsx` | `0f2f15cc38ca74a7` |
| `assets/platforms/generic/starter/src/adapters/next-link.jsx` | `2a3836921f96f155` |
| `assets/platforms/generic/starter/src/adapters/next-navigation.js` | `b5f43693b9b64175` |
| `assets/platforms/generic/starter/src/client.jsx` | `1ed46d4eb672f418` |
| `assets/platforms/generic/starter/src/engine.js` | `4cac2a7a2a9c93a9` |
| `assets/platforms/generic/starter/src/fake-api.js` | `6af051448d6a4ca1` |
| `assets/platforms/generic/starter/src/film-store.js` | `c49e784e9128204b` |
| `assets/platforms/generic/starter/src/film.css` | `a4418e374a2901f2` |
| `assets/platforms/generic/starter/src/film.jsx` | `80485df19d3dd8f6` |
| `assets/platforms/generic/starter/src/fixtures/api.js` | `000f3ff0751ed47c` |
| `assets/platforms/generic/starter/src/kit/cursor.jsx` | `5fc15cdc098087e0` |
| `assets/platforms/generic/starter/src/kit/interact.js` | `a424e3a3b47e8cb2` |
| `assets/platforms/generic/starter/src/kit/measure.js` | `ab168f5bc714a273` |
| `assets/platforms/generic/starter/src/kit/text.jsx` | `f04f8b5b1be9885b` |
| `assets/platforms/generic/starter/src/presentations.jsx` | `e9bffe85da43c048` |
| `assets/platforms/generic/starter/src/product-context.jsx` | `71f4c7bc551013e2` |
| `assets/platforms/generic/starter/src/shots/index.js` | `6eacc8c97ecaf7be` |
| `assets/platforms/generic/starter/src/shots/sample.jsx` | `272168d9f9dc3846` |
| `assets/platforms/generic/starter/stills.mjs` | `b77e44b9ab1bd77f` |

### 4.14 手法样例（fx-lab）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `assets/platforms/generic/fx-lab/README.md` | `bff3d77ea62bd172` |
| `assets/platforms/generic/fx-lab/glyph-field.js` | `42889ae9b4c0696e` |
| `assets/platforms/generic/fx-lab/horizon.jsx` | `7c55381b2a584db7` |
| `assets/platforms/generic/fx-lab/orbit.js` | `76db9b43a5d5b005` |
| `assets/platforms/generic/fx-lab/settle.js` | `eac60efb54467de4` |
| `assets/platforms/generic/fx-lab/slices.jsx` | `426f18996ce0e0ff` |
| `assets/platforms/generic/fx-lab/warp.js` | `19c8d89444f5957e` |

### 4.15 配乐与音效（audio）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `assets/platforms/generic/audio/SOURCE.md` | `127e8df52ccaed2c` |
| `assets/platforms/generic/audio/manifest.json` | `dd0d41c40c8902cd` |
| `assets/platforms/generic/audio/score-example-cinematic.py` | `2e0124af54525519` |
| `assets/platforms/generic/audio/score-example-keys.py` | `b8ae7ff640a6a0fc` |
| `assets/platforms/generic/audio/sfx/SOURCE.txt` | `c911b766351153ab` |

> 指纹是**记录**，不是门禁：升级基线时同步更新本表即可。真正阻止漂移的是 §3.3 的命令——它们检的是行为，不是字节。
> 表内收本包自己维护的全部文本文件。**不入表的是**：本文件自身（`references/BASELINE.md`，收录自己的哈希会自相矛盾）、根 `LICENSE` 与 `assets/platforms/generic/starter/LICENSE`（AGPL-3.0 标准全文，FSF 的固定文本，不属于本包创作）、`assets/platforms/generic/fallback/` 的两张预览图（由 `tokens.css` 渲染出的产物，改了样式就该重新渲染）、以及音效与手法样例目录下的二进制产物。
---

## 5. 规格版本与核对节奏

| 项 | 值 |
|---|---|
| 规格版本 | 见 `scripts/social_specs.json` 的 `specVersion` 字段（本版 `2026-10-08`） |
| 核对节奏 | **每次产出前**，若距上次核对 >3 个月，重新核对各平台来源页 |
| 不确定性处理 | 官方口径不一致的参数一律标 `uncertainty`，写成"以编辑器实际提示为准"，**不得编造确定值** |

**授权约束**（详见 [THIRD-PARTY.md](THIRD-PARTY.md) §2）：

| 范围 | 授权 | 关键约束 |
|---|---|---|
| 包内全部内容（含 `fallback/` 默认样式「纸墨」与 `starter/` 起步工程） | AGPL-3.0（作者 changjiashuai） | **无额外限制**，可自由用于收费产品、白标与商业平台 |

> 整包只有一个许可层级，**不含任何第三方组件**（详见 [THIRD-PARTY.md](THIRD-PARTY.md) §2）。`starter/LICENSE` 与 `starter/NOTICE.md` 是为复制出去的影片工程准备的，保留即可。

---

## 6. 扩展契约（新增平台只需动这些）

要给本 skill 加一个平台（例如 B 站、抖音），**只做下面 5 件事**，不碰 `core/` 语义、不碰其他平台包、不碰影片体系：

| # | 动作 | 位置 |
|---|---|---|
| 1 | 建平台包目录与文件 | `references/platforms/<平台>/PLATFORM.md` + `specs.md` + 每种形式一个 `.md` |
| 2 | 建模板资产目录 | `assets/platforms/<平台>/<形式>/` |
| 3 | 规格 JSON 加一个节点 | `scripts/social_specs.json` → `platforms.<平台>`（含 `forms.<形式>`） |
| 4 | 自检脚本加一个检查函数并登记 | `scripts/check_social_delivery.py` 的 `FORM_CHECKS` |
| 5 | 路由表加一行 | `references/core/routing.md` 第二级 + `SKILL.md` 的平台表 |

契约细节见 [平台接入契约](core/platform-schema.md)。

---

## 7. 版本记录

| 版本 | 说明 |
|---|---|
| **v1.6.0** | **新增 X 平台包（`x/article`）。** ①`references/platforms/x/`：`PLATFORM.md` 区分「长帖（约 2.5 万字符、无分节）」与「Article（约 10 万字符、有标题与分节）」并给平台红线；`specs.md` 逐条带来源分级（`x_official` / `x_third_party` / `practice`）；`article.md` 给流程、首段即摘要、格式使用纪律与 `meta.json` 契约。②`social_specs.json` 新增 `platforms.x.forms.article`，正文上限标 `uncertainty` + `safeMax` 75000（10 万字符仅第三方汇总，X 未公开固定数字）。③新增 `check_x_article`：正文/标题/首段字数、封面 16:9、分节数量、配图体积与格式、风险词；正文插图不套封面比例。④修复 `uncertain_max` 只认 `max` 不认 `maxChars` 的问题（字数规格带 uncertainty 时会抛 TypeError）；风险词扫描补上 `intro` / `digest` / `shortTitle`。⑤路由与 SKILL.md 登记第 4 个平台；`x/article` 归入静态形式。回归测试 137 → 153 项。 |
| **v1.5.0** | **补上配音能力，并明确禁用系统机器音。** ①新增 `motion-film/voiceover.md`：优先级链为用户提供 → **edge-tts** → 其他免费 TTS → **停下来问用户**；按片子气质选音色（性格→性别/语速/音高的映射表）并把理由写进 `plan.json.voiceover`；`say` / SAPI / eSpeak 一律禁用，**没有配音优于机器音**。②新增 `scripts/video-line/make_voiceover.py`：`--doctor` 体检、`--list-voices` 列音色、按 plan 逐幕生成配音与 SRT；edge-tts 输出为 24kHz mp3，自动转 48kHz 单声道 PCM wav；缺 edge-tts 时退出码 3（要求用户决定），**不降级**。③`check_environment.py` 增加 TTS 探测与禁用引擎识别，写入 `details.tts`，**不阻塞渲染**。④`pipeline-notes.md` 第 11 条由 `say` 用法改为 edge-tts 的正确用法与参数上限。⑤`SKILL.md` 第 6 步改为「配音、配乐与音效」。分册 18 → 19，脚本 6 → 7，回归测试 131 → 137 项。 |
| **v1.4.0** | **影片形式通用化：片型由内容决定，不再一律做成产品片。** ①形式 `generic/product-video` → `generic/motion-film`，目录 `references/platforms/generic/product-video/` → `motion-film/`；**旧 ID 不再兼容**（`LEGACY_ALIAS` 已移除，旧 plan.json 会报错）。②新增 `filmKind`（`product` / `evidence` / `explainer` / `story`）：`check_delivery.py` 按片型分派必备项——`product` 要求功能主张与原组件，`evidence`/`explainer` 要求 FACTS 或 RESEARCH，`story` 不要求主张但建议 `fictionNote`。③**不声明 `filmKind` 等于 `product`**，默认严格度与 v1.3.0 完全一致；任何片型都不许假造界面。④SKILL.md、routing、specs、README 同步改为「影片 + 片型」表述。回归测试 122 → 131 项。 |
| **v1.3.0** | **补上「只有网址」这一条最常见路径。** ①新增 `motion-film/web-first.md`：A/B/C 三级证据源（仓库 / 素材 / 网址），每级能做什么、不能做什么；公开来源清单（官网、文档、changelog、定价、公开仓库、数据集）与内容挖掘三层；三条硬线——只用公开可引用内容、不用泄露与付费墙内容、**不假造界面**。②新增 `motion-film/research-brief.md`：`RESEARCH.md` 契约（四问 + 证据级别与边界 + 与 FACTS/推导的关系），B/C 级必写。③`direction.md` §2 增加「证据级别 → 允许的信息形状」约束（C 级不能做 Workflow）。④`repo-and-style.md` 与 `component-pipeline.md` 开头加分流，避免只有网址时硬套仓库流程。⑤`check_delivery.py` 新增 `evidenceLevel` 解析与 `research_checks`：B/C 级缺 `RESEARCH.md` 报 error；功能镜头的原组件要求在非 repo 级别降级为 warning（**降级不等于放开伪造**）。⑥分册 15 → 18。回归测试 116 → 122 项。 |
| **v1.2.0** | **风格从「挑」改为「推导」，并补上节奏与内部溯源。** ①新增 `motion-film/style-derivation.md`：8 种信息形状 → 10 种运动语言 → 5 个性格滑块 → 单帧主构成 → 5 条不变量 + 3 条禁令；给主题或数据即可自行推导风格，不再需要用户先选风格。②新增 `motion-film/rhythm-brief.md`：路线（连续/蒙太奇/混合）、能量曲线（3 秒钩子、37% 爆点、停顿后砸落）、每小节事件密度、死时间判据。③`direction.md` 新增 §0 定标杆（学什么/绝不拿什么）；§3 由「各轴挑一个」改为「三种表达逻辑推导」并把轴表降级为手法库；§5 反重复改为六项（结构/开场/签名镜头/镜头路线/配乐形状/结尾）至少四项不同的硬判据。④`review.md` 新增独立审片人、必问「哪一段开始走神」、反馈四件套（时间码/镜头 ID/元素/源码位置）。⑤新增内部溯源契约 `provenance.md`（六形式共用一份 `evidence/FACTS.md`）；`check_social_delivery.py` 按「示意不惩罚、宣称事实无出处才阻断」分级校验。**FACTS 为内控底账，不随片交付、不主动展示。**⑥`plan.json` 新增 `styleDerivation` 字段，`--check-plan` 逐项校验。⑦分册 13 → 15。回归测试 98 → 116 项。 |
| **v1.1.0** | **把「文档纪律」变成「机器守卫」**，能力面不变、不新增平台。①`check_social_delivery.py --check-plan` 校验 `plan.json` 契约：形式是否登记、`factSource` 是否在 `selection` 内、`order` 与 `selection` 同集合、事实源排第一、静态形式不得排在动态形式之后、`audience` 必填。②`uncertainty` 从注释变成可执行约定：规格项统一为 `max` + `safeMax` + `uncertainty`，新增 `uncertain_of` / `uncertain_max` / `judge_count` / `report_uncertainty`，落在稳妥与官方之间的值报 WARN 并附原文；微信图片数量、小红书图片数量、小红书话题数量、小红书视频时长四项已归一。③`init_project.py --preset`（`generic` / `xhs-vertical` / `channels-horizontal` / `channels-vertical`）一次定好画幅与首帧/钩子要求，默认值与 v1.0.3 完全一致。④`probe_video` 收窄异常捕获，ffprobe 失败原因在报告末尾单独列出，不再静默成「合格」。⑤新增 `.github/workflows/regression.yml`：离线回归（Python 3.9 / 3.11 / 3.12）+ 模板探测 + 可选集成回归。⑥SKILL.md 平台包要点改为指向 `specs.md` 单一事实源，砍掉重复参数（约 -1.5K 字符）；README 补齐 `social content` / `product promo` 两个触发词。回归测试 73 → 98 项。 |
| **v1.0.3** | **补充第三方名称的使用说明**：`references/THIRD-PARTY.md` 新增 §2.3，逐类列出包内出现的第三方名称（案例对象 / 外部运行时依赖 / 素材来源标注 / 本机他 skill 名）及其性质，说明它们属**叙述性使用**、不是随包分发的第三方组件，并写明案例复盘保留产品实名的理由。**案例对象名一处未动**，仅新增说明。同版修正 `motion-film/audio-and-qa.md` 内置音效目录的链接为包内相对路径（原写法为包根相对路径，在按文件位置解析的渲染器下会断链）。 |
| **v1.0.2** | **起步工程改为完全原创**：`assets/platforms/generic/starter/` 的 29 个文件（运行时 `engine.js` / `film-store.js` / `client.jsx` / `film.jsx`、`kit/` 四件、`shots/` 两件、`presentations.jsx`、`product-context.jsx`、`fixtures/api.js`、`film.css`、六个工程脚本、`integration.config.mjs`、`package.json`、`adapters/` 四件）按同一对外契约重新实现，实现与表述全部新写。该目录由第三方代码改为本包原创，**包内自此没有任何第三方组件**；`NOTICE.md` 版权行改为 changjiashuai。对外契约（文件名、导出名、DOM 契约、CLI 参数、`window.*` API）全部保持不变，既有影片工程无需改动。 |
| **v1.0.1** | **默认样式改为完全原创**：`assets/platforms/generic/fallback/` 的 `tokens.css` 与 `primitives.jsx` 重写为「纸墨」样式（纸白 / 墨黑双色调，纸叠 + 纸面结构），随包的两张预览图按新样式重新渲染。该目录由第三方 BSL 1.1 组件改为本包原创 AGPL-3.0，**包内自此没有任何限制商业使用的组件**。对外契约（类名、`--film-*` 变量名、四个组件导出名）保持不变。 |
| **v1.0.0** | **首个独立发布版**。两级路由（先平台后形式，均可多选）；3 个平台包 6 个形式：微信（图文 / 公众号长文 / 视频号）、小红书（图文笔记 / 视频笔记）、通用（产品片）。产品片体系完整内置：13 个方法论分册、6 个工程脚本、起步工程、默认样式、6 个手法样例、2 个配乐示例、11 个原创音效；规格单一事实来源 `social_specs.json`；平台线自检（含公众号 HTML 白名单体检与小红书风险词扫描）+ 产品片结构与媒体自检；7 套模板 + 模板画布尺寸探测；平台线与视频线离线回归测试；本基线文档与平台接入契约。**无外部 skill 依赖。** |

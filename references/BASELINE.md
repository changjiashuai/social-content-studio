# 基线 BASELINE

本文件是 `social-content-studio` **v1.0.3 的基线快照**：把"已经跑通的能力"在平台化结构中固定下来，
明确哪些是共用底座、哪些是平台专属、规格版本是什么、怎么校验。
**后续每新增一个平台，都在此基线上叠加；基线本身只增不改。**

一句话：**基线 = 平台无关的共用底座（`core/`）+ 已固化的平台包（`references/platforms/` 与 `assets/platforms/`）+ 原生产品片体系（`SKILL.md` 总纲 + `product-video/` 分册 + `scripts/video-line/`）。**

---

## 1. 基线的三条约束

1. **可比对。** 基线里的每一项能力都必须能被一个具体文件 + 一条校验命令指认，不许"口头声称支持"。
2. **不漂移。** 产品片体系有**两个明确的事实源**：**流程总纲**在 `SKILL.md` 的「通用平台 · 产品片」章节（7 步 + 硬约束 + 工程入口），**细则**在 `references/platforms/generic/product-video/` 的 13 个分册；总纲不复制分册正文，分册不改写总纲结论，分册之间也不互相复制。规格以 `scripts/social_specs.json` 单一事实源保存，模板与自检都从它读。§4 的基线指纹可用于逐文件核对。
3. **不缩减。** 新增平台只能**叠加**，不得删改已有平台包与 `core/` 的既有语义。产品宣传片 / 版本更新片必须始终可被选中（路由第 3 项 `通用`）。

---

## 2. 基线组成（v1.0.3，本版冻结）

| 层 | 位置 | 内容 | 说明 |
|---|---|---|---|
| 产品片·总纲 | `SKILL.md` →「通用平台 · 产品片」 | 术语、7 步流程、硬约束、工程入口 | **流程的唯一事实源**；分册不改写其结论 |
| 产品片·细则 | `references/platforms/generic/product-video/` | 13 个分册（方向 / 文案节奏 / 手法词汇 / 组件接入 / 起步工程 / 仓库审计 / 依赖安装 / 配乐 / 混音验收 / 审片 / 封面 / 案例复盘 / 本机实测管线） | **细则的唯一事实源**；总纲不复制其正文 |
| 产品片·工程 | `scripts/video-line/` | 初始化、环境预检、音效落点、混音、音效生成、结构与媒体自检 | 6 个脚本，纯标准库；混音与落点需 ffmpeg |
| 产品片·资产 | `assets/platforms/generic/` | `starter/`（起步工程：运行时 / 构建 / 预览 / 渲染 / 封面 / 静帧 / 适配器 / fixture）、`fallback/`（默认样式「纸墨」）、`fx-lab/`（6 个手法样例）、`audio/`（2 个配乐示例 + 11 个音效 + manifest） | **全部本包原创** |
| 共用底座 | `references/core/` | 路由协议、生产管线、跨平台一致性、平台接入契约 | 平台无关，被所有平台包共用 |
| 平台包·通用 | `references/platforms/generic/` | `PLATFORM.md`（入口 + 分册索引 + 工程与资产 + 红线）+ `specs.md`（兜底规格 + 两层自检覆盖范围） | 方法论正文在总纲与分册（见 `core/platform-schema.md` §2 的例外约定） |
| 平台包·微信 | `references/platforms/wechat/` | 图文 / 公众号长文 / 视频号三条线 + 官方规格总表 | v1.0.0 全覆盖 |
| 平台包·小红书 | `references/platforms/xiaohongshu/` | 图文笔记 / 视频笔记两条线 + 规格总表（含来源质量提示） | v1.0.0 全覆盖 |
| 规格事实源 | `scripts/social_specs.json` | `shared` + `platforms.<平台>.forms.<形式>` | 模板画布尺寸与自检阈值都从这里读 |
| 校验·平台线 | `scripts/check_social_delivery.py` + `scripts/render_social_assets.mjs` + `tests/test_check_social_delivery.py` | 产出物自检 + 模板尺寸探测 + 平台线回归 | 纯标准库，不依赖 ffmpeg / Pillow / 网络 |
| 校验·产品片 | `scripts/video-line/check_delivery.py` + `tests/test_video_line_regressions.py` + `tests/integration.mjs` | 结构与媒体自检 + 视频线回归 + 可选集成回归 | 混音/落点两项需 ffmpeg，缺则自动跳过 |
| 授权 | `LICENSE` + `references/THIRD-PARTY.md` | 作者 changjiashuai，AGPL-3.0；**包内无第三方组件** | 无外部运行时依赖；**无限制商用的组件** |

---

## 3. 基线能力清单（不得削减）

### 3.1 产品片能力（`generic/product-video`）

| 能力 | 位置 |
|---|---|
| 产品宣传片 / 版本更新片（横版 16:9 或自由画幅） | 路由 → `通用` 平台 → `generic/product-video` |
| 产品取材、`DIRECTION.md`、镜头表、专属手法推导（流程 1–7 步） | `SKILL.md` 总纲；被所有平台包共用 |
| 分镜与文案、视觉手法词汇、组件接入、审片、封面 | `product-video/` 对应分册 |
| 工程初始化 / 环境预检 / 无头渲染 / 编码 / 混音 / 结构自检 | `scripts/video-line/` 六个脚本 |
| 起步工程、默认样式、手法样例、配乐示例、11 个原创音效 | `assets/platforms/generic/` |
| 已实跑验证的本机管线与 28 条环境坑 | `product-video/pipeline-notes.md` |

### 3.2 平台能力（`references/platforms/`）

| 平台 | 形式 | 自检函数 |
|---|---|---|
| 通用 | `generic/product-video` | `check_generic_product_video`（兜底结构检查）+ `video-line/check_delivery.py`（强检查） |
| 微信 | `wechat/image-text` | `check_wechat_image_text` |
| 微信 | `wechat/mp-article` | `check_wechat_mp_article` |
| 微信 | `wechat/channels` | `check_wechat_channels` |
| 小红书 | `xiaohongshu/image-text` | `check_xhs_image_text` |
| 小红书 | `xiaohongshu/video` | `check_xhs_video` |

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

# ── 产品片（改了 video-line 或产品片产出物后跑）──
python3 $SKILL/scripts/video-line/check_delivery.py <video-dir>/plan.json \
  --video <video-dir>/renders/final.mp4 --mix-report <video-dir>/evidence/audio-mix.json

# ── 可选：真实构建 + 无头浏览器（需要已安装的 video/node_modules）──
node $SKILL/tests/integration.mjs --modules <video-dir>/node_modules
```

①②③ 全绿，才算"平台线基线未漂移"。

---

## 4. 基线指纹（v1.0.3）

用于核对基线是否被改动。完整 SHA-256 可用 `shasum -a 256 <file>` 复算（下表取前 16 位）。

### 4.1 入口与项目文件

| 文件 | SHA-256 前 16 位 |
|---|---|
| `.gitignore` | `6e0cb83e04db8cd4` |
| `README.md` | `2b0cbbbb55752346` |
| `SKILL.md` | `588905fa3dc3ebd2` |
| `agents/openai.yaml` | `ecbfa04409b23ee2` |

### 4.2 文档与基线

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/THIRD-PARTY.md` | `4f10f901710328ca` |

### 4.3 共用底座（core）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/core/cross-platform.md` | `013dc99c5877e865` |
| `references/core/pipeline.md` | `99cd7e21188bf539` |
| `references/core/platform-schema.md` | `62d68785f8085cef` |
| `references/core/routing.md` | `d446bcb8d6190aa1` |

### 4.4 平台包 · 微信

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/platforms/wechat/PLATFORM.md` | `30f75b455c1b93f7` |
| `references/platforms/wechat/channels.md` | `a17c4908546a8f4f` |
| `references/platforms/wechat/image-text.md` | `5898947f13a77a2a` |
| `references/platforms/wechat/mp-article.md` | `8a091cd155972a1a` |
| `references/platforms/wechat/specs.md` | `2a1f126708916602` |

### 4.5 平台包 · 小红书

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/platforms/xiaohongshu/PLATFORM.md` | `492b52a073ced4fc` |
| `references/platforms/xiaohongshu/image-text.md` | `aa1512be5aca90e8` |
| `references/platforms/xiaohongshu/specs.md` | `78396ca6430be1c6` |
| `references/platforms/xiaohongshu/video.md` | `503b6b518ec2f991` |

### 4.6 平台包 · 通用（产品片）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `references/platforms/generic/PLATFORM.md` | `3ac2a0a851f50119` |
| `references/platforms/generic/product-video/audio-and-qa.md` | `a55ef57ad10f5e40` |
| `references/platforms/generic/product-video/audio-sourcing.md` | `935d9f7861af2871` |
| `references/platforms/generic/product-video/case-study.md` | `2e2268183a8793cb` |
| `references/platforms/generic/product-video/component-pipeline.md` | `d7ebea1a79698ee8` |
| `references/platforms/generic/product-video/cover.md` | `7cf9f6a5ee3a5342` |
| `references/platforms/generic/product-video/direction.md` | `cb5e549ae93cb2b1` |
| `references/platforms/generic/product-video/onboarding.md` | `1ac708ea4ccf47cf` |
| `references/platforms/generic/product-video/pipeline-notes.md` | `4cf3cb13d65072ab` |
| `references/platforms/generic/product-video/repo-and-style.md` | `1d1d2c210eda1bf1` |
| `references/platforms/generic/product-video/review.md` | `277eaedb111cd882` |
| `references/platforms/generic/product-video/starter.md` | `d303b4b564e56356` |
| `references/platforms/generic/product-video/story-and-copy.md` | `b276335346bd8cb3` |
| `references/platforms/generic/product-video/visual-vocabulary.md` | `09d7fea454bd4d71` |
| `references/platforms/generic/specs.md` | `5134aca864169fe0` |

### 4.7 平台线脚本

| 文件 | SHA-256 前 16 位 |
|---|---|
| `scripts/check_social_delivery.py` | `0e2b72752a831284` |
| `scripts/render_social_assets.mjs` | `93c51823b86a0ddd` |
| `scripts/social_specs.json` | `fd217c742102df25` |

### 4.8 产品片脚本

| 文件 | SHA-256 前 16 位 |
|---|---|
| `scripts/video-line/check_delivery.py` | `3411ce67335f2ef6` |
| `scripts/video-line/check_environment.py` | `51ed8a2fc10d3ed1` |
| `scripts/video-line/init_project.py` | `7d91e2b596687641` |
| `scripts/video-line/make_sfx.py` | `7c4cb127d93096ea` |
| `scripts/video-line/mix_audio.py` | `3f0a3e4f51ab917c` |
| `scripts/video-line/sfx_landmarks.py` | `1d9059653fa7b10d` |

### 4.9 回归测试

| 文件 | SHA-256 前 16 位 |
|---|---|
| `tests/integration.mjs` | `f717acf428b04b08` |
| `tests/test_check_social_delivery.py` | `696409b2132c3564` |
| `tests/test_video_line_regressions.py` | `fb12bb2666bb3b7e` |

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
| `assets/platforms/generic/fallback/SOURCE.md` | `2f610c1d2ad63ce2` |
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
| `assets/platforms/generic/fx-lab/README.md` | `820d179eb5a4e8a6` |
| `assets/platforms/generic/fx-lab/glyph-field.js` | `42889ae9b4c0696e` |
| `assets/platforms/generic/fx-lab/horizon.jsx` | `7c55381b2a584db7` |
| `assets/platforms/generic/fx-lab/orbit.js` | `76db9b43a5d5b005` |
| `assets/platforms/generic/fx-lab/settle.js` | `eac60efb54467de4` |
| `assets/platforms/generic/fx-lab/slices.jsx` | `426f18996ce0e0ff` |
| `assets/platforms/generic/fx-lab/warp.js` | `19c8d89444f5957e` |

### 4.15 配乐与音效（audio）

| 文件 | SHA-256 前 16 位 |
|---|---|
| `assets/platforms/generic/audio/SOURCE.md` | `e8c05ac607470c60` |
| `assets/platforms/generic/audio/manifest.json` | `dd0d41c40c8902cd` |
| `assets/platforms/generic/audio/score-example-cinematic.py` | `2e0124af54525519` |
| `assets/platforms/generic/audio/score-example-keys.py` | `2e24e798667373a0` |
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

要给本 skill 加一个平台（例如 B 站、抖音），**只做下面 5 件事**，不碰 `core/` 语义、不碰其他平台包、不碰产品片体系：

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
| **v1.0.3** | **补充第三方名称的使用说明**：`references/THIRD-PARTY.md` 新增 §2.3，逐类列出包内出现的第三方名称（案例对象 / 外部运行时依赖 / 素材来源标注 / 本机他 skill 名）及其性质，说明它们属**叙述性使用**、不是随包分发的第三方组件，并写明案例复盘保留产品实名的理由。**案例对象名一处未动**，仅新增说明。同版修正 `product-video/audio-and-qa.md` 内置音效目录的链接为包内相对路径（原写法为包根相对路径，在按文件位置解析的渲染器下会断链）。 |
| **v1.0.2** | **起步工程改为完全原创**：`assets/platforms/generic/starter/` 的 29 个文件（运行时 `engine.js` / `film-store.js` / `client.jsx` / `film.jsx`、`kit/` 四件、`shots/` 两件、`presentations.jsx`、`product-context.jsx`、`fixtures/api.js`、`film.css`、六个工程脚本、`integration.config.mjs`、`package.json`、`adapters/` 四件）按同一对外契约重新实现，实现与表述全部新写。该目录由第三方代码改为本包原创，**包内自此没有任何第三方组件**；`NOTICE.md` 版权行改为 changjiashuai。对外契约（文件名、导出名、DOM 契约、CLI 参数、`window.*` API）全部保持不变，既有影片工程无需改动。 |
| **v1.0.1** | **默认样式改为完全原创**：`assets/platforms/generic/fallback/` 的 `tokens.css` 与 `primitives.jsx` 重写为「纸墨」样式（纸白 / 墨黑双色调，纸叠 + 纸面结构），随包的两张预览图按新样式重新渲染。该目录由第三方 BSL 1.1 组件改为本包原创 AGPL-3.0，**包内自此没有任何限制商业使用的组件**。对外契约（类名、`--film-*` 变量名、四个组件导出名）保持不变。 |
| **v1.0.0** | **首个独立发布版**。两级路由（先平台后形式，均可多选）；3 个平台包 6 个形式：微信（图文 / 公众号长文 / 视频号）、小红书（图文笔记 / 视频笔记）、通用（产品片）。产品片体系完整内置：13 个方法论分册、6 个工程脚本、起步工程、默认样式、6 个手法样例、2 个配乐示例、11 个原创音效；规格单一事实来源 `social_specs.json`；平台线自检（含公众号 HTML 白名单体检与小红书风险词扫描）+ 产品片结构与媒体自检；7 套模板 + 模板画布尺寸探测；平台线与视频线离线回归测试；本基线文档与平台接入契约。**无外部 skill 依赖。** |

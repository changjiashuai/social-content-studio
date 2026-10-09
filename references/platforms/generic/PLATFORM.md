# 通用平台包（generic）

**平台 ID**：`generic`
**形式**：`generic/product-video`（产品宣传片 / 版本更新片）
**规格单一事实来源**：`scripts/social_specs.json` → `platforms.generic`

> `generic` 表示**不绑定具体投放平台的自有渠道成片**：官网首屏、社群、邮件、活动大屏、其他未纳入本 skill 的视频平台。
> 因为它不绑定平台，所以**没有平台侧的硬规格**——画幅、时长、封面都由用途决定。取而代之的约束来自视频线自身的方法论（真实功能、原组件、方向先行、不套模板）。

本平台包与微信、小红书两包**结构相同**，区别只在于它的方法论体量最大、资产最多：本形式自带一整套代码驱动的制作体系（起步工程、无头渲染、代码合成配乐、混音与证据、自动检查与审片），共 13 个分册分置在 `product-video/` 下。

---

## 1. 形式索引

| 形式 ID | 形态 | 交付物 | 完整方法论位置 |
|---|---|---|---|
| `generic/product-video` | 代码驱动的产品宣传片 / 版本更新片 | MP4 + 可复现工程 + 预览帧 + 3:4 / 4:3 / 16:9 封面 + 发布文案 | **`SKILL.md` →「通用平台 · 产品片」章节**（总纲）+ `product-video/` 13 个分册（细则） |

**总纲与分册的分工**：`SKILL.md` 那一章是**流程与硬约束的主干**（7 步流程 + 硬约束 + 工具入口），保证主入口自身可用；分册是**每一步的细则**，按需加载。两者不重叠：主干不复制分册正文，分册不改写主干结论。

## 2. 完整方法论（`product-video/`，13 个分册）

| 分册 | 什么时候读 | 讲什么 |
|---|---|---|
| [direction.md](product-video/direction.md) | **第 4 步，动手写代码之前** | 拆参考、提炼产品气质、沿不同的轴提三个方向、专属手法推导（「因为产品有 X、所以用 Y」）、反重复、画面规范、到每秒的镜头表 |
| [story-and-copy.md](product-video/story-and-copy.md) | 第 4–5 步，写文案时 | 从更新清单到故事、中文文案说人话、标题的中英分工、文案试读、动作与停留、静帧审阅 |
| [visual-vocabulary.md](product-video/visual-vocabulary.md) | 第 5 步，选手法时 | 按作用分组（开场与钩子 / 品牌与标志 / 舞台与背景 / 产品上镜 / 章节与文字 / 转场）的手法，写明表达什么、从哪里推导、怎么实现、何时不用 |
| [component-pipeline.md](product-video/component-pipeline.md) | 第 3、5 步，接通组件时 | 从真实业务组件到可渲染画面：找原功能入口、补 provider、fixture 接口、原组件状态与动画、复用证据、确定性与时间线、构图裁切、链接处理 |
| [starter.md](product-video/starter.md) | 第 2、5 步 | 起步工程的运行时结构（seek、GSAP 主时间轴、`onRender`、`onDrive`）、接入仓库、样式链、`plan.json` 字段 |
| [repo-and-style.md](product-video/repo-and-style.md) | 第 3 步，调查产品时 | 更新事实与证据、原组件及设计依赖审计、默认样式的适用范围 |
| [onboarding.md](product-video/onboarding.md) | **环境检查报缺项时才读** | 只针对被报告的那几个缺项安装，装完用 `--force` 复查 |
| [audio-sourcing.md](product-video/audio-sourcing.md) | 第 6 步 | 音乐来源优先级（用户提供 → 本机可用生成模型 → 代码合成）、先编曲再合成、音效先找录音素材、对位方法、来源留存 |
| [audio-and-qa.md](product-video/audio-and-qa.md) | 第 6–7 步 | 从「写了音效」到「真的听得见」、音乐让位、卡点、混音、自动检查、最终人工检查 |
| [review.md](product-video/review.md) | 第 5、7 步 | 三个审片节点、联系表与转场条带、常见问题对照表、指标只是提示 |
| [cover.md](product-video/cover.md) | 第 7 步，要发布时 | 3:4 / 4:3 / 16:9 三种比例的布局思路、选图、文案与导出 |
| [case-study.md](product-video/case-study.md) | **出问题时查** | 原案例复盘：有效的做法、迭代中真正修过的问题、第二/第三个项目的经验、手法是怎么从产品推导出来的 |
| [pipeline-notes.md](product-video/pipeline-notes.md) | 渲染 / 编码 / 音频踩坑时查 | 本机实测管线与环境坑（沙箱、headless 模式、zsh 通配符、loudnorm、首帧与安全边距自检等），已实跑验证 |

## 3. 工程与资产

**脚本**（`scripts/video-line/`）：

| 脚本 | 用途 |
|---|---|
| `init_project.py --output <video-dir> --style repo\|default\|hybrid --repo <repo-dir>` | 初始化隔离的视频工程（复制起步工程；`default`/`hybrid` 另复制默认样式）。`repo`/`hybrid` 必须传 `--repo` |
| `check_environment.py --project <video-dir> --engine browser\|hyperframes [--force]` | 环境预检，只报告缺项 |
| `sfx_landmarks.py <files> [--json]` | 实测音效的起音点、峰值时间与峰值电平 |
| `mix_audio.py <plan.json>` | 混音、音乐让位、独立音轨与证据报告（`evidence/audio-mix.json`） |
| `make_sfx.py --output <new-sfx-dir>` | 改变音色时重新生成内置音效 |
| `check_delivery.py <plan.json> [--video <final.mp4>] [--mix-report <audio-mix.json>]` | 结构与媒体自检（见下方 §6） |

**资产**（`assets/platforms/generic/`）：

| 目录 | 内容 |
|---|---|
| `starter/` | 起步工程（运行时、构建、预览、渲染、封面、静帧、适配器、fixture）。`init_project.py` 从这里复制。本包原创，AGPL-3.0，**无商用限制** |
| `fallback/` | 默认样式「纸墨」的组件与 token（纸白 / 墨黑双色调）。**本包原创，AGPL-3.0，无商用限制**，见该目录 `SOURCE.md` |
| `fx-lab/` | 6 个可改写的手法样例（流线场 / 粒子汇聚 / 字符场 / 发光地平线 / 切片 / 环绕），是推导示范不是风格包 |
| `audio/` | 两种气质的代码合成配乐示例 + `sfx/`（11 个原创 WAV）+ `manifest.json`（时长与 SHA-256） |

## 4. 平台级红线

| 红线 | 说明 |
|---|---|
| **没有 `DIRECTION.md` 不许开工** | 正式片必须有：选定方向与理由、从产品推导的专属手法、画面规范、到每秒的镜头表。`check_delivery.py` 会拦。 |
| **不得套模板** | 每个视觉手法都要能说出它对应产品的哪一点。同一工作区连续做片，不复用上一支的开场 / 章节 / 背景手法。 |
| **界面正文 ≥ 22px（1080p）** | 接入真实业务组件与原样式；抽象化只用于取景、布局和外层动画。 |
| **首帧必须完整** | 前 5–10 帧要是一个完整画面（通常是开场段落完成态），不能是空白底色或等待入场的背景——平台会抓首帧当缩略图。`check_delivery.py` 会测前 5 帧墨量。 |
| **范围必须由用户拍板** | 覆盖全量产品还是某个版本区间、覆盖哪些平台面（桌面 / CLI·TUI / 移动 / API），写进 `plan.scope`。交付时声明**没有**覆盖的平台面。 |
| **自动检查不等于验收** | 交付说明里必须分清：哪些是脚本检查过的、哪些是实际看过 / 听过的、哪些仍未验证。 |

## 5. 与 `core/` 的接口

| 需要什么 | 去哪里 |
|---|---|
| 取材、方向、渲染、编码、自检纪律 | `references/core/pipeline.md` |
| 多平台同做时的口径与素材复用 | `references/core/cross-platform.md` |
| 两级路由与执行顺序 | `references/core/routing.md` |
| 本形式兜底参数（机器可读） | `scripts/social_specs.json` → `platforms.generic.forms.product-video` |
| **总纲（7 步流程 + 硬约束）** | `SKILL.md` →「通用平台 · 产品片」 |
| **细则（13 个分册）** | 本目录 `product-video/` |

## 6. 自检

本形式有**两层**自检，职责不同，都要跑：

```sh
SKILL=~/.workbuddy/skills/social-content-studio

# ① 视频线自检（强）：结构 / 时间线 / 方向文件 / 主张溯源 / 媒体参数 / 节奏 / 首帧
python3 $SKILL/scripts/video-line/check_delivery.py <video-dir>/plan.json \
  --video <video-dir>/renders/final.mp4 --mix-report <video-dir>/evidence/audio-mix.json

# ② 平台线兜底自检（弱）：交付文件存在、可探测、时长 > 0
python3 $SKILL/scripts/check_social_delivery.py --project <content-dir> \
  --forms generic/product-video

# 看规格
python3 $SKILL/scripts/check_social_delivery.py --print-specs --form generic/product-video
```

`check_delivery.py` 的输出里有一项 `limits`，逐条写明它**不**证明什么（不做主张的语义核实、不做画面品味判断、不做听感与音画同步判断、节奏数字只是"该去看哪一段"的提示）。**不要把它的 `ok: true` 当成成片已验收。**

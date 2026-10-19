# 来源与授权说明

**本 skill 由 changjiashuai 维护，以 AGPL-3.0 发布。** 本文件说明两件事：包内内容统一适用的许可，以及内容生产时对外部素材与平台规则的约束。

---

## 1. 本包的授权范围

| 项 | 值 |
|---|---|
| 作者 / 版权 | **changjiashuai** |
| 授权 | **AGPL-3.0**（完整声明见 [`LICENSE`](../LICENSE)） |
| 适用本协议的范围 | **包内全部内容**：`SKILL.md`、`README.md`、`references/`、`scripts/`、`tests/`、`assets/`（含各平台模板、默认样式 `fallback/`、起步工程 `starter/`、手法样例、音效与配乐示例）。无例外 |
| 外部运行时依赖 | **无**。本 skill 可独立安装、独立分发，运行时不需要任何其他 skill 存在 |

---

## 2. 包内第三方组件

**没有。** 本包不含任何由他人创作、需要单独声明许可或另行取得授权的组件。全包（含默认样式与起步工程）都是本 skill 作者的作品，统一适用本包的 AGPL-3.0。

因此分发时**只需带上本包的 `LICENSE`**，不存在"某个子目录另有条款"的情况。**包内也没有任何限制商业使用的组件**——可自由用于收费产品、白标与商业平台。

### 2.1 `starter/` 里那两个文件是什么

`assets/platforms/generic/starter/` 目录内保留了 `LICENSE` 与 `NOTICE.md`。它们是**为复制出去的影片工程准备的**，不是第三方声明：

- `init_project.py` 会把 `starter/` 整个复制成用户的视频工程目录；工程脱离本 skill 独立存在后，需要自带一份许可与版权声明。
- 两者都指向本 skill 作者与 AGPL-3.0，与包外任何项目无关。

### 2.2 对外契约的保留说明

`fallback/` 与 `starter/` 都保留了若干**类名、CSS 变量名、导出名与文件名**（如 `film-theme`、`--film-*`、`CardFrame`、`onRender`、`engine.js`）。这些是被既有影片工程和本包脚本引用的**接口名**，为兼容性而原样保留，不表示这些名字或代码来自第三方。

### 2.3 包内出现的第三方名称（叙述性使用，不是第三方组件）

包内多处提到具体产品与工具的名字。**这些是文字指代，不是随包分发的第三方组件**，§2 的结论不变。

| 名称 | 出现位置 | 性质 |
|---|---|---|
| `CodePilot`（14 处 / 9 文件）、`Hero UI`、`Talis`、`Zed`、`GLM 5.3`、`TokenDance` | `references/platforms/generic/motion-film/` 下的 `case-study.md`、`component-pipeline.md`、`cover.md`、`direction.md`、`story-and-copy.md`、`assets/platforms/generic/fx-lab/README.md`、`assets/platforms/generic/audio/SOURCE.md`、`audio/score-example-*.py` | **案例对象**：`case-study.md` 复盘的产品，以及其中引用的参考片和故障条目里出现的组件名 |
| `HyperFrames`（22 处 / 7 文件） | `onboarding.md`、`PLATFORM.md`、`scripts/video-line/check_environment.py` 等 | **外部运行时依赖名**：npm 包名、CLI 命令、`--engine` 取值 |
| `Pixabay`（7 处 / 4 文件） | `audio-sourcing.md`、`audio-and-qa.md`、`case-study.md`、`assets/platforms/generic/audio/SOURCE.md` | **素材来源与许可标注**：用于声明本 skill 不捆绑这些录音、不携带其原片 |
| `media-use`（2 处 / 2 文件） | `audio-sourcing.md`、`case-study.md` | **本机另一个 skill 的名称**：操作指引，提示用户到哪里取本地素材库 |

这些名称以**指明事实**的方式出现（"本 skill 作者为某产品做过宣传片""运行时需要某工具""某段录音来自某素材库"）。本 skill 与上述任何一方**无隶属、赞助、背书或合作关系**；包内不含其中任何一方的代码、录音、字体或图形资产——案例中出现的产品界面按 §4 以真实界面呈现，不随包分发。

案例复盘保留产品实名，是因为该册的价值在于**可复核**：对照实验（同一仓库做过三版）、手法推导（表中每一行的"因为该产品有……"）与配乐谱系（`SOURCE.md` 与 `score-example-*.py` 的出处说明）都以同一对象为锚点。匿名化会让这些内容退化为无法验证的断言，并与产品片自检所要求的"主张可溯源"相冲突。

---

## 3. 平台规则引用（不是本 skill 的创作内容）

各平台参数属于**平台公开规则**。每个平台包都有一份人读规格总表，参数旁标注来源：

| 平台 | 规格文件 | 来源质量 |
|---|---|---|
| 微信 | `references/platforms/wechat/specs.md` | 以微信官方文档 / 帮助中心 / 服务市场为主 |
| 小红书 | `references/platforms/xiaohongshu/specs.md` | **官方未公开完整规格**，主要依据创作服务平台编辑器实际提示 + 第三方汇总；相关条目全部标 `uncertainty`，不得当确定值使用 |
| 通用 | `references/platforms/generic/specs.md` | **不引用平台规则**（自有渠道无平台侧规格）；表中数值是本 skill 自定的兜底阈值 |

**平台规则会变**：距上次核对超过 3 个月，使用前重新核对来源页。

本 skill 不包含任何平台的私有接口实现、不代用户调用公众号 / 视频号 / 小红书账号接口、不存储任何账号凭据。
微信服务号自动化路径（`add_news` / `uploadimg` / `add_material`）仅作**字段说明**，实际调用与鉴权由用户自行完成。

---

## 4. 素材版权（内容生产时的约束）

- 产品截图：使用**真实产品界面**，不重绘冒充。
- 官方图表 / 图片：记录来源与许可；在视频尺度 / 图文尺度下不可读时，按数据点重建矢量图并标注来源。
- 配乐与音效：来源优先级为「用户提供 → 本机可用的生成模型 → 代码合成」，交付时说明授权状态。包内 `assets/platforms/generic/audio/sfx/` 是 11 个程序生成的原创 WAV（无第三方采样），`score-example-*.py` 是代码合成的示例配乐；它们随包提供，来源说明见该目录 `SOURCE.md`。
- 字体：所有平台一律系统字体栈，不内嵌也未授权字体；需要特殊字体时以图片形式呈现。
- **授权不明的一律不用。** 本 skill 不对用户提供的素材做版权背书。

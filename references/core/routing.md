# 两级内容路由 routing

本文件定义 `social-content-studio` 的**强制前置交互**：产出任何内容之前，先选**平台**，再选该平台下的**内容形式**。
这是本 skill 唯一一个"不选就不许往下走"的步骤。

---

## 1. 为什么是两级，而不是把形式平铺成一列

- **平台决定硬规格，形式决定叙事骨架。** 画幅、字数、体积、封面比例、审核红线由平台定；"每张图一个观点"还是"一条论证链"由形式定。两者正交，必须分开问，否则用户在第一问里被塞进一堆无关参数。
- **防止选项爆炸。** 平铺路由在平台增多后不可维护：微信 3 种 + 小红书 2 种 + 未来 B 站/抖音各 2 种……用户要在一屏里读十几项，而你每加一个平台都在污染所有已有平台的交互。
- **两级与复用半径对齐。** 同一平台内的多形式复用（一次渲染出多个画幅、共用同一套话题与口径）比跨平台复用更紧密。先按平台分组，再选形式，复用方案才能一次定下来。
- **平台稳定，形式易变。** 平台几乎不变，平台下的形式会增删（例如某平台新出"图文+视频"混合形态）。两级结构让形式层可以独立演进，不影响其他平台。

---

## 2. 第一级：选平台（必须支持多选）

| 序号 | 平台 ID | 标签（展示给用户） | 选项描述 |
|---|---|---|---|
| 1 | `wechat` | `1 微信` | 公众号 / 视频号生态：图文消息（小绿书）、公众号长文、视频号视频 |
| 2 | `xiaohongshu` | `2 小红书` | 图文笔记、视频笔记 |
| 3 | `generic` | `3 通用（自有渠道）` | 不绑定平台的成片：产品宣传片 / 版本更新片（原视频线），可发官网、社群、其他渠道 |

**参数**：`multiSelect: true`；`header` 用「投放平台」（≤12 字符）。

> 第 3 项 `generic` 必须存在。它承载本 skill 的视频线原生能力（产品宣传片、版本更新片）。**去掉它等于削减已有能力。**

---

## 3. 第二级：选内容形式（对每个已选平台各问一次，可合并为一次多选）

### 微信（`wechat`）

| 序号 | 形式 ID | 标签 | 说明 |
|---|---|---|---|
| 1 | `wechat/image-text` | `1 图文（图片+文案）` | 图片消息 / 小绿书：3:4 图卡组 + 配套短文案，横滑浏览 |
| 2 | `wechat/mp-article` | `2 公众号（长文）` | 标题 / 摘要 / 正文 / 封面，内联样式排版，可直接粘贴后台 |
| 3 | `wechat/channels` | `3 视频号（视频）` | 成片 + 6:7 封面 + 描述与短标题 |

### 小红书（`xiaohongshu`）

| 序号 | 形式 ID | 标签 | 说明 |
|---|---|---|---|
| 1 | `xiaohongshu/image-text` | `1 图文笔记` | 3:4 图集 + 标题(≤20 字) + 正文(≤1000 字) + 话题标签 |
| 2 | `xiaohongshu/video` | `2 视频笔记` | 9:16 竖屏成片 + 3:4 封面 + 标题/正文 |

### 通用（`generic`）

| 序号 | 形式 ID | 标签 | 说明 |
|---|---|---|---|
| 1 | `generic/product-video` | `1 产品片（原视频线）` | 产品宣传片 / 版本更新片，横版 16:9，可自由画幅 |

**参数**：`multiSelect: true`；`header` 用「内容形式」。

---

## 4. 提问话术（两级各一句，不要合并成一大问）

第一级：

> 这次要投放到哪些平台？（可多选）选定后我再问你每个平台要哪种内容形式。

第二级（以微信为例）：

> 微信这边要哪种？（可多选）`1 图文（图片+文案）` / `2 公众号（长文）` / `3 视频号（视频）`

不要在平台问里夹带画幅、时长、风格——那些是选定形式之后的追问项。

---

## 5. 事实源与执行顺序（多选时才生效）

**事实源** ＝ 本次内容里承载**最完整论证与数据出处**的那一个形式。所有其他形式的数字、口径、免责说明都必须能追溯到它。

### 5.1 事实源判定（按优先级，取第一个命中的）

| 优先级 | 条件 | 事实源 |
|---|---|---|
| 1 | 含 `wechat/mp-article` | `wechat/mp-article`（上限 50000 字，论证空间最大） |
| 2 | 含 `xiaohongshu/image-text` | `xiaohongshu/image-text`（正文上限 1000 字，是图文类里最完整的） |
| 3 | 含任一视频形式 | 该视频形式的**脚本 / 镜头表**（`DIRECTION.md` + 分镜表） |
| 4 | 仅 `wechat/image-text` | `wechat/image-text`（逐图文案中最长的一条作为骨架） |

### 5.2 执行顺序（拓扑排序，先事实源后派生）

```
① 事实源（上表命中项，最先做）
② 其余静态形式：wechat/image-text、xiaohongshu/image-text
③ 动态形式：wechat/channels、xiaohongshu/video、generic/product-video
```

同层内按用户选择顺序。**先长后短、先静后动**——反了会导致各端口径打架，或长文退化成视频脚本的注水版。

### 5.3 红线

- 不允许"先做视频再倒推长文"。长文是可信度最高的载体，让它去追视频的口播稿，等于把可信度最高的载体降级。
- 只有 `generic/product-video` 时，独立走视频线原生流程（`SKILL.md` 视频线章节 1–7 步），不受本节约束。

---

## 6. 追问规则（选定形式之后，只追问一轮）

追问一次、合并同类问题，不连环问：

| 选中形式含 | 追问内容 | 为什么必须问 |
|---|---|---|
| 任一"文字型"形式（`wechat/mp-article` / `wechat/image-text` / `xiaohongshu/image-text` / `xiaohongshu/video` 的正文） | 读者是「企业决策者 / 技术人员 / 大众消费者」中的哪一类？要不要带货口吻？ | 决定长文信息密度与图文的语言风格，直接决定选题取舍 |
| 任一视频形式 | 竖版 9:16 还是横版 16:9？有没有出镜人？硬字幕还是纯画面？ | 画幅必须在分镜之前定死；出镜与否决定拍摄/素材路径 |
| 两个及以上平台 | 各平台是否统一主视觉与口号？有没有必须出现/必须不出现的东西？ | 决定是否走「跨平台一致性」的复用方案 |
| `wechat/channels` 且选了横版 | 是否接受在黑边基础上做竖版封面？ | 横版在视频号主页会被裁成 6:7，必须提前决策 |

**已有工程时不要重复问。** 沿用工程内 `BRIEF.md` 与上一版决定，只处理本次变更（与视频线第 1 步同源）。

---

## 7. 答案的落盘契约

选完立刻写入内容目录的 `plan.json`，并同步进 `BRIEF.md`：

```json
{
  "version": 1,
  "selection": {
    "wechat": ["mp-article", "image-text", "channels"],
    "xiaohongshu": ["image-text"]
  },
  "factSource": "wechat/mp-article",
  "order": [
    "wechat/mp-article",
    "wechat/image-text",
    "xiaohongshu/image-text",
    "wechat/channels"
  ],
  "audience": "technical",
  "formOptions": {
    "wechat/mp-article": { "cover": ["2.35:1", "1:1"] },
    "wechat/image-text": { "cardCount": 8, "cover": "auto-generated" },
    "wechat/channels": { "aspect": "9:16", "talent": false, "captions": "burned" },
    "xiaohongshu/image-text": { "noteCount": 8, "cover": "3:4", "topics": 8 }
  }
}
```

- **形式 ID 统一写作 `平台/形式`**（`wechat/image-text`、`xiaohongshu/video`、`generic/product-video`）。
- `selection` 的键是平台 ID，值是该平台下选中的形式 ID（**不带平台前缀**）。
- **后续所有步骤只从 `plan.json` 读形式**，不允许在某一步凭记忆改；确需变更时改 `plan.json` 并在 `BRIEF.md` 记一条变更理由。

### 7.1 写完立刻校验（机器契约）

`plan.json` 不只是给自己看的笔记——写错就是「静默改形式」的源头。写完立刻跑：

```sh
python3 <skill-dir>/scripts/check_social_delivery.py --check-plan <content-dir>/plan.json
# 或：--check-plan 不带路径 + --project <content-dir>，读 <content-dir>/plan.json
```

它只查机器能判定的部分：形式是否已登记、`factSource` 是否在 `selection` 内、`order` 与 `selection` 是否同集合、**事实源是否排在第一位**、**静态形式是否全部在动态形式之前**、`audience` 是否给了。叙事好坏不归脚本管。

退出码 `0` 通过 / `1` 有 error（或 `--strict` 下有 warning）/ `2` 用法问题。**这不是可选项**——与「产出物自检」同一条纪律：能用脚本判的就别靠自觉。

---

## 8. 目录布局（多选时）

一个内容目录下按**平台**分一级、按**形式**分二级，`assets/` 与 `DIRECTION.md` 跨平台共用：

```
<content-dir>/
├── plan.json
├── BRIEF.md
├── DIRECTION.md                  # 跨平台共用；只在画幅/信息密度上分叉
├── assets/                       # 跨平台共用选图与主视觉
├── export/
│   ├── wechat/
│   │   ├── image-text/           # 3:4 图卡 + meta.json + copy.md + cover
│   │   ├── mp-article/           # article.html + meta.json + 封面 900x383 / 500x500
│   │   └── channels/             # final.mp4 + cover-67.jpg + meta.json + copy.md
│   ├── xiaohongshu/
│   │   ├── image-text/           # 3:4 图集 + cover-34.jpg + meta.json + copy.md
│   │   └── video/                # final.mp4 + cover-34.jpg + meta.json + copy.md
│   └── generic/
│       └── product-video/        # final.mp4 + 3:4 / 4:3 / 16:9 封面
└── work/                         # 各形式的可复现工程（渲染脚本、HTML 舞台等）
```

每个 `export/<平台>/<形式>/meta.json` 是**给自检脚本读的字数 / 数量契约**（格式见对应平台文档的「交付清单」）；
少了它，`check_social_delivery.py` 只能查文件级规格，字数项会退化成 warning。

---

## 9. 边界情况

| 情况 | 处理 |
|---|---|
| 用户在同一条消息里已写明平台与形式 | 视为已回答。回一句"按你说的走 X 平台的 Y 形式"再直接执行，不重复提问 |
| 用户只回"都要" | 平台选微信 + 小红书，形式按各平台全选；追问一次受众与是否统一主视觉；并明确告知工作量与交付项清单 |
| 用户只说了平台没说形式 | 只补问第二级，不重问平台 |
| 用户不做选择、只催"快点出" | 说明一次为什么必须先定（骨架不同，返工成本高），并给出默认推荐（`wechat/mp-article` + 任一图文形式）让用户点头，不擅自默认执行 |
| 用户中途要加形式 | 允许，但要检查已产出内容的一致性：新形式若与既有内容口径冲突，先列出冲突点再改 |
| 用户选的形式与素材不匹配（如选了视频形式但没有任何视频素材） | 报告缺口与可选路径（现有截图做动态化 / 只做图文），让用户决定，不自行降级 |
| 用户要的平台尚未安装（如抖音） | 明确说明该平台包尚未安装，给出两条路：只做已支持平台，或先按 [平台接入契约](platform-schema.md) 接入该平台包 |
| 新增平台的扩展（未来） | 只加 `references/platforms/<平台>/` + `assets/platforms/<平台>/` + 规格 JSON 一个 `platforms.<平台>` 节点 + 自检脚本一个检查函数；**不动 core、不动其他平台包、不动视频线** |

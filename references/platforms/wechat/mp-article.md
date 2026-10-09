# 公众号长文（图文消息）

**载体**：公众号「图文消息」。
**交付物**：可直接粘贴进公众号后台的**内联样式 HTML 片段** + 头条封面（2.35:1）+ 次条封面（1:1）+ 标题候选 + 摘要 + 作者 + 发布检查清单。

规格与 HTML 白名单见 [微信官方规格总表](specs.md) 第一节。**动手前先读白名单表**，那是一份"能写什么、不能写什么"的清单，踩了要重排。

---

## 1. 长文与视频/图文的根本差别

长文是唯一**可以承载完整论证链**的载体。所以：

- 视频和图文负责"让人想看"，长文负责"**让人信**"。
- 长文里必须出现**来源、数据、可复现的操作步骤**。图文里因为没有脚注位置而被迫省略的东西，长文要补上。
- 长文是三端的主干：勾选了多项时，**先写长文**，图文与视频号从长文里抽切片（见 [交叉发布](../../core/cross-platform.md)）。

## 2. 步骤

### 2.1 结构与选题

默认骨架（可按内容调整，但必须"开头 300 字内出现具体结论"）：

1. **结论前置**：一句话说清"发布什么 + 对谁有用 + 关键数字"。不要写"随着 AI 时代到来"这类开场。
2. **问题/背景**：为什么做这件事，用户遇到的真实痛点。
3. **正文主体**：2–4 个论点。每个论点 = 结论 + 证据 + 对用户意味着什么。
4. **对比或实测**：before/after、数据表、操作步骤。产品类长文的可信度几乎全在这一段。
5. **怎么用**：可复制的命令 / 步骤 / 链接。
6. **收口**：一句总结 + 引导（关注/留言/内测申请）。

**标题**：≤64 字（官方硬限），但**建议 18–30 字**（列表页不折行更好读）。给 3 条候选：一条信息型、一条结果型、一条问题型。
**摘要**：≤120 字。**必须手写**——不填时系统抓正文前 54 字，那 54 字大概率是套话，等于把列表页的钩子浪费掉。如果实在不写摘要，就把正文最开头 54 字当成钩子来写。
**作者**：≤8 字。

### 2.2 写正文（先 Markdown，后转 HTML）

在 `work/article/draft.md` 写 Markdown 草稿（好改），再转成内联样式的 HTML 片段。**不要直接在 HTML 里写内容**。

### 2.3 转成微信可粘贴的 HTML 片段（最容易翻车的一步）

用 `assets/platforms/wechat/article/article.template.html` 作骨架（它已经是内联样式、无 `class` 依赖、无 `position`）。转换规则：

| 规则 | 错误写法 | 正确写法 |
|---|---|---|
| 样式全内联 | `<style>p{...}</style>` | `<p style="...">` |
| 不用 class 承载样式 | `<p class="lead">` | `<p style="font-size:17px;color:#444">` |
| 不用 position | `style="position:relative"` | 用 `margin`/`padding` 做间距，用 `text-align:center` 做居中 |
| 单位用 px / vw | `margin-top:-100%` | `margin-top:-24px` |
| 标题用保留标签 | `<div class="h2">` | `<h2 style="...">` 或 `<p style="font-size:20px;font-weight:700">` |
| 列表用 ul/ol | 手工 `·` 打头 | `<ul style="..."><li style="...">` |
| 图片走素材库 | `<img src="./x.png">` / base64 | `<img src="__UPLOAD_TO_MP_ASSET_LIBRARY__" style="width:100%">` |
| 音视频 | `<video>` | `<mpvoice>` / `<mpvideo>`（或直接用后台的多媒体入口） |
| 无交互 | `onclick=` / `<iframe>` / `<form>` | 一律不写；需要收集信息就用第三方表单链接或二维码 |

**推荐的基础样式数值**（可直接用，改色改字号即可）：

- 正文：`font-size:16px; line-height:1.8; color:#3f3f3f; letter-spacing:0.3px; margin:0 0 20px;`
- 二级标题：`font-size:20px; font-weight:700; color:#111; line-height:1.4; margin:32px 0 16px;`
- 引用：`border-left:3px solid <主色>; padding:8px 16px; color:#666; margin:20px 0;`
- 代码/命令：`background-color:#f5f5f7; border-radius:6px; padding:12px 16px; font-family:Menlo,Consolas,monospace; font-size:14px;`
- 图片：`<img style="width:100%; border-radius:8px; margin:20px 0; display:block;">`（微信自动 `max-width:100%`）
- 分隔：`<hr style="border:none; border-top:1px solid #eee; margin:28px 0;">`

**字号提醒**：后台工具栏只给三档（小/标准/大），内联 `font-size` 通常保留，但不同机型渲染有差异——**发布前必须走手机预览**。

### 2.4 封面

- **头条封面 2.35:1**：900×383（或同比例更大，如 1080×460）。模板：`assets/platforms/wechat/article/cover-235.template.html`。
- **次条及以上 1:1**：500×500。模板：`assets/platforms/wechat/article/cover-11.template.html`。
- **标题压在封面上的情况**：推送两条及以上时头条标题会叠加在封面图上 → 封面**下半部与中心区域**保持低干扰（纯色/低对比纹理），文字与主体图形上移。
- **转发缩略图**：转发时的链接卡片缩略图只能在封面区域内选取。技巧：在主封面下方再放一块 1:1 方形图，选取缩略图时选这块，就能让转发卡片显示与主封面不同的画面。

### 2.5 自检

```sh
python3 <skill-dir>/scripts/check_social_delivery.py --project <content-dir> --forms wechat/mp-article --strict
```

检查项：
- **禁用项体检**（最关键）：正文片段里是否残留 `<style`、`<script`、外链 CSS、`position:`、`@media`、`@keyframes`、`onclick`、非素材库的 `img src`、base64 图片。
- 标题 ≤64 字、摘要 ≤120 字（且不为空）、作者 ≤8 字。
- 正文字数 ≤50000、正文图片数 ≤500。
- 封面尺寸是否为 2.35:1 与 1:1，单图 ≤10MB，格式在白名单内。

### 2.6 发布步骤（交给用户操作，本 skill 不代操作账号）

1. 公众号后台 → 新建图文消息。
2. 把 `export/wechat/mp-article/article.html` 的内容**整体复制**粘贴进正文编辑器（或先切到「源码」模式粘贴，再切回富文本）。
3. **逐张替换图片**：先在「素材管理」上传正文图片，拿到 `mmbiz.qpic.cn` 地址，再替换模板里的占位符 `src`。
4. 上传封面（头条 2.35:1；若发多条，另做 1:1）。
5. 填标题、摘要、作者。
6. **手机预览**（扫预览二维码）→ 重点看：字号、图片换行、引用块边线、有没有样式丢失。
7. 桌面预览 + 手机预览都过了再群发。

---

## 4. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 粘贴后样式全丢 | 用了 `<style>` 块或 class 承载样式 | 全部改成内联 `style` |
| 部分元素错位/悬浮 | 用了 `position` 或 `%` 位移 | 改标准文档流 + px |
| 图片全裂 | `src` 是本地路径、外链或 base64 | 上传到素材库换成 `mmbiz.qpic.cn` 地址 |
| 字号在手机上偏大/偏小 | 内联字号与机型渲染差异 | 正文基准 15–17px；以手机预览为准微调，不要追求与桌面预览一致 |
| 摘要显示成了正文开头 | 没填摘要，系统抓了前 54 字 | 手写摘要，或把正文开头 54 字写成钩子 |
| 转发卡片图很难看 | 缩略图从主封面里随机取 | 主封面下方放一块 1:1 方形图供选取 |
| 标题被封面盖住 | 发多条时头条标题压在封面上 | 封面下半部保持低干扰 |

## 5. 交付清单

- `export/wechat/mp-article/article.html`：可直接粘贴的正文片段（内联样式、无禁用项）
- `export/wechat/mp-article/cover-235.jpg`、`cover-11.jpg`
- `export/wechat/mp-article/meta.md`：标题候选 3 条 / 摘要 / 作者 / 正文字数 / 图片张数与替换清单
- `export/wechat/mp-article/meta.json`：**自检脚本读它来校验字数与图片数**，必须交付：
  ```json
  {
    "form": "wechat/mp-article",
    "title": "标题（≤64 字，建议 18–30）",
    "digest": "摘要（≤120 字，必须手写）",
    "author": "作者（≤8 字）",
    "bodyChars": 3210,
    "imageCount": 7
  }
  ```
- `export/wechat/mp-article/check.json`：自检实测结果（含禁用项体检明细）
- 一句风险声明：数据主张的出处、未验证项、图片版权来源
- 服务号用户额外可选：`export/wechat/mp-article/api_payload.json`（符合 `add_news` 字段的素材 JSON，**由用户自行提交，本 skill 不调用账号接口**）

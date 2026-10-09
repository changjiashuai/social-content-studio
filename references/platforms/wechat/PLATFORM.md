# 微信平台包（wechat）

**平台 ID**：`wechat`
**形式**：图文消息（小绿书）、公众号长文、视频号视频
**规格单一事实来源**：`scripts/social_specs.json` → `platforms.wechat`

---

## 1. 形式索引

| 形式 ID | 文档 | 形态 | 交付物 |
|---|---|---|---|
| `wechat/image-text` | [image-text.md](image-text.md) | 公众号「图片消息」（小绿书），横滑浏览，3:4 | 3:4 图卡组 + 逐图文案 + 标题 + 封面方案 |
| `wechat/mp-article` | [mp-article.md](mp-article.md) | 公众号「图文消息」（长文） | 内联样式 HTML 片段 + 双封面 + 标题/摘要/作者 |
| `wechat/channels` | [channels.md](channels.md) | 视频号视频 | 成片 + 6:7 封面 + 描述 + 短标题候选 |

人读规格总表见 [specs.md](specs.md)（含 HTML / CSS 白名单与全部来源链接）。

## 2. 平台级共性（三条线都适用）

- **内容体裁**：微信是**订阅关系驱动**——读者是主动关注你的人，所以内容可以比小红书更"实"、更长、更专业。代价是分发靠打开率，标题与摘要的钩子决定生死。
- **中文字体**：不保证加载外部字体，一律系统字体栈；需要特殊字体就做成图。
- **图片必须走素材库**：公众号正文图片的 `src` 必须替换成 `https://mmbiz.qpic.cn/...` 的素材库地址，外链与 Base64 都不显示。模板里统一用占位符 `__UPLOAD_TO_MP_ASSET_LIBRARY__`，交付时明确提示替换。
- **发布即近乎定稿**：公众号已发布内容的修改额度极小（每篇 3 次，标题 3 字 / 正文 120 字 / 图片 3 张），所以**交付前必须自检**，不能"先发出去再改"。
- **外链能力有限**：图片消息（图文）完全不支持外链；公众号正文外链也仅限白名单域名。跨平台导流不要指望微信这一端。

## 3. 平台级红线

| 红线 | 后果 |
|---|---|
| 正文夹带 `<style>` / `<script>` / 外链 CSS / `position` / `@media` / 外链图片 | 粘贴进后台会被清洗，样式全丢 |
| 图片用本地路径 / 外链 / base64 | 正文全部裂图 |
| 摘要留空 | 系统抓正文前 54 字当摘要，通常是套话 |
| 发多条时封面中心区放重要元素 | 头条标题会压在封面上，元素不可读 |
| 横版视频只做 16:9 封面 | 视频号主页会把封面裁成 6:7，信息错位 |

## 4. 与 `core/` 的接口

| 需要什么 | 去哪里 |
|---|---|
| 取材、方向、渲染、编码、自检纪律 | `references/core/pipeline.md` |
| 多平台同做时的口径与素材复用 | `references/core/cross-platform.md` |
| 两级路由与执行顺序 | `references/core/routing.md` |
| 本平台硬参数（机器可读） | `scripts/social_specs.json` → `platforms.wechat` |

## 5. 自检

```sh
SKILL=~/.workbuddy/skills/social-content-studio

# 三条线一起查
python3 $SKILL/scripts/check_social_delivery.py --project <content-dir> \
  --forms wechat/image-text,wechat/mp-article,wechat/channels --strict

# 只查某一条（--form 单数 + --print-specs 可看该形式的规格）
python3 $SKILL/scripts/check_social_delivery.py --print-specs --form wechat/channels
```

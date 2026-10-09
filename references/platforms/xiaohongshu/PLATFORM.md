# 小红书平台包（xiaohongshu）

**平台 ID**：`xiaohongshu`
**形式**：图文笔记、视频笔记
**规格单一事实来源**：`scripts/social_specs.json` → `platforms.xiaohongshu`

> ⚠️ **来源质量提示**：小红书**未公开**像微信开放文档那样的完整素材规格。本包参数主要来自创作服务平台编辑器实际提示与第三方汇总，`social_specs.json` 里相关条目全部标了 `uncertainty`。
> **凡标 `uncertainty` 的都不是确定值**，交付时要写成"以编辑器实际提示为准"，不得编造精确数字。

---

## 1. 形式索引

| 形式 ID | 文档 | 形态 | 交付物 |
|---|---|---|---|
| `xiaohongshu/image-text` | [image-text.md](image-text.md) | 图文笔记，3:4 图集 + 标题 + 正文 + 话题 | 图集 + 封面 + 标题/正文/话题 |
| `xiaohongshu/video` | [video.md](video.md) | 视频笔记，9:16 竖屏 + 3:4 封面 | 成片 + 3:4 封面 + 标题/正文/话题 |

人读规格总表见 [specs.md](specs.md)。

## 2. 平台级共性（两种形式都适用）

- **内容体裁**：小红书是**发现/搜索驱动**的社区，不是订阅关系——笔记发出去先靠首图 + 标题在信息流里抢点击，再靠正文与话题吃搜索长尾。所以**封面和标题的权重远高于微信**，正文反而可以短。
- **首图即封面**：图文笔记的第 1 张就是封面；视频笔记的封面要在编辑页单独设置（**不要用视频首帧**，比例对不上且不好看）。
- **整篇只允许一种比例**：图文笔记内所有图片必须同一比例，否则滑动时跳版。
- **话题标签是主要分发入口**：每条笔记建议 5–15 个话题，从"核心标签 → 场景标签 → 长尾标签"分层。没有话题等于放弃搜索流量。
- **口语化、有个人视角**：小红书不欢迎说明书式文案。用"我实测""踩过的坑"这类第一人称，比"本产品具备…"有效得多。
- **视觉一致性**：同一账号/系列的封面建议统一版式（同色系、同字体位置），让用户在信息流里认出你。

## 3. 平台级红线（比微信严得多）

| 红线 | 说明 |
|---|---|
| **站外导流** | 不得出现微信号 / "vx" / "加我" / 二维码 / 其他平台链接。小红书对此查得很严，轻则限流重则处罚。**跨平台联动时不要设计"关注我微信"这类引导。** |
| **绝对化用语** | "最便宜""绝对有效""100%有效""根治"等涉广告法风险，笔记会被限流。 |
| **搬运与网图** | 系统会用 MD5 与语义识别比对原创度，直接搬运会被判违规。 |
| **其他平台水印 / 白边** | 图片带其他平台水印或白边，既影响观感也触发审核。 |
| **医疗 / 金融效果宣称** | 如"7 天瘦 10 斤"这类效果承诺，属高危违规。 |

> `check_social_delivery.py` 会对 `meta.json` 与 `copy.md` 做**风险词扫描**（导流词、绝对化用语），命中报 WARN —— 因为语境需要人工判断，脚本只负责把可疑处指出来，不代替决策。

## 4. 与 `core/` 的接口

| 需要什么 | 去哪里 |
|---|---|
| 取材、方向、渲染、编码、自检纪律 | `references/core/pipeline.md` |
| 多平台同做时的口径与素材复用 | `references/core/cross-platform.md`（**注意 §4.3：小红书与微信是隔离生态，不要互挂**） |
| 两级路由与执行顺序 | `references/core/routing.md` |
| 本平台硬参数（机器可读） | `scripts/social_specs.json` → `platforms.xiaohongshu` |

## 5. 自检

```sh
SKILL=~/.workbuddy/skills/social-content-studio

# 两种形式一起查
python3 $SKILL/scripts/check_social_delivery.py --project <content-dir> \
  --forms xiaohongshu/image-text,xiaohongshu/video --strict

# 看规格
python3 $SKILL/scripts/check_social_delivery.py --print-specs --form xiaohongshu/image-text
```

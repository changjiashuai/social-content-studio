# 默认样式（`fallback/`）· 来源与授权

**本目录为本 skill 原创，作者 changjiashuai，版权 © 2026。适用本 skill 主协议 GNU AGPL-3.0，不附带任何额外限制。**

`repo` 模式不会复制本目录；`default` / `hybrid` 模式会把它复制进视频工程的 `assets/fallback/`。

---

## 1. 这个目录提供什么

| 文件 | 作用 |
|---|---|
| `tokens.css` | 「纸墨」样式的全部 token 与类：`.film-theme` 双色调变量、纸叠 / 纸面 / 按钮 / 徽标 / 分隔线 / 强调线 |
| `primitives.jsx` | 对应的展示组件：`CardFrame`、`CardSurface`、`FilmButton`、`FilmBadge`、`FilmRule` |
| `preview.png` | 纸白色调的画面示例（1920×1080） |
| `title-preview.png` | 墨黑色调的画面示例（1920×1080） |

设计取向与完整 token 清单写在 `tokens.css` 的文件头。一句话概括：**把宣传画面当一张纸来搭**——可见的纸面用 1px 细线收边，纸面之下叠一层"硬边落影 + 接触影"，大面积一律留给产品自己的界面，强调色只在小面积出现。

### 双色调

| 色调 | 称呼 | 启用方式 |
|---|---|---|
| 浅色 | 纸白 | `.film-theme` 默认（不写 `data-tone`） |
| 深色 | 墨黑 | `.film-theme[data-tone="ink"]`，兼容写法 `data-tone="dark"` |

`CardFrame` / `CardSurface` 也接受 `tone="ink"`，用于在同一帧里局部压深。

---

## 2. 兼容接口（保留这些名字）

以下名字是**对外契约**，为保证既有影片工程继续可用而刻意保留；本目录不因此受到任何第三方许可约束。

- **类名**：`.film-theme`、`.film-card-frame`、`.film-card-surface`、`.film-button`、`.film-badge`、`.film-divider`
- **变量**：`--film-*`（故事与文案分册按名引用 `--film-font-en` / `--film-font-zh`）
- **组件导出**：`CardFrame`、`CardSurface`、`FilmButton`、`FilmBadge`
- **容器级可覆盖项**：`--film-shadow`、`--film-radius`、`--film-font-en`、`--film-font-zh`

新增的名字（`--film-border-strong`、`--film-accent-2`、`--film-focus`、`--film-radius-lg/sm/pill`、`.film-rule`、`FilmRule`、按钮 `ghost` 变体、徽标 `accent` 变体等）是本样式自己的扩展，影片侧按需取用。

---

## 3. 这个目录里没有什么

- 不含任何第三方产品的 Logo、业务页面、界面截图或数据。
- 不含音效或字体文件（一律走系统字体栈，见 `tokens.css` 的字体分工）。
- 不含平台规则：画幅、时长、封面比例等以 `references/platforms/generic/specs.md` 与 `scripts/social_specs.json` 为准。

使用目标产品自己的品牌资源；需要换肤时按 `references/platforms/generic/product-video/repo-and-style.md` 的范围处理，不要覆盖被演示软件的界面样式。

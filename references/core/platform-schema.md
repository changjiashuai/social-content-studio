# 平台接入契约 platform-schema

给 `social-content-studio` **新增一个平台**时必须遵守的契约。
目标：**新增平台不动老代码** —— 不改 `core/` 语义、不改已有平台包、不改视频线章节。

---

## 1. 目录契约

新增平台 `<p>`（例：`bilibili`、`douyin`、`zhihu`）需要创建：

```
references/platforms/<p>/
├── PLATFORM.md          # 平台概览 + 形式索引 + 平台共性与红线
├── specs.md             # 该平台全部硬参数的**人读**总表（每条带来源链接）
├── <form-a>.md          # 每种形式一个文件：流程 + 要点 + 常见问题 + 交付清单
└── <form-b>.md

assets/platforms/<p>/
└── <form>/              # 每种形式的模板资产（可选，纯文案类形式可以没有）
    └── *.template.html
```

## 2. 文件契约

| 文件 | 必须包含 | 不允许 |
|---|---|---|
| `PLATFORM.md` | 平台 ID、形式清单（含形式 ID）、平台级红线、与 `core/` 的接口说明 | 重复写 `core/pipeline.md` 已有的管线内容 |
| `specs.md` | 每个硬参数的值 + **来源**（官方链接优先） | 写没来源的确定值（不确定的必须标 `uncertainty`） |
| `<form>.md` | 形态、流程、要点、常见问题表、**交付清单**（含 `meta.json` 契约）、自检命令 | 复述视频线方法论（只写"复用视频线第 N 步"） |

> **唯一的例外：`generic`。** 产品片的方法论是一整套 7 步流程 + 8 条硬约束 + 28 条本机实测经验，长度远超任何其他形式，写成平台包分册会让"主入口永远是摘要、真实做法藏在二级文件"更严重。因此约定：**当某个形式的方法论属于 core 级长度时，正文留在 `SKILL.md`，平台包只放 `PLATFORM.md` + `specs.md`（索引 + 兜底规格），不复制正文**。
> 这条例外的判据是**长度与复用面**，不是"懒得写"——其他平台的形式一律按上表在平台包内落分册。

## 3. 规格 JSON 节点契约

在 `scripts/social_specs.json` 的 `platforms` 下加一个节点：

```json
"<p>": {
  "label": "平台显示名",
  "sources": ["<p>_official_1", "<p>_help_2"],
  "forms": {
    "<form-a>": {
      "id": "<p>/<form-a>",
      "label": "形式显示名",
      "exportPath": "<p>/<form-a>",
      "…": "该形式的硬参数（尺寸/比例/字数/体积/禁用项）"
    }
  }
}
```

**规则**：

1. `exportPath` 决定产出物落在 `export/<exportPath>/`，自检脚本据此找文件。
2. 每条参数旁边要么有 `source` 键，要么在 `notes` 里注明"实务经验"。**官方口径不一致的写 `uncertainty` 字段，不得当确定值使用。**
3. 平台专属的媒体标准（编码、音量）不要写进平台节点——那属于 `shared`。平台节点只写本平台特有的值。
4. 数值型参数必须机器可判：比例给 `ratioValue` + `ratioTolerance`，字数给 `maxChars`，体积给字节数。

### 3.1 口径不一致的参数怎么写（`uncertainty` + `safeMax`）

**只说「不确定」不够——脚本必须能据此降级判定。** 凡写 `uncertainty`，同时给 `safeMax`：

```json
"noteCount": {
  "min": 1,
  "recommended": [6, 9],
  "max": 18,          // 官方宣称的上限
  "safeMax": 9,       // 稳妥上限（部分入口 / 部分资料的实际上限）
  "uncertainty": "上限口径不一：多数汇总为 18 张，部分来源仍写 9 张。以 App 编辑器实际提示为准。",
  "source": "xhs_third_party"
}
```

判定规则由 `judge_count()` 统一执行，不要在检查函数里手写：

| 实测值 | 结果 |
|---|---|
| `n <= safeMax` | 正常判断（可继续比建议区间） |
| `safeMax < n <= max` | **WARN**，附 `uncertainty` 原文 + 一条 INFO 说明口径不一 |
| `n > max` | 按调用方给的级别（图片数量 ERROR / 话题数量 WARN） |

**为什么强制 `safeMax`**：没有它，`uncertainty` 就只是注释。`tests/` 里有一项守着「凡带 uncertainty 又有 max 的节点必须有 safeMax」，漏写会直接让回归失败。

## 4. 检查函数契约

在 `scripts/check_social_delivery.py` 里新增一个函数并登记：

```python
def check_<p>_<form>(specs: dict, platform: str, form_key: str, export_root: str, rep: Report):
    """<p>/<form-a> 的产出物检查。"""
    spec = specs["platforms"][platform]["forms"][form_key]
    d = os.path.join(export_root, spec["exportPath"])
    if not os.path.isdir(d):
        rep.add(spec["id"], "目录", ERROR, f"缺少产出目录 {d}")
        return
    # … 复用 §通用检查 里的 check_image / check_chars / probe_video / read_meta
```

登记进 `FORM_CHECKS`：

```python
FORM_CHECKS = {
    "wechat/image-text": check_wechat_image_text,
    "wechat/mp-article": check_wechat_mp_article,
    "wechat/channels": check_wechat_channels,
    "xiaohongshu/image-text": check_xhs_image_text,
    "xiaohongshu/video": check_xhs_video,
    "generic/product-video": check_generic_product_video,
}
```

**必须复用**已经写好的通用检查函数（`check_image` / `check_chars` / `probe_video` / `read_meta` / `human_bytes`），不要另写一套尺寸解析或字数判断。

## 5. 路由登记

在 `references/core/routing.md` 第二级表格加该平台的形式行，并在 `SKILL.md` 的平台/形式表加一行。
多选时的执行顺序由 `core/routing.md` §5 的拓扑规则自动决定，**不需要为每个平台单独写顺序**——只要正确标注它属于"静态形式"还是"动态形式"。

## 6. 验收（新增平台后必须过的 4 项）

```sh
SKILL=~/.workbuddy/skills/social-content-studio

# ① 模板画布尺寸与规格表一致（若该平台有 HTML 模板）
node $SKILL/scripts/render_social_assets.mjs --probe $SKILL/assets/platforms

# ② 该平台的形式能被列出且规格可打印
python3 $SKILL/scripts/check_social_delivery.py --print-specs --form <p>/<form-a>

# ③ 回归测试全绿（含新增平台的用例）
python3 -m unittest discover -s $SKILL/tests

# ④ 在既有平台上跑一次自检，确认没有回归
python3 $SKILL/scripts/check_social_delivery.py --project <既有内容目录> --strict
```

## 7. 反模式（不要这样做）

| 反模式 | 为什么不行 |
|---|---|
| 把平台规格写进 `SKILL.md` 正文 | 平台规则会变，写进正文等于又多一个漂移点；规格只有一个事实来源 |
| 在检查函数里硬编码尺寸/字数 | 同上，必须从 `social_specs.json` 读 |
| 为新平台改 `core/routing.md` §5 的顺序表 | 顺序是拓扑规则推导出来的，改它说明你的形式分类没标对 |
| 复制一份 `check_social_delivery.py` 改 | 直接扩展 `FORM_CHECKS`，不要分叉维护 |
| 为新平台新建一套渲染脚本 | 复用 `render_social_assets.mjs`，新平台只是多一份 HTML 模板 + manifest 条目 |

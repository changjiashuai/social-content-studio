#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_social_delivery.py — 全平台多形式产出物自检

把 scripts/social_specs.json 当作唯一事实来源，逐项核对产出物的
尺寸 / 比例 / 文件大小 / 字数 / 平台禁用项，并把每项实测值打出来。

用法：
  # 列出全部平台与形式（含产出目录）
  python3 check_social_delivery.py --list

  # 查某个形式的规格
  python3 check_social_delivery.py --print-specs --form xiaohongshu/image-text

  # 自检（--project 可以是内容目录，也可以是 export 目录本身）
  python3 check_social_delivery.py --project <content-dir> \
      --forms wechat/mp-article,xiaohongshu/image-text --strict

  # 不给 --forms 时，自动发现 export/ 下已存在的形式并全部检查

退出码：0 = 通过；1 = 有 error（或 --strict 下有 warning）；2 = 用法 / 规格文件问题。

约定：各形式的字数类元数据放在 export/<平台>/<形式>/meta.json，
缺省则只查文件级规格并给出 warning。格式见各平台文档的「交付清单」。

新增平台：在 FORM_CHECKS 里登记一个 `平台/形式 -> 检查函数` 即可，
其余（规格读取、报告渲染、自动发现）都是通用的。见 references/core/platform-schema.md。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS_PATH = os.path.join(HERE, "social_specs.json")

ERROR, WARN, INFO, OK = "error", "warn", "info", "ok"
LEVEL_ORDER = {OK: 0, INFO: 1, WARN: 2, ERROR: 3}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v"}


# ---------------------------------------------------------------- 基础设施

@dataclass
class Finding:
    channel: str
    item: str
    level: str
    message: str
    actual: Any = None
    expected: Any = None


@dataclass
class Report:
    findings: list = field(default_factory=list)
    checked_files: int = 0
    skipped: list = field(default_factory=list)

    def add(self, channel, item, level, message, actual=None, expected=None):
        self.findings.append(Finding(channel, item, level, message, actual, expected))

    @property
    def worst(self):
        return max((LEVEL_ORDER[f.level] for f in self.findings), default=0)

    def counts(self):
        c = {ERROR: 0, WARN: 0, INFO: 0, OK: 0}
        for f in self.findings:
            c[f.level] += 1
        return c


def load_specs() -> dict:
    with open(SPECS_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def form_index(specs: dict) -> dict:
    """返回 {form_id: (platform, form_key, spec)}，顺序即 specs.json 里的书写顺序。"""
    idx = {}
    for pkey, plat in specs["platforms"].items():
        for fkey, fspec in plat["forms"].items():
            fid = fspec.get("id") or f"{pkey}/{fkey}"
            idx[fid] = (pkey, fkey, fspec)
    return idx


def form_spec(specs: dict, fid: str) -> dict:
    idx = form_index(specs)
    if fid not in idx:
        raise KeyError(fid)
    return idx[fid][2]


def human_bytes(n: int | float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{int(n)}B"
        n /= 1024.0
    return f"{n:.1f}GB"


def human_duration(sec: float) -> str:
    m, s = divmod(int(round(sec)), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    return f"{m}m{s:02d}s"


# ------------------------------------------------------- 纯标准库图片尺寸解析

def read_image_size(path: str) -> tuple[int, int] | None:
    """不依赖 Pillow：从文件头解析 jpg/jpeg/png/gif/bmp/webp 的像素宽高。"""
    try:
        with open(path, "rb") as fh:
            head = fh.read(32)
            if len(head) < 10:
                return None

            # PNG
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", head[16:24])
                return int(w), int(h)

            # GIF
            if head[:6] in (b"GIF87a", b"GIF89a"):
                w, h = struct.unpack("<HH", head[6:10])
                return int(w), int(h)

            # BMP
            if head[:2] == b"BM":
                w, h = struct.unpack("<ii", head[18:26])
                return abs(int(w)), abs(int(h))

            # WEBP
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                chunk = head[12:16]
                if chunk == b"VP8X":
                    fh.seek(24)
                    b = fh.read(6)
                    if len(b) == 6:
                        w = int.from_bytes(b[0:3], "little") + 1
                        h = int.from_bytes(b[3:6], "little") + 1
                        return w, h
                if chunk == b"VP8 ":
                    fh.seek(26)
                    b = fh.read(4)
                    if len(b) == 4:
                        w = int.from_bytes(b[0:2], "little") & 0x3FFF
                        h = int.from_bytes(b[2:4], "little") & 0x3FFF
                        return w, h
                if chunk == b"VP8L":
                    fh.seek(21)
                    b = fh.read(4)
                    if len(b) == 4:
                        bits = int.from_bytes(b, "little")
                        w = (bits & 0x3FFF) + 1
                        h = ((bits >> 14) & 0x3FFF) + 1
                        return w, h
                return None

            # JPEG：扫 SOF 段
            if head[:2] == b"\xff\xd8":
                fh.seek(2)
                while True:
                    byte = fh.read(1)
                    if not byte:
                        return None
                    if byte != b"\xff":
                        continue
                    marker = fh.read(1)
                    while marker == b"\xff":
                        marker = fh.read(1)
                    if not marker:
                        return None
                    m = marker[0]
                    if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
                        continue
                    seg_len_raw = fh.read(2)
                    if len(seg_len_raw) < 2:
                        return None
                    seg_len = struct.unpack(">H", seg_len_raw)[0]
                    if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                        body = fh.read(5)
                        if len(body) < 5:
                            return None
                        h, w = struct.unpack(">HH", body[1:5])
                        return int(w), int(h)
                    fh.seek(seg_len - 2, os.SEEK_CUR)
    except OSError:
        return None
    return None


def count_gif_frames(path: str) -> tuple[int | None, str]:
    """统计 GIF 帧数。优先 Pillow，否则退化为 GCE 块计数（启发式）。"""
    try:
        from PIL import Image  # type: ignore
        with Image.open(path) as im:
            return int(getattr(im, "n_frames", 1)), "pillow"
    except Exception:
        pass
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        if data[:6] not in (b"GIF87a", b"GIF89a"):
            return None, "not-gif"
        return len(re.findall(b"\x21\xf9\x04", data)), "heuristic"
    except OSError:
        return None, "unreadable"


def read_image_palette_colors(path: str) -> int | None:
    """GIF 调色板位数（用于提示颜色数）。非 GIF 返回 None。"""
    try:
        with open(path, "rb") as fh:
            head = fh.read(11)
        if head[:6] not in (b"GIF87a", b"GIF89a"):
            return None
        packed = head[10]
        if not (packed & 0x80):
            return 2
        return 2 ** ((packed & 0x07) + 1)
    except OSError:
        return None


# ------------------------------------------------------------- 视频探测

def ffprobe_available() -> bool:
    return shutil.which("ffprobe") is not None


def probe_video(path: str) -> dict | None:
    if not ffprobe_available():
        return None
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=60, check=True).stdout
        data = json.loads(out.decode("utf-8", "replace"))
    except Exception:
        return None
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})
    if not v:
        return None
    nb = v.get("nb_frames")
    dur = fmt.get("duration") or v.get("duration")
    bits = fmt.get("bit_rate")
    info = {
        "width": int(v.get("width") or 0),
        "height": int(v.get("height") or 0),
        "codec": (v.get("codec_name") or "").lower(),
        "duration": float(dur) if dur else 0.0,
        "bitrate": int(bits) if bits else 0,
        "pix_fmt": v.get("pix_fmt"),
        "fps": _parse_fps(v.get("r_frame_rate") or v.get("avg_frame_rate")),
        "has_audio": a is not None,
        "audio_codec": (a or {}).get("codec_name", "").lower(),
        "size": int(fmt.get("size") or os.path.getsize(path)),
        "nb_frames": int(nb) if nb and str(nb).isdigit() else None,
    }
    return info


def _parse_fps(expr: str | None) -> float | None:
    if not expr or "/" not in str(expr):
        return None
    try:
        num, den = str(expr).split("/")
        den = float(den)
        return round(float(num) / den, 2) if den else None
    except (ValueError, ZeroDivisionError):
        return None


# ------------------------------------------------------------- 通用检查

def check_image(path: str, spec_ratio: dict, ch: str, item: str, rep: Report,
                max_bytes: int, formats: list[str], allow_gif: bool = True,
                max_gif_frames: int = 300):
    name = os.path.basename(path)
    size = os.path.getsize(path)
    rep.checked_files += 1

    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if formats and ext not in formats:
        rep.add(ch, item, ERROR, f"{name} 格式不在白名单内（{ext}）", ext, formats)
    if size > max_bytes:
        rep.add(ch, item, ERROR, f"{name} 体积超标", human_bytes(size), f"≤{human_bytes(max_bytes)}")
    else:
        rep.add(ch, item, OK, f"{name} 体积 {human_bytes(size)}")

    wh = read_image_size(path)
    if not wh:
        rep.add(ch, item, WARN, f"{name} 无法解析像素尺寸（格式或文件损坏）")
        return None
    w, h = wh
    ratio = w / h if h else 0
    target = spec_ratio.get("ratioValue")
    tol = spec_ratio.get("ratioTolerance", 0.02)
    label = spec_ratio.get("ratio", "?")
    if target:
        dev = abs(ratio - target)
        if dev > tol * 2.5:
            rep.add(ch, item, ERROR,
                    f"{name} 比例偏离：实测 {w}x{h} = {ratio:.3f}，目标 {label}",
                    f"{w}x{h} ({ratio:.3f})", f"{label} (±{tol})")
        elif dev > tol:
            rep.add(ch, item, WARN,
                    f"{name} 比例略有偏差：{w}x{h} = {ratio:.3f}",
                    f"{w}x{h}", f"{label}")
        else:
            rep.add(ch, item, OK, f"{name} {w}x{h} 比例符合 {label}")

        # 与推荐像素尺寸的差异提示
        exp_w, exp_h = spec_ratio.get("width"), spec_ratio.get("height")
        if exp_w and exp_h and (w, h) != (exp_w, exp_h):
            if abs(w / exp_w - h / exp_h) < 0.02:
                rep.add(ch, item, INFO,
                        f"{name} 用等比例尺寸 {w}x{h}（模板推荐 {exp_w}x{exp_h}），像素量偏小可能发虚")
        # 平台给了最小分辨率时一并提示
        min_res = spec_ratio.get("minResolution")
        if min_res and (w < min_res.get("width", 0) or h < min_res.get("height", 0)):
            rep.add(ch, item, WARN,
                    f"{name} {w}x{h} 低于建议最小分辨率 "
                    f"{min_res.get('width')}x{min_res.get('height')}，信息流里会发虚",
                    f"{w}x{h}", f"≥{min_res.get('width')}x{min_res.get('height')}")
    else:
        rep.add(ch, item, INFO, f"{name} {w}x{h}")

    if ext == "gif":
        if not allow_gif:
            rep.add(ch, item, ERROR, f"{name} GIF 在该渠道不支持")
        frames, how = count_gif_frames(path)
        if frames is None:
            rep.add(ch, item, WARN, f"{name} 无法统计动图帧数")
        else:
            if frames > max_gif_frames:
                rep.add(ch, item, ERROR, f"{name} 动图帧数超标", frames, f"≤{max_gif_frames}")
            else:
                rep.add(ch, item, OK, f"{name} 动图 {frames} 帧（统计方式：{how}）")
            if w > 640:
                rep.add(ch, item, INFO, f"{name} 宽 {w}px 超过 GIF 建议宽度 640px")
            colors = read_image_palette_colors(path)
            if colors:
                rep.add(ch, item, INFO, f"{name} 调色板 {colors} 色")
    return w, h


def check_chars(rep: Report, ch: str, item: str, value, max_chars: int,
                label: str, min_soft: int | None = None):
    if value is None:
        rep.add(ch, item, WARN, f"缺少 {label}，跳过字数检查")
        return
    n = len(str(value))
    if n > max_chars:
        rep.add(ch, item, ERROR, f"{label} 超限：{n} 字", n, f"≤{max_chars} 字")
    else:
        rep.add(ch, item, OK, f"{label} {n} 字（上限 {max_chars}）")
    if min_soft and n < min_soft:
        rep.add(ch, item, WARN, f"{label} 仅 {n} 字，建议 ≥{min_soft} 字以便列表页不被折行 / 空洞", n, min_soft)


def check_body_chars(rep: Report, ch: str, item: str, meta: dict, max_chars: int,
                     label: str, min_soft: int | None = None):
    """正文字数检查：优先读 meta.body（文本，取其长度），否则读 meta.bodyChars（本身已是字数）。"""
    text = meta.get("body")
    if isinstance(text, str) and text.strip():
        n = len(text)
    else:
        raw = meta.get("bodyChars")
        if raw is None:
            rep.add(ch, item, WARN, f"缺少 body / bodyChars，{label}未校验")
            return
        try:
            n = int(raw)
        except (TypeError, ValueError):
            rep.add(ch, item, WARN, f"{label}字段无法解析（{raw!r}）")
            return
    if n > max_chars:
        rep.add(ch, item, ERROR, f"{label} 超限：{n} 字", n, f"≤{max_chars} 字")
    else:
        rep.add(ch, item, OK, f"{label} {n} 字（上限 {max_chars}）")
    if min_soft and n < min_soft:
        rep.add(ch, item, WARN, f"{label} 仅 {n} 字，建议 ≥{min_soft} 字", n, min_soft)


def check_banned_text(text: str, spec: dict, ch: str, item: str, rep: Report,
                      source_name: str = "文案"):
    """扫描平台风险词（bannedContent）。返回命中条数。默认 WARN —— 语境误伤要人工判断。"""
    hits = 0
    for rule in spec.get("bannedContent", []):
        try:
            pattern = re.compile(rule["pattern"], flags=re.IGNORECASE)
        except re.error:
            continue
        for m in pattern.finditer(text):
            hits += 1
            line = text.count("\n", 0, m.start()) + 1
            snippet = text[max(0, m.start() - 20): m.start() + 40].replace("\n", " ")
            rep.add(ch, item, WARN,
                    f"{source_name}:{line} 命中平台风险词 `{m.group(0)}` —— {rule.get('why', '')}",
                    snippet)
    if hits == 0 and spec.get("bannedContent"):
        rep.add(ch, item, OK, f"{source_name} 未命中平台风险词（{len(spec['bannedContent'])} 条规则）")
    return hits


def read_meta(export_dir: str) -> dict | None:
    p = os.path.join(export_dir, "meta.json")
    if not os.path.isfile(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        return {"__error__": str(exc)}


def list_images(d: str, exclude_prefixes=("cover",)) -> list[str]:
    if not os.path.isdir(d):
        return []
    out = []
    for n in sorted(os.listdir(d)):
        if n.startswith("."):
            continue
        if any(n.lower().startswith(p) for p in exclude_prefixes):
            continue
        if os.path.splitext(n)[1].lower() in IMAGE_EXTS:
            out.append(os.path.join(d, n))
    return out


def list_files_with_prefix(d: str, prefix: str) -> list[str]:
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, n) for n in sorted(os.listdir(d))
            if n.lower().startswith(prefix.lower())
            and os.path.splitext(n)[1].lower() in IMAGE_EXTS]


def list_videos(d: str) -> list[str]:
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, n) for n in sorted(os.listdir(d))
            if os.path.splitext(n)[1].lower() in VIDEO_EXTS]


def collect_banned_texts(export_dir: str, meta: dict | None) -> list[tuple[str, str]]:
    """收集需要做风险词扫描的文本：(来源名, 内容)。"""
    texts = []
    if isinstance(meta, dict):
        for key, label in (("title", "meta.title"), ("body", "meta.body"),
                           ("description", "meta.description")):
            v = meta.get(key)
            if isinstance(v, str) and v.strip():
                texts.append((label, v))
        if isinstance(meta.get("topics"), list):
            texts.append(("meta.topics", " ".join(str(t) for t in meta["topics"])))
    cp = os.path.join(export_dir, "copy.md")
    if os.path.isfile(cp):
        try:
            with open(cp, "r", encoding="utf-8", errors="replace") as fh:
                texts.append(("copy.md", fh.read()))
        except OSError:
            pass
    return texts


# ------------------------------------------------------------- 微信三线

def check_wechat_image_text(specs: dict, export_root: str, rep: Report):
    spec = form_spec(specs, "wechat/image-text")
    ch = spec["id"]
    d = os.path.join(export_root, spec["exportPath"])
    if not os.path.isdir(d):
        rep.add(ch, "目录", ERROR, f"缺少产出目录 {d}")
        return

    cards = list_images(d)
    n = len(cards)
    if n == 0:
        rep.add(ch, "图片组", ERROR, "没有找到任何图卡（非 cover 前缀的图片）")
        return

    cnt = spec["cardCount"]
    if n > cnt["maxSubscriptionHelper"]:
        rep.add(ch, "图片数量", ERROR, f"共 {n} 张，超过官方上限 {cnt['maxSubscriptionHelper']} 张", n, cnt["maxSubscriptionHelper"])
    elif n > cnt["maxMobile"]:
        rep.add(ch, "图片数量", WARN,
                f"共 {n} 张：订阅号助手端上限 {cnt['maxSubscriptionHelper']} 张，但部分入口为 {cnt['maxMobile']} 张",
                n, f"≤{cnt['maxMobile']}（稳妥口径）")
    lo, hi = cnt["recommended"]
    if not (lo <= n <= hi):
        rep.add(ch, "图片数量", WARN, f"共 {n} 张，建议 {lo}–{hi} 张", n, f"{lo}–{hi}")
    else:
        rep.add(ch, "图片数量", OK, f"共 {n} 张，落在建议区间 {lo}–{hi}")

    if n >= 3:
        rep.add(ch, "列表缩略图", WARN,
                "≥3 张时列表显示前 3 张并裁成 2.35:1 —— 请人工确认前 3 张的关键信息落在中心安全区")
    else:
        rep.add(ch, "列表缩略图", WARN,
                f"{n} 张时列表用首图裁成 16:9 —— 请人工确认首图中心安全区可读")

    for p in cards:
        check_image(p, spec["card"], ch, "图卡", rep,
                    max_bytes=spec["card"]["maxBytes"], formats=spec["card"]["formats"],
                    max_gif_frames=spec["animated"]["maxFrames"])

    meta = read_meta(d)
    if meta is None:
        rep.add(ch, "meta.json", WARN, "缺少 meta.json，标题与逐图文案的字数未校验（见 references/platforms/wechat/image-text.md 交付清单）")
    elif "__error__" in meta:
        rep.add(ch, "meta.json", ERROR, f"meta.json 解析失败：{meta['__error__']}")
    else:
        title = meta.get("title")
        check_chars(rep, ch, "标题", title, spec["title"]["maxChars"], "标题")
        texts = meta.get("cardTexts") or []
        if not texts:
            rep.add(ch, "逐图文案", WARN, "meta.json 缺 cardTexts，逐图文案未校验")
        for i, t in enumerate(texts, 1):
            s = str(t)
            if len(s) > spec["perCardText"]["officialMaxChars"]:
                rep.add(ch, "逐图文案", ERROR,
                        f"第 {i} 张图文字 {len(s)} 字，超过官方上限 {spec['perCardText']['officialMaxChars']}",
                        len(s), spec["perCardText"]["officialMaxChars"])
            elif len(s) > spec["perCardText"]["recommendedMaxChars"]:
                rep.add(ch, "逐图文案", WARN,
                        f"第 {i} 张图文字 {len(s)} 字，建议 ≤{spec['perCardText']['recommendedMaxChars']} 字（超过就拆张）",
                        len(s), spec["perCardText"]["recommendedMaxChars"])
            else:
                rep.add(ch, "逐图文案", OK, f"第 {i} 张图 {len(s)} 字")


def check_wechat_mp_article(specs: dict, export_root: str, rep: Report):
    spec = form_spec(specs, "wechat/mp-article")
    ch = spec["id"]
    d = os.path.join(export_root, spec["exportPath"])
    if not os.path.isdir(d):
        rep.add(ch, "目录", ERROR, f"缺少产出目录 {d}")
        return

    # ---- 正文片段：禁用项体检（最关键）
    html_paths = [os.path.join(d, n) for n in sorted(os.listdir(d))
                  if n.lower().endswith((".html", ".htm"))]
    if not html_paths:
        rep.add(ch, "正文片段", ERROR, "找不到正文片段 html（交付物必须是可直接粘贴的 HTML 片段）")
    for hp in html_paths:
        rep.checked_files += 1
        name = os.path.basename(hp)
        try:
            with open(hp, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            rep.add(ch, "正文片段", ERROR, f"{name} 读取失败：{exc}")
            continue

        hits = []
        for rule in spec["htmlWhitelist"]["bannedPatterns"]:
            for m in re.finditer(rule["pattern"], text, flags=re.IGNORECASE):
                line = text.count("\n", 0, m.start()) + 1
                snippet = text[max(0, m.start() - 20): m.start() + 40].replace("\n", " ")
                hits.append((rule["pattern"], rule["why"], line, snippet))
        if hits:
            for pat, why, line, snippet in hits:
                pretty = pat.replace("\\s*", " ").replace("\\", "")
                rep.add(ch, "禁用项", ERROR, f"{name}:{line} 命中 `{pretty}` —— {why}", snippet)
        else:
            rep.add(ch, "禁用项", OK, f"{name} 未命中任何平台禁用项")

        # 内联样式覆盖率提示
        tags = re.findall(r"<(p|section|span|div|h[1-6]|li|blockquote)\b[^>]*>", text, flags=re.IGNORECASE)
        styled = re.findall(r"<(p|section|span|div|h[1-6]|li|blockquote)\b[^>]*style\s*=", text, flags=re.IGNORECASE)
        if tags:
            cov = len(styled) / len(tags)
            msg = f"{name} 内联样式覆盖 {len(styled)}/{len(tags)} 个块级标签（{cov:.0%}）"
            rep.add(ch, "内联样式", WARN if cov < 0.8 else OK, msg)

        # 图片 src 是否走素材库
        srcs = re.findall(r"<img[^>]*\bsrc\s*=\s*[\"']([^\"']*)[\"']", text, flags=re.IGNORECASE)
        bad = [s for s in srcs if "qpic.cn" not in s and "__UPLOAD" not in s.upper() and not s.startswith("RESERVED")]
        if bad:
            for s in bad[:20]:
                rep.add(ch, "图片 src", ERROR,
                        "正文图片未使用微信素材库地址，粘贴后台会裂图", s[:80], "https://mmbiz.qpic.cn/...")
        elif srcs:
            rep.add(ch, "图片 src", OK, f"{len(srcs)} 处图片均为素材库地址或占位符（交付时需替换占位符）")
        if "class=" in text.lower():
            rep.add(ch, "class 属性", INFO, "片段里仍用 class —— 微信保留 class 但不应用样式，确认样式也写在内联 style 里")

    # ---- meta.json 字数
    meta = read_meta(d)
    if meta is None:
        rep.add(ch, "meta.json", WARN, "缺少 meta.json，标题 / 摘要 / 作者 / 正文与图片数未校验（见 references/platforms/wechat/mp-article.md 交付清单）")
    elif "__error__" in meta:
        rep.add(ch, "meta.json", ERROR, f"meta.json 解析失败：{meta['__error__']}")
    else:
        check_chars(rep, ch, "标题", meta.get("title"), spec["title"]["maxChars"], "标题",
                    min_soft=spec["title"]["recommended"][0])
        n = len(str(meta.get("title") or ""))
        if 0 < n < 18:
            rep.add(ch, "标题", WARN, f"标题仅 {n} 字，建议 18–30 字", n, "18–30")
        check_chars(rep, ch, "摘要", meta.get("digest"), spec["digest"]["maxChars"], "摘要")
        if meta.get("digest") in (None, ""):
            rep.add(ch, "摘要", WARN,
                    f"摘要为空 —— 系统会抓正文前 {spec['digest']['autoFallbackChars']} 字，必须手写摘要或把开头写成钩子")
        check_chars(rep, ch, "作者", meta.get("author"), spec["author"]["maxChars"], "作者")
        bc = meta.get("bodyChars")
        if bc is None:
            rep.add(ch, "正文字数", WARN, "meta.json 缺 bodyChars，正文字数未校验")
        elif int(bc) > spec["body"]["maxChars"]:
            rep.add(ch, "正文字数", ERROR, f"正文 {bc} 字超限", bc, spec["body"]["maxChars"])
        else:
            rep.add(ch, "正文字数", OK, f"正文 {bc} 字（上限 {spec['body']['maxChars']}）")
        ic = meta.get("imageCount")
        if ic is not None and int(ic) > spec["bodyImageCount"]["max"]:
            rep.add(ch, "正文图片数", ERROR, f"正文图片 {ic} 张超限", ic, spec["bodyImageCount"]["max"])
        elif ic is not None:
            rep.add(ch, "正文图片数", OK, f"正文图片 {ic} 张（上限 {spec['bodyImageCount']['max']}）")

    # ---- 封面
    cover = spec["cover"]
    pairs = [
        ("cover-235", cover["headline"], "头条封面"),
        ("cover-11", cover["secondary"], "次条封面"),
    ]
    for prefix, cs, label in pairs:
        found = list_files_with_prefix(d, prefix)
        if not found:
            rep.add(ch, label, WARN, f"没找到 {prefix}.* 封面（{cs['ratio']}，推荐 {cs['width']}x{cs['height']}）")
            continue
        for n in found:
            check_image(n, cs, ch, label, rep,
                        max_bytes=spec["image"]["maxBytes"], formats=spec["image"]["formats"])

    rep.add(ch, "封面标题区", WARN,
            "发多条时头条标题会压在封面图上 —— 请人工确认封面下半部与中心区低干扰")


def check_wechat_channels(specs: dict, export_root: str, rep: Report):
    spec = form_spec(specs, "wechat/channels")
    ch = spec["id"]
    d = os.path.join(export_root, spec["exportPath"])
    if not os.path.isdir(d):
        rep.add(ch, "目录", ERROR, f"缺少产出目录 {d}")
        return

    vids = list_videos(d)
    vspec = spec["video"]
    if not vids:
        rep.add(ch, "成品视频", ERROR, "找不到成品视频（mp4/mov/m4v）")
    if not ffprobe_available():
        rep.add(ch, "成品视频", WARN, "本机没有 ffprobe，跳过时长 / 编码 / 码率 / 分辨率检查")
        rep.skipped.append(f"{ch}: video probe (ffprobe missing)")
    for vp in vids:
        rep.checked_files += 1
        name = os.path.basename(vp)
        info = probe_video(vp) if ffprobe_available() else None
        if not info:
            rep.add(ch, "成品视频", WARN, f"{name} 无法探测媒体信息")
            continue
        size = info["size"]
        if size > vspec["maxBytesMobile"]:
            rep.add(ch, "视频体积", ERROR, f"{name} {human_bytes(size)} 超过手机端上限",
                    human_bytes(size), f"≤{human_bytes(vspec['maxBytesMobile'])}")
        else:
            rep.add(ch, "视频体积", OK, f"{name} {human_bytes(size)}（手机端上限 {human_bytes(vspec['maxBytesMobile'])}）")

        dur = info["duration"]
        if dur < vspec["durationSeconds"]["min"]:
            rep.add(ch, "时长", ERROR, f"{name} 仅 {dur:.1f}s，低于最短 {vspec['durationSeconds']['min']}s")
        elif dur > vspec["durationSeconds"]["maxMobile"]:
            rep.add(ch, "时长", ERROR, f"{name} {human_duration(dur)} 超过手机端上限",
                    human_duration(dur), human_duration(vspec["durationSeconds"]["maxMobile"]))
        else:
            rep.add(ch, "时长", OK, f"{name} {human_duration(dur)}")
        if dur > 90 and dur <= vspec["durationSeconds"]["maxMobile"]:
            rep.add(ch, "时长", INFO, f"{name} {human_duration(dur)} 较长：完播率通常在 60–90s 后明显下降（经验值，非官方红线）")

        _check_aspect_and_resolution(info, vspec, ch, name, rep)

        codec = info["codec"]
        if codec not in vspec["codecs"]:
            rep.add(ch, "编码", WARN, f"{name} 编码 {codec or '未知'} 不在 H.264/H.265 内", codec, vspec["codecs"])
        elif codec == "hevc":
            rep.add(ch, "编码", WARN,
                    f"{name} 为 H.265(HEVC)：Windows 的 Chrome/Edge 不能播放，建议改导 H.264 或提示用户用 Mac Safari 上传",
                    codec, "h264")
        else:
            rep.add(ch, "编码", OK, f"{name} 编码 {codec}")

        br = info["bitrate"]
        if br:
            if br < vspec["recommendedBitrateBps"]:
                rep.add(ch, "码率", WARN, f"{name} 码率 {br / 1e6:.1f}Mbps 低于建议的 ≥{vspec['recommendedBitrateBps'] / 1e6:.0f}Mbps",
                        f"{br / 1e6:.1f}Mbps", "≥10Mbps")
            else:
                rep.add(ch, "码率", OK, f"{name} 码率 {br / 1e6:.1f}Mbps")
        if info["pix_fmt"] and info["pix_fmt"] != "yuv420p":
            rep.add(ch, "像素格式", WARN, f"{name} pix_fmt={info['pix_fmt']}，建议 yuv420p 以保证全平台可播",
                    info["pix_fmt"], "yuv420p")
        if not info["has_audio"]:
            rep.add(ch, "音轨", WARN, f"{name} 没有音频轨")

    # 封面
    cv = spec["cover"]
    for prefix, cs, label in [
        ("cover-67", cv["vertical"], "竖版封面"),
        ("cover-169", cv["horizontal"], "横版封面"),
    ]:
        found = list_files_with_prefix(d, prefix)
        if not found:
            rep.add(ch, label, WARN if prefix == "cover-169" else ERROR,
                    f"没找到 {prefix}.* 封面（{cs['ratio']}，推荐 {cs['width']}x{cs['height']}）")
            continue
        for n in found:
            check_image(n, cs, ch, label, rep, max_bytes=10 * 1024 * 1024,
                        formats=["jpg", "jpeg", "png", "bmp", "gif", "webp"])
    rep.add(ch, "封面裁切", WARN, "横版视频在主页列表会被裁成 6:7 —— 请人工确认关键信息在 6:7 中心安全区")
    rep.add(ch, "首帧", WARN, "第 1 帧即默认封面，必须是完整画面（沿用视频线 check_delivery.py 的前 5 帧检测）")

    meta = read_meta(d)
    if meta is None:
        rep.add(ch, "meta.json", WARN, "缺少 meta.json，描述与短标题字数未校验（见 references/platforms/wechat/channels.md 交付清单）")
    elif "__error__" in meta:
        rep.add(ch, "meta.json", ERROR, f"meta.json 解析失败：{meta['__error__']}")
    else:
        check_chars(rep, ch, "描述", meta.get("description"), spec["description"]["maxChars"], "描述")
        sts = meta.get("shortTitles") or []
        if not sts:
            rep.add(ch, "短标题", WARN, "meta.json 缺 shortTitles —— 短标题会进搜索场景，必须单独打磨")
        for i, s in enumerate(sts, 1):
            check_chars(rep, ch, "短标题", s, spec["shortTitle"]["maxChars"], f"短标题候选 {i}")


def _check_aspect_and_resolution(info: dict, vspec: dict, ch: str, name: str, rep: Report):
    """宽高比落在区间内 + 是否接近推荐比例 + 短边分辨率（1080p 口径按短边判）。"""
    w, h = info["width"], info["height"]
    ratio = w / h if h else 0
    lo, hi = vspec["aspectRange"]
    if not (lo <= ratio <= hi):
        rep.add(ch, "宽高比", ERROR, f"{name} {w}x{h} 宽高比 {ratio:.3f} 超出官方区间 {lo}~{hi}",
                f"{w}x{h}", f"{lo}~{hi}")
    else:
        near = min(
            [(abs(ratio - (9 / 16)), "9:16"), (abs(ratio - (16 / 9)), "16:9"),
             (abs(ratio - (6 / 7)), "6:7"), (abs(ratio - 0.75), "3:4"), (abs(ratio - 1.0), "1:1")],
            key=lambda x: x[0],
        )
        if near[0] < 0.02:
            rep.add(ch, "宽高比", OK, f"{name} {w}x{h} 宽高比 {ratio:.3f}，接近推荐比例 {near[1]}")
        else:
            rep.add(ch, "宽高比", WARN,
                    f"{name} {w}x{h} 宽高比 {ratio:.3f} 在区间内，但不接近平台推荐比例",
                    f"{w}x{h}", "、".join(vspec.get("recommendedAspects", [])) or "推荐比例")

    short_side = min(w, h)
    soft = vspec.get("minResolutionHeightSoft")
    hard = vspec.get("minResolutionHeight", 1080)
    if short_side < (soft or hard):
        rep.add(ch, "分辨率", ERROR,
                f"{name} 短边仅 {short_side}px，低于最低要求 {soft or hard}px",
                f"{w}x{h}（短边 {short_side}）", f"短边 ≥{soft or hard}")
    elif short_side < hard:
        rep.add(ch, "分辨率", WARN,
                f"{name} 短边 {short_side}px 达到最低要求但低于建议的 {hard}px，信息密度高时会不可读",
                f"{w}x{h}（短边 {short_side}）", f"短边 ≥{hard}")
    else:
        rep.add(ch, "分辨率", OK, f"{name} {w}x{h} 短边 {short_side}px 满足 ≥{hard}p")


# ------------------------------------------------------------- 小红书两线

def check_xhs_image_text(specs: dict, export_root: str, rep: Report):
    spec = form_spec(specs, "xiaohongshu/image-text")
    ch = spec["id"]
    d = os.path.join(export_root, spec["exportPath"])
    if not os.path.isdir(d):
        rep.add(ch, "目录", ERROR, f"缺少产出目录 {d}")
        return

    cards = list_images(d)
    n = len(cards)
    if n == 0:
        rep.add(ch, "图片组", ERROR, "没有找到任何图集图片（非 cover 前缀的图片）")
    else:
        cnt = spec["noteCount"]
        if n > cnt["max"]:
            rep.add(ch, "图片数量", ERROR, f"共 {n} 张，超过上限 {cnt['max']} 张", n, cnt["max"])
        elif n > cnt.get("alternateMax", cnt["max"]):
            rep.add(ch, "图片数量", WARN,
                    f"共 {n} 张：多数资料上限 {cnt['max']} 张，部分入口为 {cnt.get('alternateMax')} 张，以编辑器提示为准",
                    n, f"≤{cnt.get('alternateMax')}（稳妥口径）")
        lo, hi = cnt["recommended"]
        if not (lo <= n <= hi):
            rep.add(ch, "图片数量", WARN, f"共 {n} 张，建议 {lo}–{hi} 张（过少显薄，过多完读率下降）", n, f"{lo}–{hi}")
        else:
            rep.add(ch, "图片数量", OK, f"共 {n} 张，落在建议区间 {lo}–{hi}")

        # 逐张比例 + 全篇比例一致性（小红书整篇只允许一种比例）
        first_ratio = None
        for p in cards:
            wh = check_image(p, spec["card"], ch, "图集", rep,
                             max_bytes=spec["card"]["maxBytes"], formats=spec["card"]["formats"],
                             allow_gif=False)
            if wh and wh[1]:
                r = round(wh[0] / wh[1], 3)
                if first_ratio is None:
                    first_ratio = (r, os.path.basename(p))
                elif abs(r - first_ratio[0]) > 0.02:
                    rep.add(ch, "比例一致性", ERROR,
                            f"{os.path.basename(p)} 比例 {r} 与首图 {first_ratio[1]} 的 {first_ratio[0]} 不一致 —— "
                            f"小红书整篇笔记只允许一种比例",
                            r, first_ratio[0])
        if first_ratio:
            rep.add(ch, "比例一致性", OK, f"全篇比例一致（{first_ratio[0]}，基准 {first_ratio[1]}）")

    # 可选单独封面
    for n_cov in list_files_with_prefix(d, "cover-34"):
        check_image(n_cov, spec["coverOptional"], ch, "单独封面", rep,
                    max_bytes=spec["card"]["maxBytes"], formats=spec["card"]["formats"],
                    allow_gif=False)

    meta = read_meta(d)
    if meta is None:
        rep.add(ch, "meta.json", WARN, "缺少 meta.json，标题 / 正文 / 话题未校验（见 references/platforms/xiaohongshu/image-text.md 交付清单）")
    elif "__error__" in meta:
        rep.add(ch, "meta.json", ERROR, f"meta.json 解析失败：{meta['__error__']}")
    else:
        check_chars(rep, ch, "标题", meta.get("title"), spec["title"]["maxChars"], "标题")
        check_body_chars(rep, ch, "正文", meta, spec["body"]["maxChars"], "正文字数",
                         min_soft=spec["body"]["recommended"][0])
        _check_topics(rep, ch, meta.get("topics"), spec["topics"])

    # 风险词扫描（小红书特有：站外导流 + 绝对化用语）
    texts = collect_banned_texts(d, meta if isinstance(meta, dict) else None)
    if not texts:
        rep.add(ch, "风险词", WARN, "没找到可扫描的文案（meta.json / copy.md），停用词与导流词未核对 —— 小红书这是重点打击项")
    for src, txt in texts:
        check_banned_text(txt, spec, ch, "风险词", rep, source_name=src)

    rep.add(ch, "封面", WARN, "首图即封面 —— 请人工确认第 1 张的钩子在 3:4 中心安全区内可读")


def check_xhs_video(specs: dict, export_root: str, rep: Report):
    spec = form_spec(specs, "xiaohongshu/video")
    ch = spec["id"]
    d = os.path.join(export_root, spec["exportPath"])
    if not os.path.isdir(d):
        rep.add(ch, "目录", ERROR, f"缺少产出目录 {d}")
        return

    vids = list_videos(d)
    vspec = spec["video"]
    if not vids:
        rep.add(ch, "成品视频", ERROR, "找不到成品视频（mp4/mov/m4v）")
    if not ffprobe_available():
        rep.add(ch, "成品视频", WARN, "本机没有 ffprobe，跳过时长 / 编码 / 分辨率检查")
        rep.skipped.append(f"{ch}: video probe (ffprobe missing)")
    for vp in vids:
        rep.checked_files += 1
        name = os.path.basename(vp)
        info = probe_video(vp) if ffprobe_available() else None
        if not info:
            rep.add(ch, "成品视频", WARN, f"{name} 无法探测媒体信息")
            continue

        size = info["size"]
        if size > vspec["maxBytes"]:
            rep.add(ch, "视频体积", ERROR, f"{name} {human_bytes(size)} 超过上限",
                    human_bytes(size), f"≤{human_bytes(vspec['maxBytes'])}")
        else:
            rep.add(ch, "视频体积", OK, f"{name} {human_bytes(size)}（上限 {human_bytes(vspec['maxBytes'])}）")

        dur = info["duration"]
        if dur < vspec["durationSeconds"]["min"]:
            rep.add(ch, "时长", ERROR, f"{name} 仅 {dur:.1f}s，低于最短 {vspec['durationSeconds']['min']}s")
        elif dur > vspec["durationSeconds"]["max"]:
            rep.add(ch, "时长", ERROR, f"{name} {human_duration(dur)} 超过上限 {human_duration(vspec['durationSeconds']['max'])}",
                    human_duration(dur), human_duration(vspec["durationSeconds"]["max"]))
        else:
            rep.add(ch, "时长", OK, f"{name} {human_duration(dur)}")
        if dur > 180:
            rep.add(ch, "时长", INFO, f"{name} 超过 3 分钟：小红书这类内容完播率通常低于 1–2 分钟的（经验值，非平台红线）")

        _check_aspect_and_resolution(info, vspec, ch, name, rep)

        codec = info["codec"]
        if codec not in vspec["codecs"]:
            rep.add(ch, "编码", WARN, f"{name} 编码 {codec or '未知'} 不在推荐编码内（建议 H.264）", codec, vspec["codecs"])
        else:
            rep.add(ch, "编码", OK, f"{name} 编码 {codec}")
        if info["pix_fmt"] and info["pix_fmt"] != "yuv420p":
            rep.add(ch, "像素格式", WARN, f"{name} pix_fmt={info['pix_fmt']}，建议 yuv420p", info["pix_fmt"], "yuv420p")
        fps = info.get("fps")
        if fps:
            lo, hi = vspec["fpsRange"]
            if not (lo - 1 <= fps <= hi + 1):
                rep.add(ch, "帧率", WARN, f"{name} 帧率 {fps}fps 不在建议区间 {lo}–{hi}fps", fps, f"{lo}–{hi}")
            else:
                rep.add(ch, "帧率", OK, f"{name} 帧率 {fps}fps")
        if not info["has_audio"]:
            rep.add(ch, "音轨", WARN, f"{name} 没有音频轨（视频笔记通常需要 BGM 或人声）")

    # 封面（3:4 独立封面）
    cv = spec["cover"]["primary"]
    found = list_files_with_prefix(d, "cover-34")
    if not found:
        rep.add(ch, "封面", ERROR, f"没找到 cover-34.* 封面（{cv['ratio']}，推荐 {cv['width']}x{cv['height']}）—— 小红书视频封面不要用首帧")
    for n in found:
        check_image(n, cv, ch, "封面", rep, max_bytes=20 * 1024 * 1024,
                    formats=["jpg", "jpeg", "png"])

    meta = read_meta(d)
    if meta is None:
        rep.add(ch, "meta.json", WARN, "缺少 meta.json，标题 / 正文 / 话题未校验（见 references/platforms/xiaohongshu/video.md 交付清单）")
    elif "__error__" in meta:
        rep.add(ch, "meta.json", ERROR, f"meta.json 解析失败：{meta['__error__']}")
    else:
        check_chars(rep, ch, "标题", meta.get("title"), spec["title"]["maxChars"], "标题")
        check_body_chars(rep, ch, "正文", meta, spec["body"]["maxChars"], "正文字数",
                         min_soft=spec["body"]["recommended"][0])
        _check_topics(rep, ch, meta.get("topics"), spec["topics"])

    texts = collect_banned_texts(d, meta if isinstance(meta, dict) else None)
    if not texts:
        rep.add(ch, "风险词", WARN, "没找到可扫描的文案（meta.json / copy.md），导流词与绝对化用语未核对")
    for src, txt in texts:
        check_banned_text(txt, spec, ch, "风险词", rep, source_name=src)

    rep.add(ch, "前 3 秒", WARN, "完播关键在前 3 秒 —— 请人工确认开头即钩子，没有等待入场的空镜头")


def _check_topics(rep: Report, ch: str, topics, tspec: dict):
    if topics is None:
        rep.add(ch, "话题标签", WARN, "meta.json 缺 topics，话题数量未校验（小红书话题直接影响被发现）")
        return
    n = len(topics) if isinstance(topics, list) else len(str(topics).split())
    hi = tspec.get("max", 15)
    lo = tspec.get("min", 5)
    if n > hi:
        rep.add(ch, "话题标签", WARN, f"话题 {n} 个超过建议上限 {hi} 个", n, f"≤{hi}")
    elif n < lo:
        rep.add(ch, "话题标签", WARN, f"话题仅 {n} 个，建议 {lo}–{hi} 个", n, f"{lo}–{hi}")
    else:
        rep.add(ch, "话题标签", OK, f"话题 {n} 个，落在建议区间 {lo}–{hi}")


# ------------------------------------------------------------- 通用产品片

def check_generic_product_video(specs: dict, export_root: str, rep: Report):
    """产品片走视频线原生流程，这里只做兜底结构检查（不校验画幅/封面）。"""
    spec = form_spec(specs, "generic/product-video")
    ch = spec["id"]
    d = os.path.join(export_root, spec["exportPath"])
    if not os.path.isdir(d):
        rep.add(ch, "目录", ERROR, f"缺少产出目录 {d}")
        return

    vids = list_videos(d)
    if not vids:
        rep.add(ch, "成品视频", ERROR, "找不到成品视频（mp4/mov/m4v）")
    for vp in vids:
        rep.checked_files += 1
        name = os.path.basename(vp)
        info = probe_video(vp) if ffprobe_available() else None
        if not info:
            rep.add(ch, "成品视频", WARN, f"{name} 无法探测媒体信息（无 ffprobe 或文件异常）")
            continue
        dur = info["duration"]
        rep.add(ch, "成品视频", OK, f"{name} {info['width']}x{info['height']} "
                                   f"{human_duration(dur)} {info['codec']} {human_bytes(info['size'])}")
        if dur < spec["video"]["durationSeconds"]["min"]:
            rep.add(ch, "时长", ERROR, f"{name} 时长 {dur:.1f}s 过短", dur, f"≥{spec['video']['durationSeconds']['min']}s")
        if spec["video"].get("requiresAudio") and not info["has_audio"]:
            rep.add(ch, "音轨", WARN, f"{name} 声明需要音频但没有音轨")
    rep.add(ch, "验收", WARN,
            "产品片的正式验收用视频线 check_delivery.py（结构 / 时间线 / 方向文件 / 画面节奏 + 人工审片），本项只做兜底结构检查")


# ------------------------------------------------------------------ 登记表

FORM_CHECKS = {
    "wechat/image-text": check_wechat_image_text,
    "wechat/mp-article": check_wechat_mp_article,
    "wechat/channels": check_wechat_channels,
    "xiaohongshu/image-text": check_xhs_image_text,
    "xiaohongshu/video": check_xhs_video,
    "generic/product-video": check_generic_product_video,
}

# 兼容旧的一级形式名（v1.0 的 channels 取值），仅用于平滑迁移
LEGACY_ALIAS = {
    "wechat-image-text": "wechat/image-text",
    "wechat-mp-article": "wechat/mp-article",
    "wechat-channels": "wechat/channels",
    "product-video": "generic/product-video",
}


# ------------------------------------------------------------------ 主流程

def resolve_export_root(project: str) -> str:
    p = os.path.abspath(project)
    nested = os.path.join(p, "export")
    if os.path.isdir(nested):
        return nested
    return p


def discover_forms(export_root: str) -> list[str]:
    """自动发现 export/ 下已存在的形式目录。"""
    found = []
    for fid in FORM_CHECKS:
        spec_path = fid.split("/")
        d = os.path.join(export_root, *spec_path)
        if os.path.isdir(d):
            found.append(fid)
    return found


def form_label(specs: dict, fid: str) -> str:
    idx = form_index(specs)
    if fid in idx:
        return idx[fid][2].get("label", fid)
    return fid


def print_list(specs: dict):
    print(f"规格版本：{specs['specVersion']}\n")
    for pkey, plat in specs["platforms"].items():
        print(f"● {plat['label']}  ({pkey})")
        for fkey, fspec in plat["forms"].items():
            fid = fspec.get("id", f"{pkey}/{fkey}")
            mark = "✓" if fid in FORM_CHECKS else "·"
            print(f"    {mark} {fid:<26} {fspec.get('label', fkey):<18} → export/{fspec['exportPath']}/")
    print(f"\n已登记自检的形式：{len(FORM_CHECKS)} / 共 "
          f"{sum(len(p['forms']) for p in specs['platforms'].values())} 个")


def print_specs(specs: dict, fid: str | None):
    if fid:
        fid = LEGACY_ALIAS.get(fid, fid)
        try:
            spec = form_spec(specs, fid)
        except KeyError:
            print(f"未知形式 {fid}；可用：{', '.join(form_index(specs))}", file=sys.stderr)
            sys.exit(2)
        print(json.dumps(spec, ensure_ascii=False, indent=2))
        return
    print(json.dumps({"specVersion": specs["specVersion"],
                      "platforms": {k: {"label": v["label"], "forms": list(v["forms"])}
                                    for k, v in specs["platforms"].items()},
                      "sources": specs["sources"]}, ensure_ascii=False, indent=2))


def render_report(rep: Report, specs: dict) -> str:
    icons = {ERROR: "✗", WARN: "!", INFO: "·", OK: "✓"}
    idx = form_index(specs)
    lines = []
    for fid in idx:
        fs = [f for f in rep.findings if f.channel == fid]
        if not fs:
            continue
        lines.append(f"\n── {form_label(specs, fid)} ({fid}) " + "─" * 16)
        for f in sorted(fs, key=lambda x: -LEVEL_ORDER[x.level]):
            a = f" [实测 {f.actual}]" if f.actual is not None else ""
            e = f" [要求 {f.expected}]" if f.expected is not None else ""
            lines.append(f"  {icons[f.level]} {f.item}: {f.message}{a}{e}")
        c = {ERROR: 0, WARN: 0, INFO: 0, OK: 0}
        for f in fs:
            c[f.level] += 1
        lines.append(f"  小计：error {c[ERROR]} / warn {c[WARN]} / info {c[INFO]} / ok {c[OK]}")
    other = [f for f in rep.findings if f.channel not in idx]
    if other:
        lines.append("\n── 其他 " + "─" * 30)
        for f in other:
            lines.append(f"  {icons[f.level]} {f.channel}/{f.item}: {f.message}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="全平台多形式产出物自检（规格来源：scripts/social_specs.json）")
    ap.add_argument("--project", help="内容目录，或 export 目录本身")
    ap.add_argument("--forms", default=None,
                    help="逗号分隔的形式 ID，如 wechat/mp-article,xiaohongshu/image-text；不给则自动发现")
    ap.add_argument("--channels", dest="forms_alias", default=None,
                    help="（已弃用）旧参数名，等价于 --forms，兼容 v1.0 的形式名")
    ap.add_argument("--strict", action="store_true", help="把 warning 也算失败（退出码 1）")
    ap.add_argument("--list", action="store_true", help="列出全部平台与形式后退出")
    ap.add_argument("--print-specs", action="store_true", help="打印规格后退出")
    ap.add_argument("--form", "--channel", dest="single_form", help="配合 --print-specs，只打印某一形式的规格")
    ap.add_argument("--json", dest="json_out", help="把完整报告写成 JSON 到该路径")
    args = ap.parse_args()

    specs = load_specs()

    if args.list:
        print_list(specs)
        return 0

    if args.print_specs:
        print_specs(specs, args.single_form)
        return 0

    if not args.project:
        ap.error("--project 必填（除非用 --print-specs / --list）")

    raw = args.forms if args.forms is not None else args.forms_alias
    if raw:
        forms = [LEGACY_ALIAS.get(f.strip(), f.strip()) for f in raw.split(",") if f.strip()]
    else:
        export_root = resolve_export_root(args.project)
        forms = discover_forms(export_root)
        if not forms:
            print(f"在 {export_root} 下没有发现任何已登记的形式目录，"
                  f"可用：{', '.join(FORM_CHECKS)}", file=sys.stderr)
            return 2
        print(f"（未指定 --forms，自动发现 {len(forms)} 个形式）")

    unknown = [f for f in forms if f not in FORM_CHECKS]
    if unknown:
        print(f"未登记的形式：{', '.join(unknown)}；可用：{', '.join(FORM_CHECKS)}", file=sys.stderr)
        return 2

    export_root = resolve_export_root(args.project)
    print(f"内容目录：{os.path.abspath(args.project)}")
    print(f"产出目录：{export_root}")
    print(f"规格版本：{specs['specVersion']}   形式：{', '.join(forms)}")

    rep = Report()
    for fid in forms:
        FORM_CHECKS[fid](specs, export_root, rep)

    print(render_report(rep, specs))
    c = rep.counts()
    print(f"\n共检查 {rep.checked_files} 个文件；error {c[ERROR]} / warn {c[WARN]} / info {c[INFO]} / ok {c[OK]}")
    print("\n提醒：本脚本只证明尺寸 / 比例 / 体积 / 字数 / 禁用项等结构性事实。视觉效果、语义正确性、"
          "平台真实渲染（尤其公众号粘贴后的样式、小红书封面裁切、手机预览）必须人工复核 —— "
          "与视频线硬约束「授权与真实验收」一致。")

    if rep.skipped:
        print("跳过项：" + "; ".join(rep.skipped))

    if args.json_out:
        payload = {
            "project": os.path.abspath(args.project),
            "exportRoot": export_root,
            "specVersion": specs["specVersion"],
            "forms": forms,
            "counts": {k: v for k, v in rep.counts().items()},
            "checkedFiles": rep.checked_files,
            "findings": [asdict(f) for f in rep.findings],
        }
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"报告已写入 {args.json_out}")

    if rep.worst >= LEVEL_ORDER[ERROR]:
        print("\n结论：不通过（存在 error）")
        return 1
    if args.strict and rep.worst >= LEVEL_ORDER[WARN]:
        print("\n结论：--strict 模式不通过（存在 warning）")
        return 1
    print("\n结论：通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())

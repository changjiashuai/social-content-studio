#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_social_delivery.py 的单元测试。

用法：
    python3 -m unittest discover -s <skill-dir>/tests -v

设计原则：**不依赖 ffmpeg / Pillow / 网络**。测试样本用纯标准库现场生成
（自写 PNG/GIF 字节流），所以任何环境下都能跑，适合放进 CI 或改脚本后的回归。

视频相关的深度检查需要 ffprobe，本文件只覆盖「无 ffprobe 时也应成立」的部分
（文件存在性、封面比例、字数、风险词）；真实视频的时长/编码/码率靠产出物验收。
"""

from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(SKILL_DIR, "scripts", "check_social_delivery.py")
SPECS_FILE = os.path.join(SKILL_DIR, "scripts", "social_specs.json")
PY = sys.executable


# ───────────────────────────────────── 样本构造（纯标准库）

def write_png(path: str, w: int, h: int, rgb=(0x2F, 0x6B, 0xFF)):
    """写一张纯色 PNG。"""
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(typ: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    blob = b"\x89PNG\r\n\x1a\n"
    blob += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    blob += chunk(b"IDAT", zlib.compress(raw, 6))
    blob += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(blob)


def write_fake_gif(path: str, frames: int, w: int = 1080, h: int = 1440):
    """写一个 GCE 块数量可控的 GIF 字节流，用于验证动图帧数上限检查。"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    blob = b"GIF89a" + struct.pack("<HH", w, h) + b"\xf7\x00\x00"
    blob += b"\x21\xf9\x04" * frames
    blob += b"\x3b"
    with open(path, "wb") as fh:
        fh.write(blob)


def write_json(path: str, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False)


def write_text(path: str, text: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def write_bytes(path: str, blob: bytes):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(blob)


def read_json(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ───────────────────────────────────── 基类

class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="social-check-test-")
        self.export = os.path.join(self.tmp, "export")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_check(self, forms="wechat/image-text", strict=False, extra=None, project=None):
        cmd = [PY, SCRIPT, "--project", project or self.tmp]
        if forms:
            cmd += ["--forms", forms]
        if strict:
            cmd.append("--strict")
        if extra:
            cmd += extra
        p = subprocess.run(cmd, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    # 便捷构造：一组合规的图卡/图集
    def make_cards(self, n=8, w=1080, h=1440, sub="wechat/image-text", prefix=""):
        for i in range(1, n + 1):
            write_png(os.path.join(self.export, sub, f"{prefix}{i:02d}.png"), w, h)


# ───────────────────────────────────── 注册表与规格

class TestRegistry(Base):
    def test_list_forms(self):
        p = subprocess.run([PY, SCRIPT, "--list"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        for fid in ("wechat/image-text", "wechat/mp-article", "wechat/channels",
                    "xiaohongshu/image-text", "xiaohongshu/video", "generic/product-video"):
            self.assertIn(fid, p.stdout, f"--list 未列出 {fid}")

    def test_print_specs_single_form(self):
        p = subprocess.run([PY, SCRIPT, "--print-specs", "--form", "wechat/channels"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["cover"]["vertical"]["width"], 1080)
        self.assertEqual(data["cover"]["vertical"]["height"], 1260)
        self.assertEqual(data["shortTitle"]["maxChars"], 16)

    def test_print_specs_xiaohongshu(self):
        p = subprocess.run([PY, SCRIPT, "--print-specs", "--form", "xiaohongshu/image-text"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual((data["card"]["width"], data["card"]["height"]), (1080, 1440))
        self.assertEqual(data["title"]["maxChars"], 20)
        self.assertEqual(data["body"]["maxChars"], 1000)

    def test_legacy_alias_still_works(self):
        """v1.0 的一级形式名（wechat-channels）应被平滑映射到 wechat/channels。"""
        p = subprocess.run([PY, SCRIPT, "--print-specs", "--form", "wechat-channels"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["id"], "wechat/channels")

    def test_print_specs_unknown_form_exit_2(self):
        p = subprocess.run([PY, SCRIPT, "--print-specs", "--form", "douyin/video"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    def test_every_form_is_registered(self):
        """specs.json 里的每个形式都必须有对应的检查函数（漏登记会导致静默跳过）。"""
        sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
        import check_social_delivery as mod  # noqa: E402
        specs = read_json(SPECS_FILE)
        ids = {f["id"] for p in specs["platforms"].values() for f in p["forms"].values()}
        self.assertEqual(ids, set(mod.FORM_CHECKS),
                         "specs.json 与 FORM_CHECKS 的形式集合不一致")

    def test_specs_match_all_templates(self):
        """specs.json 的画布尺寸与模板 CSS 必须一致（防止改一处忘了另一处）。"""
        specs = read_json(SPECS_FILE)

        def spec_of(fid, *path):
            plat, form = fid.split("/")
            node = specs["platforms"][plat]["forms"][form]
            for k in path:
                node = node[k]
            return node

        self.assertEqual(tuple(spec_of("wechat/image-text", "card")[k] for k in ("width", "height")), (1080, 1440))
        self.assertEqual(tuple(spec_of("wechat/channels", "cover", "vertical")[k] for k in ("width", "height")), (1080, 1260))
        self.assertEqual(tuple(spec_of("xiaohongshu/image-text", "card")[k] for k in ("width", "height")), (1080, 1440))
        self.assertEqual(tuple(spec_of("xiaohongshu/video", "cover", "primary")[k] for k in ("width", "height")), (1080, 1440))

        def html(rel):
            return read_text(os.path.join(SKILL_DIR, rel))

        self.assertIn("--card-w: 1080px", html("assets/platforms/wechat/image-text/card.template.html"))
        self.assertIn("--card-h: 1440px", html("assets/platforms/wechat/image-text/card.template.html"))
        self.assertIn("1080px", html("assets/platforms/wechat/channels/cover-67.template.html"))
        self.assertIn("1260px", html("assets/platforms/wechat/channels/cover-67.template.html"))
        self.assertIn("--card-w: 1080px", html("assets/platforms/xiaohongshu/image-text/note.template.html"))
        self.assertIn("--card-h: 1440px", html("assets/platforms/xiaohongshu/image-text/note.template.html"))
        self.assertIn("width: 1080px", html("assets/platforms/xiaohongshu/video/cover-34.template.html"))
        self.assertIn("height: 1440px", html("assets/platforms/xiaohongshu/video/cover-34.template.html"))


# ───────────────────────────────────── 图片尺寸解析

class TestImageSizeParser(Base):
    def _mod(self):
        sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
        import check_social_delivery as mod  # noqa: E402
        return mod

    def test_read_image_size_png(self):
        p = os.path.join(self.tmp, "a.png")
        write_png(p, 1234, 567)
        self.assertEqual(self._mod().read_image_size(p), (1234, 567))

    def test_read_image_size_bad_file(self):
        p = os.path.join(self.tmp, "b.bin")
        write_bytes(p, b"not an image at all, really")
        self.assertIsNone(self._mod().read_image_size(p))


# ───────────────────────────────────── 微信图文

class TestWechatImageText(Base):
    def test_pass_clean_cards(self):
        self.make_cards(8)
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"), {
            "form": "wechat/image-text",
            "title": "打包体积砍到 48MB",
            "cardTexts": ["短", "也很短"],
        })
        rc, out = self.run_check()
        self.assertEqual(rc, 0, out)
        self.assertIn("结论：通过", out)

    def test_wrong_ratio_is_error(self):
        self.make_cards(6)
        write_png(os.path.join(self.export, "wechat/image-text", "07.png"), 1000, 1000)
        rc, out = self.run_check()
        self.assertEqual(rc, 1, out)
        self.assertIn("比例偏离", out)

    def test_off_ratio_within_tolerance_only_warns(self):
        # 1078x1440 → 0.7486，偏离 0.0014，在容差内
        self.make_cards(6)
        write_png(os.path.join(self.export, "wechat/image-text", "07.png"), 1078, 1440)
        rc, out = self.run_check()
        self.assertEqual(rc, 0, out)

    def test_too_many_cards_is_error(self):
        self.make_cards(21)
        rc, out = self.run_check()
        self.assertEqual(rc, 1, out)
        self.assertIn("超过官方上限 20 张", out)

    def test_twelve_cards_warns_not_error(self):
        self.make_cards(12)
        rc, out = self.run_check()
        self.assertEqual(rc, 0, out)
        self.assertIn("稳妥口径只到 9 张", out)

    def test_title_over_64_is_error(self):
        self.make_cards(6)
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"),
                   {"title": "字" * 65, "cardTexts": ["x"]})
        rc, out = self.run_check()
        self.assertEqual(rc, 1, out)
        self.assertIn("标题 超限：65 字", out)

    def test_title_exactly_64_passes(self):
        self.make_cards(6)
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"),
                   {"title": "字" * 64, "cardTexts": ["x"]})
        rc, out = self.run_check()
        self.assertEqual(rc, 0, out)
        self.assertIn("标题 64 字", out)

    def test_per_card_text_over_2000_is_error(self):
        self.make_cards(6)
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"),
                   {"title": "ok", "cardTexts": ["字" * 2001]})
        rc, out = self.run_check()
        self.assertEqual(rc, 1, out)
        self.assertIn("超过官方上限 2000", out)

    def test_gif_frames_over_300_is_error(self):
        self.make_cards(6)
        write_fake_gif(os.path.join(self.export, "wechat/image-text", "07.gif"), frames=301)
        rc, out = self.run_check()
        self.assertEqual(rc, 1, out)
        self.assertIn("动图帧数超标", out)

    def test_missing_dir_is_error(self):
        rc, out = self.run_check()
        self.assertEqual(rc, 1, out)
        self.assertIn("缺少产出目录", out)


# ───────────────────────────────────── 公众号长文

class TestWechatMpArticle(Base):
    FORM = "wechat/mp-article"
    SUB = "wechat/mp-article"

    def make_cover(self, w=900, h=383, name="cover-235.png"):
        write_png(os.path.join(self.export, self.SUB, name), w, h)

    def test_banned_style_block_is_error(self):
        write_text(os.path.join(self.export, self.SUB, "article.html"),
                   "<style>p{color:red}</style><p style='font-size:16px'>hi</p>")
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("禁用项", out)
        self.assertIn("style 块会被剥离", out)

    def test_clean_inline_html_passes(self):
        write_text(os.path.join(self.export, self.SUB, "article.html"),
                   '<p style="font-size:16px; line-height:1.8; color:#3f3f3f;">正文</p>'
                   '<img src="https://mmbiz.qpic.cn/mmbiz_jpg/x/0?wx_fmt=jpeg" style="width:100%">')
        self.make_cover()
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"title": "标题", "digest": "摘要", "author": "作者", "bodyChars": 100, "imageCount": 1})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)
        self.assertIn("未命中任何平台禁用项", out)

    def test_placeholder_src_is_accepted(self):
        write_text(os.path.join(self.export, self.SUB, "article.html"),
                   '<p style="font-size:16px">x</p><img src="__UPLOAD_TO_MP_ASSET_LIBRARY__">')
        self.make_cover()
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"title": "标题", "digest": "摘要", "author": "作者", "bodyChars": 1, "imageCount": 0})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)

    def test_external_img_src_is_error(self):
        write_text(os.path.join(self.export, self.SUB, "article.html"),
                   '<p style="font-size:16px">x</p><img src="./local.png">')
        self.make_cover()
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"title": "标题", "digest": "摘要", "author": "作者", "bodyChars": 1, "imageCount": 1})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("未使用微信素材库地址", out)

    def test_digest_over_120_is_error(self):
        write_text(os.path.join(self.export, self.SUB, "article.html"),
                   '<p style="font-size:16px">x</p>')
        self.make_cover()
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"title": "标题", "digest": "字" * 121, "author": "作者", "bodyChars": 1, "imageCount": 0})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("摘要 超限：121 字", out)

    def test_cover_ratio_mismatch_is_error(self):
        write_text(os.path.join(self.export, self.SUB, "article.html"),
                   '<p style="font-size:16px">x</p>')
        self.make_cover(900, 383, "cover-235.png")
        self.make_cover(900, 383, "cover-11.png")   # 1:1 位置放了 2.35:1 的图
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"title": "标题", "digest": "摘要", "author": "作者", "bodyChars": 1, "imageCount": 0})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("次条封面", out)


# ───────────────────────────────────── 视频号（不依赖 ffprobe 的部分）

class TestWechatChannels(Base):
    FORM = "wechat/channels"
    SUB = "wechat/channels"

    def setUp(self):
        super().setUp()
        write_png(os.path.join(self.export, self.SUB, "cover-67.png"), 1080, 1260)
        write_png(os.path.join(self.export, self.SUB, "cover-169.png"), 1080, 608)

    def test_short_title_over_16_is_error(self):
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"description": "短描述", "shortTitles": ["字" * 17]})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("短标题候选 1 超限：17 字", out)

    def test_description_over_1000_is_error(self):
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"description": "字" * 1001, "shortTitles": ["还行"]})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("描述 超限：1001 字", out)

    def test_cover_ratios_checked(self):
        write_png(os.path.join(self.export, self.SUB, "cover-67.png"), 1080, 1080)  # 应为 6:7
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"description": "短", "shortTitles": ["短标题"]})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("竖版封面", out)

    def test_missing_video_reported(self):
        write_json(os.path.join(self.export, self.SUB, "meta.json"),
                   {"description": "短", "shortTitles": ["短标题"]})
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("找不到成品视频", out)


# ───────────────────────────────────── 小红书图文笔记

class TestXhsImageText(Base):
    FORM = "xiaohongshu/image-text"
    SUB = "xiaohongshu/image-text"

    def write_meta(self, title="首屏快 3 倍", body_chars=186, topics=None):
        write_json(os.path.join(self.export, self.SUB, "meta.json"), {
            "form": "xiaohongshu/image-text",
            "title": title,
            "bodyChars": body_chars,
            "topics": topics if topics is not None else ["#前端性能", "#技术分享", "#实用技巧", "#首屏优化", "#程序员"],
        })

    def test_pass_clean_note(self):
        self.make_cards(8, sub=self.SUB)
        self.write_meta()
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)
        self.assertIn("全篇比例一致", out)

    def test_mixed_ratio_is_error(self):
        self.make_cards(5, sub=self.SUB)
        write_png(os.path.join(self.export, self.SUB, "06.png"), 1080, 1080)
        self.write_meta()
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("比例一致性", out)

    def test_too_many_images_is_error(self):
        self.make_cards(19, sub=self.SUB)
        self.write_meta()
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("超过官方上限 18 张", out)

    def test_title_over_20_is_error(self):
        self.make_cards(6, sub=self.SUB)
        self.write_meta(title="字" * 21)
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("标题 超限：21 字", out)

    def test_body_over_1000_is_error(self):
        self.make_cards(6, sub=self.SUB)
        self.write_meta(body_chars=1001)
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("正文字数 超限：1001 字", out)

    def test_too_few_topics_warns(self):
        self.make_cards(6, sub=self.SUB)
        self.write_meta(topics=["#前端性能", "#技术分享"])
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)
        self.assertIn("话题仅 2 个", out)

    def test_too_many_topics_warns(self):
        self.make_cards(6, sub=self.SUB)
        self.write_meta(topics=[f"#tag{i}" for i in range(16)])
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)
        # 话题上限口径不一（15 vs 10）：16 个超过官方宣称的 15 个，仍只 WARN，附原文
        self.assertIn("共 16 个，超过官方上限 15 个", out)
        self.assertIn("话题数量上限为官方口径不一项", out)

    def test_topics_in_uncertain_band_warns_with_safe_value(self):
        """12 个话题落在「稳妥 10 ~ 官方 15」之间：WARN 并给出稳妥口径，而不是判 OK。"""
        self.make_cards(6, sub=self.SUB)
        self.write_meta(topics=[f"#tag{i}" for i in range(12)])
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)
        self.assertIn("官方上限 15 个", out)
        self.assertIn("稳妥口径", out)

    def test_gif_is_rejected(self):
        self.make_cards(6, sub=self.SUB)
        write_fake_gif(os.path.join(self.export, self.SUB, "07.gif"), frames=10)
        self.write_meta()
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("GIF 在该渠道不支持", out)

    def test_offsite_funnel_is_warned(self):
        """站外导流词命中报 WARN（小红书红线，脚本负责指出，人工判断语境）。"""
        self.make_cards(6, sub=self.SUB)
        self.write_meta(title="加我微信领资料")
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)          # WARN 不改退出码
        self.assertIn("命中平台风险词", out)

    def test_absolute_wording_is_warned(self):
        self.make_cards(6, sub=self.SUB)
        self.write_meta(title="全网最低价 最有效")
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)
        self.assertIn("命中平台风险词", out)

    def test_optional_cover_checked(self):
        self.make_cards(6, sub=self.SUB)
        write_png(os.path.join(self.export, self.SUB, "cover-34.png"), 1080, 1080)  # 应为 3:4
        self.write_meta()
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("单独封面", out)

    def test_missing_dir_is_error(self):
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("缺少产出目录", out)


# ───────────────────────────────────── 小红书视频笔记

class TestXhsVideo(Base):
    FORM = "xiaohongshu/video"
    SUB = "xiaohongshu/video"

    def write_meta(self, title="首屏快 3 倍", body_chars=142, topics=None):
        write_json(os.path.join(self.export, self.SUB, "meta.json"), {
            "form": "xiaohongshu/video",
            "title": title,
            "bodyChars": body_chars,
            "topics": topics if topics is not None else ["#前端性能", "#技术分享", "#实用技巧", "#首屏优化", "#程序员"],
        })

    def test_missing_cover_is_error(self):
        write_bytes(os.path.join(self.export, self.SUB, "final.mp4"), b"\x00\x00\x00\x18ftypmp42")
        self.write_meta()
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("小红书视频封面不要用首帧", out)

    def test_cover_wrong_ratio_is_error(self):
        write_bytes(os.path.join(self.export, self.SUB, "final.mp4"), b"\x00\x00\x00\x18ftypmp42")
        write_png(os.path.join(self.export, self.SUB, "cover-34.png"), 1080, 1080)  # 应为 3:4
        self.write_meta()
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("封面", out)
        self.assertIn("比例偏离", out)

    def test_correct_cover_and_meta_passes(self):
        write_bytes(os.path.join(self.export, self.SUB, "final.mp4"), b"\x00\x00\x00\x18ftypmp42")
        write_png(os.path.join(self.export, self.SUB, "cover-34.png"), 1080, 1440)
        self.write_meta()
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)

    def test_title_over_20_is_error(self):
        write_bytes(os.path.join(self.export, self.SUB, "final.mp4"), b"\x00\x00\x00\x18ftypmp42")
        write_png(os.path.join(self.export, self.SUB, "cover-34.png"), 1080, 1440)
        self.write_meta(title="字" * 21)
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("标题 超限：21 字", out)

    def test_offsite_funnel_is_warned(self):
        write_bytes(os.path.join(self.export, self.SUB, "final.mp4"), b"\x00\x00\x00\x18ftypmp42")
        write_png(os.path.join(self.export, self.SUB, "cover-34.png"), 1080, 1440)
        self.write_meta(title="私信我拿模板")
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)
        self.assertIn("命中平台风险词", out)


# ───────────────────────────────────── 通用产品片

class TestGenericProductVideo(Base):
    FORM = "generic/product-video"
    SUB = "generic/product-video"

    def test_missing_dir_is_error(self):
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("缺少产出目录", out)

    def test_missing_video_is_error(self):
        os.makedirs(os.path.join(self.export, self.SUB), exist_ok=True)
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 1, out)
        self.assertIn("找不到成品视频", out)

    def test_video_present_does_not_hard_fail(self):
        """产品片允许自由画幅：无 ffprobe 时只提示，不判失败。"""
        write_bytes(os.path.join(self.export, self.SUB, "final.mp4"), b"\x00\x00\x00\x18ftypmp42")
        rc, out = self.run_check(self.FORM)
        self.assertEqual(rc, 0, out)


# ───────────────────────────────────── CLI 行为

class TestCli(Base):
    def test_unknown_form_exit_2(self):
        os.makedirs(self.export, exist_ok=True)
        p = subprocess.run([PY, SCRIPT, "--project", self.tmp, "--forms", "nope/nope"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    def test_strict_turns_warning_into_failure(self):
        self.make_cards(12)                      # 12 张 → 触发 warning，但不触发 error
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"),
                   {"title": "标题", "cardTexts": ["x"]})
        rc, _ = self.run_check(strict=False)
        self.assertEqual(rc, 0)
        rc, out = self.run_check(strict=True)
        self.assertEqual(rc, 1, out)
        self.assertIn("--strict 模式不通过", out)

    def test_json_report_written(self):
        self.make_cards(6)
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"),
                   {"title": "标题", "cardTexts": ["x"]})
        out_json = os.path.join(self.tmp, "check.json")
        rc, out = self.run_check(extra=["--json", out_json])
        self.assertTrue(os.path.isfile(out_json), out)
        data = read_json(out_json)
        self.assertEqual(data["specVersion"], read_json(SPECS_FILE)["specVersion"])
        self.assertIn("wechat/image-text", data["forms"])
        self.assertTrue(any(f["level"] == "ok" for f in data["findings"]))

    def test_export_dir_can_be_passed_directly(self):
        self.make_cards(6)
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"),
                   {"title": "标题", "cardTexts": ["x"]})
        rc, out = self.run_check(forms="wechat/image-text", project=self.export)
        self.assertEqual(rc, 0, out)

    def test_form_auto_discovery(self):
        """不给 --forms 时，自动发现 export/ 下已存在的形式。"""
        self.make_cards(6)
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"),
                   {"title": "标题", "cardTexts": ["x"]})
        rc, out = self.run_check(forms=None)
        self.assertEqual(rc, 0, out)
        self.assertIn("自动发现", out)

    def test_two_forms_checked_together(self):
        """跨平台同时自检：两个形式的结果都要出现在同一份报告里。"""
        self.make_cards(6)
        write_json(os.path.join(self.export, "wechat/image-text", "meta.json"),
                   {"title": "标题", "cardTexts": ["x"]})
        self.make_cards(5, sub="xiaohongshu/image-text")
        write_json(os.path.join(self.export, "xiaohongshu/image-text", "meta.json"),
                   {"title": "标题", "bodyChars": 120,
                    "topics": ["#a", "#b", "#c", "#d", "#e"]})
        rc, out = self.run_check(forms="wechat/image-text,xiaohongshu/image-text")
        self.assertEqual(rc, 0, out)
        self.assertIn("wechat/image-text", out)
        self.assertIn("xiaohongshu/image-text", out)


# ───────────────────────────────────── 不确定规格（uncertainty）

class TestUncertaintySpecs(Base):
    """social_specs.json 里的口径不一项目必须被脚本消费，而不是只当注释。"""

    def load_module(self):
        sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
        import check_social_delivery as mod
        return mod

    def test_specs_with_uncertainty_use_safe_max(self):
        """凡带 uncertainty 的上限项，都必须给出 safeMax，否则灰区无从判断。"""
        with open(SPECS_FILE, encoding="utf-8") as fh:
            specs = json.load(fh)

        def walk(node, path):
            if isinstance(node, dict):
                if "uncertainty" in node and "max" in node:
                    self.assertIn("safeMax", node,
                                  f"{path} 有 uncertainty 却没有 safeMax，脚本无法判定稳妥口径")
                for k, v in node.items():
                    walk(v, f"{path}/{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{path}[{i}]")

        walk(specs, "")
        # 至少确认已知的几项确实带 safeMax
        forms = specs["platforms"]
        self.assertEqual(forms["wechat"]["forms"]["image-text"]["cardCount"]["safeMax"], 9)
        self.assertEqual(forms["xiaohongshu"]["forms"]["image-text"]["noteCount"]["safeMax"], 9)
        self.assertEqual(forms["xiaohongshu"]["forms"]["image-text"]["topics"]["safeMax"], 10)

    def test_uncertain_max_splits_band(self):
        m = self.load_module()
        soft, hard, u = m.uncertain_max({"max": 18, "safeMax": 9, "uncertainty": "口径不一"})
        self.assertEqual((soft, hard), (9, 18))
        self.assertIsNotNone(u)

    def test_uncertain_max_without_declaration_has_no_band(self):
        m = self.load_module()
        soft, hard, u = m.uncertain_max({"max": 20})
        self.assertEqual((soft, hard), (20, 20))
        self.assertIsNone(u)

    def test_uncertain_max_swapped_bounds_do_not_crash(self):
        """safeMax 写得比 max 还大时不崩，且 soft <= hard。"""
        m = self.load_module()
        soft, hard, _ = m.uncertain_max({"max": 5, "safeMax": 9, "uncertainty": "x"})
        self.assertLessEqual(soft, hard)

    def test_uncertainty_object_form_is_accepted(self):
        """uncertainty 允许写成 {"note":…, "safeMax":…}。"""
        m = self.load_module()
        soft, hard, u = m.uncertain_max(
            {"max": 900, "uncertainty": {"note": "时长口径不一", "safeMax": 900}})
        self.assertEqual((soft, hard), (900, 900))
        self.assertIn("时长", u["note"])

    def test_wechat_cards_in_band_warn_and_are_listed(self):
        """12 张落在 9~20 的灰区：WARN + 把 uncertainty 原文写进报告。"""
        with tempfile.TemporaryDirectory() as tmp:
            export = os.path.join(tmp, "export")
            for i in range(12):
                write_png(os.path.join(export, "wechat", "image-text", f"{i:02d}.png"),
                          1080, 1440)
            write_json(os.path.join(export, "wechat", "image-text", "meta.json"),
                       {"title": "标题", "cardTexts": ["x"]})
            rc, out = self.run_check(forms="wechat/image-text", project=tmp)
        self.assertEqual(rc, 0, out)
        self.assertIn("稳妥口径只到 9 张", out)
        self.assertIn("官方口径不一项", out)


# ───────────────────────────────────── plan.json 契约

class TestCheckPlan(Base):
    def write_plan(self, tmp, plan: dict, name="plan.json"):
        path = os.path.join(tmp, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(plan, fh, ensure_ascii=False)
        return path

    def run_plan(self, path):
        proc = subprocess.run([PY, SCRIPT, "--check-plan", path],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout + proc.stderr

    def test_valid_plan_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"wechat": ["mp-article", "image-text", "channels"],
                              "xiaohongshu": ["image-text"]},
                "factSource": "wechat/mp-article",
                "order": ["wechat/mp-article", "wechat/image-text",
                          "xiaohongshu/image-text", "wechat/channels"],
                "audience": "technical",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("结论：通过", out)

    def test_default_plan_path_under_project(self):
        """--check-plan 不带参数时读 <project>/plan.json。"""
        with tempfile.TemporaryDirectory() as tmp:
            self.write_plan(tmp, {
                "selection": {"wechat": ["mp-article"]},
                "factSource": "wechat/mp-article",
                "order": ["wechat/mp-article"],
                "audience": "consumer",
            })
            proc = subprocess.run([PY, SCRIPT, "--check-plan", "--project", tmp],
                                  capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_fact_source_outside_selection_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"wechat": ["mp-article"]},
                "factSource": "xiaohongshu/image-text",
                "order": ["wechat/mp-article"],
                "audience": "technical",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("不在 selection 内", out)

    def test_fact_source_must_come_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"wechat": ["mp-article", "image-text"]},
                "factSource": "wechat/mp-article",
                "order": ["wechat/image-text", "wechat/mp-article"],
                "audience": "technical",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("必须先定事实源再派生", out)

    def test_static_after_dynamic_is_error(self):
        """「先静后动」被破坏时必须报错。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"wechat": ["channels", "mp-article"]},
                "factSource": "wechat/channels",
                "order": ["wechat/channels", "wechat/mp-article"],
                "audience": "technical",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("先静后动", out)

    def test_order_mismatch_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"wechat": ["mp-article", "image-text"]},
                "factSource": "wechat/mp-article",
                "order": ["wechat/mp-article"],
                "audience": "technical",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("order 与 selection 不一致", out)

    def test_duplicate_order_entry_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"wechat": ["mp-article"]},
                "factSource": "wechat/mp-article",
                "order": ["wechat/mp-article", "wechat/mp-article"],
                "audience": "technical",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("重复", out)

    def test_unknown_platform_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"douyin": ["video"]},
                "factSource": "douyin/video",
                "order": ["douyin/video"],
                "audience": "consumer",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("未知平台", out)

    def test_unknown_form_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"wechat": ["podcast"]},
                "factSource": "wechat/podcast",
                "order": ["wechat/podcast"],
                "audience": "consumer",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("没有形式", out)

    def test_missing_selection_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {"audience": "consumer"})
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("缺少 selection", out)

    def test_missing_order_is_warning_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"wechat": ["mp-article"]},
                "factSource": "wechat/mp-article",
                "audience": "consumer",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("没有 order", out)
        # --strict 下 warning 也会失败
        proc = subprocess.run([PY, SCRIPT, "--check-plan", p, "--strict"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stdout)

    def test_broken_json_reports_error_not_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "plan.json")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("{not json")
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("解析失败", out)
        self.assertNotIn("Traceback", out)

    def test_missing_file_reports_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out = self.run_plan(os.path.join(tmp, "nope.json"))
        self.assertEqual(rc, 1, out)
        self.assertIn("找不到", out)

    def test_check_plan_does_not_need_project_export(self):
        """--check-plan 是纯契约校验，不该要求产出目录存在。"""
        with tempfile.TemporaryDirectory() as tmp:
            p = self.write_plan(tmp, {
                "selection": {"generic": ["product-video"]},
                "factSource": "generic/product-video",
                "order": ["generic/product-video"],
                "audience": "executive",
            })
            rc, out = self.run_plan(p)
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)

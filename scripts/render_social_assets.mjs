#!/usr/bin/env node
/**
 * render_social_assets.mjs — 批量导出各平台形式的图卡与封面
 *
 * 复用视频线的渲染管线（无头 Chrome + puppeteer-core），沿用其环境坑：
 *   · headless 必须是布尔 true，不能写 'new'（视频线第 13 条：--headless=new 会被 SIGTERM 杀掉）
 *   · 关沙箱运行，且**前台跑**（视频线第 1 条）
 *   · 渲染实例与 node_modules 可跨工程软链复用（视频线第 16 条）
 *
 * 关键设计：deviceScaleFactor 固定为 1，且在截图后**读回真实像素尺寸**校验。
 *          CSS 写 1080px 不等于出图就是 1080px —— 所有平台线最容易踩的坑。
 *
 * 用法：
 *   node render_social_assets.mjs \
 *     --manifest <content-dir>/work/social-render.json \
 *     --out <content-dir>/export
 *
 *   # 只探测模板画布尺寸，不装 puppeteer、不渲染
 *   node render_social_assets.mjs --probe <skill-dir>/assets/platforms
 *
 * manifest 格式（每条 = 一次元素截图）：
 *   [
 *     {
 *       "page": "wechat/image-text/card.template.html",  // 相对 --root，或绝对路径
 *       "selector": "#card",
 *       "out": "wechat/image-text/01.jpg",
 *       "spec": "wechat/image-text.card",                 // 平台/形式[.子字段]，用于截图后校验
 *       "width": 1080, "height": 1440,                    // 视口；留空则用元素实际尺寸
 *       "format": "jpeg", "quality": 92,
 *       "hideSelectors": ["#safe-center"],
 *       "replace": { ".headline": "冷启动快 2 秒" }        // 可选：截图前替换文案
 *     }
 *   ]
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(__dirname, '..');
const SPECS = JSON.parse(fs.readFileSync(path.join(__dirname, 'social_specs.json'), 'utf8'));

const args = process.argv.slice(2);
const getArg = (name, def = null) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
};
const hasFlag = (name) => args.includes(name);

/** 解析 "平台/形式[.子字段]" 为 specs.json 里的规格对象。 */
function resolveSpec(expr) {
  if (!expr) return null;
  const [fid, ...rest] = String(expr).split('.');
  const [plat, form] = fid.split('/');
  let o = SPECS.platforms?.[plat]?.forms?.[form];
  for (const k of rest) o = o ? o[k] : null;
  return o ?? null;
}

/** 取形式规格本体（不含子字段）。 */
const formSpec = (fid) => resolveSpec(fid);

const CHROME_CANDIDATES = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
];

function findChrome() {
  const explicit = process.env.CHROME_PATH || getArg('--chrome');
  if (explicit) return explicit;
  return CHROME_CANDIDATES.find((p) => fs.existsSync(p)) || null;
}

// ───────────────────────── 纯 node 图片尺寸读取（与 python 脚本同一套判据）

function readImageSize(buf) {
  if (buf.length < 24) return null;
  if (buf.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) {
    return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20), fmt: 'png' };
  }
  const sig6 = buf.slice(0, 6).toString('latin1');
  if (sig6 === 'GIF87a' || sig6 === 'GIF89a') {
    return { w: buf.readUInt16LE(6), h: buf.readUInt16LE(8), fmt: 'gif' };
  }
  if (buf.slice(0, 2).toString('latin1') === 'BM') {
    return { w: Math.abs(buf.readInt32LE(18)), h: Math.abs(buf.readInt32LE(22)), fmt: 'bmp' };
  }
  if (buf.slice(0, 4).toString('latin1') === 'RIFF' && buf.slice(8, 12).toString('latin1') === 'WEBP') {
    const chunk = buf.slice(12, 16).toString('latin1');
    if (chunk === 'VP8X') {
      return {
        w: (buf[24] | (buf[25] << 8) | (buf[26] << 16)) + 1,
        h: (buf[27] | (buf[28] << 8) | (buf[29] << 16)) + 1,
        fmt: 'webp',
      };
    }
    if (chunk === 'VP8 ') {
      return { w: buf.readUInt16LE(26) & 0x3fff, h: buf.readUInt16LE(28) & 0x3fff, fmt: 'webp' };
    }
    if (chunk === 'VP8L') {
      const b = buf.readUInt32LE(21);
      return { w: (b & 0x3fff) + 1, h: ((b >> 14) & 0x3fff) + 1, fmt: 'webp' };
    }
    return null;
  }
  if (buf[0] === 0xff && buf[1] === 0xd8) {
    let off = 2;
    while (off < buf.length - 9) {
      if (buf[off] !== 0xff) { off++; continue; }
      const m = buf[off + 1];
      if (m === 0xd8 || m === 0xd9 || (m >= 0xd0 && m <= 0xd7)) { off += 2; continue; }
      const len = buf.readUInt16BE(off + 2);
      if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) {
        return { w: buf.readUInt16BE(off + 7), h: buf.readUInt16BE(off + 5), fmt: 'jpeg' };
      }
      off += 2 + len;
    }
  }
  return null;
}

const humanBytes = (n) => {
  const u = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return `${i === 0 ? n : n.toFixed(1)}${u[i]}`;
};

// ─────────────────────────────────────────── probe：只测模板画布尺寸

function probe(root) {
  /** 从 :root 里读出 CSS 变量表，用于解析 var(--x)。 */
  const cssVars = (html) => {
    const vars = {};
    const rootRule = html.match(/:root\s*\{([\s\S]*?)\}/);
    if (rootRule) {
      for (const m of rootRule[1].matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) {
        vars[m[1]] = m[2].trim();
      }
    }
    return vars;
  };

  /** 取某选择器的 CSS 规则块，并把 var() 解析成具体值。 */
  const ruleOf = (html, selector) => {
    const stripped = html.replace(/<!--[\s\S]*?-->/g, '');
    const vars = cssVars(stripped);
    const esc = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`(^|[},;\\s])${esc}\\s*(,[^{}]*)?\\{([^}]*)\\}`, 'm');
    const m = stripped.match(re);
    if (!m) return null;
    const block = m[3];
    const resolve = (v) => {
      const t = v.trim();
      const vm = t.match(/^var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+))?\)$/);
      if (vm) return (vars[vm[1]] ?? vm[2] ?? '').trim();
      return t;
    };
    const wRaw = (block.match(/(?:^|[;\s])width\s*:\s*([^;]+)/) || [])[1];
    const hRaw = (block.match(/(?:^|[;\s])height\s*:\s*([^;]+)/) || [])[1];
    if (!wRaw || !hRaw) return null;
    return { w: resolve(wRaw), h: resolve(hRaw), block };
  };

  console.log(`探测模板画布尺寸（来源 ${path.relative(process.cwd(), root)}）\n`);
  const expected = [
    ['wechat/image-text/card.template.html', '#card', formSpec('wechat/image-text').card],
    ['wechat/article/cover-235.template.html', '#cover', formSpec('wechat/mp-article').cover.headline],
    ['wechat/article/cover-11.template.html', '#cover', formSpec('wechat/mp-article').cover.secondary],
    ['wechat/channels/cover-67.template.html', '#cover', formSpec('wechat/channels').cover.vertical],
    ['xiaohongshu/image-text/note.template.html', '#card', formSpec('xiaohongshu/image-text').card],
    ['xiaohongshu/video/cover-34.template.html', '#cover', formSpec('xiaohongshu/video').cover.primary],
  ];
  let bad = 0;
  for (const [rel, sel, spec] of expected) {
    const p = path.join(root, rel);
    if (!fs.existsSync(p)) { console.log(`✗ 缺模板 ${rel}`); bad++; continue; }
    const html = fs.readFileSync(p, 'utf8');
    const rule = ruleOf(html, sel);
    if (!rule) {
      console.log(`! ${rel}：没能从 CSS 里读出 ${sel} 的尺寸（可能用了非 px 单位或未定义），请人工核对`);
      bad++;
      continue;
    }
    const w = parseFloat(rule.w);
    const h = parseFloat(rule.h);
    const ok = w === spec.width && h === spec.height;
    if (!ok) bad++;
    console.log(`${ok ? '✓' : '✗'} ${rel.padEnd(44)} ${sel} = ${rule.w}×${rule.h}` +
      `   规格要求 ${spec.width}×${spec.height} (${spec.ratio})`);
  }
  if (bad) {
    console.log(`\n✗ ${bad} 处与 scripts/social_specs.json 不一致 —— 改规格时请改 specs.json 再同步模板。`);
    process.exit(1);
  }
  console.log('\n✓ 模板画布尺寸与规格表一致。');
}

// ─────────────────────────────────────────── render：元素截图

async function loadPuppeteer() {
  try {
    const mod = await import('puppeteer-core');
    return mod.default ?? mod;
  } catch {
    console.error('缺少 puppeteer-core。请先安装（沿用视频线做法，注意 npm registry 可能被劫持）：');
    console.error('  cd <workspace> && npm init -y && npm i puppeteer-core --registry=https://registry.npmmirror.com --maxsockets 2');
    console.error('  跨工程复用：ln -sfn <other-project>/node_modules ./node_modules');
    console.error('  或用 NODE_PATH 无效的场景（ESM import 不吃 NODE_PATH，必须软链）。');
    process.exit(2);
  }
}

async function render(manifestPath, root, outRoot) {
  const puppeteer = await loadPuppeteer();
  const exe = findChrome();
  if (!exe) {
    console.error('找不到 Chrome/Chromium。用 CHROME_PATH=/path/to/Chrome 指定。');
    process.exit(2);
  }

  const jobs = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const browser = await puppeteer.launch({
    executablePath: exe,
    headless: true,               // 必须布尔 true，不要 'new'（视频线第 13 条）
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none'],
  });

  const results = [];
  try {
    for (const job of jobs) {
      const pagePath = path.isAbsolute(job.page) ? job.page : path.join(root, job.page);
      if (!fs.existsSync(pagePath)) {
        console.log(`✗ ${job.out}：找不到页面 ${pagePath}`);
        results.push({ out: job.out, ok: false, error: 'page-missing' });
        continue;
      }
      const outPath = path.join(outRoot, job.out);
      fs.mkdirSync(path.dirname(outPath), { recursive: true });

      const page = await browser.newPage();
      await page.setViewport({
        width: job.width ?? 1080,
        height: job.height ?? 1440,
        deviceScaleFactor: 1,     // ← 固定 1，保证出图像素 == CSS 像素
      });
      await page.goto('file://' + pagePath, { waitUntil: 'load', timeout: 60000 });
      await page.evaluate(() => document.fonts && document.fonts.ready);

      // 隐藏导引元素（安全区虚线绝不能进成图）
      for (const sel of job.hideSelectors ?? ['#safe-band', '#safe-center', '#safe-169']) {
        await page.$$eval(sel, (els) => els.forEach((e) => e.classList.add('hidden'))).catch(() => {});
      }

      // 可选：截图前替换文案
      if (job.replace) {
        for (const [sel, text] of Object.entries(job.replace)) {
          await page.$$eval(sel, (els, t) => { els.forEach((e) => { e.innerHTML = t; }); }, text).catch(() => {});
        }
      }

      const el = await page.$(job.selector);
      if (!el) {
        console.log(`✗ ${job.out}：找不到元素 ${job.selector}`);
        results.push({ out: job.out, ok: false, error: 'selector-missing' });
        await page.close();
        continue;
      }

      const box = await el.boundingBox();
      const format = job.format ?? 'jpeg';
      await el.screenshot({
        path: outPath,
        type: format,
        ...(format === 'jpeg' ? { quality: job.quality ?? 92 } : {}),
        omitBackground: false,
      });
      await page.close();

      // ── 读回实测像素与体积，与规格核对
      const buf = fs.readFileSync(outPath);
      const size = readImageSize(buf);
      const spec = resolveSpec(job.spec);
      let note = '';
      if (size) {
        const ratio = size.h ? size.w / size.h : 0;
        note = `${size.w}×${size.h} ${humanBytes(buf.length)}`;
        if (box && (Math.abs(box.width - size.w) > 1 || Math.abs(box.height - size.h) > 1)) {
          note += `  ⚠ 元素 ${Math.round(box.width)}×${Math.round(box.height)} ≠ 出图 ${size.w}×${size.h}`;
        }
        if (spec?.ratioValue && Math.abs(ratio - spec.ratioValue) > (spec.ratioTolerance ?? 0.02) * 2.5) {
          note += `  ✗ 比例 ${ratio.toFixed(3)} 偏离规格 ${spec.ratio}`;
        }
        if (spec?.maxBytes && buf.length > spec.maxBytes) {
          note += `  ✗ 体积超过 ${humanBytes(spec.maxBytes)}`;
        }
      } else {
        note = `${humanBytes(buf.length)}  ⚠ 无法解析像素尺寸`;
      }
      console.log(`✓ ${job.out.padEnd(38)} ${note}`);
      results.push({ out: job.out, ok: true, bytes: buf.length, size });
    }
  } finally {
    await browser.close();
  }

  const bad = results.filter((r) => !r.ok);
  const reportPath = path.join(outRoot, 'render-report.json');
  fs.mkdirSync(outRoot, { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify({ generatedAt: new Date().toISOString(), exe, results }, null, 2));
  console.log(`\n共 ${results.length} 项，失败 ${bad.length} 项。报告：${reportPath}`);
  console.log('提醒：本脚本只保证像素尺寸 / 体积 / 比例。视觉与文字可读性必须人工看全尺寸图。');
  process.exit(bad.length ? 1 : 0);
}

// ─────────────────────────────────────────── main

const root = getArg('--root', path.join(SKILL_DIR, 'assets', 'platforms'));
const out = getArg('--out', path.join(process.cwd(), 'export'));
const manifest = getArg('--manifest');

if (hasFlag('--probe') || (!manifest && !hasFlag('--no-probe'))) {
  probe(getArg('--probe') && getArg('--probe') !== 'true' ? getArg('--probe') : root);
  if (!manifest) process.exit(0);
}

if (manifest) {
  render(path.resolve(manifest), root, path.resolve(out)).catch((e) => {
    console.error('渲染失败：', e);
    process.exit(1);
  });
} else {
  console.log('\n未提供 --manifest，只做了尺寸探测。举例：');
  console.log(`  node ${path.relative(process.cwd(), fileURLToPath(import.meta.url))} --manifest ./work/social-render.json --out ./export`);
}

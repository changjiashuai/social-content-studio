// 从 cover/cover.html 导出封面。
// 每个封面是带 data-cover="3x4" | "4x3" | "16x9" 的元素（任意子集），CSS 像素尺寸：
//   3x4 → 1080×1440，4x3 → 1440×1080，16x9 → 1920×1080。导出时按 2× 设备像素比放大。
// node cover.mjs [--scale 2] [--out covers]
import {chromium} from 'playwright';
import {mkdir} from 'node:fs/promises';
import path from 'node:path';

const args = process.argv.slice(2);
const option = (flag, fallback) => { const i = args.indexOf(flag); return i < 0 ? fallback : args[i + 1]; };
const scale = Number(option('--scale', 2));
const out = option('--out', 'covers');
const RATIOS = {'3x4': [1080, 1440], '4x3': [1440, 1080], '16x9': [1920, 1080]};

await mkdir(out, {recursive: true});
const browser = await chromium.launch({headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
try {
  const page = await browser.newPage({viewport: {width: 2000, height: 1600}, deviceScaleFactor: scale});
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('requestfailed', r => errors.push('failed ' + r.url()));

  await page.goto('file://' + path.resolve('cover/cover.html'));
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
  });

  const covers = await page.$$eval('[data-cover]', els => els.map(el => ({id: el.dataset.cover, w: el.offsetWidth, h: el.offsetHeight})));
  if (!covers.length) throw new Error('No [data-cover] elements in cover/cover.html');

  for (const cover of covers) {
    const want = RATIOS[cover.id];
    if (!want) throw new Error(`Unknown cover ratio "${cover.id}" (use 3x4, 4x3, 16x9)`);
    if (cover.w !== want[0] || cover.h !== want[1]) throw new Error(`${cover.id} cover is ${cover.w}×${cover.h}; expected ${want[0]}×${want[1]}`);
    const file = path.join(out, `cover-${cover.id}.png`);
    await page.locator(`[data-cover="${cover.id}"]`).screenshot({path: file});
    console.log(file, `${want[0] * scale}×${want[1] * scale}`);
  }

  if (errors.length) throw new Error(errors.join('\n'));
} finally {
  await browser.close();
}

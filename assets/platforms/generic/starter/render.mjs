// node render.mjs --audio assets/master.wav --output renders/final.mp4 [--from s --to s] [--still t --output f.png]
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
import {readFile, mkdir, mkdtemp, rm} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {serve} from './server.mjs';

const args = process.argv.slice(2);
const option = (flag, fallback) => { const i = args.indexOf(flag); return i < 0 ? fallback : args[i + 1]; };

const plan = JSON.parse(await readFile('plan.json', 'utf8'));
const output = option('--output', 'renders/technical-demo.mp4');
const still = option('--still', null);
const audio = option('--audio', null);
const from = Number(option('--from', 0));
const to = Number(option('--to', plan.duration));
const partial = from > 0 || to < plan.duration;
const silentDemo = args.includes('--silent-demo');

// 用户明确豁免音效时（记了原因），才允许无音轨成片。
const silentApproved = !plan.demo && plan.audioRequired === false
  && typeof plan.audioExceptionReason === 'string' && plan.audioExceptionReason.trim();

if (still === null && !partial && !audio && !silentApproved && !silentDemo) {
  throw new Error('Provide --audio master.wav; silent technical tests require --silent-demo (drafts: pass --from/--to).');
}
if (still === null && !partial && !plan.demo && silentDemo) {
  throw new Error('Silent-demo is only for technical samples.');
}
// 正式成片前确认混音没有过期，且用的确实是那一版 master。
if (still === null && !partial && !plan.demo && plan.audioRequired && plan.sfxRequired !== false) {
  const report = JSON.parse(await readFile('evidence/audio-mix.json', 'utf8'));
  const digest = bytes => createHash('sha256').update(bytes).digest('hex');
  if (report.planSha256 !== digest(await readFile('plan.json'))) throw new Error('Audio mix is stale; remix for the current plan.');
  if (!report.cues?.length) throw new Error('Music-only report: SFX cues missing.');
  if (!audio || digest(await readFile(audio)) !== report.master.sha256) throw new Error('Use the verified BGM + SFX master.');
}

await mkdir(path.dirname(output), {recursive: true});
const {server, url} = await serve();
// SwiftShader 让 WebGL（Three.js 图层）在无头捕获里也能画出来。
const browser = await chromium.launch({headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});

let frames;
try {
  const page = await browser.newPage({viewport: {width: plan.width, height: plan.height}, deviceScaleFactor: 1});
  const failures = [];
  page.on('pageerror', e => failures.push(e.message));
  page.on('requestfailed', r => failures.push('failed ' + r.url()));
  page.on('response', r => { if (r.status() >= 400) failures.push(`${r.status()} ${r.url()}`); });

  await page.goto(url, {waitUntil: 'networkidle'});
  await page.evaluate(async () => {
    await window.__filmReady;
    await document.fonts.ready;
    await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
  });
  if (failures.length) throw new Error(failures.join('\n'));

  if (still !== null) {
    await page.evaluate(t => window.seek(t), Number(still));
    await page.screenshot({path: output});
  } else {
    frames = await mkdtemp(path.join(tmpdir(), 'software-film-'));
    const first = Math.round(from * plan.fps), last = Math.round(to * plan.fps);
    const startedAt = Date.now();
    for (let f = first; f < last; f++) {
      await page.evaluate(t => window.seek(t), f / plan.fps);   // seek 可能等待 driver（点击、弹层）
      await page.screenshot({path: path.join(frames, String(f - first).padStart(6, '0') + '.jpg'), type: 'jpeg', quality: 95});
      if ((f - first) % 300 === 0) console.log(`frame ${f}/${last} · ${((Date.now() - startedAt) / 1000).toFixed(0)}s`);
    }
    if (failures.length) throw new Error(failures.join('\n'));

    const ff = ['-v', 'error', '-y', '-framerate', String(plan.fps), '-i', path.join(frames, '%06d.jpg')];
    if (audio) ff.push('-ss', String(from), '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-af', 'apad', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000');
    ff.push('-t', String(to - from), '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', output);
    await new Promise((resolve, reject) => {
      const proc = spawn('ffmpeg', ff, {stdio: 'inherit'});
      proc.on('error', reject);
      proc.on('close', code => code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}`)));
    });
  }

  console.log(output);
} finally {
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
  if (frames) await rm(frames, {recursive: true, force: true});
}

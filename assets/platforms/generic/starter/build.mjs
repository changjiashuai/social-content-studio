// 把影片打成 dist/：浏览器里挂载产品组件（接口走 src/fake-api.js 的 fixture），
// 一条暂停的 GSAP 主时间轴加各镜头的 render 钩子，逐帧都由 window.seek(t) 驱动。
import {build} from 'esbuild';
import {readFile, writeFile, mkdir, cp, rm} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import integration from './integration.config.mjs';

const plan = JSON.parse(await readFile('plan.json', 'utf8'));
const repoDir = integration.repoDir || plan.repo;

await rm('dist', {recursive: true, force: true});
await mkdir('dist', {recursive: true});

const result = await build({
  entryPoints: ['src/client.jsx'],
  bundle: true, platform: 'browser', format: 'iife', jsx: 'automatic',
  outfile: '.build/client.js', metafile: true, minify: true, legalComments: 'none',
  // 产品的依赖优先从产品自己的 node_modules 解析。
  nodePaths: [...(repoDir ? [path.resolve(repoDir, 'node_modules')] : []), path.resolve('node_modules')],
  // 影片和每个被打进来的产品组件共用同一份 React。
  alias: {
    ...integration.aliases,
    react: path.resolve('node_modules/react'),
    'react-dom': path.resolve('node_modules/react-dom'),
  },
  define: {'process.env.NODE_ENV': '"production"', 'process.env': '{}', 'process.platform': '"darwin"', ...integration.define},
  external: integration.external || [],
  loader: {'.js': 'jsx', '.css': 'css', '.module.css': 'local-css', '.png': 'file', '.jpg': 'file', '.svg': 'file', '.woff': 'file', '.woff2': 'file', '.ttf': 'file', ...integration.loaders},
  assetNames: 'assets/[name]-[hash]',
  logLevel: 'error',
  ...(integration.esbuild || {}),   // 例如用 tsconfigRaw 放宽产品的编译器选项，只为这次显示构建
});

await mkdir('evidence', {recursive: true});
await writeFile('evidence/component-imports.json', JSON.stringify(result.metafile, null, 2));

const bundle = await readFile('.build/client.js', 'utf8');
if (!plan.demo && bundle.includes('data-skill-placeholder')) {
  throw new Error('Technical fixture is still on screen. Connect the actual product feature components before production.');
}

// 样式按固定次序拼进 <style>：默认样式 → 产品自己的样式 → 组件带出的 CSS → 影片层。
let css = '';
for (const file of ['assets/fallback/tokens.css', 'src/product.css', '.build/client.css', 'src/film.css']) {
  if (existsSync(file)) css += '\n' + await readFile(file, 'utf8');
}

await writeFile('dist/index.html', `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${plan.product || 'film'}</title><style>${css}</style><body><div id="film-root"></div><script src="client.js"></script></body></html>`);
await cp('.build/client.js', 'dist/client.js');
if (existsSync('public')) await cp('public', 'dist', {recursive: true});
if (existsSync('assets')) await cp('assets', 'dist/assets', {recursive: true});

// esbuild 的 file loader 产物（图片、字体、CSS 资产）按 .build 下的相对路径搬到 dist。
for (const file of Object.keys(result.metafile.outputs)) {
  if (/\.(?:js|css|map)$/.test(file)) continue;
  const dest = path.join('dist', path.relative('.build', file));
  await mkdir(path.dirname(dest), {recursive: true});
  await cp(file, dest);
}

console.log('Built dist/index.html; imports recorded in evidence/component-imports.json');

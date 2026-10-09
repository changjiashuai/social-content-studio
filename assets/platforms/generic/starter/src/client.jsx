import './fake-api.js';
import React from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {Film} from './film.jsx';
import {seek, frame, master} from './engine.js';
import {SHOT_BUILDERS} from './shots/index.js';

// 产品若用 motion / framer-motion，让它的微动画直接跳到终态，别和影片时钟抢状态：
//   import {MotionGlobalConfig} from 'motion/react'; MotionGlobalConfig.skipAnimations = true;

const root = createRoot(document.getElementById('film-root'));
flushSync(() => root.render(<Film />));

window.seek = seek;
window.__master = master;

// 就绪信号：等布局、字体与 fixture 请求都落定，builder 才能量到真实组件的位置。
window.__filmReady = (async () => {
  await document.fonts.ready;
  await new Promise(resolve => setTimeout(resolve, 800));   // 等 fixture 请求与 effect 收尾
  await frame();
  await frame();

  // builder 可能返回 Promise（例如等一张图 decode 完）。
  // 注意 GSAP 时间轴也是 thenable，而暂停的时间轴永远不会 resolve —— 所以只 await 真 Promise。
  for (const build of Object.values(SHOT_BUILDERS)) {
    const pending = build(master);
    if (pending instanceof Promise) await pending;
  }

  await seek(0);
})();

// 浏览器预览用：按真实时间连续 seek。渲染成片走 render.mjs，不用这两条。
let origin = null, scheduled = null;
window.playFilm = () => {
  cancelAnimationFrame(scheduled);
  origin = null;
  const tick = async stamp => {
    origin ??= stamp;
    await seek((stamp - origin) / 1000);
    scheduled = requestAnimationFrame(tick);
  };
  scheduled = requestAnimationFrame(tick);
};
window.stopFilm = () => cancelAnimationFrame(scheduled);

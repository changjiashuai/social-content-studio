// 影片引擎。画面是「第 t 秒」的纯函数：同一个 t 反复 seek，结果必须完全一致。
//
// 一次 seek 依次推进四层，次序本身就是正确性的一部分：
//   1. 把时间交给 React（flushSync 强制同步重渲染，离散状态才会立刻落定）
//   2. 跑真实交互（打字、点击、弹层），该等的等完
//   3. 定位那条约乎永不动画的 GSAP 主时间轴
//   4. 切镜头显隐，再逐个跑每帧绘制钩子（canvas / WebGL / 依赖时间的样式）
import gsap from 'gsap';
import {flushSync} from 'react-dom';
import plan from '../plan.json';
import {FilmClock} from './film-store.js';

// 影片的时间只由 seek() 决定，绝不跟着墙上时钟走。
gsap.ticker.sleep();

export const master = gsap.timeline({paused: true});
export const shots = plan.shots;
export const shot = id => shots.find(s => s.id === id);

// 两类钩子，各自保持注册顺序。每帧只派发落在镜头窗口附近的那些。
const painters = [];   // onRender：每帧重算的画面
const actors = [];     // onDrive：真实产品交互

/** 注册每帧绘制。fn(localTime, filmTime) —— 镜头内时间与全片时间。 */
export const onRender = (id, fn) => painters.push({s: shot(id), fn});

/** 注册镜头内的真实交互。fn(localTime) 可以返回 Promise（例如等弹层定位完）。 */
export const onDrive = (id, fn) => actors.push({s: shot(id), fn});

/** 等浏览器画一帧。交互之后需要重新布局再截图时用它。 */
export const frame = () => new Promise(resolve => requestAnimationFrame(resolve));

// 镜头在自己的窗口前后各多活这么久：转场才有重叠的余地，进出场不会被硬切断。
const TAIL = 0.8;
const inWindow = (s, t) => t >= s.start - TAIL && t < s.end + TAIL;

export async function seek(seconds) {
  const t = Math.min(Math.max(Number(seconds) || 0, 0), plan.duration - 1 / plan.fps);

  flushSync(() => FilmClock.set(t));

  const waits = actors.filter(a => inWindow(a.s, t)).map(a => a.fn(t - a.s.start)).filter(r => r && r.then);
  if (waits.length) await Promise.all(waits);

  master.seek(t, true);

  for (const s of shots) {
    const section = document.querySelector(`section[data-shot="${s.id}"]`);
    if (section) section.style.visibility = inWindow(s, t) ? 'visible' : 'hidden';
  }

  for (const p of painters) if (inWindow(p.s, t)) p.fn(t - p.s.start, t);

  window.CURRENT_TIME = t;
}

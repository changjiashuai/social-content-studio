import {frame} from '../engine.js';

// 从 onDrive() 里驱动真实的产品组件。这些函数必须幂等：
// 先按镜头内时间算出目标状态，只有和 DOM 不一致时才动手。

/** 给受 React 控制的 input / textarea 赋值，并触发 React 真正监听的 input 事件。 */
export function setFieldValue(field, value) {
  if (!field || field.value === value) return;
  const proto = field instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, 'value').set.call(field, value);
  field.dispatchEvent(new Event('input', {bubbles: true}));
}

/** 从 at 起按 cps 字/秒打字，clearAt 之后清空。返回该时刻应该显示的文本。 */
export function typed(text, local, at, cps, clearAt = Infinity) {
  if (local < at || local >= clearAt) return '';
  const chars = Array.from(text);
  return chars.slice(0, Math.min(chars.length, Math.floor((local - at) * cps) + 1)).join('');
}

/** 需要真实点击才能开合的菜单 / 弹层。isOpen() 读 DOM，toggle() 执行点击。 */
export async function ensureOpen(want, isOpen, toggle) {
  if (want === isOpen()) return;
  toggle();
  await frame();
  await frame();   // 给 floating-ui 之类的定位留两帧
}

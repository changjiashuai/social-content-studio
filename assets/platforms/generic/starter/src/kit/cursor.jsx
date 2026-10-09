import React from 'react';

// 指针浮层：属于影片层，不是产品里的元素。放进被缩放的产品根内部，它才会跟着产品的镜头走；
// 位置由 driver 调 paintCursor() 写入。
export function Cursor({id, color = '#111', stroke = '#fff'}) {
  return <div className="film-cursor" data-cursor={id}>
    <svg viewBox="0 0 24 24" width="32" height="32"><path d="M5 2.5v17.2l4.6-4.3 2.9 6.6 2.8-1.2-2.8-6.5h6.3z" fill={color} stroke={stroke} strokeWidth="1.3" strokeLinejoin="round" /></svg>
    <i className="film-ripple" />
  </div>;
}

const smooth = x => (x < 0.5 ? 16 * x ** 5 : 1 - Math.pow(-2 * x + 2, 5) / 2);

/** keys: [{at,x,y}]（产品像素坐标）；clicks: [t]（点击时刻）；show: [from,to]。
 *  全部只依赖镜头内时间，所以前后跳转都成立。 */
export function paintCursor(el, local, keys, clicks = [], show = [-1, 1e9]) {
  if (!el) return;
  const visible = local >= show[0] && local < show[1] && keys.length;
  el.style.opacity = visible ? '1' : '0';
  if (!visible) return;

  let pos = keys[0];
  for (let i = 0; i < keys.length - 1; i++) {
    const from = keys[i], to = keys[i + 1];
    if (local >= to.at) { pos = to; continue; }
    if (local >= from.at) {
      const u = smooth((local - from.at) / (to.at - from.at));
      pos = {x: from.x + (to.x - from.x) * u, y: from.y + (to.y - from.y) * u};
    }
    break;
  }

  const sinceClick = clicks.map(c => local - c).filter(d => d >= 0 && d < 0.45)[0];
  el.style.transform = `translate(${pos.x - 6}px, ${pos.y - 3}px)`;

  // 点击后 0.18s 内指针轻微回缩，0.45s 内涟漪扩散淡出。
  el.querySelector('svg').style.transform = sinceClick !== undefined && sinceClick < 0.18 ? `scale(${0.84 + 0.16 * sinceClick / 0.18})` : '';
  const ripple = el.querySelector('.film-ripple');
  ripple.style.opacity = sinceClick !== undefined ? String(1 - sinceClick / 0.45) : '0';
  ripple.style.transform = sinceClick !== undefined ? `scale(${0.4 + sinceClick * 3})` : '';
}

import React from 'react';

// 把文字拆成一串 span，交给 GSAP 做错落入场。
// 拆法按片子的语气选：'ch' 逐字、'word' 逐词、'line' 按 \n 逐行。
export function Split({text, by = 'ch', className = '', lang}) {
  const units = by === 'line' ? text.split('\n') : by === 'word' ? text.split(/(\s+)/) : Array.from(text);
  return <span className={'split ' + className} lang={lang}>
    {units.map((u, i) => <span key={i} className={'u u-' + by}>{u === ' ' ? ' ' : u}</span>)}
  </span>;
}

/** 把 root 里的拆分单元从 from 状态错落推到静止态。from 状态属于片子的判断，不在这里定。 */
export function reveal(timeline, root, at, {from = {opacity: 0, y: 24, filter: 'blur(12px)'}, dur = 0.7, stagger = 0.035, ease = 'expo.out'} = {}) {
  const units = root.querySelectorAll('.u');
  const to = Object.fromEntries(Object.keys(from).map(k => [k, k === 'filter' ? 'blur(0px)' : k === 'opacity' || k === 'scale' ? 1 : 0]));
  timeline.fromTo(units, from, {...to, duration: dur, ease, stagger}, at);
}

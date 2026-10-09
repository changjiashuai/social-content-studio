import React from 'react';
import {Split, reveal} from '../kit/text.jsx';
import {shot} from '../engine.js';
import {FeatureVisual} from '../presentations.jsx';

// 技术样片：只用来验证 mount → 时间轴 → seek → 抓帧这条链路能通。
// 它刻意没有画面方向。正式镜头的每一镜都从 DIRECTION.md 推导另写
// （见 references/platforms/generic/product-video/direction.md）。
const pick = (id, selector) => document.querySelector(`section[data-shot="${id}"] ${selector}`);

export function TitleView({shot: s}) {
  return <div className="sample-title">
    <div className="en"><Split text={s.headlineEn || ''} lang="en" /></div>
    <div className="zh"><Split text={s.headline} lang="zh-CN" /></div>
  </div>;
}

export function ComponentView() {
  return <div className="sample-component"><div className="sample-cam"><FeatureVisual /></div></div>;
}

export const buildTitle = id => timeline => {
  const s = shot(id);
  timeline.set(document.querySelector(`section[data-shot="${id}"]`), {opacity: 1}, s.start);
  reveal(timeline, pick(id, '.en'), s.start + 0.1);
  reveal(timeline, pick(id, '.zh'), s.start + 0.4, {stagger: 0.05});
};

export const buildComponent = id => timeline => {
  const s = shot(id);
  timeline.set(document.querySelector(`section[data-shot="${id}"]`), {opacity: 1}, s.start);
  timeline.fromTo(pick(id, '.sample-cam'), {scale: 0.9, opacity: 0}, {scale: 1, opacity: 1, duration: 0.8, ease: 'expo.out'}, s.start);
  timeline.to(pick(id, '.sample-cam'), {scale: 1.04, duration: s.end - s.start - 0.8, ease: 'none'}, s.start + 0.8);
};

// Frame Kit「纸墨」默认样式 —— 展示组件
// Copyright (C) 2026 changjiashuai · AGPL-3.0（随本 skill 主协议）
//
// 这四个导出名（CardFrame / CardSurface / FilmButton / FilmBadge）是起步工程注入的
// fixture 依赖的**兼容接口**，请勿改名或删除。实现为本包原创。
// 组件只负责给出类名并透传其余 DOM 属性，不注入业务布局、不依赖 Tailwind。

import React from 'react';

const cx = (...parts) => parts.filter(Boolean).join(' ');

/** 纸叠：投影与圆角层。内层请放 CardSurface。tone="ink" 可局部转深色。 */
export function CardFrame({ className, tone, children, ...rest }) {
  return (
    <div {...rest} data-tone={tone} className={cx('film-card-frame', className)}>
      {children}
    </div>
  );
}

/** 纸面：可见的承载体，负责底色、描边与裁切。 */
export function CardSurface({ className, tone, children, ...rest }) {
  return (
    <div {...rest} data-tone={tone} className={cx('film-card-surface', className)}>
      {children}
    </div>
  );
}

/** 按钮。variant: default | secondary | outline | ghost */
export function FilmButton({ variant = 'default', type = 'button', className, children, ...rest }) {
  return (
    <button {...rest} type={type} data-variant={variant} className={cx('film-button', className)}>
      {children}
    </button>
  );
}

/** 徽标。variant: default | accent */
export function FilmBadge({ variant = 'default', className, children, ...rest }) {
  return (
    <span {...rest} data-variant={variant} className={cx('film-badge', className)}>
      {children}
    </span>
  );
}

/** 强调短线：用于章节起头或标题上方的一笔点缀。 */
export function FilmRule({ className, ...rest }) {
  return <hr {...rest} className={cx('film-rule', className)} />;
}

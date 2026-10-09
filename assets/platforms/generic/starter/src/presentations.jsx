import React from 'react';

// 技术占位，不是对目标产品的任何主张。接真功能时：换上仓库里真实的组件
// （在 ProductContext 里 client-mounted 挂载），并去掉 placeholder 标记。
export function FeatureVisual() {
  return <div className="neutral-fixture" data-skill-placeholder="true">
    <div className="fx-label">COMPONENT ADAPTER</div>
    <h2>把真实组件放到这里</h2>
    <p>接入产品组件后，用影片时钟驱动它的真实状态。</p>
  </div>;
}

import React from 'react';

// 显示适配层：产品 App 外壳平时提供的那些 provider（i18n、主题、tooltip、路由 / 面板上下文……）。
// 读产品的根布局和外壳，只把上镜组件真正要用的那几个照过来，全部用静态值。
// 需要产品的暗色主题时给 dark 传 true。
export function ProductContext({children, dark = false, className = ''}) {
  return <div className={'product-root ' + (dark ? 'dark ' : '') + className}>{children}</div>;
}

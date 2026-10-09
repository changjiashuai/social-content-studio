import React from 'react';

// next/image → 普通 <img>：片子里没有图片优化器。
export default function Image({src, alt = '', width, height, className, style, fill, priority, unoptimized, ...rest}) {
  const url = typeof src === 'object' ? src.src : src;
  const sized = fill
    ? {position: 'absolute', inset: 0, width: '100%', height: '100%', ...style}
    : style;
  return <img src={url} alt={alt} width={fill ? undefined : width} height={fill ? undefined : height} className={className} style={sized} {...rest} />;
}

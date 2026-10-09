// 量真实组件：推镜头的落点、光标走的路径都从这里取数。

/** el 的中心。沿 offsetParent 链累加，不受 transform 影响，结果在 root 自己的坐标系里。 */
export function offsetCenter(el, root) {
  let x = 0, y = 0, node = el;
  while (node && node !== root) {
    x += node.offsetLeft;
    y += node.offsetTop;
    node = node.offsetParent;
  }
  return {x: x + el.offsetWidth / 2, y: y + el.offsetHeight / 2};
}

/** el 在影片时间 t 真正出现在屏幕的哪里（含 3D 倾斜、透视、缩放）。
 *  做法：把已搭好的时间轴 seek 到 t，量一次，再退回 0。用来瞄推镜头的终点。 */
export function screenCenterAt(timeline, t, el) {
  timeline.seek(t, true);
  const box = el.getBoundingClientRect();
  timeline.seek(0, true);
  return {x: box.left + box.width / 2, y: box.top + box.height / 2};
}

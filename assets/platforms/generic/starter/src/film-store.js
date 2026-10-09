// 影片时钟。组件通过它读「现在第几秒」，并且只在自己选中的离散值变化时重渲染
// —— 比如已经露出几步工具调用、回复多了几个字。
import {useSyncExternalStore, createContext, useContext} from 'react';

let now = 0;
const watchers = new Set();

export const FilmClock = {
  get: () => now,
  set(t) {
    now = t;
    for (const notify of watchers) notify();
  },
  subscribe(notify) {
    watchers.add(notify);
    return () => watchers.delete(notify);
  },
};

// 每个镜头把自己的窗口挂上来，组件就能换算镜头内时间。
export const ShotContext = createContext({start: 0, end: 0});

/** 从镜头内时间取出一个原始值。取值的粒度决定重渲染的频率。 */
export function useShotState(select) {
  const {start} = useContext(ShotContext);
  return useSyncExternalStore(FilmClock.subscribe, () => select(now - start), () => select(0));
}

/** times 里已经过了几个时刻 —— 直接当「第几步」用。 */
export const stageAt = (local, times) => times.filter(at => local >= at).length;

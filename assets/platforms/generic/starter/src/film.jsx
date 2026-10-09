import React from 'react';
import {ShotContext} from './film-store.js';
import {shots} from './engine.js';
import {SHOT_VIEWS} from './shots/index.js';

// 每个镜头一层，按 plan.json 的顺序叠起来：后面的盖住前面的。
export function Film() {
  return <main id="film" className="film-theme">
    {shots.map((s, order) => {
      const View = SHOT_VIEWS[s.id];
      if (!View) throw new Error(`No view for shot "${s.id}" in src/shots/index.js`);
      return <section key={s.id} data-shot={s.id} className={'shot shot-' + s.id} style={{zIndex: order + 1}}>
        <ShotContext.Provider value={s}><View shot={s} /></ShotContext.Provider>
      </section>;
    })}
  </main>;
}

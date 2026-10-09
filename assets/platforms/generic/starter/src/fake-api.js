// 影片的确定性浏览器运行时。必须在任何产品模块之前 import。
//   - 固定时钟 + 定种子的 Math.random（按时段的问候语、随机挑选都会稳定下来）
//   - 把产品 API 路由接到 fixture，真实组件就能离线跑完自己的 effect
//   - EventSource / WebSocket 静音替身（不建任何流式连接）
import {API_FIXTURES, API_PREFIXES} from './fixtures/api.js';

// 挑一个适合这个故事的时刻。
const FROZEN_NOW = new Date('2026-01-15T10:00:00+08:00').getTime();
const NativeDate = Date;
class FilmDate extends NativeDate {
  constructor(...args) { args.length ? super(...args) : super(FROZEN_NOW); }
  static now() { return FROZEN_NOW; }
}
globalThis.Date = FilmDate;

// Park–Miller，种子固定 —— 同一个 t 永远算出同一串随机数。
let seed = 20260115;
Math.random = () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

try { localStorage.clear(); sessionStorage.clear(); } catch {}

// 实际请求过的路径会记在这里：stills.mjs 会打印出来，用来查缺哪些 fixture。
window.__filmApiLog = [];

const asJson = (data, status = 200) => new Response(JSON.stringify(data), {status, headers: {'Content-Type': 'application/json'}});
const passThrough = window.fetch.bind(window);

window.fetch = async (input, init) => {
  const url = new URL(typeof input === 'string' ? input : input.url, location.href);
  if (!API_PREFIXES.some(prefix => url.pathname.startsWith(prefix))) return passThrough(input, init);
  window.__filmApiLog.push(url.pathname + url.search);
  const fixture = API_FIXTURES[url.pathname];
  if (fixture === undefined) return asJson({});
  return asJson(typeof fixture === 'function' ? fixture(url, init) : fixture);
};

// 片子里不需要真的连流：给一个什么都不做的替身就够了。
class Muted {
  constructor() { this.readyState = 0; }
  close() {}
  send() {}
  addEventListener() {}
  removeEventListener() {}
}
window.EventSource = Muted;
window.WebSocket = Muted;

import http from 'node:http';
import path from 'node:path';
import {readFile, realpath} from 'node:fs/promises';

const MIME = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff': 'font/woff',
  '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.json': 'application/json',
  '.wav': 'audio/wav', '.mp3': 'audio/mpeg',
};

/** 只服务 dist/ 的静态服务器。port 传 0 交给系统分配，返回真实 url。 */
export async function serve(port = 0) {
  const root = await realpath('dist');
  const server = http.createServer(async (req, res) => {
    try {
      const rel = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      // 先 realpath 再比前缀：符号链接与 ../ 都逃不出 dist/。
      const file = await realpath(path.join(root, rel === '/' ? 'index.html' : rel));
      if (file !== root && !file.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
      const body = await readFile(file);
      res.writeHead(200, {'Content-Type': MIME[path.extname(file)] || 'application/octet-stream'});
      res.end(body);
    } catch {
      res.writeHead(404); res.end('Not found');
    }
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(port, '127.0.0.1', resolve); });
  return {server, url: `http://127.0.0.1:${server.address().port}`};
}

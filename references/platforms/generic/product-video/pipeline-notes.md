# 本机实测管线与环境坑

> 本分册记录**已实跑验证过**的渲染 / 编码 / 音频管线，以及实际踩过的环境坑。
> 第 2 节的 28 条**对全部平台包适用**——平台线与视频线共用同一条渲染与编码底座。结论来自两支完整跑通的片子，不是设想。
> 首次制作前先读一遍第 2 节；渲染中途出怪现象时回来查。

**案例**：2026-10-02 `mai-promo`（24s / 1080p25 产品宣传片）；2026-10-06 `beam-news`（28s / 1080p25 六幕新闻短片，全程中文配音 + 中文硬字幕、官方图表矢量化重建、响度归一化 + 逐句时序验收）。

---

## 1. 已验证的管线

- **工程结构**：`<promo>/video/index.html`（1920×1080 舞台 + GSAP 主时间轴，`gsap.timeline({paused:true})` 由渲染器 seek）+ `render.mjs` + `audio.py`。
- **封面**：`<promo>/cover/cover.html` 把 3:4 与 4:3 两张卡片放进同一页（`display:flex` 并排），`render_cover.cjs` 用 `viewport` 放大到能容纳全部卡片、再对每个元素 `el.screenshot()` 分别出图——一次渲染出齐所有画幅，且改一处即两张同步；`check_cover.py` 做尺寸 / 边距 / 缩略图自检。做法与坑见第 25–28 条。
- **渲染** `render.mjs`：puppeteer-core 连本机 Chrome（`/Applications/Google Chrome.app/...`），`page.evaluate(() => tl.seek(t).progress())` 后 `page.screenshot({type:'jpeg',quality:90})` 存 `frames/f%05d.jpg`。600 帧 ≈ 27s。
- **编码**：`ffmpeg -framerate 25 -i frames/f%05d.jpg -i mix.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k -shortest out.mp4`。
- **音频**：numpy 合成（pad 长音 + 琶音 + 心跳脉冲 + 场景边界铃音 + whoosh/tick/ding），WAV 写盘后由 ffmpeg 混流；响度目标 mean ≈ -15dB / max ≈ -1.3dB。

## 2. 环境坑（28 条）

### 渲染与浏览器

1. Chrome/puppeteer 必须**关沙箱**运行（代码签名克隆与临时 profile 写入会被沙箱拦截），渲染命令加 `dangerouslyDisableSandbox` 且**前台跑**——后台任务会被沙箱杀掉。
2. 重渲染前 `rm -f frames/*.jpg`，否则残留帧混进新片。
3. 场景转场两段动画重叠 ≥0.4s，否则中间出空白帧；审片时抽转场时刻（如 S1 出点 ±0.2s）单独看帧。
9. 渲染器 seek 后**切勿链 `.progress(1)`**——progress 是 setter，会把时间轴强制跳到片尾，所有帧都渲染成末状态。只 `tl.seek(t)` 即可。
13. **Chrome `--headless=new` 在本沙箱会被 SIGTERM(137) 杀掉**，`--headless`（旧模式）正常。puppeteer-core 用 `headless: true`（布尔），不要写 `'new'`，否则渲染脚本静默失败。
23. **计数滚动要看小整数**：`0 → 1` 这类小目标用 tween 滚动时，前 40–50% 时间会显示 `0`，落成事实错误的读数（如「0M 上下文窗口」）。`to <= 2` 的计数器不要滚动，直接随块入场呈现终值。

### 网络与环境

4. `npm install` 偶发被杀，加 `--maxsockets 2` 重试。
6. GitHub 被代理墙死时（git / curl / 镜像全 502），拿不到仓库文件；此时改用 WebFetch 取网页文档，npm registry 通常仍可达，puppeteer-core / gsap 可正常装。
7. npm registry 本身也可能被劫持（2026-10-03 实测：`registry.npmjs.org` 返回 m.baidu.com 的 HTML，报 "invalid json response body"），此时追加 `--registry=https://registry.npmmirror.com` 可正常安装。
16. `NODE_PATH` 对 **ESM import 无效**。跨工程复用 `node_modules` 用软链：`ln -sfn <other-project>/node_modules ./node_modules`。
17. zsh 两个坑：`rm -f frames/*.png` 无匹配时直接报 `no matches found` 并**中断整条 `&&` 链**（先 `setopt +o nomatch`）；`for x in $var` **不做词分割**（多值列表用数组或文件 + `while read`）。

### 素材获取

5. 站点真实素材直接 curl 下载原站 uploads 资产（webp→png 用 magick 转），色板用 `magick ... -format "%[pixel:p{x,y}]"` 采样，比目测准。
8. WebFetch 对目标站点也可能 fetch failed（代理只放行浏览器流量）。替代方案：Chrome headless `--screenshot` 截首屏，puppeteer-core 截整页 / 按元素截图，页内 `fetch()` + FileReader base64 可绕过代理下载站点图片资产；正文用 `document.body.innerText` 落盘。
12. 素材图若带原站 UI 残留（如预览 iframe 的按钮），优先用画面内标签精确覆盖（按原图坐标换算缩放后位置），或换 crop 区域。
14. **无头 Chrome 一联网就被杀**（截图外网必挂）。要拿站点素材改用 `curl`：本机 curl 能直连多数站点（GitHub 仍 502）。`reflection.ai` 类 Next.js 站可直接抓 HTML，再 grep `--color-*` 拿到全套设计变量、grep 图片 URL 拿到原图，比截图重多了。
15. Sanity CDN（`cdn.sanity.io`）图片 URL **必须带完整文件名含扩展名**，加 `?w=` / `?fm=` 查询参数会返回 400「Invalid filename」。

### 画面、文案与语音

10. 场景转场**不要用半透明交叉淡化**：两幕文字会叠印成糊。用「不透明面板滑动盖入 + 旧幕视差平移」（scene 自带不透明底色与网格，DOM 顺序即层叠顺序）；转场手法可在轴向上变化（右滑 / 底部滑入）。
11. macOS `say -v Tingting` 语速 -r 200→210 无效（饱和），长台词超窗口时优先扩该幕时长而非加速；`say` 输出无尾部静音，`silencedetect` 只能测到句中停顿。
19. 官方图表当素材时，其内部标注在视频尺度下常只有 11–13px（低于硬约束 22px）。分镜阶段用官方 PNG 占位，成片阶段**按官方数据点与配色重建矢量图**并叠加中文标注引线；若用户坚持用原图，就用放大裁切单面板缓解。
24. 定稿前务必重渲染关键帧确认每一处修补真的生效——改 CSS/JS 后不重渲染就交付，是这类管线最容易漏的一步。

### 版面与安全边距自检

18. **版面自检脚本化**：硬字幕条的 y 范围不要凭 CSS 的 `bottom` 值估算——它由 `font-size × line-height + padding` 决定（32px/1.4/13px 上下 padding = 条高 ≈71px），必须扫帧实测。判定别用「整屏近黑像素行」：深底幕整屏都是暗的，会把背景认成字幕条。可靠判据是**中央区域存在跨度 400–800px、密度 >0.45 的暗块，且纵向连续 ≥26 行**（见 `check.py` 的 `_bar_row/find_bar`）。量到条体顶边后，再与该幕内容的最低行比对，两者必须留出净空。长图核对用 PIL 裁顶部 40%／底部 38% 再缩到 1100–1280px 宽，可快速核实官方图表标题与字幕 / 数字条是否撞车。
20. **安全边距自检要跳过转场与入场位移帧**：面板滑入时元素正从画外进入（如 `x:-30` 的滑入块），会把左 / 右 96px 判成越界。只测「各幕开场 2.2s 之后、收尾 0.9s 之前」的稳态帧；深底幕若背景是官方满幅主视觉（必然铺满画布），该幕不做像素判定，改人工看全尺寸帧。
27. **判断「安全边距内有没有文字」别数纸白像素**：官方点阵的白点也是纸白，会大量误报。可靠判据是**纸白像素的横向连续段长度**（文字笔画 ≥18px，点阵单点仅 3–6px）。另外通栏 HUD 是设计上贴顶的页眉元素，必须单独排除，不能算越界。

### 音频与响度

21. **只做峰值归一化的混音会停在 -22 LUFS 左右**，比网络视频常见的 -14~-16 LUFS 明显偏小。必须再过一道 `ffmpeg loudnorm`（两遍：先 `print_format=json` 测，再带 `measured_*` + `linear=true` 应用），目标 I=-15 / TP=-1.5。两个附带坑：`loudnorm` 默认会把输出提到 **192kHz**（文件体积 ×4.35），必须显式 `-ar 44100`；`ebur128` 会周期性打印摘要，解析必须取**最后一条**（`rfind('I:')` / `rfind('Peak:')`），否则拿到的是中途值。
22. **旁白与配乐的配比要用 500–4000Hz 可懂度频段判**。全带 RMS 会被配乐的低频 bed 与 kick 拉高，看起来「配乐比人声还响」，实际人声可懂度毫无损失（本片全带只差 1.5dB，可懂度频段差 18dB）。另外取「纯配乐间隙」做基准时，要排除片头淡入段与音乐收束段（否则均值被静音拉低几十 dB）。混音前把 `music/vox/sfx` 三条 stem 落盘，事后才能同基准复核。

### 封面

25. **做封面先测「官方满幅主视觉」的底色。** 若它与成片主色完全一致（beam-news 实测 `key_rings.png` 底色 = `#203409` = `--forest`），就可以任意 `background-size` / `background-position` 裁剪位移而**不出现接缝**——留白处由 `background-color` 自然补齐。这让「一张横向主视觉改出 3:4 / 4:3 / 16:9 三个画幅」变得很省事：竖版取局部（如只取最大的那个图形本体），横版 `cover` 取景即可。
26. **深底封面必须给 HUD 区单独压暗**。白色 HUD 直接压在官方亮色点阵 / 纹理上几乎不可读；加一层 ~210px 高的顶部渐变 scrim（成片里的 `.hudscrim`）才干净。做封面时最容易忘的就是这个——因为封面没有动画，不会自动「入场到干净状态」。
28. **要让主视觉在文字区之前「收束淡出」，用 `mask-image` 而不是加暗色遮罩。** 遮罩会把背景压成非纯色、留下灰蒙蒙的痕迹；`mask-image: linear-gradient(180deg,#000 0%,#000 30%,rgba(0,0,0,.55) 38%,transparent 52%)` 让图案真正淡出到 0，下层纯色背景直接露出来，边缘干净。另外竖版复用横向主视觉时，**取景边界要避开相邻图形的残影**（beam-news 的 `key_rings.png` 是「左小圆→右大圆」序列，取景落在中圆附近时左边会露出一块暗色残影，右移到只含大圆本体才干净）。

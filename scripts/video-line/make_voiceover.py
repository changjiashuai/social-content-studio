#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成配音：优先 edge-tts，绝不回退到系统机器音。

用法：
  # 先看本机有哪些 TTS 可用、edge-tts 有哪些音色
  python3 make_voiceover.py --doctor
  python3 make_voiceover.py --list-voices

  # 按 plan.json 的 voiceover 配置生成
  python3 make_voiceover.py <video-dir>/plan.json

  # 指定音色与参数
  python3 make_voiceover.py <video-dir>/plan.json --voice zh-CN-YunjianNeural --rate=-5%

退出码：
  0  成功
  1  失败（edge-tts 报错、文案缺失等）
  2  用法问题
  3  需要用户决定：没有可用的合适 TTS（此时不要自行降级到 say）
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 明确禁止的系统机器音：这些即使装上也不用。
FORBIDDEN_ENGINES = {
    'say': 'macOS say（系统机器音）',
    'espeak': 'eSpeak（拼接式合成）',
    'festival': 'Festival',
    'pico2wave': 'pico2wave',
}
FORBIDDEN_HINT = 'espeak|festival|pico2wave'

DEFAULT_VOICE = 'zh-CN-XiaoxiaoNeural'
EXIT_NEEDS_DECISION = 3


def run(cmd, timeout=60, input_text=None):
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, input=input_text)


def have_edge_tts():
    """返回 (是否可用, 版本或错误信息)。"""
    try:
        proc = run([sys.executable, '-c',
                    'import edge_tts; print(getattr(edge_tts, "__version__", "unknown"))'], timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f'{type(exc).__name__}: {exc}'
    if proc.returncode != 0:
        return False, (proc.stderr or '').strip().splitlines()[-1:] and (proc.stderr or '').strip().splitlines()[-1] or 'import failed'
    return True, proc.stdout.strip()


def list_voices(proxy=None):
    """列出 edge-tts 音色。返回 [(short_name, gender, locale)]；失败返回 None。"""
    cmd = [sys.executable, '-m', 'edge_tts', '--list-voices']
    if proxy:
        cmd += ['--proxy', proxy]
    cmd = [sys.executable, '-c', (
        'import asyncio, edge_tts\n'
        'async def m():\n'
        '    vs = await edge_tts.list_voices()\n'
        '    for v in sorted(vs, key=lambda x: x["ShortName"]):\n'
        '        print(v["ShortName"], v.get("Gender",""), v.get("Locale",""))\n'
        'asyncio.run(m())\n')]
    try:
        proc = run(cmd, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    out = []
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and 'Neural' in parts[0]:
            out.append((parts[0], parts[1], parts[2]))
    return out or None


def forbidden_hits():
    """本机装了的、但我们不用的机器音引擎。"""
    hits = []
    for name, label in FORBIDDEN_ENGINES.items():
        if shutil.which(name):
            hits.append(label)
    return hits


def doctor():
    """环境体检：把可用性与禁止项一次说清。"""
    print('== 配音环境体检 ==')
    ok, info = have_edge_tts()
    if ok:
        print(f'[可用] edge-tts {info}（首选；合成需要联网）')
    else:
        print(f'[不可用] edge-tts：{info}')
        print('       安装：pip3 install edge-tts')

    if ok:
        voices = list_voices()
        if voices:
            zh = [v for v in voices if v[0].startswith('zh-')]
            print(f'         当前可用音色 {len(voices)} 个，其中中文 {len(zh)} 个')
        else:
            print('         音色列表拉取失败（可能无网络或区域限制）')

    hits = forbidden_hits()
    if hits:
        print('[禁用] 本机已安装这些系统机器音，本项目一律不用：' + '、'.join(hits))
        print('       没有配音优于机器音；落不到 edge-tts 时按 voiceover.md §6 问用户。')

    if not ok:
        print('\n结论：第 1 级不可用。请按 voiceover.md §1 落到第 2 级'
              '（其他免费 TTS），仍无合适者则暂停并让用户决定（退出码 3）。')
    return 0 if ok else EXIT_NEEDS_DECISION


def read_plan(plan_path):
    try:
        with open(plan_path, encoding='utf-8') as fh:
            return json.load(fh)
    except FileNotFoundError:
        print(f'找不到 plan.json：{plan_path}', file=sys.stderr)
        return None
    except (OSError, ValueError) as exc:
        print(f'plan.json 解析失败：{exc}', file=sys.stderr)
        return None


def collect_lines(plan):
    """从 plan.json 的镜头里取配音文案。

    优先 shots[].voiceoverText；其次 headline + description。
    跳过空文本。
    """
    lines = []
    for shot in plan.get('shots', []) if isinstance(plan.get('shots'), list) else []:
        if not isinstance(shot, dict):
            continue
        text = shot.get('voiceoverText')
        if not isinstance(text, str) or not text.strip():
            parts = [shot.get(k) for k in ('headline', 'description')]
            text = '。'.join(str(p).strip() for p in parts if isinstance(p, str) and p.strip())
        if text and text.strip():
            lines.append({'id': shot.get('id', 'shot'),
                          'start': shot.get('start'),
                          'end': shot.get('end'),
                          'text': text.strip()})
    return lines


def synth(text, voice, rate, pitch, media_path, subs_path, proxy=None):
    """调用 edge-tts 生成一条音频与字幕。返回 (ok, 错误信息)。"""
    # 注意：--rate/--pitch 的值以 - 或 + 开头，必须用 --k=v 形式，
    # 否则 argparse 会把 '-5%' 当成选项名。
    cmd = [sys.executable, '-m', 'edge_tts',
           '--text', text,
           '--voice', voice,
           f'--rate={rate}',
           f'--pitch={pitch}',
           '--write-media', str(media_path),
           '--write-subtitles', str(subs_path),
           '--no-progress']
    if proxy:
        cmd += ['--proxy', proxy]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f'{type(exc).__name__}: {exc}'
    if proc.returncode != 0:
        err = (proc.stderr or '').strip().splitlines()
        return False, err[-1] if err else f'exit {proc.returncode}'
    if not media_path.is_file() or media_path.stat().st_size == 0:
        return False, '输出文件为空'
    return True, ''


def to_wav(src, dst, rate=48000):
    """把 edge-tts 的 mp3 转成 48kHz 单声道 PCM wav。没有 ffmpeg 时直接拷贝并警告。"""
    if not shutil.which('ffmpeg'):
        shutil.copyfile(src, dst)
        return True, 'no ffmpeg; copied as-is (may be mp3 in a .wav name)'
    try:
        proc = run(['ffmpeg', '-v', 'error', '-y', '-i', str(src),
                    '-ar', str(rate), '-ac', '1', '-c:a', 'pcm_s16le', str(dst)], timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f'{type(exc).__name__}: {exc}'
    if proc.returncode != 0:
        err = (proc.stderr or '').strip().splitlines()
        return False, err[-1] if err else f'exit {proc.returncode}'
    return True, ''


def probe_duration(path):
    if not shutil.which('ffprobe'):
        return None
    try:
        proc = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'csv=p=0', str(path)], timeout=30)
        return round(float(proc.stdout.strip()), 3) if proc.returncode == 0 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('plan', nargs='?', help='视频工程的 plan.json')
    ap.add_argument('--doctor', action='store_true', help='只做环境体检')
    ap.add_argument('--list-voices', action='store_true', help='列出 edge-tts 可用音色')
    ap.add_argument('--voice', help='音色 ShortName，覆盖 plan.json 里的设置')
    ap.add_argument('--rate', default=None, help='例如 -5%% 或 +8%%')
    ap.add_argument('--pitch', default=None, help='例如 -2Hz')
    ap.add_argument('--proxy', default=None, help='edge-tts 走代理')
    args = ap.parse_args()

    if args.doctor:
        return doctor()

    if args.list_voices:
        ok, info = have_edge_tts()
        if not ok:
            print(f'edge-tts 不可用：{info}', file=sys.stderr)
            return EXIT_NEEDS_DECISION
        voices = list_voices(args.proxy)
        if not voices:
            print('音色列表拉取失败（无网络 / 区域限制 / 代理问题）', file=sys.stderr)
            return EXIT_NEEDS_DECISION
        for name, gender, locale in voices:
            if locale.startswith('zh') or 'Multilingual' in name:
                print(f'{name:38} {gender:7} {locale}')
        return 0

    if not args.plan:
        ap.error('需要 plan.json，或用 --doctor / --list-voices')

    plan = read_plan(args.plan)
    if plan is None:
        return 2

    vo = plan.get('voiceover') if isinstance(plan.get('voiceover'), dict) else {}
    if vo.get('source') == 'none':
        print('plan.json 标记为无配音（voiceover.source = none），跳过。')
        return 0
    if vo.get('source') in ('user-recording', 'user-specified'):
        print(f"plan.json 指定使用用户提供的配音（{vo.get('source')}），不生成。")
        return 0

    ok, info = have_edge_tts()
    if not ok:
        print(f'edge-tts 不可用：{info}', file=sys.stderr)
        print('按 voiceover.md §1：落到第 2 级（其他免费 TTS）；仍无合适者请让用户决定。'
              '不要使用系统机器音。', file=sys.stderr)
        return EXIT_NEEDS_DECISION

    voice = args.voice or vo.get('voice') or DEFAULT_VOICE
    rate = args.rate or vo.get('rate') or '+0%'
    pitch = args.pitch or vo.get('pitch') or '+0Hz'
    for flag, value, pattern in (('--rate', rate, r'^[+-]\d+%$'), ('--pitch', pitch, r'^[+-]\d+Hz$')):
        if not re.match(pattern, value):
            print(f'{flag} 格式错误：{value}（应为 +0% / -5% / -2Hz 这类）', file=sys.stderr)
            return 2

    lines = collect_lines(plan)
    if not lines:
        print('plan.json 的镜头里没有可配音的文案（需要 voiceoverText，或 headline + description）',
              file=sys.stderr)
        return 1

    project = Path(args.plan).resolve().parent
    out_dir = project / 'assets' / 'voice'
    ev_dir = project / 'evidence'
    out_dir.mkdir(parents=True, exist_ok=True)
    ev_dir.mkdir(parents=True, exist_ok=True)

    medias, failures = [], []
    for i, line in enumerate(lines, 1):
        raw = out_dir / f'vo-{i:02d}.mp3'
        media = out_dir / f'vo-{i:02d}.wav'
        subs = out_dir / f'vo-{i:02d}.srt'
        good, err = synth(line['text'], voice, rate, pitch, raw, subs, args.proxy)
        if good:
            # edge-tts 输出 mp3/24k；转成 48k 单声道 PCM，避免下游混音踩坑。
            conv_ok, conv_err = to_wav(raw, media)
            if not conv_ok:
                failures.append((line['id'], f'转 wav 失败：{conv_err}'))
                print(f"  ✗ {line['id']}: 转 wav 失败：{conv_err}", file=sys.stderr)
                continue
            raw.unlink(missing_ok=True)
            line['file'] = str(media.relative_to(project))
            line['duration'] = probe_duration(media)
            medias.append(media)
            print(f"  ✓ {line['id']}: {len(line['text'])} 字 → {media.name}"
                  + (f"（{line['duration']}s）" if line['duration'] else ''))
        else:
            failures.append((line['id'], err))
            print(f"  ✗ {line['id']}: {err}", file=sys.stderr)

    if failures:
        print(f'\n{len(failures)} 条配音失败。常见原因：无网络、区域限制、音色名不存在。'
              '先跑 --doctor，再考虑落到第 2 级或让用户决定。', file=sys.stderr)
        return 1

    report = {
        'engine': 'edge-tts',
        'voice': voice,
        'rate': rate,
        'pitch': pitch,
        'reason': vo.get('reason'),
        'lines': lines,
        'note': '配音默认听着清楚；鸣谢与响度由 mix_audio.py 的 loudnorm 处理。'
                '生成后必须试听并核对转写，多音字与数字读法是常见错误。',
    }
    (ev_dir / 'voiceover.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(f'\n完成：{len(medias)} 条 → {out_dir}')
    print(f'记录：{ev_dir / "voiceover.json"}')
    print('下一步：试听、逐句核对转写，再按 audio-and-qa.md 混音。')
    return 0


if __name__ == '__main__':
    sys.exit(main())

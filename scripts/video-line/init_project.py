#!/usr/bin/env python3
"""Initialize an isolated promo workspace without installing dependencies or touching the repo."""
import argparse
import json
import shutil
from pathlib import Path

# 投放预设：同一个起步工程，按目标渠道改画幅 / 时长 / 节奏基准。
# 差异来自 references/platforms/{xiaohongshu/video.md, wechat/channels.md}：
# 小红书视频 9:16、前 3 秒即钩子、30s–3min 最稳；视频号横竖皆可但第 1 帧即默认封面。
PRESETS = {
    'generic': {
        'width': 1920, 'height': 1080, 'duration': 10,
        'label': '通用（自有渠道）',
        'notes': ['横版 16:9 为默认起点，画幅可按渠道自定。'],
    },
    'xhs-vertical': {
        'width': 1080, 'height': 1920, 'duration': 10,
        'label': '小红书视频笔记',
        'notes': [
            '9:16 竖屏；横版素材加黑边做竖版，不要留白边。',
            '前 3 秒即钩子：第 1 个镜头就要给出具体利益点，不要片头、问候或空镜。',
            '封面必须单独做 3:4（1080×1440），不要用视频首帧。',
            '30 秒–3 分钟最稳；时长上限口径不一，以 App 实际提示为准。',
        ],
    },
    'channels-horizontal': {
        'width': 1920, 'height': 1080, 'duration': 10,
        'label': '视频号（横版）',
        'notes': [
            '横版 16:9；宽高比允许 0.33–3.0。',
            '第 1 帧即默认封面，必须是完整画面（check_delivery.py 会测前 5 帧）。',
            '横版封面在主页会被裁成 6:7 —— 要单独确认裁切后主体仍完整。',
            '短标题 ≤16 字会进搜索场景，必须单独打磨。',
        ],
    },
    'channels-vertical': {
        'width': 1080, 'height': 1920, 'duration': 10,
        'label': '视频号（竖版）',
        'notes': [
            '9:16 竖版；封面 1080×1260（6:7），横版封面在主页会被裁成 6:7。',
            '第 1 帧即默认封面，必须是完整画面。',
            '短标题 ≤16 字会进搜索场景，必须单独打磨。',
        ],
    },
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--style', required=True, choices=['repo', 'default', 'hybrid'])
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--preset', default='generic', choices=sorted(PRESETS),
                        help='投放预设：决定画幅、时长基准与首帧/钩子要求（默认 generic 横版 16:9）')
    args = parser.parse_args()
    preset = PRESETS[args.preset]
    repo = args.repo.expanduser().resolve() if args.repo else None
    target = args.output.expanduser().resolve()
    if args.style in ('repo', 'hybrid') and (repo is None or not repo.is_dir()):
        parser.error('repo/hybrid requires --repo pointing to an existing repository')
    if repo is not None and not repo.is_dir():
        parser.error('--repo must be a directory')
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        parser.error('output must be absent or empty; existing work is never overwritten')
    skill = Path(__file__).resolve().parents[2]
    if target == skill or skill in target.parents:
        parser.error('output must be outside the skill bundle')
    if not target.is_dir():target.mkdir(parents=True)
    shutil.copytree(skill / 'assets/platforms/generic/starter', target, dirs_exist_ok=True)
    for name in ['assets', 'evidence', 'renders', 'public']:
        if not (target/name).is_dir():(target/name).mkdir(parents=True)
    if args.style != 'repo':
        shutil.copytree(skill/'assets/platforms/generic/fallback', target/'assets/fallback')
        (target/'src/presentations.jsx').write_text("""import React from 'react';
import {CardFrame, CardSurface, FilmButton, FilmBadge} from '../assets/fallback/primitives.jsx';
// Technical fixture using the adapted fallback primitives, not product business components.
export function FeatureVisual() {
  return <CardFrame data-skill-placeholder="true"><CardSurface style={{padding:54}}>
    <FilmBadge>组件展示 / DEMO</FilmBadge>
    <h2>组件可以直接接进来。</h2>
    <p>把真实产品组件接进来，再安排选中、展开和切换。</p>
    <div style={{display:'flex',gap:16,marginTop:42,fontSize:26}}>
      <FilmButton>主要操作</FilmButton><FilmButton variant="secondary">次要操作</FilmButton>
    </div>
  </CardSurface></CardFrame>;
}
""")
    shots = [
        {'id':'intro','start':0,'end':3,'type':'title','headlineEn':"What's new",'headline':'这次更新，带来了什么？','description':'先用一句话讲清楚变化，再展示具体怎么用。'},
        {'id':'component','start':3,'end':7,'type':'detail','headlineEn':'Real components','headline':'直接用产品里的组件','description':'把仓库里的按钮和卡片接进来，再用代码安排它们的出场和切换。','component':'src/presentations.jsx'},
        {'id':'close','start':7,'end':10,'type':'end','headlineEn':'Ready to share','headline':'画面和声音，一起检查','description':'确认字幕读得完、操作听得见，再导出视频。'},
    ]
    for shot in shots:
        shot.update({'descriptionAt':0,'claim':False,'source':[], 'plainExplanation':shot['description'],
                     'actions':[{'id':shot['id']+'-enter','at':0,'action':'copy enters','soundRequired':False}]})
        shot.setdefault('component', None)
    shots[1]['actions'].append({'id':'component-appear','at':0.45,'action':'controls appear','soundRequired':True})
    shots[2]['actions'][0]['soundRequired']=True
    plan = {'demo':True,'product':'软件更新 · 技术样片','style':args.style,
            'preset':args.preset,
            'width':preset['width'],'height':preset['height'],'fps':30,'duration':preset['duration'],
            'repo':str(repo) if repo else None,'audioRequired':True,'sfxRequired':True,
            'typography':{'mode':'bilingual','zhFont':'PingFang SC / Noto Sans CJK SC','enFont':'Georgia','zhStyle':'sans-serif'},
            'audio':{'ducking':{'enabled':True},'music':{'file':'assets/music.wav','gain':0.65},'cues':[
              {'at':3.45,'actionId':'component-appear','file':'assets/sfx/click.wav','gain':0.8,'role':'sfx','kind':'click'},
              {'at':7.0,'actionId':'close-enter','file':'assets/sfx/ding-dong.wav','gain':0.7,'role':'sfx','kind':'ding-dong'}]},
            'shots':shots}
    (target/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    (target/'BRIEF.md').write_text(f"""# 视频 brief

- 状态：技术起步，尚未完成产品调研与分镜。
- 风格选择：{args.style}（应来自用户已确认的选择）
- 投放预设：{preset['label']}（`{args.preset}`，画幅 {preset['width']}×{preset['height']}、时长基准 {preset['duration']}s）
- 仓库：{repo or '未指定，制作真实产品内容前补充'}
- 产品 / 更新范围 / 发布状态：待从用户输入和仓库确定。
- 平台 / 画幅 / 时长 / 语言：待记录；plan.json 当前仅为 {preset['duration']} 秒技术样片。
- 品牌资源 / 字体：待审计。
- 是否允许链接 / CTA：待记录用户要求。
- 声音：音乐默认用代码原创；音效先找适合本片的素材，缺项才用 skill 内置 WAV。技术样片尚未配音轨；plan 已分别列出配乐和关键动作音效，须实际准备并混入。
- 卖点证据、风格审计与素材来源：记录在 evidence/。

### 本预设的硬要求

{chr(10).join('- ' + n for n in preset['notes'])}

保留原有用户决定；没有确认的字段不要伪装成已确认。正式成片完成后同步 plan.json 与实际时间线。
""")
    (target/'DIRECTION.md').write_text('''# 影片方向（写代码前完成，见 references/platforms/generic/motion-film/direction.md）

> 这份文件只有问题，没有答案。每一项都从这个产品本身推导；不要照抄案例或上一支片子。

## 1. 参考拆解（用户给了参考才写）
| 参考里的手法 | 它在表达什么 | 本片是否采用、怎么改写 |
|---|---|---|

## 2. 产品气质
- 产品是做什么的、给谁用、用起来是什么感觉：
- 设计语言（色板、字体、圆角、明暗主题）来源：
- 能成为视觉母题的产品元素（标志几何、核心界面、数据形态、领域隐喻）：

## 3. 三个方向（沿不同的轴拉开）
| 方向 | 底色与光 | 字体声音 | 母题来源 | 镜头语言 | 节奏 | 音乐 |
|---|---|---|---|---|---|---|
| A | | | | | | |
| B | | | | | | |
| C | | | | | | |

## 4. 选择与理由
- 选哪个、为什么适合这个产品和受众：
- 本片专属手法（3–5 个，每个写出从产品哪一点推导而来）：
- 与本工作区既往影片的区别（开场、转场、背景、配乐）：

## 5. 画面规范
- 画幅 / 帧率 / 底色 / 安全区：
- 字号阶梯（英文、中文、说明）与字体来源：
- 产品界面上镜倍数（正文 ≥ 22px）与明暗主题：
- 动效语法（入场、镜头运动、缓动、禁止项）：

## 6. 镜头表
| # | 时间 | 镜头 | 主角 | 画面与动作 | 文案 | 声音 |
|---|---|---|---|---|---|---|
''')
    print(json.dumps({'project':str(target),'style':args.style,'demo':True,'next':'Research the product, then write DIRECTION.md (references/platforms/generic/motion-film/direction.md) before production shots.'},ensure_ascii=False))

if __name__ == '__main__':
    main()

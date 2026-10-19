"""Offline regressions for delivery gates and headless-only preflight."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import shutil
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/'video-line'/f'{name}.py')
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
delivery=module('check_delivery');environment=module('check_environment')
class Delivery(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
        (self.root/'evidence.md').write_text('Release evidence fixture')
        (self.root/'DIRECTION.md').write_text('# 方向\n因为产品是模型选择器，所以镜头推近选择器。\n| # | 镜头 |\n|---|---|\n| 1 | feature |\n')
        self.plan={'demo':False,'style':'repo','duration':5,'fps':30,'width':1920,'height':1080,'audioRequired':False,'audioExceptionReason':'User requested a silent version',
            'typography':{'mode':'bilingual','zhStyle':'sans-serif','zhFont':'Noto Sans CJK','enFont':'Georgia'},
            'shots':[{'id':'feature','start':0,'end':5,'type':'detail','headline':'切换模型，继续对话','headlineEn':'Switch models','claim':True,'source':['file:evidence.md'],
                'plainExplanation':'切换模型后，可以带着之前的对话继续工作。','description':'切换模型后，对话内容会保留。','component':'src/selector.tsx','actions':[]}]}
    def errors(self):return delivery.check(self.plan,project_dir=self.root)['errors']
    def test_valid_production(self):self.assertEqual(self.errors(),[])
    def test_all_claims_false(self):
        self.plan['shots'][0]['claim']=False;self.assertTrue(any('at least one' in x for x in self.errors()))
    def test_demo_still_allowed(self):
        self.plan['demo']=True;self.plan['shots'][0]['claim']=False;self.assertEqual(self.errors(),[])
    def test_feature_components_required(self):
        for kind in ['detail','workspace','macro']:
            for value in [None,'','   ']:
                with self.subTest(kind=kind,value=value):
                    self.plan['shots'][0].update(type=kind,component=value)
                    self.assertTrue(any('component source' in x for x in self.errors()))
    def test_audio_exception_required(self):
        for value in [None,'','   ',True]:
            self.plan['audioExceptionReason']=value
            self.assertTrue(any('audioExceptionReason' in x for x in self.errors()))
    def test_source_files_resolve(self):
        for source in ['file:missing.md','./missing.md','repo:missing.tsx']:
            self.plan['shots'][0]['source']=[source];self.assertTrue(self.errors())
        self.plan['repo']=str(self.root)
        for source in ['repo:evidence.md:2','file:evidence.md#L3','evidence.md']:
            self.plan['shots'][0]['source']=[source];self.assertEqual(self.errors(),[])
    def test_legacy_paths_search_video_then_repo(self):
        repo=self.root/'product';(repo/'src/components').mkdir(parents=True)
        (repo/'src/components/Selector.jsx').write_text('export const Selector = 1;')
        (repo/'CHANGELOG.md').write_text('Product release')
        self.plan['repo']='product'
        self.plan['shots'][0]['source']=['src/components/Selector.jsx:12','CHANGELOG.md#L2']
        self.assertEqual(self.errors(),[])
        self.assertEqual(delivery.source_file('CHANGELOG.md',self.root,'product'),repo/'CHANGELOG.md')
        (self.root/'CHANGELOG.md').write_text('Video evidence')
        self.assertEqual(delivery.source_file('CHANGELOG.md',self.root,'product'),self.root/'CHANGELOG.md')
        self.plan['shots'][0]['source']=['missing.md'];self.assertTrue(self.errors())
    def test_explicit_source_roots_do_not_fall_back(self):
        repo=self.root/'product';repo.mkdir();(repo/'release.md').write_text('Release')
        self.plan['repo']=str(repo)
        for source in ['file:release.md','./release.md','../release.md']:
            self.plan['shots'][0]['source']=[source];self.assertTrue(self.errors())
        self.plan['shots'][0]['source']=['repo:release.md'];self.assertEqual(self.errors(),[])
        self.assertEqual(delivery.source_file(str(repo/'release.md'),self.root,None),repo/'release.md')
    def test_production_requires_direction(self):
        (self.root/'DIRECTION.md').unlink()
        self.assertTrue(any('DIRECTION.md' in x for x in self.errors()))
        self.plan['demo']=True;self.assertFalse(any('DIRECTION.md' in x for x in self.errors()))
    def test_direction_without_reasons_warns(self):
        (self.root/'DIRECTION.md').write_text('| # | 镜头 |\n|---|---|\n| 1 | feature |\n')
        warnings=delivery.check(self.plan,project_dir=self.root)['warnings']
        self.assertTrue(any('derive devices' in w for w in warnings))
    def test_external_evidence_not_treated_as_file(self):
        self.plan['shots'][0]['source']=['https://example.org/release.md','tag:v1.0','commit:abc123'];self.assertEqual(self.errors(),[])
class Preflight(unittest.TestCase):
    def probe(self,project,launch_ok=True):
        def fake_run(args,cwd=None,timeout=30):
            out=''
            if '--version' in args:out='v22.0.0' if 'node' in args[0] else '10.0.0'
            elif '-version' in args:out='ffmpeg 8'
            elif '-filters' in args:out='volume adelay amix loudnorm afade aresample asetnsamples'
            elif '-encoders' in args:out='libx264 aac'
            elif '-e' in args:
                js=args[args.index('-e')+1]
                if 'chromium.launch' in js:
                    if not launch_ok:return {'ok':False,'stdout':'','stderr':'Permission denied','output':'Permission denied'}
                else:
                    self.assertNotIn('executablePath()',js)
                    out=json.dumps({k:{'version':'1.0','path':'/unavailable/'+k} for k in ['playwright','esbuild','react','react-dom','gsap','three']})
            return {'ok':True,'stdout':out,'stderr':'','output':out}
        with patch.object(environment,'run',side_effect=fake_run),patch.object(environment.shutil,'which',side_effect=lambda n:'/bin/'+n),patch('sys.argv',['check_environment','--project',str(project)]),contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as caught:environment.main()
        return caught.exception.code,json.loads(output.getvalue())
    def test_headless_only_and_cache_revalidation(self):
        with tempfile.TemporaryDirectory() as d:
            code,result=self.probe(Path(d));self.assertEqual(code,0);self.assertTrue(result['ready']);self.assertTrue(result['browser']['launched'])
            code,result=self.probe(Path(d));self.assertTrue(result['cached'])
            code,result=self.probe(Path(d),False);self.assertEqual(code,1);self.assertFalse(result['cached']);self.assertIn('browser-launch',result['missing'])
class Starter(unittest.TestCase):
    def test_default_repo_and_unedited_demo_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d)/'repo';repo.mkdir();project=Path(d)/'video'
            subprocess.run([sys.executable,str(ROOT/'scripts/video-line/init_project.py'),'--output',str(project),'--style','default','--repo',str(repo)],capture_output=True,check=True)
            plan=json.loads((project/'plan.json').read_text())
            self.assertEqual(plan['repo'],str(repo.resolve()))
            self.assertIn(str(repo.resolve()),(project/'BRIEF.md').read_text())
            plan['demo']=False
            self.assertTrue(any('at least one' in e for e in delivery.check(plan,project_dir=project)['errors']))
    def test_init_writes_direction_questions_not_answers(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d)/'repo';repo.mkdir();project=Path(d)/'video'
            subprocess.run([sys.executable,str(ROOT/'scripts/video-line/init_project.py'),'--output',str(project),'--style','repo','--repo',str(repo)],capture_output=True,check=True)
            text=(project/'DIRECTION.md').read_text()
            for heading in ['参考拆解','产品气质','三个方向','选择与理由','画面规范','镜头表']:self.assertIn(heading,text)
            self.assertIn('不要照抄',text)
            self.assertTrue((project/'src/engine.js').is_file())
    def test_preset_controls_frame_and_duration(self):
        """--preset 决定画幅与时长基准，并写进 plan.json 与 BRIEF.md。"""
        cases = {
            'generic': (1920, 1080),
            'xhs-vertical': (1080, 1920),
            'channels-horizontal': (1920, 1080),
            'channels-vertical': (1080, 1920),
        }
        import tempfile
        for preset, (w, h) in cases.items():
            with tempfile.TemporaryDirectory() as d:
                project = Path(d) / 'video'
                subprocess.run([sys.executable, str(ROOT / 'scripts/video-line/init_project.py'),
                                '--output', str(project), '--style', 'default',
                                '--preset', preset], capture_output=True, check=True)
                plan = json.loads((project / 'plan.json').read_text())
                self.assertEqual((plan['width'], plan['height']), (w, h), preset)
                self.assertEqual(plan['preset'], preset)
                self.assertIn(preset, (project / 'BRIEF.md').read_text())

    def test_default_preset_is_backwards_compatible(self):
        """不给 --preset 时行为必须和 v1.0.3 一致：横版 1920x1080。"""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / 'video'
            subprocess.run([sys.executable, str(ROOT / 'scripts/video-line/init_project.py'),
                            '--output', str(project), '--style', 'default'],
                           capture_output=True, check=True)
            plan = json.loads((project / 'plan.json').read_text())
            self.assertEqual((plan['width'], plan['height'], plan['duration']), (1920, 1080, 10))

    def test_unknown_preset_is_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / 'video'
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/video-line/init_project.py'),
                                   '--output', str(project), '--style', 'default',
                                   '--preset', 'tiktok'],
                                  capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse((project / 'plan.json').exists())

    def test_xhs_preset_brief_carries_hook_requirement(self):
        """小红书预设必须把「前 3 秒即钩子」和竖版封面要求写进 BRIEF，而不是只改数字。"""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / 'video'
            subprocess.run([sys.executable, str(ROOT / 'scripts/video-line/init_project.py'),
                            '--output', str(project), '--style', 'default',
                            '--preset', 'xhs-vertical'], capture_output=True, check=True)
            brief = (project / 'BRIEF.md').read_text()
            self.assertIn('前 3 秒即钩子', brief)
            self.assertIn('1080×1440', brief)

    def test_sample_views_cover_plan_shots(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d)/'repo';repo.mkdir();project=Path(d)/'video'
            subprocess.run([sys.executable,str(ROOT/'scripts/video-line/init_project.py'),'--output',str(project),'--style','repo','--repo',str(repo)],capture_output=True,check=True)
            ids=[s['id'] for s in json.loads((project/'plan.json').read_text())['shots']]
            index=(project/'src/shots/index.js').read_text()
            for i in ids:self.assertIn(i+':',index)
class FirstFrame(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg needed')
    def test_blank_opening_fails_production(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            blank=root/'blank.mp4';busy=root/'busy.mp4'
            for src,out in [('color=c=0xfafaf9:s=640x360:r=30:d=1',blank),('testsrc2=s=640x360:r=30:d=1',busy)]:
                subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',src,'-pix_fmt','yuv420p',str(out)],check=True)
            self.assertTrue(all(r<0.004 for r in delivery.first_frame_metrics(blank)['inkRatio']))
            self.assertTrue(all(r>0.004 for r in delivery.first_frame_metrics(busy)['inkRatio']))
class Mix(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg needed')
    def test_outputs_are_capped_to_film_duration(self):
        import math,struct,wave
        mixer=module('mix_audio')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'assets/sfx').mkdir(parents=True)
            def tone(path,seconds,freq,channels=2):
                rate=48000;frames=[]
                for i in range(int(rate*seconds)):
                    v=int(0.3*32767*math.sin(2*math.pi*freq*i/rate));frames+= [v]*channels
                with wave.open(str(path),'wb') as w:w.setnchannels(channels);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<%dh'%len(frames),*frames))
            tone(root/'assets/music.wav',3.2,220);tone(root/'assets/sfx/a.wav',0.4,880);tone(root/'assets/sfx/b.wav',1.5,660,1)
            actions=[{'id':f'k{i}','at':0.2+i*0.3,'action':'key','soundRequired':True} for i in range(8)]
            cues=[{'at':a['at'],'actionId':a['id'],'file':'assets/sfx/'+('a' if i%2 else 'b')+'.wav','gain':0.8,'role':'sfx','kind':'click'} for i,a in enumerate(actions)]
            plan={'duration':3,'fps':30,'shots':[{'id':'s','start':0,'end':3,'actions':actions}],'audio':{'music':{'file':'assets/music.wav','gain':0.6},'cues':cues,'ducking':{'enabled':True}}}
            (root/'plan.json').write_text(json.dumps(plan))
            with contextlib.redirect_stdout(io.StringIO()):mixer.mix(root/'plan.json')
            for name in ['sfx-stem.wav','music-ducked.wav','master.wav']:
                out=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(root/'assets'/name)],capture_output=True,text=True).stdout
                self.assertAlmostEqual(float(out),3.0,delta=0.05,msg=name)
class Landmarks(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg needed')
    def test_onset_and_peak(self):
        import math,struct,wave
        landmarks=module('sfx_landmarks').landmarks
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'hit.wav';rate=48000;data=[]
            for i in range(rate):
                t=i/rate;amp=0 if t<0.25 else (0.4 if t<0.5 else 0.9*math.exp(-(t-0.5)*8))
                data.append(int(amp*32767*math.sin(2*math.pi*440*t)))
            with wave.open(str(f),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<%dh'%len(data),*data))
            r=landmarks(f)
            self.assertAlmostEqual(r['onset'],0.25,delta=0.01)
            self.assertAlmostEqual(r['peak'],0.5,delta=0.01)
            self.assertAlmostEqual(r['peakDbfs'],-0.9,delta=0.3)

class EvidenceLevel(unittest.TestCase):
    """只有网址时（B/C 级）先写 RESEARCH.md，且不要求原组件——但不能伪造界面。"""

    def make_plan(self, level=None):
        plan = {'duration': 10, 'fps': 30, 'width': 1920, 'height': 1080,
                'style': 'default', 'repo': None, 'demo': False, 'audioRequired': True,
                'typography': {'mode': 'bilingual', 'zhFont': 'PingFang SC',
                               'enFont': 'Georgia', 'zhStyle': 'sans-serif'},
                'shots': [
                    {'id': 'intro', 'start': 0, 'end': 4, 'type': 'title',
                     'headlineEn': 'See it', 'headline': '看这个', 'description': '一句话说清',
                     'descriptionAt': 0, 'claim': False, 'source': [],
                     'actions': [{'id': 'a1', 'at': 0, 'action': 'x', 'soundRequired': True}]},
                    {'id': 'feat', 'start': 4, 'end': 10, 'type': 'detail',
                     'headlineEn': 'How it works', 'headline': '它怎么工作',
                     'description': '讲清机理', 'descriptionAt': 0, 'claim': True,
                     'source': ['https://example.com/docs'],
                     'plainExplanation': '文档描述了实现方式',
                     'actions': [{'id': 'a2', 'at': 0, 'action': 'y', 'soundRequired': True}]}]}
        if level:
            plan['evidenceLevel'] = level
        return plan

    def test_web_level_without_research_is_error(self):
        delivery = module('check_delivery')
        errs = delivery.check(self.make_plan('web'), project_dir=tempfile.mkdtemp())['errors']
        self.assertTrue(any('RESEARCH.md' in e for e in errs), errs)

    def test_web_level_with_research_passes_that_check(self):
        delivery = module('check_delivery')
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'RESEARCH.md').write_text(
                '# 调研\n- 证据级别：web\n- https://example.com\n', encoding='utf-8')
            errs = delivery.check(self.make_plan('web'), project_dir=d)['errors']
        self.assertFalse(any('RESEARCH.md' in e for e in errs), errs)

    def test_web_level_relaxes_component_requirement(self):
        """没有源码时不强求 component，但必须给 warning 提醒别伪造界面。"""
        delivery = module('check_delivery')
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'RESEARCH.md').write_text('证据级别 web https://e.com', encoding='utf-8')
            res = delivery.check(self.make_plan('web'), project_dir=d)
        self.assertFalse(any('component source' in e for e in res['errors']), res['errors'])
        self.assertTrue(any('must not be an invented interface' in w for w in res['warnings']),
                        res['warnings'])

    def test_repo_level_still_requires_component(self):
        """A 级行为不变：缺 component 仍然报错。"""
        delivery = module('check_delivery')
        errs = delivery.check(self.make_plan(), project_dir=tempfile.mkdtemp())['errors']
        self.assertTrue(any('component source' in e for e in errs), errs)

    def test_invalid_evidence_level_is_error(self):
        delivery = module('check_delivery')
        errs = delivery.check(self.make_plan('screenshot'), project_dir=tempfile.mkdtemp())['errors']
        self.assertTrue(any('evidenceLevel' in e for e in errs), errs)

    def test_research_without_url_warns(self):
        delivery = module('check_delivery')
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'RESEARCH.md').write_text('# 调研\n证据级别 web\n', encoding='utf-8')
            warns = delivery.check(self.make_plan('web'), project_dir=d)['warnings']
        self.assertTrue(any('no source URL' in w for w in warns), warns)

class FilmKind(unittest.TestCase):
    """片型由内容决定：不声明时按 product（保持原有严格度），声明其他片型则放宽对应项。"""

    def make_plan(self, kind=None, claim=False):
        plan = {'duration': 10, 'fps': 30, 'width': 1920, 'height': 1080,
                'style': 'default', 'repo': None, 'demo': False, 'audioRequired': True,
                'typography': {'mode': 'bilingual', 'zhFont': 'PingFang SC',
                               'enFont': 'Georgia', 'zhStyle': 'sans-serif'},
                'shots': [
                    {'id': 'intro', 'start': 0, 'end': 4, 'type': 'title',
                     'headlineEn': 'Saturn', 'headline': '土星', 'description': '环怎么来的',
                     'descriptionAt': 0, 'claim': False, 'source': [],
                     'actions': [{'id': 'a1', 'at': 0, 'action': 'x', 'soundRequired': True}]},
                    {'id': 'detail', 'start': 4, 'end': 10, 'type': 'detail',
                     'headlineEn': 'Rings', 'headline': '环的成分', 'description': '冰粒组成',
                     'descriptionAt': 0, 'claim': claim,
                     'source': ['https://nasa.gov'] if claim else [],
                     'plainExplanation': '资料描述', 'component': None,
                     'actions': [{'id': 'a2', 'at': 0, 'action': 'y', 'soundRequired': True}]}]}
        if kind:
            plan['filmKind'] = kind
        return plan

    def errors(self, plan, d):
        delivery = module('check_delivery')
        return delivery.check(plan, project_dir=d)['errors']

    def test_default_kind_is_product_and_keeps_strictness(self):
        """不声明片型时行为与以前一致：要求 feature claim。"""
        with tempfile.TemporaryDirectory() as d:
            errs = self.errors(self.make_plan(), d)
        self.assertTrue(any('evidenced feature claim' in e for e in errs), errs)

    def test_explainer_does_not_require_feature_claim(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'evidence').mkdir()
            Path(d, 'evidence', 'FACTS.md').write_text(
                '| 主张 | 上屏内容 | 来源 |\n|---|---|---|\n| x | y | https://e.com |\n',
                encoding='utf-8')
            errs = self.errors(self.make_plan('explainer'), d)
        self.assertFalse(any('feature claim' in e for e in errs), errs)
        self.assertFalse(any('FACTS' in e for e in errs), errs)

    def test_explainer_without_sources_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            errs = self.errors(self.make_plan('explainer'), d)
        self.assertTrue(any('FACTS.md or RESEARCH.md' in e for e in errs), errs)

    def test_explainer_accepts_research_md_as_source(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'RESEARCH.md').write_text('https://e.com', encoding='utf-8')
            errs = self.errors(self.make_plan('explainer'), d)
        self.assertFalse(any('FACTS.md or RESEARCH.md' in e for e in errs), errs)

    def test_story_does_not_require_claim_or_sources(self):
        with tempfile.TemporaryDirectory() as d:
            errs = self.errors(self.make_plan('story'), d)
        self.assertFalse(any('feature claim' in e for e in errs), errs)
        self.assertFalse(any('FACTS.md or RESEARCH.md' in e for e in errs), errs)

    def test_story_without_fiction_note_warns(self):
        delivery = module('check_delivery')
        with tempfile.TemporaryDirectory() as d:
            warns = delivery.check(self.make_plan('story'), project_dir=d)['warnings']
        self.assertTrue(any('fictionNote' in w for w in warns), warns)

    def test_story_with_fiction_note_is_quiet(self):
        delivery = module('check_delivery')
        plan = self.make_plan('story')
        plan['fictionNote'] = '人物与情节为虚构示意'
        with tempfile.TemporaryDirectory() as d:
            warns = delivery.check(plan, project_dir=d)['warnings']
        self.assertFalse(any('fictionNote' in w for w in warns), warns)

    def test_non_product_kind_never_requires_component(self):
        """非产品片没有业务组件可接，但必须提醒不得画假界面。"""
        delivery = module('check_delivery')
        for kind in ('explainer', 'story', 'evidence'):
            with tempfile.TemporaryDirectory() as d:
                plan = self.make_plan(kind)
                res = delivery.check(plan, project_dir=d)
            self.assertFalse(any('component source' in e for e in res['errors']), (kind, res['errors']))
            self.assertTrue(any('must not be invented' in w for w in res['warnings']), (kind, res['warnings']))

    def test_invalid_film_kind_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            errs = self.errors(self.make_plan('animation'), d)
        self.assertTrue(any('filmKind' in e for e in errs), errs)

if __name__=='__main__':unittest.main()

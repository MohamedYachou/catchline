"""Verify deliverables, alpha, fonts, slice geometry, provenance and scope.
Run after build_ui_kit.py with Pillow + fontTools. No Unity required.
"""
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
UI=ROOT/'Assets/Art/UI'
manifest=json.loads((UI/'slices.json').read_text())
expected={
 *['panel-cream','card-white','card-selected','toast-dark','chip-dark'],
 *[f'button-{n}-{s}' for n in ['primary','secondary','disabled','tab-on','tab-off'] for s in ['normal','pressed']],
 *['bubble-white','bubble-white-tail','bubble-hot','bubble-hot-tail'],
 *['strike-water','bobber-floating','bobber-dipped','bobber-underwater','fish-shadow','ripple-ring','tap-burst'],
 *[f'bar-{n}' for n in ['background','teal','green','red']],
 *[f'icon-{n}' for n in ['coin','fish','bait-worm','food','cooler','ice','rod','crew','contract-scroll','map-pin','home-anchor','clock','star','lock']]
}
assert expected<=set(manifest['sprites'])
assert all(n in expected or m.get('task')==5 for n,m in manifest['sprites'].items())
assert {p.stem for p in UI.glob('*.png')}==set(manifest['sprites'])
text=(UI/'UI.md').read_text()
checks=[]
for name,m in manifest['sprites'].items():
    im=Image.open(UI/m['file']); assert im.mode=='RGBA'
    assert im.size==tuple(m['export_size'])==tuple(2*x for x in m['intended_size'])
    lo,hi=im.getchannel('A').getextrema(); assert hi>0 and (lo==255 if m.get('opaque') else lo==0),(name,lo,hi)
    assert im.info['srgb']==0 and im.info['Source']
    assert (ROOT/m['source']).is_file() and m['file'] in text
    border=m['border_px']
    if border:
        assert all(isinstance(v,int) and v>0 for v in border.values())
        assert border['left']+border['right']<im.width
        assert border['top']+border['bottom']<im.height
    checks.append({'file':m['file'],'passed':True,'sha256':hashlib.sha256((UI/m['file']).read_bytes()).hexdigest()})
assert Image.open(UI/'strike-water.png').size==(920,440)
for name in ['16-ui-kit','17-hud-fishing','18-hud-harbour']:
    im=Image.open(ROOT/'Art/Concepts'/f'{name}.png'); assert im.size==(1920,1080)
    assert im.info['Source']
font=TTFont(UI/'Fonts/Fredoka-Medium.ttf')
assert 'fvar' not in font
assert 'SIL OPEN FONT LICENSE' in (UI/'Fonts/OFL.txt').read_text()
# Baseline manifest from the previous art handoff proves both crew files unchanged.
old=json.loads(subprocess.check_output(['git','show','HEAD:Art/Models/GullHarbour/files.json'],cwd=ROOT,text=True))
for f in old['files']:
    if f['file'].endswith(('/CrewBody.blend','/CrewBody.fbx')):
        assert hashlib.sha256((ROOT/f['file']).read_bytes()).hexdigest()==f['sha256']
changed=subprocess.check_output(['git','diff','--name-only','HEAD','--','Assets/Scripts','Assets/Scenes'],cwd=ROOT,text=True).splitlines()
assert not any(p.startswith(('Assets/Scripts/','Assets/Scenes/')) for p in changed)
result={'sprite_count':len(checks),'all_passed':True,'sprites':checks,'mockups_1920x1080':True,'font_static_ttf_and_ofl':True,'crew_body_unchanged':True,'prohibited_paths_unchanged':True,'unity_opened':False,'scope':'Offline dimensions, transparent alpha, slice border bounds, font packaging, PNG provenance and baseline crew hashes. No Unity importer or runtime validation.'}
(UI/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('UI_VALIDATED',len(checks),'sprites / three 1920x1080 mockups / crew unchanged')

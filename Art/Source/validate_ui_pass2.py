"""Validate task 05 exports and unchanged original UI/model/protected files.
Use --complete at final delivery; writes task05-validation.json only.
"""
from pathlib import Path
import sys,json,hashlib,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]; UI=ROOT/'Assets/Art/UI'
expected={'logo-catchline':(1024,384),'title-backdrop':(1920,1080),'sea-chart':(1240,520),'daily-gift':(512,512)}
expected.update({'header-'+n:(1240,220) for n in ['market','harbourmaster','crewoffice','chandlery','supplies']})
expected.update({'fish-'+n:(256,256) for n in ['herring','mackerel','pollock','seabass','conger','plaice','cod','unknown']})
expected.update({'icon-'+n:(256,256) for n in ['rodholder','bigcooler','icebox','lunchtin','rod-fibreglass','rod-carbon','chart','squid','fuel','net','skiff','trophy','gift']})
expected.update({'portrait-'+n:(256,256) for n in ['captain','deckhand','fisherman','veteran']})
expected.update({'coin-pop':(256,256),'sparkle':(256,256),'catch-card':(256,320),'popup-panel':(256,320),'badge-new':(256,128)})
data=json.loads((UI/'slices.json').read_text()); new={n:m for n,m in data['sprites'].items() if m.get('task')==5}
assert set(new)<=set(expected)
if '--complete' in sys.argv:assert set(new)==set(expected),(set(expected)-set(new))
checks=[]
for n,m in new.items():
    im=Image.open(UI/m['file']);assert im.mode=='RGBA' and im.size==expected[n]==tuple(m['export_size'])
    assert im.size==tuple(2*v for v in m['intended_size'])
    assert im.info.get('srgb')==0 and im.info.get('Source')
    alpha=im.getchannel('A');lo,hi=alpha.getextrema();assert hi==255
    if n!='title-backdrop':
        assert lo==0 and all(alpha.getpixel(p)==0 for p in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]),n
    else:assert lo==255
    assert (ROOT/m['source']).is_file() and m['file'] in (UI/'UI.md').read_text()
    b=m['border_px']
    if b:assert b['left']+b['right']<im.width and b['top']+b['bottom']<im.height
    checks.append({'file':m['file'],'size':list(im.size),'sha256':hashlib.sha256((UI/m['file']).read_bytes()).hexdigest(),'passed':True})
# Compare against the last complete task04 handoff, independent of current HEAD.
base='3ddbe1f'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True)
assert not git('diff',base,'--name-only','--','Assets/Scripts','Assets/Scenes')
# Later additive model batches do not invalidate the original-model preservation check.
assert not git('diff',base,'--name-only','--diff-filter=DMRTUXB','--','Assets/Art/Models','Art/Models')
old=json.loads(git('show',base+':Assets/Art/UI/slices.json'))
requests=[base+':Assets/Art/UI/'+m['file'] for m in old['sprites'].values()]
raw=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(requests)+'\n').encode(),cwd=ROOT)
contents=[]; offset=0
for request in requests:
    end=raw.index(b'\n',offset); size=int(raw[offset:end].split()[-1]); offset=end+1
    contents.append(raw[offset:offset+size]);offset+=size+1
for (n,m),content in zip(old['sprites'].items(),contents):
    assert data['sprites'][n]==m
    # Git stores LFS pointers: compare the declared oid when present.
    payload=(UI/m['file']).read_bytes()
    if content.startswith(b'version https://git-lfs'):assert ('oid sha256:'+hashlib.sha256(payload).hexdigest()).encode() in content
    else:assert payload==content
assert {p.stem for p in UI.glob('*.png')}==set(data['sprites'])
result={'all_passed':True,'task05_count':len(new),'expected_final_count':len(expected),'original_44_unchanged':True,'models_and_protected_paths_unchanged':True,'unity_opened':False,'sprites':checks}
(UI/'task05-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(new),'task05 sprites; original 44, models and protected paths unchanged')

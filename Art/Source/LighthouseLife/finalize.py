"""Validate already audited/reviewed LIGHTHOUSE-LIFE-1 delivery and bind bytes.

Does not generate visual acceptance or invoke Blender/Unity.
"""
import hashlib,json,re,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/LighthouseLife';S=R/'Art/Source/LighthouseLife'
NAMES={'Puffin':600,'PuffinGroup':2000,'TideRace':400,'LighthouseGlow':160}
VIEWS={'three-quarter','front','right','back','top'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 deps=read(O/'metrics/dependencies.json');assert len(deps)==10
 for rel,h in deps.items():assert sha(R/rel)==h,('changed dependency',rel)
 expected={};counts={};audits={}
 for name,limit in NAMES.items():
  b=read(O/'metrics'/(name+'-build.json'));a=read(O/'metrics'/(name+'-audit.json'));audits[name]=a
  assert a['result']==a['surface']['result']=='PASS'
  assert b['triangles']==a['source']['triangles']==a['imported']['triangles']<=limit
  assert a['surface']['max_vertex_error_metres']<.000020
  assert a['source']['parents']==a['imported']['parents']
  counts[name]=b['triangles']
  for ext in ['blend','fbx']:assert sha(O/(name+'.'+ext))==a['sha256'][ext]==b['sha256'][ext],(name,ext)
  for step,mark in [('build','LIGHTHOUSE BUILT'),('audit','LIGHTHOUSE AUDIT PASS'),('render','LIGHTHOUSE RENDERS')]:
   log=(S/(name+'-'+step+'.log')).read_text(errors='replace');assert mark in log and 'Traceback' not in log,(name,step)
  rows=read(O/'renders'/(name+'.json'));studios=[v for v in rows if 'action' not in v]
  assert len(studios)==5 and {v['view'] for v in studios}==VIEWS
  assert all(v['projection']=='orthographic' and v['size']==[720,600] for v in studios)
  assert len(rows)==(15 if name=='Puffin' else 5)
  if name=='Puffin':
   assert set(a['animation'])=={'Idle','Flap'}
   assert abs(a['dimensions_unity_xyz_m'][1]-.3)<1e-6
   assert b['contract']['bones']==['Root','Body','Head','Wing.L','Wing.R']
   for clip,frames,secs in [('Idle',[1,23,46,68,91],3.),('Flap',[1,4,7,10,13],.4)]:
    c=a['animation'][clip];samples=[v for v in rows if v.get('action')==clip]
    assert [v['frame'] for v in samples]==frames
    assert all(v['size']==[640,480] and abs(v['seconds']-(v['frame']-1)/30)<1e-9 for v in samples)
    for version in ['source','imported']:
     d=c[version];assert d['seconds']==secs and d['loop'] is True and d['root_stationary_all_frames'] is True
     assert d['samples']==frames and d['frames']==[1,frames[-1]] and d['max_vertex_motion_m']>.001 and d['end_vs_start_m']<.000020
    assert set(c['samples'])==set(map(str,frames))
    assert all(d['result']=='PASS' and d['max_vertex_error_metres']<.000020 for d in c['samples'].values())
  else:assert a['animation']=={}
  for v in rows:
   assert v['file'] not in expected
   expected[v['file']]={'size':v['size'],'source_mtime':(O/(name+'.blend')).stat().st_mtime}
 g=audits['PuffinGroup'];assert abs(g['dimensions_unity_xyz_m'][0]-1.2)<1e-6
 t=audits['TideRace'];assert abs(t['dimensions_unity_xyz_m'][0]-6)<1e-6 and abs(t['dimensions_unity_xyz_m'][2]-2)<1e-6
 assert t['source']['bounds_unity'][1][1]<=.25
 glow=audits['LighthouseGlow'];assert glow['vertex_alpha_roundtrip'] is True
 assert set(glow['materials'])=={'M_LampGlow'} and glow['source']['bounds_unity'][1][0]==12
 ass=read(O/'renders/Assembly.json');assert len(ass['views'])==2
 assert {tuple(v['size']) for v in ass['views']}=={(1440,900),(844,390)}
 assert {p[0] for p in ass['placements']}=={'PuffinGroup','TideRace'}
 assert all(p[4]==1 and p[3] is None for p in ass['placements'])
 for v in ass['views']:
  assert v['projection']=='orthographic' and v['down_degrees']==45
  loX,loY,hiX,hiY=v['asset_projected_bounds_01'];assert .03<=loX<hiX<=.97 and .03<=loY<hiY<=.97
  expected[v['file']]={'size':v['size'],'source_mtime':max((O/(n+'.blend')).stat().st_mtime for n in ['PuffinGroup','TideRace'])}
 log=(S/'Assembly-render.log').read_text(errors='replace');assert 'LIGHTHOUSE RENDERS Assembly 2' in log and 'Traceback' not in log
 assert (O/'LighthouseLife-assembly-review.blend').is_file()
 review=read(O/'visual-review.json');assert len(review['images'])==len(expected)==32
 assert {v['file'] for v in review['images']}==set(expected)=={p.relative_to(O).as_posix() for p in (O/'renders').rglob('*.png')}
 production={p.name:sha(p) for n in NAMES for p in [O/(n+'.blend'),O/(n+'.fbx')]}
 assert review['production_sha256']==production,'review production hashes stale'
 for v in review['images']:
  p=O/v['file'];raw=p.read_bytes()
  assert raw[:8]==b'\x89PNG\r\n\x1a\n' and list(struct.unpack('>II',raw[16:24]))==v['size']==expected[v['file']]['size']
  assert v['opened_individually'] is True and v['review'] and sha(p)==v['sha256'],v['file']
  assert p.stat().st_mtime>=expected[v['file']]['source_mtime'],('stale PNG',v['file'])
 links=re.findall(r'\[[^\]]+\]\(([^)]+)\)',(O/'REPORT.md').read_text())
 for link in links:assert (O/link).is_file() or link=='delivery-receipt.json',('missing report link',link)
 for p in S.glob('*.py'):compile(p.read_text(),str(p),'exec')
 return {'result':'PASS','triangles':counts,'reviewed_pngs':32,'local_report_links':len(links),'unchanged_dependencies':len(deps),'limits':'Blender source/actual-FBX, two looping surface animations and individually opened isolated evidence only; native Unity/Legacy/shader/map/HUD acceptance external.'}
if __name__=='__main__':
 result=verify()
 if '--preflight' in sys.argv:print('LIGHTHOUSE PREFLIGHT PASS',json.dumps(result))
 else:
  assert not (S/'pre-refine').exists(),'Remove owned temporary backup after successful preflight.'
  assert not list(O.rglob('*.blend1'))
  files={}
  for base in [O,S]:
   for p in sorted(base.rglob('*')):
    if p.is_file() and p.name!='delivery-receipt.json' and '__pycache__' not in p.parts:
     files[p.relative_to(R).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
  receipt={'task':'LIGHTHOUSE-LIFE-1','owner':'Codex 2 (WSL CLI)','checks':result,'dependencies_sha256':read(O/'metrics/dependencies.json'),'files':files}
  path=O/'delivery-receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
  for rel,row in read(path)['files'].items():
   p=R/rel;assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],rel
  print('LIGHTHOUSE DELIVERY PASS',len(files),'files;',result['local_report_links'],'links; receipt',sha(path))

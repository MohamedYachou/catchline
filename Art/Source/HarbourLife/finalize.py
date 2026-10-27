"""Verify actual export audits and independently opened evidence; bind final bytes."""
import json,hashlib,struct,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/HarbourLife';S=R/'Art/Source/HarbourLife';U=S/'ui'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def png(p):
 b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';return list(struct.unpack('>II',b[16:24]))
def verify():
 dep=read(O/'metrics/dependencies.json');assert len(dep)==11
 for p,h in dep.items():assert sha(R/p)==h['sha256'] and (R/p).stat().st_size==h['bytes'],('dependency',p)
 expected={};prod={};tri={}
 for n,limit,height,bones,clips in [('Dog',1200,.55,14,{'Trot':(.6,19),'Sit':(3,91),'Sniff':(2,61)}),('Cat',900,.3,12,{'Sleep':(4,121),'Look':(3,91)})]:
  a=read(O/'metrics'/f'{n}-audit.json');b=read(O/'metrics'/f'{n}-build.json');assert a['result']==a['surface']['result']=='PASS'
  assert a['source']['triangles']==a['imported']['triangles']==b['triangles']<=limit;tri[n]=b['triangles']
  assert a['bone_count']==len(b['bones'])==bones<=14 and abs(a['dimensions_unity_xyz_m'][1]-height)<1e-6
  assert a['surface']['max_vertex_error_metres']<.00002 and a['source']['parents']==a['imported']['parents']
  for ext in ['blend','fbx']:
   p=O/f'{n}.{ext}';assert sha(p)==a['sha256'][ext]==b['sha256'][ext];prod[p.name]=sha(p)
  assert set(a['animation'])==set(clips)
  rows=read(O/'renders'/f'{n}.json');studios=[v for v in rows if 'action' not in v]
  assert len(studios)==5 and {v['view'] for v in studios}=={'three-quarter','front','right','back','left'}
  assert all(v['pose']=='rest' and v['size']==[720,600] for v in studios)
  for c,(secs,end) in clips.items():
   frames=[1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end];aa=a['animation'][c]
   poses=[v for v in rows if v.get('action')==c];assert [v['frame'] for v in poses]==frames
   assert all(v['size']==[640,480] and v['common_camera_within_action'] and abs(v['seconds']-(v['frame']-1)/30)<1e-9 for v in poses)
   for vers in ['source','imported']:
    x=aa[vers];assert x['seconds']==secs and x['frames']==[1,end] and x['samples']==frames
    assert x['loop'] and x['root_stationary_all_frames'] and x['end_vs_start_m']<.00003 and x['allframe_min_z_m']>=-.004
    assert x['max_vertex_motion_m']>(.0008 if c=='Sleep' else .005) and x['action_name'].endswith(c)
   assert set(aa['samples'])==set(map(str,frames)) and all(x['result']=='PASS' and x['max_vertex_error_metres']<.00002 for x in aa['samples'].values())
  assert len(rows)==5+len(clips)*5
  for v in rows:
   assert v['projection']=='orthographic' and v['source_sha256']==prod[n+'.blend'];lo,bt,hi,tp=v['projected_bounds_01'];assert .03<lo<hi<.97 and .03<bt<tp<.97
   expected['Art/Models/HarbourLife/'+v['file']]=v['size']
  for step,marker in [('build','HARBOUR BUILT'),('audit','HARBOUR AUDIT PASS'),('render','HARBOUR RENDERS')]:
   log=(S/f'{n}-{step}.log').read_text(errors='replace');assert marker in log and 'Traceback' not in log
 post=read(U/'post.json');assert len(post['cards'])==2
 for row in post['cards']:
  p=U/row['file'];assert row['size']==png(p)==[480,360] and row['mode']=='RGBA' and sha(p)==row['sha256'];assert p.read_bytes()[25]==6
  raw=U/(row['file'].replace('v2-item-','').replace('.png','-raw.png'));assert sha(raw)==row['raw_sha256']
  name=row['file'].replace('v2-item-','').replace('.png','');rr=read(U/f'{name}-render.json');assert rr['raw_sha256']==sha(raw) and rr['source_sha256']==sha(R/rr['source'])
  assert png(raw)==[960,720] and rr['camera_projection']=='orthographic' and rr['visible_meshes'] and (U/f'{name}-review.blend').is_file()
  log=(S/f'{name}-boats.log').read_text(errors='replace');assert 'HARBOUR BOAT RENDER' in log and 'Traceback' not in log
  expected[p.relative_to(R).as_posix()]=[480,360]
 assert sha(U/'comparison.png')==post['comparison_sha256'];expected[(U/'comparison.png').relative_to(R).as_posix()]=[1040,840]
 for v in post['references']:assert sha(R/v['file'])==v['sha256']
 review=read(O/'visual-review.json');assert review['production_sha256']==prod
 assert len(review['images'])==len(expected)==38 and {v['file'] for v in review['images']}==set(expected)
 for v in review['images']:
  p=R/v['file'];assert v['opened_individually'] and v['review'] and sha(p)==v['sha256'] and png(p)==expected[v['file']]==v['size']
 assert {p.relative_to(R).as_posix() for p in (O/'renders').rglob('*.png')}=={p for p in expected if p.startswith('Art/Models/')}
 links=re.findall(r'\[[^\]]+\]\(([^)]+)\)',(O/'REPORT.md').read_text())
 for link in links:assert (O/link).is_file() or link=='delivery-receipt.json',link
 for p in S.glob('*.py'):compile(p.read_text(),str(p),'exec')
 return {'result':'PASS','triangles':tri,'reviewed_pngs':38,'resolved_report_links':len(links),'unchanged_dependencies':len(dep),'native_acceptance':'External: Unity Legacy import/material conversion, scene scale/placement, HUD/refit presentation and animation playback were not run.'}
if __name__=='__main__':
 result=verify()
 if '--preflight' in sys.argv:print('HARBOUR PREFLIGHT PASS',json.dumps(result))
 else:
  assert not (S/'backup-pre-pose').exists() and not (S/'backup-pre-visual').exists()
  assert not list(O.rglob('*.blend1')) and not list(S.rglob('*.blend1'))
  files={p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for base in [O,S] for p in sorted(base.rglob('*')) if p.is_file() and p.name!='delivery-receipt.json' and '__pycache__' not in p.parts}
  rec={'task':'HARBOUR-LIFE-2','owner':'Codex 2 (WSL CLI)','checks':result,'dependencies_sha256':read(O/'metrics/dependencies.json'),'files':files};path=O/'delivery-receipt.json';path.write_text(json.dumps(rec,indent=2)+'\n')
  for rel,x in read(path)['files'].items():assert sha(R/rel)==x['sha256'] and (R/rel).stat().st_size==x['bytes'],rel
  print('HARBOUR DELIVERY PASS',len(files),'files',sha(path))

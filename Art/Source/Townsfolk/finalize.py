"""Hash-bind finished Townsfolk source/export and individually reviewed evidence."""
import hashlib,json,re,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/Townsfolk';D=Path(__file__).resolve().parent
NAMES=['Town_OldWoman','Town_Kid','Town_Fisherman','Town_Shopkeeper','Town_Walker']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def verify():
 a=read(O/'metrics/audit.json');b=read(O/'metrics/build.json');v=read(O/'visual-review.json');m=read(O/'renders/manifest.json')
 assert a['result']=='PASS' and a['bones']==20 and a['action_frame_count']==421
 assert a['all_original_source_action_curves_identical'] and a['original_actual_fbx_pose_parity']
 assert a['skeleton_source_max_error']==a['original_source_pose_max_error']==0
 assert a['skeleton_actual_fbx_reference_max_error']<=1e-6 and a['original_fbx_pose_max_error']<=2e-6
 assert a['walk_samples']==[1,7,13,19,25] and a['walk_seconds']==1
 assert set(a['people'])==set(b['people'])==set(NAMES)
 for n in NAMES:
  assert a['people'][n]==b['people'][n] and b['people'][n]['triangles']<=2500
  assert a['weights'][n]['all_vertices_weighted'] and a['weights'][n]['normalization_error']<1e-6
  assert {r['view'] for r in m if r.get('person')==n}=={'front','back','left','right','three-quarter',*[f'Walk-{i}' for i in range(5)]}
  assert [r['frame'] for r in m if r.get('person')==n and r['view'].startswith('Walk-')]==[1,7,13,19,25]
 assert set(a['actions'])=={'Bait','Carry','Cast','Cheer','Idle','Reel','Row','Stow','Strike','Wait','Walk'}
 for e in ['blend','fbx']:assert sha(O/('Townsfolk.'+e))==a['sha256'][e]==b['sha256'][e]==v['model_sha256'][e]
 assert len(m)==len(v['images'])==51
 assert {r['file'] for r in m}=={r['file'] for r in v['images']}=={p.relative_to(O).as_posix() for p in (O/'renders').rglob('*.png')}
 modeltime=max((O/('Townsfolk.'+e)).stat().st_mtime for e in ['blend','fbx'])
 for row in v['images']:
  p=O/row['file'];assert row['opened_individually'] and row['assessment'] and sha(p)==row['sha256']
  assert list(struct.unpack('>II',p.read_bytes()[16:24]))==row['size']
  assert p.stat().st_mtime>=modeltime,(row['file'],'stale render')
 for row in m:
  assert row['image_bounds_normalized'][0]>.025 and row['image_bounds_normalized'][1]<.975
  assert row['image_bounds_normalized'][2]>.025 and row['image_bounds_normalized'][3]<.975
  assert row['projection']=='orthographic'
 lineup=next(r for r in m if r['view']=='line-up');assert lineup['size']==[1800,660] and lineup['child_mesh_scale']==.75 and lineup['all_object_armature_scales']==[1,1,1]
 for p,h in read(O/'metrics/dependencies.json').items():assert sha(R/p)==h,('dependency drift',p)
 for step in ['build','audit']+['render-'+n for n in NAMES]:
  t=(D/(step+'.log')).read_text(errors='replace');assert 'TOWNSFOLK '+step.split('-')[0].upper()+' PASS' in t and 'Traceback' not in t,step
 links=re.findall(r'\[[^\]]+\]\(([^)]+)\)',(O/'REPORT.md').read_text())
 for p in links:assert (O/p).is_file() or p=='delivery-receipt.json',p
 return {'result':'PASS','bones':20,'original_actions':11,'integer_action_frames':421,'people_triangles':{n:b['people'][n]['triangles'] for n in NAMES},'reviewed_images':51,'report_links':len(links),'limits':'Artist source/actual-FBX parity and isolated Blender evidence; Unity Legacy/native integration remains external.'}
if __name__=='__main__':
 checks=verify()
 if '--preflight' in sys.argv:print('TOWNSFOLK PREFLIGHT PASS',checks);sys.exit(0)
 assert not (D/'pre-polish-backup').exists(),'Remove scoped temporary backup only after successful preflight.'
 files={}
 for base in [O,D]:
  for p in sorted(base.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts and p.name!='delivery-receipt.json':files[p.relative_to(R).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
 receipt=O/'delivery-receipt.json';receipt.write_text(json.dumps({'task':'TOWNSFOLK-1','owner':'Codex 2 (WSL CLI)','checks':checks,'files':files},indent=2)+'\n')
 for p,e in read(receipt)['files'].items():assert (R/p).stat().st_size==e['bytes'] and sha(R/p)==e['sha256']
 print('TOWNSFOLK DELIVERY PASS',len(files),checks)

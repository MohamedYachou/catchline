"""Reconcile reviewed kit deliverables without rerunning Blender or asserting native acceptance."""
import hashlib,json,re,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def verify(kit):
 o=R/'Art/Models'/kit;a=read(o/'metrics/audit.json');b=read(o/'metrics/build.json');assert a['result']=='PASS';assert a['source']['triangles']==a['imported']['triangles']==b['triangles']<=2500
 for e in ['blend','fbx']:assert sha(o/(kit+'.'+e))==a['sha256'][e]==b['sha256'][e]
 m=read(o/'renders/manifest.json');v=read(o/'visual-review.json');assert len(m)==len(v['images'])==(37 if kit=='JigKit' else 22)
 assert {x['file'] for x in m}=={x['file'] for x in v['images']}=={p.relative_to(o).as_posix() for p in (o/'renders').rglob('*.png')}
 for row in v['images']:
  p=o/row['file'];d=p.read_bytes();assert row['opened_individually'] and sha(p)==row['sha256'];assert list(struct.unpack('>II',d[16:24]))==row['size']
 for item in b['parents']:
  if item in ['KelpRibbon',kit]:continue
  assert {r['view'] for r in m if r.get('item')==item}=={'front','back','right','top','three-quarter'}
 if kit=='JigKit':
  assert [r['frame'] for r in m if r.get('action')=='Sway']==[1,31,61,91,121];assert a['sway_imported']['seconds']==4 and a['sway_imported']['loop'];assert all(x['result']=='PASS' for x in a['animation'].values())
 assert {tuple(r['size']) for r in m if '/Assembly/' in r['file']}=={(1440,900),(844,390)}
 deps=read(o/'metrics/dependencies.json')
 for rel,h in deps.items():assert sha(R/rel)==h,rel
 links=re.findall(r'\[[^\]]+\]\(([^)]+)\)',(o/'REPORT.md').read_text())
 for rel in links:assert (o/rel).is_file() or rel=='delivery-receipt.json',rel
 return {'result':'PASS','triangles':b['triangles'],'reviewed_images':len(m),'resolved_links':len(links),'limits':'Artist source/FBX and isolated Blender evidence; no Unity/native acceptance.'}
if __name__=='__main__':
 for kit in ['JigKit','RepairKit']:
  checks=verify(kit)
  if '--preflight' in sys.argv:print('KIT PREFLIGHT',kit,checks);continue
  assert not (R/'Art/Source/JigKit/pre-mote').exists();assert not (R/'Art/Source/JigKit/pre-rocks').exists()
  files={}
  for base in [R/'Art/Models'/kit,R/'Art/Source/JigKit',R/'Art/Source/RepairKit']:
   for p in sorted(base.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.name!='delivery-receipt.json':files[p.relative_to(R).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
  p=R/'Art/Models'/kit/'delivery-receipt.json';p.write_text(json.dumps({'task':'JIG-ART-1','owner':'Codex 2 (WSL CLI)','checks':checks,'files':files},indent=2)+'\n')
  for rel,e in read(p)['files'].items():assert (R/rel).stat().st_size==e['bytes'] and sha(R/rel)==e['sha256']
  print('KIT DELIVERY PASS',kit,len(files),checks)

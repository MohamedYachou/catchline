"""Validate current delivered art/evidence hashes and publish a sealed inventory."""
from pathlib import Path
import json,hashlib,re,struct
O=Path(__file__).resolve().parent;R=O.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda f:json.loads((O/f).read_text())
rows=load('props4-manifest.json');reviews=load('props4-visual-review.json');placement=load('dressing-placement.json')
assert len(rows)==10 and len({r['name'] for r in rows})==10
assert sum(r['tris'] for r in rows)==9002
entries=[e for g in ['wall','rain','festival','critic'] for e in placement[g]]
assert len(entries)==10 and {e['name'] for e in entries}=={r['name'] for r in rows}
assert [len(placement[g]) for g in ['wall','rain','festival','critic']]==[5,3,1,1]
assets=set();images=set();metas=set();delivery=set()
for r in rows:
 e=next(e for e in entries if e['name']==r['name']);assert e['file']==r['file'] and e['scale']==1
 assert len(e['position'])==3 and isinstance(e['yaw_degrees'],(int,float))
 target='dressing' if 'Wall_' in r['name'] else 'service'
 f=R/r['file'];assert f.parent==R/'Assets/Art/Models/Restaurant/Pack'/target
 assert sha(f)==r['sha256'];assert 0<r['tris']<2000
 assert r['render_review']==reviews[r['name']]['status']=='OPENED_AND_INSPECTED'
 assert len(r['renders'])==2 and set(r['renders'])==set(reviews[r['name']]['images'])
 assets.add(f);metas.add(Path(str(f)+'.meta'));delivery.add(R/r['source'])
 for render in r['renders']:
  image=R/render;raw=image.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
  assert struct.unpack('>II',raw[16:24])==(1440,900)
  assert sha(image)==reviews[r['name']]['images'][render],render
  images.add(image)
assert len(images)==20
critic=placement['critic'][0];assert critic['demo_position_only'] and critic['attach_to']=='selected_critic_table'
assert critic['surface_clearance_m']==.002
lantern=placement['festival'][0];assert lantern['position']==[-3,2.5,-2.465] and lantern['yaw_degrees']==0
metas.add(R/'Assets/Art/Models/Restaurant/Pack/dressing.meta')
new_guids={}
for meta in metas:
 guid=re.search(r'^guid: ([0-9a-f]{32})$',meta.read_text(),re.M).group(1)
 assert guid not in new_guids,(meta,new_guids.get(guid));new_guids[guid]=meta
for meta in (R/'Assets/Art/Models/Restaurant').rglob('*.meta'):
 match=re.search(r'^guid: ([0-9a-f]{32})$',meta.read_text(),re.M)
 if match and match.group(1) in new_guids:assert new_guids[match.group(1)]==meta,meta
for fn in ['props4-audit.json','props4-source-audit.json']:
 audit=load(fn);assert audit['status']=='PASS' and {i['name'] for i in audit['items']}=={r['name'] for r in rows}
for source in load('props4-source-audit.json')['items']:assert sha(R/source['source'])==source['sha256']
base=load('props4-preservation.json');external=load('props4-external-dependency-changes.json')['items'];allow={e['file']:e for e in external}
unchanged=0
for f,h in base.items():
 current=sha(R/f)
 if f in allow:assert h==allow[f]['before_sha256'] and current==allow[f]['current_sha256']
 else:assert current==h,f;unchanged+=1
assert unchanged==335 and len(allow)==1
# Preserve the already reviewed accepted PROPS-3 evidence too.
old_review=load('props3-visual-review.json');old_frames=0
for value in old_review:
 for frame in value.get('frames',[]):
  assert sha(R/frame['file'])==frame['sha256'],frame['file'];old_frames+=1
report=(O/'REPORT.md').read_text().split('# SERVICE-PROPS-4\n',1)[1]
links=re.findall(r'\]\(([^)]+)\)',report)
# Inventory itself and result are produced below before links are checked.
delivery.update(assets|metas|images)
delivery.update(O.glob('*props4*.py'));delivery.update(O.glob('props4-*.json'));delivery.add(O/'dressing-placement.json');delivery.add(O/'REPORT.md')
delivery.discard(O/'props4-artifact-check.json')
assert all(p.is_file() for p in delivery)
inventory=O/'props4-source-and-evidence.sha256'
inventory.write_text(''.join(sha(p)+'  '+p.relative_to(R).as_posix()+'\n' for p in sorted(delivery)))
result=dict(status='PASS',props=10,total_triangles=9002,production_blends=10,opened_current_frames=20,frame_size=[1440,900],unique_new_guids=len(new_guids),placements=10,preserved_dependencies=unchanged,exact_external_metadata_changes=len(allow),preserved_props3_reviewed_frames=old_frames,report_links=len(links),sealed_files=len(delivery),native_runtime_acceptance='Not run; Claude owns integration',git_commands=False,subagents=False)
(O/'props4-artifact-check.json').write_text(json.dumps(result,indent=2)+'\n')
assert all((O/f).is_file() for f in links),[f for f in links if not (O/f).is_file()]
print(json.dumps(result,indent=2))

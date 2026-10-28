"""Verify delivery completeness, report links, render evidence and import identities."""
import json,hashlib,re
from pathlib import Path
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parents[2]
records=json.loads((O/'manifest.json').read_text());reviews=json.loads((O/'review-notes.json').read_text());audit=json.loads((O/'export-audit.json').read_text())
assert len(records)==19 and len({r['name'] for r in records})==19
assert {r['name'] for r in records}=={r['name'] for r in audit['items']}==set(reviews)
assert len([r for r in records if '/dishes/' in r['file']])==8
files=[];guids=[];render_count=0
for rec in records:
 name=rec['name'];f=R/rec['file'];meta=Path(str(f)+'.meta');blend=O/'blends'/(name+'.blend')
 for p in [f,meta,blend]:assert p.is_file() and p.stat().st_size>0,p
 assert hashlib.sha256(f.read_bytes()).hexdigest()==rec['sha256']
 guids.append(re.search(r'^guid: (\w+)$',meta.read_text(),re.M).group(1));files.extend([f,meta,blend])
 assert reviews[name]['frames']==['service','close'] and 'opened' in rec['render_review']
 for p in rec['renders']:
  p=R/p;im=Image.open(p);assert im.size==(900,700) and im.format=='PNG',p;im.verify();files.append(p);render_count+=1
assert render_count==38 and len(guids)==len(set(guids))==19
folder=R/'Assets/Art/Models/Restaurant/Pack/service.meta';assert folder.exists() and 'folderAsset: yes' in folder.read_text();files.append(folder)
for n in ['sink-fit-service.png','sink-fit-close.png']:
 p=O/'renders'/n;im=Image.open(p);im.verify();files.append(p)
report=O/'REPORT.md';assert report.exists()
for link in re.findall(r'\]\(([^)]+)\)',report.read_text()):
 if link not in {'artifact-check.json','source-and-evidence.sha256'}:assert (O/link).resolve().exists(),link
assert not list((O/'blends').glob('*.blend1')),'Temporary backups remain'
result=dict(status='PASS',items=19,required_renders=render_count,extra_sink_fit_renders=2,authored_blends=19,unique_fbx_guids=len(set(guids)),report_links='PASS',individual_open_review_notes=19,fbx_roundtrip=audit['status'],preserved_dependency_count=audit['untouched_dependency_count'],native_unity='Not run; runtime integration is separate')
(O/'artifact-check.json').write_text(json.dumps(result,indent=2)+'\n')
files.extend(p for p in O.rglob('*') if p.is_file() and p.name!='source-and-evidence.sha256' and '__pycache__' not in p.parts and not p.name.endswith('.blend1'))
files=sorted(set(files));(O/'source-and-evidence.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(R))+'\n' for p in files))
print(json.dumps(result));print('HASHED_FILES',len(files))

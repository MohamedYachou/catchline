"""Bind final manually reviewed NET-ART-1 evidence and delivery to exact bytes.
Run only after opening every final image. Does not substitute for visual review.
"""
import json,hashlib,re,struct,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/NetKit';S=R/'Art/Source/NetKit'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
assert not (S/'_revision-backup').exists()
assert not (S/'__pycache__').exists()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=json.loads((O/'renders/NetBunt.json').read_text())+json.loads((O/'renders/NetPanelSet.json').read_text())+json.loads((O/'assembly.json').read_text())['images']
assert len(rows)==24 and len({r['file'] for r in rows})==24
assert {p.relative_to(O).as_posix() for p in O.rglob('*.png')}=={r['file'] for r in rows}
for row in rows:
    p=O/row['file'];raw=p.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
    dims=list(struct.unpack('>II',raw[16:24]));assert dims==row['size']
    row.update(sha256=sha(p),reviewer='Codex 2 (WSL CLI)',opened_individually=True,result='PASS',review_basis='Direct image inspection recorded in comms.md NET-ART-1 D checkpoints; no clipped asset, modeled net holes and correct subject/state visible.')
write(O/'visual-review.json',{'task':'NET-ART-1','recorded_utc':now,'status':'24 final frames individually opened and visually reviewed','images':rows,'native_acceptance':False})
for n in ('NetBunt','NetPanelSet'):
    m=json.loads((O/'metrics'/(n+'.json')).read_text());assert m['round_trip']['result']=='PASS'
    assert m['triangles']<m['limit']
    if n=='NetPanelSet':assert all(m['objects'][k]['triangles']<800 for k in ('NetPanel','NetHeap'))
    for ext in ('blend','fbx'):assert sha(O/(n+'.'+ext))==m['sha256'][ext]
    for step,marker in (('build','NET BUILT'),('audit','NET AUDIT PASS'),('render','NET RENDERS')):
        log=(S/(n+'-'+step+'.log')).read_text();assert marker in log and 'Traceback' not in log
for n in ('fbx-axes','fixture-audit'):
    m=json.loads((O/'metrics'/(n+'.json')).read_text())
    assert m['result']=='PASS' if n=='fixture-audit' else all(r['result']=='PASS' for r in m.values())
for step,marker in (('assembly','NET ASSEMBLY'),('axes','NET AXES PASS'),('fixture_audit','NET FIXTURE AUDIT PASS')):
    log=(S/('NetKit-'+step+'.log')).read_text();assert marker in log and 'Traceback' not in log
meta=json.loads((O/'assembly.json').read_text())
for rel,digest in meta['readonly_dependencies_sha256'].items():assert sha(R/rel)==digest,rel
report=(O/'REPORT.md').read_text();links=re.findall(r'\]\(([^)]+)\)',report)
for link in links:
    if link=='delivery-receipt.json':continue
    assert (O/link).resolve().is_file(),link
assert all(r['file'] in links for r in rows)
files=[]
for folder in (O,S):
    for p in sorted(folder.rglob('*')):
        if not p.is_file() or p==O/'delivery-receipt.json':continue
        assert p.stat().st_size>0,p
        assert p.suffix not in ('.blend1','.pyc'),p
        files.append({'file':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
receipt={'task':'NET-ART-1','owner':'Codex 2 (WSL CLI)','recorded_utc':now,'delivery':'Artist source/export/evidence complete','native_acceptance':False,'remaining':'Claude Unity import/material/blendshape/Fill wiring and desktop/phone runtime review','final_pngs_reviewed':24,'blend_fbx_pairs':2,'meshes':3,'readonly_fixture_dependencies_sha256':meta['readonly_dependencies_sha256'],'report_links_checked':len(links),'files':files}
write(O/'delivery-receipt.json',receipt)
# Read receipt and every bound file back, including the authoring/verification scripts.
read=json.loads((O/'delivery-receipt.json').read_text())
for row in read['files']:
    p=R/row['file'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],p
print('NET FINAL DELIVERY PASS',len(files),'bound files;',len(rows),'reviewed PNGs;',len(links),'report links; receipt SHA256',sha(O/'delivery-receipt.json'))

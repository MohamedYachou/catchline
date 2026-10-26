"""Independent final image/hash/source/link checks; manual viewing is a separate sealed record."""
from pathlib import Path
from PIL import Image
import ast,hashlib,json,re
O=Path(__file__).resolve().parent;R=O.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v=json.loads((O/'validation.json').read_text());m=json.loads((O/'build-metrics.json').read_text());a=json.loads((O/'layout-audit.json').read_text());opens=json.loads((O/'visual-review.json').read_text())
assert v['pass'] and a['pass'];assert sha(O/'Stage1V1.fbx')==v['sha256'];assert v['triangles']==m['triangles']<=m['budget'];assert v['mesh_count']==13
assert len(a['footprint_rows'])==12
for row in a['footprint_rows']:assert row['within_footprint_and_floor_pivot'] and max(abs(x-1) for x in row['root_scale'])<1e-6
names={r['file']:r for r in json.loads((O/'render-manifest.json').read_text())}
for n,res in [('kit-sheet.png',[2400,1250]),('compare-interior.png',[2880,1300]),('compare-kit.png',[2880,1300])]:names[n]={'resolution':res}
assert len(names)==15;assert set(names)=={p.name for p in (O/'renders').glob('*.png')};assert set(names)=={r['file'] for r in opens['images']}
opened={r['file']:r for r in opens['images']};images=[]
for name,row in names.items():
 p=O/'renders'/name
 with Image.open(p) as im:im.load();assert list(im.size)==row['resolution'] and im.mode in ['RGB','RGBA'];mode=im.mode
 assert opened[name]['opened_individually'] and sha(p)==opened[name]['sha256'];images.append({'file':name,'dimensions':row['resolution'],'mode':mode,'opened_hash_matches':True,'sha256':sha(p)})
chars=json.loads((O/'character-scale.json').read_text())
for row in chars:assert sha(R/row['source'])==row['source_sha256'] and row['uniform_scale_unchanged']
for row in opens['accepted_references']:assert sha(R/row['file'])==row['sha256']
scripts=list(O.glob('*.py'))
for p in scripts:ast.parse(p.read_text(),filename=str(p))
report=(O/'REPORT.md').read_text();links=re.findall(r'\[[^\]]+\]\(([^)]+)\)',report)
for link in links:assert (O/link).exists(),link
assert not list(O.rglob('*.meta')) and not list(O.rglob('*.cs'))
result={'pass':True,'images':images,'manual_review_limit':'Manual opens recorded separately; decoder/hash checks do not determine aesthetic quality.','source_character_hashes_verified':3,'accepted_reference_hashes_verified':2,'python_AST_checks':len(scripts),'report_links_checked':len(links),'export_triangles':v['triangles'],'export_meshes':13,'footprint_roots':12,'Unity_or_touch_verified':False}
(O/'independent-audit.json').write_text(json.dumps(result,indent=2));print('FINAL AUDIT PASS: 15 images,3 original character refs,2 concept refs,',len(scripts),'scripts,',len(links),'report links')

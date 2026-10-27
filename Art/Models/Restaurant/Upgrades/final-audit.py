"""Seal current technical audits and the explicitly opened visual evidence."""
from pathlib import Path
import json,hashlib
from PIL import Image
O=Path(__file__).resolve().parent;W=O.parent/'Stage1V4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((O/'manifest.json').read_text());v=json.loads((O/'validation.json').read_text());assert v['pass'] and len(v['assets'])==16
byname={r['name']:r for r in v['assets']}
for r in manifest['assets']:
 assert sha(O/(r['name']+'.fbx'))==r['fbx_sha256']==byname[r['name']]['fbx_sha256'];assert json.loads((O/(r['name']+'.footprint.json')).read_text())==r
for name,digest in manifest['atlas_hashes'].items():assert sha(O/'textures'/name)==sha(W/'textures'/name)==digest
assert byname['TableCandle']['meshes']==['TableCandle','TableCandle_Flame'] or set(byname['TableCandle']['meshes'])=={'TableCandle','TableCandle_Flame'}
w=json.loads((W/'backwall-validation.json').read_text());assert w['pass'] and sha(W/'Stage1V4.fbx')==w['fbx_sha256'];assert w['unchanged_source_geometry_transform_secondaryUV_meshes']==239
steam=json.loads((O/'Steam/validation.json').read_text());assert steam['pass'] and len(steam['frames'])==8
sheet=Image.open(O/'Steam/steam-sheet.png');assert sheet.size==(2048,256) and sheet.mode=='RGBA'
for i,r in enumerate(steam['frames']):
 p=O/'Steam'/r['file'];assert sha(p)==r['sha256'];im=Image.open(p);assert im.mode=='RGBA' and im.size==(256,256);assert sheet.crop((i*256,0,(i+1)*256,256)).tobytes()==im.tobytes()
for root,ledger in [(O,'visual-review.json'),(W,'backwall-visual-review.json')]:
 data=json.loads((root/ledger).read_text());assert data['opened_by']=='Codex 2 (WSL CLI)'
 for r in data['images']:assert sha(root/r['file'])==r['sha256']
 assert data['native_unity_acceptance_claimed'] is False
for p in list(O.glob('*.py'))+list(W.glob('backwall-*.py')):compile(p.read_text(),str(p),'exec')
files=[O/'manifest.json',O/'validation.json',O/'REPORT.md',O/'visual-review.json',O/'Steam/validation.json',O/'Steam/steam.json',O/'Steam/steam-sheet.png',W/'Stage1V4.fbx',W/'Stage1V4.blend',W/'backwall-validation.json',W/'backwall-REPORT.md',W/'backwall-visual-review.json']
(O/'final-audit.json').write_text(json.dumps({'pass':True,'assets':16,'table_assemblies':6,'standalone_chairs':3,'other_props_including_candle':7,'steam_frames':8,'V4_nodes_preserved':239,'all_current_FBX_hashes_match_fresh_import_audits':True,'UV_bounds_origins_footprints_verified':True,'atlas_byte_identical':True,'current_opened_visual_hashes_verified':True,'native_unity_unverified':True,'artifacts':{str(p.relative_to(O.parent)):sha(p) for p in files}},indent=2));print('FINAL ART AUDIT PASS')

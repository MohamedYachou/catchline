"""Read-only delivery checks; no Blender or upstream mutations."""
from pathlib import Path
import json,hashlib,ast,gzip
O=Path(__file__).resolve().parent;C=O.parent/'Clothes';V=O.parent/'Stage1V4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
a=read(C/'workclips-validation.json');m=read(C/'workclips-manifest.json')
assert a['pass'] and a['bone_count']==20 and a['all_meshes_preserved'] and a['fps']==24
assert len(a['original_mesh_preservation'])==19 and all(all(v.values()) for v in a['original_mesh_preservation'].values())
assert a['fbx_sha256']==m['fbx_sha256']==sha(C/'CrewRig_Restaurant.fbx')
assert a['source_sha256']==sha(O.parents[3]/'Assets/Art/Models/Crew/CrewRig.fbx')
assert {r['name'] for r in m['clips']}==set('Cook Chop Pour Wipe Wash Repair Greet CarryPlate TakeOrder'.split())
assert sum(r['loop'] for r in m['clips'])==8
snapshot=json.loads(gzip.decompress((C/'workclips-baseline-measurements.json.gz').read_bytes()));assert snapshot['baseline_fbx_sha256']==a['baseline_fbx_sha256']
b=read(O/'validation.json');metrics=read(O/'build-metrics.json')
assert b['pass'] and b['FBX_sha256']==sha(O/'Stage2Bistro.fbx')
assert b['mesh_count']==len(metrics['production_meshes'])==213 and b['triangles']==metrics['room_triangles']==154060
assert metrics['source_V4_sha256']==sha(V/'Stage1V4.blend')
for name in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:assert sha(O/'textures'/name)==sha(V/'textures'/name)
layout=read(O/'layout.json');assert layout['tile_m']==1 and layout['room_tiles']==[10,5] and sum(t['seats'] for t in layout['terrace_tables'])==10
cameras=read(O/'final-cameras.json');original=read(V/'final-cameras.json')
for c,v in zip(cameras,original):
 assert c['rotation_blender_rad']==v['rotation_blender_rad'] and c['lens_mm']==v['lens_mm'] and c['resolution']==v['resolution']
opened={}
for folder,file in [(C,'workclips-visual-review.json'),(O,'visual-review.json')]:
 for rel,h in read(folder/file)['opened'].items():assert sha(folder/rel)==h,rel;opened[str(folder.name)+'/'+rel]=h
for folder,pattern in [(C,'workclips-*.py'),(O,'*.py')]:
 for p in folder.glob(pattern):ast.parse(p.read_text())
files=[O/'Stage2Bistro.blend',O/'Stage2Bistro.fbx',O/'Bistro-V4-check.blend',O/'layout.json',O/'lighting.json',O/'final-cameras.json',O/'validation.json',O/'REPORT.md',C/'CrewRig_Restaurant.blend',C/'CrewRig_Restaurant.fbx',C/'workclips-validation.json',C/'workclips-REPORT.md']
assert not (C/'_workclips-backup').exists()
(O/'final-audit.json').write_text(json.dumps({'pass':True,'workclip_names':[r['name'] for r in m['clips']],'rig_preservation_pass':True,'bistro_fresh_FBX_pass':True,'upstream_V4_unchanged':True,'atlas_byte_identical':True,'camera_orientation_and_lens_match_V4':True,'temporary_rig_backup_removed':True,'files':{str(p.relative_to(O.parent)):sha(p) for p in files},'opened_visuals':opened,'native_unity_acceptance_unverified':True},indent=2))
print('FINAL AUDIT PASS',len(files),'delivery hashes,',len(opened),'opened visuals')

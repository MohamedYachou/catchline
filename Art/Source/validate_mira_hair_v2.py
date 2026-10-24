"""Original-rig/source/actual-FBX audit plus r20 nonhair and full-circle hair proof."""
import bpy,hashlib,json,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/CrewV2/Mira-sol';BASE=OUT/'iterations/r20'
sys.path.insert(0,str(ROOT/'Art/Source'))
from crew_female_coverage import audit
man=json.loads((OUT/'build-manifest.json').read_text());p=man['r20_preservation']
for name,digest in p['archive_sha256'].items():assert hashlib.sha256((BASE/name).read_bytes()).hexdigest()==digest,('r20 archive changed',name)
def mesh_fingerprint(ob):
 me=ob.data
 return hashlib.sha256(repr(([tuple(v.co) for v in me.vertices],[(tuple(p.vertices),p.material_index,p.use_smooth) for p in me.polygons],[m.name for m in me.materials],[[ (ob.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in me.vertices],[[tuple(x.uv) for x in uv.data] for uv in me.uv_layers])).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Mira.blend'))
expected={name:mesh_fingerprint(bpy.data.objects[name]) for name in p['five_nonhair_fingerprints']}
assert expected==p['five_nonhair_fingerprints']
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Mira.blend'))
assert {name:mesh_fingerprint(bpy.data.objects[name]) for name in expected}==expected
assert hashlib.sha256((OUT/'Mira_Face.png').read_bytes()).hexdigest()==p['archive_sha256']['Mira_Face.png']
coverage=audit(bpy,'Mira',OUT,man['revision'],'waves',hair_name='Mira_HairSculpt',hat_name='Mira_OfficerCap')
# Existing independent validator reopens both the source and the exported FBX.
runpy.run_path(str(ROOT/'Art/Source/validate_mira_sol.py'),run_name='__main__')
result=json.loads((OUT/'validation.json').read_text())
# Check hair image/UV on the actual imported FBX, in addition to face proof above.
ob=bpy.data.objects['Mira_HairSculpt'];assert ob.data.uv_layers.active
images=[n.image for mat in ob.data.materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
assert images
for image in images:
 path=Path(bpy.path.abspath(image.filepath));assert path.is_file()
 assert hashlib.sha256(path.read_bytes()).hexdigest()==hashlib.sha256((OUT/'Mira_Hair.png').read_bytes()).hexdigest()
result.update(revision=man['revision'],hair_coverage=coverage,r20_nonhair_fingerprints=expected,r20_nonhair_exact=True,r20_face_texture_exact=True,hair_uv_and_actual_fbx_texture_resolve=True,delivery_sha256={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ('Mira.blend','Mira.fbx','Mira_Face.png','Mira_Hair.png','build-manifest.json')})
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS full-hair revision: five r20 nonhair meshes exact, r20 face texture exact, archive unchanged, source+actual FBX, radial scalp gaps zero',flush=True)

import bpy,json,math,hashlib,gzip
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders';P.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clear():bpy.ops.wm.read_factory_settings(use_empty=True)
def bind(rig,clip):
 a=next(a for a in bpy.data.actions if a.name.split('|')[-1]==clip);rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
def inventory():
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';bpy.context.view_layer.update()
 bones={b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local]} for b in rig.data.bones};meshes={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  meshes[o.name]={'v':[[round(x,6) for x in v.co] for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'mat':[m.name for m in o.data.materials],'mi':[p.material_index for p in o.data.polygons],'w':[{o.vertex_groups[g.group].name:round(g.weight,5) for g in v.groups} for v in o.data.vertices],'uv':[[[round(x,6) for x in v.uv] for v in uv.data] for uv in o.data.uv_layers]}
 clips={a.name.split('|')[-1]:list(a.frame_range) for a in bpy.data.actions};motions={}
 rig.data.pose_position='POSE'
 for clip,frames in clips.items():
  bind(rig,clip);out=[]
  for f in [frames[0]+(frames[1]-frames[0])*t/4 for t in range(5)]:
   bpy.context.scene.frame_set(int(f));bpy.context.view_layer.update();out.append({b.name:[list(r) for r in b.matrix] for b in rig.pose.bones})
  motions[clip]=out
 return rig,bones,meshes,clips,motions

baseline=O/'_mira-match-backup/CrewRig_Restaurant.fbx';snapshot=O/'mira-match-baseline-measurements.json.gz'
if baseline.exists():
 clear();bpy.ops.import_scene.fbx(filepath=str(baseline));_,rb,rm,rc,ra=inventory();baseline_hash=sha(baseline)
 snapshot.write_bytes(gzip.compress(json.dumps({'hash':baseline_hash,'bones':rb,'meshes':rm,'clips':rc,'poses':ra},separators=(',',':')).encode()))
else:
 data=json.loads(gzip.decompress(snapshot.read_bytes()));rb,rm,rc,ra=[data[k] for k in ['bones','meshes','clips','poses']];baseline_hash=data['hash']
clear();bpy.ops.import_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'));rig,b,m,c,a=inventory()
assert set(b)==set(rb) and len(b)==20
assert all(b[n]['parent']==rb[n]['parent'] for n in b)
rest=max(abs(b[n]['matrix'][i][j]-rb[n]['matrix'][i][j]) for n in b for i in range(4) for j in range(4));assert rest<1e-5
assert c==rc
motion={clip:max(abs(a[clip][f][n][i][j]-ra[clip][f][n][i][j]) for f in range(5) for n in b for i in range(4) for j in range(4)) for clip in c};assert max(motion.values())<1e-4,motion
changed={'Hat_HairUpClip'};assert set(m)==set(rm)
preservation={n:row==m[n] for n,row in rm.items() if n not in changed};assert all(preservation.values()),preservation
bounds=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 if o.name in changed:assert all(v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in o.data.vertices),o.name
 assert all(mod.object==rig for mod in o.modifiers if mod.type=='ARMATURE')
 pts=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)];assert max(hi[k]-lo[k] for k in range(3))<1.5
 bounds.append({'name':o.name,'min_m':lo,'max_m':hi,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)})
(O/'mira-match-validation.json').write_text(json.dumps({'pass':True,'fbx_sha256':sha(O/'CrewRig_Restaurant.fbx'),'baseline_sha256':baseline_hash,'bone_count':len(b),'rest_max_delta':rest,'clips':c,'all_clip_pose_max_deltas':motion,'unchanged_meshes':preservation,'refined_existing_mesh_names':sorted(changed),'all_names_stable':True,'refined_mesh_weights_normalized':True,'legacy_weights_preserved':True,'meshes':bounds,'native_unverified':True},indent=2));print('MIRA MATCH VALIDATION PASS')

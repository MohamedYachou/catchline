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
baseline=O/'_workclips-backup/CrewRig_Restaurant.fbx';snapshot=O/'workclips-baseline-measurements.json.gz'
if baseline.exists():
 clear();bpy.ops.import_scene.fbx(filepath=str(baseline));_,rb,rm,rc,ra=inventory();baseline_hash=sha(baseline)
 snapshot.write_bytes(gzip.compress(json.dumps({'baseline_fbx_sha256':baseline_hash,'bones':rb,'meshes':rm,'clips':rc,'poses':ra},separators=(',',':')).encode()))
else:
 data=json.loads(gzip.decompress(snapshot.read_bytes()));rb,rm,rc,ra=[data[k] for k in ['bones','meshes','clips','poses']];baseline_hash=data['baseline_fbx_sha256']
clear();bpy.ops.import_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'));rig,b,m,c,a=inventory()
assert b.keys()==rb.keys();assert all(b[n]['parent']==rb[n]['parent'] for n in b)
rest=max(abs(b[n]['matrix'][i][j]-rb[n]['matrix'][i][j]) for n in b for i in range(4) for j in range(4));assert rest<1e-5,rest
assert all(c.get(n)==v for n,v in rc.items()),(c,rc)
newclips={r['name']:r for r in json.loads((O/'workclips-manifest.json').read_text())['clips']}
assert set(c)==set(rc)|set(newclips)
for n,row in newclips.items():assert c[n]==row['frames'],(n,c[n],row)
motion={clip:max(abs(a[clip][f][n][i][j]-ra[clip][f][n][i][j]) for f in range(5) for n in b for i in range(4) for j in range(4)) for clip in rc};assert max(motion.values())<1e-4,motion
preservation={n:{k:m[n][k]==v for k,v in row.items()} for n,row in rm.items()};assert all(all(row.values()) for row in preservation.values()),preservation
expected=[];assert set(m)==set(rm)
rig.data.pose_position='REST';bounds=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 # No new skin data: compare every existing weight exactly to the baseline above.
 assert all(mod.object==rig for mod in o.modifiers if mod.type=='ARMATURE')
 vs=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];assert max(hi[i]-lo[i] for i in range(3))<1.5,(o.name,lo,hi)
 bounds.append({'mesh':o.name,'bounds':[lo,hi],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)})
(O/'workclips-validation.json').write_text(json.dumps({'pass':True,'source_sha256':sha(R/'Assets/Art/Models/Crew/CrewRig.fbx'),'fbx_sha256':sha(O/'CrewRig_Restaurant.fbx'),'bone_count':len(b),'rest_max_delta':rest,'original_mesh_preservation':preservation,'clips':c,'all_clip_motion_max_deltas':motion,'meshes':bounds,'added_mesh_names':expected,'weights_unchanged':True,'new_skin_weights_introduced':False,'native_unity_unverified':True},indent=2));print('WORKCLIPS PRESERVATION PASS',flush=True)

loops={};spans={};rig.data.pose_position='POSE'
for n,row in newclips.items():
 bind(rig,n);samples=[];hands=[]
 for frame in range(row['frames'][0],row['frames'][1]+1):
  bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();samples.append({p.name:[list(r) for r in p.matrix] for p in rig.pose.bones});hands.append({s:list(rig.pose.bones[s+'Hand'].head) for s in ['Left','Right']})
 loops[n]=max(abs(samples[0][b][i][j]-samples[-1][b][i][j]) for b in samples[0] for i in range(4) for j in range(4))
 if row['loop']:assert loops[n]<2e-5,(n,loops[n])
 spans[n]={s:[max(h[s][k] for h in hands)-min(h[s][k] for h in hands) for k in range(3)] for s in ['Left','Right']}
 motiondelta=max(abs(samples[f][b][i][j]-samples[0][b][i][j]) for f in range(len(samples)) for b in samples[0] for i in range(4) for j in range(4));assert motiondelta>.015,(n,motiondelta)
 if n=='CarryPlate':assert max(spans[n][s][2] for s in spans[n])<.0001,spans[n]
p=O/'workclips-validation.json';v=json.loads(p.read_text());v.update({'baseline_fbx_sha256':baseline_hash,'all_meshes_preserved':True,'new_clip_endpoint_matrix_deltas':loops,'new_clip_hand_travel_m':spans,'fps':bpy.context.scene.render.fps,'clip_loop_flags_require_unity_import_settings':True});assert v['fps']==24;p.write_text(json.dumps(v,indent=2))
print('WORKCLIPS VALIDATION PASS',flush=True)

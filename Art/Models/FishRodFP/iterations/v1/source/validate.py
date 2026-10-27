"""Independent saved-source / actual-FBX audits, run with Windows Blender 5.2."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'Art/Models/FishRodFP'
M=json.loads((OUT/'build-manifest.json').read_text()); report={}
def evaluated(ob):
 e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=e.to_mesh()
 pts=[e.matrix_world@v.co for v in me.vertices];e.to_mesh_clear()
 assert all(math.isfinite(x) for v in pts for x in v)
 return pts
def sample(rig,mesh,a,f):
 rig.animation_data_create();rig.animation_data.action=a
 bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
 return {'heads':{p.name:list(rig.matrix_world@p.head) for p in rig.pose.bones},
         'vertices':[list(p) for p in evaluated(mesh)]}
def structure(rig):return {b.name:b.parent.name if b.parent else None for b in rig.data.bones}
def meshcheck(ob,rig):
 ob.data.calc_loop_triangles();t=len(ob.data.loop_triangles)
 assert t==M['triangles'] and t<6000,t
 assert len(ob.data.materials)==1
 assert ob.data.uv_layers.active
 maxw=0
 for v in ob.data.vertices:
  assert v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-5,v.index
  assert all(ob.vertex_groups[g.group].name in rig.data.bones for g in v.groups)
  maxw=max(maxw,sum(g.weight>1e-6 for g in v.groups))
 assert maxw<=4,maxw
 return {'triangles':t,'vertices':len(ob.data.vertices),'max_weights':maxw,'normalized':True}
bpy.ops.wm.open_mainfile(filepath=str(OUT/'FishRodFP.blend'))
rig=bpy.data.objects['FishRodFP_Rig'];mesh=bpy.data.objects['FishRodFP_Mesh']
assert tuple(rig.scale)==(1,1,1) and tuple(mesh.scale)==(1,1,1)
assert bpy.context.scene.render.fps==40
assert bpy.context.scene.unit_settings.scale_length==1
assert len(rig.data.bones)==14 and len(bpy.data.actions)==7
assert set(bpy.data.actions.keys())==set(M['clips'])
report['source']=meshcheck(mesh,rig); hierarchy=structure(rig)
tip=rig.data.bones['LineTip'].head_local
butt=Vector((0,.956304756*.28,-.292371705*.28))
assert abs((tip-butt).length-2.1)<1e-5,(tip-butt).length
report['source']['rod_length_m']=(tip-butt).length
for i in range(1,9):
 b=rig.data.bones['Rod_%02d'%i]
 assert b.parent.name==('RodRoot' if i==1 else 'Rod_%02d'%(i-1))
 if i>1:assert (b.head_local-b.parent.tail_local).length<1e-7
source={};durations={};loops={}
for name,clip in M['clips'].items():
 a=bpy.data.actions[name];lo,hi=a.frame_range
 assert abs(lo)<.001 and abs(hi-clip['frames'][1])<.001,(name,lo,hi)
 durations[name]=(hi-lo)/40
 for f in range(int(hi)+1):
  source[(name,f)]=sample(rig,mesh,a,f)
 # Loop endpoints must agree in actual deformation, even when crank angles differ by 2pi.
 if clip['loop']:
  p=source[(name,0)]['vertices'];q=source[(name,int(hi))]['vertices']
  err=max((Vector(x)-Vector(y)).length for x,y in zip(p,q))
  assert err<1e-5,(name,'loop discontinuity',err)
  loops[name]=err
report['source']['clip_durations']=durations
report['source']['action_pose_samples']=len(source)
report['source']['loop_endpoint_max_error_m']=loops
# Check direct procedural bend at all 3 requested amounts and tangent continuity.
rig.animation_data.action=None
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
curves={}
for amount in [0,.5,1]:
 for i,r in enumerate(M['bend_radians_at_1']):rig.pose.bones['Rod_%02d'%(i+1)].rotation_euler.x=r*amount
 bpy.context.view_layer.update()
 ps=[rig.pose.bones['Rod_%02d'%i].head.copy() for i in range(1,9)]+[rig.pose.bones['Rod_08'].tail.copy()]
 angles=[(ps[i]-ps[i-1]).angle(ps[i+1]-ps[i]) for i in range(1,8)]
 assert max(angles)<=.261,angles
 curves[str(amount)]={'bone_polyline':[list(p) for p in ps],'max_adjacent_bone_angle_rad':max(angles)}
report['procedural_bend']=curves
# Actual PNG palette values, relative path and one image shader.
images=[n.image for n in mesh.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE']
assert len(images)==1 and tuple(images[0].size)==(256,256)
assert Path(bpy.path.abspath(images[0].filepath)).resolve()==(OUT/'FishRodFP_Atlas.png').resolve()
report['texture']={'size':[256,256],'relative_path':images[0].filepath,'one_material':True}
rest=structure(rig)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT/'FishRodFP.fbx'),use_anim=True)
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(rigs)==1 and len(meshes)==1
assert len(bpy.context.scene.objects)==2,'Review stage leaked to FBX'
rig=rigs[0];mesh=meshes[0]
assert structure(rig)==hierarchy
report['fbx']=meshcheck(mesh,rig)
imported_images=[n.image for n in mesh.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE']
assert len(imported_images)==1
assert Path(bpy.path.abspath(imported_images[0].filepath)).resolve()==(OUT/'FishRodFP_Atlas.png').resolve()
report['fbx']['atlas_resolves']=True
actions={a.name.split('|')[-1]:a for a in bpy.data.actions}
assert set(actions)==set(M['clips']),list(actions)
maxbone=maxvert=0
# Import converts the FBX scene frame rate to its explicit source fps.
report['fbx']['fps']=bpy.context.scene.render.fps
assert bpy.context.scene.render.fps==40
for (name,f),s in source.items():
 # Blender's FBX importer intentionally starts imported clips at frame 1.
 # Compare clip-relative time, not two different absolute timeline origins.
 imported_start=round(actions[name].frame_range[0])
 assert abs((actions[name].frame_range[1]-imported_start)-M['clips'][name]['frames'][1])<.001
 actual=sample(rig,mesh,actions[name],f+imported_start)
 be=max((Vector(s['heads'][n])-Vector(actual['heads'][n])).length for n in s['heads'])
 assert len(actual['vertices'])==len(s['vertices'])
 ve=max((Vector(x)-Vector(y)).length for x,y in zip(s['vertices'],actual['vertices']))
 maxbone=max(maxbone,be);maxvert=max(maxvert,ve)
 assert be<.0001,(name,f,'bone',be)
 assert ve<.0002,(name,f,'mesh',ve)
report['fbx'].update({'pose_samples':len(source),'comparison':'clip-relative frames; source starts0, FBX importer starts1','max_bone_error_m':maxbone,'max_vertex_error_m':maxvert,'stage_excluded':True})
report['sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'FishRodFP.blend',OUT/'FishRodFP.fbx',OUT/'FishRodFP_Atlas.png']}
report['status']='PASS'
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('FISH ROD VALIDATION PASS',json.dumps(report['fbx']))

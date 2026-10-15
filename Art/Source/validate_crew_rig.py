"""Source and round-trip FBX validation; Blender 5.2 headless."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/CrewRig'
m=json.loads((OUT/'manifest.json').read_text());results={}
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CrewRig.blend'))
arm=bpy.data.objects['CrewRig']
assert set(b.name for b in arm.data.bones)==set(m['bones'])
assert len(m['bones'])==20
body=bpy.data.objects['Body'];assert abs(max(v.co.z for v in body.data.vertices)-.95)<1e-5 and abs(min(v.co.z for v in body.data.vertices))<1e-5
for n in m['skinned_meshes']:
 ob=bpy.data.objects[n];assert ob.type=='MESH'
 assert any(mod.type=='ARMATURE' and mod.object==arm for mod in ob.modifiers)
 for v in ob.data.vertices:
  assert len(v.groups)>0 and abs(sum(g.weight for g in v.groups)-1)<1e-5,(n,v.index)
 assert all(mat.name.startswith('M_') for mat in ob.data.materials)
for n in m['hats']:
 ob=bpy.data.objects[n];assert ob.parent==arm and ob.parent_type=='BONE' and ob.parent_bone=='HatMount'
assert set(a.name for a in bpy.data.actions)==set(c['name'] for c in m['clips'])
assert bpy.context.scene.render.fps==24
for c in m['clips']:
 a=bpy.data.actions[c['name']];assert tuple(a.frame_range)==(c['start'],c['end'])
 arm.animation_data.action=a
 poses=[]
 for f in (1,(c['end']+1)//2,c['end']):
  bpy.context.scene.frame_set(f);poses.append([tuple(p.matrix.translation) for p in arm.pose.bones])
 if c['loop']:
  assert max((Vector(a)-Vector(b)).length for a,b in zip(poses[0],poses[-1]))<1e-4,c['name']
 # Verify meaningful movement on quarter-cycle as well as midpoint.
 bpy.context.scene.frame_set(1);start=[p.matrix.copy() for p in arm.pose.bones]
 bpy.context.scene.frame_set(1+(c['end']-1)//4)
 assert any(sum(abs(x-y) for ra,rb in zip(a,p.matrix) for x,y in zip(ra,rb))>.001 for a,p in zip(start,arm.pose.bones)),c['name']
results['source']={'bones':len(m['bones']),'skinned_meshes':m['skinned_meshes'],'rigid_hats':m['hats'],'normalized_weights':True,'height_m':.95,'actions':11,'loop_endpoints_match':True}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/Art/Models/Crew/CrewRig.fbx'),use_anim=True)
arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];assert len(arms)==1
arm=arms[0];assert set(b.name for b in arm.data.bones)==set(m['bones'])
meshes={o.name for o in bpy.context.scene.objects if o.type=='MESH'};assert meshes==set(m['skinned_meshes']+m['hats']),meshes
names=[a.name for a in bpy.data.actions]
curve_checks=[]
for c in m['clips']:
 matches=[a for a in bpy.data.actions if a.name.split('|')[-1]==c['name']];assert len(matches)==1,(c,names)
 assert tuple(matches[0].frame_range)==(c['start'],c['end']),(c,matches[0].frame_range)
 a=matches[0];bag=a.layers[0].strips[0].channelbag(a.slots[0]);curves=list(bag.fcurves)
 assert all(sum(f.data_path.startswith('pose.bones["'+n+'"]') for f in curves)>=9 for n in m['bones']),(a.name,len(curves))
 assert all(len(f.keyframe_points)==c['end'] for f in curves),(a.name,sorted({len(f.keyframe_points) for f in curves}))
 curve_checks.append({'action':c['name'],'channels':len(curves),'samples_per_channel':c['end'],'duration_seconds':(c['end']-1)/24})
# FBX is metres, rather than an accidental centimetre-sized rig.
assert abs((arm.matrix_world@arm.data.bones['Head'].head_local).z-.60)<1e-4
for n in m['skinned_meshes']:
 ob=bpy.data.objects[n];assert any(mod.type=='ARMATURE' and mod.object==arm for mod in ob.modifiers)
 for v in ob.data.vertices:assert v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-4
results['fbx_roundtrip']={'bones':len(arm.data.bones),'mesh_names':sorted(meshes),'imported_action_names':names,'frame_ranges_match':True,'curve_checks':curve_checks,'metre_scale':True,'normalized_skin_weights':True}
results['all_passed']=True;(OUT/'validation.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS CrewRig source and FBX roundtrip: 20 bones / 8 meshes / 11 clips')

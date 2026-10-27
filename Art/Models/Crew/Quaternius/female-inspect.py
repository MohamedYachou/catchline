import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[4]
S=R/'Art/Downloads/quaternius/base/Universal Base Characters[Standard]'
bpy.ops.wm.read_factory_settings(use_empty=True)
out=[]
for path in [S/'Base Characters/Unity/Superhero_Female_FullBody.fbx',S/'Hairstyles/Rigged to Head Bone/FBX (Unity)/Hair_Buns.fbx',S/'Hairstyles/Rigged to Head Bone/FBX (Unity)/Eyebrows_Female.fbx']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(path))
 data=[]
 for o in bpy.context.scene.objects:
  d=dict(name=o.name,type=o.type,loc=list(o.location),scale=list(o.scale),rotation=list(o.rotation_euler),parent=o.parent.name if o.parent else None,parent_type=o.parent_type,parent_bone=o.parent_bone)
  if o.type=='ARMATURE': d['bones']=[dict(name=b.name,parent=b.parent.name if b.parent else None,head=list(b.head_local),tail=list(b.tail_local)) for b in o.data.bones]
  if o.type=='MESH':
   d.update(verts=len(o.data.vertices),polys=len(o.data.polygons),materials=[m.name for m in o.data.materials],groups=[g.name for g in o.vertex_groups],bounds=[list(v) for v in o.bound_box])
   d['mat_counts']={str(i):sum(p.material_index==i for p in o.data.polygons) for i in range(len(o.data.materials))}
  data.append(d)
 out.append(dict(path=str(path),objects=data))
Path(__file__).with_name('female-source-inspection.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))

import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/mnt/c/Users/momoy/Projects/Catchline');out=[]
for n in ['dishes/Restaurant_Dish_GrilledFish','dishes/Restaurant_Dish_FilletsLemon','dishes/Restaurant_Dish_Lemonade','Restaurant_SinkDishRack']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 __import__('io_scene_fbx.import_fbx',fromlist=['load']).load(type('Reporter',(),{'report':lambda *a:print(*a[1:])})(),bpy.context,filepath=str(R/'Assets/Art/Models/Restaurant/Pack'/f'{n}.fbx'))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH']; vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 rec=dict(name=n,blender_min=lo,blender_max=hi,size=[hi[i]-lo[i] for i in range(3)],meshes=[])
 for o in obs:
  o.data.calc_loop_triangles();u=o.data.uv_layers.active
  rec['meshes'].append(dict(name=o.name,tris=len(o.data.loop_triangles),materials=[m.name for m in o.data.materials],location=list(o.location),rotation=list(o.rotation_euler),uvrange=[list(min(d.uv[i] for d in u.data) for i in range(2)),list(max(d.uv[i] for d in u.data) for i in range(2))] if u else None))
 out.append(rec)
print(json.dumps(out,indent=2));(R/'Art/Source/RestaurantService/reference-measurements.json').write_text(json.dumps(out,indent=2))

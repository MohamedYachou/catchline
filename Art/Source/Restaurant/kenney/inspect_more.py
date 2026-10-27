import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];records={}
for kind,name,path in [('kenney','sushi-salmon',R/'Art/Downloads/kenney/food/Models/GLB format/sushi-salmon.glb'),('kenney','fries',R/'Art/Downloads/kenney/food/Models/GLB format/fries.glb'),('kaykit','rings',R/'Art/Downloads/kaykit/restaurant/addons/kaykit_restaurant_bits/Assets/fbx(unity)/food_ingredient_onion_rings.fbx'),('catchline','crab',R/'Art/Models/Props/Crab.blend')]:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if path.suffix=='.glb':bpy.ops.import_scene.gltf(filepath=str(path))
 elif path.suffix=='.fbx':bpy.ops.import_scene.fbx(filepath=str(path))
 else:
  with bpy.data.libraries.load(str(path),link=False) as (a,b):b.objects=[n for n in a.objects]
  for o in b.objects:
   if o:bpy.context.scene.collection.objects.link(o)
 rows=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  verts=o.data.vertices;adj={i:set() for i in range(len(verts))}
  for e in o.data.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
  left=set(adj);parts=[]
  while left:
   stack=[min(left)];part=set()
   while stack:
    v=stack.pop()
    if v in part:continue
    part.add(v);stack.extend(adj[v]-part)
   left-=part;vs=[o.matrix_world@verts[i].co for i in part]
   parts.append(dict(first=min(part),count=len(part),min=[min(p[i] for p in vs) for i in range(3)],max=[max(p[i] for p in vs) for i in range(3)]))
  rows.append(dict(name=o.name,components=parts,materials=[m.name for m in o.data.materials]))
 records[name]=rows
(O/'component-inventory.json').write_text(json.dumps(records,indent=2))

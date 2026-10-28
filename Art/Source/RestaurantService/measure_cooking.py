import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Matrix
sys.dont_write_bytecode=True
R=Path('/mnt/c/Users/momoy/Projects/Catchline');O=R/'Art/Source/RestaurantService';P=R/'Assets/Art/Models/Restaurant/Pack'
from io_scene_fbx import import_fbx
class Op:
 def report(self,*a):print(*a)
out=[]
for n in ['Stove','Grill','Fryer','Oven','Steamer','SoupKettle','PrepCounter','TableFor2','TableFor4']:
 path=P/('Restaurant_'+n+'.fbx')
 if not path.exists():continue
 bpy.ops.wm.read_factory_settings(use_empty=True);import_fbx.load(Op(),bpy.context,filepath=str(path),use_anim=False)
 bpy.context.view_layer.update();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
 # Updated importer matrices are Blender Z-up. Surface y is Unity height; footprint bounds are Blender XY.
 faces=[]
 for ob in obs:
  for f in ob.data.polygons:
   pts=[ob.matrix_world@ob.data.vertices[i].co for i in f.vertices]
   if max(p.z for p in pts)-min(p.z for p in pts)<.0001:
    faces.append(dict(y=round(sum(p.z for p in pts)/len(pts),6),area=f.area,bounds=[[min(p[i] for p in pts) for i in [0,1]],[max(p[i] for p in pts) for i in [0,1]]],material=ob.data.materials[f.material_index].name if ob.data.materials else ''))
 out.append(dict(name=n,bounds_blender_zup=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],meshes=[o.name for o in obs],horizontal_faces=sorted(faces,key=lambda a:a['area'],reverse=True)[:65]))
(O/'cooking-measurements.json').write_text(json.dumps(out,indent=2))
for a in out:print(a['name'],a['bounds'],json.dumps(a['horizontal_faces'][:16]))
# Room imports already in Z up.
bpy.ops.wm.read_factory_settings(use_empty=True);import_fbx.load(Op(),bpy.context,filepath=str(R/'Assets/Resources/Restaurant/Stage1V4.fbx'),use_anim=False)
bpy.context.view_layer.update();rec=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];rec.append(dict(name=ob.name,bounds_blender_zup=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]))
(O/'cooking-room-objects.json').write_text(json.dumps(rec,indent=2));print('ROOM',json.dumps(rec))

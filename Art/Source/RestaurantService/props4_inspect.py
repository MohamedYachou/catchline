import bpy,sys,json
from pathlib import Path
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));import build_props3 as p
from mathutils import Vector
b=p.b;bpy.ops.wm.read_factory_settings(use_empty=True)
obs=b.load_fbx(p.R/'Assets/Resources/Restaurant/Stage1V4.fbx');bpy.context.view_layer.update();rows=[]
for o in obs:
 if o.type!='MESH':continue
 v=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in v) for i in range(3)];hi=[max(v[i] for v in v) for i in range(3)]
 if True:rows.append(dict(name=o.name,min_blender=lo,max_blender=hi))
(O/'props4-room-measurements.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=1))
shell=next(o for o in obs if o.name=='EXPORT_RoomShell')
for y in [1.1,.3,-.4,-1.3]:
 for z in [.55,.95,1.2]:
  hit,co,n,fi=shell.ray_cast(shell.matrix_world.inverted()@Vector((2,y,z)),shell.matrix_world.inverted().to_3x3()@Vector((1,0,0)))
  print('RIGHTCONTACT',y,z,hit,tuple(shell.matrix_world@co))
for ob in b.load_fbx(p.R/'Assets/Resources/Restaurant/RestaurantPier.fbx'):
 par=ob;names=[]
 while par:names.append(par.name);par=par.parent
 if not any(s.startswith(('Pier_S2','Pier_S3','Pier_S4')) for s in names):obs.append(ob)
bpy.context.view_layer.update()
for x,y in [(-2.7,-3.94),(2.55,-3.65),(3.85,-2.9)]:
 hits=[]
 for ob in obs:
  if ob.type!='MESH':continue
  hit,co,n,fi=ob.ray_cast(ob.matrix_world.inverted()@Vector((x,y,5)),ob.matrix_world.inverted().to_3x3()@Vector((0,0,-1)))
  if hit:
   co=ob.matrix_world@co
   if co.z<.5:hits.append((co.z,ob.name))
 print('FLOOR',x,y,sorted(hits,reverse=True)[:4])

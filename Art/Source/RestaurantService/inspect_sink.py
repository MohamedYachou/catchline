import sys,math,json,bpy
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_service as b
bpy.ops.wm.read_factory_settings(use_empty=True)
obs=b.load_fbx(b.PACK/'Restaurant_SinkDishRack.fbx')
for ob in obs:
 if not ob.parent:ob.matrix_world=Matrix.Rotation(math.pi/2,4,'X')@ob.matrix_world
for ob in obs:
 if ob.type!='MESH':continue
 for m in ob.data.materials:
  if m and m.use_nodes:
   for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE':n.image=bpy.data.images.load(str(b.PACK/'restaurantbits_texture-catchline.png'),check_existing=True)
 # Dominant upper horizontal faces identify the actual basin and countertop surface.
 polys=[]
 for p in ob.data.polygons:
  vs=[ob.matrix_world@ob.data.vertices[i].co for i in p.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
  if min(v.z for v in vs)>.55 and p.area>.002:polys.append(dict(area=p.area,lo=lo,hi=hi))
 (b.O/'sink-upper-faces.json').write_text(json.dumps(polys,indent=2))
cam=b.setup_stage();b.place_camera(cam,(0,0,.45),2.8,55);bpy.context.scene.cycles.samples=24
bpy.context.scene.render.filepath=str(b.REND/'reference-sink-inspection.png');bpy.ops.render.render(write_still=True)

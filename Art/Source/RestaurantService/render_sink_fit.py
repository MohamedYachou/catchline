"""Read-only assembly evidence against the existing sink; no source model changes."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_service as b
bpy.ops.wm.read_factory_settings(use_empty=True)
for path,shift in [(b.PACK/'Restaurant_SinkDishRack.fbx',Vector((0,0,0))),(b.PACK/'service/Restaurant_SinkPile6.fbx',Vector((.39866665,-.041,.323)))]:
 obs=b.load_fbx(path)
 for ob in obs:
  if not ob.parent:ob.matrix_world=Matrix.Translation(shift)@Matrix.Rotation(math.pi/2,4,'X')@ob.matrix_world
 for ob in obs:
  if ob.type!='MESH':continue
  for m in ob.data.materials:
   if m and m.name.startswith('RestaurantAtlas'):
    ob.data.materials.clear();ob.data.materials.append(b.atlas_material());break
   if m and m.use_nodes:
    for n in m.node_tree.nodes:
     if n.type=='TEX_IMAGE':n.image=bpy.data.images.load(str(b.PACK/'restaurantbits_texture-catchline.png'),check_existing=True)
cam=b.setup_stage();bpy.context.scene.cycles.samples=64
b.place_camera(cam,(.05,0,.43),2.7,38)
bpy.context.scene.render.filepath=str(b.REND/'sink-fit-service.png');bpy.ops.render.render(write_still=True)
b.place_camera(cam,(.38,-.04,.43),1.05,55)
bpy.context.scene.render.filepath=str(b.REND/'sink-fit-close.png');bpy.ops.render.render(write_still=True)
print('SINK_FIT_RENDERED',flush=True)

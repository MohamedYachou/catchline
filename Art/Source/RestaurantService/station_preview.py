import sys,importlib.util,math,bpy
from pathlib import Path
from mathutils import Matrix,Vector
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('base',O/'build_service.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
bpy.ops.wm.read_factory_settings(use_empty=True);b.MAT=b.atlas_material()
for i,n in enumerate(['Stove','Grill','Fryer','Oven','Steamer','SoupKettle','PrepCounter']):
 obs=b.load_fbx(b.PACK/f'Restaurant_{n}.fbx')
 for o in obs:
  if not o.parent:o.matrix_world=Matrix.Translation((i*1.5,0,0))@Matrix.Rotation(math.pi/2,4,'X')@o.matrix_world
  if o.type=='MESH':
   o.data.materials.clear();o.data.materials.append(b.MAT)
cam=b.setup_stage();bpy.context.scene.cycles.samples=24;bpy.context.scene.render.resolution_x=1800;bpy.context.scene.render.resolution_y=600
b.place_camera(cam,(4.5,0,.5),11.5,38);bpy.context.scene.render.filepath=str(O/'renders/cooking-stations-inspection.png');bpy.ops.render.render(write_still=True)

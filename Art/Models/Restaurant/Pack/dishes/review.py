"""Fresh exported FBXs, no build scene reuse. Table/detail/contact evidence."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;R=O.parents[4]
sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import reset,load,bounds
from build_fit import component,instantiate,scene_setup

def render(rec):
 reset();obs=load(O/(rec['name']+'.fbx'));food=[o for o in obs if o.type=='MESH']
 for ob in food:
  # Bake restored Blender importer axis conversion for unambiguous proof placement.
  ob.data=ob.data.copy();ob.data.transform(ob.matrix_world);ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.location.z=.692
 tc=component('table_round_A',(.54,.54,.69),(0,0,0),pack='kaykit')
 tableobs=instantiate(tc,'KayKit game-size round table')
 s=scene_setup(target=(0,0,.55),span=1.25,width=720,height=600)
 s.render.engine='BLENDER_EEVEE';s.render.film_transparent=False
 s.render.filepath=str(O/'renders'/(rec['name']+'-table.png'));bpy.ops.render.render(write_still=True)
 # Independent detail view, same game pitch/yaw/lens, exactly same scale for every item.
 cam=s.camera;target=Vector((0,0,.734));v=cam.location-Vector((0,0,.55));cam.location=target+v*(.34/1.25)
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(O/'renders'/(rec['name']+'-detail.png'));bpy.ops.render.render(write_still=True)
 print('REVIEWED',rec['name'],flush=True)

if __name__=='__main__':
 for rec in json.loads((O/'manifest.json').read_text())['items']:render(rec)

import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;P=O/'workclips-renders';P.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'));sc=bpy.context.scene;rig=next(o for o in sc.objects if o.type=='ARMATURE')
sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.world=bpy.data.worlds.new('RestaurantNight');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.18,.26,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size,col in [((-2,-3,4),170,3,(1,.83,.64)),((2,-1,2.5),100,2,(.66,.83,1)),((0,2,3),180,2,(1,.72,.42))]:
 data=bpy.data.lights.new('REVIEW_Softbox','AREA');data.energy=power;data.color=col;data.shape='DISK';data.size=size;ob=bpy.data.objects.new(data.name,data);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.5))-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('REVIEW_V4Camera',bpy.data.cameras.new('REVIEW_V4Camera'));sc.collection.objects.link(cam);sc.camera=cam;v4=json.loads((O.parent/'Stage1V4/final-cameras.json').read_text())[0];cam.rotation_euler=v4['rotation_blender_rad'];cam.data.lens=58;cam.location=Vector((0,0,.48))+cam.rotation_euler.to_matrix()@Vector((0,0,3.1));sc.render.resolution_x=360;sc.render.resolution_y=440;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.view_settings.view_transform='AgX'
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);return m
navy=mat('REVIEW_Navy',(.03,.08,.15));wood=mat('REVIEW_Wood',(.33,.19,.08));ivory=mat('REVIEW_Ivory',(.8,.75,.61));steel=mat('REVIEW_Steel',(.19,.25,.29))
props=[]
def box(n,loc,dims,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name='REVIEW_'+n;ob.dimensions=dims;ob.data.materials.append(m);props.append(ob);return ob

def cylinder(n,loc,r,h,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=h,location=loc);ob=bpy.context.object;ob.name='REVIEW_'+n;ob.data.materials.append(m);props.append(ob);return ob
rows=json.loads((O/'workclips-manifest.json').read_text())['clips']
for row in rows:
 name=row['name'];outfit='Outfit_CookWhites' if name in ['Cook','Chop','Wash'] else 'Outfit_HostFormal' if name=='Greet' else 'Outfit_Handyman' if name=='Repair' else 'Outfit_Barista' if name=='Pour' else 'Outfit_WaiterSuit';hat='Hat_Toque' if outfit=='Outfit_CookWhites' else 'Hat_HairUpClip' if outfit=='Outfit_HostFormal' else None
 for ob in sc.objects:
  if ob.type=='MESH':ob.hide_render=ob.name not in ['Body',outfit,hat]
 rig.animation_data_create();a=next(a for a in bpy.data.actions if a.name.split('|')[-1]==name);rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
 for idx,t in enumerate([0,.25,.5,.75]):
  for ob in props:bpy.data.objects.remove(ob,do_unlink=True)
  props=[];sc.frame_set(1+round((row['frames'][1]-1)*t));bpy.context.view_layer.update();r=rig.pose.bones['RightHand'].tail.copy();l=rig.pose.bones['LeftHand'].tail.copy()
  if name in ['Cook','Chop','Pour','Wipe','Wash']:
   box('Counter',(0,-.32,.375),(.52,.32,.05),wood)
  if name=='Cook':
   cylinder('Pan',(0,-.32,.424),.108,.04,navy);box('PanHandle',(.13,-.29,.44),(.18,.035,.025),navy);ob=cylinder('Spoon',r+Vector((0,0,-.06)),.009,.15,wood)
  elif name=='Chop':
   box('Board',(0,-.32,.41),(.28,.20,.02),wood);box('Knife',r+Vector((.0,-.01,-.035)),(.11,.016,.07),steel)
  elif name=='Pour':
   cylinder('Cup',l+Vector((0,0,-.025)),.038,.065,ivory);ob=cylinder('Jug',r+Vector((0,0,.018)),.044,.085,steel);ob.rotation_euler.y=-.5-.4*math.sin(t*math.pi)**2
  elif name=='Wipe':box('Cloth',r+Vector((0,0,-.02)),(.12,.10,.014),ivory)
  elif name=='Wash':
   cylinder('Basin',(0,-.30,.409),.12,.018,steel);ob=cylinder('Dish',(r+l)/2,.07,.014,ivory);ob.rotation_euler.x=.6
  elif name=='Repair':
   box('LowMachine',(0,-.33,.18),(.30,.22,.34),navy);box('HammerHandle',r,(.018,.018,.13),wood);box('HammerHead',r+Vector((0,0,.075)),(.10,.035,.035),steel)
  elif name=='CarryPlate':cylinder('Plate',(r+l)/2+Vector((0,0,.012)),.15,.018,ivory)
  elif name=='TakeOrder':
   ob=box('Notepad',l+Vector((0,0,.018)),(.13,.10,.018),ivory);ob.rotation_euler.x=.16;box('Pencil',r,(.008,.008,.09),wood)
  sc.render.filepath=str(P/(name+'-'+str(idx)+'.png'));bpy.ops.render.render(write_still=True)
 print('WORKCLIP RENDER',name,flush=True)
print('WORKCLIPS RENDER PASS',flush=True)

"""Render actual reimported Stage1V2 FBX with shared atlas restored by explicit recipe."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders'
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
bpy.ops.import_scene.fbx(filepath=str(O/'Stage1V2.fbx'),colors_type='LINEAR');bpy.context.view_layer.update()
metrics=json.loads((O/'build-metrics.json').read_text());meshes=[o for o in sc.objects if o.type=='MESH']
# FBX cannot encode an arbitrary node graph: load only the material datablock from authored production blend.
# Geometry remains fresh FBX. These nodes exactly match the documented URP texture/vertex-colour recipe.
with bpy.data.libraries.load(str(O/'Stage1V2.blend'),link=False) as (src,dst):dst.materials=['Restaurant_Atlas_URP']
atlasmat=dst.materials[0]
for ob in meshes:ob.data.materials.clear();ob.data.materials.append(atlasmat)
# Independent render from FBX; original module roots and positions preserved.
env=list(sc.objects);module_roots={o.name:o for o in env if o.type=='EMPTY'}
sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=True;sc.cycles.device='GPU'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.render.threads_mode='FIXED';sc.render.threads=6;sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.35
sc.world=bpy.data.worlds.new('CoolAmbient');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.29,.43,.68,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.18
# Unity can set clear colour independently of ambient lighting; camera-ray background does that here.
worldnodes=sc.world.node_tree.nodes;worldlinks=sc.world.node_tree.links
cam_bg=worldnodes.new('ShaderNodeBackground');cam_bg.name='CreamClearColour';cam_bg.inputs[0].default_value=(.008,.035,.065,1);cam_bg.inputs[1].default_value=1
lp=worldnodes.new('ShaderNodeLightPath');mix=worldnodes.new('ShaderNodeMixShader');worldlinks.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);worldlinks.new(worldnodes['Background'].outputs[0],mix.inputs[1]);worldlinks.new(cam_bg.outputs[0],mix.inputs[2]);worldlinks.new(mix.outputs[0],worldnodes['World Output'].inputs[0]);sc.render.film_transparent=False
lights=[]
def light(name,typ,pos,power,col,radius=0):
 d=bpy.data.lights.new(name,typ);d.energy=power;d.color=col
 if typ=='POINT':d.shadow_soft_size=radius
 o=bpy.data.objects.new('REVIEW_'+name,d);sc.collection.objects.link(o);o.location=pos;lights.append(o);return o
sun=light('WarmKey','SUN',(-3,-4,7),.30,(.65,.76,1));sun.rotation_euler=(Vector((0,0,0))-sun.location).to_track_quat('-Z','Y').to_euler();sun.data.angle=math.radians(9)
lantern_positions=metrics['architectural_lantern_positions_m']
for i,(x,y,z) in enumerate(lantern_positions):light('Lantern'+str(i+1),'POINT',(x,y,z+.16),90,(1,.57,.22),.16)
for i,(x,y,z) in enumerate([(1.32,.84,.84),(1.2,-1.4,.85)]):light('Candle'+str(i+1),'POINT',(x,y,z+.12),9,(1,.62,.30),.11)
for i,x in enumerate([-2.65,-.6,1.45]):light('Window'+str(i+1),'POINT',(x,-2.95,.6),18,(1,.59,.24),.28)
light('KitchenWarmFill','AREA',(-2.5,.4,3.5),190,(1,.77,.47),.55)
lights[-1].data.shape='DISK';lights[-1].data.size=4
light('DiningWarmFill','AREA',(1.6,.3,3.8),150,(1,.81,.57),.55)
lights[-1].data.shape='DISK';lights[-1].data.size=4
lighting={'render_engine':'Cycles OPTIX 48 samples denoised','view_transform':'AgX Medium High Contrast','exposure_ev':.35,'world_linear_rgb':[.29,.43,.68],'world_strength':.18,'sun':{'energy':.30,'linear_rgb':[.65,.76,1],'source_position':[-3,-4,7],'target':[0,0,0],'angular_diameter_deg':9},'points':[{'name':o.name,'position_blender_m':list(o.location),'watts':o.data.energy,'linear_rgb':list(o.data.color),'source_radius_m':o.data.shadow_soft_size} for o in lights if o.data.type=='POINT'],'area_lights':[{'name':o.name,'position_m':list(o.location),'watts':o.data.energy,'linear_rgb':list(o.data.color),'size_m':o.data.size} for o in lights if o.data.type=='AREA'],'bloom':False,'dof':False,'global_outline':False,'note':'Cycles indirect diffuse/contact shadows require URP baked room lightmap + probes or restrained SSAO; numerical watt-to-URP intensity parity is not asserted.'}
(O/'lighting.json').write_text(json.dumps(lighting,indent=2))
# Import exact existing crew, use common Idle action and retain selected original ship outfit.
characters=[];character_rows=[]
def character(src,name,loc,outfit=None,hat=None,yaw=0):
 previous=set(sc.objects);bpy.ops.import_scene.fbx(filepath=str(R/src));new=list(set(sc.objects)-previous);arm=next(o for o in new if o.type=='ARMATURE')
 if outfit:
  for o in new:
   if o.type=='MESH' and (o.name.startswith('Outfit_') or o.name.startswith('Hat_')):o.hide_render=not(o.name.split('.')[0] in [outfit,hat]);o.hide_viewport=o.hide_render
 idle=next((a for a in bpy.data.actions if a.name.endswith('Idle')),None)
 if idle:
  arm.animation_data_create();arm.animation_data.action=idle
  if idle.slots:arm.animation_data.action_slot=idle.slots[0]
 wrapper=bpy.data.objects.new('REVIEW_'+name+'_placement',None);sc.collection.objects.link(wrapper)
 for o in new:
  if not o.parent:o.parent=wrapper
 wrapper.location=loc;wrapper.rotation_euler.z=math.radians(yaw);new.append(wrapper)
 sc.frame_set(12);bpy.context.view_layer.update()
 deps=bpy.context.evaluated_depsgraph_get();pts=[]
 for o in new:
  if o.type=='MESH' and not o.hide_render:
   ev=o.evaluated_get(deps);pts.extend(ev.matrix_world@v.co for v in ev.data.vertices)
 character_rows.append({'name':name,'source':src,'source_sha256':hashlib.sha256((R/src).read_bytes()).hexdigest(),'position_blender_m':loc,'height_m':max(p.z for p in pts)-min(p.z for p in pts),'uniform_scale_unchanged':True,'outfit':outfit,'hat':hat,'action':idle.name if idle else 'rest','frame':12});characters.extend(new)
character('Assets/Art/Models/Crew/CrewRig.fbx','Cook',(-2.4,.84,.07),'Outfit_Deckhand','Hat_Beanie',90)
character('Assets/Art/Models/Crew/CrewRig.fbx','Waiter',(.1,-.3,.07),'Outfit_Captain','Hat_CaptainCap',-20)
character('Art/Models/CrewV2/Mira-sol/Mira.fbx','Mira',(2.9,-1.20,.07),yaw=0)
(O/'character-scale.json').write_text(json.dumps(character_rows,indent=2))
cam=bpy.data.objects.new('REVIEW_Camera52',bpy.data.cameras.new('Camera52'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.lens=50;cam.data.clip_end=200
render_records=[]
def frame_camera(points,res,pitch=52,yaw=0,padding=1.12):
 sc.render.resolution_x,sc.render.resolution_y=res;target=Vector((0,0,.3));a=math.radians(pitch);b=math.radians(yaw);cam.location=target+Vector((math.sin(b)*math.cos(a),-math.cos(b)*math.cos(a),math.sin(a)))*20;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();iv=cam.matrix_world.inverted();ps=[iv@p for p in points];dx=(max(p.x for p in ps)+min(p.x for p in ps))/2;dy=(max(p.y for p in ps)+min(p.y for p in ps))/2;cam.location+=cam.matrix_world.to_quaternion()@Vector((dx,dy,0));cam.data.ortho_scale=max(max(p.x for p in ps)-min(p.x for p in ps),(max(p.y for p in ps)-min(p.y for p in ps))*res[0]/res[1])*padding
 return cam.data.ortho_scale
pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
for res in [(1440,900),(844,390)]:
 label='room-'+str(res[0])+'x'+str(res[1]);scale=frame_camera(pts,res);sc.render.filepath=str(P/(label+'.png'));bpy.ops.render.render(write_still=True);render_records.append({'file':label+'.png','resolution':res,'pitch_deg':52,'yaw_deg':0,'ortho_horizontal_span_m':scale,'camera_position':list(cam.location),'camera_rotation_rad':list(cam.rotation_euler),'HUD_or_touch_tested':False});print('STAGE1 RENDER',label,flush=True)
# Save reproducible review scene; not a production FBX; contains references and lights.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'LookProof.blend'))

# Kit proof grouped sheets are separate renders, with library items imported individually.
for o in characters:o.hide_render=True
for o in env:o.hide_render=True
# Hide room fixtures' local point lights; broad rig for library inspection remains.
for o in lights:
 if o.data.type=='POINT':o.hide_render=True
sc.world.node_tree.nodes['CreamClearColour'].inputs[0].default_value=(.32,.39,.42,1)
kit=json.loads((O/'build-metrics.json').read_text())['roots']
for row in kit:
 name=row['root']
 if name=='RoomShell' or name.endswith('_B'):continue
 before=set(sc.objects);bpy.ops.import_scene.fbx(filepath=str(O/row['fbx']),colors_type='LINEAR');new=list(set(sc.objects)-before);parts=[o for o in new if o.type=='MESH']
 for ob in parts:ob.data.materials.clear();ob.data.materials.append(atlasmat)
 bpy.context.view_layer.update();pp=[o.matrix_world@v.co for o in parts for v in o.data.vertices]
 frame_camera(pp,(480,420),52,-18,1.20);sc.render.filepath=str(P/('kit-'+name+'.png'));bpy.ops.render.render(write_still=True)
 render_records.append({'file':'kit-'+name+'.png','resolution':[480,420],'pitch_deg':52,'yaw_deg':-18,'source_fbx':row['fbx']})
 for ob in new:bpy.data.objects.remove(ob,do_unlink=True)
 print('V2 ITEM RENDER',name,flush=True)
(O/'render-manifest.json').write_text(json.dumps(render_records,indent=2));print('V2 RENDERS COMPLETE',flush=True)

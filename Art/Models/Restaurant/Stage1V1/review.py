"""Reimport production FBX, verify metres/mesh bounds/triangles then render the actual export."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders'
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;bpy.ops.import_scene.fbx(filepath=str(O/'Stage1V1.fbx'));bpy.context.view_layer.update()
metrics=json.loads((O/'build-metrics.json').read_text());source={r['name']:r for r in metrics['rows']};objs=list(sc.objects);meshes=[o for o in objs if o.type=='MESH'];rows=[];delta=0
for o in meshes:
 pts=[o.matrix_world@v.co for v in o.data.vertices];assert all(math.isfinite(x) for p in pts for x in p);lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)];tri=sum(len(p.vertices)-2 for p in o.data.polygons);s=source[o.name];err=max(abs(a-b) for aa,bb in [(lo,s['min_m']),(hi,s['max_m'])] for a,b in zip(aa,bb));delta=max(delta,err)
 assert tri==s['triangles'];assert o.parent.name==s['parent'];assert err<.0001;assert all(-5.1<lo[i] and hi[i]<5.1 for i in range(3));assert 'REVIEW' not in o.name
 rows.append({'name':o.name,'parent':o.parent.name,'min_m':lo,'max_m':hi,'triangles':tri,'bounds_delta_m':err})
fbx,_=parse_fbx.parse(str(O/'Stage1V1.fbx'));settings=next(e for e in fbx.elems if e.id==b'GlobalSettings');prop=next(e for e in settings.elems if e.id==b'Properties70');unit=next(e.props[-1] for e in prop.elems if e.props[0]==b'UnitScaleFactor');assert unit==100
assert len(rows)==len(source);total=sum(r['triangles'] for r in rows);assert total==metrics['triangles'] and total<=60000
record={'pass':True,'unit_scale_factor':unit,'triangles':total,'budget':60000,'mesh_count':len(rows),'max_source_export_bounds_delta_m':delta,'no_presentation_floor_or_extra_mesh':True,'room_floor_dimensions_m':[8,5],'kitchen_floor_dimensions_m':[3,5],'native_Unity_verified':False,'sha256':hashlib.sha256((O/'Stage1V1.fbx').read_bytes()).hexdigest(),'rows':rows}
(O/'validation.json').write_text(json.dumps(record,indent=2));print('STAGE1 EXPORT AUDIT PASS',total,len(rows),delta,flush=True)
if '--audit-only' in sys.argv:sys.exit(0)
# Independent render from FBX; original module roots and positions preserved.
env=list(sc.objects);module_roots={o.name:o for o in env if o.type=='EMPTY'}
sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=True;sc.cycles.device='GPU'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.render.threads_mode='FIXED';sc.render.threads=6;sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.5
sc.world=bpy.data.worlds.new('CoolAmbient');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.65,.8,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.35
# Unity can set clear colour independently of ambient lighting; camera-ray background does that here.
worldnodes=sc.world.node_tree.nodes;worldlinks=sc.world.node_tree.links
cam_bg=worldnodes.new('ShaderNodeBackground');cam_bg.name='CreamClearColour';cam_bg.inputs[0].default_value=(1,.94,.78,1);cam_bg.inputs[1].default_value=1
lp=worldnodes.new('ShaderNodeLightPath');mix=worldnodes.new('ShaderNodeMixShader');worldlinks.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);worldlinks.new(worldnodes['Background'].outputs[0],mix.inputs[1]);worldlinks.new(cam_bg.outputs[0],mix.inputs[2]);worldlinks.new(mix.outputs[0],worldnodes['World Output'].inputs[0]);sc.render.film_transparent=False
lights=[]
def light(name,typ,pos,power,col,radius=0):
 d=bpy.data.lights.new(name,typ);d.energy=power;d.color=col
 if typ=='POINT':d.shadow_soft_size=radius
 o=bpy.data.objects.new('REVIEW_'+name,d);sc.collection.objects.link(o);o.location=pos;lights.append(o);return o
sun=light('WarmKey','SUN',(-3,-4,7),2.1,(1,.82,.63));sun.rotation_euler=(Vector((0,0,0))-sun.location).to_track_quat('-Z','Y').to_euler();sun.data.angle=math.radians(9)
for i,(x,y) in enumerate([(-3.8,2.3),(.15,2.3),(3.8,2.3),(3.82,-1.18)]):light('Lantern'+str(i+1),'POINT',(x,y,1.13),45,(1,.64,.29),.18)
light('KitchenCeiling','POINT',(-2.4,.2,2.7),100,(1,.82,.57),.55)
lighting={'render_engine':'Cycles OPTIX 48 samples denoised','view_transform':'AgX Medium High Contrast','exposure_ev':.5,'world_linear_rgb':[.55,.65,.8],'world_strength':.35,'sun':{'energy':2.1,'linear_rgb':[1,.82,.63],'source_position':[-3,-4,7],'target':[0,0,0],'angular_diameter_deg':9},'points':[{'name':o.name,'position_blender_m':list(o.location),'watts':o.data.energy,'linear_rgb':list(o.data.color),'source_radius_m':o.data.shadow_soft_size} for o in lights if o.data.type=='POINT'],'area_lights':0,'bloom':False,'dof':False,'global_outline':False,'note':'Cycles indirect diffuse/contact shadows require URP baked room lightmap + probes or restrained SSAO; numerical watt-to-URP intensity parity is not asserted.'}
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
character('Assets/Art/Models/Crew/CrewRig.fbx','Cook',(-2.32,.62,.03),'Outfit_Deckhand','Hat_Beanie',90)
character('Assets/Art/Models/Crew/CrewRig.fbx','Waiter',(.15,.1,.03),'Outfit_Captain','Hat_CaptainCap',-20)
character('Art/Models/CrewV2/Mira-sol/Mira.fbx','Mira',(2.7,-.92,.03),yaw=0)
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
# Isolated kit renders use the identical export geometry and lighting, not new models.
for o in characters:o.hide_render=True
for o in env:o.hide_render=True
kit=['PrepCounter','Stove','SoupKettle','Fridge','SinkDishRack','CoffeeMachine','TableFor2','ReceptionDesk','PassCounter','TrashCan']
for name in kit:
 root=module_roots[name];children=[o for o in env if o.parent==root];oldloc=root.location.copy();oldrot=root.rotation_euler.copy();root.location=(0,0,0);root.rotation_euler=(0,0,0)
 for o in children:o.hide_render=False
 bpy.context.view_layer.update();pp=[o.matrix_world@v.co for o in children if o.type=='MESH' for v in o.data.vertices];frame_camera(pp,(560,480),52,-18,1.2);sc.render.filepath=str(P/('kit-'+name+'.png'));bpy.ops.render.render(write_still=True)
 for o in children:o.hide_render=True
 root.location=oldloc;root.rotation_euler=oldrot
 render_records.append({'file':'kit-'+name+'.png','resolution':[560,480],'pitch_deg':52,'yaw_deg':-18});print('STAGE1 KIT RENDER',name,flush=True)
(O/'render-manifest.json').write_text(json.dumps(render_records,indent=2));print('STAGE1 RENDERS COMPLETE',flush=True)

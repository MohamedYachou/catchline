"""Review toggle contract in actual lit room, per-outfit full V4 views and diagnostic crops."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V4';P=O/'outfits2-renders';P.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(V/'RoomLook3-Check.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
# Keep the lit source room and kitchen/bar props. Remove proof guests, dining seats and preview cloth for a clear uniform stage.
names={r['name'] for r in json.loads((V/'build-metrics.json').read_text())['production_meshes']}
for o in list(sc.objects):
 if o.type in ['MESH','ARMATURE','EMPTY'] and (o.name not in names or o.name.startswith(('DiningTwo','DiningFour','TerraceTable','PlaceSetting_','Glass_','Candle_','V4_Plate_','V4_Glass_'))):bpy.data.objects.remove(o,do_unlink=True)
# Keep water from the source check if it was deleted above; room floor is the actual atlas source.
sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
outfits=['Outfit_HostFormal','Outfit_Host','Outfit_WaiterSuit','Outfit_WaiterSkirt','Outfit_CookWhites','Outfit_Barista','Outfit_Handyman','Outfit_HelperSuit','Outfit_Dishwasher'];cams=json.loads((V/'final-cameras.json').read_text());records=[]
def actor(name,pos):
 before=set(sc.objects);bpy.ops.import_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'));added=set(sc.objects)-before;rig=next(o for o in added if o.type=='ARMATURE');rig.animation_data_clear();keep=['Body',name]+(['Hat_HairUpClip'] if name=='Outfit_HostFormal' else ['Hat_Toque'] if name=='Outfit_CookWhites' else [])
 for ob in list(added):
  if ob.type=='MESH' and ob.name.split('.')[0] not in keep:bpy.data.objects.remove(ob,do_unlink=True)
 root=bpy.data.objects.new('REVIEW_ActorRoot',None);sc.collection.objects.link(root);root.location=pos;rig.parent=root;rig.data.pose_position='POSE';a=next(a for a in bpy.data.actions if a.name.split('|')[-1]=='Idle');rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
 sc.frame_set(13);return (set(sc.objects)-before)|{root}
def render(file,row):
 sc.camera.location=row['position_blender_m'];sc.camera.rotation_euler=row['rotation_blender_rad'];sc.camera.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.filepath=str(P/file);bpy.ops.render.render(write_still=True)
for n in outfits:
 if n in ['Outfit_HostFormal','Outfit_Host'] and all((P/(n+'-'+suffix+'.png')).exists() for suffix in ['1440','844','detail']):continue
 objs=actor(n,(1.8,-1.05,.045))
 for c in cams:render(n+'-'+str(c['resolution'][0])+'.png',c)
 # Diagnostic enlargement uses same lens/orientation translated closer; clearly labelled separate from game proof.
 cam=sc.camera;cam.location=Vector((1.8,-1.05,.54))+cam.rotation_euler.to_matrix()@Vector((0,0,2.5));cam.data.lens=58;sc.render.resolution_x=360;sc.render.resolution_y=460;sc.render.filepath=str(P/(n+'-detail.png'));bpy.ops.render.render(write_still=True)
 for ob in objs:
  if ob.name in bpy.data.objects:bpy.data.objects.remove(ob,do_unlink=True)
 print('OUTFIT ROOM RENDERED',n,flush=True)
# Nine uniforms across the game-managed dining footprint, kitchen side free.
for i,n in enumerate(outfits):actor(n,(.28+(i%3)*1.13,-1.45+(i//3)*1.26,.045))
for c in cams:render('lineup-'+str(c['resolution'][0])+'.png',c)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Outfits2-RoomCheck.blend'))
(O/'outfits2-cameras.json').write_text(json.dumps({'camera_source':str(V/'final-cameras.json'),'camera_rows':cams,'per_outfit':outfits,'actor_spot_blender_m':[1.8,-1.05,.045],'room':'RoomLook3-Check.blend, matching source room and practical lights; proof seats removed','detail_crops':'same orientation; camera translated close. Diagnostic only.','native_unverified':True},indent=2));print('OUTFITS2 ROOM REVIEW PASS')

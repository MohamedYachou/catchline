"""SERVICE-PROPS-3 night evidence. Actual Stage1V4 practicals; lower review fill/exposure prevents gold clipping. Camera/surfaces follow accepted room proof."""
from build_cooking import *

def scene_setup(ob,rec,key):
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.view_layers[0].cycles.use_denoising=True
 try:
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='CUDA';pref.get_devices()
  for dev in pref.devices:dev.use=dev.type=='CUDA'
  if any(d.type=='CUDA' for d in pref.devices):scene.cycles.device='GPU'
 except Exception:pass
 scene.world=bpy.data.worlds.new('Harbour blue dusk');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.16,.28,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.32
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-1.5
 scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 room=b.load_fbx(R/'Assets/Resources/Restaurant/Stage1V4.fbx');rm=room_material()
 for o in room:
  if o.type=='MESH':
   o.data.materials.clear();o.data.materials.append(rm)
   source=o.data.color_attributes.active_color
   if not o.data.color_attributes.get('Color'):
    vals=[tuple(c.color) for c in source.data] if source else [];col=o.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
    for i,c in enumerate(col.data):c.color=vals[i] if vals else (1,1,1,1)
 # Evidence-only station substitution in the existing prep slot, never written back to room.
 offset=Vector(rec['origin_offset_authored'])
 if key in COOK:
  station,top=COOK[key];at=Vector((-2.48,-.05,.04))
  for o in room:
   if o.name=='EXPORT_PrepCounter':o.hide_render=True
  station_obs=load_station(station)
  for o in station_obs:
   if not o.parent:o.location+=at
  delta=Vector((-.23,-.138,0)) if key=='Pan' else Vector((.16,-.03,0)) if key=='BreadBoard' else Vector((0,0,0))
  ob.location=at+Vector((offset.x,offset.y,top))+delta
  rec['station']=station;rec['station_top_y_m']=top;rec['station_local_unity_pivot_m']=[-offset.x-delta.x,top,-offset.y-delta.y]
  rec['review_station_world_blender_m']=list(at)
  service_target=at+Vector((0,0,.66));service_scale=3.0
 elif key.startswith('TipCoins'):
  top=.812;at=Vector((1.35,.28,0));ob.location=at+Vector((0,0,top))
  rec['station']='Stage1V4 EXPORT_DiningTwo_Cloth_Four upper cloth';rec['station_top_y_m']=top;rec['station_local_unity_pivot_m']=[-1.35,top,-.28];rec['placement_note']='Room-local Unity (-1.35,0.812,-0.28), identity rotation, scale1; ray-measured cloth surface.'
  service_target=Vector((1.35,.45,.48));service_scale=1.7
 elif key=='WarmingLamp':
  top=1.05;at=Vector((-2.48,-.05,.04))
  for o in room:
   if o.name=='EXPORT_PrepCounter':o.hide_render=True
  for o in load_station('PassCounter'):
   if not o.parent:o.location+=at
  ob.location=at+Vector((0,0,top));service_target=at+Vector((0,0,1.15));service_scale=2.5
  rec['station']='PassCounter';rec['station_top_y_m']=top;rec['station_local_unity_pivot_m']=[0,top,0]
 elif key=='ServiceBell':
  top=.78;at=Vector((-2.48,-.05,.04));delta=Vector((.15,-.10,0))
  for o in room:
   if o.name=='EXPORT_PrepCounter':o.hide_render=True
  for o in load_station('ReceptionDesk'):
   if not o.parent:o.location+=at
  ob.location=at+delta+Vector((0,0,top));service_target=at+Vector((.10,-.03,.64));service_scale=1.7
  rec['station']='ReceptionDesk main writing surface';rec['station_top_y_m']=top;rec['station_local_unity_pivot_m']=[-.15,top,.10]
 elif key=='Bunting':
  harbour_context(rm,scene);ob.location=Vector((-4.0,3.65,2.65))
  rec['station']='RestaurantPier quay festival overhead';rec['station_local_unity_pivot_m']=[4,2.65,-3.65]
  rec['placement_note']='Left attachment at local origin; string extends8m along Unity-X; right anchor(-8,0,0). Authored sag0.34m; lowest pennant~0.77m below attachment.'
  service_target=Vector((0,2.55,1.35));service_scale=11.6
 elif key=='PlateRack':
  import props3_captain
  anchor=Vector((0,0,.04));ob.location=anchor+Vector((0,-.28,.43))
  props3_captain.carry_review(anchor,ob,rec)
  rec['station']='Stage1V4 aisle; read-only current captain Mira carry-scale proof';rec['rack_local_unity_pivot_m']=[0,.43,.28]
  rec['grip_local_unity_m']=[0,.307,-.075];rec['carry_pose_note']='Evidence-only two-arm IK on untouched Mira import, normalized to CrewAnim.GameHeight1.14. Runtime currently carries props at root(0,.65,.27); attach rack by grip above with hand placement; no runtime/animation edits.'
  service_target=anchor+Vector((0,-.12,.58));service_scale=2.5
 elif key.startswith('Dish_'):
  top=.812;ob.location=(1.35,.28,top);service_target=Vector((1.35,.45,.58));service_scale=1.7
  rec['station']='Stage1V4 DiningFour upper cloth';rec['station_top_y_m']=top;rec['station_local_unity_pivot_m']=[-1.35,top,-.28]
 elif key=='Critic':
  ob.location=Vector((0,-.65,.04));service_target=ob.location+Vector((0,0,.5));service_scale=2.65
  rec['station']='Stage1V4 dining room';rec['station_top_y_m']=.04
 elif key=='CatchBoard':
  harbour_context(rm,scene);ob.location=Vector((-5.60,3.65,0))
  rec['station']='RestaurantPier Pier_S1 quay approach';rec['station_top_y_m']=0;rec['station_local_unity_pivot_m']=[5.60,0,-3.65]
  rec['blank_slate_panel_unity']={'centre_m':[0,.445,.205-(.170/.89)*.445+.004],'normal':[0,.170/.89,1],'width_m':.40,'height_m':.31,'up':[0,1,-.170/.89],'note':'Normal/up vectors normalise before use; fish patch lies below fixed chalk heading. Front faces local Unity +Z.'}
  service_target=Vector((-5.05,3.35,.45));service_scale=3.7
 elif key=='Ferry':
  harbour_context(rm,scene);ob.location=Vector((10.5,2.65,-.57))
  rec['station']='RestaurantPier quay / AddSea';rec['station_top_y_m']=-.57;rec['station_local_unity_pivot_m']=[-10.5,-.57,-2.65];rec['waterline_local_unity_y_m']=0;rec['draught_m']=.62;rec['heading_unity']=[-1,0,0];rec['placement_note']='Room/pier-local Unity (-10.5,-0.57,-2.65), identity rotation, scale1; local forward -X, waterlineY0, actual AddSea surfaceY-0.57.'
  rec['window_emission']='Existing yellow atlas cell(3,2), Surface.B=1, canonical shader emission factor2.8; no new material/texture.'
  service_target=Vector((5.25,1.6,.55));service_scale=23
  d=bpy.data.lights.new('REVIEW_FerryWarmQuayBounce','AREA');d.energy=650;d.color=(1,.77,.5);d.size=7;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(10.5,2,6)
 else:raise ValueError(key)
 lights=json.loads((R/'Assets/Resources/Restaurant/Stage1V4-lighting.json').read_text())['lights']
 for r in lights:
  if r['type']!='POINT':continue
  d=bpy.data.lights.new('REVIEW_'+r['name'],'POINT');d.energy=r['blender_power'];d.color=r['linear_rgb'];d.shadow_soft_size=max(.12,r.get('radius_m',.2));o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=r['position_blender_m']
 for name,loc,energy,color,size in [('RoomBounce',(0,-.5,6),300,(1,.77,.5),8),('Worklight',(-3,-2,3.8),110,(1,.79,.52),2)]:
  d=bpy.data.lights.new('REVIEW_'+name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-2.48,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.clip_end=120;scene.camera=cam
 b.place_camera(cam,service_target,service_scale,38)
 if key in ['CatchBoard','Ferry','Bunting']:cam.location=service_target+(cam.location-service_target).normalized()*25
 if rec.get('rig'):return scene,cam,room
 if not rec.get('close_only'):
  scene.render.filepath=str(O/'renders'/(rec['name']+'-service.png'));bpy.ops.render.render(write_still=True)
 target=ob.location+Vector((0 if key.startswith('Dish_') or key in ['WarmingLamp','ServiceBell','PlateRack'] else -offset.x,0 if key.startswith('Dish_') or key in ['WarmingLamp','ServiceBell','PlateRack'] else -offset.y,rec['size_xyz_unity_m'][1]*(.5 if key=='WarmingLamp' else .4)))
 scale=max(rec['size_xyz_unity_m'][0]*1.55,rec['size_xyz_unity_m'][2]*2,rec['size_xyz_unity_m'][1]*1.7,.25 if key.startswith('TipCoins') else .55)
 if key=='PlateRack':target=ob.location+Vector((0,0,.17));scale=.80
 if key=='Bunting':target=ob.location+Vector((4,0,-.40));scale=2.7
 if key=='WarmingLamp':scale=max(scale,rec['size_xyz_unity_m'][1]*2.2)
 close_pitch=30 if key=='WarmingLamp' else 55
 b.place_camera(cam,target,scale,close_pitch)
 if key in ['Ferry','Bunting']:cam.location=target+(cam.location-target).normalized()*25
 scene.render.filepath=str(O/'renders'/(rec['name']+'-close.png'));bpy.ops.render.render(write_still=True)
 rec['renders']=[str((O/'renders'/(rec['name']+'-'+s+'.png')).relative_to(R)) for s in ['service','close']]
 rec['service_camera_pitch_deg']=38;rec['close_camera_pitch_deg']=close_pitch

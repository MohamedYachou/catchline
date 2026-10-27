"""V3 room: linked V2 kit, additive dressing, exact reproducible night/camera proof."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];V=O.parent/'Stage1V2';P=O/'renders';P.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=24
meta=json.loads((V/'build-metrics.json').read_text());rows={r['root']:r for r in meta['roots']}
with bpy.data.libraries.load(str(V/'Stage1V2.blend'),link=True) as (src,dst):dst.objects=[r['mesh'] for r in rows.values()]
meshes={r['root']:bpy.data.objects.get(r['mesh']).data for r in rows.values()};placements=[];production=[]
def kit(src,name,loc,yaw=0):
 ob=bpy.data.objects.new(name,meshes[src]);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler.z=math.radians(yaw);production.append(ob)
 placements.append({'name':name,'source_root':src,'source_blend':'../Stage1V2/Stage1V2.blend','position_m':list(loc),'yaw_deg':yaw,'footprint_tiles':rows[src]['footprint_tiles'],'triangles':rows[src]['triangles']});return ob
kit('RoomShell','RoomShell',(0,0,0))
for n,(loc,yaw) in meta['placements'].items():
 if n not in ['TableFor2','TableFor4','TableLantern','TableLantern_B','GrilledFishPlate','SoupBowl','Glass','PlateClean','Cloche']:
  kit(n,n,loc,yaw)
# Three freestanding tables; booth retained at rear. Each kit retains its complete section5 footprint.
tables=[('TableFor2','DiningTwo_A',(.65,-1.35,.04)),('TableFor2','DiningTwo_B',(2.25,-1.35,.04)),('TableFor4','DiningFour',(1.35,.48,.04))]
for src,n,loc in tables:kit(src,n,loc)
kit('TerraceTable','TerraceTable',(-2.85,-3.48,-.04));kit('Parasol','TerraceParasol',(-3.05,-3.22,-.04))
for i,(x,y,z) in enumerate([(.65,-1.35,.74),(2.25,-1.35,.74),(1.35,.48,.74),(2.15,1.74,.74),(-2.85,-3.48,.66)]):
 kit('TableLantern','Candle_'+str(i),(x,y,z));kit('PlateClean','PlaceSetting_'+str(i),(x-.14,y-.12,z-.02));kit('Glass','Glass_'+str(i),(x+.13,y-.08,z))
# Pass full plates and clean stack. Existing fixed wall shelves/hood/trophy remain in referenced RoomShell.
for i in range(3):kit('PlateClean','PassStack'+str(i),(-.62,-.67+i*.42,.79+i*.018))
kit('GrilledFishPlate','PassFish',(-.62,.47,.77));kit('Cloche','PassCloche',(-.62,.0,.77))
kit('SoupBowl','DinnerSoup',(1.12,.37,.74));kit('PlateClean','DinnerPlate',(1.62,.36,.74))
for i,loc in enumerate([(-3.75,-3.07,-.03),(-1.65,-3.10,-.03),(4.3,-1.4,-.03),(.05,1.72,.04)]):kit('PlantPot1','ExtraPlant'+str(i),loc)
kit('LampPost','JettyLamp',(1.35,-3.10,-.03));kit('Barrel','JettyBarrel',(1.05,-3.15,-.03));kit('Crate','JettyCrate',(.55,-3.18,-.03))
# Additive mesh helpers; warm broad colours and bevelled edges, no global outlines.
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def mat(n,h,rough=.65,emit=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');c=tuple(lin(int(h[i:i+2],16)/255) for i in (0,2,4));m.diffuse_color=(*c,1);b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=rough
 if emit:b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=emit
 return m
stone=mat('WarmLimestone','C9B99D');wood=mat('HoneyTimber','BB824B');navy=mat('DeepNavyEnamel','164867',.36);warm=mat('LanternEmission','FFB943',.32,5);brass=mat('OldBrass','C88B38',.32);ivory=mat('CrockeryIvory','F1E4C8',.3)
def box(n,loc,sz,m,bev=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=sz;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bev:mod=o.modifiers.new('SoftBevel','BEVEL');mod.width=bev;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 production.append(o);return o
def rod(n,a,b,r,m):
 delta=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=delta.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=n;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.data.materials.append(m);production.append(o);return o
# Full back wall elevation makes faces, lanterns and painted fittings read at the lower camera.
for row,z in enumerate([1.13,1.39,1.65]):
 for j in range(16):
  x=-3.81+j*.505+(row%2)*.12
  if x<3.96:box('RearMasonry_%d_%d'%(row,j),(x,2.57,z),(.49,.20,.24),stone,.028)
box('RearCoping',(0,2.57,1.82),(8.2,.29,.12),ivory)
# Back shelves above kitchen, no roof or upper wall blocking the service view.
box('HighKitchenShelf',(-2.06,2.28,1.48),(2.8,.34,.08),wood)
for i in range(8):kit('CoffeeCup','ShelfCup'+str(i),(-3.14+i*.23,2.22,1.53))
# Four warm wall lanterns with opaque emission and distinct metal cages.
practical=[]
for i,x in enumerate([-3.35,-.7,1.02,3.42]):
 box('WallBracket'+str(i),(x,2.34,1.59),(.12,.13,.25),navy,.015)
 box('WallGlow'+str(i),(x,2.19,1.47),(.12,.13,.20),warm,.035)
 box('LanternRoof'+str(i),(x,2.19,1.59),(.21,.22,.06),brass,.02)
 for dx in [-.078,.078]:rod('LanternRail',(x+dx,2.1,1.35),(x+dx,2.1,1.58),.012,navy)
 practical.append((x,1.99,1.49))
# Terrace paving extension: floor-contact-only, measured with the exported production meshes.
box('TerraceFoundation',(-2.85,-3.45,-.20),(2.7,1.65,.34),stone,.08)
for j in range(4):
 for i in range(7):box('TerracePaving',(-4.0+i*.38,-4.02+j*.38,-.005),(.36,.36,.06),stone,.025)
# Cool water is review scenery, explicitly excluded from room FBX and budget.
water=mat('REVIEW_Water','075674',.23)
box('REVIEW_WaterPlane',(0,0,-.59),(200,200,.04),water,0);production.remove(bpy.data.objects['REVIEW_WaterPlane'])
# Reproducible lighting. All practical points are in metres and recorded with sRGB conversion.
sc.render.engine='CYCLES';sc.cycles.samples=40;sc.cycles.use_denoising=True;sc.cycles.device='GPU'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.render.threads_mode='FIXED';sc.render.threads=6
sc.world=bpy.data.worlds.new('BlueHour');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.19,.38,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.12
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.4
lightrows=[]
def light(n,typ,pos,power,srgb,radius=.15,size=1):
 d=bpy.data.lights.new(n,typ);d.energy=power;d.color=tuple(lin(v) for v in srgb);o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=pos
 if typ=='POINT':d.shadow_soft_size=radius
 if typ=='AREA':d.shape='DISK';d.size=size
 if typ=='SUN':d.angle=math.radians(12);o.rotation_euler=(.4,-.3,-.3)
 lightrows.append({'name':n,'type':typ,'position_blender_m':list(pos),'position_unity_m':[pos[0],pos[2],-pos[1]],'blender_power':power,'srgb':list(srgb),'hex':'#'+''.join('%02X'%round(v*255) for v in srgb),'radius_m':radius,'area_size_m':size});return o
light('DuskDirectional','SUN',(-4,-6,9),.12,(.42,.57,1))
for i,loc in enumerate(practical):light('WallLantern'+str(i),'POINT',loc,65,(1,.64,.25),.14)
for i,(x,y,z) in enumerate([(.65,-1.35,.98),(2.25,-1.35,.98),(1.35,.48,.98),(2.15,1.74,.98),(-2.85,-3.48,.9)]):light('TableCandle'+str(i),'POINT',(x,y,z),7,(1,.68,.32),.10)
for i,(x,y,z) in enumerate(meta['architectural_lantern_positions_m']):light('OriginalLantern'+str(i),'POINT',(x,y,z+.12),28,(1,.64,.25),.14)
for i,x in enumerate([-2.65,-.6,1.45]):light('WindowWash'+str(i),'POINT',(x,-2.95,.60),28,(1,.65,.24),.3)
light('KitchenWarmBounce','AREA',(-2.4,.4,3.3),155,(1,.77,.50),size=3)
light('DiningWarmBounce','AREA',(1.4,.0,3.7),110,(1,.77,.53),size=3)
light('TerraceWarmBounce','AREA',(-2.9,-3.5,2.4),45,(1,.73,.40),size=2)
light('JettyLampPool','POINT',(1.35,-3.12,1.34),65,(1,.64,.25),.18)
# Blender 5 compositor supports bloom as fog glow, recorded independently of URP settings.
cg=bpy.data.node_groups.new('RestaurantNightBloom','CompositorNodeTree');sc.compositing_node_group=cg
cg.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=cg.nodes.new('CompositorNodeRLayers');gl=cg.nodes.new('CompositorNodeGlare');gl.inputs['Type'].default_value='Fog Glow';gl.inputs['Quality'].default_value='High';gl.inputs['Threshold'].default_value=1.8;gl.inputs['Strength'].default_value=.07;gl.inputs['Size'].default_value=.35
out=cg.nodes.new('NodeGroupOutput');cg.links.new(rl.outputs['Image'],gl.inputs['Image']);cg.links.new(gl.outputs['Image'],out.inputs['Image'])
# Exact camera candidates: lower view reveals fronts and faces; no fictitious claim of recovering generated 3D.
cam=bpy.data.objects.new('ServiceCamera',bpy.data.cameras.new('ServiceCamera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.clip_end=250;cam.data.sensor_width=36
camrows=[]
def camera(kind,res):
 sc.render.resolution_x,sc.render.resolution_y=res;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
 elev=38.;yaw=-2.;target=Vector((-.02,-.55,.43));dist=21.;az=math.radians(yaw);el=math.radians(elev)
 cam.location=target+Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))*dist;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=kind;cam.data.lens=58;cam.data.ortho_scale=12.4
 # Phone wider framing preserves the entire quay without clipping top/bottom.
 if res[0]/res[1]>2:cam.data.lens=53;cam.data.ortho_scale=13.3
 camrows.append({'projection':kind,'resolution':list(res),'elevation_deg':elev,'yaw_deg':yaw,'distance_m':dist,'target_blender_m':list(target),'position_blender_m':list(cam.location),'rotation_blender_rad':list(cam.rotation_euler),'position_unity_m':[cam.location.x,cam.location.z,-cam.location.y],'rotation_unity_euler_deg':[elev,180+yaw,0],'vertical_fov_deg':math.degrees(2*math.atan(36/(res[0]/res[1])/(2*cam.data.lens))),'horizontal_fov_deg':math.degrees(2*math.atan(36/(2*cam.data.lens))),'lens_mm':cam.data.lens,'ortho_horizontal_span_m':cam.data.ortho_scale,'unity_orthographic_size_m':cam.data.ortho_scale/(res[0]/res[1])/2})
# Production export excludes camera/water/lights/people.
# Additive masonry/metal has explicit independent lightmap charts; linked V2 UV0/UV1 preserved.
for ob in production:
 if ob.data.library:continue
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='UVMap')
 uv=ob.data.uv_layers.new(name='LightmapUV');ob.data.uv_layers.active_index=len(ob.data.uv_layers)-1
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.035);bpy.ops.object.mode_set(mode='OBJECT');ob.data.uv_layers.active_index=0

bpy.context.view_layer.update();tri=0;meshrows=[]
for o in production:
 o.data.calc_loop_triangles();t=len(o.data.loop_triangles);tri+=t;pts=[o.matrix_world@v.co for v in o.data.vertices];meshrows.append({'name':o.name,'triangles':t,'linked_V2':bool(o.data.library),'world_min_m':[min(v[k] for v in pts) for k in range(3)],'world_max_m':[max(v[k] for v in pts) for k in range(3)]})
assert tri<=180000,tri
bpy.ops.object.select_all(action='DESELECT')
export_copies=[]
for o in production:
 c=o.copy();c.data=o.data.copy();sc.collection.objects.link(c);c.name='EXPORT_'+o.name;c.select_set(True);export_copies.append(c)
bpy.ops.export_scene.fbx(filepath=str(O/'Stage1V3.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
for c in export_copies:bpy.data.objects.remove(c,do_unlink=True)
(O/'build-metrics.json').write_text(json.dumps({'room_triangles':tri,'budget':180000,'production_meshes':meshrows,'placements':placements,'V2_blend_sha256':hashlib.sha256((V/'Stage1V2.blend').read_bytes()).hexdigest(),'footprint_room':[8,5],'kitchen':[3,5],'linked_assets_unchanged':True},indent=2))
(O/'lighting.json').write_text(json.dumps({'lights':lightrows,'world_linear_rgb':[.09,.19,.38],'world_strength':.12,'view_transform':'AgX Medium High Contrast','exposure_ev':.4,'bloom':{'type':'FOG_GLOW','threshold':1.8,'size':.35,'strength':.07},'URP_units_not_equivalent_to_watts':True},indent=2))
camera('PERSP',(1440,900));bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage1V3.blend'),relative_remap=True)
# Camera A/B first, fully dressed room without people. Final people scene appended in review.py.
for kind in ['PERSP','ORTHO']:
 camera(kind,(1440,900));sc.render.filepath=str(P/('camera-'+kind.lower()+'.png'));bpy.ops.render.render(write_still=True)
(O/'camera-study.json').write_text(json.dumps(camrows,indent=2));print('V3 BUILD PASS',tri,len(production),flush=True)

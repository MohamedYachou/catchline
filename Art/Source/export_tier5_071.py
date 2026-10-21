"""Export Mo-approved BOAT069 as additive Tier5FisherV1; no review statues."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/Tier5Production071';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/Models/Tier5Blockout069/tier5-size-study.blend'))
col=bpy.data.collections['Tier 5 provisional 8.5 x 4.2']
for o in list(bpy.data.objects):
 if o.name not in col.objects or o.name=='Studio floor' or any(k in o.name for k in [' captain ',' fisher ','prep hand','sixth hired crew','engineer Body','engineer Outfit','engineer Hat']):bpy.data.objects.remove(o,do_unlink=True)
# Remove baked rods, exterior trap placeholders and decorative food. Runtime owns these.
for o in list(col.objects):
 if any(k in o.name for k in [' rod ','Rod holder','Fixed buoy','Buoy mooring','Buoy trap','Crab box','Chum pail','Fish on cutting board','Worker standing mat']):bpy.data.objects.remove(o,do_unlink=True)
for o in list(col.objects):
 if o.type!='MESH':continue
 world=o.matrix_world.copy();data=o.data.copy()
 for v in data.vertices:
  w=world@v.co;v.co=(w.x-3.9,w.y,w.z)
 o.data=data;o.matrix_world.identity()
 o.name=o.name.replace('T5 T4 ','').replace('T5 ','')
# Canonical named palette, independent of source-only review shaders.
colors={'032 Navy':'M_HullNavy','032 Ivory':'M_RailIvory','032 Wood':'M_DeckWood','032 Rubber':'M_Rubber','032 Teal':'M_SeaTeal','032 Steel':'M_Steel','032 Orange':'M_SafetyOrange','032 Fish':'M_FishSilver','032 Ice':'M_SeaTeal','069 navy':'M_HullNavy','069 teal':'M_SeaTeal','069 safety orange':'M_SafetyOrange','069 steel':'M_Steel','069 ivory':'M_RailIvory','069 wood':'M_DeckWood'}
for o in col.objects:
 if o.type=='MESH':
  for slot in o.material_slots:
   if slot.material:
    base=slot.material.name.split('.')[0];name=colors.get(base,base)
    slot.material.name=name

def empty(name,loc=(0,0,0)):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.location=loc;return o
prep=empty('PrepStation');raw=empty('RawBuckets');ice=empty('RawIceCoolers');hold=empty('PreparedHold');net2=empty('NetModule2')
for o in list(col.objects):
 if o.type!='MESH':continue
 centre=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 if o.name.startswith('Convertible second net'):
  o.name='Module2_'+o.name.split('net ')[-1].replace('T5 T4 ','');o.parent=net2
  for poly in o.data.polygons:poly.flip()
 elif o.name.startswith(('RAW ice cooler','Ice marker')) or o.name.startswith(('Insulated lid','Recessed lid handle','Storage front latch')) and centre.y<.7:o.parent=ice
 elif o.name.startswith(('PREPARED freezer','Insulated lid','Recessed lid handle','Storage front latch')):o.parent=hold
 elif o.name.startswith(('Prep ','Cutting board','Knife ')):o.parent=prep
# Plain raw bins use same physical envelope, preserving tier4 ice-upgrade ownership.
for o in list(ice.children):
 if o.name.startswith('Ice marker'):continue
 n=o.copy();n.data=o.data.copy();col.objects.link(n);n.name='Plain_'+o.name;n.parent=raw
# Group visibility is runtime-owned; FBX includes both variants.
for o in col.objects:o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
# Origins for real moving parts.
for o in col.objects:
 if o.type=='MESH' and ('NetDrum' in o.name or o.name in ('NetCrank','Propeller')):
  pivot=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices);o.data.transform(Matrix.Translation(-pivot));o.location+=pivot
anchors={'PrepWorker_1':(-.43,1.75,0),'PrepWorker_2':(.43,1.75,0),'PrepInput':(0,.175,.4),'PrepSurface':(0,.90,.70),'PreparedOutput':(0,2.55,.5),
 'RodSocket_1':(-1.9,-.35,.47),'RodSocket_2':(1.9,-.35,.47),'RodSocket_3':(1.9,1.1,.47),'RodSocket_4':(1.9,2.55,.47),
 'BuoyAccess_1':(-1.35,-2.05,0),'BuoyAccess_2':(.95,-2.05,0),'BuoyAnchor_1':(-2.8,-2.05,-.3),'BuoyAnchor_2':(2.8,-2.05,-.3),
 'ServiceAccess_1':(.65,-1.05,0),'ServiceAccess_2':(-.85,-1.05,0),'NetWorker_1':(-1.0,2.90,0),'NetWorker_2':(1.0,2.90,0)}
for n,pos in anchors.items():empty(n,pos)
# Four separate holder fittings; first two are permanent, lasttwo runtimehide withNet2.
for i in range(4):
 pos=anchors['RodSocket_'+str(i+1)];bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.065,depth=.22,location=(pos[0],pos[1],.43));o=bpy.context.object;o.name='RodHolder_'+str(i+1)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(bpy.data.materials.get('M_Steel'))
# Geometry/export checks.
hull=bpy.data.objects['Hull'];bounds=[hull.matrix_world@v.co for v in hull.data.vertices];size=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)]
assert abs(size[0]-4.2)<.01 and abs(size[1]-8.5)<.01,size
assert not any(o.name.endswith('Body') for o in col.objects)
assert len(net2.children)>=4
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
path=ROOT/'Assets/Art/Models/Boats/Tier5FisherV1.fbx'
bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Tier5FisherV1.blend'))
# Source FBX roundtrip bounds and groups must survive actual reimport.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path))
h=bpy.data.objects.get('Hull');assert h is not None
points=[h.matrix_world@v.co for v in h.data.vertices];dims=sorted(max(v[i] for v in points)-min(v[i] for v in points) for i in range(3))
assert abs(dims[-1]-8.5)<.01 and abs(dims[-2]-4.2)<.01,dims
for n in ['NetModule2','RawBuckets','RawIceCoolers','PreparedHold']+list(anchors):assert bpy.data.objects.get(n) is not None,n
report={'hull_source_m':size,'roundtrip_dimensions_m':dims,'anchors_source':anchors,'six_hired_plus_captain':True,'crew_exported':False,'groups':['NetModule2','RawBuckets','RawIceCoolers','PreparedHold'],'triangles':sum(len(o.data.loop_triangles) for o in bpy.data.objects if o.type=='MESH')}
(OUT/'export.json').write_text(json.dumps(report,indent=2));print('TIER071 EXPORT ROUNDTRIP VERIFIED',json.dumps(report))

# Matching portrait of the existing authored crab; transparent pixels, no invented image.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/Art/Models/Props/Crab.fbx'))
meshes=[o for o in bpy.data.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)));center=(lo+hi)/2
bpy.ops.object.camera_add(location=center+Vector((.35,-.45,.50)));cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(hi-lo)*1.50
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.film_transparent=True
scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.world=bpy.data.worlds.new("Crab portrait world");scene.world.color=(.6,.6,.6)
bpy.ops.object.light_add(type='AREA',location=center+Vector((.2,-.3,.7)));lamp=bpy.context.object;lamp.data.energy=35;lamp.data.size=.6;lamp.rotation_euler=(center-lamp.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'Assets/Art/UI/fish-crab.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'crab-portrait.blend'));bpy.ops.render.render(write_still=True)
print('TIER071 CRAB PORTRAIT COMPLETE')

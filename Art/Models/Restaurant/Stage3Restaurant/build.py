"""Additive stage-two kit derived from accepted V4. Never writes upstream."""
import bpy,bmesh,json,math,hashlib,shutil,sys,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V4';R=O.parents[3];sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('geom',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
bpy.ops.wm.open_mainfile(filepath=str(O.parent/'Stage2Bistro/Stage2Bistro.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
T=O/'textures';T.mkdir(exist_ok=True)
for n in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:shutil.copyfile(V/'textures'/n,T/n)
cells={c['name']:c for c in json.loads((T/'atlas.json').read_text())['cells']}
sourcehash=hashlib.sha256((V/'Stage1V4.blend').read_bytes()).hexdigest()
bistrohash=hashlib.sha256((O.parent/'Stage2Bistro/Stage2Bistro.blend').read_bytes()).hexdigest()
mat=bpy.data.materials.new('Restaurant_Atlas_Restaurant3');mat.use_nodes=True;ns=mat.node_tree.nodes;lk=mat.node_tree.links;bs=ns.get('Principled BSDF');im=ns.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(T/'Restaurant_BaseColor.png'));im.image.pack();lk.new(im.outputs['Color'],bs.inputs['Base Color']);sf=ns.new('ShaderNodeTexImage');sf.image=bpy.data.images.load(str(T/'Restaurant_Surface.png'));sf.image.colorspace_settings.name='Non-Color';sf.image.pack();sep=ns.new('ShaderNodeSeparateColor');lk.new(sf.outputs['Color'],sep.inputs[0]);lk.new(sep.outputs['Red'],bs.inputs['Roughness']);lk.new(sep.outputs['Green'],bs.inputs['Metallic']);lk.new(im.outputs['Color'],bs.inputs['Emission Color']);mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=2.5;lk.new(sep.outputs['Blue'],mul.inputs[0]);lk.new(mul.outputs[0],bs.inputs['Emission Strength'])
new=[]
def obj(name,g,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(g.vertices,[],g.faces);me.update();ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);me.materials.append(mat);uv=me.uv_layers.new(name='UV0')
 for p,col in zip(me.polygons,g.colours):
  cell=cells[col];x,y,w,h=cell['pixel_cell'];axis=max(range(3),key=lambda k:abs(p.normal[k]));ax=[k for k in range(3) if k!=axis];points=[me.vertices[me.loops[i].vertex_index].co for i in p.loop_indices];lo=[min(v[k] for v in points) for k in ax];hi=[max(v[k] for v in points) for k in ax]
  for i,v in zip(p.loop_indices,points):
   a=[(v[k]-l)/max(r-l,1e-8) for k,l,r in zip(ax,lo,hi)];uv.data[i].uv=((x+24+a[0]*(w-48))/2048,1-(y+24+a[1]*(h-48))/2048)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 if bevel:
  mod=ob.modifiers.new('SoftEdges','BEVEL');mod.width=bevel;mod.segments=1;bpy.ops.object.modifier_apply(modifier=mod.name)
  # Remap any bevel bridges to an inset point in their nearest source cell.
  uv=me.uv_layers[0]
  for p in me.polygons:
   ids={int(uv.data[i].uv.x*8)+8*int(uv.data[i].uv.y*4) for i in p.loop_indices}
   if len(ids)>1:
    av=sum((uv.data[i].uv for i in p.loop_indices),Vector((0,0)))/len(p.loop_indices);cx=min(7,int(av.x*8));cy=min(3,int(av.y*4))
    for i in p.loop_indices:uv.data[i].uv=((cx+.5)/8,(cy+.5)/4)
 me.uv_layers.new(name='LightmapUV');me.uv_layers.active_index=1;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');me.uv_layers.active_index=0
 ao=me.color_attributes.new(name='LocalAO',type='BYTE_COLOR',domain='CORNER')
 for d in ao.data:d.color=(.9,.9,.9,1)
 new.append(ob);return ob

def box(g,c,d,col):g.box(c,d,col)
def tube(g,a,b,r,col,n=8):g.tube([a,b],[r,r],n,col)
# Stage 3 shell expands to 12x6 tiles. Transform structure in world space, retain the kitchen silhouettes.
def sx(x):return x if x<=-1 else -1+(x+1)*9/7
def sy(y):return y*1.4 if y>0 else (-2.5+(y+2.5)*1.5 if y< -2.5 else y)
remove_prefix=('Dining','Candle_','PlaceSetting_','Glass_','V4_Plate_','V4_Glass_','BistroTerraceTable_')
remove_names={'Booth','DinnerSoup','DinnerPlate','BistroBlueAwning','BistroAwningFacade'}
for o in list(sc.objects):
 if o.type=='MESH' and (o.name.startswith(remove_prefix) or o.name in remove_names):bpy.data.objects.remove(o,do_unlink=True)
for o in sc.objects:
 if o.type=='MESH' and not o.name.startswith('REVIEW_'):
  o.data=o.data.copy()
  if o.name=='RoomShell' or o.name.startswith(('RearMasonry','RearCoping','V4_RearMortar','BistroTerraceDeck','BistroTerraceRail','BistroEntryJetty','BistroStringLights')):
   mw=o.matrix_world.copy();mi=mw.inverted()
   for v in o.data.vertices:
    p=mw@v.co;p.x=sx(p.x);p.y=sy(p.y);v.co=mi@p
  else:o.location.x=sx(o.location.x);o.location.y=sy(o.location.y)
 elif o.type=='LIGHT':o.location.x=sx(o.location.x);o.location.y=sy(o.location.y)
# A proper dining room: ivory upper plaster, navy lower panelling, shallow pilasters and brass trim.
g=H.Geometry();box(g,(3.48,3.72,2.11),(9.12,.22,1.38),'ivory');box(g,(3.48,3.69,.91),(9.12,.20,.66),'navy');box(g,(3.48,3.55,1.26),(9.10,.055,.055),'brass');box(g,(3.48,3.72,2.81),(9.24,.28,.10),'navy')
for x in [-.95,1.25,3.45,5.65,7.85]:
 box(g,(x,3.52,1.43),(.11,.12,2.68),'ivory');box(g,(x,3.49,.18),(.18,.15,.19),'navy');box(g,(x,3.49,2.70),(.20,.17,.14),'brass')
obj('RestaurantDiningWall',g,.008)
# Tall recessed arched windows with deep blue opaque panes, broad ivory mullions and brass sill.
g=H.Geometry()
for cx in [.15,2.35,4.55,6.75]:
 profile=[(-.58,1.46),(.58,1.46),(.58,2.12)]+[(.58*math.cos(a*math.pi/12),2.12+.48*math.sin(a*math.pi/12)) for a in range(1,13)]
 g.add([(cx+x,3.575,z) for x,z in profile],[tuple(range(len(profile)))],'blue')
 path=[(cx+x,3.54,z) for x,z in profile]+[(cx+profile[0][0],3.54,profile[0][1])];g.tube(path,[.04]*len(path),8,'navy')
 tube(g,(cx,3.50,1.46),(cx,3.50,2.56),.019,'ivory');tube(g,(cx-.55,3.50,1.98),(cx+.55,3.50,1.98),.018,'ivory');box(g,(cx,3.49,1.44),(1.27,.18,.06),'brass')
obj('RestaurantArchedWindows',g)
# Shallow wall panelling on the dining side; no roof masks the stations.
g=H.Geometry()
for x in [-.55+i*.48 for i in range(18)]:box(g,(x,3.53,.88),(.37,.035,.44),'blue')
obj('RestaurantWallPanels',g,.007)
# Reuse finished linen/brass furniture without stretching it; all moveable table nodes distinct.
with bpy.data.libraries.load(str(O.parent/'Upgrades/RestaurantUpgrades.blend'),link=False) as (a,b):b.objects=['Dining4_Tier3','Dining2_Tier3']
loaded={o.name:o for o in b.objects if o}
tables=[]
def linen(name,loc,seats):
 src=loaded['Dining4_Tier3' if seats==4 else 'Dining2_Tier3'];o=src.copy();o.data=src.data.copy();o.name=name;sc.collection.objects.link(o);o.location=loc;tables.append({'name':name,'seats':seats,'position_blender_m':list(loc),'tabletop_z_m':loc[2]+.736,'includes_chairs':True,'tier':3});return o
for i,(x,y,seats) in enumerate([(1.0,-1.30,2),(3.55,-1.30,4),(1.0,.7,2),(3.55,.7,4),(1.0,2.45,2),(3.55,2.45,4)]):linen('RestaurantDiningTable_'+str(i+1),(x,y,.04),seats)
for i,x in enumerate([-2.75,-.45,1.85,4.15,6.45]):linen('RestaurantTerraceTable_'+str(i+1),(x,-4.35,-.03),4)
# A long bar counter with slab top, navy panels, brass footrail, three upholstered stools.
g=H.Geometry();box(g,(6.90,.55,.43),(.65,2.65,.78),'navy');box(g,(6.90,.55,.87),(.78,2.78,.10),'woodlight')
for y in [-.30,.55,1.40]:box(g,(6.56,y,.43),(.035,.68,.54),'blue')
tube(g,(6.43,-.65,.19),(6.43,1.75,.19),.022,'brass')
for y in [-.55,1.65]:tube(g,(6.56,y,.19),(6.43,y,.19),.022,'brass')
obj('RestaurantBarCounter',g,.012)
g=H.Geometry()
for y in [-.32,.55,1.42]:
 g.tube([(5.98,y,0.04),(5.98,y,.58)],[.105,.035],12,'navy');g.tube([(5.98,y,.58),(5.98,y,.65)],[.14,.14],16,'teal');g.tube([(5.98+.10*math.cos(i*math.tau/16),y+.10*math.sin(i*math.tau/16),.26) for i in range(17)],[.012]*17,6,'brass')
obj('RestaurantBarStools',g)
# Back bar shelf and bottles, with free prep space on the working counter.
g=H.Geometry();box(g,(7.17,3.36,1.54),(1.18,.28,.07),'woodlight');box(g,(7.17,3.56,1.88),(1.18,.045,.62),'navy')
for i,x in enumerate([6.74,6.94,7.14,7.34,7.54]):
 g.tube([(x,3.32,1.58),(x,3.32,1.83)],[.046,.046],10,'leaf' if i%2 else 'orange');g.tube([(x,3.32,1.83),(x,3.32,1.92)],[.022,.022],8,'brass');box(g,(x,3.265,1.70),(.06,.012,.08),'ivory')
obj('RestaurantBackBar',g)
# Coffee station moves behind bar; reception remains near entry with a clear main aisle.
bpy.data.objects['CoffeeBar'].location=(7.30,2.35,.04)
if 'CoffeeCup' in bpy.data.objects:bpy.data.objects['CoffeeCup'].location=(7.15,2.23,.80)
bpy.data.objects['ReceptionDesk'].location=(7.18,-1.65,.04)
# Decorative wall lamps are small, opaque emissive atlas meshes; actual illumination follows recipe.
recipe=json.loads((O.parent/'Stage2Bistro/lighting.json').read_text())
for r in recipe['lights']:
 p=r['position_blender_m'];p[0]=sx(p[0]);p[1]=sy(p[1]);r['position_unity_m']=[p[0],p[2],-p[1]]
# Replace old table candle positions with the actual new linen-table lights.
old=[r['name'] for r in recipe['lights'] if r['name'].startswith(('TableCandle','BistroTableCandle'))]
for n in old:
 if n in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
recipe['lights']=[r for r in recipe['lights'] if r['name'] not in old]
def point(name,loc,power,rad=.12):
 d=bpy.data.lights.new(name,'POINT');d.energy=power;d.color=(1,.603827,.204902);d.shadow_soft_size=rad;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;recipe['lights'].append({'name':name,'type':'POINT','position_blender_m':list(loc),'position_unity_m':[loc[0],loc[2],-loc[1]],'blender_power':power,'linear_rgb':list(d.color),'range_recipe_m':2.5,'radius_m':rad})
for i,row in enumerate(tables):x,y,z=row['position_blender_m'];point('RestaurantTableLamp'+str(i),(x,y,z+.91),7)
g=H.Geometry()
for i,x in enumerate([1.25,3.45,5.65]):
 box(g,(x,3.36,1.86),(.10,.12,.32),'brass');g.ellipsoid((x,3.27,1.91),(.07,.07,.14),12,5,'glow');point('RestaurantSconce'+str(i),(x,3.10,1.91),12)
obj('RestaurantBrassSconces',g)
# Terrace entry remains the accepted right-side jetty, now following the larger deck.
# Add a second restrained string on the outer edge: festoon visible against open water.
g=H.Geometry();path=[(-4.30+i*12.6/40,-5.85,1.93-.26*math.sin(math.pi*i/40)) for i in range(41)];g.tube(path,[.012]*len(path),6,'dark')
for i in range(25):
 x=-4.3+(i+.5)*12.6/25;z=1.93-.26*math.sin(math.pi*(i+.5)/25);tube(g,(x,-5.85,z),(x,-5.85,z-.06),.010,'brass');g.ellipsoid((x,-5.85,z-.10),(.035,.035,.05),10,4,'glow')
for x in [-4.3,8.3]:tube(g,(x,-5.85,-.03),(x,-5.85,1.98),.030,'navy')
obj('RestaurantOuterFestoon',g)
for i,x in enumerate([-3,-.5,2,4.5,7]):point('RestaurantTerraceString'+str(i),(x,-5.75,1.6),10,.18)
recipe['source_recipe']='Stage2Bistro/lighting.json';recipe['stage3_additions']='11linen-tablelamps,3brasswallsconces,5outerfestoon practicals';(O/'lighting.json').write_text(json.dumps(recipe,indent=2))
# Record table seat positions for placement integration, same local table/chair geometry as Upgrades.
for row in tables:
 fp=json.loads((O.parent/'Upgrades'/('Dining4_Tier3.footprint.json' if row['seats']==4 else 'Dining2_Tier3.footprint.json')).read_text());row['seat_sockets']=fp['seat_sockets']
# Clear inherited plant clusters from the new rear table and coffee footprint.
for name in ['PlantPot1','ExtraPlant3','V4_WallPlant_2','V4_WallPlant_3']:
 if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bpy.data.objects['PlantPot2'].location.x-=.95
# Pack all new imagery; source-only presentation objects never export.
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.filepath=bpy.path.abspath(im.filepath);im.pack()
  except Exception:pass
prod=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')]
for o in prod:
 if len(o.data.uv_layers)<2 or o.name.startswith('Restaurant'):
  while len(o.data.uv_layers)>1:o.data.uv_layers.remove(o.data.uv_layers[-1])
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();me=o.data;uv=me.uv_layers.new(name='LightmapUV');grid=math.ceil(math.sqrt(len(me.polygons)));pad=.12
  for j,p in enumerate(me.polygons):
   x=j%grid;y=j//grid
   for li,(u,v) in zip(p.loop_indices,[(pad,pad),(1-pad,pad),(pad,1-pad)]):uv.data[li].uv=((x+u)/grid,(y+v)/grid)
  me.uv_layers.active_index=0
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;bpy.context.view_layer.update();rows=[]
for o in prod:
 o.data.calc_loop_triangles();p=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'triangles':len(o.data.loop_triangles),'world_min_m':[min(v[k] for v in p) for k in range(3)],'world_max_m':[max(v[k] for v in p) for k in range(3)],'linked_V2':o.get('kit_source',''),'export_name':'EXPORT_'+o.name})
metrics={'source_V4_sha256':sourcehash,'source_Bistro_sha256':bistrohash,'room_triangles':sum(r['triangles'] for r in rows),'production_meshes':rows,'unit_scale_m':1,'layout_tile_m':1,'camera_note':'V4 orientation/lenses retained; wider framing for expanded room'};(O/'build-metrics.json').write_text(json.dumps(metrics,indent=2))
(O/'layout.json').write_text(json.dumps({'stage':3,'name':'Restaurant','room_tiles':[12,6],'tile_m':1,'room_bounds_blender_m':[[-4,-2.5,0],[8,3.5,0]],'kitchen_tiles':[3,6],'floor_surface_z_m':.04,'terrace_surface_z_m':-.03,'terrace_bounds_blender_m':[[-4.43,-6.325,-.03],[8.56,-2.49,-.03]],'waterline_z_m':-.55,'origin':'V4 retained; expanded positiveX/north and terrace forward','convert_blender_to_unity':'[x,z,-y]','runtime_layout_convention':'EXPORT_<component>; hide original layout component when replacing it','dining_tables':[r for r in tables if 'Dining' in r['name']],'terrace_tables':[r for r in tables if 'Terrace' in r['name']],'bar_counter':{'name':'RestaurantBarCounter','position_blender_m':[6.9,.55,.04],'stool_centres_blender_m':[[5.98,y,.04] for y in [-.32,.55,1.42]]},'entry_centre_blender_m':[sx(5.16),sy(-5.7),-.03]},indent=2))
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in prod:
 q=o.copy();q.data=o.data.copy();q.name='EXPORT_'+o.name;sc.collection.objects.link(q);q.select_set(True);copies.append(q)
bpy.context.view_layer.objects.active=copies[0]
bpy.ops.export_scene.fbx(filepath=str(O/'Stage3Restaurant.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,global_scale=1,axis_forward='-Z',axis_up='Y',use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
for q in copies:bpy.data.objects.remove(q,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage3Restaurant.blend'));print('STAGE3 BUILD PASS',len(prod),metrics['room_triangles'],flush=True)

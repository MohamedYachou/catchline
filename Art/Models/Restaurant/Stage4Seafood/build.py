"""Additive stage-two kit derived from accepted V4. Never writes upstream."""
import bpy,bmesh,json,math,hashlib,shutil,sys,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V4';R=O.parents[3];sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('geom',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
bpy.ops.wm.open_mainfile(filepath=str(O.parent/'Stage3Restaurant/Stage3Restaurant.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
T=O/'textures';T.mkdir(exist_ok=True)
for n in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:shutil.copyfile(V/'textures'/n,T/n)
cells={c['name']:c for c in json.loads((T/'atlas.json').read_text())['cells']}
sourcehash=hashlib.sha256((V/'Stage1V4.blend').read_bytes()).hexdigest()
bistrohash=hashlib.sha256((O.parent/'Stage3Restaurant/Stage3Restaurant.blend').read_bytes()).hexdigest()
mat=bpy.data.materials.new('Restaurant_Atlas_Seafood4');mat.use_nodes=True;ns=mat.node_tree.nodes;lk=mat.node_tree.links;bs=ns.get('Principled BSDF');im=ns.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(T/'Restaurant_BaseColor.png'));im.image.pack();lk.new(im.outputs['Color'],bs.inputs['Base Color']);sf=ns.new('ShaderNodeTexImage');sf.image=bpy.data.images.load(str(T/'Restaurant_Surface.png'));sf.image.colorspace_settings.name='Non-Color';sf.image.pack();sep=ns.new('ShaderNodeSeparateColor');lk.new(sf.outputs['Color'],sep.inputs[0]);lk.new(sep.outputs['Red'],bs.inputs['Roughness']);lk.new(sep.outputs['Green'],bs.inputs['Metallic']);lk.new(im.outputs['Color'],bs.inputs['Emission Color']);mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=2.5;lk.new(sep.outputs['Blue'],mul.inputs[0]);lk.new(mul.outputs[0],bs.inputs['Emission Strength'])
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
# Explicit 14x5 floor. Retain accepted detailing as rigid objects; never stretch furniture.
def sx(x):return x if x< -1 else x+2
def sy(y):return y-1 if y>1 else y
remove={'RoomShell','RestaurantBarCounter','RestaurantBarStools','RestaurantOuterFestoon','BistroTerraceDeck','BistroTerraceRail','BistroEntryJetty','BistroStringLights','PassCounter','PassFish','PassCloche','TrashCan','PlantPot2','PlantPot3','ExtraPlant2','V4_WallPlant_4','V4_WallPlant_5','V4_WallPlant_6','RopeFencePost'}
for o in list(sc.objects):
 if o.type=='MESH' and (o.name in remove or o.name.startswith(('RestaurantDiningTable','PassStack','BistroTerracePlant','V4_PillarLantern'))):bpy.data.objects.remove(o,do_unlink=True)
for o in sc.objects:
 if o.type=='MESH' and not o.name.startswith('REVIEW_'):
  corners=[o.matrix_world@Vector(c) for c in o.bound_box]
  cx=(min(v.x for v in corners)+max(v.x for v in corners))/2
  cy=(min(v.y for v in corners)+max(v.y for v in corners))/2
  o.location.x+=sx(cx)-cx;o.location.y+=sy(cy)-cy
 elif o.type=='LIGHT':o.location.x=sx(o.location.x);o.location.y=sy(o.location.y)
# Kitchen boundary grows from X=-1 to X=1. Left utility line stays in place.
g=H.Geometry();box(g,(3,0,-.11),(14,5,.22),'wood')
for x in range(5):
 for y in range(5):box(g,(-3.5+x,-2+y,.015),(.985,.985,.05),'tile1' if (x+y)%3 else 'ivory')
for i in range(20):
 y=-2.375+i*.25
 for j in range(5):
  x=1.9+j*1.8+(.45 if i%2 else 0);lo=max(1,x-.893);hi=min(10,x+.893)
  if hi>lo:box(g,((lo+hi)/2,y,.02),(hi-lo,.243,.04),'woodlight' if (i+j)%5==0 else 'wood')
# Low side walls, open foreground for game visibility, doorway at right.
for x in [-4.13,10.13]:box(g,(x,0,.48),(.25,5.25,.96),'plaster');box(g,(x,0,.995),(.29,5.28,.075),'navy')
box(g,(1,-2.63,.31),(10,.24,.62),'plaster');box(g,(1,-2.63,.64),(10.05,.28,.07),'navy');box(g,(9.55,-2.63,.31),(1.15,.24,.62),'plaster')
box(g,(3,2.64,.48),(14.25,.26,.96),'plaster');box(g,(3,2.67,.985),(14.3,.28,.07),'navy')
obj('RoomShell',g,.008)
# Old kitchen shelf and lanterns y positions adjusted rigidly above. A second work line fills the wider kitchen.
with bpy.data.libraries.load(str(O.parent/'KitchenKit2/RestaurantKitchenKit2.blend'),link=False) as (a,b):b.objects=['Restaurant_Grill','Restaurant_Steamer','Restaurant_BigFridge']
for o,loc in zip(b.objects,[(-.48,2.02,.04),(-1.52,2.02,.04),(.40,-1.85,.04)]):
 if o:sc.collection.objects.link(o);o.location=loc;o.name='Seafood'+o.name.removeprefix('Restaurant_');new.append(o)
# Two accepted linen tables at front leave the rear booths and tank readable.
with bpy.data.libraries.load(str(O.parent/'Upgrades/RestaurantUpgrades.blend'),link=False) as (a,b):b.objects=['Dining4_Tier3','Dining2_Tier3','TableCandle']
loaded={o.name:o for o in b.objects if o};tables=[]
for i,(x,y) in enumerate([(2.5,-1.15),(5.05,-1.15)]):
 src=loaded['Dining4_Tier3'];o=src.copy();o.data=src.data.copy();sc.collection.objects.link(o);o.name='SeafoodDiningTable_'+str(i+1);o.location=(x,y,.04);tables.append({'name':o.name,'seats':4,'position_blender_m':list(o.location),'tabletop_z_m':.776,'includes_chairs':True,'seat_sockets':json.loads((O.parent/'Upgrades/Dining4_Tier3.footprint.json').read_text())['seat_sockets']})
# Booths: facing upholstered bench pairs, central linen table, six sockets each.
booths=[]
for i,cx in enumerate([2.6,5.1]):
 g=H.Geometry()
 for x in [cx-.85,cx+.85]:
  box(g,(x,1.47,.23),(.49,1.53,.36),'navy');box(g,(x,1.47,.46),(.51,1.52,.15),'teal');box(g,(x+(-.20 if x<cx else .20),1.47,.76),(.15,1.54,.66),'navy');box(g,(x+(-.12 if x<cx else .12),1.47,.79),(.08,1.39,.49),'teal')
 box(g,(cx,1.47,.70),(.99,1.54,.085),'woodlight');box(g,(cx,1.47,.754),(1.02,1.57,.025),'ivory');box(g,(cx,1.47,.36),(.16,.66,.64),'navy')
 # Brass table lamp plus simple plate settings.
 g.tube([(cx,1.47,.78),(cx,1.47,.95)],[.045,.018],10,'brass');g.ellipsoid((cx,1.47,.98),(.075,.075,.075),10,4,'glow')
 for xx in [cx-.27,cx+.27]:
  for yy in [.99,1.47,1.95]:g.tube([(xx,yy,.774),(xx,yy,.789)],[.12,.12],12,'ivory')
 name='SeafoodBooth_'+str(i+1);obj(name,g,.008);booths.append({'name':name,'seats':6,'position_blender_m':[cx,1.47,.04],'tabletop_z_m':.767,'includes_chairs':True,'seat_sockets':[{'position_blender_m':[xx,yy,.49],'facing_blender_xy':[1 if xx<cx else -1,0]} for xx in [cx-.75,cx+.75] for yy in [.99,1.47,1.95]],'seat_socket_space':'absolute Blender coordinates'})
# A larger working bar, brass rail, five separate upholstered stools.
g=H.Geometry();box(g,(8.95,.10,.44),(.72,3.55,.80),'navy');box(g,(8.95,.10,.90),(.88,3.70,.12),'woodlight')
for y in [-1.2,-.55,.1,.75,1.4]:box(g,(8.57,y,.44),(.04,.51,.56),'blue')
tube(g,(8.39,-1.53,.19),(8.39,1.72,.19),.025,'brass');obj('SeafoodBarCounter',g,.012)
g=H.Geometry()
for y in [-1.15,-.52,.11,.74,1.37]:
 g.tube([(7.99,y,.04),(7.99,y,.59)],[.10,.035],12,'navy');g.tube([(7.99,y,.59),(7.99,y,.66)],[.145,.145],16,'teal')
obj('SeafoodBarStools',g)
# Open ice counter in the new kitchen aisle. Opaque pale ice with readable whole fish, lemon.
g=H.Geometry();box(g,(-.22,.49,.43),(1.95,.79,.78),'navy');box(g,(-.22,.49,.85),(2.04,.87,.10),'steel');box(g,(-.22,.49,.916),(1.85,.70,.034),'ivory')
for x in [-1.18,.74]:box(g,(x,.49,.98),(.065,.87,.18),'steel')
for y in [.08,.90]:box(g,(-.22,y,.98),(1.96,.06,.18),'steel')
for i,x in enumerate([-.85,-.33,.19]):
 g.ellipsoid((x,.45,.984),(.23,.105,.06),12,5,'steel');g.ellipsoid((x,.45,1.011),(.20,.085,.034),12,4,'blue');g.add([(x+.16,.45,1.00),(x+.33,.32,1.0),(x+.31,.57,1.0)],[(0,1,2)],'steel');g.ellipsoid((x-.16,.375,1.01),(.017,.012,.017),8,3,'dark')
for x,y in [(.55,.30),(.49,.58),(-.65,.71)]:g.ellipsoid((x,y,.99),(.055,.05,.025),10,4,'food')
obj('SeafoodIceCounter',g,.008)
# Display tank is open topped: tinted opaque rear/sides only, no front pane masking fish.
g=H.Geometry();box(g,(6.92,1.89,.30),(1.45,.74,.52),'navy');box(g,(6.92,1.89,.59),(1.51,.80,.10),'brass');box(g,(6.92,2.22,.95),(1.44,.045,.62),'blue');box(g,(6.22,1.89,.95),(.045,.70,.62),'blue');box(g,(7.62,1.89,.95),(.045,.70,.62),'blue');box(g,(6.92,1.89,.66),(1.38,.67,.025),'teal')
for x in [6.20,7.64]:tube(g,(x,1.52,.64),(x,1.52,1.27),.023,'brass')
for y in [1.52,2.26]:tube(g,(6.2,y,1.27),(7.64,y,1.27),.023,'brass')
for i,x in enumerate([6.57,7.14]):
 g.ellipsoid((x,1.83,.94+i*.09),(.23,.085,.095),12,5,'steel');g.add([(x+.17,1.83,.94+i*.09),(x+.35,1.83,.82+i*.09),(x+.35,1.83,1.05+i*.09)],[(0,1,2)],'orange');g.ellipsoid((x-.17,1.75,.97+i*.09),(.015,.012,.015),8,3,'dark')
obj('SeafoodDisplayTank',g)
# Full frontage terrace remains over the water, 14m wide with six linen assemblies.
def deckx(x):return -4+(x+4)*14/12
for name in ['RestaurantTerraceTable_'+str(i) for i in range(1,6)]:
 if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
g=H.Geometry();box(g,(3,-4.40,-.16),(14.8,3.60,.25),'navy')
for i in range(14):box(g,(3,-6.08+i*.25,-.065),(14.72,.242,.07),'woodlight' if i%5==0 else 'wood')
for x in [-4.25,-.75,2.75,6.25,10.25]:
 for y in [-6.0,-2.82]:tube(g,(x,y,-1.05),(x,y,-.14),.10,'wood')
obj('SeafoodTerraceDeck',g,.008)
g=H.Geometry()
for x in [-4.25+i*1.45 for i in range(11)]:tube(g,(x,-6.1,-.03),(x,-6.1,.72),.035,'navy');g.ellipsoid((x,-6.1,.74),(.05,.05,.035),8,3,'brass')
path=[(-4.25+i*14.5/80,-6.1,.5-.07*abs(math.sin(math.pi*i/8))) for i in range(81)];g.tube(path,[.018]*len(path),6,'rope');obj('SeafoodTerraceRail',g)
for i,x in enumerate([-3,-.65,1.70,4.05,6.40,8.75]):
 src=loaded['Dining4_Tier3'];o=src.copy();o.data=src.data.copy();sc.collection.objects.link(o);o.name='SeafoodTerraceTable_'+str(i+1);o.location=(x,-4.31,-.03);tables.append({'name':o.name,'seats':4,'position_blender_m':list(o.location),'tabletop_z_m':.706,'includes_chairs':True,'seat_sockets':json.loads((O.parent/'Upgrades/Dining4_Tier3.footprint.json').read_text())['seat_sockets']})
g=H.Geometry();box(g,(9.10,-7.13,-.16),(2.0,2.0,.25),'navy')
for i in range(8):box(g,(9.10,-7.99+i*.25,-.065),(1.94,.242,.07),'wood')
obj('SeafoodEntryJetty',g,.008)
# Dual festoon strings, short poles, no roof over stations.
g=H.Geometry()
for y in [-2.94,-5.94]:
 path=[(-4.25+i*14.5/50,y,2.03-.28*math.sin(math.pi*i/50)) for i in range(51)];g.tube(path,[.012]*len(path),6,'dark')
 for x in [-4.25,10.25]:tube(g,(x,y,-.03),(x,y,2.06),.03,'navy')
 for i in range(28):
  x=-4.25+(i+.5)*14.5/28;z=2.03-.28*math.sin(math.pi*(i+.5)/28);tube(g,(x,y,z),(x,y,z-.065),.01,'brass');g.ellipsoid((x,y,z-.10),(.035,.035,.05),10,4,'glow')
obj('SeafoodStringLights',g)
# Keep kitchen compact and furniture clear of the low side walls.
bpy.data.objects['SinkDishRack'].location.y+=.20
bpy.data.objects['ReceptionDesk'].location=(9.34,-1.78,.04)
bpy.data.objects['CoffeeBar'].location=(9.30,1.86,.04)
bpy.data.objects['CoffeeCup'].location=(9.15,1.74,.80)
# Accepted source lights follow moved rear walls. Replace all table/terrace lights with measured positions.
recipe=json.loads((O.parent/'Stage3Restaurant/lighting.json').read_text());recipe['lights']=[r for r in recipe['lights'] if not r['name'].startswith(('RestaurantTable','RestaurantTerrace','Bistro','TableCandle'))]
keep={r['name'] for r in recipe['lights']}
for o in list(sc.objects):
 if o.type=='LIGHT' and o.name not in keep:bpy.data.objects.remove(o,do_unlink=True)
for r in recipe['lights']:
 o=bpy.data.objects.get(r['name'])
 if o:r['position_blender_m']=list(o.location);r['position_unity_m']=[o.location.x,o.location.z,-o.location.y]
def point(name,loc,power):
 d=bpy.data.lights.new(name,'POINT');d.energy=power;d.color=(1,.603827,.204902);d.shadow_soft_size=.14;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;recipe['lights'].append({'name':name,'type':'POINT','position_blender_m':list(loc),'position_unity_m':[loc[0],loc[2],-loc[1]],'blender_power':power,'linear_rgb':list(d.color),'range_recipe_m':2.5,'radius_m':.14})
for i,r in enumerate(tables):x,y,z=r['position_blender_m'];point('SeafoodTableLamp'+str(i),(x,y,z+.91),8)
for i,x in enumerate([2.6,5.1]):point('SeafoodBoothLamp'+str(i),(x,1.47,1.02),8)
for i,x in enumerate([-3,-.5,2,4.5,7,9.5]):point('SeafoodTerraceString'+str(i),(x,-5.65,1.6),10)
point('SeafoodIceLight',(-.22,.49,1.65),14)
recipe['source_recipe']='Stage3Restaurant/lighting.json';recipe['stage4_additions']='booth/tablelamps,seafoodicelight,terracestring';(O/'lighting.json').write_text(json.dumps(recipe,indent=2))
# Pack source and generate nondegenerate lightmap UVs for every new component.
prod=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')]
for o in prod:
 if o not in new and len(o.data.uv_layers)>=2:continue
 me=o.data
 while len(me.uv_layers)>1:me.uv_layers.remove(me.uv_layers[-1])
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='LightmapUV');grid=math.ceil(math.sqrt(len(me.polygons)))
 for j,p in enumerate(me.polygons):
  for li,(u,v) in zip(p.loop_indices,[(.12,.12),(.88,.12),(.12,.88)]):uv.data[li].uv=((j%grid+u)/grid,(j//grid+v)/grid)
 me.uv_layers.active_index=0
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.filepath=bpy.path.abspath(im.filepath);im.pack()
  except Exception:pass
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;bpy.context.view_layer.update();rows=[]
for o in prod:
 o.data.calc_loop_triangles();p=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'triangles':len(o.data.loop_triangles),'world_min_m':[min(v[k] for v in p) for k in range(3)],'world_max_m':[max(v[k] for v in p) for k in range(3)],'linked_V2':o.get('kit_source',''),'export_name':'EXPORT_'+o.name})
metrics={'source_V4_sha256':sourcehash,'source_Stage3_sha256':hashlib.sha256((O.parent/'Stage3Restaurant/Stage3Restaurant.blend').read_bytes()).hexdigest(),'room_triangles':sum(r['triangles'] for r in rows),'production_meshes':rows,'unit_scale_m':1,'layout_tile_m':1};(O/'build-metrics.json').write_text(json.dumps(metrics,indent=2))
(O/'layout.json').write_text(json.dumps({'stage':4,'name':'Seafood house','room_tiles':[14,5],'tile_m':1,'room_bounds_blender_m':[[-4,-2.5,0],[10,2.5,0]],'kitchen_tiles':[5,5],'kitchen_bounds_blender_m':[[-4,-2.5,0],[1,2.5,0]],'floor_surface_z_m':.04,'terrace_surface_z_m':-.03,'terrace_bounds_blender_m':[[-4.4,-6.2,-.03],[10.4,-2.6,-.03]],'waterline_z_m':-.55,'origin':'V4 retained; kitchenboundaryX1; roomextendsX10','convert_blender_to_unity':'[x,z,-y]','runtime_layout_convention':'EXPORT_<component>; hide whole combined furniture node before replacement','dining_tables':[r for r in tables if 'Dining' in r['name']],'booths':booths,'terrace_tables':[r for r in tables if 'Terrace' in r['name']],'bar_counter':{'name':'SeafoodBarCounter','stool_centres_blender_m':[[7.99,y,.04] for y in [-1.15,-.52,.11,.74,1.37]]},'seafood_display':['SeafoodIceCounter','SeafoodDisplayTank'],'entry_centre_blender_m':[9.1,-7.13,-.03]},indent=2))
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in prod:
 q=o.copy();q.data=o.data.copy();q.name='EXPORT_'+o.name;sc.collection.objects.link(q);q.select_set(True);copies.append(q)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.export_scene.fbx(filepath=str(O/'Stage4Seafood.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,global_scale=1,axis_forward='-Z',axis_up='Y',use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
for q in copies:bpy.data.objects.remove(q,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage4Seafood.blend'));print('STAGE4 BUILD PASS',len(prod),metrics['room_triangles'],flush=True)

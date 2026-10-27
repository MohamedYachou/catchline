"""Room-look3: unchanged atlas, richer local pigments, off-grid dressing and warm practical pools."""
import bpy,bmesh,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];bpy.ops.wm.open_mainfile(filepath=str(O/'Stage1V4.blend'));sc=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
spec=importlib.util.spec_from_file_location('geom',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
cells={c['name']:c for c in json.loads((O/'textures/atlas.json').read_text())['cells']};mat=bpy.data.materials['Restaurant_Atlas_URP_V4']
def obj(n,g):
 me=bpy.data.meshes.new(n);me.from_pydata(g.vertices,[],g.faces);me.update();ob=bpy.data.objects.new(n,me);sc.collection.objects.link(ob);me.materials.append(mat);uv=me.uv_layers.new(name='UV0')
 for p,col in zip(me.polygons,g.colours):
  x,y,w,h=cells[col]['pixel_cell'];ax=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(p.normal[k]))];pts=[me.vertices[me.loops[i].vertex_index].co for i in p.loop_indices];lo=[min(v[k] for v in pts) for k in ax];hi=[max(v[k] for v in pts) for k in ax]
  for i,v in zip(p.loop_indices,pts):
   a=[(v[k]-l)/max(r-l,1e-8) for k,l,r in zip(ax,lo,hi)];uv.data[i].uv=((x+24+a[0]*(w-48))/2048,1-(y+24+a[1]*(h-48))/2048)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='LightmapUV');grid=math.ceil(math.sqrt(len(me.polygons)))
 for j,p in enumerate(me.polygons):
  for i,(u,v) in zip(p.loop_indices,[(.12,.12),(.88,.12),(.12,.88)]):uv.data[i].uv=((j%grid+u)/grid,(j//grid+v)/grid)
 me.uv_layers.active_index=0;ao=me.color_attributes.new(name='LocalAO',type='BYTE_COLOR',domain='CORNER')
 for d in ao.data:d.color=(.85,.85,.85,1)
 return ob
if not sc.get('room_look3_v1'):
 # Existing floor geometry and palette retained; shift per-board LocalAO pigment to suppress uniform orange/white.
 changes=[]
 for ob in list(sc.objects):
  if ob.type!='MESH' or ob.name.startswith('REVIEW_'):continue
  ao=ob.data.color_attributes.get('LocalAO')
  if not ao:continue
  for p in ob.data.polygons:
   c=ob.matrix_world@p.center;factor=1
   if ob.name=='RoomShell' and p.normal.z>.65 and -.02<c.z<.10 and -4<c.x<4 and -2.55<c.y<2.55:
    # Kitchen cool ivory, dining warm chestnut; consistent shade per individual floorboard.
    v=(math.sin(math.floor(c.x*2)*17.3+math.floor(c.y*4)*31.7)+1)/2
    factor=(.66+.12*v) if c.x<-1 else (.70+.24*v)
   elif ob.name.startswith('RearMasonry_'):factor=.80+.15*((sum(map(ord,ob.name))%7)/6)
   if factor!=1:
    for i in p.loop_indices:
     d=ao.data[i];r,g,b,a=d.color;d.color=(r*factor,g*factor,b*factor,a)
    changes.append(ob.name)
 # Three cloth runners merge visually with the existing table proofs and share runtime-hide prefixes.
 for n,x,y,z,w,d in [('DiningTwo_Cloth_A',.65,-1.35,.806,.54,.42),('DiningTwo_Cloth_B',2.25,-1.35,.806,.54,.42),('DiningTwo_Cloth_Four',1.35,.48,.806,.70,.63)]:
  g=H.Geometry();g.box((x,y,z),(w,d,.012),'ivory');g.box((x-w/2+.025,y,z+.008),(.035,d,.005),'blue');g.box((x+w/2-.025,y,z+.008),(.035,d,.005),'blue');obj(n,g)
 # Chalk-menu geometry and frame mounted to the dining back wall, clear of the floor grid.
 g=H.Geometry();g.box((3.15,2.405,1.48),(.66,.09,.75),'wooddark');g.box((3.15,2.35,1.48),(.56,.025,.65),'dark')
 for i,width in enumerate([.32,.40,.35,.26]):
  z=1.70-i*.14;g.box((3.13,2.33,z),(width,.008,.018),'ivory')
  if i:g.box((3.35,2.327,z),(.045,.008,.015),'brass')
 obj('Look3_WallMenu',g)
 # Off-grid sill herbs and doorway flowers use established kit meshes.
 for n,loc,scale in [('Look3_SillHerbA',(-3.65,2.40,1.04),.40),('Look3_SillHerbB',(-2.95,2.40,1.04),.35),('Look3_DoorFlowers',(4.38,-1.75,.03),.72)]:
  src=bpy.data.objects.get('PlantPot1');q=src.copy();q.data=src.data.copy();q.name=n;sc.collection.objects.link(q);q.location=loc;q.scale=tuple(v*scale for v in src.scale)
 # Jetty-only festoon. Thin posts sit outside the room; all bulbs and cord below camera sight line to diners.
 g=H.Geometry();points=[(-4.45+8.9*i/40,-3.43,1.82-.24*math.sin(math.pi*i/40)) for i in range(41)];g.tube(points,[.014]*41,6,'dark')
 for x in [-4.45,4.45]:g.tube([(x,-3.43,-.04),(x,-3.43,1.88)],[.032,.032],8,'navy')
 for i in range(21):
  x=-4.25+8.5*i/20;z=1.82-.24*math.sin(math.pi*(x+4.45)/8.9);g.ellipsoid((x,-3.43,z-.045),(.035,.035,.05),8,3,'glow')
 obj('Look3_JettyFestoon',g)
 for ob in sc.objects:
  if ob.type!='LIGHT':continue
  if ob.data.type=='SUN':ob.data.energy=.14
  elif ob.data.type=='AREA':ob.data.energy*=.35;ob.data.color=(1,.73,.46)
  elif ob.name.startswith(('WallLantern','WindowWash')):ob.data.energy*=.72;ob.data.shadow_soft_size=.16
 for i,(x,y) in enumerate([(.65,-1.35),(2.25,-1.35),(1.35,.48),(2.15,1.78),(-2.85,-3.48)]):
  d=bpy.data.lights.new('Look3_TablePool'+str(i),'POINT');d.energy=25;d.color=(1,.56,.20);d.shadow_soft_size=.16;q=bpy.data.objects.new(d.name,d);sc.collection.objects.link(q);q.location=(x,y,1.45)
 sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.18;sc.view_settings.exposure=-.40;sc['room_look3_v1']=True
 (O/'room-look-changes.json').write_text(json.dumps({'pigment_nodes':sorted(set(changes)),'atlas_images_changed':False,'existing_geometry_and_names_preserved':True,'new_static_dressing':['Look3_WallMenu','Look3_SillHerbA','Look3_SillHerbB','Look3_DoorFlowers','Look3_JettyFestoon'],'preview_linen_nodes_hidden_by_game_prefix':'DiningTwo_Cloth_*','light_pools':5},indent=2))
prod=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')];bpy.context.view_layer.update();rows=[]
for ob in prod:
 ob.data.calc_loop_triangles();pts=[ob.matrix_world@v.co for v in ob.data.vertices];rows.append({'name':ob.name,'triangles':len(ob.data.loop_triangles),'linked_V2':True if not ob.name.startswith(('Look3_','DiningTwo_Cloth')) else False,'world_min_m':[min(p[k] for p in pts) for k in range(3)],'world_max_m':[max(p[k] for p in pts) for k in range(3)]})
M=json.loads((O/'build-metrics.json').read_text());M.update(room_triangles=sum(r['triangles'] for r in rows),production_meshes=rows,room_look3=True);(O/'build-metrics.json').write_text(json.dumps(M,indent=2))
bpy.ops.object.select_all(action='DESELECT');copies=[]
for ob in prod:q=ob.copy();q.data=ob.data.copy();q.name='EXPORT_'+ob.name;sc.collection.objects.link(q);q.select_set(True);copies.append(q)
bpy.ops.export_scene.fbx(filepath=str(O/'Stage1V4.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
for q in copies:bpy.data.objects.remove(q,do_unlink=True)
recipe=json.loads((O/'lighting.json').read_text());recipe.update(world_strength=.18,exposure_ev=-.40,room_look3='reduced broad cool fill, warm table-specific pools; point lights suggested range2.2m, non-equivalent Blender watts');recipe['lights']=[{'name':o.name,'type':o.data.type,'position_blender_m':list(o.location),'position_unity_m':[o.location.x,o.location.z,-o.location.y],'blender_power':o.data.energy,'linear_rgb':list(o.data.color),'range_recipe_m':2.2 if o.name.startswith('Look3_TablePool') else 4,'radius_m':o.data.shadow_soft_size} for o in sc.objects if o.type=='LIGHT'];(O/'lighting.json').write_text(json.dumps(recipe,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage1V4.blend'));print('ROOM LOOK3 BUILD PASS',M['room_triangles'])

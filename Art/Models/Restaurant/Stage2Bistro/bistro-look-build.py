"""BISTRO-LOOK-1: additive dressing, unchanged grid/atlas/names, V4 export."""
import bpy,bmesh,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
bpy.ops.wm.open_mainfile(filepath=str(O/'Stage2Bistro.blend'));sc=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
spec=importlib.util.spec_from_file_location('geom',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
cells={c['name']:c for c in json.loads((O/'textures/atlas.json').read_text())['cells']};mat=bpy.data.materials['Restaurant_Atlas_Bistro']
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
 for d in ao.data:d.color=(.86,.86,.86,1)
 return ob
def remap(ob,p,col):
 uv=ob.data.uv_layers[0].data;avg=sum((uv[i].uv for i in p.loop_indices),Vector((0,0)))/len(p.loop_indices);oldx=min(7,max(0,int(avg.x*8)));oldy=min(3,max(0,int((1-avg.y)*4)));n=cells[col]['index'];delta=Vector(((n%8-oldx)/8,-(n//8-oldy)/4))
 for i in p.loop_indices:uv[i].uv+=delta
def light(n,loc,power,radius=.20):
 d=bpy.data.lights.new(n,'POINT');d.energy=power;d.color=(1,.60,.27);d.shadow_soft_size=radius;q=bpy.data.objects.new(n,d);sc.collection.objects.link(q);q.location=loc
if not sc.get('bistro_look1_v1'):
 # Cell remaps survive the runtime's shared-material replacement; no atlas edits.
 painted={}
 for ob in list(sc.objects):
  if ob.type!='MESH' or ob.name.startswith('REVIEW_'):continue
  count=0;ao=ob.data.color_attributes.get('LocalAO')
  for p in ob.data.polygons:
   c=ob.matrix_world@p.center;dest=None;factor=1
   if ob.name=='GridFloor' and c.z>-.02:
    tx=int(math.floor(c.x+4));ty=int(math.floor(2.5-c.y))
    if tx<4:dest=['tile1','tile2','tile3'][(tx+2*ty)%3];factor=.84
    else:factor=.73+.14*((tx*13+ty*7)%5)/4
   elif ob.name.startswith('RearMasonry_'):dest='stonecream' if sum(map(ord,ob.name))%5==0 else 'plaster';factor=.9
   if dest:remap(ob,p,dest);count+=1
   if ao and factor!=1:
    for i in p.loop_indices:
     r,g,b,a=ao.data[i].color;ao.data[i].color=(r*factor,g*factor,b*factor,a)
  if count:painted[ob.name]=count
 # Runners stay flush: 9mm above floor; no fixed seating or station obstruction.
 for n,x,y,w,d in [('DiningRunner',2.8,0,1.3,3.6),('TerraceRunner',7.45,0,.82,3.6)]:
  g=H.Geometry();g.box((x,y,.045),(w,d,.010),'teal' if n=='DiningRunner' else 'navy')
  for sx in [-1,1]:
   g.box((x+sx*(w/2-.06),y,.052),(.035,d-.09,.003),'rope')
  for sy in [-1,1]:
   g.box((x,y+sy*(d/2-.07),.052),(w-.10,.035,.003),'rope')
   for i in range(7):g.box((x-w*.39+i*w*.13,y+sy*(d/2+.025),.046),(.018,.065,.003),'rope')
  obj('BistroLook_'+n,g)
 # Real menu board, framed against the back wall, below the awning's upper band.
 g=H.Geometry();g.box((3.65,2.39,1.14),(.65,.085,.77),'wooddark');g.box((3.65,2.34,1.14),(.55,.025,.66),'dark')
 for j,w in enumerate([.32,.38,.30,.36]):
  g.box((3.61,2.32,1.38-j*.15),(w,.008,.018),'white');g.box((3.84,2.318,1.38-j*.15),(.035,.009,.018),'brass')
 obj('BistroLook_WallMenu',g)
 # Floor-standing cargo/plants sit outside the approved grid; one herb pot is sill-mounted.
 def copy_at(src,n,center,scale=1):
  q=src.copy();q.data=src.data.copy();q.name=n;sc.collection.objects.link(q);q.scale=tuple(v*scale for v in src.scale);bpy.context.view_layer.update();pts=[q.matrix_world@v.co for v in q.data.vertices];base=Vector(((min(v.x for v in pts)+max(v.x for v in pts))/2,(min(v.y for v in pts)+max(v.y for v in pts))/2,min(v.z for v in pts)));q.location+=Vector(center)-base;return q
 for i,(x,y,s) in enumerate([(6.65,-2.79,.6),(8.45,2.8,.65),(1.25,2.43,.3)]):
  copy_at(bpy.data.objects['PlantPot1'],'BistroLook_EdgeHerb'+str(i),(x,y,.04 if i<2 else 1.05),s)
 for i,(x,y,z) in enumerate([(-3.45,-2.9,.04),(-2.95,-2.91,.04),(-3.45,-2.9,.40)]):copy_at(bpy.data.objects['Crate'],'BistroLook_JettyCrate'+str(i),(x,y,z),.72)
 # Jetty cord and high side-terrace cord: sky and doorway remain open.
 for n,a,b,height,drop,bulbs in [('Jetty',(-4.25,-3.11),(5.85,-3.11),1.85,.20,24),('Terrace',(6.25,2.70),(8.9,2.70),2.22,.20,9)]:
  g=H.Geometry();pts=[(a[0]+(b[0]-a[0])*i/40,a[1]+(b[1]-a[1])*i/40,height-drop*math.sin(math.pi*i/40)) for i in range(41)];g.tube(pts,[.012]*41,6,'dark')
  for x,y in [a,b]:g.tube([(x,y,.02),(x,y,height+.06)],[.025,.025],8,'navy')
  for i in range(bulbs):
   t=(i+.5)/bulbs;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;z=height-drop*math.sin(math.pi*t);g.ellipsoid((x,y,z-.045),(.033,.033,.05),8,3,'glow')
  obj('BistroLook_'+n+'Festoon',g)
 # Compact metal lanterns on the terrace perimeter (not on usable floor cells).
 for i,y in enumerate([-2.69,2.69]):
  x=8.45;g=H.Geometry();g.box((x,y,.08),(.22,.22,.08),'navy');g.box((x,y,.24),(.13,.13,.25),'glow');g.box((x,y,.39),(.23,.23,.06),'navy')
  for dx in [-.082,.082]:
   for dy in [-.082,.082]:g.tube([(x+dx,y+dy,.11),(x+dx,y+dy,.38)],[.012,.012],6,'brass')
  obj('BistroLook_TerraceLantern'+str(i),g);light('BistroLook_LanternPool'+str(i),(x,y,.52),20,.13)
 for ob in sc.objects:
  if ob.type!='LIGHT':continue
  if ob.data.type=='SUN':ob.data.energy=.14
  elif ob.data.type=='AREA':ob.data.energy*=.38;ob.data.color=(1,.77,.55)
  elif ob.name.startswith(('WallLantern','WindowWash')):ob.data.energy*=.65
  elif ob.name.startswith('GridTerraceWarm'):ob.data.energy=30
 # Interior pools are illustrative recipe positions, not fixed table placement.
 for i,(x,y) in enumerate([(1.7,-1.1),(3.9,.65),(1.7,1.35),(7.4,-.9),(7.4,1.25)]):light('BistroLook_WarmPool'+str(i),(x,y,1.8),24,.26)
 for i,x in enumerate([-2.8,.3,3.6]):light('BistroLook_JettyPool'+str(i),(x,-2.95,1.55),13,.22)
 sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.18;sc.view_settings.exposure=-.4;sc['bistro_look1_v1']=True
 (O/'bistro-look-changes.json').write_text(json.dumps({'repainted_faces':painted,'atlas_unchanged':True,'grid_geometry_unchanged':True,'runners_max_z_m':.0535,'floor_standing_cargo_and_plants_off_grid':True,'sill_mounted_herb_pot':True,'warm_pools':'illustrative anchors; native tables own moving light pools'},indent=2))
prod=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')];bpy.context.view_layer.update();rows=[]
for o in prod:
 o.data.calc_loop_triangles();pts=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'export_name':'EXPORT_'+o.name,'triangles':len(o.data.loop_triangles),'world_min_m':[min(v[k] for v in pts) for k in range(3)],'world_max_m':[max(v[k] for v in pts) for k in range(3)],'linked_V2':o.get('kit_source','')})
M=json.loads((O/'build-metrics.json').read_text());M.update(production_meshes=rows,room_triangles=sum(r['triangles'] for r in rows),bistro_look1=True);(O/'build-metrics.json').write_text(json.dumps(M,indent=2))
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in prod:q=o.copy();q.data=o.data.copy();q.name='EXPORT_'+o.name;sc.collection.objects.link(q);q.select_set(True);copies.append(q)
bpy.ops.export_scene.fbx(filepath=str(O/'Stage2Bistro.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
for q in copies:bpy.data.objects.remove(q,do_unlink=True)
recipe=json.loads((O/'lighting.json').read_text());recipe.update(world_strength=.18,exposure_ev=-.4,bistro_look1='warm practical pools, reduced broad fill; warm-pool anchors illustrative, usable tables remain runtime-placed',URP_units_not_equivalent_to_watts=True)
recipe['lights']=[{'name':o.name,'type':o.data.type,'position_blender_m':list(o.location),'position_unity_m':[o.location.x,o.location.z,-o.location.y],'blender_power':o.data.energy,'linear_rgb':list(o.data.color),'range_recipe_m':2.5 if o.name.startswith('BistroLook_') else 4,'radius_m':o.data.shadow_soft_size} for o in sc.objects if o.type=='LIGHT'];(O/'lighting.json').write_text(json.dumps(recipe,indent=2))
recipe['preview_only_lights']=[r for r in recipe['lights'] if r['name'].startswith('BistroLook_WarmPool')]
recipe['lights']=[r for r in recipe['lights'] if not r['name'].startswith('BistroLook_WarmPool')]
recipe['preview_only_reason']='Illustrative table pools for the Blender proof. Native layout already places and lights each usable table; do not import these five anchors.'
(O/'lighting.json').write_text(json.dumps(recipe,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage2Bistro.blend'));print('BISTRO LOOK BUILD PASS',M['room_triangles'],len(rows),flush=True)

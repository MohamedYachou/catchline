import bpy,bmesh,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
STAGE=O.name
bpy.ops.wm.open_mainfile(filepath=str(O/'_kitchen-look-backup'/(STAGE+'.blend')));sc=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
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
 for d in ao.data:d.color=(.86,.86,.86,1)
 return ob
def remap(ob,p,col):
 uv=ob.data.uv_layers[0].data;avg=sum((uv[i].uv for i in p.loop_indices),Vector((0,0)))/len(p.loop_indices);oldx=min(7,max(0,int(avg.x*8)));oldy=min(3,max(0,int((1-avg.y)*4)));n=cells[col]['index'];delta=Vector(((n%8-oldx)/8,-(n//8-oldy)/4))
 for i in p.loop_indices:uv[i].uv+=delta
def light(n,loc,power,radius=.20):
 d=bpy.data.lights.new(n,'POINT');d.energy=power;d.color=(1,.60,.27);d.shadow_soft_size=radius;q=bpy.data.objects.new(n,d);sc.collection.objects.link(q);q.location=loc

# Preserve all vertices/pivots/footprints. Change only atlas cells and vertex pigment.
painted={}
for ob in list(sc.objects):
 if ob.type!='MESH' or ob.name.startswith('REVIEW_'):continue
 count=0
 for poly in ob.data.polygons:
  c=ob.matrix_world@poly.center;dest=None;tint=None
  if ob.name in ['RoomShell','GridFloor'] and poly.normal.z>.65 and -.03<c.z<.10 and -4<c.x<(-1 if STAGE=='Stage1V4' else 0) and -2.5<c.y<2.5:
   dest='white' if (math.floor(c.x+4+1e-5)+math.floor(2.5-c.y+1e-5))%4==0 else 'tile3';tint=(1,.955,.875)
  elif ob.name.startswith('RearMasonry_') and c.x<(-1 if STAGE=='Stage1V4' else 0):
   dest='white' if sum(map(ord,ob.name))%4==0 else 'stonecream';tint=(1,.965,.91)
  elif ob.name in ['FridgeV2','Oven','Stove'] and abs(poly.normal.y)>.8:
   uv=ob.data.uv_layers[0].data;avg=sum((uv[i].uv for i in poly.loop_indices),Vector((0,0)))/len(poly.loop_indices);idx=min(3,max(0,int((1-avg.y)*4)))*8+min(7,max(0,int(avg.x*8)))
   if idx in [0,2,3,7,14,15,16,18]:dest='steel'
  if dest:remap(ob,poly,dest);count+=1
  if tint:
   ao=ob.data.color_attributes.get('LocalAO')
   if ao:
    for i in poly.loop_indices:
     v=ao.data[i].color;ao.data[i].color=tuple(v[k]*tint[k] for k in range(3))+(v[3],)
 if count:painted[ob.name]=count
# Wall-mounted extractor: sloping steel canopy, dark baffle slots, short chimney.
g=H.Geometry();x=-3.43;y=2.05
# Hand-authored trapezoidal frustum; underside high enough to clear every station.
verts=[(x+dx,y+dy,z) for z,w,d in [(1.76,1.05,.63),(2.08,.54,.29)] for dx,dy in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
g.vertices.extend(verts);g.faces.extend([(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);g.colours.extend(['dark','steel','steel','steel','steel','steel'])
g.box((x,y,2.18),(.40,.26,.23),'steel');g.box((x,1.716,1.775),(1.10,.055,.075),'steel')
for i in range(9):g.box((x-.43+i*.107,1.68,1.78),(.055,.012,.023),'dark')
g.box((x,1.86,1.751),(.80,.045,.025),'glow');obj('KitchenLook_ExtractorHood',g)
# Higher cookware shelf clear of the incumbent crockery shelf; substantial pot silhouettes.
g=H.Geometry();g.box((-1.90,2.26,1.89),(1.75,.37,.065),'wooddark');g.box((-1.90,2.055,1.90),(1.80,.035,.075),'steel')
for x in [-2.56,-1.25]:g.box((x,2.32,1.79),(.045,.12,.20),'steel')
obj('KitchenLook_PotShelf',g)
for i,x in enumerate([-2.54,-2.04,-1.49]):
 g=H.Geometry();r=.14 if i!=1 else .17;z=1.94
 g.tube([(x,2.24,z),(x,2.24,z+.18)],[r,r*.97],12,'steel' if i!=1 else 'navy');g.tube([(x,2.24,z+.18),(x,2.24,z+.20)],[r*1.04,r*.96],12,'steel');g.ellipsoid((x,2.24,z+.21),(.035,.035,.023),8,3,'dark')
 for sx in [-1,1]:g.tube([(x+sx*r,2.24,z+.11),(x+sx*(r+.09),2.24,z+.11)],[.023,.023],7,'dark')
 obj('KitchenLook_StockPot'+str(i),g)
# Distinct hanging tools, rather than another row of cups. Positioned right of hood.
g=H.Geometry();g.tube([(-.98,2.01,1.36),(-.12,2.01,1.36)],[.018,.018],8,'brass')
for i,x in enumerate([-.88,-.72,-.56,-.40,-.24]):
 g.tube([(x,1.98,1.36),(x,1.96,1.31),(x,1.96,1.05)],[.012,.018,.018],7,'steel')
 if i%3==0:g.ellipsoid((x,1.94,1.025),(.055,.026,.08),10,4,'steel')
 elif i%3==1:
  g.box((x,1.94,1.02),(.10,.025,.12),'steel')
  for dx in [-.025,0,.025]:g.box((x+dx,1.923,1.02),(.009,.005,.065),'dark')
 else:
  for dx in [-.04,0,.04]:g.tube([(x,1.96,1.10),(x+dx,1.94,1.03),(x+dx,1.94,.99)],[.008]*3,6,'steel')
obj('KitchenLook_UtensilRail',g)
# Warm task illumination on the rear working zone; moving table lights are untouched.
for i,(x,y,z,power) in enumerate([(-3.43,1.65,1.68,28),(-2.04,1.92,1.77,18)]):light('KitchenLook_Task'+str(i),(x,y,z),power,.18)
(O/'kitchen-look-changes.json').write_text(json.dumps({'atlas_remapped_faces':painted,'geometry_preserved':True,'new_static_wall_dressing':['KitchenLook_ExtractorHood','KitchenLook_PotShelf','KitchenLook_StockPot0','KitchenLook_StockPot1','KitchenLook_StockPot2','KitchenLook_UtensilRail'],'station_names_and_footprints_unchanged':True,'native_station_faces_note':'FridgeV2/Oven/Stove UV steel-face remaps apply to source nodes; native hides layout placeholders, carry these finishes to native station models when importing.'},indent=2))
prod=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')];bpy.context.view_layer.update();rows=[]
for o in prod:
 o.data.calc_loop_triangles();pts=[o.matrix_world@v.co for v in o.data.vertices];rows.append({**next((r for r in json.loads((O/'build-metrics.json').read_text())['production_meshes'] if r['name']==o.name),{'linked_V2':False}),'name':o.name,'triangles':len(o.data.loop_triangles),'world_min_m':[min(v[k] for v in pts) for k in range(3)],'world_max_m':[max(v[k] for v in pts) for k in range(3)]})
M=json.loads((O/'build-metrics.json').read_text());M.update(production_meshes=rows,room_triangles=sum(r['triangles'] for r in rows),kitchen_look1=True);(O/'build-metrics.json').write_text(json.dumps(M,indent=2))
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in prod:
 q=o.copy();q.data=o.data.copy();q.name='EXPORT_'+o.name;sc.collection.objects.link(q);q.select_set(True);copies.append(q)
bpy.ops.export_scene.fbx(filepath=str(O/(STAGE+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
for q in copies:bpy.data.objects.remove(q,do_unlink=True)
recipe=json.loads((O/'lighting.json').read_text());recipe['kitchen_look1']='Two warm wall-task practicals under hood/shelf. Keep existing layout-driven station/table lights. No change to world/exposure.'
recipe['lights']=[r for r in recipe['lights'] if not r['name'].startswith('KitchenLook_')]
recipe['lights'] += [{'name':o.name,'type':'POINT','position_blender_m':list(o.location),'position_unity_m':[o.location.x,o.location.z,-o.location.y],'blender_power':o.data.energy,'linear_rgb':list(o.data.color),'range_recipe_m':1.6,'radius_m':o.data.shadow_soft_size} for o in sc.objects if o.type=='LIGHT' and o.name.startswith('KitchenLook_')]
(O/'lighting.json').write_text(json.dumps(recipe,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/(STAGE+'.blend')));print('KITCHEN LOOK BUILD PASS',STAGE,len(rows),M['room_triangles'],flush=True)

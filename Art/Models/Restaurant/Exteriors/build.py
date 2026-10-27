"""Additive stage-two kit derived from accepted V4. Never writes upstream."""
import bpy,bmesh,json,math,hashlib,shutil,sys,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V4';R=O.parents[3];sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('geom',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
T=O/'textures';T.mkdir(exist_ok=True)
for n in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:shutil.copyfile(V/'textures'/n,T/n)
cells={c['name']:c for c in json.loads((T/'atlas.json').read_text())['cells']}
sourcehash=hashlib.sha256((V/'Stage1V4.blend').read_bytes()).hexdigest()
bistrohash=hashlib.sha256((O.parent/'Stage3Restaurant/Stage3Restaurant.blend').read_bytes()).hexdigest()
mat=bpy.data.materials.new('Restaurant_Exterior_Atlas');mat.use_nodes=True;ns=mat.node_tree.nodes;lk=mat.node_tree.links;bs=ns.get('Principled BSDF');im=ns.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(T/'Restaurant_BaseColor.png'));im.image.pack();lk.new(im.outputs['Color'],bs.inputs['Base Color']);sf=ns.new('ShaderNodeTexImage');sf.image=bpy.data.images.load(str(T/'Restaurant_Surface.png'));sf.image.colorspace_settings.name='Non-Color';sf.image.pack();sep=ns.new('ShaderNodeSeparateColor');lk.new(sf.outputs['Color'],sep.inputs[0]);lk.new(sep.outputs['Red'],bs.inputs['Roughness']);lk.new(sep.outputs['Green'],bs.inputs['Metallic']);lk.new(im.outputs['Color'],bs.inputs['Emission Color']);mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=2.5;lk.new(sep.outputs['Blue'],mul.inputs[0]);lk.new(mul.outputs[0],bs.inputs['Emission Strength'])
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
# Facade faces Blender +Y / Unity -Z, toward the water. All stages share footprint centre.
def window(g,x,y,z,w=.85,h=1.05,shutters=True):
 box(g,(x,y,z),(w,.065,h),'wooddark');box(g,(x,y+.043,z),(w-.10,.03,h-.10),'glow')
 for xx in [x-w/2,x,x+w/2]:box(g,(xx,y+.07,z),(.045,.075,h+.09),'ivory')
 for zz in [z-h/2,z,z+h/2]:box(g,(x,y+.07,zz),(w+.09,.075,.045),'ivory')
 box(g,(x,y+.12,z-h/2-.07),(w+.25,.22,.10),'stonecream')
 if shutters:
  for side in [-1,1]:
   xx=x+side*(w/2+.18);box(g,(xx,y+.055,z),(.25,.075,h),'navy')
   for j in range(7):box(g,(xx,y+.101,z-h*.40+j*h*.13),(.21,.028,.026),'blue')
def planter(g,x,y,z,w=.9):
 box(g,(x,y,z),(w,.28,.23),'wooddark');box(g,(x,y+.15,z+.07),(w+.04,.035,.08),'woodlight')
 for j in range(6):
  xx=x-w*.40+j*w*.16;g.ellipsoid((xx,y,z+.21+(.04 if j%2 else 0)),(.13,.17,.16),8,3,'leaf')
  if j%2==0:g.ellipsoid((xx,y+.08,z+.31),(.055,.05,.05),8,3,'orange')
def lantern(g,x,y,z):
 box(g,(x,y,z),(.14,.16,.24),'glow')
 for dx in [-.085,.085]:
  for dy in [-.095,.095]:tube(g,(x+dx,y+dy,z-.14),(x+dx,y+dy,z+.14),.014,'brass',6)
 box(g,(x,y,z+.16),(.24,.25,.06),'navy');box(g,(x,y,z-.15),(.20,.22,.045),'brass')
def roof(g,cx,w,eave,ridge):
 a=w/2+.22;b=2.73
 v=[(cx-a,-b,eave),(cx+a,-b,eave),(cx,-b,ridge),(cx-a,b,eave),(cx+a,b,eave),(cx,b,ridge)]
 g.add(v,[(0,1,2),(3,5,4)],'plaster');g.add(v,[(0,3,4,1)],'wooddark')
 # Overlapping bands and tile joints follow the slope, no flat presentation caps.
 for side in [-1,1]:
  for i in range(8):
   t0=i/8;t1=(i+1.10)/8;x0=cx+side*a*t0;x1=cx+side*a*t1;z0=ridge-(ridge-eave)*t0+.025;z1=ridge-(ridge-eave)*t1+.025
   for j in range(13):
    y0=-b+j*(2*b/13);y1=y0+2*b/13-.012
    g.add([(x0,y0,z0),(x1,y0,z1),(x1,y1,z1),(x0,y1,z0)],[(0,1,2,3)],'blue' if (i+j)%5==0 else 'navy')
   tube(g,(x1,-b,z1),(x1,b,z1),.018,'navy',6)
  tube(g,(cx,b,ridge+.045),(cx+side*a,b,eave),.055,'woodlight')
  tube(g,(cx+side*a,-b,eave),(cx+side*a,b,eave),.065,'navy')
 tube(g,(cx,-b,ridge+.04),(cx,b,ridge+.04),.065,'navy')
def signtext(text,x,y,z,width):
 cu=bpy.data.curves.new('SignLettering','FONT');cu.body=text;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=.38;cu.extrude=.008;cu.bevel_depth=.003;cu.bevel_resolution=0
 ob=bpy.data.objects.new('RestaurantSignLettering',cu);sc.collection.objects.link(ob);ob.location=(x,y,z);ob.rotation_euler=(math.pi/2,0,math.pi) # text normal toward +Y
 # x direction reversed by 180; use correct +X facing camera through -90 around X.
 ob.rotation_euler=(math.pi/2,0,math.pi)
 bpy.context.view_layer.update()
 if ob.dimensions.x>width:ob.scale*=width/ob.dimensions.x
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');me=ob.data;me.materials.append(mat)
 for layer in list(me.uv_layers):me.uv_layers.remove(layer)
 uv=me.uv_layers.new(name='UV0');c=cells['brass'];x0,y0,w,h=c['pixel_cell']
 for d in uv.data:d.uv=((x0+w*.5)/2048,1-(y0+h*.5)/2048)
 new.append(ob);return ob
# Build each stage in isolation. Ground-footprint origin is identical; terrace is an overhang.
manifest=[]
for stage,label,W,module_widths,terracedepth in [(1,'Cafe',8,[5.2,2.8],1.65),(2,'Bistro',10,[5.2,4.8],2.5),(3,'Restaurant',12,[5.2,4.0,2.8],3.0),(4,'SeafoodHouse',14,[5.2,5.0,3.8],3.5)]:
 for ob in list(sc.objects):bpy.data.objects.remove(ob,do_unlink=True)
 new.clear();left=-W/2;g=H.Geometry();fac=H.Geometry();rg=H.Geometry();plants=H.Geometry();lights=[]
 # Warm pale masonry with blue corner trim, separate gabled joined houses.
 for mi,mw in enumerate(module_widths):
  cx=left+mw/2;wall=3.75 if mi==0 else 3.38;ridge=5.30 if mi==0 else (4.75 if mi==1 else 4.5)
  box(g,(cx,0,wall/2),(mw,5,wall),'plaster' if mi%2 else 'ivory');box(g,(cx,0,.20),(mw+.03,5.03,.40),'stonecream')
  roof(rg,cx,mw,wall,ridge)
  # Front lower shop windows and upper shuttered room windows.
  n=max(2,round(mw/1.55))
  for j in range(n):
   xx=left+(j+.5)*mw/n
   if mi==0 and j==n//2:
    box(fac,(xx,2.565,.99),(.90,.13,1.98),'navy');box(fac,(xx,2.65,1.3),(.66,.045,.90),'glow');box(fac,(xx+.27,2.70,.91),(.04,.06,.07),'brass');box(fac,(xx,2.77,.065),(1.1,.55,.13),'stonecool')
   else:window(fac,xx,2.55,1.22,1.02,1.30,False)
  for j in range(max(2,round(mw/2))):
   xx=left+(j+.5)*mw/max(2,round(mw/2));window(fac,xx,2.55,2.91,.70,.85,True);planter(plants,xx,2.76,2.34,.84)
  # Chimney and simple ridge finial, hand-painted bands at corners.
  box(fac,(cx+.75,-.95,ridge-.12),(.42,.46,.90),'stonecream');box(fac,(cx+.75,-.95,ridge+.37),(.54,.58,.10),'wooddark')
  for xx in [left+.045,left+mw-.045]:
   box(fac,(xx,2.55,wall/2),(.11,.10,wall),'woodlight')
   for z in [.42,.72,1.02]:box(fac,(xx,2.57,z),(.22,.12,.14),'stonecream')
  # Side windows, visible from harbour oblique.
  if mi==0:
   for yy in [-1.45,.50]:
    box(fac,(left-.025,yy,1.45),(.055,.85,1.05),'navy');box(fac,(left-.06,yy,1.45),(.025,.70,.90),'glow')
    for yy2 in [yy-.38,yy,yy+.38]:box(fac,(left-.085,yy2,1.45),(.04,.045,1.03),'ivory')
  left+=mw
 obj('ExteriorWalls',g,.018);obj('BlueTiledRoofs',rg);obj('DoorsWindowsChimneys',fac,.005)
 # Painted awning, gently scalloped valance with ivory piping.
 g=H.Geometry();aw=W-.65;ay=3.36
 box(g,(0,3.05,2.18),(aw,1.18,.09),'navy')
 for i in range(math.ceil(aw/.34)):
  xx=-aw/2+(i+.5)*aw/math.ceil(aw/.34);box(g,(xx,3.64,2.08),(aw/math.ceil(aw/.34)-.008,.075,.17),'navy');tube(g,(xx-.12,3.688,2.02),(xx+.12,3.688,2.02),.012,'ivory',6)
 tube(g,(-aw/2,3.65,2.19),(aw/2,3.65,2.19),.025,'ivory')
 for xx in [-aw/2,aw/2]:tube(g,(xx,3.60,0),(xx,3.60,2.22),.035,'navy')
 obj('BlueAwning',g)
 # Sign spans frontage at the shop line; stage 4 earns the sculpted fish crest.
 g=H.Geometry();box(g,(0,3.69,2.12),(min(W-.8,6.8),.16,.47),'navy');box(g,(0,3.78,2.35),(min(W-.75,6.85),.045,.035),'brass');obj('RestaurantSignBoard',g,.012)
 tx=signtext({'Cafe':'CAFE','Bistro':'BISTRO','Restaurant':'RESTAURANT','SeafoodHouse':'SEAFOOD HOUSE'}[label],0,3.785,2.12,min(W-1.2,6.3));tx.name='RestaurantSignLetters'
 if stage==4:
  g=H.Geometry();g.ellipsoid((0,2.76,4.22),(1.0,.14,.29),16,6,'steel');g.add([(.75,2.77,4.22),(1.27,2.77,3.85),(1.27,2.77,4.57)],[(0,1,2)],'brass');g.ellipsoid((-.71,2.91,4.28),(.055,.035,.055),10,4,'navy');tube(g,(-.55,2.92,4.04),(-.55,2.92,4.36),.018,'brass');obj('SeafoodFishCrest',g)
 # Full wooden terrace, contact floor Z0 and piles below. Shared anchor stays at room centre.
 g=H.Geometry();front=2.5+terracedepth;box(g,(0,2.5+terracedepth/2,-.13),(W+.36,terracedepth,.26),'wooddark')
 for i in range(math.ceil(terracedepth/.23)):
  yy=2.5+(i+.5)*terracedepth/math.ceil(terracedepth/.23);box(g,(0,yy,.012),(W+.26,terracedepth/math.ceil(terracedepth/.23)-.012,.04),'woodlight' if i%4==0 else 'wood')
 for xx in [-W/2+.15,0,W/2-.15]:
  for yy in [2.68,front-.12]:tube(g,(xx,yy,-1),(xx,yy,-.08),.10,'wooddark')
 obj('TerraceDeckPiles',g,.006)
 g=H.Geometry()
 for xx in [-W/2,W/2]:
  for yy in [2.75,front-.08]:tube(g,(xx,yy,0),(xx,yy,.76),.035,'navy')
  tube(g,(xx,2.75,.56),(xx,front-.08,.56),.02,'rope')
 for x0,x1 in [(-W/2,-.8),(.8,W/2)]:
  for xx in [x0,x1]:tube(g,(xx,front-.08,0),(xx,front-.08,.76),.035,'navy')
  tube(g,(x0,front-.08,.56),(x1,front-.08,.56),.025,'rope')
 obj('TerraceRails',g)
 # Bistro and above have dining; cafe has compact outdoor two-tops.
 g=H.Geometry();count=[2,3,4,5][stage-1]
 for j in range(count):
  xx=-W/2+1.0+j*(W-2)/(count-1);yy=2.5+terracedepth*.60
  box(g,(xx,yy,.69),(.85,.72,.08),'woodlight' if stage<3 else 'ivory');tube(g,(xx,yy,0),(xx,yy,.65),.065,'navy')
  for dx in [-.63,.63]:
   box(g,(xx+dx,yy,.40),(.36,.42,.07),'woodlight');box(g,(xx+dx+(-.17 if dx<0 else .17),yy,.65),(.045,.43,.42),'navy')
   for dy in [-.16,.16]:tube(g,(xx+dx,yy+dy,0),(xx+dx,yy+dy,.38),.025,'navy',6)
  if stage>1:lantern(g,xx,yy,.89)
 obj('TerraceTablesChairs',g,.007)
 # Lush entrance plants and facade climbing foliage make the progression warmer.
 for xx in [-W/2+.28,W/2-.28]:
  g=plants;g.tube([(xx,front-.35,.02),(xx,front-.35,.46)],[.20,.27],12,'terracotta')
  for z in [.55,.76,1.01]:g.ellipsoid((xx,front-.35,z),(.31,.26,.25),10,4,'leaf')
 if stage>1:
  for xx in [-W/2+.05,W/2-.05]:
   tube(plants,(xx,2.72,.15),(xx,2.72,3.2),.035,'wooddark')
   for j in range(12):plants.ellipsoid((xx+math.sin(j*1.7)*.15,2.74,.3+j*.25),(.18,.11,.17),8,3,'leaf')
 obj('FlowerBoxesEntrancePlants',plants)
 g=H.Geometry()
 for xx in [-W/2+.45,W/2-.45]:lantern(g,xx,2.8,1.85);lights.append([xx,2.98,1.85])
 if stage>=2:
  for xx in [-W/2+.15,W/2-.15]:tube(g,(xx,front-.15,0),(xx,front-.15,2.35),.035,'navy')
  path=[(-W/2+.15+(W-.3)*i/40,front-.15,2.32-.32*math.sin(math.pi*i/40)) for i in range(41)];g.tube(path,[.014]*41,6,'dark')
  for i in range(stage*3):
   t=(i+.5)/(stage*3);xx=-W/2+.15+(W-.3)*t;zz=2.29-.32*math.sin(math.pi*t);g.ellipsoid((xx,front-.15,zz),(.045,.045,.065),8,3,'glow');lights.append([xx,front-.15,zz])
 obj('LanternsStringLights',g)
 # Unified data conventions: UV0 painted atlas, UV1 positive-area separated charts, local AO.
 prod=[o for o in sc.objects if o.type=='MESH'];rows=[]
 for o in prod:
  me=o.data;bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.get('LightmapUV') or me.uv_layers.new(name='LightmapUV');grid=math.ceil(math.sqrt(len(me.polygons)))
  for j,p in enumerate(me.polygons):
   for li,(u,v) in zip(p.loop_indices,[(.12,.12),(.88,.12),(.12,.88)]):uv.data[li].uv=((j%grid+u)/grid,(j//grid+v)/grid)
  me.uv_layers.active_index=0
  if not me.color_attributes:
   ao=me.color_attributes.new(name='LocalAO',type='BYTE_COLOR',domain='CORNER')
   for d in ao.data:d.color=(.9,.9,.9,1)
  bpy.context.view_layer.update();me.calc_loop_triangles();pts=[o.matrix_world@v.co for v in me.vertices];rows.append({'name':o.name,'triangles':len(me.loop_triangles),'min_m':[min(v[k] for v in pts) for k in range(3)],'max_m':[max(v[k] for v in pts) for k in range(3)]})
 sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 filename='RestaurantExterior_'+label
 bpy.ops.object.select_all(action='DESELECT')
 for o in prod:o.select_set(True)
 bpy.context.view_layer.objects.active=prod[0];bpy.ops.export_scene.fbx(filepath=str(O/(filename+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',colors_type='LINEAR',global_scale=1,axis_forward='-Z',axis_up='Y',use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE')
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(filename+'.blend')))
 footprint={'stage':stage,'name':label,'tiles':[W,5],'tile_m':1,'origin':'room footprint centre; floor contact Blender Z0 / Unity Y0','facade_blender_direction':[0,1,0],'facade_unity_direction':[0,0,-1],'unity_local_rotation_euler':[0,0,0],'room_bounds_blender_m':[[-W/2,-2.5,0],[W/2,2.5,0]],'terrace_overhang_depth_m':terracedepth,'terrace_front_blender_y_m':front,'quay_placement_unity_example_m':[0,.35,4.95],'placement_note':'Example centre Z4.95 puts facade at Unity Z2.45 near water edge2.3; terrace projects toward negativeZ/water. Choose free corner slot; not an instruction to overlap existing houses.','lamp_positions_blender_m':lights,'axis_conversion':'[x,z,-y]','harbour_comparison':'HouseA3x2.6x3.6m and HouseB3.4x2.8x3.9m; restaurant is 8-14m wide joined row, 5.3m main ridge'}
 (O/(filename+'.footprint.json')).write_text(json.dumps(footprint,indent=2));manifest.append({'stage':stage,'name':label,'file':filename+'.fbx','footprint':filename+'.footprint.json','triangles':sum(r['triangles'] for r in rows),'meshes':rows})
(O/'manifest.json').write_text(json.dumps({'stages':manifest,'atlas_source':'../Stage1V4/textures; byte-identical','harbour_source':'VoyageHarbour.cs quayY.35,waterZ<2.3; VoyageGame.cs camera45pitch35yaw','geometry_axes':'Blender metres,Zup; FBX-Zforward,Yup','native_import_unverified':True},indent=2));print('EXTERIORS BUILD PASS',[(r['name'],r['triangles']) for r in manifest],flush=True)

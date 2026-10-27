"""Atlas-coloured arrange-mode furniture. Metres, footprint-centre/floor-contact origins."""
import bpy,bmesh,math,json,hashlib,shutil,sys,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('geometry',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
T=O/'textures';T.mkdir(exist_ok=True)
for n in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:shutil.copyfile(O.parent/'Stage1V4/textures'/n,T/n)
cells={c['name']:c for c in json.loads((T/'atlas.json').read_text())['cells']}
mat=bpy.data.materials.new('Restaurant_Atlas_Upgrades');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(T/'Restaurant_BaseColor.png'));im.image.pack();l.new(im.outputs['Color'],bs.inputs['Base Color']);sf=n.new('ShaderNodeTexImage');sf.image=bpy.data.images.load(str(T/'Restaurant_Surface.png'));sf.image.colorspace_settings.name='Non-Color';sf.image.pack();sep=n.new('ShaderNodeSeparateColor');l.new(sf.outputs['Color'],sep.inputs[0]);l.new(sep.outputs['Red'],bs.inputs['Roughness']);l.new(sep.outputs['Green'],bs.inputs['Metallic']);l.new(im.outputs['Color'],bs.inputs['Emission Color']);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=2.5;l.new(sep.outputs['Blue'],mul.inputs[0]);l.new(mul.outputs[0],bs.inputs['Emission Strength'])
def ell(g,c,r,col,n=12):g.ellipsoid(c,r,n,5,col)
def leaf(g,c,a,length,col):
 x,y,z=c;dx,dy=math.cos(a),math.sin(a);mx,my=x+dx*length*.48,y+dy*length*.48;w=length*.26
 vs=[(x,y,z),(mx-dy*w,my+dx*w,z+.045),(x+dx*length,y+dy*length,z+.13),(mx+dy*w,my-dx*w,z+.045),(mx,my,z+.075),(mx,my,z+.035)]
 g.add(vs,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,5,1),(1,5,2),(2,5,3),(3,5,0)],col)
def tube(g,a,b,r,col,n=8):g.tube([a,b],[r,r],n,col)
def cyl(g,c,r,h,col,n=16):tube(g,(c[0],c[1],c[2]-h/2),(c[0],c[1],c[2]+h/2),r,col,n)
def rounded(g,w,d,z,h,col,corner=.025):
 x,y=w/2,d/2;r=min(corner,x,y);g.extrude_polygon([(-x+r,-y),(x-r,-y),(x,-y+r),(x,y-r),(x-r,y),(-x+r,y),(-x,y-r),(-x,-y+r)],z,z+h,col)
def move(g,c,yaw=0):
 m=Matrix.Translation(Vector(c))@Matrix.Rotation(yaw,4,'Z');g.vertices=[tuple(m@Vector(v)) for v in g.vertices];return g
def merge(g,a):g.add(a.vertices,a.faces,None);g.colours[-len(a.colours):]=a.colours
# Separate reusable chairs, also built into the table assemblies exactly at their seat sockets.
def chair(tier):
 g=H.Geometry();frame='wood' if tier==1 else 'navy';seat='woodlight' if tier==1 else 'teal' if tier==2 else 'navy'
 for x in [-.112,.112]:
  for y in [-.11,.11]:tube(g,(x*1.08,y*1.08,0),(x,y,.35),.020,frame)
 rounded(g,.30,.29,.345,.055,'wood');rounded(g,.275,.265,.40,.035,seat)
 for x in [-.12,.12]:tube(g,(x,.115,.365),(x,.135,.76),.021,frame)
 # Curved back, broad at camera distance, slatted plain wood at tier1.
 if tier==1:
  for z in [.57,.69]:g.box((0,.13,z),(.29,.045,.055),'woodlight')
 else:
  g.box((0,.13,.635),(.275,.055,.20),seat)
  if tier==3:
   for x in [-.12,.12]:ell(g,(x,.13,.755),(.026,.026,.026),'brass',8)
   tube(g,(-.12,.09,.72),(.12,.09,.72),.008,'brass')
 return g

def candle(g,c=(0,0,0),lamp=False):
 x,y,z=c
 cyl(g,(x,y,z+.009),.055,.018,'brass');cyl(g,(x,y,z+.027),.036,.025,'brass')
 if lamp:
  cyl(g,(x,y,z+.090),.012,.12,'brass',12);cyl(g,(x,y,z+.17),.034,.045,'glow',12)
  # Solid small linen shade, with warm lower rim.
  prof=[(.074,.145),(.048,.235)]
  vs=[(x+r*math.cos(i*math.tau/12),y+r*math.sin(i*math.tau/12),z+zz) for r,zz in prof for i in range(12)]
  g.add(vs,[(i,(i+1)%12,(i+1)%12+12,i+12) for i in range(12)]+[tuple(range(12,24))],'white')
  cyl(g,(x,y,z+.147),.075,.008,'brass',12);ell(g,(x,y,z+.245),(.012,.012,.012),'brass',8)
 else:
  cyl(g,(x,y,z+.065),.026,.065,'white',12);tube(g,(x,y,z+.095),(x,y,z+.111),.002,'dark',6)
  ell(g,(x+.003,y,z+.121),(.012,.010,.025),'glow',10)

def table(tier,seats):
 g=H.Geometry();w=.51 if seats==2 else 1.14;d=.49;legs=[(0,0)] if seats==2 else [(-.40,0),(.40,0)]
 for x,y in legs:
  cyl(g,(x,y,.028),.13,.056,'wooddark' if tier==1 else 'navy');tube(g,(x,y,.045),(x,y,.64),.044,'wood' if tier==1 else 'navy',12)
 rounded(g,w,d,.64,.08,'wood',.035)
 # Broad plank seam, only tier1 exposed timber.
 if tier==1:
  for yy in [-.08,.08]:g.box((0,yy,.721),(w-.05,.006,.002),'wooddark')
 else:
  # Continuous tailored cloth over top and four overhanging short folded skirts.
  col='white' if tier==3 else 'teal';rounded(g,w+.012,d+.012,.721,.008,col,.028)
  for yy in [-1,1]:g.box((0,yy*(d/2+.005),.668),(w-.035,.012,.11),col)
  for xx in [-1,1]:g.box((xx*(w/2+.005),0,.668),(.012,d-.035,.11),col)
  if tier==2:rounded(g,w*.49,d+.015,.73,.003,'white',.006)
  candle(g,(0,0,.736),lamp=tier==3)
 seatspec=[(-.33,0,math.pi/2),(.33,0,-math.pi/2)] if seats==2 else [(x,y,math.pi if y<0 else 0) for x in [-.36,.36] for y in [-.33,.33]]
 for x,y,a in seatspec:merge(g,move(chair(tier),(x,y,0),a))
 return g,seatspec
assets=[]
def add(name,g,fp=(1,1),**meta):assets.append((name,g,fp,meta))
for t in [1,2,3]:
 for seats in [2,4]:
  g,s=table(t,seats);add(f'Dining{seats}_Tier{t}',g,(1 if seats==2 else 2,1),tier=t,seats=seats,tabletop_z_m=.72 if t==1 else .736,seat_sockets=[{'position_blender_m':[x,y,0],'yaw_blender_deg':math.degrees(a),'seat_top_z_m':.435} for x,y,a in s],includes_matching_chairs=True)
 add(f'Chair_Tier{t}',chair(t),tier=t,seats=1,seat_top_z_m=.435)
# Wall-mounted decor uses a floor-contact base origin. Runtime raises it to the stated mount height.
g=H.Geometry();path=[(-.44,0,.57),(-.23,-.025,.42),(0,-.035,.34),(.23,-.025,.42),(.44,0,.57)];g.tube(path,[.014]*5,6,'rope')
# Coarse draped net: crossing strands following a trapezoid rather than an opaque panel.
for j in range(7):
 x=-.39+j*.13;top=.53+.18*abs(x);bottom=.03+.09*abs(x);g.tube([(x,0,top),(x*.86,-.035,(top+bottom)/2),(x*.72,-.025,bottom)],[.006]*3,5,'rope')
for j in range(5):
 z=.06+j*.105;g.tube([(-.32-j*.02,-.024,z+.035),(0,-.04,z),(.32+j*.02,-.024,z+.035)],[.006]*3,5,'rope')
for i,x in enumerate([-.40,-.20,0,.20,.40]):ell(g,(x,-.025,.58-.16*(1-abs(x)/.4)),(.033,.035,.046),'orange' if i%2 else 'ivory',10)
# Rope ends touch local zero for the grounded mount contract.
g.tube([(-.30,-.025,.08),(-.30,-.026,0)],[.006]*2,5,'rope');g.tube([(.30,-.025,.08),(.30,-.026,0)],[.006]*2,5,'rope');add('WallNetFloats',g,mount='wall',recommended_base_height_m=1.05)
g=H.Geometry();rounded(g,.88,.045,0,.38,'wooddark',.055);# plaque initially horizontal XY -> turn upright XZ
# replace board with an XZ rounded plaque by transform.
g.vertices=[(x,-z,y+.19) for x,y,z in g.vertices];# now plaque width.88,height.045? correct below
# Explicit bevel-outline board XZ.
g=H.Geometry();panel=H.Geometry();rounded(panel,.88,.38,0,.055,'wooddark',.06);panel.vertices=[(x,-z,y+.19) for x,y,z in panel.vertices];merge(g,panel)
ell(g,(-.01,-.09,.20),(.28,.055,.105),'fish',16);ell(g,(-.245,-.105,.205),(.06,.04,.08),'fish',12)
ell(g,(-.268,-.14,.23),(.012,.006,.012),'dark',8)
g.add([(.21,-.10,.20),(.39,-.10,.32),(.36,-.10,.19),(.39,-.10,.08)],[(0,1,2),(0,2,3)],'navy');tube(g,(.21,-.10,.20),(.38,-.10,.29),.012,'navy');tube(g,(.21,-.10,.20),(.38,-.10,.11),.012,'navy')
g.add([(-.03,-.10,.29),(.06,-.10,.36),(.12,-.10,.27)],[(0,1,2)],'navy');add('WallFishTrophy',g,mount='wall',recommended_base_height_m=1.15)
g=H.Geometry();g.box((0,0,.32),(.52,.055,.64),'wood');g.box((0,-.033,.32),(.45,.012,.56),'dark')
# Legible chalk menu cues: tiny fish, three price rows, no invented economy text.
ell(g,(-.03,-.045,.49),(.10,.006,.036),'white',12);g.add([(.05,-.045,.49),(.12,-.045,.53),(.12,-.045,.45)],[(0,1,2)],'white')
for j,z in enumerate([.37,.28,.19]):
 tube(g,(-.16,-.045,z),(.055-.025*(j%2),-.045,z),.007,'white',6)
 for x in [.12,.155]:ell(g,(x,-.045,z),(.009,.004,.009),'brass',8)
add('WallMenuBoard',g,mount='wall',recommended_base_height_m=.95)
g=H.Geometry();path=[(-.90+i*.10,0,.26+.22*(((-.9+i*.10)/.9)**2)) for i in range(19)];g.tube(path,[.009]*len(path),6,'dark')
for i in range(9):
 x=-.80+i*.20;z=.26+.22*(x/.9)**2;tube(g,(x,0,z),(x,0,z-.05),.012,'brass',8);ell(g,(x,0,z-.083),(.030,.030,.040),'glow',10)
# Independent support pins anchor strand at local floor/base0; wall install can raise the whole prop.
for x in [-.91,.91]:tube(g,(x,0,0),(x,0,.49),.014,'navy',8)
add('StringLights',g,(2,1),mount='wall',recommended_base_height_m=1.00)
for style in [1,2]:
 g=H.Geometry();h=.22 if style==1 else .30;col='terracotta' if style==1 else 'ivory'
 # Broad tapered pot and rolled lip.
 g.tube([(0,0,0),(0,0,h)],[.105,.15],16,col);cyl(g,(0,0,h),.16,.035,col);cyl(g,(0,0,h+.022),.132,.012,'wooddark')
 for j in range(9 if style==1 else 7):
  a=j*2.399;r=.16 if style==1 else .12;height=.26+(j%3)*.065
  stem=[(0,0,h+.02),(r*.45*math.cos(a),r*.45*math.sin(a),h+height*.55),(r*math.cos(a),r*math.sin(a),h+height)]
  g.tube(stem,[.009,.007,.004],6,'leaf')
  for k in [1,2]:
   c=stem[k];leaf(g,c,a+(k-1)*1.25,.22 if style==1 else .17,'leaf' if j%2 else 'lettuce')
 if style==2:
  for j in range(4):
   a=j*1.57;c=(.09*math.cos(a),.09*math.sin(a),h+.43)
   for petal in range(5):
    b=petal*math.tau/5;ell(g,(c[0]+.025*math.cos(b),c[1]+.025*math.sin(b),c[2]),(.022,.022,.010),'white',8)
   ell(g,(c[0],c[1],c[2]+.01),(.012,.012,.008),'brass',8)
 add('PlantPot_Herbs' if style==1 else 'PlantPot_Flowering',g)
g=H.Geometry();candle(g);add('TableCandle',g,placement='tabletop',flame_mesh='separate child TableCandle_Flame',emission='V4 glow cell; Surface.B=1; suggested multiplier2.5; no baked point light')
rows=[]
for name,g,fp,meta in assets:
 me=bpy.data.meshes.new(name);me.from_pydata(g.vertices,[],g.faces);me.update();ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);me.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
 for p,col in zip(me.polygons,g.colours):
  x,y,w,h=cells[col]['pixel_cell'];vs=[me.vertices[me.loops[i].vertex_index].co for i in p.loop_indices];axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis];lo=[min(v[k] for v in vs) for k in axes];hi=[max(v[k] for v in vs) for k in axes]
  for li,v in zip(p.loop_indices,vs):
   a=(v[axes[0]]-lo[0])/max(hi[0]-lo[0],1e-7);b=(v[axes[1]]-lo[1])/max(hi[1]-lo[1],1e-7);uv.data[li].uv=((x+24+a*(w-48))/2048,1-(y+24+b*(h-48))/2048)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 # Slight broad bevels preserve the miniature kit language; UVs remain inside assigned cells.
 mod=ob.modifiers.new('SoftKitEdges','BEVEL');mod.width=.006;mod.segments=1;mod.affect='EDGES';mod.angle_limit=.65;bpy.ops.object.modifier_apply(modifier=mod.name)
 # Repair bevel-generated UV corners where unlike pigments meet.
 me=ob.data;uv=me.uv_layers.active.data
 for p in me.polygons:
  vals=[uv[i].uv.copy() for i in p.loop_indices]
  def fits(c):
   x,y,w,h=c['pixel_cell'];return all((x+16)/2048-1e-6<=v.x<=(x+w-16)/2048+1e-6 and 1-(y+h-16)/2048-1e-6<=v.y<=1-(y+16)/2048+1e-6 for v in vals)
  if any(fits(c) for c in cells.values()):continue
  avg=sum(vals,Vector((0,0)))/len(vals)
  chosen=min(cells.values(),key=lambda c:(avg.x-(c['pixel_cell'][0]+128)/2048)**2+(avg.y-(1-(c['pixel_cell'][1]+256)/2048))**2)
  x,y,w,h=chosen['pixel_cell'];vs=[me.vertices[me.loops[i].vertex_index].co for i in p.loop_indices];axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis];lo=[min(v[k] for v in vs) for k in axes];hi=[max(v[k] for v in vs) for k in axes]
  for li,v in zip(p.loop_indices,vs):
   a=(v[axes[0]]-lo[0])/max(hi[0]-lo[0],1e-7);b=(v[axes[1]]-lo[1])/max(hi[1]-lo[1],1e-7);uv[li].uv=((x+24+a*(w-48))/2048,1-(y+24+b*(h-48))/2048)
 # Snap the lowest sloped tube cap to the declared contact plane.
 floor_delta=-min(v.co.z for v in ob.data.vertices)
 for v in ob.data.vertices:v.co.z+=floor_delta
 meta['contact_correction_m']=floor_delta
 # TableCandle flame remains separately toggleable (named mesh) with the same atlas material.
 export=[ob]
 if name=='TableCandle':
  # Separate vertices above wick by plane; full glowing lobe is >.096m.
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='DESELECT');bpy.ops.object.mode_set(mode='OBJECT')
  me=ob.data
  selected=set()
  for face in me.polygons:
   coord=me.uv_layers.active.data[face.loop_start].uv
   if int(coord.x*8)==3 and int((1-coord.y)*4)==2:selected.update(face.vertices)
  assert selected,'Missing glow faces'
  for v in me.vertices:v.select=v.index in selected
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.separate(type='SELECTED');bpy.ops.object.mode_set(mode='OBJECT');flame=next(o for o in sc.objects if o.select_get() and o!=ob);flame.name='TableCandle_Flame';export.append(flame)
 bpy.context.view_layer.update();points=[o.matrix_world@v.co for o in export for v in o.data.vertices];lo=[min(v[k] for v in points) for k in range(3)];hi=[max(v[k] for v in points) for k in range(3)];assert abs(lo[2])<1e-5,(name,lo);assert hi[0]-lo[0]<=fp[0]+1e-5 and hi[1]-lo[1]<=fp[1]+1e-5,(name,lo,hi,fp)
 for o in export:o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,path_mode='COPY',embed_textures=True)
 tri=0
 for o in export:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 row={'name':name,'tiles_w':fp[0],'tiles_d':fp[1],'tile_size_m':1,'origin_blender_m':[0,0,0],'axis_conversion':'Blender X,Y,Z -> Unity X,Z,-Y','floor_contact_z_m':0,'bounds_blender_m':[lo,hi],'triangles':tri,'export_meshes':[o.name for o in export],'atlas_cells':sorted(set(g.colours)),**meta,'fbx_sha256':hashlib.sha256((O/(name+'.fbx')).read_bytes()).hexdigest()};(O/(name+'.footprint.json')).write_text(json.dumps(row,indent=2));rows.append(row)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'RestaurantUpgrades.blend'));(O/'manifest.json').write_text(json.dumps({'assets':rows,'atlas_source':'../Stage1V4/textures','units':'metres','atlas_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in T.iterdir()}},indent=2));print('UPGRADES BUILD PASS',len(rows),flush=True)

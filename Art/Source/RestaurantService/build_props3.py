"""SERVICE-PROPS-3. Additive Blender sources, canonical atlas, no Unity/git.
One recipe per invocation. All colours are sampled from the immutable atlas with
linear vertex tints (the production shader multiplies BaseMap * COLOR).
"""
import sys, importlib.util, bpy, bmesh, math, json, hashlib, uuid
from pathlib import Path
from mathutils import Vector, Matrix
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[2]
spec=importlib.util.spec_from_file_location('cooking',O/'build_cooking.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
b=c.b
sys.path.insert(0,str(O));sys.modules['build_cooking']=c
box=b.box;ell=b.ell;rod=b.rod;cyl=b.cyl;lathe=b.lathe;torus=b.torus;mesh=b.mesh;PI=math.pi

def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

def paint(ob,cell=None,hexcode=None):
 if cell:
  col,row=b.CELLS[cell];uv=ob.data.uv_layers.active
  for d in uv.data:d.uv=((col+.5)/8,1-(row+.5)/4)
 tint=[1,1,1,1]
 if hexcode:
  col,row=b.CELLS[cell];im=bpy.data.images.get('Restaurant_BaseColor.png');px=int((col+.5)/8*im.size[0]);py=int((1-(row+.5)/4)*im.size[1]);base=im.pixels[(py*im.size[0]+px)*4:(py*im.size[0]+px)*4+3]
  rgb=[int(hexcode[i:i+2],16)/255 for i in [0,2,4]]
  # Blender image pixels are sRGB values for this colour image, not linear shader values.
  tint=[linear(rgb[i])/max(linear(base[i]),1e-6) for i in range(3)]+[1]
 attr=ob.data.color_attributes.get('Color') or ob.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
 for d in attr.data:d.color=tint
 return ob

def finish(name,parts=None,centre=True):
 old=b.PARTS
 if parts is not None:b.PARTS=parts
 for ob in b.PARTS:
  if not ob.data.color_attributes.get('Color'):paint(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for o in b.PARTS:o.select_set(True)
 bpy.context.view_layer.objects.active=b.PARTS[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=name;ob.data.name=name
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);b.clean_geometry(ob)
 coords=[v.co for v in ob.data.vertices];lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)])
 offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 for v in ob.data.vertices:v.co-=offset
 for p in ob.data.polygons:p.material_index=0;p.use_smooth=False
 ob.data.materials.clear();ob.data.materials.append(b.MAT);ob.data.calc_loop_triangles()
 rec=dict(name=name,tris=len(ob.data.loop_triangles),size_xyz_blender_m=list(hi-lo),size_xyz_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],origin_offset_authored=list(offset),vertices=len(ob.data.vertices))
 ob.data.color_attributes.active_color=ob.data.color_attributes['Color'];assert len(ob.data.uv_layers)==1
 ob['service_props_task']='SERVICE-PROPS-3'
 if not centre:
  for v in ob.data.vertices:v.co+=Vector(rec['origin_offset_authored'])
  ob.data.update();ob['pivot']='left attachment end';rec['pivot']='left attachment end'
 b.PARTS=old
 return ob,rec

def gold_coin(x,y,z,r,angle=0):
 paint(lathe('Gold dark milled rim',[(0,0),(r*.88,0),(r,.002),(r,.010),(r*.86,.013),(0,.013)],'gold',12,(x,y,z)),'gold','A8741E')
 paint(cyl('Saturated gold face',(x,y,z+.0133),r*.84,.0018,'white',12),'white','F2C14E')
 paint(box('Gold raised stamp',(x,y,z+.0148),(r*.82,r*.24,.0015),'white',0,angle),'white','FFE49B')
 # Broad highlighted bevel sector, never a white/peach coin face.
 va=[]
 for rr,zz in [(r*.84,z+.0144),(r*.98,z+.0105)]:
  va.extend([(x+rr*math.cos(a+angle),y+rr*math.sin(a+angle),zz) for a in [.20,.72,1.24]])
 paint(b.orient_sheet(mesh('Gold bevel glint',va,[(0,3,4,1),(1,4,5,2)],'white')),'white','FFE49B')

def tip_coins(big=False):
 # Exactly ~0.18m / ~0.30m envelope after bottom-centering.
 r=.035 if big else .029
 stacks=[(-.033,-.026,6),(.060,.010,4)] if big else [(.007,-.012,4)]
 for x,y,n in stacks:
  for i in range(n):gold_coin(x,y,i*.014,r,i*.31)
 loose=[(-.115,-.028),(.115,-.041),(.025,-.094)] if big else [(-.061,-.034),(.061,.012)]
 for i,(x,y) in enumerate(loose):gold_coin(x,y,0,r,i*.8)
 # Smaller folded ivory note supports gold silhouette instead of hiding it.
 s=1.5 if big else 1.;x=-.025;y=.061 if big else .042
 v=[(x-.03*s,y-.021*s,.002),(x+.03*s,y-.021*s,.002),(x-.03*s,y,.029*s),(x+.03*s,y,.029*s),(x-.03*s,y+.021*s,.004),(x+.03*s,y+.021*s,.004)]
 note=b.orient_sheet(mesh('Folded cream tip note',v,[(0,1,3,2),(2,3,5,4)],'crumb'))
 mod=note.modifiers.new('Paper thickness','SOLIDIFY');mod.thickness=.0012;bpy.context.view_layer.objects.active=note;bpy.ops.object.modifier_apply(modifier=mod.name)
 for yy,zz in [(y-.011*s,.017*s),(y+.011*s,.017*s)]:
  stripe=box('Teal banknote band',(x,yy,zz+.001),(.010*s,.015*s,.0015),'teal',0);stripe.rotation_euler.x=math.atan2(.027 if yy<y else -.025,.021)

def ice_cream():
 b.plate(radius=.105,n=16)
 paint(lathe('Faceted sundae foot',[(0,0),(.045,0),(.048,.005),(.038,.012),(.012,.018),(.009,.067)],'glass',12,(0,0,.012)),'glass')
 paint(lathe('Thick fluted sundae bowl',[(.009,.064),(.027,.073),(.051,.102),(.066,.145),(.067,.151),(.059,.153),(.054,.141),(.045,.112),(.025,.093),(0,.090)],'glass',12,(0,0,.012)),'glass')
 torus('Rolled glass lip',(0,0,.163),.062,.004,'ice',12,4)
 # Opaque frosted-glass atlas is the established pack convention; broad flutes catch warm light.
 for i in range(8):
  a=2*PI*i/8;rod('Glass flute',(.027*math.cos(a),.027*math.sin(a),.091),(.059*math.cos(a),.059*math.sin(a),.155),.0022,'ice',4)
 for name,at,size,col in [('Vanilla',(-.028,-.014,.170),(.085,.080,.077),'F5DBA0'),('Strawberry',(.028,.006,.177),(.082,.083,.077),'DD7580'),('Chocolate',(-.008,.026,.204),(.080,.077,.077),'78412F')]:
  paint(ell(name+' scoop',at,size,'white',2),'white',col)
 # Cream rosette, bright cherry, leaf and an angled wafer give a clean service silhouette.
 for z,r in [(.233,.023),(.249,.016),(.260,.009)]:ell('Whipped cream rosette',(-.011,.015,z),(r*2,r*2,r*1.15),'crumb')
 paint(ell('Glazed red cherry',(-.008,.013,.274),(.026,.026,.025),'white',2),'white','BE3843')
 rod('Cherry stem',(-.008,.013,.282),(.001,.017,.300),.0016,'darkwood',5)
 ell('Mint leaf',(.014,.017,.279),(.028,.014,.006),'leaf',rot=.35)
 wafer=box('Biscuit wafer',(.043,.030,.224),(.021,.011,.119),'bread',.002);wafer.rotation_euler.y=.24
 for j in range(4):
  a=box('Wafer toasted stripe',(.043+.24*(j*.020-.030),.023,.194+j*.020),(.021,.0015,.003),'crust',0);a.rotation_euler.y=.24
 rod('Dessert spoon handle',(.052,-.064,.027),(.090,-.011,.030),.003,'steel',6)
 ell('Dessert spoon bowl',(.092,-.006,.030),(.019,.027,.005),'steel',2)

def pudding():
 b.plate(radius=.13,n=16)
 paint(ell('Toffee sauce pool',(-.016,0,.014),(.187,.151,.009),'white',2),'white','A55E27')
 paint(lathe('Dark date sponge',[(0,0),(.058,0),(.066,.012),(.058,.073),(.049,.080),(0,.080)],'white',12,(-.026,0,.017)),'white','74402A')
 # Irregular continuous sauce skirt, closed at the top and underside.
 n=12;v=[]
 for ring in range(3):
  for i in range(n):
   a=2*PI*i/n;r=[.050,.060,.061][ring];z=[.102,.091,.075-(.016 if i%4==0 else .007 if i%3==0 else 0)][ring];v.append((-.026+r*math.cos(a),r*math.sin(a),z))
 faces=[tuple(range(n-1,-1,-1)),tuple(range(2*n,3*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(2) for i in range(n)]
 paint(mesh('Glossy toffee drape',v,faces,'white'),'white','B97432')
 for x,y,z in [(-.052,-.029,.100),(-.007,.028,.101),(-.032,.011,.104)]:paint(ell('Toffee nut piece',(x,y,z),(.011,.008,.007),'white'),'white','DCA15B')
 ell('Cream quenelle',(.064,-.019,.039),(.069,.044,.043),'crumb',2,rot=-.4)
 for x,y,z,r in [(.057,-.012,.056,.018),(.067,-.015,.067,.012),(.071,-.014,.076,.007)]:ell('Cream fold',(x,y,z),(r*2,r*1.5,r),'crumb')
 for x,y,rot in [(.064,.043,.3),(.046,.050,-.4)]:ell('Fresh mint',(x,y,.027),(.030,.014,.007),'leaf',rot=rot)
 rod('Pudding spoon handle',(-.070,-.079,.028),(.020,-.095,.029),.003,'steel',6)
 ell('Pudding spoon bowl',(-.079,-.077,.030),(.029,.019,.006),'steel',2,rot=-.2)

def warming_lamp():
 box('Weighted enamel foot',(0,0,.020),(.29,.23,.040),'teal',.014)
 box('Brass foot trim',(0,0,.040),(.265,.205,.008),'gold',.005)
 cyl('Stand mounting collar',(-.087,.035,.059),.028,.034,'gold',12)
 rod('Upright brass stem',(-.087,.035,.071),(-.087,.035,.500),.012,'gold',10)
 for a,z in [(0,.500),(1,.554)]:ell('Stand elbow',(-.087+a*.025,.035,z),(.032,.032,.032),'gold',2)
 rod('Curved stand rise',(-.087,.035,.500),(-.062,.035,.554),.012,'gold',10)
 rod('Overhead brass arm',(-.062,.035,.554),(.043,.035,.582),.012,'gold',10)
 cyl('Shade collar',(.043,.035,.578),.020,.032,'gold',12)
 shade_first=len(b.PARTS)
 lathe('Teal heat-lamp shade',[(.024,.576),(.052,.561),(.100,.491),(.107,.474),(.099,.470),(.091,.488),(.047,.549),(.023,.565),(.024,.576)],'teal',16,(.043,.035,0))
 lathe('Cream inner reflector',[(.094,.477),(.085,.493),(.043,.551),(.022,.561)],'cream',16,(.043,.035,0))
 torus('Brass shade rim',(.043,.035,.474),.103,.0045,'gold',16,4)
 cyl('Bulb ceramic socket',(.043,.035,.536),.016,.040,'cream',10)
 # Keep Bulb as its own mesh; its shader emission comes solely from atlas Surface.B.
 first=len(b.PARTS)
 paint(ell('Bulb',(.043,.035,.480),(.058,.058,.078),'yellow',2),'yellow','F86428')
 # Articulated shade points down toward the pass and presents its reflector at service pitch.
 anchor=Vector((.043,.035,.578));q=Matrix.Rotation(math.radians(-55),3,'X')
 bpy.context.view_layer.update()
 for part in b.PARTS[shade_first:]:
  mat=part.matrix_world.copy();inv=mat.inverted()
  for v in part.data.vertices:v.co=inv@(q@(mat@v.co-anchor)+anchor)
 bulb_parts=b.PARTS[first:];b.PARTS=b.PARTS[:first]
 return bulb_parts

def service_bell():
 lathe('Dark enamel bell plinth',[(0,0),(.083,0),(.092,.006),(.092,.017),(.083,.025),(0,.025)],'teal',16)
 paint(lathe('Brass base moulding',[(.079,.022),(.087,.023),(.086,.029),(.077,.033)],'gold',16),'gold','DDAA3C')
 paint(lathe('Faceted brass bell dome',[(0,.031),(.079,.031),(.076,.045),(.066,.077),(.049,.098),(.023,.109),(0,.111)],'gold',16),'gold','E6B647')
 torus('Bell lower rolled lip',(0,0,.034),.077,.003,'gold',16,4)
 cyl('Push-button post',(0,0,.118),.007,.019,'steel',8)
 paint(cyl('Brass push button',(0,0,.131),.022,.011,'gold',12),'gold','EFC665')
 cyl('Cream button insert',(0,0,.138),.015,.003,'crumb',12)
 # A small dark opening beneath the dome separates bell from base at service distance.
 torus('Bell shadow reveal',(0,0,.029),.077,.0022,'ink',16,4)

def bunting():
 sag=lambda x:-.34*math.sin(PI*x/8)
 for i in range(32):
  x=i*.25;rod('Festival rope',(x,0,sag(x)),(x+.25,0,sag(x+.25)),.012,'crumb',6)
 palette=['D45F48','E5B74D','258C89','F1DDAA']
 for i in range(18):
  x=.40+i*(7.20/17);xl=x-.16;xr=x+.16;tip=x+.022*math.sin(i*1.7);y=.018*math.sin(i*.8)
  front=[(xl,-.004,sag(xl)-.007),(x,-.020,sag(x)-.008),(xr,-.004,sag(xr)-.007),(tip,y,sag(x)-.435)]
  v=front+[(a,bb+.008,cc) for a,bb,cc in front]
  f=[(0,1,3),(1,2,3),(7,5,4),(7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
  paint(mesh('Triangle flag %02d'%(i+1),v,f,'white'),'white',palette[i%4])
  # Cream sewn top binding connects each pennant visibly to the rope.
  rod('Pennant binding',(xl,0,sag(xl)-.007),(xr,0,sag(xr)-.007),.007,'crumb',4)
 for x in [.018,7.982]:torus('Brass end eye',(x,0,0),.023,.004,'gold',8,4,rotate=Matrix.Rotation(PI/2,3,'Y'))
 # Attachment plane is x=0; clamp end-cap bevels so measured width stays exactly8m.
 bpy.context.view_layer.update()
 for part in b.PARTS:
  mat=part.matrix_world.copy();inv=mat.inverted()
  for v in part.data.vertices:
   w=mat@v.co;w.x=max(0,min(8,w.x));v.co=inv@w

def plate_rack():
 for x in [-.095,.095]:box('Rubber rack foot',(x,0,.006),(.050,.205,.012),'navy',.003)
 box('Honey timber carry base',(0,0,.023),(.280,.250,.022),'wood',.006)
 box('Teal base inset',(0,0,.037),(.253,.227,.008),'teal',.003)
 for z in [.045,.119,.193]:
  b.plate(at=(0,-.006,z),radius=.106,n=16)
  for x in [-.119,.119]:rod('Brass plate support',(x,-.092,z+.002),(x,.075,z+.002),.006,'gold',6)
 for x in [-.125,.125]:
  for y in [-.070,.075]:rod('Open enamel rack upright',(x,y,.042),(x,y,.240),.008,'teal',6)
  rod('Handle rise',(x,.075,.225),(x,.075,.307),.008,'gold',6)
  ell('Handle elbow',(x,.075,.307),(.020,.020,.020),'gold')
 rod('Carry handle',(-.125,.075,.307),(.125,.075,.307),.010,'gold',8)
 rod('Navy hand grip',(-.085,.075,.307),(.085,.075,.307),.014,'navy',8)
 for x in [-.125,.125]:
  for z in [.045,.119,.193]:ell('Brass rack rivet',(x,-.079,z),(.014,.008,.014),'gold')

def export_asset(ob,path,children):
 b.export(ob,path)
 if children:
  from io_scene_fbx import export_fbx_bin
  from bpy_extras.io_utils import axis_conversion
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
  for ch in children:ch.select_set(True)
  bpy.context.view_layer.objects.active=ob
  export_fbx_bin.save(b.OP,bpy.context,filepath=str(path),use_selection=True,object_types={'MESH'},global_matrix=axis_conversion(to_forward='-Z',to_up='Y').to_4x4(),axis_up='Y',axis_forward='-Z',bake_space_transform=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,use_triangles=True,use_tspace=False,mesh_smooth_type='FACE',path_mode='STRIP',use_custom_props=True)

def material():
 m=c.room_material();c.atlas_emission(m);return m

def render_table(ob,rec):
 # Reuse the accepted actual-room review setup and ray-measured upper cloth.
 actual=rec['name'];rec['name']='props3-'+actual
 import props3_scene
 key=actual.removeprefix('Restaurant_');props3_scene.scene_setup(ob,rec,'TipCoins_S' if key.startswith('TipCoins') else key)
 rec['review_lighting']='Stage1V4 practicals unchanged; review room fill300W; exposure-1.5EV; canonical atlas response'
 rec['name']=actual

def save_manifest(rec):
 for key in ['file','source']:
  if key in rec:rec[key]=rec[key].replace('\\','/')
 if 'renders' in rec:rec['renders']=[f.replace('\\','/') for f in rec['renders']]
 p=O/'props3-manifest.json';rows=json.loads(p.read_text()) if p.exists() else []
 p.write_text(json.dumps([x for x in rows if x['name']!=rec['name']]+[rec],indent=2)+'\n')

def main():
 key=sys.argv[sys.argv.index('--')+1];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;b.PARTS=[];b.MAT=material()
 child_parts=[]
 if key.startswith('TipCoins'):tip_coins(key.endswith('_L'))
 elif key=='Dish_IceCream':ice_cream()
 elif key=='Dish_Pudding':pudding()
 elif key=='WarmingLamp':child_parts=warming_lamp()
 elif key=='ServiceBell':service_bell()
 elif key=='Bunting':bunting()
 elif key=='PlateRack':plate_rack()
 else:raise ValueError(key)
 name='Restaurant_'+key;ob,rec=finish(name,centre=key!='Bunting');children=[]
 if child_parts:
  ch,cr=finish('Bulb',child_parts,centre=False)
  for v in ch.data.vertices:v.co-=Vector(rec['origin_offset_authored'])
  ch.parent=ob;children.append(ch);rec['tris']+=cr['tris'];rec['children']=['Bulb'];rec['bulb_emission']='Canonical yellow-cell Surface.B times2.8; red-orange vertex tint; no new material'
 rec['triangle_limit_exclusive']=1500 if key.startswith('Dish_') else 3000
 assert rec['tris']<rec['triangle_limit_exclusive']
 folder='dishes' if key.startswith('Dish_') else 'gadgets' if key in ['WarmingLamp','ServiceBell','Bunting','PlateRack'] else 'service';path=b.PACK/folder/(name+'.fbx');path.parent.mkdir(exist_ok=True)
 if folder=='gadgets' and not path.parent.with_suffix('.meta').exists():path.parent.with_suffix('.meta').write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
 export_asset(ob,path,children)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'blends'/('props3-'+name+'.blend')),check_existing=False)
 rec.update(file=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),render_review='PENDING',material='RestaurantAtlas',source=str((O/'blends'/('props3-'+name+'.blend')).relative_to(R)))
 save_manifest(rec)
 if '--build-only' not in sys.argv:render_table(ob,rec);save_manifest(rec)
 print('PROPS3_RENDERED',name,rec['tris'],rec['size_xyz_unity_m'],flush=True)
if __name__=='__main__':main()

"""PACK-DECOR-3 source assemblies. Run standalone Blender; all units metres."""
import bpy,bmesh,sys,math,json,hashlib,shutil,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;P=O.parent;R=P.parents[3]
spec=importlib.util.spec_from_file_location('accepted_decor',P/'decor/build.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
d.O=O;d.base.O=O
part,box,rod,uv=d.part,d.box,d.rod,d.uv
reset,bounds=d.reset,d.bounds
NAMES='ShipWheel PortholeMirror LifeRing WindowFlowerBox WelcomeMat HangingHerbs BarBottleShelf ReedVase'.split()
WALL=set(NAMES)-{'WelcomeMat','ReedVase'}
NOTES={
'ShipWheel':'KayKit pictureframe_small_A mounting plaque, with authored eight-spoke timber wheel, brass collar and grips.',
'PortholeMirror':'Kenney food plate turned upright and atlas-recoloured as mirror, with authored brass rim, hinge, dogs and bolts. Opaque blue-steel face; runtime reflection is importer-owned.',
'LifeRing':'KayKit shelf_A_small fastening blocks, with authored navy/cream ring sectors, rope and lashings.',
'WindowFlowerBox':'KayKit crate planter + Kenney pottedPlant leaf-only crowns, with authored cream/rose/amber flowers and wall brackets.',
'WelcomeMat':'Kenney rugDoormat + navy border, cream inner stripe and coarse woven ribs; no baked lettering.',
'HangingHerbs':'KayKit shelf_A_small brackets + Kenney pottedPlant leaf-only hanging bunches and KayKit onion bulbs, with authored ties, garlic braid and dried chilli silhouettes.',
'BarBottleShelf':'KayKit shelf_A_small + Kenney bottle-oil, bottle-ketchup and glass, with shelf brackets and small cream bottle labels.',
'ReedVase':'KayKit jar_D_large + Kenney pottedPlant dried leaf-only reeds, with authored splayed reeds and pampas heads; ceramic teal/cream.'}

def orb(name,pos,size,cell):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=1,location=pos);o=bpy.context.object;o.name=name;o.scale=size;uv(o,cell);return o

def ring(name,centre,radius,tube,cell,sectors=None):
 # Ring in X/Z plane, cylindrical axis Y. Sector colours are baked to accepted atlas UVs.
 verts=[];faces=[];N=64;T=8
 for i in range(N):
  a=i*2*math.pi/N
  for j in range(T):
   b=j*2*math.pi/T;rr=radius+tube*math.cos(b)
   verts.append((centre[0]+rr*math.sin(a),centre[1]+tube*math.sin(b),centre[2]+rr*math.cos(a)))
 for i in range(N):
  for j in range(T):faces.append((i*T+j,((i+1)%N)*T+j,((i+1)%N)*T+(j+1)%T,i*T+(j+1)%T))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);uv(o,cell)
 if sectors:
  layer=o.data.uv_layers.active
  for f in me.polygons:
   c=sectors[(f.index//T)//(N//len(sectors))]
   for j in f.loop_indices:layer.data[j].uv=((c%8+.5)/8,1-(c//8+.5)/4)
 return o

def recolour(obs,cell):
 for o in obs:uv(o,cell)
 return obs


def foliage(model,size,pos,cell):
 # Derived assembly subset: retain only original plant material faces, omit wooden pots.
 obs=d.base.component(model,(1,1,1),pack='kenney:furniture',rot=0)
 for ob in obs:
  bm=bmesh.new();bm.from_mesh(ob.data)
  remove=[f for f in bm.faces if 'plant' not in ob.data.materials[f.material_index].name.lower()]
  bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(ob.data);bm.free()
 lo,hi=bounds(obs);centre=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 for ob in obs:
  for v in ob.data.vertices:v.co=Vector([(v.co[k]-centre[k])*size[k]/max(1e-7,hi[k]-lo[k])+pos[k] for k in range(3)])
  uv(ob,cell)
 d.base.PARTS[-1].update(size_blender=list(size),bottom_centre_blender=list(pos),geometry_subset='plant material faces only; wooden pot omitted')
 return obs

def assembly(n):
 reset();d.base.PARTS=[]
 if n=='ShipWheel':
  part('pictureframe_small_A',(.25,.055,.25),(0,.0275,-.125))
  ring('Rounded timber wheel',(0,.105,0),.285,.027,0)
  ring('Brass inner rim',(0,.108,0),.254,.009,20)
  rod('Brass axle',(0,.04,0),(0,.15,0),.065,20,24)
  rod('Timber hub',(0,.15,0),(0,.175,0),.043,0,16)
  for i in range(8):
   a=i*math.pi/4;v=Vector((math.sin(a),0,math.cos(a)))
   rod('Turned timber spoke',Vector((0,.108,0))+v*.052,Vector((0,.108,0))+v*.37,.016,0,10)
   rod('Brass grip collar',Vector((0,.108,0))+v*.306,Vector((0,.108,0))+v*.322,.024,20,10)
   orb('Rounded wood grip',Vector((0,.108,0))+v*.355,(.027,.027,.027),0)
 elif n=='PortholeMirror':
  obs=part('plate',(.48,.48,.018),pack='kenney:food')
  for o in obs:o.data.transform(Matrix.Rotation(math.pi/2,4,'X'))
  recolour(obs,6)
  ring('Broad brass porthole',(0,.035,0),.246,.039,20)
  ring('Navy rubber gasket',(0,.067,0),.213,.008,8)
  for i in range(8):
   a=i*math.pi/4;x,z=.245*math.sin(a),.245*math.cos(a)
   rod('Porthole bolt',(x,.067,z),(x,.081,z),.011,0,8)
  box('Hinge left',(-.272,.023,0),(.055,.06,.10),20)
  box('Fastening dog right',(.27,.044,0),(.055,.04,.065),20)
  # Matte facet gleams, deliberately not a fake reflected image.
  rod('Soft mirror highlight',(-.11,.073,.10),(-.035,.073,.155),.004,5,6)
 elif n=='LifeRing':
  part('shelf_A_small',(.07,.035,.09),(-.23,.0175,.16))
  part('shelf_A_small',(.07,.035,.09),(.23,.0175,.16))
  ring('Cream life ring with four navy bands',(0,.080,0),.225,.061,5,[8,5,5,5,8,5,5,5,8,5,5,5,8,5,5,5])
  ring('Outer rope',(0,.087,0),.312,.009,0)
  for i in range(4):
   a=i*math.pi/2
   for t in [-.012,.012]:
    x,z=math.sin(a),math.cos(a);rod('Rope lashing',(x*.27+z*t,.13,z*.27-x*t),(x*.325+z*t,.10,z*.325-x*t),.006,0,6)
 elif n=='WindowFlowerBox':
  part('crate',(.94,.24,.24),(0,.15,-.17),pack='restaurant')
  box('Navy planter front',(0,.276,-.045),(.90,.024,.18),8)
  box('Honey planter top lip',(0,.292,.064),(.97,.035,.034),0)
  for x in [-.35,.35]:box('Wall bracket',(x,.055,-.11),(.055,.11,.20),20)
  for i,x in enumerate([-.36,-.18,0,.18,.36]):
   obs=foliage('pottedPlant',(.23,.18,.22),(x,.15,.055),22 if i%2 else 23)
   z=.28+.025*(i%2);y=.19
   rod('Flower stalk',(x,y,.09),(x,y,z),.005,23,6)
   for j in range(5):
    a=j*math.pi*2/5;orb('Broad flower petal',(x+.032*math.cos(a),y+.012*math.sin(a),z+.025*math.sin(a)),(.032,.018,.026),[5,21,20,5,21][i])
   orb('Flower gold centre',(x,y+.02,z),(.019,.014,.019),20)
 elif n=='WelcomeMat':
  recolour(part('rugDoormat',(1,.60,.015),pack='kenney:furniture'),0)
  box('Navy mat border',(0,0,.014),(1,.60,.012),8)
  box('Cream mat inset',(0,0,.021),(.924,.524,.008),5)
  box('Woven honey field',(0,0,.027),(.875,.475,.007),0)
  for i in range(25):box('Coarse woven rib',(-.414+i*.0345,0,.031),(.009,.45,.003),3)
  # Two small navy corner diamonds keep the broad central weave calm.
  for x in [-.37,.37]:
   q=box('Navy lozenge',(x,0,.035),(.052,.052,.004),8);q.rotation_euler.z=math.pi/4
 elif n=='HangingHerbs':
  part('shelf_A_small',(.065,.08,.09),(-.40,.04,.165))
  part('shelf_A_small',(.065,.08,.09),(.40,.04,.165))
  rod('Brass herb rail',(-.43,.10,.21),(.43,.10,.21),.014,20,12)
  for idx,x in enumerate([-.31,-.10,.12]):
   obs=foliage('pottedPlant',(.19,.14,.30),(0,0,0),10 if idx%2 else 23)
   for o in obs:
    for v in o.data.vertices:v.co=Vector((v.co.x+x,v.co.y+.13,.12-v.co.z))
   recolour(obs,23 if idx%2 else 22)
   rod('Twine stem tie',(x,.13,.10),(x,.10,.21),.009,0,6)
   ring('Herb tie',(x,.13,.075),.025,.005,0)
  # Bulbs retain original onion geometry, recoloured ivory as garlic.
  for j in range(5):
   x=.32+(.025 if j%2 else -.025);z=.11-j*.052
   recolour(part('food_ingredient_onion',(.065,.060,.065),(x,.13,z-.065),pack='restaurant'),5)
   rod('Garlic braid',(x,.13,z),( .32,.10,.21),.004,0,6)
  for j in range(3):
   x=-.02+j*.04
   rod('Chilli hanging tie',(x,.10,.21),(x,.205,-.075),.0035,0,6)
   orb('Dried chilli body',(x,.205,-.12),(.012,.012,.052),21)
   rod('Chilli tapered tip',(x,.205,-.16),(x+.018,.20,-.20),.005,21,6)
 elif n=='BarBottleShelf':
  part('shelf_A_small',(.98,.23,.23),(0,.115,-.15))
  box('Navy backboard',(0,.02,.14),(.96,.035,.45),8)
  for j,x in enumerate([-.35,-.19,-.03,.13]):
   model='bottle-oil' if j%2==0 else 'bottle-ketchup';obs=part(model,(.10,.10,.26 if j%2==0 else .21),(x,.13,.081),pack='kenney:food')
   recolour(obs,10 if j%2==0 else 21)
   rod('Bottle cork',(x,.13,.341 if j%2==0 else .291),(x,.13,.358 if j%2==0 else .308),.018,0,8)
   box('Cream bottle label',(x,.183,.186),(.061,.003,.053),5)
  for x in [.29,.41]:
   recolour(part('glass',(.082,.082,.13),(x,.13,.081),pack='kenney:food'),6)
  rod('Brass retaining rail',(-.46,.232,.13),(.46,.232,.13),.009,20,10)
 elif n=='ReedVase':
  recolour(part('jar_D_large',(.34,.34,.52),pack='restaurant'),10)
  ring_ob=ring('Ceramic cream collar',(0,0,0),.10,.013,5)
  # Collar ring is horizontal, just under the jar mouth.
  ring_ob.rotation_euler.x=math.pi/2;ring_ob.location.z=.43
  foliage('pottedPlant',(.24,.22,.30),(0,0,.43),0)
  for j in range(9):
   a=j*2.399;x=.17*math.sin(a);y=.13*math.cos(a);z=1.02+.17*math.sin(j*1.7)
   rod('Dried reed stem',(.04*math.sin(a),.04*math.cos(a),.42),(x,y,z-.12),.004,0,6)
   o=orb('Pampas seed head',(x,y,z-.015),(.025,.022,.15),5 if j%3 else 20);o.rotation_euler=(Vector((x,y,.6))).to_track_quat('Z','Y').to_euler()
 else:raise ValueError(n)
 meshes=[o for o in bpy.data.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 lo,hi=bounds([o]);shift=Vector(((lo.x+hi.x)/2,lo.y if n in WALL else (lo.y+hi.y)/2,(lo.z+hi.z)/2 if n in WALL else lo.z))
 for v in o.data.vertices:v.co-=shift
 o.name='Restaurant_'+n;o.data.name=o.name+'_Mesh'
 for m in o.data.materials:
  if m and m.use_nodes:
   for node in m.node_tree.nodes:
    if node.type=='TEX_IMAGE' and node.image:
     p=O/Path(node.image.filepath).name
     if p.exists():node.image=bpy.data.images.load(str(p),check_existing=True);node.image.pack()
 lo,hi=bounds([o]);rec=dict(name=o.name,stem=n,mount='wall' if n in WALL else 'floor',mount_height_m=1.6 if n in WALL else 0,footprint_tiles=[1,1],front_fbx='-Z' if n in WALL else 'floor prop',bounds_blender=[list(lo),list(hi)],size_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],components=d.base.PARTS,notes=NOTES[n],triangles=sum(len(p.vertices)-2 for p in o.data.polygons))
 return o,rec

def build(a,b):
 records=json.loads((O/'manifest.json').read_text())['items'] if (O/'manifest.json').exists() else []
 for n in NAMES[a:b]:
  o,rec=assembly(n);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.export_scene.fbx(filepath=str(O/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,bake_anim=False,path_mode='COPY',embed_textures=True,colors_type='LINEAR')
  bpy.ops.wm.save_as_mainfile(filepath=str(O/(o.name+'.blend')))
  rec['fbx_sha256']=hashlib.sha256((O/(o.name+'.fbx')).read_bytes()).hexdigest();records=[r for r in records if r['stem']!=n]+[rec];records.sort(key=lambda r:NAMES.index(r['stem']))
  (O/'manifest.json').write_text(json.dumps(dict(units='m',wall_pivot='rear contact plane, height centre; mount at1.6m',coordinate_contract='Blender [x,y,z] -> FBX [x,z,-y]; front +Y -> -Z',items=records),indent=2));print('BUILT',n,rec['size_unity_m'],flush=True)
if __name__=='__main__':
 for p in P.glob('*.png'):shutil.copy2(p,O/p.name)
 a,b=map(int,sys.argv[-1].split(':'));build(a,b)

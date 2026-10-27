"""PACK-DECOR-1: additive CC0 pack assemblies, metre/Y-up baked FBX exports."""
import bpy,sys,math,json,hashlib,shutil
sys.dont_write_bytecode=True  # Keep imported source helper caches read-only.
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent; P=O.parent; R=P.parents[3]
sys.path.insert(0,str(P));import build as base
base.O=O
from inspect_pack import reset,load,bounds
NAMES='PlantPot2 WallShelf FramedPicture MenuBoard WallClock Rug Bunting StringLights WineRack CoatStand Bookshelf Barrel'.split()
WALL={'WallShelf','FramedPicture','WallClock','Bunting','StringLights'}
COLORS={0:'#BD915E',3:'#C29A6A',5:'#D6D0C0',6:'#818C91',8:'#1D4A64',10:'#3B979B',18:'#13191B',20:'#DAAE7D',21:'#9B5A45',22:'#55B66A',23:'#52AA48'}
DETAILS=[]
def mat():
 m=bpy.data.materials.get('Decor_Furniture_Atlas')
 if m:return m
 m=bpy.data.materials.new('Decor_Furniture_Atlas');m.use_nodes=True
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/'furniturebits_texture-catchline.png'),check_existing=True)
 m.node_tree.links.new(tex.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color']);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.78
 return m

def uv(ob,cell):
 ob.data.materials.clear();ob.data.materials.append(mat());layer=ob.data.uv_layers.active or ob.data.uv_layers.new(name='UVMap')
 for v in layer.data:v.uv=((cell%8+.5)/8,1-(cell//8+.5)/4)
 return ob

def flat_to_atlas(obs):
 # Kenney furniture has named flat materials. Preserve palette decisions by sampling accepted atlas swatches.
 for ob in obs:
  slots=list(ob.data.materials);cells=[]
  for m in slots:
   bs=m.node_tree.nodes.get('Principled BSDF') if m and m.use_nodes else None
   rgb=bs.inputs['Base Color'].default_value[:3] if bs else (0.4,0.3,0.2)
   rgb=[12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055 for v in rgb]
   def distance(c):return sum((rgb[j]-int(COLORS[c][1+2*j:3+2*j],16)/255)**2 for j in range(3))
   cells.append(min(COLORS,key=distance))
  layer=ob.data.uv_layers.active or ob.data.uv_layers.new(name='UVMap')
  for face in ob.data.polygons:
   cell=cells[min(face.material_index,len(cells)-1)] if cells else 0
   for i in face.loop_indices:layer.data[i].uv=((cell%8+.5)/8,1-(cell//8+.5)/4)
   face.material_index=0
  ob.data.materials.clear();ob.data.materials.append(mat())

def part(model,size,pos=(0,0,0),pack='furniture',rot=0):
 obs=base.component(model,size,pos,pack,rot)
 if pack=='kenney:furniture':flat_to_atlas(obs)
 return obs

def box(name,pos,size,cell=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.scale=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bevel=o.modifiers.new('Broad edge highlights','BEVEL');bevel.width=min(.012,min(size)*.19);bevel.segments=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
 uv(o,cell);return o

def rod(name,a,b,r=.01,cell=0,verts=10):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=(b-a).length,location=(a+b)*.5)
 o=bpy.context.object;o.name=name;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();uv(o,cell);return o

def polygon(name,pts,cell,thick=.003):
 me=bpy.data.meshes.new(name);me.from_pydata(pts,[],[list(range(len(pts)))]);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);uv(o,cell)
 s=o.modifiers.new('Solid graphic','SOLIDIFY');s.thickness=thick;bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=s.name)
 return o

def text_mesh(text,pos,size=.065):
 bpy.ops.object.text_add(location=pos,rotation=(math.pi/2,0,math.pi))
 o=bpy.context.object;o.data.body=text;o.data.size=size;o.data.align_x='CENTER';o.data.extrude=.0008
 bpy.ops.object.convert(target='MESH');uv(bpy.context.object,5)

def assembly(n):
 global DETAILS
 reset();base.PARTS=[];DETAILS=[]
 if n=='PlantPot2':
  part('pottedPlant',(.47,.47,1.15),pack='kenney:furniture')
  # Existing PlantPot1 is .72m; this taller variety gains a second leafy crown.
  part('plantSmall3',(.28,.27,.35),(.14,.02,.46),pack='kenney:furniture')
 elif n=='WallShelf':
  part('shelf_A_small',(.86,.23,.22),(0,.115,-.11))
  # Jars sit on the shelf, with lids below the next notional shelf.
  for i,(kind,h) in enumerate([('jar_A_small',.15),('jar_B_medium',.20),('jar_C_small',.17)]):part(kind,(.12,.12,h),(-.26+i*.25,.12,.03),pack='restaurant')
 elif n=='FramedPicture':
  part('pictureframe_medium',(.70,.07,.48),(0,.035,-.24))
  box('Painted navy harbour',(0,.078,0),(.57,.008,.35),8)
  box('Teal water',(0,.086,-.09),(.55,.005,.13),10)
  polygon('Ivory sail',[(-.12,.093,-.04),(.04,.093,-.04),(.04,.093,.13)],5)
  polygon('Honey hull',[(-.16,.096,-.055),(.13,.096,-.055),(.08,.096,-.105),(-.11,.096,-.105)],0)
  for x in [-.23,.19,.24]:box('Quayside houses',(x,.09,-.005),(.045,.01,.065),20)
  rod('Boat mast',(.047,.099,-.056),(.047,.099,.15),.005,0)
 elif n=='MenuBoard':
  part('menu',(.49,.30,.86),pack='restaurant')
  # Standing board front +Y; menu uses large chalk marks at game distance.
  box('Chalk slate',(0,.162,.49),(.36,.013,.52),8)
  text_mesh('MENU',(0,.174,.63),.065)
  for z,w in [(.56,.23),(.49,.25),(.42,.20),(.35,.24)]:box('Chalk daily specials',(0,.177,z),(w,.004,.009),5)
 elif n=='WallClock':
  # Pack frame gives the same timber profile; face/ticks are declared simple additions.
  part('pictureframe_small_A',(.40,.065,.40),(0,.0325,-.20))
  rod('Cream clock face',(0,.067,0),(0,.081,0),.157,5,32)
  for k in range(12):
   a=k*math.pi/6;x,z=.132*math.sin(a),.132*math.cos(a)
   rod('Clock tick',(x*.88,.084,z*.88),(x,.084,z),.0038,8,6)
  rod('Hour hand',(0,.088,0),(-.065,.088,.065),.007,8)
  rod('Minute hand',(0,.089,0),(.085,.089,.045),.005,8)
  rod('Brass pin',(0,.089,0),(0,.097,0),.014,0)
 elif n=='Rug':
  part('rug_rectangle_stripes_A',(2,1,.014))
 elif n=='Bunting':
  # Pack book covers supply the atlas family; pennant/cord silhouettes explicitly authored.
  part('book_single',(.055,.025,.07),(-.43,.035,.02))
  for i in range(12):
   x=-.46+i*.92/12;x2=-.46+(i+1)*.92/12
   rod('Cotton cord',(x,.035,.04-.10*(1-(x/.46)**2)),(x2,.035,.04-.10*(1-(x2/.46)**2)),.006,0,6)
  for i in range(5):
   x=-.35+i*.175;z=.04-.10*(1-(x/.46)**2)
   polygon('Cloth pennant',[(x-.066,.039,z),(x+.066,.039,z),(x,.039,z-.15)],[8,5,10,5,8][i],.006)
 elif n=='StringLights':
  part('shelf_A_small',(.055,.05,.09),(-.44,.025,0))
  part('shelf_A_small',(.055,.05,.09),(.44,.025,0))
  for i in range(16):
   a=-.44+i*.88/16;b=-.44+(i+1)*.88/16
   rod('Dark light cord',(a,.05,.025-.12*(1-(a/.44)**2)),(b,.05,.025-.12*(1-(b/.44)**2)),.006,8,6)
  for x in [-.35,-.175,0,.175,.35]:
   z=.025-.12*(1-(x/.44)**2)
   rod('Bulb socket',(x,.05,z),(x,.05,z-.04),.018,0)
   bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=.032,location=(x,.05,z-.067));uv(bpy.context.object,5)
 elif n=='WineRack':
  part('bookcaseOpenLow',(.62,.30,.56),pack='kenney:furniture',rot=180)
  # Horizontal labelled bottles in two open cradles in an open bookcase.
  for z in [.18,.37]:
   box('Wine shelf',(0,.245,z-.08),(.56,.20,.035),0)
   for x in [-.19,0,.19]:
    obs=part('bottle-oil',(.085,.085,.24),(0,0,0),pack='kenney:food',rot=0)
    for ob in obs:
     ob.data.transform(Matrix.Rotation(-math.pi/2,4,'X'))
     for v in ob.data.vertices:v.co+=Vector((x,.13,z))
 elif n=='CoatStand':part('coatRackStanding',(.46,.46,1.65),pack='kenney:furniture')
 elif n=='Bookshelf':
  part('bookcaseOpenLow',(.86,.31,.78),pack='kenney:furniture')
  part('book_set',(.54,.20,.22),(0,.02,.45))
  part('plantSmall1',(.19,.18,.25),(.24,0,.78),pack='kenney:furniture')
 elif n=='Barrel':part('barrel',(.51,.51,.68),pack='kenney:food')
 else:raise ValueError(n)
 meshes=[o for o in bpy.data.objects if o.type=='MESH']
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 lo,hi=bounds([o])
 shift=Vector(((lo.x+hi.x)/2,lo.y if n in WALL else (lo.y+hi.y)/2,(lo.z+hi.z)/2 if n in WALL else lo.z))
 for v in o.data.vertices:v.co-=shift
 o.name='Restaurant_'+n;o.data.name=o.name+'_Mesh'
 # All materials become colocated atlas references. No free colour-only shaders.
 for m in o.data.materials:
  if m and m.use_nodes:
   for node in m.node_tree.nodes:
    if node.type=='TEX_IMAGE' and node.image:
     p=O/Path(node.image.filepath).name
     if p.exists():node.image=bpy.data.images.load(str(p),check_existing=True);node.image.pack()
 lo,hi=bounds([o]);return o,dict(name=o.name,stem=n,mount='wall' if n in WALL else 'floor',mount_height_m=1.6 if n in WALL else 0,footprint_tiles=[2,1] if n=='Rug' else [1,1],front_fbx='-Z' if n in WALL or n in {'MenuBoard','WineRack'} else '+Z' if n=='Bookshelf' else 'unspecified floor prop',bounds_blender=[list(lo),list(hi)],size_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],components=base.PARTS,triangles=sum(len(p.vertices)-2 for p in o.data.polygons))

def build(a,b):
 records=json.loads((O/'manifest.json').read_text())['items'] if (O/'manifest.json').exists() else []
 for n in NAMES[a:b]:
  o,rec=assembly(n);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.export_scene.fbx(filepath=str(O/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,bake_anim=False,path_mode='COPY',embed_textures=True,colors_type='LINEAR')
  bpy.ops.wm.save_as_mainfile(filepath=str(O/(o.name+'.blend')))
  rec['fbx_sha256']=hashlib.sha256((O/(o.name+'.fbx')).read_bytes()).hexdigest()
  records=[r for r in records if r['stem']!=n]+[rec]
  (O/'manifest.json').write_text(json.dumps(dict(units='m',wall_pivot='back contact, height centre; mount origin at1.6m',coordinate_contract='Blender [x,y,z] -> FBX [x,z,-y]; front +Y -> -Z; Unity handedness remains importer-owned',items=records),indent=2))
  print('BUILT',n,rec['size_unity_m'],flush=True)
if __name__=='__main__':
 O.mkdir(exist_ok=True)
 for p in P.glob('*.png'):shutil.copy2(p,O/p.name)
 a,b=map(int,sys.argv[-1].split(':'));build(a,b)

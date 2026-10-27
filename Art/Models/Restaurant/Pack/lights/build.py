"""PACK-DECOR-2 source fixtures. External accepted helpers are read-only."""
import sys
sys.dont_write_bytecode=True
import bpy,math,json,hashlib,shutil,importlib.util,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;P=O.parent;R=P.parents[3]
spec=importlib.util.spec_from_file_location('decor_helpers',P/'decor/build.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
d.O=O;d.base.O=O
NAMES='PendantLamp WallSconce HangingLantern StringLightsLong TableLamp Brazier'.split()
WALL={'WallSconce','HangingLantern','StringLightsLong'}
G=[]
def sphere(name,pos,size,glow=True,cell=5):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=pos);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if glow:G.append(o)
 else:d.uv(o,cell)
 return o

def gbox(name,pos,size):
 o=d.box(name,pos,size,5);G.append(o);return o

def ring(name,z,r,cell=0,at=(0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=6,location=(*at,z),major_radius=r,minor_radius=.009)
 d.uv(bpy.context.object,cell);bpy.context.object.name=name

def shade(name,bottom,top,r1,r2,cell=5):
 vs=[]
 for z,r in [(bottom,r1),(top,r2)]:vs.extend([(r*math.cos(i*math.tau/16),r*math.sin(i*math.tau/16),z) for i in range(16)])
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(i,(i+1)%16,(i+1)%16+16,i+16) for i in range(16)]);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);d.uv(ob,cell)
 mod=ob.modifiers.new('Shade thickness','SOLIDIFY');mod.thickness=.006;bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name)
 ring('Brass shade hem',bottom,r1);ring('Brass shade crown',top,r2)

def joined(obs,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.name=name;o.data.name=name+'_Mesh';return o

def assembly(n):
 global G
 d.reset();G=[];d.base.PARTS=[]
 if n=='PendantLamp':
  # Compress the original pack ceiling fitting into a small mounting canopy.
  d.part('lampSquareCeiling',(.16,.16,.055),(0,0,.75),pack='kenney:furniture',rot=0)
  d.rod('Navy pendant cable',(0,0,.38),(0,0,.76),.012,8)
  shade('Cream pendant shade',.18,.39,.21,.085)
  sphere('Pendant exposed bulb',(0,0,.015),(.10,.10,.11))
  d.rod('Brass bulb socket',(0,0,.09),(0,0,.39),.025,0)
 elif n=='WallSconce':
  d.part('shelf_A_small',(.14,.075,.20),(0,.0375,-.10))
  d.rod('Brass rising arm',(0,.07,-.055),(0,.20,-.055),.018,0)
  d.rod('Brass globe cup',(0,.20,-.055),(0,.20,.02),.038,0)
  sphere('Ivory globe',(0,.20,.10),(.105,.105,.11))
  ring('Globe collar',.005,.063,at=(0,.20))
 elif n=='HangingLantern':
  d.part('shelf_A_small',(.12,.09,.17),(0,.045,.24))
  d.rod('Lantern hook',(0,.045,.35),(0,.24,.35),.014,0)
  d.rod('Lantern hanger',(0,.24,.25),(0,.24,.35),.012,0)
  for z in [-.15,.21]:d.box('Navy lantern cornice',(0,.24,z),(.27,.25,.045),8)
  for x in [-.115,.115]:
   for y in [.135,.345]:d.rod('Brass corner',(x,y,-.13),(x,y,.19),.012,0)
  # Opaque bright panes; no glass/transparency, all panes isolated as glow geometry.
  for x in [-.108,.108]:gbox('Lit side pane',(x,.24,.025),(.006,.19,.27))
  for y in [.142,.338]:gbox('Lit front pane',(0,y,.025),(.21,.006,.27))
  for x in [-.112,.112]:d.rod('Window crossbar',(x,.14,-.10),(-x,.14,.15),.006,8,6)
  d.box('Lantern navy crown',(0,.24,.25),(.17,.17,.045),8)
 elif n=='StringLightsLong':
  for x in [-1.40,1.40]:d.part('shelf_A_small',(.075,.055,.11),(x,.0275,.02))
  def z(x):return .055-.23*(1-(x/1.4)**2)
  for i in range(32):
   a=-1.4+i*2.8/32;b=-1.4+(i+1)*2.8/32
   d.rod('Navy insulated strand',(a,.065,z(a)),(b,.065,z(b)),.008,8,6)
  for i in range(10):
   x=-1.26+i*2.52/9;v=z(x)
   d.rod('Brass bulb socket',(x,.065,v),(x,.065,v-.045),.023,0,8)
   sphere('Warm festoon bulb',(x,.065,v-.087),(.040,.040,.052))
 elif n=='TableLamp':
  obs=d.part('lampRoundTable',(.33,.33,.54),pack='kenney:furniture',rot=0)
  for o in obs:
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z>.12],context='VERTS');bm.to_mesh(o.data);bm.free();d.uv(o,0)
  shade('Ivory table shade',.34,.55,.18,.105)
  d.rod('Brass lamp stem',(0,0,.035),(0,0,.25),.018,0)
  sphere('Visible table bulb',(0,0,.18),(.078,.078,.083))
  d.rod('Brass socket',(0,0,.23),(0,0,.42),.020,0)
 elif n=='Brazier':
  obs=d.part('pot_A',(.53,.53,.24),(0,0,.38),pack='restaurant')
  for o in obs:d.uv(o,8)
  for x in [-.17,.17]:
   for y in [-.17,.17]:d.rod('Splayed brazier leg',(x*1.25,y*1.25,0),(x,y,.42),.022,8,8)
  ring('Brass fire bowl rim',.59,.235)
  for i in range(9):
   a=i*2.4;rr=.15*math.sqrt(i/9);sphere('Amber coal',(rr*math.cos(a),rr*math.sin(a),.575),(.060,.050,.034))
  for i in range(5):
   a=i*math.tau/5;sphere('Dark coal',(.16*math.cos(a),.16*math.sin(a),.575),(.048,.045,.027),False,18)
  for k in range(10):
   a=k*math.tau/10;d.rod('Heat guard',(math.cos(a)*.25,math.sin(a)*.25,.58),(math.cos(a)*.22,math.sin(a)*.22,.73),.008,8,6)
  ring('Guard rim',.73,.22,8)
 else:raise ValueError(n)
 allmesh=[o for o in bpy.data.objects if o.type=='MESH'];body=joined([o for o in allmesh if o not in G],'Restaurant_'+n);glow=joined(G,n+'_Glow')
 m=bpy.data.materials.new(n+'_Glow');m.use_nodes=True
 rgb=[int('FFE0A0'[i:i+2],16)/255 for i in (0,2,4)];lin=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
 m.diffuse_color=(*lin,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*lin,1);bs.inputs['Roughness'].default_value=.42
 glow.data.materials.clear();glow.data.materials.append(m)
 for face in glow.data.polygons:face.material_index=0
 if not glow.data.uv_layers.active:glow.data.uv_layers.new(name='UVMap')
 lo,hi=d.bounds([body,glow]);mount='wall' if n in WALL else 'ceiling' if n=='PendantLamp' else 'floor/table' if n=='TableLamp' else 'floor'
 shift=Vector(((lo.x+hi.x)/2,lo.y if n in WALL else (lo.y+hi.y)/2,(lo.z+hi.z)/2 if n in WALL else hi.z if n=='PendantLamp' else lo.z))
 for o in [body,glow]:
  for v in o.data.vertices:v.co-=shift
  for mat in o.data.materials:
   if mat and mat.use_nodes:
    for node in mat.node_tree.nodes:
     if node.type=='TEX_IMAGE' and node.image:
      p=O/Path(node.image.filepath).name
      if p.exists():node.image=bpy.data.images.load(str(p),check_existing=True);node.image.pack()
 lo,hi=d.bounds([body,glow]);return [body,glow],dict(stem=n,name=body.name,glow_mesh=glow.name,glow_material=m.name,glow_hex='#FFE0A0',glow_clusters=10 if n=='StringLightsLong' else 9 if n=='Brazier' else 4 if n=='HangingLantern' else 1,mount=mount,mount_height_m=1.6 if n in WALL else 2.5 if n=='PendantLamp' else .72 if n=='TableLamp' else 0,footprint_tiles=[3,1] if n=='StringLightsLong' else [1,1],bounds_blender=[list(lo),list(hi)],size_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],triangles=sum(len(p.vertices)-2 for o in [body,glow] for p in o.data.polygons),components=d.base.PARTS)

def build(a,b):
 records=json.loads((O/'manifest.json').read_text())['items'] if (O/'manifest.json').exists() else []
 for n in NAMES[a:b]:
  obs,r=assembly(n);bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  bpy.ops.export_scene.fbx(filepath=str(O/(r['name']+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,bake_anim=False,path_mode='COPY',embed_textures=True,colors_type='LINEAR')
  bpy.ops.wm.save_as_mainfile(filepath=str(O/(r['name']+'.blend')))
  r['fbx_sha256']=hashlib.sha256((O/(r['name']+'.fbx')).read_bytes()).hexdigest();records=[v for v in records if v['stem']!=n]+[r];records.sort(key=lambda x:NAMES.index(x['stem']))
  (O/'manifest.json').write_text(json.dumps(dict(units='m',coordinate_contract='Blender [x,y,z] -> FBX [x,z,-y]; wall front +Y -> -Z; geometry baked, roots identity',items=records),indent=2));print('BUILT',n,r['size_unity_m'],flush=True)
if __name__=='__main__':
 for p in P.glob('*.png'):shutil.copy2(p,O/p.name)
 build(*map(int,sys.argv[-1].split(':')))

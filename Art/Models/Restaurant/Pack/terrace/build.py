"""Standalone terrace assemblies. Immutable CC0 sources; accepted baked FBX contract."""
import bpy,sys,math,json,hashlib,shutil,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;P=O.parent;R=P.parents[3]
spec=importlib.util.spec_from_file_location('nautical',P/'decor2/build.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
h.O=O;h.d.O=O;h.d.base.O=O
part,box,rod,uv=h.part,h.box,h.rod,h.uv
reset,bounds=h.reset,h.bounds
NAMES='StandaloneParasol DeckChair HarbourBench RailingRopeSwag PotLadder QuayBollard'.split()
WALL={'RailingRopeSwag'}
NOTES={
'StandaloneParasol':'Kenney food plate weighted base; authored timber mast, brass runner/ribs and eight-panel cream/teal canopy. No table or chairs.',
'DeckChair':'KayKit pillow_A head cushion; authored folding timber X-frame, brass pivots, cream/teal sling and arms.',
'HarbourBench':'Kenney bench frame, warm-wood seat/back slats and brass fasteners; 1.4m wide.',
'RailingRopeSwag':'KayKit shelf_A_small mounting blocks; authored catenary-like rope with cork floats and navy/cream binding bands.',
'PotLadder':'KayKit shelf_A_small three shelf boards and jar_D_large planters; Kenney pottedPlant leaf-only crowns; authored timber A-frame, spreaders and brass fasteners.',
'QuayBollard':'Kenney food plate base, authored navy cast mooring post/crosshead with brass collars and coiled rope.'}

def beam(name,a,b,width,depth,cell=0):
 a,b=Vector(a),Vector(b);ob=box(name,(a+b)/2,(width,depth,(b-a).length),cell);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob

def horizontal_ring(name,c,r,t,cell):
 ob=h.ring(name,(0,0,0),r,t,cell);ob.data.transform(Matrix.Rotation(math.pi/2,4,'X'));ob.location=c;return ob

def rope(name,points,r=.012,cell=0):
 for a,b in zip(points,points[1:]):rod(name,a,b,r,cell,8)

def panel(name,points,cell,thickness=.008):
 return h.d.polygon(name,points,cell,thickness)

def assembly(n):
 reset();h.d.base.PARTS=[]
 if n=='StandaloneParasol':
  h.recolour(part('plate',(.39,.39,.047),pack='kenney:food'),8)
  rod('Weighted navy base',(0,0,.025),(0,0,.095),.14,8,24)
  rod('Timber parasol mast',(0,0,.07),(0,0,1.92),.024,0,12)
  rod('Brass pole shoe',(0,0,.065),(0,0,.16),.033,20,12)
  rod('Brass canopy runner',(0,0,1.48),(0,0,1.57),.037,20,12)
  for i in range(8):
   a=i*math.pi/4;b=(i+1)*math.pi/4
   pts=[(0,0,1.96),(.30*math.cos(a),.30*math.sin(a),1.84),(.49*math.cos(a),.49*math.sin(a),1.72),(.49*math.cos(b),.49*math.sin(b),1.72),(.30*math.cos(b),.30*math.sin(b),1.84)]
   panel('Cream teal canvas canopy',pts,5 if i%2==0 else 10,.012)
   rod('Timber radial rib',(0,0,1.88),(.48*math.cos(a),.48*math.sin(a),1.713),.009,0,8)
   rod('Canopy brace',(0,0,1.53),(.29*math.cos(a),.29*math.sin(a),1.82),.006,20,6)
   panel('Scalloped valance',[(.49*math.cos(a),.49*math.sin(a),1.72),(.49*math.cos(b),.49*math.sin(b),1.72),(.49*math.cos(b),.49*math.sin(b),1.665),(.49*math.cos(a),.49*math.sin(a),1.665)],5 if i%2==0 else 10,.008)
  h.orb('Brass finial',(0,0,1.977),(.026,.026,.035),20)
 elif n=='DeckChair':
  # Front is +Y in Blender. Two crossing timber legs each side, reclined back to -Y.
  for x in [-.265,.265]:
   beam('Folding outer rail',(x,-.40,.035),(x,.36,.60),.045,.048)
   beam('Folding inner rail',(x,.40,.035),(x,-.30,.66),.043,.046)
   beam('Long back upright',(x,.22,.26),(x,-.36,.92),.043,.045)
   rod('Brass folding pivot',(x-.029,0,.33),(x+.029,0,.33),.025,20,12)
   beam('Arm rest',(x,-.14,.58),(x,.28,.58),.067,.045,0)
   beam('Arm support',(x,.23,.37),(x,.23,.58),.024,.028)
  for y,z in [(.31,.48),(-.35,.90),(-.37,.08),(.37,.08)]:rod('Timber crossbar',(-.286,y,z),(.286,y,z),.022,0,10)
  # Separate broad fabric strips follow a dipped seat then reclined back.
  for j in range(7):
   x0=-.235+j*.47/7;x1=x0+.47/7
   for (y0,z0),(y1,z1) in zip([(.32,.48),(.02,.32),(-.35,.89)],[(.02,.32),(-.35,.89),(-.35,.89)]):
    if y0==y1:continue
    panel('Striped canvas sling',[(x0,y0,z0),(x1,y0,z0),(x1,y1,z1),(x0,y1,z1)],5 if j%2==0 else 10,.012)
  obs=h.recolour(part('pillow_A',(.35,.10,.12),(0,-.305,.76)),5)
  for ob in obs:ob.name='Pack head cushion'
 elif n=='HarbourBench':
  # Keep the complete CC0 bench rather than a scratch-built substitute.
  obs=part('bench',(1.40,.50,.82),pack='kenney:furniture',rot=180)
  for ob in obs:ob.name='Kenney timber bench'
  # Sparse thin slats raise broad warm timber planes above the existing seat.
  for j in range(4):box('Warm seat slat',(0,-.16+j*.105,.466),(1.35,.091,.035),0 if j%2==0 else 3)
  for z in [.62,.74]:box('Warm backrest slat',(0,-.217,z),(1.35,.035,.070),0)
  for x in [-.56,.56]:
   for z in [.62,.74]:rod('Brass slat screw',(x,-.193,z),(x,-.183,z),.008,20,8)
 elif n=='RailingRopeSwag':
  for x in [-.46,.46]:
   h.recolour(part('shelf_A_small',(.065,.035,.095),(x,.0175,.065)),8)
   h.ring('Brass fence eye',(x,.062,.10),.027,.006,20)
  # Front is +Y; all geometry remains outside the rear contact plane.
  for strand in range(2):
   pts=[]
   for k in range(33):
    x=-.46+k*.92/32;z=.10-.17*(1-(x/.46)**2)+strand*.018
    pts.append((x,.075+strand*.012,z))
   rope('Doubled harbour rope',pts,.009,0)
  for i,x in enumerate([-.32,-.16,0,.16,.32]):
   z=.10-.17*(1-(x/.46)**2)
   h.orb('Cork float',(x,.09,z),(.041,.034,.061),0)
   for zz in [z-.026,z+.026]:horizontal_ring('Float painted binding',(x,.09,zz),.035,.006,5 if i%2 else 8)
 elif n=='PotLadder':
  for x in [-.285,.285]:
   beam('A-frame front leg',(x,.28,.03),(x,0,1.17),.044,.048)
   beam('A-frame rear leg',(x,-.28,.03),(x,0,1.17),.044,.048)
   rod('Brass hinge',(x-.027,0,1.14),(x+.027,0,1.14),.021,20,12)
   beam('Ladder spreader',(x,-.19,.35),(x,.19,.35),.025,.024,8)
  # Pack shelf geometry is flattened as boards, not stretched into structural legs.
  for j,(z,depth) in enumerate([(.24,.45),(.57,.30),(.89,.19)]):
   h.recolour(part('shelf_A_small',(.61,depth,.035),(0,0,z)),0)
   x=[-.07,.055,0][j];y=[.08,.035,0][j]
   h.recolour(part('jar_D_large',(.18,.17,.16),(x,y,z+.036),pack='restaurant'),[8,10,5][j])
   h.O=O;h.d.O=O
   h.foliage('pottedPlant',(.23,.20,.14),(x,y,z+.17),22 if j%2 else 23)
 elif n=='QuayBollard':
  h.recolour(part('plate',(.40,.40,.037),pack='kenney:food'),8)
  rod('Cast bollard base',(0,0,.018),(0,0,.065),.155,8,20)
  rod('Navy mooring post',(0,0,.06),(0,0,.44),.068,8,16)
  rod('Brass shoe collar',(0,0,.065),(0,0,.098),.075,20,16)
  rod('Cast crosshead',(-.19,0,.40),(.19,0,.40),.050,8,12)
  for x in [-.19,.19]:h.orb('Rounded crosshead end',(x,0,.40),(.054,.054,.054),8)
  rod('Brass top cap',(0,0,.44),(0,0,.46),.074,20,16)
  # Three turns resting flat on quay, plus an end loop running around the post.
  for k in range(3):horizontal_ring('Coiled rope',(0,0,.048+k*.019),.215-k*.027,.010,0)
  rope('Rope end',[(-.19,.11,.07),(-.21,.18,.07),(-.14,.25,.026),(.04,.27,.012),(.17,.23,.012)],.011,0)
  horizontal_ring('Mooring loop',(0,0,.28),.085,.011,0)
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
 lo,hi=bounds([o]);rec=dict(name=o.name,stem=n,mount='wall' if n in WALL else 'floor',mount_height_m=1.05 if n in WALL else 0,footprint_tiles=[2,1] if n=='HarbourBench' else [1,1],front_fbx='-Z',bounds_blender=[list(lo),list(hi)],size_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],components=h.d.base.PARTS,notes=NOTES[n],triangles=sum(len(p.vertices)-2 for p in o.data.polygons))
 return o,rec

def build(a,b):
 records=json.loads((O/'manifest.json').read_text())['items'] if (O/'manifest.json').exists() else []
 for n in NAMES[a:b]:
  o,rec=assembly(n);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.export_scene.fbx(filepath=str(O/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,bake_anim=False,path_mode='COPY',embed_textures=True,colors_type='LINEAR')
  bpy.ops.wm.save_as_mainfile(filepath=str(O/(o.name+'.blend')))
  rec['fbx_sha256']=hashlib.sha256((O/(o.name+'.fbx')).read_bytes()).hexdigest();records=[r for r in records if r['stem']!=n]+[rec];records.sort(key=lambda r:NAMES.index(r['stem']))
  (O/'manifest.json').write_text(json.dumps(dict(units='m',wall_pivot='rear contact, height centre; mount1.05m',coordinate_contract='Blender [x,y,z] -> FBX [x,z,-y], front +Y -> -Z',items=records),indent=2));print('BUILT',n,rec['size_unity_m'],flush=True)
if __name__=='__main__':
 for p in P.glob('*.png'):shutil.copy2(p,O/p.name)
 a,b=map(int,sys.argv[-1].split(':'));build(a,b)

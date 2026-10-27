"""PACK-STRUCTURE-1 additive CC0 overhead assemblies."""
import sys
sys.dont_write_bytecode=True
import bpy,bmesh,math,json,hashlib,shutil,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;P=O.parent
s=importlib.util.spec_from_file_location('light_helpers',P/'lights/build.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
d=h.d;d.O=O;d.base.O=O

NAMES='Pergola CeilingBeam TerraceAwning HangingBasket'.split()
WALL={'TerraceAwning'}
NOTES={
'Pergola':'KayKit shelf_A_small four rafter mounting brackets; authored solid bevelled timbers, squared posts, diagonal knee braces, navy foot/collar shoes and brass bolts. Open rafter frame, no roof.',
'CeilingBeam':'Authored solid bevelled timber beam with two KayKit shelf_A_small end brackets, navy straps and brass pendant eyes.',
'TerraceAwning':'KayKit shelf_A_small pair of wall brackets; authored wood batten, navy/cream solid striped fabric with scalloped valance, brass support stays.',
'HangingBasket':'Kenney pottedPlant leaf-only crown; authored honey wicker basket with woven ribs, three brass suspension chains and top eye.'}

def timber(name,pos,size):
 # Authored solid timbers match the accepted pack wood atlas and broad bevels.
 return [d.box(name,pos,size,0)]

def torus(name,at,r,tube=.008,cell=0,rotate=None,segments=16):
 bpy.ops.mesh.primitive_torus_add(major_segments=segments,minor_segments=6 if segments==16 else 4,major_radius=r,minor_radius=tube,location=at)
 ob=bpy.context.object;ob.name=name
 if rotate:ob.rotation_euler=rotate
 d.uv(ob,cell);return ob

def assembly(n):
 d.reset();d.base.PARTS=[]
 if n=='Pergola':
  for x in [-1.36,1.36]:
   for y in [-.40,.40]:
    d.box('Warm timber post',(x,y,1.16),(.13,.13,2.32),0)
    d.box('Navy post shoe',(x,y,.07),(.15,.15,.14),8)
    d.box('Navy upper collar',(x,y,2.21),(.142,.142,.065),8)
    for xx in [x-.044,x+.044]:d.rod('Brass bolt',(xx,y-.078,.09),(xx,y-.082,.09),.009,20,8)
    # Knee braces leave 1.90m clear under the frame.
    dx=-.28 if x>0 else .28
    ob=d.box('Diagonal timber knee',(x+dx/2,y,2.11),(.065,.075,.40),3);ob.rotation_euler.y=math.copysign(math.pi/4,dx)
  for y in [-.40,.40]:timber('Long bearer',(0,y,2.34),(3,.14,.18))
  for x in [-1.36,1.36]:
   for y in [-.40,.40]:
    for ob in d.part('shelf_A_small',(.12,.12,.14),(x,y,2.20)):d.uv(ob,0)
  for x in [-1.36,-.68,0,.68,1.36]:timber('Open cross rafter',(x,0,2.48),(.11,1,.14))
 elif n=='CeilingBeam':
  timber('Exposed overhead timber',(0,0,-.09),(2,.17,.18))
  for x in [-.88,.88]:
   obs=d.part('shelf_A_small',(.11,.20,.24),(x,0,-.25))
   for o in obs:d.uv(o,8)
   d.box('Navy beam strap',(x,0,-.095),(.055,.184,.185),8)
   for yy in [-.098,.098]:d.rod('Bracket brass bolt',(x,yy,-.09),(x,yy*1.04,-.09),.013,20,10)
  for x in [-.53,.53]:torus('Pendant hanging eye',(x,-.075,-.205),.027,.007,20,(math.pi/2,0,0))
 elif n=='TerraceAwning':
  # Wall is Blender Y=0. Cloth slopes toward +Y (FBX front -Z).
  d.box('Timber wall batten',(0,.045,-.045),(1.5,.09,.09),0)
  for x in [-.64,.64]:
   obs=d.part('shelf_A_small',(.075,.11,.18),(x,.055,-.18))
   for o in obs:d.uv(o,8)
   d.rod('Brass awning stay',(x,.06,-.17),(x,.82,-.27),.012,20,8)
  for i in range(10):
   x=-.75+i*.15;cell=8 if i%2==0 else 5
   d.polygon('Striped fabric roof',[(x,.07,-.022),(x+.15,.07,-.022),(x+.15,.88,-.275),(x,.88,-.275)],cell,.008)
   pts=[(x,.88,-.275),(x+.15,.88,-.275),(x+.15,.88,-.36),(x+.12,.88,-.385),(x+.075,.88,-.40),(x+.03,.88,-.385),(x,.88,-.36)]
   d.polygon('Scalloped fabric valance',pts,cell,.008)
  d.rod('Awning front rail',(-.755,.876,-.28),(.755,.876,-.28),.014,20,10)
 elif n=='HangingBasket':
  # Pack foliage only: native wood pot faces must never become green leaves.
  obs=d.base.component('pottedPlant',(1,1,1),pack='kenney:furniture',rot=0)
  for o in obs:
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if 'plant' not in o.data.materials[f.material_index].name.lower()],context='FACES');bm.to_mesh(o.data);bm.free()
  lo,hi=d.bounds(obs);centre=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
  for o in obs:
   for vert in o.data.vertices:vert.co=Vector([(vert.co[k]-centre[k])*[.43,.43,.38][k]/max(hi[k]-lo[k],1e-7)+[0,0,-.56][k] for k in range(3)])
   d.uv(o,23)
  d.base.PARTS[-1].update(geometry_subset='plant material faces only, wooden pot omitted',size_blender=[.43,.43,.38],bottom_centre_blender=[0,0,-.56])
  bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.145,radius2=.215,depth=.20,location=(0,0,-.64));d.uv(bpy.context.object,0);bpy.context.object.name='Wicker basket body'
  for z,r in [(-.74,.145),(-.69,.163),(-.64,.18),(-.59,.198),(-.54,.215)]:torus('Wicker horizontal weave',(0,0,z),r,.006,3)
  for i in range(16):
   a=i*math.tau/16;d.rod('Wicker vertical rib',(.145*math.cos(a),.145*math.sin(a),-.74),(.215*math.cos(a),.215*math.sin(a),-.54),.006,20,6)
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.197,depth=.008,location=(0,0,-.535));d.uv(bpy.context.object,18);bpy.context.object.name='Dark basket soil'
  for k in range(3):
   a=k*math.tau/3;tangent=Vector((.20*math.cos(a),.20*math.sin(a),-.485)).normalized();side=Vector((-math.sin(a),math.cos(a),0))
   for j in range(20):
    t=(j+.5)/20;pt=(.20*t*math.cos(a),.20*t*math.sin(a),-.055-.485*t)
    normal=side if j%2==0 else tangent.cross(side)
    torus('Brass suspension chain',pt,.017,.004,20,normal.to_track_quat('Z','Y').to_euler(),segments=10)
  torus('Top hanging eye',(0,0,-.028),.020,.008,20,(math.pi/2,0,0))
 else:raise ValueError(n)
 meshes=[o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)]
 for o in list(bpy.data.objects):
  if o.type=='MESH' and not len(o.data.vertices):bpy.data.objects.remove(o,do_unlink=True)
 body=h.joined(meshes,'Restaurant_'+n);obs=[body]
 lo,hi=d.bounds(obs);mount='floor' if n=='Pergola' else 'wall' if n=='TerraceAwning' else 'ceiling'
 # Awning origin is top edge of back-contact batten; overhead pivots are top mounts.
 shift=Vector(((lo.x+hi.x)/2,lo.y if mount=='wall' else (lo.y+hi.y)/2,lo.z if mount=='floor' else hi.z))
 for v in body.data.vertices:v.co-=shift
 for mat in body.data.materials:
  for node in mat.node_tree.nodes if mat and mat.use_nodes else []:
   if node.type=='TEX_IMAGE' and node.image:
    p=O/Path(node.image.filepath).name
    if p.exists():node.image=bpy.data.images.load(str(p),check_existing=True);node.image.pack()
 lo,hi=d.bounds(obs)
 return obs,dict(stem=n,name=body.name,mount=mount,mount_height_m=0 if mount=='floor' else 2.6,footprint_tiles=[3,1] if n=='Pergola' else [2,1] if n in {'CeilingBeam','TerraceAwning'} else [1,1],size_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],bounds_blender=[list(lo),list(hi)],triangles=sum(len(p.vertices)-2 for p in body.data.polygons),components=d.base.PARTS,authored_details=NOTES[n],glow_mesh=None,glow_material=None,mount_convention='floor footprint centre, feet Y0' if mount=='floor' else 'wall contact at top of batten, front -Z; all geometry Y<=0' if mount=='wall' else 'top mount Y0, all geometry hangs below',clear_span_unity_m=[2.59,.67] if n=='Pergola' else None)

def build(a,b):
 records=json.loads((O/'manifest.json').read_text())['items'] if (O/'manifest.json').exists() else []
 for n in NAMES[a:b]:
  obs,r=assembly(n);bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  bpy.ops.export_scene.fbx(filepath=str(O/(r['name']+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,bake_anim=False,path_mode='COPY',embed_textures=True,colors_type='LINEAR')
  bpy.ops.wm.save_as_mainfile(filepath=str(O/(r['name']+'.blend')))
  r['fbx_sha256']=hashlib.sha256((O/(r['name']+'.fbx')).read_bytes()).hexdigest();records=[x for x in records if x['stem']!=n]+[r];records.sort(key=lambda x:NAMES.index(x['stem']))
  (O/'manifest.json').write_text(json.dumps(dict(units='m',coordinate_contract='Blender [x,y,z] -> FBX [x,z,-y]; wall front -Z; axis conversion baked, root identity',items=records),indent=2));print('BUILT',n,r['size_unity_m'],flush=True)
if __name__=='__main__':
 for p in P.glob('*.png'):shutil.copy2(p,O/p.name)
 build(*map(int,sys.argv[-1].split(':')))

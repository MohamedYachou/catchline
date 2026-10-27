"""PACK-KITCHEN-1 additive CC0 assemblies. Only hood owns a glow mesh."""
import sys
sys.dont_write_bytecode=True
import bpy,math,json,hashlib,shutil,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;P=O.parent
s=importlib.util.spec_from_file_location('light_helpers',P/'lights/build.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
d=h.d;d.O=O;d.base.O=O
NAMES='ExtractorHood PotRail UtensilRail SpiceShelf KnifeStrip ChoppingBlock'.split();WALL=set(NAMES[:-1])
NOTES={
'ExtractorHood':'KayKit extractorhood, steel atlas finish, navy filter grille, brass controls; separate ExtractorHood_Glow task-light strip.',
'PotRail':'Two KayKit shelf_A_small brackets, steel rail/hooks, three hanging KayKit pan_A/pan_B and one pot_A; pans turned vertically.',
'UtensilRail':'Two KayKit shelf_A_small brackets and steel rail, authored ladle, slotted turner, whisk and wood spoon.',
'SpiceShelf':'KayKit shelf_A_small plus six varied jar_A_small/jar_B_small/jar_C_small with cream labels and navy/brass/teal lids.',
'KnifeStrip':'KayKit cuttingboard as wall magnet backboard plus four KayKit knife variants, steel blades and navy handles.',
'ChoppingBlock':'KayKit cuttingboard thickened into an end-grain butcher block; wood inlays, scored top and four small rubber feet.'}

def rail(width):
 for x in [-width/2+.045,width/2-.045]:
  obs=d.part('shelf_A_small',(.07,.075,.11),(x,.0375,.12))
  for o in obs:d.uv(o,8)
 d.rod('Steel hanging rail',(-width/2,.12,.20),(width/2,.12,.20),.016,6,12)

def hanging(model,w,height,x,top=.17):
 obs=d.part(model,(w,height,.055),pack='restaurant',rot=0)
 for o in obs:
  o.data.transform(Matrix.Rotation(-math.pi/2,4,'X'));d.uv(o,6)
 lo,hi=d.bounds(obs);shift=Vector((x-(lo.x+hi.x)/2,.10-lo.y,top-hi.z))
 for o in obs:
  for v in o.data.vertices:v.co+=shift
 # actual suspension above handle at rail, spaced from backboard
 d.rod('Brass pan hook',(x,.12,.22),(x,.12,top-.015),.008,0,8)


def assembly(n):
 d.reset();d.base.PARTS=[];glows=[]
 if n=='ExtractorHood':
  obs=d.part('extractorhood',(1.0,.49,.63),(0,.245,0),pack='restaurant',rot=180)
  for o in obs:d.uv(o,6)
  d.box('Navy front lip',(0,.491,.06),(.98,.018,.065),8)
  # Task-light diffuser under the hood, its exposed front lip stays visible from the game camera.
  glows.append(d.box('Task light underside',(0,.30,-.004),(.78,.31,.016),5))
  glows.append(d.box('Task light visible lip',(0,.506,.027),(.78,.012,.023),5))
  for x in [-.39,-.26,-.13,0,.13,.26,.39]:d.box('Underside filter slot',(x,.28,-.014),(.012,.26,.006),18)
  for x in [.31,.39]:d.rod('Hood control',(x,.502,.09),(x,.512,.09),.013,0,10)
 elif n=='PotRail':
  rail(1.0)
  for i,(kind,w,ht) in enumerate([('pan_A',.205,.36),('pan_B',.23,.40),('pan_A',.18,.33),('pot_A',.225,.255)]):hanging(kind,w,ht,-.375+i*.25)
 elif n=='UtensilRail':
  rail(.84)
  for x in [-.30,-.10,.10,.30]:
   d.rod('Brass tool hook',(x,.12,.22),(x,.12,.145),.007,0,8)
   d.rod('Navy utensil handle',(x,.13,.145),(x,.13,-.06),.016,8,10)
   d.rod('Brass handle ferrule',(x,.13,-.045),(x,.13,-.073),.018,0,10)
  # Deep ladle bowl; open toward the viewer (+Y), shell has real thickness.
  x=-.30;vs=[];faces=[]
  for j in range(5):
   a=j*math.pi/8
   for i in range(12):
    t=i*math.tau/12;vs.append((x+.061*math.sin(a)*math.cos(t),.13-.043*math.cos(a),-.13+.061*math.sin(a)*math.sin(t)))
  for j in range(4):
   for i in range(12):faces.append((j*12+i,j*12+(i+1)%12,(j+1)*12+(i+1)%12,(j+1)*12+i))
  me=bpy.data.meshes.new('Ladle bowl');me.from_pydata(vs,[],faces);ob=bpy.data.objects.new('Steel ladle bowl',me);bpy.context.collection.objects.link(ob);d.uv(ob,6)
  mod=ob.modifiers.new('Cup thickness','SOLIDIFY');mod.thickness=.004;bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name)
  d.rod('Ladle stem',(x,.13,-.065),(x,.13,-.10),.009,6)
  # Slotted spatula with three true open slots.
  for xx in [-.145,-.115,-.085,-.055]:d.box('Turner steel tine',(xx,.13,-.13),(.014,.013,.12),6)
  for zz in [-.074,-.185]:d.box('Turner crosspiece',(-.10,.13,zz),(.108,.013,.012),6)
  # Six wire loops make a round whisk rather than a solid paddle.
  for k in range(6):
   a=k*math.pi/6
   for i in range(16):
    def pt(j):
     t=j*math.tau/16;r=.043*math.sin(t);return (.10+r*math.cos(a),.13+r*math.sin(a),-.135+.073*math.cos(t))
    d.rod('Whisk wire',pt(i),pt(i+1),.0035,6,5)
  d.rod('Wood spoon neck',(.30,.13,-.06),(.30,.13,-.105),.012,0)
  h.sphere('Wood spoon bowl',(.30,.13,-.145),(.043,.014,.064),False,0)
 elif n=='SpiceShelf':
  d.part('shelf_A_small',(.90,.22,.18),(0,.11,-.09))
  for i,kind in enumerate(['jar_A_small','jar_B_small','jar_C_small','jar_A_small','jar_C_small','jar_B_small']):
   x=-.35+i*.14;ht=[.145,.18,.16][i%3];obs=d.part(kind,(.105,.105,ht),(x,.12,.091),pack='restaurant')
   # Matching pale ceramic with coloured lid and a big cream label.
   for ob in obs:d.uv(ob,[0,10,3,0,10,3][i])
   d.box('Cream spice label',(x,.175,.091+ht*.48),(.068,.006,.047),5)
   d.box('Navy label dash',(x,.180,.091+ht*.48),(.036,.003,.005),8)
   d.rod('Spice jar lid',(x,.12,.091+ht-.014),(x,.12,.091+ht+.008),.055,[8,0,10][i%3],12)
 elif n=='KnifeStrip':
  obs=d.part('cuttingboard',(.70,.24,.035),pack='restaurant',rot=0)
  for o in obs:
   o.data.transform(Matrix.Rotation(-math.pi/2,4,'X'))
  lo,hi=d.bounds(obs)
  for o in obs:
   for v in o.data.vertices:v.co+=Vector((0,-lo.y,-(lo.z+hi.z)/2))
  d.box('Dark magnet strip',(0,.042,0),(.64,.015,.040),8)
  for i in range(4):
   x=-.245+i*.16;ht=[.32,.27,.34,.235][i]
   obs=d.part('knife',([.073,.059,.085,.050][i],.028,ht),(x,.075,-.20),pack='restaurant',rot=180)
   # Original upright knife has blade low and grip high; keep original atlas material separation.
 elif n=='ChoppingBlock':
  obs=d.part('cuttingboard',(.48,.34,.105),pack='restaurant',rot=0)
  for o in obs:d.uv(o,0)
  # End-grain inlays and shallow knife scores retain the pack's wood palette.
  for i in range(6):
   for j in range(4):
    d.box('End grain inset',(-.195+i*.078,-.126+j*.081,.106),(.075,.078,.004),[0,3,20,3][(i+j)%4])
  for x,y,ang in [(-.09,0,.3),(.06,.01,-.25),(.14,-.07,.15)]:
   o=d.box('Shallow knife score',(x,y,.109),(.002,.12,.001),3);o.rotation_euler.z=ang
  for x in [-.16,.16]:
   for y in [-.10,.10]:d.box('Rubber counter foot',(x,y,-.010),(.055,.045,.02),18)
 else:raise ValueError(n)
 meshes=[o for o in bpy.data.objects if o.type=='MESH'];body=h.joined([o for o in meshes if o not in glows],'Restaurant_'+n);obs=[body];gm=None
 if glows:
  glow=h.joined(glows,n+'_Glow');obs.append(glow);gm=bpy.data.materials.new(n+'_Glow');gm.use_nodes=True
  sr=[int('FFE0A0'[i:i+2],16)/255 for i in (0,2,4)];lin=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in sr]
  gm.diffuse_color=(*lin,1);bs=gm.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*lin,1);bs.inputs['Roughness'].default_value=.42;bs.inputs['Emission Strength'].default_value=0
  glow.data.materials.clear();glow.data.materials.append(gm)
  for p in glow.data.polygons:p.material_index=0
 lo,hi=d.bounds(obs);wall=n in WALL;shift=Vector(((lo.x+hi.x)/2,lo.y if wall else (lo.y+hi.y)/2,(lo.z+hi.z)/2 if wall else lo.z))
 for ob in obs:
  for v in ob.data.vertices:v.co-=shift
  for mat in ob.data.materials:
   if mat and mat.use_nodes:
    for node in mat.node_tree.nodes:
     if node.type=='TEX_IMAGE' and node.image:
      p=O/Path(node.image.filepath).name
      if p.exists():node.image=bpy.data.images.load(str(p),check_existing=True);node.image.pack()
 lo,hi=d.bounds(obs)
 return obs,dict(stem=n,name=body.name,mount='wall' if wall else 'counter',mount_height_m=1.95 if n=='ExtractorHood' else 1.60 if wall else .80,footprint_tiles=[1,1],size_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],bounds_blender=[list(lo),list(hi)],triangles=sum(len(p.vertices)-2 for ob in obs for p in ob.data.polygons),components=d.base.PARTS,authored_details=NOTES[n],glow_mesh=n+'_Glow' if glows else None,glow_material=gm.name if gm else None,glow_hex='#FFE0A0' if glows else None)

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

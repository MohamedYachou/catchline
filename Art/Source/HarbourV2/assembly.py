"""Occupied harbour evidence. Read-only source meshes; writes only HarbourV2.

--layout plan is the documented appendix, with explicit new-kit front/datum
corrections. --layout clearance is a proposed placement correction, not a
claim that foreign runtime code has adopted it. Independent mesh intersections
and source hashes are recorded alongside each editable scene and image.
"""
import bpy,math,json,sys,argparse,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
S=Path(__file__).resolve().parent;R=S.parents[2];O=R/'Art/Models/GullHarbour/HarbourV2'
spec=importlib.util.spec_from_file_location('harbour_build',S/'build.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
CACHE={};SOURCES={};ITEMS=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def source(name):
 if name in B.GROUPS['A']+B.GROUPS['B']+B.GROUPS['C']+B.GROUPS['D']:return O/(name+'.blend')
 if name in ['Rowboat','Skiff','CompactFisherV1','PrepFisherV1','Tier5DeepLines103']:return R/'Assets/Art/Models/Boats'/(name+'.fbx')
 return R/'Art/Models/GullHarbour/Harbour'/(name+'.blend')
def load(name):
 if name in CACHE:return CACHE[name]
 p=source(name);SOURCES[p.relative_to(R).as_posix()]=sha(p);before=set(bpy.data.objects)
 if p.suffix=='.blend':
  with bpy.data.libraries.load(str(p),link=False) as (fr,to):to.collections=[n for n in fr.collections if n=='ASSET_EXPORT']
  assert to.collections,(name,'no export collection')
  for col in to.collections:bpy.context.scene.collection.children.link(col)
 else:bpy.ops.import_scene.fbx(filepath=str(p),use_anim=False)
 bpy.context.view_layer.update();added=set(bpy.data.objects)-before
 meshes=[]
 for obj in added:
  if obj.type!='MESH':continue
  mesh=obj.data.copy();mesh.transform(obj.matrix_world);meshes.append((obj.name,mesh))
 assert meshes,name
 for obj in added:bpy.data.objects.remove(obj,do_unlink=True)
 CACHE[name]=meshes;return meshes
def bounds(objects):
 pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
 return [Vector(tuple(f(p[i] for p in pts) for i in range(3))) for f in (min,max)]
def place(name,x,z,y=.35,yaw=0,kind='structure',tag=None,scale=1):
 tag=tag or f'{name}@({x:g},{z:g})'
 meshes=load(name);rot=Matrix.Rotation(-math.radians(yaw),4,'Z')
 transform=Matrix.Translation((x,-z,y))@rot@Matrix.Scale(scale,4)
 objects=[]
 for label,data in meshes:
  obj=bpy.data.objects.new((tag or name)+' / '+label,data);bpy.context.scene.collection.objects.link(obj);obj.matrix_world=transform;objects.append(obj)
 bpy.context.view_layer.update();lo,hi=bounds(objects)
 item={'name':tag or name,'asset':name,'kind':kind,'position_unity':[x,y,z],'yaw_unity':yaw,'bounds_blender':[list(lo),list(hi)],'objects':objects}
 ITEMS.append(item);return item
def boat(name,x,z,bowin,tag):
 # All five canonical imports have long Y and bow -Y; retain world geometry,
 # then orient explicitly to the plan's -X / +Z bow convention.
 item=place(name,0,0,0,0 if bowin else 90,'boat',tag)
 lo,hi=bounds(item['objects']);center=(lo+hi)*.5
 shift=Vector((x-center.x,-z-center.y,0))
 for obj in item['objects']:obj.location+=shift
 bpy.context.view_layer.update();lo,hi=bounds(item['objects'])
 item['position_unity']=[x,0,z];item['bounds_blender']=[list(lo),list(hi)]
 return item
def ground_rowboat(item,support):
 # Match ramp pitch, then solve contact from actual hull vertices and densely
 # sampled edges against the actual concrete/rail surface. No hull edits.
 pitch=Matrix.Rotation(-math.atan(1.25/7),4,'X')
 centre=Vector((item['position_unity'][0],-item['position_unity'][2],0))
 for obj in item['objects']:obj.matrix_world=Matrix.Translation(centre)@pitch@Matrix.Translation(-centre)@obj.matrix_world
 bpy.context.view_layer.update();ramp=tree(support);samples=[]
 for obj in item['objects']:
  for edge in obj.data.edges:
   a,b=[obj.matrix_world@obj.data.vertices[i].co for i in edge.vertices]
   count=max(1,math.ceil((b-a).length/.06))
   samples.extend(a.lerp(b,i/count) for i in range(count+1))
 lowest=None
 for v in samples:
  hit,normal,index,distance=ramp.ray_cast(Vector((v.x,v.y,5)),Vector((0,0,-1)),10)
  if hit is not None:
   gap=v.z-hit.z
   if lowest is None or gap<lowest[0]:lowest=(gap,v.copy(),hit.copy())
 assert lowest is not None
 lift=.001-lowest[0]
 for obj in item['objects']:obj.location.z+=lift
 bpy.context.view_layer.update();lo,hi=bounds(item['objects']);item['bounds_blender']=[list(lo),list(hi)]
 item['position_unity'][1]=lift
 item['ramp_support']={'pitch_degrees':-math.degrees(math.atan(1.25/7)),'lift_metres':lift,'sample_spacing_max_metres':.06,'contact_gap_metres':.001,'boat_contact_blender':list(lowest[1]+Vector((0,0,lift))),'ramp_contact_blender':list(lowest[2])}
def block(name,c,size,colour):
 g=B.G();B.box(g,(c[0],-c[2],c[1]),(size[0],size[2],size[1]),colour,.01)
 obj=g.object(name,None,bpy.context.scene.collection)
 lo,hi=bounds([obj]);ITEMS.append({'name':name,'asset':'ground construction','kind':'ground','position_unity':list(c),'bounds_blender':[list(lo),list(hi)],'objects':[obj]})
def tree(item):
 vs=[];fs=[]
 for obj in item['objects']:
  offset=len(vs);vs += [obj.matrix_world@v.co for v in obj.data.vertices]
  fs += [tuple(offset+i for i in face.vertices) for face in obj.data.polygons]
 return BVHTree.FromPolygons(vs,fs,all_triangles=False,epsilon=0)
def collisions():
 # Ground/ground, shared quay joins and deliberate lantern-on-plinth contacts
 # are excluded. Every boat is tested against every boat and solid structure.
 result=[];trees={}
 for i,a in enumerate(ITEMS):
  for j,b in enumerate(ITEMS[i+1:],i+1):
   if a['kind']!='boat' and b['kind']!='boat':continue
   la,ha=map(Vector,a['bounds_blender']);lb,hb=map(Vector,b['bounds_blender'])
   if any(min(ha[k],hb[k])-max(la[k],lb[k])<=.00001 for k in range(3)):continue
   if i not in trees:trees[i]=tree(a)
   if j not in trees:trees[j]=tree(b)
   hits=trees[i].overlap(trees[j])
   if hits:result.append({'a':a['name'],'b':b['name'],'triangle_pairs':len(hits)})
 return result
def scene(tier,layout):
 corrected=layout in ('clearance','updated')
 updated=layout=='updated'
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 CACHE.clear();SOURCES.clear();ITEMS.clear();B.H.MATERIALS.clear();B.H.MATERIALS.update({k:B.H.material(k,v) for k,v in B.PALETTE.items()})
 sc=bpy.context.scene;sc.unit_settings.system='METRIC'
 # Solid support, matching the plan's quay and shore extents.
 block('QuayBack',(-6,-.12,8.5),(72,.94,8.5),'M_Steel')
 if corrected:
  block('BeachWest',(-35.5,-.40,1.6),(13,.50,6.6),'M_Rope')
  block('BeachEast',(-20.5,-.40,1.6),(1,.50,6.6),'M_Rope')
  block('BeachRampLanding',(-25,-.12,3.65),(8,.94,2.5),'M_Rope')
 else:block('Beach',(-31,-.40,1.6),(22,.50,6.6),'M_Rope')
 block('BeachBank',(-31,-.11,4.6),(22,.90,1.2),'M_Rope')
 for x in range(-18,27,4):place('Quay4m',x,3.3,.217 if corrected else .35)
 ramp=place('Slipway',-25,2.4,-.05 if corrected else 0)
 place('SuppliesShed',-28 if corrected else -29,6)
 if tier<3:
  place('MarketStallAwning',-21.5,5,.35,180)
  place('HarbourMasterHut',-17.5,6)
 place('NoticeBoard',-15.6,4.6)
 if tier>=1:
  place('BoatyardShed',-35 if corrected else -34,6.5)
  place('BoatCradle',-35 if corrected else -34,6.5 if corrected else 2.5)
  place('PontoonGangway',-13,3.5 if corrected else 2.4,0)
  for z in (-1.5,-5.5):place('PontoonSegment',-13,z,0)
  place('FuelDock',-13,-8.5 if corrected else -8.6,0)
  for n,x,front in [('HouseA',-10.4,'ShopFront_CrewOffice'),('HouseB',-6.8,'ShopFront_Chandlery')]:
   place(n,x,6.6,.35,180,scale=.95);place(front,x,4.95,.35)
 if tier>=2:
  place('NetLoft',9,6.6);place('QuayCrane',16.5 if corrected else 11.5,4.2)
 if tier>=3:
  for n,x,front in [('HouseA',-2.6,'ShopFront_FishMarket'),('HouseB',1,'ShopFront_HarbourMaster')]:
   place(n,x,6.6,.35,180,scale=.95);place(front,x,4.95,.35)
  place('IceHouse',5,6.4)
 breakz=-12 if corrected else -8
 for z in (0,-4,-8) if corrected else (2,-2,-6):place('BreakwaterWall',28,z,0,90)
 for x in (26,22,18,14,10) if corrected else (28,24,20,16,12,8):place('BreakwaterWall',x,breakz,0)
 headx=6.5 if corrected else 4.5
 place('BreakwaterEnd',headx,breakz-.5,0);place('Lighthouse',headx-.7,breakz-.5,.60,200)
 for i in range(13):
  t=i/12;x=(1-t)**2*-40+2*t*(1-t)*-34+t*t*-19;z=(1-t)**2*1+2*t*(1-t)*-16+t*t*-14
  place('BreakwaterRock'+['A','B','C'][i%3],x,z,-.35,i*57,scale=1.6)
 place('MouthBeacon',-18.6 if corrected else -18,-14 if corrected else -11,0)
 wharfz=-10.6 if corrected else -6.6
 if tier>=4:
  for x in (12,16,20,24):place('OuterWharf',x,wharfz,0)
  for x in (10.6,25.4):place('WharfLight',x,wharfz,.35)
 # Actual canonical boats and the delivered paint variants occupy every berth.
 for i,x in enumerate((-27.35,-22.65) if corrected else (-27.2,-22.8)):
  row=boat('Rowboat',x,-1.8 if updated else (-4.8 if corrected else -.6),True,f'Rowboat slot{i}')
  # Keep all rowboats level at their canonical floating datum.
 if tier>=1:
  boat('Skiff' if tier>=1 else 'Skiff_VariantYellow',-10.25,-6.5,True,'Pontoon slot0')
  boat('Skiff_VariantYellow',-15.75,-1.6,True,'Pontoon slot1')
 # Leave these visible at all tiers so future fishing hulls are seen across water.
 fish=['CompactFisherV1_VariantRed','PrepFisherV1_VariantGreen']
 if tier==2:fish[0]='CompactFisherV1'
 if tier>=3:fish=['PrepFisherV1','CompactFisherV1']
 for i,(name,x) in enumerate(zip(fish,(1.5,12.5))):
  sample=load(name);pts=[v.co for _,data in sample for v in data.vertices];beam=max(v.x for v in pts)-min(v.x for v in pts)
  boat(name,x,2.05-beam/2,False,f'FishQuay slot{i}')
 for i,x in enumerate(((12.4,24.2) if updated else (11.9,21.4)) if corrected else (11.5,22)):
  name='Tier5DeepLines103' if tier>=4 and i==0 else 'Tier5DeepLines103_VariantBlue'
  sample=load(name);pts=[v.co for _,data in sample for v in data.vertices];beam=max(v.x for v in pts)-min(v.x for v in pts)
  boat(name,x,wharfz+.9+(.55 if updated else .3)+beam/2 if corrected else -7.65,False,f'OuterWharf slot{i}')
 bpy.context.view_layer.update();hits=collisions()
 meshes=[o for item in ITEMS for o in item['objects']]
 
 if ARGS.audit_only:
  out=O/'assembly'/layout;out.mkdir(parents=True,exist_ok=True)
  (out/f'tier{tier}-audit.json').write_text(json.dumps({'tier':tier,'items':[{k:v for k,v in it.items() if k!='objects'} for it in ITEMS],'conflicts':hits},indent=2)+'\n')
  print('AUDIT',layout,tier,json.dumps(hits),flush=True);return
 sc,lo,hi=B.stage(meshes);bpy.data.objects['Preview_Ground'].hide_render=True
 # Sea is an evidence-stage surface, never exported with an asset.
 g=B.G();B.box(g,(0,0,-.35),(250,250,.06),'M_HullBlue',0);water=g.object('AssemblyWater',None,sc.collection)
 sc.render.resolution_x=1440;sc.render.resolution_y=900;sc.cycles.samples=24
 out=O/'assembly'/layout;out.mkdir(parents=True,exist_ok=True)
 cam=sc.camera;cam.data.type='ORTHO';pitch=math.radians(45);yaw=math.radians(35)
 def camera(target,scale):
  cam.location=Vector(target)+Vector((math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),math.sin(pitch)))*160
  cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 camera((-6,0,0),88)
 sc.render.filepath=str(out/f'tier{tier}-whole.png');bpy.ops.render.render(write_still=True)
 paths=[Path(sc.render.filepath)]
 sc.render.resolution_x=844;sc.render.resolution_y=390
 focuses=[(-25,-1,0,31),(-17,-1,0,36),(6,-1,0,35),(4,-1,0,35),(13,3,0,38)]
 x,y,z,scale=focuses[tier];camera((x,y,z),scale)
 sc.render.filepath=str(out/f'tier{tier}-phone.png');bpy.ops.render.render(write_still=True);paths.append(Path(sc.render.filepath))
 bpy.ops.wm.save_as_mainfile(filepath=str(out/f'tier{tier}.blend'),check_existing=False)
 for p,h in SOURCES.items():assert sha(R/p)==h,('changed source',p)
 receipt={'tier':tier,'layout':layout,'camera':{'pitch':45,'yaw':35,'projection':'orthographic'},
  'sources':SOURCES,'items':[{k:v for k,v in item.items() if k!='objects'} for item in ITEMS],
  'boat_surface_intersections':hits,'clearance_result':'FAIL' if hits else 'NO_SURFACE_INTERSECTIONS',
  'limitations':['Surface intersections do not prove containment-free solid clearance.','Datum/front corrections applied explicitly; this is Blender evidence, not Unity runtime acceptance.','Phone frame uses landscape844x390 berth focus, whole view uses full harbour.'],
  'renders':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'review':'pending'} for p in paths]}
 (out/f'tier{tier}.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('ASSEMBLY',layout,tier,'intersections',len(hits),json.dumps(hits),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--tier',type=int,choices=range(5),required=True);ap.add_argument('--layout',choices=['plan','clearance','updated'],default='plan')
 ap.add_argument('--audit-only',action='store_true')
 ARGS=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);scene(ARGS.tier,ARGS.layout)

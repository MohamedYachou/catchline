"""Task07 world kit. Windows Blender5.2 headless; optional -- asset names.
Existing sources are read only. Runtime axes +Y up,+Z forward. M_* palette.
"""
import bpy,math,json,sys,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('task04',Path(__file__).with_name('build_task04.py'));T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
K=T.K;B=K.B;G=K.G;box=K.bevel_box;part=K.part;ring=K.ring;lathe=K.lathe
NAVY=T.NAVY;WOOD=T.WOOD;IVORY=T.IVORY;STEEL=T.STEEL;TEAL=T.TEAL;ORANGE=T.ORANGE;ROPE=T.ROPE;GREEN='M_KelpGreen';BLUE='M_HullBlue';DARK='M_Rubber';GOLD='M_OilskinYellow'
OUT=ROOT/'Art/Models/WorldPolish'
B.PALETTE.update({'M_HairChestnut':'#50392E','M_HairSilver':'#ADB6AF'})
def recolour(mapping):
 for o in K.COLLECTION.objects:
  if o.type=='MESH':
   for slot in o.material_slots:
    if slot.material.name in mapping:slot.material=B.MATERIALS[mapping[slot.material.name]]
def scale_parts(s):
 for o in K.COLLECTION.objects:
  if o.type=='MESH':
   o.location=Vector([o.location[i]*s[i] for i in range(3)])
   for v in o.data.vertices:v.co=Vector([v.co[i]*s[i] for i in range(3)])
   K.PIVOTS[o.name]=list(o.location)
def house(g,c=(0,0,0),scale=1,col=IVORY):
 a=G();box(a,(0,0,.8),(1.65,1.4,1.6),col,.035)
 a.add([(-.95,-.8,1.6),(.95,-.8,1.6),(0,-.8,2.35),(-.95,.8,1.6),(.95,.8,1.6),(0,.8,2.35)],[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],ORANGE if col==TEAL else NAVY)
 box(a,(0,-.708,.54),(.42,.035,1.08),NAVY,.01)
 for x in (-.55,.55):
  box(a,(x,-.72,1.02),(.35,.045,.46),BLUE,.015)
  for dx in (-.2,.2):a.beam((x+dx,-.75,.78),(x+dx,-.75,1.28),.04,.04,IVORY)
  for z in (.78,1.28):a.beam((x-.2,-.75,z),(x+.2,-.75,z),.04,.04,IVORY)
 box(a,(.36,.20,2.18),(.20,.22,.55),IVORY,.015);g.merge(a,c,scale)
def tree(g,c=(0,0,0),s=1):
 a=G();a.beam((0,0,0),(0,0,1.45),.13,.13,WOOD)
 a.ellipsoid((0,0,1.48),(.55,.50,.70),9,4,GREEN);a.ellipsoid((.32,.02,1.42),(.36,.34,.42),8,3,GREEN);g.merge(a,c,s)
def upgrade(n):
 if n in ('BigCooler','BigIceBox'):K.cooler(n=='BigIceBox');scale_parts((1.25,1.2,1.111111111));return
 if n.startswith('FishingRod_'):
  K.fishing_rod();recolour({NAVY:IVORY,WOOD:ORANGE} if n.endswith('Fibreglass') else {NAVY:DARK,WOOD:GOLD,'M_WoodHighlight':GOLD,STEEL:STEEL});return
 if n=='Outboard_Small':
  T.skiff()
  for o in list(K.COLLECTION.objects):
   if o.type=='MESH' and o.name not in ('OutboardMotor','Propeller'):bpy.data.objects.remove(o,do_unlink=True)
  shift=Vector((0,3.05,.35))
  for o in K.COLLECTION.objects:
   if o.type=='MESH':
    o.location-=shift;K.PIVOTS[o.name]=list(o.location)
  for k in list(K.PIVOTS):
   if k not in ('OutboardMotor','Propeller'):del K.PIVOTS[k]
  K.NOTES[:]=['Root at transom clamp; source propeller pivot (0,.35,-.95), Unity(0,-.95,-.35). Spins source Y / Unity Z.'];return
 g=G()
 if n=='RodHolderClamp':
  box(g,(0,0,.035),(.16,.10,.07),STEEL,.01);box(g,(0,.065,.01),(.13,.04,.14),NAVY,.008)
  ring(g,.043,.011,.07,.24,STEEL,sides=12);g.beam((.075,.05,.04),(.13,.05,.04),.025,.025,DARK)
 elif n=='FuelCan':
  box(g,(0,0,.19),(.28,.18,.38),ORANGE,.025);box(g,(.07,0,.407),(.07,.08,.06),DARK,.009)
  g.rectangle_ring(.18,.10,.025,.38,.47,.025,ORANGE);box(g,(0,-.097,.19),(.17,.009,.10),IVORY,.012)
 elif n in ('SquidTub','WormTub'):
  lathe(g,[(0,.12),(.02,.14),(.14,.16)],16,TEAL if n=='SquidTub' else NAVY)
  ring(g,.165,.012,.135,.16,IVORY);lathe(g,[(.145,.15),(.15,.15)],16,DARK)
  if n=='SquidTub':
   for x in (-.07,.03):
    g.ellipsoid((x,0,.16),(.031,.068,.024),12,4,IVORY)
    for i in range(4):g.tube([(x-.02+i*.012,-.03,.16),(x-.025+i*.015,-.10,.155),(x-.01+i*.01,-.13,.157)],[.006]*3,6,IVORY)
  else:
   for i in range(4):g.tube([(-.09+i*.047,-.07,.155),(-.07+i*.047,0,.16),(-.10+i*.047,.07,.155)],[.009]*3,7,ROPE)
 part(n,g)
def harbour(n):
 if n.startswith('Rowboat_Variant'):K.rowboat();recolour({NAVY:ORANGE if n.endswith('Red') else GREEN});return
 if n=='Skiff_VariantBlue':T.skiff();recolour({NAVY:BLUE});return
 g=G()
 if n=='HillBackdrop':
  # Matching 40m end profile; tiers read as landscape rather than a wall.
  profile=[(-4,0),(-3.5,1.1),(-1.8,1.1),(-1,2.3),(1,2.3),(2,3.4),(4,3.4),(5,0)]
  verts=[(x,y,z) for x in (-20,-12,-4,4,12,20) for y,z in profile];N=len(profile)
  g.add(verts,[tuple(reversed(range(N))),tuple(range(5*N,6*N))],GREEN)
  for j in range(5):
   for i in range(N):g.add(verts,[(j*N+i,(j+1)*N+i,(j+1)*N+(i+1)%N,j*N+(i+1)%N)],GREEN if i in (1,3,5) else STEEL)
  part('SteppedHills',g);g=G()
  for i,x in enumerate((-16,-10,-3,5,13,17)):house(g,(x,.3 if i%2 else 2.9,2.3 if i%2 else 3.4),.9 if i%2 else .75,TEAL if i%2 else IVORY)
  part('HillHouses',g);g=G()
  box(g,(2,2.9,5.25),(1.6,1.4,3.7),IVORY,.04)
  lathe(g,[(7.1,.99),(8.5,0)],4,NAVY,(2,2.9,0));box(g,(2,2.18,6.6),(.55,.03,.70),BLUE,.03)
  g.beam((2,2.9,8.4),(2,2.9,9),.06,.06,STEEL);g.beam((1.8,2.9,8.75),(2.2,2.9,8.75),.06,.06,STEEL)
  part('ChurchTower',g);g=G()
  for x,y,z in [(-18,0,2.3),(-13,3,3.4),(-7,3,3.4),(0,-1.1,1.1),(9,3,3.4),(16,-1,1.1)]:tree(g,(x,y,z),.8)
  for x in range(-18,19,2):
   g.beam((x,-2.1,1.1),(x,-2.1,1.8),.07,.07,WOOD)
  for z in (1.35,1.63):g.beam((-18,-2.1,z),(18,-2.1,z),.07,.07,WOOD)
  for i in range(12):box(g,(-6,-3.2+i*.35,.05+i*.10),(1.25,.40,.10),STEEL,.01)
  part('TreesFencesSteps',g);K.NOTES.append('40m X repeat, end cross-sections match. Place behind shops; includes separate landscape,houses,tower,dressing.');return
 elif n=='Shed_Shipyard':
  for x in (-3.8,3.8):
   for y in (-2.7,0,2.7):g.beam((x,y,0),(x,y,4.1),.20,.20,WOOD,.02)
  box(g,(0,2.85,2),(8,.16,4),TEAL,.03)
  for x in (-3.95,3.95):box(g,(x,0,2),(.12,5.7,4),TEAL,.02)
  g.add([(-4.2,-3,4),(4.2,-3,4),(0,-3,5.6),(-4.2,3,4),(4.2,3,4),(0,3,5.6)],[(0,1,2),(3,5,4),(0,2,5,3),(1,4,5,2)],NAVY)
  for y in (-2.9,-1.4,0,1.4,2.9):g.beam((-4.2,y,4),(0,y,5.6),.08,.08,WOOD);g.beam((4.2,y,4),(0,y,5.6),.08,.08,WOOD)
  part('ShedShell',g);g=G()
  for x in (-1.4,1.4):g.beam((x,-5.2,-.35),(x,2.6,.12),.13,.13,STEEL)
  for y in (-4.8,-3.8,-2.8,-1.8,-.8,.2,1.2,2.2):box(g,(0,y,-.13+(y+4.8)*.06),(3.2,.22,.14),WOOD,.012)
  part('Slipway',g);K.NOTES.append('8x6m shed shell; open water-facing entrance. Slipway extends2.2m in front, below ground.');return
 elif n=='MarketStall':
  T.harbour_prop('MarketStallAwning');g=G();box(g,(.72,0,1.0),(.33,.28,.06),STEEL,.012)
  box(g,(.72,.04,1.2),(.07,.07,.38),NAVY,.01);box(g,(.72,-.015,1.34),(.24,.07,.22),IVORY,.018)
  g.ellipsoid((.72,-.057,1.34),(.08,.012,.08),16,5,STEEL);g.beam((.72,-.072,1.34),(.75,-.072,1.39),.009,.009,NAVY)
  # Obvious display on the viewer-facing counter edge, clear of the awning.
  box(g,(-.28,-.49,.982),(1.20,.48,.075),IVORY,.018)
  for x,y in [(-.65,-.49),(-.28,-.46),(.09,-.50)]:
   g.ellipsoid((x,y,1.055),(.075,.18,.035),14,5,'M_FishSilver')
   g.ellipsoid((x,y+.02,1.079),(.048,.135,.012),12,4,BLUE)
   g.extrude_polygon([(x,y+.13),(x-.073,y+.26),(x+.073,y+.26)],1.04,1.065,BLUE)
   g.ellipsoid((x+.046,y-.12,1.078),(.011,.011,.006),8,3,DARK)
   for dx,dy in [(-.08,-.04),(.075,.05)]:box(g,(x+dx,y+dy,1.04),(.045,.045,.035),IVORY,.006)
  part('ScaleAndIce',g);return
 elif n=='Gangway':
  for i in range(12):box(g,(0,-1.5+i*.27,.025),(.90,.26,.05),WOOD,.003)
  for x in (-.5,.5):
   for y in (-1.55,0,1.55):g.beam((x,y,0),(x,y,.85),.045,.045,STEEL)
   g.beam((x,-1.55,.85),(x,1.55,.85),.055,.055,STEEL)
 elif n=='Ladder':
  for x in (-.25,.25):g.tube([(x,0,.05),(x,0,1.6),(x,-.12,1.75)],[.028]*3,8,STEEL)
  for i in range(8):g.beam((-.25,0,.13+i*.20),(.25,0,.13+i*.20),.035,.035,STEEL)
 elif n=='LifebuoyStand':
  T.harbour_prop('Lifebuoy');g=G();g.beam((0,.1,0),(0,.1,1.2),.065,.065,WOOD)
  box(g,(0,.1,.035),(.6,.4,.07),NAVY,.015)
  # Raise existing ring to a readable display height.
  ob=next(o for o in K.COLLECTION.objects if o.name=='Lifebuoy')
  for v in ob.data.vertices:v.co.z+=.50
 elif n=='CrabPotStack':
  for c in [(-.31,0,0),(.36,.04,0),(0,.02,.37)]:g.merge(B.pot_geometry(),c)
 elif n=='Bench':
  for y in (-.18,0,.18):box(g,(0,y,.43),(1.5,.15,.065),WOOD,.012)
  for z in (.70,.90):box(g,(0,.26,z),(1.5,.06,.13),WOOD,.012)
  for x in (-.55,.55):
   for y in (-.18,.18):g.beam((x,y,0),(x,y,.40),.065,.065,NAVY)
   g.beam((x,.26,.35),(x,.26,1),.065,.065,NAVY)
 part(n,g)
def sea(n):
 g=G()
 if n=='RockArch':
  # Open arch assembled from closed faceted rock segments; walk/water opening clear.
  for x,z,rx,rz in [(-1.7,.85,.8,1.1),(1.7,.85,.8,1.1),(-1.2,2.0,.8,.65),(1.2,2.0,.8,.65),(0,2.48,.95,.55)]:g.ellipsoid((x,0,z),(rx,.62,rz),9,4,STEEL)
 elif n=='WreckMast':
  g.beam((-.3,0,-.4),(.3,0,2.8),.15,.15,WOOD,.02);g.beam((-1.3,0,1.95),(1.45,0,2.2),.09,.09,WOOD)
  g.tube([(-1.3,0,1.95),(.3,0,2.8),(1.45,0,2.2)],[.018]*3,6,ROPE)
  g.extrude_polygon([(-.05,-.03),(.95,-.03),(.45,.03),(-.05,.03)],.8,1.55,IVORY)
 elif n=='KelpForest':
  K.kelp();obs=[o for o in K.COLLECTION.objects if o.type=='MESH'];o=obs[0]
  low=[min(v.co[i] for v in o.data.vertices) for i in (0,1)];hi=[max(v.co[i] for v in o.data.vertices) for i in (0,1)]
  for v in o.data.vertices:
   for i in (0,1):v.co[i]=(v.co[i]-(low[i]+hi[i])/2)*4/(hi[i]-low[i])
  K.NOTES.append('Exactly4x4m planar at waterline; two-sided palette material recommended.');return
 elif n=='SandBank_Large':
  g.extrude_polygon([(-3.2,-.4),(-2.1,-1.5),(.4,-1.4),(3.2,-.5),(2.2,1.2),(-1,1.5)],-.10,0,ROPE)
  g.extrude_polygon([(-2,-.4),(-1.6,-.9),(.4,-.9),(2,-.3),(1.3,.8),(-.7,.9)],.001,.015,'M_WoodHighlight')
 elif n=='BirdIsland':
  g.ellipsoid((0,0,.27),(1.15,.8,.4),10,4,STEEL);part('IslandRock',g)
  T.seagull()
  for ob in list(K.COLLECTION.objects):
   if ob.type=='MESH' and ob.name!='IslandRock':
    for v in ob.data.vertices:v.co.z+=.58
  return
 elif n.startswith('MarkerBuoy_'):
  col=GREEN if n.endswith('Green') else ORANGE
  lathe(g,[(-.18,.12),(0,.28),(.17,.28),(.32,.11)],12,col);ring(g,.282,.015,.08,.15,IVORY)
  g.beam((0,0,.3),(0,0,1.0),.04,.04,NAVY)
  if n.endswith('Green'):lathe(g,[(.85,.19),(1.18,0)],8,col)
  else:lathe(g,[(.89,.16),(1.10,.16)],12,col)
  K.NOTES.append('Waterline root, red cylindrical/green conical topmarks; region navigation rules set by game.')
 elif n=='WhaleTail':
  g.ellipsoid((0,0,.18),(.45,.28,.45),14,7,BLUE)
  for s in (-1,1):
   poly=[(0,-.02),(s*.55,-.25),(s*1.18,-.12),(s*1.45,.28),(s*.55,.20),(s*.18,.13)]
   a=G();a.extrude_polygon(poly,.48,.61,BLUE);a.vertices=[(x,y,z+.20*abs(x)) for x,y,z in a.vertices];g.merge(a)
  part('Tail',g,(0,0,0));K.NOTES.append('Tail pivot at waterline base. Consumer raises/lowers whole Tail mesh for rare event; no baked clip.');return
 part(n,g)
def npc(n):
 role,hat,act,frame={'NPC_Fishmonger':('Fisherman','Hood','Wait',10),'NPC_HarbourMaster':('Captain','CaptainCap','Bait',1),'NPC_Sitting':('Veteran','Beanie','Row',1)}[n]
 with bpy.data.libraries.load(str(ROOT/'Art/Models/CrewRig/CrewRig.blend'),link=False) as (src,dst):
  dst.objects=[x for x in ['CrewRig','Body','Outfit_'+role,'Hat_'+hat] if x in src.objects];dst.actions=[act]
 loaded=[o for o in dst.objects if o]
 for o in loaded:
  if o.name not in bpy.context.scene.objects:K.COLLECTION.objects.link(o)
 arm=next(o for o in loaded if o.type=='ARMATURE');arm.animation_data_create();arm.animation_data.action=dst.actions[0];bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
 if n=='NPC_Sitting':
  # Strong static seated adaptation of Row: horizontal thighs, vertical shins.
  from mathutils import Quaternion
  arm.pose.bones['Hips'].location.z=0
  for side in ('Left','Right'):
   arm.pose.bones[side+'UpLeg'].rotation_quaternion=Quaternion((1,0,0),-math.pi/2)
   arm.pose.bones[side+'Leg'].rotation_quaternion=Quaternion((1,0,0),math.pi/2)
  bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get()
 for ob in [o for o in loaded if o.type=='MESH']:
  ev=ob.evaluated_get(dg);mesh=bpy.data.meshes.new_from_object(ev,depsgraph=dg);g=G()
  mats=[slot.material.name.split('.')[0] for slot in ob.material_slots]
  for mat in mats:
   if mat not in B.PALETTE:
    B.PALETTE[mat]={'M_HairChestnut':'#50392E','M_HairSilver':'#ADB6AF'}[mat];B.MATERIALS[mat]=B.material(mat,B.PALETTE[mat])
  g.vertices=[tuple(ob.matrix_world@v.co) for v in mesh.vertices];g.faces=[tuple(p.vertices) for p in mesh.polygons];g.colours=[mats[p.material_index] for p in mesh.polygons]
  part(n+'_'+ob.name,g,smooth=True)
 for ob in loaded:bpy.data.objects.remove(ob,do_unlink=True)
 K.NOTES.append('Static evaluated Task06 rig pose; no runtime armature/actions. NPC_Sitting adapts Row with horizontal thighs and vertical shins. Bare local outfit seat contact Z=.239; Bench seat top Z=.4625. Place NPC root at UnityY=.2235 above Bench root; short legs dangle. Crew source unchanged.')
UP=['BigCooler','BigIceBox','RodHolderClamp','FishingRod_Fibreglass','FishingRod_Carbon','Outboard_Small','FuelCan','SquidTub','WormTub']
HAR=['HillBackdrop','Shed_Shipyard','MarketStall','Rowboat_VariantRed','Rowboat_VariantGreen','Skiff_VariantBlue','Gangway','Ladder','LifebuoyStand','CrabPotStack','Bench']
NPC=['NPC_Fishmonger','NPC_HarbourMaster','NPC_Sitting']
SEA=['RockArch','WreckMast','KelpForest','SandBank_Large','BirdIsland','MarkerBuoy_Green','MarkerBuoy_Red','WhaleTail']
ASSETS={**{n:('Boats' if n=='Outboard_Small' else 'DeckProps',lambda n=n:upgrade(n)) for n in UP},**{n:('Harbour',lambda n=n:harbour(n)) for n in HAR},**{n:('Harbour',lambda n=n:npc(n)) for n in NPC},**{n:('Sea',lambda n=n:sea(n)) for n in SEA}}
def build(n,assets=ASSETS,out=OUT):
 group,factory=assets[n];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 K.PIVOTS.clear();K.NOTES.clear();B.MATERIALS.clear();B.MATERIALS.update({k:B.material(k,v) for k,v in B.PALETTE.items()})
 K.COLLECTION=bpy.data.collections.new('ASSET_EXPORT');scene.collection.children.link(K.COLLECTION)
 K.ASSET_ROOT=bpy.data.objects.new('Catchline_'+n,None);K.COLLECTION.objects.link(K.ASSET_ROOT)
 K.ASSET_ROOT['unity_forward']='+Z';factory();bpy.context.view_layer.update()
 meshes=[o for o in K.COLLECTION.objects if o.type=='MESH'];stats=[B.mesh_stats(o) for o in meshes]
 low=[min(p['bounds_min_blender'][i] for p in stats) for i in range(3)];high=[max(p['bounds_max_blender'][i] for p in stats) for i in range(3)]
 B.preview_stage(scene,meshes);cam=scene.camera;target=Vector([(low[i]+high[i])/2 for i in range(3)])
 scale=max(1,max(high[i]-low[i] for i in range(3)));cam.location=target+Vector((.406,.579 if group=='Stations' else -.579,.707))*scale*3;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 projected=[cam.matrix_world.inverted()@(o.matrix_world@Vector(p)) for o in meshes for p in o.bound_box]
 cam.data.ortho_scale=max(max(p[i] for p in projected)-min(p[i] for p in projected) for i in (0,1))*1.24
 for light in bpy.data.collections['PREVIEW_ONLY_NOT_EXPORTED'].objects:
  if light.type=='LIGHT':light.location*=scale;light.data.energy*=scale*scale;light.data.size*=scale
 bpy.data.objects['Preview_Ground'].location.z=low[2];scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=512
 for p in (out/group,out/'Previews'/group,ROOT/'Assets/Art/Models'/group):p.mkdir(parents=True,exist_ok=True)
 source=out/group/(n+'.blend');fbx=ROOT/'Assets/Art/Models'/group/(n+'.fbx');preview=out/'Previews'/group/(n+'.png')
 bpy.ops.object.select_all(action='DESELECT')
 for ob in K.COLLECTION.objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=K.ASSET_ROOT
 bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,use_triangles=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,use_custom_props=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(source));scene.render.filepath=str(preview);bpy.ops.render.render(write_still=True)
 print('BUILT',n,flush=True)
 return {'asset':n,'group':group,'source':source.relative_to(ROOT).as_posix(),'fbx':fbx.relative_to(ROOT).as_posix(),'preview':preview.relative_to(ROOT).as_posix(),'triangles':sum(p['triangles'] for p in stats),'bounds_min_blender':low,'bounds_max_blender':high,'dimensions_width_depth_height_m':[high[i]-low[i] for i in range(3)],'parts':stats,'pivots_blender':dict(K.PIVOTS),'notes':list(K.NOTES)}
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(ASSETS)
 OUT.mkdir(parents=True,exist_ok=True);p=OUT/'build-metrics.json';data=json.loads(p.read_text()) if p.exists() else {'assets':[]};index={a['asset']:a for a in data['assets']}
 for n in args:index[n]=build(n);data['assets']=list(index.values());data['palette_srgb']=B.PALETTE;p.write_text(json.dumps(data,indent=2)+'\n')

"""SERVICE-PROPS-4: one item per invocation; canonical atlas; Blender-only evidence.
Authoring XYZ -> RoomRoot local Unity (-X,Z,-Y). No runtime asset writes.
"""
import sys,json,math,hashlib,uuid
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import build_props3 as p
import bpy
from mathutils import Vector,Matrix
b=p.b;c=p.c;R=p.R;PI=math.pi
box=b.box;ell=b.ell;rod=b.rod;torus=b.torus;lathe=b.lathe;mesh=b.mesh;cyl=b.cyl

def tint(o,color):return p.paint(o,'white',color)
def B(n,a,s,col,bev=.008,rot=0):return tint(box(n,a,s,'white',bev,rot),col)
def E(n,a,s,col,sub=1):return tint(ell(n,a,s,'white',sub),col)
def T(n,a,ma,mi,col,nseg=16,m=4,rot=None):return tint(torus(n,a,ma,mi,'white',nseg,m,rotate=rot),col)
def D(n,a,bb,r,col,nseg=6):return tint(rod(n,a,bb,r,'white',nseg),col)
def L(n,profile,col,nseg=12,at=(0,0,0),sx=1,sy=1):return tint(lathe(n,profile,'white',nseg,at,sx,sy),col)
FRONT=Matrix.Rotation(PI/2,3,'X')
CREAM='F4E5BB';TEAL='237E83';CORAL='D9694F';BRASS='BD8D3D';NAVY='224958';ROPE='C5A77C';WOOD='966036'

def life_ring():
 # Torus axis -Y, rear-most ring face on contact plane y=0.
 o=T('Chunky cream cork ring',(0,-.074,0),.252,.071,CREAM,24,6,FRONT)
 # Broad coral bands are separate raised torus arcs, exactly 4 with open centre preserved.
 for k in range(4):
  vv=[];nn=4;mm=6
  for i in range(nn+1):
   a=k*PI/2-.19+i*.38/nn
   for j in range(mm):
    q=j*2*PI/mm;rr=.252+.074*math.cos(q);vv.append((rr*math.cos(a),-.074+.074*math.sin(q),rr*math.sin(a)))
  ff=[(i*mm+j,(i+1)*mm+j,(i+1)*mm+(j+1)%mm,i*mm+(j+1)%mm) for i in range(nn) for j in range(mm)]
  tint(mesh('Coral safety band',vv,ff,'white'),CORAL)
 T('Coarse perimeter rope',(0,-.057,0),.355,.013,ROPE,32,4,FRONT)
 for k in range(4):
  a=k*PI/2+.40
  D('Rope keeper',(.305*math.cos(a),-.06,.305*math.sin(a)),(.355*math.cos(a),-.06,.355*math.sin(a)),.019,CREAM)
 B('Wall hook',(0,-.025,.362),(.035,.05,.07),BRASS,.003)

def ship_wheel():
 T('Honey wheel rim',(0,-.071,0),.235,.033,'B78043',20,5,FRONT)
 T('Brass inner rim',(0,-.081,0),.235,.009,BRASS,20,4,FRONT)
 for i in range(8):
  a=i*PI/4
  D('Broad wheel spoke',(.045*math.cos(a),-.071,.045*math.sin(a)),(.245*math.cos(a),-.071,.245*math.sin(a)),.021,'C89859')
  D('Rounded timber grip',(.257*math.cos(a),-.071,.257*math.sin(a)),(.340*math.cos(a),-.071,.340*math.sin(a)),.026,WOOD,8)
  E('Grip end',(.343*math.cos(a),-.071,.343*math.sin(a)),(.052,.052,.052),'C89859')
 D('Wall mount',(0,0,0),(0,-.13,0),.064,BRASS,12)
 D('Navy hub cap',(0,-.13,0),(0,-.147,0),.047,NAVY,12)
 D('Brass centre pin',(0,-.148,0),(0,-.155,0),.012,BRASS,8)

def fish_print():
 B('Timber backboard',(0,-.027,0),(.76,.054,.47),WOOD)
 B('Cream painted paper',(0,-.059,0),(.65,.014,.36),CREAM,.001)
 for x in [-.357,.357]:B('Teal frame stile',(x,-.060,0),(.046,.050,.47),TEAL,.006)
 for z in [-.212,.212]:B('Teal frame rail',(0,-.06,z),(.69,.050,.046),TEAL,.006)
 # Flat painted fish is tangible low-relief graphic, no lettering.
 def patch(n,v,col,y=-.071):return tint(mesh(n,[(x,y,z) for x,z in v],[tuple(range(len(v)))],'white'),col)
 patch('Painted fish body',[(-.245,0),(-.17,.090),(.025,.105),(.195,.018),(.21,0),(.15,-.075),(-.09,-.085)],TEAL)
 patch('Painted tail',[(-.20,0),(-.29,.105),(-.28,-.095)],CORAL,-.0707)
 patch('Painted fish belly',[(-.16,-.025),(.18,-.01),(.15,-.075),(-.09,-.085)],'70B6AE',-.072)
 patch('Dorsal fin',[(-.08,.09),(.00,.16),(.09,.086)],NAVY,-.0707)
 patch('Pectoral fin',[(.02,.0),(-.06,-.05),(.055,-.035)],CORAL,-.073)
 # Painted circles, rotated to face the room.
 for n,x,z,r,col in [('Ivory painted eye',.132,.033,.023,CREAM),('Navy painted pupil',.136,.035,.012,NAVY)]:
  patch(n,[(x+r*math.cos(i*2*PI/12),z+r*math.sin(i*2*PI/12)) for i in range(12)],col,-.075 if r<.02 else -.074)
 for x in [-.22,-.13,-.04,.05,.14]:D('Painted sea dash',(x,-.072,-.135),(x+.035,-.072,-.135),.0028,'8ABAB1',4)

def net_floats():
 # Open diamond lattice, hung from two rear-contact brass pegs.
 def pt(i,j):
  x=(i+j)*.103-.4635
  return (x,-.038-.015*math.sin((i+j)/9*PI),(i-j)*.072-.10*math.sin((i+j)/9*PI))
 for i in range(6):
  for j in range(5):
   if i<5:D('Knotted net diagonal',pt(i,j),pt(i+1,j),.0045,ROPE,3)
   if j<4:D('Knotted net diagonal',pt(i,j),pt(i,j+1),.0045,ROPE,3)
 for a,bb in [((0,0),(0,4)),((0,4),(5,4)),((5,4),(5,0)),((5,0),(0,0))]:
  for k in range(6):
   t=k/6;u=(k+1)/6
   D('Heavy net border',pt(a[0]+(bb[0]-a[0])*t,a[1]+(bb[1]-a[1])*t),pt(a[0]+(bb[0]-a[0])*u,a[1]+(bb[1]-a[1])*u),.008,ROPE,4)
 for i,j in [(0,2),(2,1),(3,3),(5,2)]:
  x,y,z=pt(i,j);o=E('Sea glass float',(x,y-.025,z),(.104,.104,.104),TEAL,2);p.paint(o,'glass','60A9A5')
  T('Float rope binding',(x,y-.025,z),.053,.005,ROPE,10,3,FRONT)
  E('Glass glint',(x-.018,y-.074,z+.016),(.018,.008,.022),'BDDED1')
 for x in [-.464,.464]:
  D('Brass net peg',(x,0,0),(x,-.045,0),.014,BRASS,6)
  D('Hanging net tie',(x,-.043,0),(x,-.043,.10),.006,ROPE,4)

def bottle_shelf():
 B('Dark timber shelf back',(0,-.018,0),(.70,.036,.31),WOOD)
 B('Teal shelf plank',(0,-.112,-.126),(.73,.224,.046),TEAL)
 for x in [-.29,.29]:
  D('Brass shelf brace',(x,-.025,-.145),(x,-.195,-.105),.012,BRASS,6)
  D('Brass shelf stanchion',(x,-.215,-.10),(x,-.215,-.015),.009,BRASS,6)
 D('Bottle retaining rail',(-.30,-.215,-.015),(.30,-.215,-.015),.008,BRASS,6)
 for i,x in enumerate([-.25,-.125,0,.125,.25]):
  h=[.21,.24,.18,.25,.20][i];col=[TEAL,'578E64',CORAL,'438E91','B88739'][i]
  o=L('Harbour bottle',[(0,0),(.032,0),(.037,.018),(.037,h*.66),(.017,h*.82),(.014,h), (0,h)],col,10,(x,-.105,-.103));p.paint(o,'glass',col)
  L('Bottle cork',[(0,0),(.016,0),(.016,.022),(0,.022)],ROPE,8,(x,-.105,h-.108))
  B('Unlettered cream bottle label',(x,-.143,-.103+h*.40),(.040,.002,.055),CREAM,.001)
 for x in [-.32,.32]:D('Shelf fixing',(x,0,.115),(x,-.044,.115),.011,BRASS,6)

def puddle_s():
 # A closed, shallow irregular water lens; canonical puddle swatch gives wet roughness.
 n=28;outline=[]
 for i in range(n):
  a=2*PI*i/n;r=1+.10*math.sin(3*a+.3)+.055*math.cos(5*a)
  outline.append((.34*r*math.cos(a),.19*r*math.sin(a)))
 vv=[(0,0,0),(0,0,.0025)]
 vv += [(x,y,.001) for x,y in outline]+[(x*.94,y*.94,.0025) for x,y in outline]
 ff=[]
 for i in range(n):
  j=(i+1)%n;ff.extend([(0,2+j,2+i),(2+i,2+j,2+n+j,2+n+i),(1,2+n+i,2+n+j)])
 p.paint(mesh('Shallow glossy sea-blue water',vv,ff,'puddle'),'puddle','315B6B')
 # Two broad, broken surface glints remain restrained under warm night light.
 for k,(a0,a1,rr) in enumerate([(.20,1.30,.67),(2.96,3.55,.74)]):
  v=[]
  for i in range(6):
   a=a0+(a1-a0)*i/5
   for d in [-.012,.012]:v.append((.34*(rr+d)*math.cos(a),.19*(rr+d)*math.sin(a),.0029))
  p.paint(b.orient_sheet(mesh('Broken cool water sheen',v,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(5)],'puddle')),'puddle','77979B' if k==0 else '537E8B')

def puddle_l():
 puddle_s()
 for ob in b.PARTS:
  for v in ob.data.vertices:
   x,y=v.co.x,v.co.y
   v.co.x=x*1.86;v.co.y=y*1.58*(1+.12*math.sin(x*7))

def umbrella_stand():
 def brass(o):return p.paint(o,'gold',BRASS)
 brass(L('Weighted brass foot',[(0,0),(.17,0),(.19,.012),(.19,.026),(.16,.044),(0,.044)],BRASS,16))
 L('Navy recessed drip tray',[(0,.045),(.146,.045),(.146,.052),(0,.052)],NAVY,16)
 for z,r in [(.075,.157),(.355,.169)]:brass(T('Rolled brass stand rim',(0,0,z),r,.014,BRASS,16,4))
 for a in [0,2*PI/3,4*PI/3]:
  brass(D('Brass stand upright',(.157*math.cos(a),.157*math.sin(a),.068),(.169*math.cos(a),.169*math.sin(a),.355),.012,BRASS,6))
 for i,(x,y,col,angle) in enumerate([(-.075,-.025,CORAL,-.13),(.067,-.020,TEAL,.11),(0,.073,CREAM,.025)]):
  start=len(b.PARTS);base=Vector((x,y,.065))
  D('Umbrella wooden shaft',(x,y,.07),(x,y,.84),.0075,NAVY,6)
  L('Furled '+['coral','teal','cream'][i]+' cloth',[(0,.105),(.012,.105),(.025,.19),(.043,.31),(.046,.43),(.029,.55),(.017,.65),(0,.66)],col,10,(x,y,.065))
  D('Metal umbrella tip',(x,y,.065),(x,y,.17),.009,BRASS,6)
  T('Navy fastening strap',(x,y,.47),.0465,.0045,NAVY,10,3)
  for k in range(6):
   a=PI-k*PI/6;aa=PI-(k+1)*PI/6
   D('Crook handle',(x+.026+.026*math.cos(a),y,.84+.026*math.sin(a)),(x+.026+.026*math.cos(aa),y,.84+.026*math.sin(aa)),.010,NAVY,5)
  D('Crook return',(x+.052,y,.84),(x+.052,y,.814),.010,NAVY,5)
  rot=Matrix.Rotation(angle,3,'Y')@Matrix.Rotation((i-1)*.055,3,'X')
  for part in b.PARTS[start:]:
   transform=part.matrix_world.copy()
   for v in part.data.vertices:v.co=base+rot@(transform@v.co-base)
   part.matrix_world=Matrix.Identity(4)

LANTERN_CHILDREN=[]
def paper_lanterns():
 global LANTERN_CHILDREN
 LANTERN_CHILDREN=[]
 # Fixed X cross-sections keep string endpoints exactly 0 and -6 in authoring.
 vv=[];segments=16;sides=4
 for i in range(segments+1):
  x=-6*i/segments;z=-.14*math.sin(PI*i/segments)
  for j in range(sides):
   a=j*2*PI/sides;vv.append((x,.004*math.cos(a),z+.004*math.sin(a)))
 ff=[(i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j) for i in range(segments) for j in range(sides)]
 ff += [tuple(reversed(range(sides))),tuple(segments*sides+j for j in range(sides))]
 tint(mesh('Six metre sagging suspension cord',vv,ff,'white'),NAVY)
 for x in [-.015,-5.985]:p.paint(B('Brass attachment tab',(x,0,.010),(.030,.028,.040),BRASS,.003),'gold',BRASS)
 for i in range(6):
  x=-(i+.5);cord=-.14*math.sin(PI*(i+.5)/6);centre=Vector((x,0,cord-.25))
  D('Short lantern hanger',(x,0,cord),(x,0,centre.z+.167),.0055,NAVY,4)
  rootparts=b.PARTS;b.PARTS=[]
  for z in [-.158,.158]:
   o=cyl('Brass paper cap',(x,0,centre.z+z),.061,.024,'gold',8);p.paint(o,'gold',BRASS)
  T('Single teal paper rib',centre,.164,.0035,TEAL,12,3)
  frame,_=p.finish('Lantern_'+str(i+1).zfill(2),centre=False)
  b.PARTS=[]
  # The canonical yellow cell supplies Surface.B emission; no extra material.
  o=L('Glow',[(0,-.17),(.080,-.147),(.140,-.090),(.163,0),(.140,.090),(.080,.147),(0,.17)],CREAM,12,centre)
  p.paint(o,'yellow','FFD66E' if i%2==0 else 'F5AE72')
  glow,_=p.finish('Glow',centre=False)
  glow.parent=frame;glow.location=(0,0,0)
  frame['lantern_index']=i+1;glow['role']='glowing paper; canonical atlas emission'
  LANTERN_CHILDREN.extend([frame,glow]);b.PARTS=rootparts

def export_with_glow_names(ob,path,children):
 # Blender IDs must be unique; FBX sibling groups may each contain exact "Glow".
 from io_scene_fbx import export_fbx_bin
 previous=export_fbx_bin.fbx_name_class
 def name_class(name,cls):return previous(b'Glow' if name.startswith(b'Glow') else name,cls)
 export_fbx_bin.fbx_name_class=name_class
 try:
  b.export(ob,path)
  from bpy_extras.io_utils import axis_conversion
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
  for child in children:child.select_set(True)
  bpy.context.view_layer.objects.active=ob
  # Preserve parent transforms: experimental space baking breaks nested meshes.
  export_fbx_bin.save(b.OP,bpy.context,filepath=str(path),use_selection=True,object_types={'MESH'},global_matrix=axis_conversion(to_forward='-Z',to_up='Y').to_4x4(),axis_up='Y',axis_forward='-Z',bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,use_triangles=True,use_tspace=False,mesh_smooth_type='FACE',path_mode='STRIP',use_custom_props=True)
 finally:export_fbx_bin.fbx_name_class=previous

def reserved_sign():
 # Two thick folded panels, centred at their hinge; front faces Unity +Z.
 def panel(n,w,z0,z1,side,col,advance=0):
  vv=[]
  for depth in [-.0015,.0015]:
   for x,z in [(-w/2,z0),(w/2,z0),(w/2,z1),(-w/2,z1)]:
    vv.append((x,side*(.047*(1-z/.094)+advance)+depth,z))
  o=mesh(n,vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'white')
  p.paint(o,'gold' if col==BRASS else 'white',col)
 for side in [-1,1]:
  panel('Brass folded card',.190,0,.094,side,BRASS)
  panel('Cream inset card face',.168,.009,.083,side,CREAM,.004)
 p.paint(D('Brass fold hinge',(-.095,0,.094),(.095,0,.094),.0038,BRASS,8),'gold',BRASS)
 # A simple navy beret, no words: slanted low crown, flat brim and top stalk.
 def ink(n,points):
  o=mesh(n,[(x,-.047*(1-z/.094)-.0075,z) for x,z in points],[tuple(range(len(points)))],'white');tint(b.orient_sheet(o),NAVY)
 ink('Beret crown',[(-.042,.046),(-.045,.056),(-.034,.065),(-.014,.071),(.012,.069),(.036,.061),(.043,.051),(.030,.045)])
 ink('Beret brim',[(-.043,.040),(.037,.040),(.043,.045),(-.042,.046)])
 ink('Beret stalk',[(-.006,.068),(-.003,.079),(.003,.079),(.005,.068)])

RECIPES={'Wall_LifeRing':life_ring,'Wall_ShipWheel':ship_wheel,'Wall_FishPrint':fish_print,'Wall_NetFloats':net_floats,'Wall_BottleShelf':bottle_shelf,'Puddle_S':puddle_s,'Puddle_L':puddle_l,'UmbrellaStand':umbrella_stand,'PaperLanterns':paper_lanterns,'ReservedSign':reserved_sign}

def placements():
 path=O/'dressing-placement.json'
 if path.exists():return json.loads(path.read_text())
 return {'schema':1,'units':'metres','coordinate_space':'RoomRoot-local Unity Y up; +X screen-left; camera toward -Z','rotation':'yaw_degrees around local +Y; local front +Z','camera':{'source':'RestaurantWorld.cs live Stage1 camera','position':[-.598,13.359,17.088],'euler_degrees':[38,178,0],'vertical_fov_degrees':21.9542},'wall':[],'rain':[],'festival':[],'critic':[],'notes':['Dressing never occupies configurable dining floor. Wall origins are back/contact centre. Rain positions are fixed outdoor perimeter. Critic card attaches to actual selected table, not a fixed floor position.']}

# Coordinates chosen against delivered Stage1V4, not room-table tile assumptions.
PLACEMENT={
 'ReservedSign':('critic',[-1.35,.814,-.71],0,'Demo only: card on rear four-seat table cloth Y0.812, 2mm clearance. Runtime attach to selected critic table at a clear table edge; never instantiate at a fixed dining-floor location.'),
 'PaperLanterns':('festival',[-3,2.50,-2.465],0,'Six-metre string along fixed rear ceiling/wall edge, two end hooks at RoomRoot X-3/+3. Paper stays above rear coping; no supports on configurable dining floor. Ceiling is cut away in source room.'),
 'UmbrellaStand':('rain',[-3.85,.001,2.90],-16,'Brass stand on S1 deck Y0.000 outside door-side wall edge. Three furled umbrellas; keep outside doorway and configurable dining floor.'),
 'Puddle_L':('rain',[-2.55,.001,3.65],8,'Large wet patch on exterior deck beyond entrance mat. Fixed outdoor RestaurantPier planks measured Y0.000; clear of entrance threshold and terrace step.'),
 'Puddle_S':('rain',[2.70,.0255,3.94],-14,'Small wet patch at terrace front edge; paving upper bevel Y0.025, water pivot Y0.0255. Outside configurable room and clear of door.'),
 'Wall_BottleShelf':('wall',[-3.94,.81,1.46],90,'Right-wall shelf between middle and door planters, behind fixed perimeter; no station/door overlap.'),
 'Wall_NetFloats':('wall',[-3.94,.60,-.12],90,'Draped net below right coping between rear and middle planters; stays at wall edge.'),
 'Wall_LifeRing':('wall',[-.36,1.57,-2.465],0,'Back-wall small cork ring above bottle shelf; clear of utensils and existing fish board.'),
 'Wall_ShipWheel':('wall',[-3.94,.61,-1.05],90,'Inner right cutaway wall, below coping and forward of rear planter; no dining tile occupied.'),
 'Wall_FishPrint':('wall',[-3.80,1.43,-2.465],0,'Small framed fish at far-right back-wall pier, clear of menu and lantern.'),
}

def position(ob,entry):
 x,y,z=entry['position'];ob.location=(-x,-z,y);ob.rotation_euler.z=-math.radians(entry['yaw_degrees'])

def room_scene():
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
 try:
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='CUDA';pref.get_devices()
  for d in pref.devices:d.use=d.type=='CUDA'
  if any(d.type=='CUDA' for d in pref.devices):scene.cycles.device='GPU'
 except Exception:pass
 scene.world=bpy.data.worlds.new('Harbour dusk');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.16,.28,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.32
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-1.35
 scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 obs=b.load_fbx(R/'Assets/Resources/Restaurant/Stage1V4.fbx');rm=p.material()
 # Runtime LayoutPlaced removes the old fixed coffee bar. Hide that obsolete
 # station in evidence too; the live starter layout locates coffee in kitchen.
 for ob in obs:
  if ob.name.removeprefix('EXPORT_') in ['CoffeeBar','CoffeeCup']:ob.hide_render=True
 for ob in obs:
  if ob.type=='MESH':
   ob.data.materials.clear();ob.data.materials.append(rm)
   src=ob.data.color_attributes.active_color
   if not ob.data.color_attributes.get('Color'):
    vals=[tuple(d.color) for d in src.data] if src else [];col=ob.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
    for i,d in enumerate(col.data):d.color=vals[i] if vals else (1,1,1,1)
 c.harbour_context(rm,scene)
 for r in json.loads((R/'Assets/Resources/Restaurant/Stage1V4-lighting.json').read_text())['lights']:
  if r['type']!='POINT':continue
  data=bpy.data.lights.new('REVIEW_'+r['name'],'POINT');data.energy=r['blender_power'];data.color=r['linear_rgb'];data.shadow_soft_size=max(.12,r.get('radius_m',.2));o=bpy.data.objects.new(data.name,data);scene.collection.objects.link(o);o.location=r['position_blender_m']
 data=bpy.data.lights.new('REVIEW_RoomBounce','AREA');data.energy=300;data.color=(1,.77,.5);data.size=8;o=bpy.data.objects.new(data.name,data);scene.collection.objects.link(o);o.location=(0,-.5,6)
 bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='PERSP';cam.data.lens_unit='FOV';cam.data.sensor_fit='VERTICAL';cam.data.angle=math.radians(21.9542);cam.data.clip_end=120
 # Exact Unity camera converted to Blender coordinates; local view vectors match yaw178/pitch38.
 cam.location=(.598,-17.088,13.359);forward=Vector((-.0348995*.7880108,.9993908*.7880108,-.6156615));cam.rotation_euler=forward.to_track_quat('-Z','Y').to_euler()
 return scene,cam

def render(rec,entry):
 # Import exported FBX for evidence, so proof includes the delivered axis transforms.
 bpy.ops.wm.read_factory_settings(use_empty=True);obs=b.load_fbx(R/rec['file']);b.MAT=p.material()
 for o in obs:
  if o.type=='MESH':o.data.materials.clear();o.data.materials.append(b.MAT)
 roots=[o for o in obs if not o.parent]
 anchor=bpy.data.objects.new('REVIEW_Placement',None);bpy.context.collection.objects.link(anchor)
 for o in roots:o.parent=anchor
 position(anchor,entry)
 # Include all prior delivered props at their own JSON locations for cumulative room dressing.
 data=placements()
 for group in ['wall','rain','festival','critic']:
  for e in data[group]:
   if e['name']==rec['name']:continue
   if not (R/e['file']).exists():continue
   more=b.load_fbx(R/e['file']);root=bpy.data.objects.new('REVIEW_'+e['name'],None);bpy.context.collection.objects.link(root)
   for o in more:
    if not o.parent:o.parent=root
    if o.type=='MESH':o.data.materials.clear();o.data.materials.append(b.MAT)
   position(root,e)
 scene,cam=room_scene();bpy.context.view_layer.update()
 scene.render.filepath=str(O/'renders'/('props4-'+rec['name']+'-service.png'));bpy.ops.render.render(write_still=True)
 # Wall close angle follows wall normal; inspect right wall from inside, clear of near wall occlusion.
 coords=[o.matrix_world@v.co for o in obs if o.type=='MESH' for v in o.data.vertices]
 lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)]);target=(lo+hi)/2
 scale=max((hi.x-lo.x)*1.6,(hi.y-lo.y)*1.6,(hi.z-lo.z)*2.3,.55)
 if rec['name']=='Restaurant_PaperLanterns':
  target=anchor.location+Vector((-1.5,0,-.25-.14*math.sin(PI*1.5/6)));scale=1.05
 cam.data.type='ORTHO';cam.data.ortho_scale=scale
 yaw=-math.radians(entry['yaw_degrees']);direction=Vector((.24,-.97,.43));direction=Matrix.Rotation(yaw,3,'Z')@direction
 if 'Puddle' in rec['name']:direction=Vector((.20,-.70,1))
 cam.location=target+direction.normalized()*max(3,scale);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(O/'renders'/('props4-'+rec['name']+'-close.png'));bpy.ops.render.render(write_still=True)
 rec['renders']=[str((O/'renders'/('props4-'+rec['name']+'-'+s+'.png')).relative_to(R)).replace('\\','/') for s in ['service','close']]

def save_rec(rec):
 path=O/'props4-manifest.json';rows=json.loads(path.read_text()) if path.exists() else [];path.write_text(json.dumps([r for r in rows if r['name']!=rec['name']]+[rec],indent=2)+'\n')

def main():
 key=sys.argv[sys.argv.index('--')+1];name='Restaurant_'+key
 if '--render-only' in sys.argv:
  rec=next(r for r in json.loads((O/'props4-manifest.json').read_text()) if r['name']==name);entry=next(e for g in ['wall','rain','festival','critic'] for e in placements()[g] if e['name']==name);render(rec,entry);save_rec(rec);return
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;b.PARTS=[];b.MAT=p.material()
 RECIPES[key]();
 if key in ['Wall_LifeRing','Wall_FishPrint']:
  factor=.75 if key=='Wall_LifeRing' else .52
  for part in b.PARTS:
   for v in part.data.vertices:v.co*=factor
   part.location*=factor
 ob,rec=p.finish(name,centre=not key.startswith('Wall_') and key!='PaperLanterns')
 if key.startswith('Wall_'):rec['pivot']='back centre wall contact; local +Z front';ob['pivot']=rec['pivot']
 children=LANTERN_CHILDREN if key=='PaperLanterns' else []
 if children:
  for ch in children:
   if not ch.parent:ch.parent=ob
  bpy.context.view_layer.update();parts=[ob]+children
  coords=[o.matrix_world@v.co for o in parts for v in o.data.vertices]
  lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)])
  for o in parts:o.data.calc_loop_triangles()
  rec.update(tris=sum(len(o.data.loop_triangles) for o in parts),vertices=sum(len(o.data.vertices) for o in parts),size_xyz_blender_m=list(hi-lo),size_xyz_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],pivot='left string attachment; extends local +X exactly6m',children=[o.name for o in children if o.name.startswith('Lantern_')],glow_mesh_count=6,glow_export_name='Glow')
  ob['pivot']=rec['pivot']
 assert rec['tris']<2000,(name,rec['tris'])
 folder='dressing' if key.startswith('Wall_') else 'service';path=b.PACK/folder/(name+'.fbx');path.parent.mkdir(exist_ok=True)
 if not path.parent.with_suffix('.meta').exists():path.parent.with_suffix('.meta').write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
 ob['service_props_task']='SERVICE-PROPS-4'
 if children:export_with_glow_names(ob,path,children)
 else:b.export(ob,path)
 source=O/'blends'/('props4-'+name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False)
 rec.update(file=str(path.relative_to(R)).replace('\\','/'),source=str(source.relative_to(R)).replace('\\','/'),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),triangle_limit_exclusive=2000,material='RestaurantAtlas',render_review='PENDING')
 data=placements();group,pos,yaw,note=PLACEMENT[key];entry=dict(name=name,file=rec['file'],position=pos,yaw_degrees=yaw,scale=1,pivot=rec.get('pivot','bottom centre'),note=note);
 if key=='ReservedSign':entry.update(attach_to='selected_critic_table',surface_clearance_m=.002,table_clear_edge_offset_xz_m=[0,-.23],demo_table='EXPORT_DiningTwo_Cloth_Four',demo_position_only=True)
 data[group]=[e for e in data[group] if e['name']!=name]+[entry];(O/'dressing-placement.json').write_text(json.dumps(data,indent=2)+'\n');save_rec(rec)
 if '--build-only' not in sys.argv:render(rec,entry);save_rec(rec)
 print('PROPS4',name,rec['tris'],flush=True)
if __name__=='__main__':main()

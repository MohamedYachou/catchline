"""JIG-BOAT-1. New authoring geometry only. Blender --background --python build_jig.py."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent; R=HERE.parents[3]; OUT=R/'Art/Models/BoatsV2/JigBoatV1'; OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(HERE.parent));import geometry2 as G
G.PALETTE.update({'M_BandIvory':'F3DEA1','M_SeaTeal':'168F9F'})
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
root=bpy.data.objects.new('Catchline_JigBoatV1',None);bpy.context.scene.collection.objects.link(root);G.ROOT=root
Geo=G.Geo;ring=G.ring
# Same direction and origin as the neighbouring authoring hulls: -Y bow, Z up, deck0.
raw=[(-1.1,2.6),(1.1,2.6),(1.34,2.34),(1.4,1.55),(1.4,0),(1.4,-1.45),(1.38,-1.92),(1.34,-2.13),(.94,-2.3),(.48,-2.65),(0,-2.8),(-.48,-2.65),(-.94,-2.3),(-1.34,-2.13),(-1.38,-1.92),(-1.4,-1.45),(-1.4,0),(-1.4,1.55),(-1.34,2.34)]
plan=[(x*1.65/1.4,(y+2.8)*7/5.4-3.5) for x,y in raw]
def sheer(y):return .345+.22*(max(0,-y)/3.5)**2+.085*(max(0,y)/3.5)**2
def level(t,proud=0):
 f=.72+.28*min(1,t/.48);fy=.85+.15*min(1,t/.48)
 return [(x*f+proud*x/1.65,y*fy,-.62+(sheer(y)+.62)*t) for x,y in plan]
g=Geo();last=level(0)
for t in [.18,.245,.36,.48,.67,1]:
 up=level(t);ring(g,last,up,'M_SafetyOrange' if t==.245 else 'M_HullNavy');last=up
 if t in [.36,.48,.67]:
  lap=level(t,.018);ring(g,up,lap,'M_ClinkerRecess');lip=[(x,y,z+.018) for x,y,z in lap];ring(g,lap,lip,'M_ClinkerRecess');last=lip
g.add(level(0),[tuple(reversed(range(len(plan))))],'M_HullNavy');g.mesh('Hull')
g=Geo();outer=level(1);inner=[(x*.95,y*.985,z) for x,y,z in outer];low=[(x*.95,y*.985,-.025) for x,y in plan];ring(g,outer,inner,'M_WoodHighlight');ring(g,inner,low,'M_DeckWood');g.mesh('InnerBulwark')
g=Geo()
for off,h,w,mat in [(.012,.045,.05,'M_RailIvory'),(-.07,.04,.025,'M_WoodHighlight')]:
 a=[(x*(1+w/1.65),y,sheer(y)+off) for x,y in plan];b=[(x,y,z+h) for x,y,z in a];c=[(x*.96,y*.99,z) for x,y,z in b];d=[(x,y,z-h) for x,y,z in c]
 for aa,bb in [(a,b),(b,c),(c,d),(d,a)]:ring(g,aa,bb,mat)
g.mesh('SweptCapAndRubber')
g=Geo();g.beam((0,3.22,-.66),(0,-3.05,-.66),.10,.13,'M_WoodRecess');g.beam((0,-3.05,-.66),(0,-3.52,.59),.10,.10,'M_WoodRecess');g.mesh('KeelAndRakedStem')
# Broad deck planks clipped against a slightly inset convex plan; no deck-crossing gaps.
def clip(poly,axis,v,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]>=v if greater else a[axis]<=v;ib=b[axis]>=v if greater else b[axis]<=v
  if ia:out.append(a)
  if ia!=ib:
   t=(v-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[j]+(b[j]-a[j])*t for j in range(2)))
 return out
p=[(x*.948,y*.983) for x,y in plan];g=Geo()
for i in range(12):
 a=-1.57+i*3.14/12;b=a+3.14/12;q=clip(clip(p,0,a,True),0,b,False)
 if len(q)<3:continue
 g.add([(x,y,-.045) for x,y in q]+[(x,y,0) for x,y in q],[tuple(reversed(range(len(q)))),tuple(range(len(q),2*len(q)))]+[(j,(j+1)%len(q),(j+1)%len(q)+len(q),j+len(q)) for j in range(len(q))],'M_WoodHighlight' if i%4==0 else 'M_DeckWood')
g.mesh('PlankDeck')
def box(name,c,s,m,bevel=.015):
 g=Geo();g.box(c,s,m);return g.mesh(name,bevel=bevel)
def beam(g,a,b,w=.04,m='M_Steel'):g.beam(a,b,w,w,m)
def cyl(g,a,b,r,m,n=12,r2=None):
 a,b=Vector(a),Vector(b);u=(b-a).normalized();v=u.cross(Vector((0,0,1))).normalized()
 if v.length<.1:v=Vector((1,0,0))
 w=u.cross(v).normalized();r2=r if r2 is None else r2
 vs=[tuple(p+(v*math.cos(i*2*math.pi/n)+w*math.sin(i*2*math.pi/n))*rr) for p,rr in [(a,r),(b,r2)] for i in range(n)]
 g.add(vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
# Enclosed forward cabin leaves walkable side passages; all panels meet solid body.
box('WheelhouseBody',(0,-1.95,.66),(1.30,1.48,1.32),'M_RailIvory',.045)
box('WheelhouseRoof',(0,-1.95,1.37),(1.52,1.72,.12),'M_RailIvory',.04)
box('RoofTimberLip',(0,-1.95,1.302),(1.47,1.67,.035),'M_WoodHighlight',.008)
# Opaque navy glazing is house style, no fragile transparency/interior.
for x in [-.335,.335]:box('FrontWindow'+str(x),(x,-2.701,.98),(.53,.025,.48),'M_HullNavy',.025)
for x in [-.661,.661]:
 for y in [-2.35,-1.65]:box('SideWindow'+str(x)+str(y),(x,y,.98),(.025,.55,.48),'M_HullNavy',.025)
box('CabinAftDoor',(0,-1.202,.56),(.65,.024,1.08),'M_DeckWood',.02)
box('CabinDoorGlass',(0,-1.22,.90),(.43,.028,.36),'M_HullNavy',.018)
box('DoorLatch',(.23,-1.176,.53),(.06,.04,.10),'M_Steel',.008)
g=Geo();cyl(g,(.45,-2.25,1.45),(.45,-2.25,1.56),.045,'M_HullNavy');cyl(g,(.45,-2.25,1.56),(.45,-2.25,1.65),.055,'M_SafetyOrange');cyl(g,(-.40,-1.75,1.43),(-.40,-1.75,1.95),.012,'M_Steel',8);g.mesh('CabinBeaconAerial')
# Life ring on port cabin, torus normal X, four ivory binding segments.
g=Geo();N=24;K=6;vs=[]
for i in range(N):
 for j in range(K):
  t=i*2*math.pi/N;u=j*2*math.pi/K;rr=.215+.052*math.cos(u);vs.append((-.72+.052*math.sin(u),-1.95+rr*math.cos(t),.43+rr*math.sin(t)))
for i in range(N):
 for j in range(K):g.add([vs[i*K+j],vs[((i+1)%N)*K+j],vs[((i+1)%N)*K+(j+1)%K],vs[i*K+(j+1)%K]],[(0,1,2,3)],'M_RailIvory' if i%6==0 else 'M_SafetyOrange')
g.mesh('CabinLifeRing')
# Lamps run above starboard rail; bases exactly on the walking surface, not floating.
mastx=1.35;front=-1.02;aft=2.94;top=1.92
g=Geo()
for y in [front,aft]:
 g.box((mastx,y,.055),(.22,.23,.11),'M_HullNavy');cyl(g,(mastx,y,.11),(mastx,y,top),.045,'M_HullNavy',10);cyl(g,(mastx,y,top-.10),(mastx,y,top+.025),.065,'M_Steel',10)
g.mesh('TwoShortLampMasts')
def wire(t):return (mastx,front+(aft-front)*t,top-.29*4*t*(1-t))
g=Geo()
for i in range(24):cyl(g,wire(i/24),wire((i+1)/24),.012,'M_Rubber',6)
g.mesh('LampCable')
for i in range(8):
 t=(i+.5)/8;x,y,z=wire(t);g=Geo();cyl(g,(x,y,z+.01),(x,y,z-.105),.015,'M_Rubber',6);cyl(g,(x,y,z-.085),(x,y,z-.145),.042,'M_HullNavy',8)
 cyl(g,(x,y,z-.145),(x,y,z-.245),.042,'M_BandIvory',8,r2=.065);cyl(g,(x,y,z-.245),(x,y,z-.33),.065,'M_BandIvory',8,r2=.035);cyl(g,(x,y,z-.33),(x,y,z-.35),.035,'M_WoodHighlight',8,r2=.005)
 g.mesh('SquidLamp_%02d'%(i+1))
# Three tiny jig reels safely inside port bulwark, poles/lines stay off central floor.
for i,y in enumerate([-.15,1.05,2.22],1):
 g=Geo();x=-1.43;g.box((x,y,.025),(.20,.26,.05),'M_HullNavy');beam(g,(x,y,.04),(x,y,.62),.055)
 for xx,r,m in [(x-.10,.15,'M_HullNavy'),(x+.10,.15,'M_HullNavy')]:cyl(g,(xx-.025,y,.65),(xx+.025,y,.65),r,m)
 cyl(g,(x-.08,y,.65),(x+.08,y,.65),.11,'M_SafetyOrange');cyl(g,(x-.08,y,.65),(x+.08,y,.65),.07,'M_Rope')
 beam(g,(x+.14,y,.65),(x+.14,y+.18,.65),.025);cyl(g,(x+.10,y+.18,.65),(x+.19,y+.18,.65),.025,'M_WoodRecess',8)
 beam(g,(x,y,.60),(-1.67,y-.12,.81),.022,'M_HullNavy');cyl(g,(-1.67,y-.12,.81),(-1.67,y-.12,-.35),.006,'M_Rope',6)
 g.mesh('JigReel_%02d'%i)
# Small sorting tray on aft starboard rail; centre corridor remains1.6m wide.
g=Geo();x=1.04;y=2.13
for dx in [-.28,.28]:
 for dy in [-.29,.29]:beam(g,(x+dx,y+dy,0),(x+dx,y+dy,.67),.042)
g.box((x,y,.68),(.72,.80,.055),'M_Steel')
for c,s in [((x-.35,y,.77),(.045,.80,.17)),((x+.35,y,.77),(.045,.80,.17)),((x,y-.38,.77),(.72,.045,.17)),((x,y+.38,.77),(.72,.045,.17))]:g.box(c,s,'M_Steel')
g.box((x,y,.714),(.62,.69,.012),'M_SeaTeal');g.mesh('SortingTray',bevel=.01)
# Rail-side storage and a flush centre hatch, no net processing machinery.
box('SternLocker',(-.65,2.97,.21),(.80,.43,.42),'M_RailIvory',.025);box('SternLockerLid',(-.65,2.97,.44),(.85,.47,.06),'M_SeaTeal',.02)
box('FlushHoldHatch',(0,.55,.008),(.68,.95,.016),'M_WoodRecess',.006);box('HoldHatchLid',(0,.55,.018),(.63,.90,.012),'M_DeckWood',.005);box('HatchHandle',(0,.55,.027),(.18,.055,.006),'M_Steel',.002)
# External propulsion below stern, no axle crossing deck.
box('OutboardMotor',(0,3.46,.12),(.44,.38,.50),'M_HullNavy',.05);box('MotorOrangeCap',(0,3.46,.39),(.45,.40,.055),'M_SafetyOrange',.018)
g=Geo();beam(g,(0,3.46,.1),(0,3.48,-.67),.12,'M_Rubber');cyl(g,(0,3.35,-.61),(0,3.61,-.61),.055,'M_Steel');g.box((0,3.63,-.61),(.39,.035,.065),'M_Steel');g.mesh('EngineLegPropeller')
# Cleats and six fenders, mounted to hull rather than hovering.
g=Geo()
for x,y in [(-1.45,.65),(-1.40,2.85),(1.50,.15),(1.40,2.85),(-.90,-2.70),(.90,-2.70)]:
 z=sheer(y);cyl(g,(x,y,z+.04),(x,y,z+.12),.035,'M_Steel',8);beam(g,(x-.09,y,z+.13),(x+.09,y,z+.13),.035)
g.mesh('DeckCleats')
g=Geo()
for x,y in [(-1.66,.6),(-1.58,2.50),(1.66,.6),(1.58,2.50),(-1.62,-1.35),(1.62,-1.35)]:
 cyl(g,(x,y,sheer(y)+.01),(x,y,-.06),.013,'M_Rope',6);cyl(g,(x,y,.05),(x,y,-.24),.070,'M_RailIvory',10,r2=.06)
g.mesh('SafetyFenders')
bpy.context.view_layer.update();obs=list(bpy.context.scene.objects);stats=G.stats(obs);tri=sum(d['triangles'] for d in stats.values());assert tri<=13000,tri
for o in obs:
 if o.type=='MESH':assert all(p.area>1e-10 for p in o.data.polygons),(o.name,'degenerate')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(OUT/'JigBoatV1.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'JigBoatV1.blend'))
(OUT/'build-metrics.json').write_text(json.dumps({'triangles':tri,'triangle_cap':13000,'objects':stats,'hull_nominal_length_m':7,'hull_nominal_beam_m':3.3,'deck_z_m':0,'clear_centre_corridor_x_m':[-.8,.65],'lamp_count':8,'reel_count':3,'sockets_authored':False,'source_axis':'X right, -Y bow, Z up','materials':G.PALETTE},indent=2))
print('JIG BUILD PASS',tri,flush=True)

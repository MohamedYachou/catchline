"""JIG-BOAT-1. New authoring geometry only. Blender --background --python build_jig.py."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent; R=HERE.parents[3]; OUT=R/'Art/Models/BoatsV2/Tier6V1'; OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(HERE.parent));import geometry2 as G
G.PALETTE.update({'M_BandIvory':'F3DEA1','M_SeaTeal':'168F9F'})
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
root=bpy.data.objects.new('Catchline_Tier6V1',None);bpy.context.scene.collection.objects.link(root);G.ROOT=root
Geo=G.Geo;ring=G.ring
# Same direction and origin as the neighbouring authoring hulls: -Y bow, Z up, deck0.
raw=[(-1.1,2.6),(1.1,2.6),(1.34,2.34),(1.4,1.55),(1.4,0),(1.4,-1.45),(1.38,-1.92),(1.34,-2.13),(.94,-2.3),(.48,-2.65),(0,-2.8),(-.48,-2.65),(-.94,-2.3),(-1.34,-2.13),(-1.38,-1.92),(-1.4,-1.45),(-1.4,0),(-1.4,1.55),(-1.34,2.34)]
plan=[(x*2.5/1.4,(y+2.8)*10/5.4-5) for x,y in raw]
def sheer(y):return .48+.30*(max(0,-y)/5)**2+.12*(max(0,y)/5)**2
def level(t,proud=0):
 f=.72+.28*min(1,t/.48);fy=.85+.15*min(1,t/.48)
 return [(x*f+proud*x/2.5,y*fy,-.82+(sheer(y)+.82)*t) for x,y in plan]
g=Geo();last=level(0)
for t in [.18,.245,.36,.48,.67,1]:
 up=level(t);ring(g,last,up,'M_SafetyOrange' if t==.245 else 'M_HullNavy');last=up
 if t in [.36,.48,.67]:
  lap=level(t,.018);ring(g,up,lap,'M_ClinkerRecess');lip=[(x,y,z+.018) for x,y,z in lap];ring(g,lap,lip,'M_ClinkerRecess');last=lip
g.add(level(0),[tuple(reversed(range(len(plan))))],'M_HullNavy');g.mesh('Hull')
g=Geo();outer=level(1);inner=[(x*.95,y*.985,z) for x,y,z in outer];low=[(x*.95,y*.985,-.025) for x,y in plan];ring(g,outer,inner,'M_WoodHighlight');ring(g,inner,low,'M_DeckWood');g.mesh('InnerBulwark')
g=Geo()
for off,h,w,mat in [(.012,.045,.05,'M_RailIvory'),(-.07,.04,.025,'M_WoodHighlight')]:
 a=[(x*(1+w/2.5),y,sheer(y)+off) for x,y in plan];b=[(x,y,z+h) for x,y,z in a];c=[(x*.96,y*.99,z) for x,y,z in b];d=[(x,y,z-h) for x,y,z in c]
 for aa,bb in [(a,b),(b,c),(c,d),(d,a)]:ring(g,aa,bb,mat)
g.mesh('SweptCapAndRubber')
g=Geo();g.beam((0,4.6,-.86),(0,-4.5,-.86),.10,.13,'M_WoodRecess');g.beam((0,-4.5,-.86),(0,-5.03,.80),.10,.10,'M_WoodRecess');g.mesh('KeelAndRakedStem')
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
for i in range(18):
 a=-2.37+i*4.74/18;b=a+4.74/18;q=clip(clip(p,0,a,True),0,b,False)
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
# Selected C: enclosed forward helm, compact cabin-only roof; all work stations open.
box('WheelhouseBody',(0,-3.05,.84),(1.70,2.0,1.68),'M_RailIvory',.045)
box('WheelhouseRoof',(0,-3.75,1.77),(1.88,2.20,.14),'M_HullNavy',.035)
box('RoofTimberLip',(0,-3.75,1.685),(1.84,2.16,.04),'M_WoodHighlight',.008)
for x in [-.43,.43]:box('FrontWindow'+str(x),(x,-4.065,1.18),(.68,.026,.60),'M_HullBlue',.025)
for x in [-.866,.866]:
 for y in [-3.65,-2.62]:box('SideWindow'+str(x)+str(y),(x,y,1.18),(.026,.72,.60),'M_HullBlue',.025)
box('CabinAftDoor',(0,-2.037,.69),(.68,.026,1.34),'M_DeckWood',.018)
box('CabinDoorGlass',(0,-2.017,1.15),(.46,.026,.40),'M_HullNavy',.015)
box('DoorLatch',(.24,-1.99,.68),(.06,.04,.10),'M_Steel',.006)
g=Geo()
for x in [-.82,.82]:cyl(g,(x,-2.79,.08),(x,-2.79,1.70),.022,'M_Steel',8)
g.mesh('ShelterRoofAftPosts')
g=Geo();cyl(g,(.55,-3.4,1.84),(.55,-3.4,2.05),.06,'M_HullNavy',8);cyl(g,(.55,-3.4,2.05),(.55,-3.4,2.19),.065,'M_SafetyOrange',8);cyl(g,(-.5,-2.9,1.84),(-.5,-2.9,2.65),.015,'M_Steel',8);g.mesh('CabinBeaconAerial')
# Compact roof radar, forward of the beacon; same palette and no deck roof.
box('CabinRadarBase',(0,-4.06,1.94),(.17,.17,.20),'M_RailIvory',.01)
box('CabinRadarBar',(0,-4.06,2.08),(.70,.14,.10),'M_RailIvory',.015)
g=Geo();N=24;K=6
for i in range(N):
 for j in range(K):
  vs=[]
  for ii,jj in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]:
   t=ii*2*math.pi/N;u=jj*2*math.pi/K;rr=.24+.055*math.cos(u);vs.append((-.91+.055*math.sin(u),-3.08+rr*math.cos(t),.60+rr*math.sin(t)))
  g.add(vs,[(0,1,2,3)],'M_RailIvory' if i%6==0 else 'M_SafetyOrange')
g.mesh('CabinLifeRing')
from mathutils import Matrix
inventory=json.loads((HERE/'station-inventory.json').read_text())
provenance=[]
def bring(source,names,xf):
 path=R/'Art/Models/BoatsV2'/source/(source+'.blend')
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=[n for n in names if n in src.objects]
 loaded={o.name:o for o in dst.objects if o}
 for o in loaded.values():
  if not o.users_collection:bpy.context.scene.collection.objects.link(o)
 bpy.context.view_layer.update()
 saved={o:o.matrix_world.copy() for o in loaded.values()}
 def depth(o):return 1+depth(o.parent) if o.parent in saved else 0
 for o in sorted(loaded.values(),key=depth):
  oldparent=o.parent
  if oldparent not in saved:o.parent=root
  o.matrix_world=xf@saved[o]
  bpy.context.view_layer.update()
 bpy.context.view_layer.update()
 for o in loaded.values():
  if o.type=='MESH':
   o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY');bm.to_mesh(o.data);bm.free();o.data.update()
 provenance.append({'source':source,'objects':list(loaded),'source_sha256':inventory[source]['sha256'],'transform':[list(r) for r in xf]})
 return loaded
def T(x,y,z=0):return Matrix.Translation((x,y,z))
def rot(a):return Matrix.Rotation(math.radians(a),4,'Z')
def family(source,name):
 data={v['name']:v for v in inventory[source]['objects']};out=[name]
 for n,v in data.items():
  p=v['parent']
  while p:
   if p==name:out.append(n);break
   p=data[p]['parent'] if p in data else None
 return out
S5='Tier5DeepLines103'
# Rotate worktables/coolers lengthwise along rails; same semantic hierarchy.
bring(S5,family(S5,'PrepStation'),T(-2.5,-1.15)@rot(-90))
bring(S5,family(S5,'RawIceCoolers'),T(1.77,-.75)@rot(90))
bring(S5,family(S5,'PreparedHold'),T(-4.15,.35)@rot(-90))
# State alternative RawBuckets becomes actual separate stowed buckets, not duplicate coolers.
def empty(n,pos,parent=root):
 o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);o.parent=parent;o.matrix_world=Matrix.Translation(pos);return o
raw=empty('RawBuckets',(0,0,0))
for i,y in enumerate([-1.62,-.9],1):
 g=Geo();x=2.10;cyl(g,(x,y,.04),(x,y,.32),.14,'M_HullBlue',10,r2=.17);cyl(g,(x,y,.32),(x,y,.35),.18,'M_Steel',10);o=g.mesh('RawBucketStow_%d'%i);o.parent=raw
# DeepLine modules: preserve rig/reel-pivot local articulation and names.
deep=empty('DeepLineModule',(0,0,0))
for i,dy in [(1,.7),(2,.85)]:
 names=family(S5,'DeepLineRig_%d'%i)+['DeepLineBase_%d'%i,'DeepLineTip_%d'%i,'DeepLineWorker_%d'%i]
 loaded=bring(S5,names,T(.35,dy))
 for n,o in loaded.items():
  if o.parent==root:
   w=o.matrix_world.copy();o.parent=deep;o.matrix_world=w
bring(S5,family(S5,'NetModule1'),T(-.30,.38))
bring(S5,family(S5,'NetModule2'),T(.24,2.15))
# Four rod holders keep per-rail sockets and optional module stable.
optional=empty('OptionalRodModule',(0,0,0))
for i,(x,y) in enumerate([(-2.25,-.30),(2.25,-.30),(2.25,1.85),(-2.25,2.75)],1):
 old=next(v for v in inventory[S5]['objects'] if v['name']=='RodHolder_%d'%i)['position']
 loaded=bring(S5,['RodHolder_%d'%i,'RodSocket_%d'%i],T(x-old[0],y-old[1]))
 for o in loaded.values():
  if i>=3:w=o.matrix_world.copy();o.parent=optional;o.matrix_world=w
# Exact companion station/access names, with worker feet on deck0.
anchors={'BuoyAccess_1':(-1.35,-3.0,0),'BuoyAccess_2':(1.35,-3.0,0),'BuoyAnchor_1':(-3.05,-3.0,-.3),'BuoyAnchor_2':(3.05,-3.0,-.3),
'NetWorker_1':(.65,3.70,0),'NetWorker_2':(1.35,3.70,0),
'PrepWorker_1':(-.75,-.72,0),'PrepWorker_2':(-.75,-1.58,0),'PrepSurface':(-1.6,-1.15,.72),'PrepInput':(1.6,-.75,.4),
'HoldWorker':(-.75,.35,0),'RawWorker':(.75,-.75,0),'PreparedOutput':(-1.6,.35,.5),'ServiceAccess_1':(.65,-1.85,0),'ServiceAccess_2':(-.65,-1.85,0),
'RawInput_1':(1.6,-1.18,.4),'RawInput_2':(1.6,-.32,.4),'PreparedOutput_1':(-1.6,.78,.5),'PreparedOutput_2':(-1.6,-.08,.5)}
for n,p in anchors.items():empty(n,p)
# Both buoy stations visibly carry compact winch/booms, not just empty anchors.
for i,sgn in enumerate([-1,1],1):
 x=sgn*2.08;y=-3.0;g=Geo();g.box((x,y,.06),(.27,.28,.12),'M_HullNavy');cyl(g,(x,y,.10),(x,y,.85),.05,'M_Steel',10)
 cyl(g,(x-.16,y,.74),(x+.16,y,.74),.15,'M_HullNavy',10);cyl(g,(x-.10,y,.74),(x+.10,y,.74),.11,'M_SafetyOrange',10)
 beam(g,(x,y,.8),(sgn*3.05,y,1.35),.055);cyl(g,(sgn*3.05,y,1.35),(sgn*3.05,y,-.30),.008,'M_Rope',6);g.mesh('BuoyRig_%d'%i)
# Jig equipment retained, moved to port; warm bulb material from accepted Jig lights export.
SJ='JigBoatV1'
for i,y in enumerate([1.55,2.70,3.80],1):
 old=next(v for v in inventory[SJ]['objects'] if v['name']=='JigReel_%02d'%i)['bounds'];cy=(old[0][1]+old[1][1])/2
 # original mesh geometry world x=-1.43; offset rail to-2.14.
 bring(SJ,['JigReel_%02d'%i],T(-.71,y-[-.15,1.05,2.22][i-1]))
 empty('JigWorker_%d'%i,(-1.35,min(y,3.45),0))
# Lamps translated to port; long spread from-0.2 to4.2.
lamps=['TwoShortLampMasts','LampCable']+['SquidLamp_%02d'%i for i in range(1,9)]
xf=T(-3.49,.2) # original mastx1.35 -> -2.14, y-1.02..2.94 ->-.82..3.14
bring(SJ,lamps,xf)
bring(SJ,['SortingTray'],T(-2.70,2.15));empty('SortingWorker',(-.78,3.65,0))
# Flush hold names inherited from Compact, deck stays uninterrupted.
fh=box('FishHold',(0,1.1,-.045),(.68,1.1,.07),'M_WoodRecess',.005)
box('HoldLid',(0,1.1,.005),(.64,1.05,.01),'M_DeckWood',.004)
g=Geo()
for y in [.76,1.44]:g.box((.26,y,.015),(.06,.13,.012),'M_Steel')
g.mesh('HoldRimHinges')
# Move enclosed cabin forward to leave a full cross-deck route behind it.
for o in list(bpy.context.scene.objects):
 if o.name.startswith(('WheelhouseBody','FrontWindow','SideWindow','CabinAftDoor','CabinDoorGlass','DoorLatch','CabinBeaconAerial','CabinLifeRing')):o.location.y-=.70
# Ten reachable crew capacity points, additional to named task workers.
crew=[(-.65,-1.85),(.65,-1.85),(-.65,-.1),(.65,-.1),(-.65,1.65),(.65,1.65),(-.65,3.1),(.65,3.1),(0,.65),(0,2.4)]
for i,(x,y) in enumerate(crew,1):empty('CrewStand_%d'%i,(x,y,0))
# Railing around broad aft deck, no crossbar across worker route.
g=Geo()
for x in [-2.29,2.29]:
 for y in [-1.8,-.15,1.5,3.1,4.35]:cyl(g,(x,y,sheer(y)),(x,y,.98),.022,'M_Steel',8)
 for a,b in [(-1.8,-.15),(-.15,1.5),(1.5,3.1),(3.1,4.35)]:cyl(g,(x,a,.98),(x,b,.98),.023,'M_Steel',8)
g.mesh('SafetyRail')
box('OutboardMotor',(0,4.91,.12),(.50,.40,.62),'M_HullNavy',.04)
box('MotorOrangeCap',(0,4.91,.45),(.52,.42,.06),'M_SafetyOrange',.015)
g=Geo();beam(g,(0,4.91,.1),(0,4.94,-.82),.14,'M_Rubber');cyl(g,(0,4.8,-.76),(0,5.15,-.76),.06,'M_Steel',10);g.box((0,5.16,-.76),(.44,.035,.08),'M_Steel');g.mesh('EngineLegPropeller')
g=Geo()
for x,y in [(-2.48,-.4),(2.48,-.4),(-2.45,2.8),(2.45,2.8),(-2.13,-3.5),(2.13,-3.5)]:
 cyl(g,(x,y,.56),(x,y,-.12),.012,'M_Rope',6);cyl(g,(x,y,.12),(x,y,-.30),.085,'M_RailIvory',10)
g.mesh('SafetyFenders')
bpy.context.view_layer.update()
obs=list(bpy.context.scene.objects);stats=G.stats(obs);tri=sum(d['triangles'] for d in stats.values());assert tri<=18000,tri
for o in obs:
 if o.type=='MESH':assert all(p.area>1e-10 for p in o.data.polygons),(o.name,'degenerate')
# Connected passage boxes with polygon-level clearance, recorded and checked independently after export.
walk=[{'name':'MainSpine','min':[-.45,-2.60,.045],'max':[.45,4.10,1.65]},
{'name':'PortCabinPass','min':[-1.70,-3.95,.045],'max':[-.98,-1.90,1.65]},
{'name':'StarboardCabinPass','min':[.98,-3.95,.045],'max':[1.70,-1.90,1.65]},
{'name':'CabinCrossAft','min':[-1.70,-2.60,.045],'max':[1.70,-1.90,1.65]}]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(OUT/'Tier6V1.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Tier6V1.blend'))
(OUT/'build-metrics.json').write_text(json.dumps({'triangles':tri,'triangle_cap':18000,'objects':stats,'provenance':provenance,'hull_nominal_length_m':10,'hull_nominal_beam_m':5,'deck_z_m':0,'walkway_boxes':walk,'crew_capacity':10,'source_axis':'X right, -Y bow, Z up'},indent=2))
print('TIER6 BUILD PASS',tri,len(obs),flush=True)

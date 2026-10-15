"""Task08 exact day-boat deck and modular 1m-grid stations. Blender5.2."""
import bpy,math,json,sys,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('world',Path(__file__).with_name('build_world_polish.py'));W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)
K=W.K;B=W.B;G=W.G;part=W.part;box=W.box;ring=W.ring;lathe=W.lathe
NAVY=W.NAVY;WOOD=W.WOOD;IVORY=W.IVORY;STEEL=W.STEEL;TEAL=W.TEAL;ORANGE=W.ORANGE;ROPE=W.ROPE;DARK=W.DARK;BLUE=W.BLUE
ROOT=W.ROOT;OUT=ROOT/'Art/Models/DayBoatKit'
def boat():
 outline=[(-2.9,5.5),(2.9,5.5),(2.9,-5),(1.8,-6.05),(0,-6.5),(-1.8,-6.05),(-2.9,-5)]
 N=len(outline);g=G();levels=[(.72,.93,-1.1),(.92,.98,-.32),(1,1,.60),(.955,.985,.60),(.87,.96,-.75)]
 verts=[(x*sx,y*sy,z) for sx,sy,z in levels for x,y in outline]
 for j in range(len(levels)-1):g.add(verts[j*N:(j+2)*N],[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],NAVY if j<2 else WOOD)
 g.add(verts[:N],[tuple(reversed(range(N)))],NAVY);g.add(verts[-N:],[tuple(range(N))],WOOD);part('Hull',g)
 stripe=G();v=[(x*sx,y*sy,z) for sx,sy,z in ((.90,.978,-.40),(.94,.983,-.25)) for x,y in outline]
 stripe.add(v,[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],ORANGE);part('WaterlineStripe',stripe)
 g=G()
 for i in range(20):box(g,(-2.375+i*.25,0,-.025),(.25,10,.05),WOOD if i%4 else 'M_WoodHighlight',.003)
 part('PlankDeck',g)
 # Authoritative cabin bounds x[-1.5,1.5], y[-5,-3].
 g=G();box(g,(0,-4,.825),(3,2,1.65),IVORY,.035);part('WheelhouseBody',g)
 g=G();box(g,(0,-4,1.70),(3.18,2.16,.10),NAVY,.025)
 for x in (-1.12,0,1.12):box(g,(x,-5.023,1.12),(.83,.045,.58),BLUE,.015)
 for x in (-1.52,1.52):
  for y in (-4.55,-3.53):box(g,(x,y,1.10),(.045,.72,.60),BLUE,.015)
 box(g,(0,-2.98,.70),(.65,.045,1.4),NAVY,.02);box(g,(0,-2.949,1.04),(.45,.024,.50),BLUE,.01)
 box(g,(.22,-2.925,.62),(.055,.025,.09),STEEL,.005)
 for x in (-1.37,-.66,.66,1.37):g.beam((x,-5.052,.79),(x,-5.052,1.46),.04,.04,IVORY)
 g.beam((0,-4,1.75),(0,-4,2.7),.065,.065,STEEL)
 box(g,(0,-4,2.55),(.85,.20,.10),IVORY,.025);g.ellipsoid((0,-4,2.76),(.09,.09,.09),12,5,ORANGE)
 part('RoofWindowsDoorMastRadar',g)
 rail=G();path=[(-2.82,5.35),(2.82,5.35),(2.82,-4.98),(1.7,-5.95),(0,-6.3),(-1.7,-5.95),(-2.82,-4.98),(-2.82,2.5),(-2.82,4.0)]
 # Last side section between2.5 and4.0 is the hauler gap.
 for i,p in enumerate(path):
  q=path[(i+1)%len(path)]
  if i==7:continue
  rail.beam((p[0],p[1],.66),(q[0],q[1],.66),.09,.075,IVORY,.01)
  dist=math.dist(p,q);steps=max(1,math.ceil(dist/1.4))
  for j in range(steps):
   t=j/steps;x=p[0]+(q[0]-p[0])*t;y=p[1]+(q[1]-p[1])*t
   rail.beam((x,y,.03),(x,y,.66),.055,.055,IVORY,.008)
 part('Rails',rail)
 for i,(x,y) in enumerate([(-2.75,1.75),(-2.75,0),(-2.75,-2),(2.75,3.5),(2.75,0),(2.75,-2)],1):
  g=G();ring(g,.064,.016,.58,.75,STEEL,(x,y),12);part('RodSocket_'+str(i),g,(x,y,.58))
 K.NOTES.append('Exact deck X[-2.5,2.5],sourceY[-5,5],topZ=0;UnityZ[-5,5]. Cabin X[-1.5,1.5],UnityZ[3,5],3acrossx2fore-aft,rows8/9 columns1/2/3. Port hauler gap UnityZ[-4,-2.5]. 6 sockets are rigid attachment origins. Radar/mast static.')
def station(n):
 g=G()
 if n=='NetDrum':
  for x in (-.83,.83):box(g,(x,0,.37),(.12,.72,.74),NAVY,.018)
  box(g,(0,0,.055),(1.85,.85,.11),NAVY,.02);part('Frame',g);g=G()
  g.tube([(-.74,0,.69),(.74,0,.69)],[.30,.30],20,TEAL)
  for x in (-.72,.72):g.tube([(x-.03,0,.69),(x+.03,0,.69)],[.37,.37],20,STEEL)
  for i in range(11):
   a=math.tau*i/11;g.beam((-.68,.31*math.cos(a),.69+.31*math.sin(a)),(.68,.31*math.cos(a),.69+.31*math.sin(a)),.023,.023,ROPE)
  part('Drum',g,(0,0,.69));return
 if n=='PowerHauler':
  box(g,(0,0,.045),(.75,.75,.09),NAVY,.015);g.beam((0,0,.08),(0,0,.98),.14,.14,ORANGE,.02)
  g.beam((0,0,.95),(0,-.25,1.16),.12,.12,ORANGE,.015);part('Frame',g);g=G()
  g.tube([(-.075,-.25,1.16),(.075,-.25,1.16)],[.21,.21],20,DARK)
  for x in (-.08,.08):g.tube([(x-.01,-.25,1.16),(x+.01,-.25,1.16)],[.24,.24],20,STEEL)
  part('Sheave',g,(0,-.25,1.16));return
 if n.startswith('Conveyor'):
  for x in (-.34,.34):
   for y in (-.34,.34):g.beam((x,y,0),(x,y,.44),.06,.06,NAVY)
  box(g,(0,0,.44),(.90,.90,.08),STEEL,.012);part('Frame',g);g=G()
  if n=='Conveyor_Straight':
   box(g,(0,0,.50),(.68,.88,.04),DARK,.008)
   for i in range(10):box(g,(0,-.40+i*.088,.526),(.68,.012,.012),TEAL,.002)
  else:
   # Broad curved travel band, geometry ridges rotate with Belt as a group.
   verts=[]
   for r in (.13,.72):
    for i in range(17):a=i*math.pi/32;verts.append((-.40+r*math.cos(a),-.40+r*math.sin(a),.51))
   g.add(verts,[(i,i+1,18+i,17+i) for i in range(16)],DARK)
   for i in range(11):
    a=i*math.pi/20;g.beam((-.40+.13*math.cos(a),-.40+.13*math.sin(a),.52),(-.40+.72*math.cos(a),-.40+.72*math.sin(a),.52),.014,.014,TEAL)
  part('Belt',g,(0,0,.50) if n=='Conveyor_Straight' else (-.40,-.40,.50));K.NOTES.append('UV-less ridged Belt. Recycle/translate Straight ridges or rotate Corner Belt about centre path in consumer; no texture scrolling baked.');return
 if n=='SortingChute':
  for x in (-.83,.83):
   for y in (-.32,.32):g.beam((x,y,0),(x,y,.55),.055,.055,NAVY)
  box(g,(0,0,.55),(1.85,.82,.065),STEEL,.012)
  for x in (-.45,.45):a=G();a.rectangle_ring(.73,.62,.035,.58,.73,.02,TEAL);g.merge(a,(x,0,0));box(g,(x,0,.59),(.73,.62,.025),TEAL,.005)
  g.beam((-.92,-.37,.65),(.92,-.37,.65),.025,.025,STEEL)
  # Short downward chute within the reserved footprint, feeding an external bin.
  v=[(x,y,z) for zoff in (0,-.025) for x,y,z in [(-.30,.27,.58),(.30,.27,.58),(.30,.48,.34),(-.30,.48,.34)] for z in [z+zoff]]
  g.add(v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],STEEL)
 elif n=='FishHold':
  g.rectangle_ring(1.90,1.90,.08,-.62,.04,.04,NAVY);box(g,(0,0,-.64),(1.9,1.9,.04),TEAL,.01)
  g.rectangle_ring(1.94,1.94,.045,0,.07,.04,STEEL);part('HoldWell',g);g=G()
  box(g,(0,0,.075),(1.82,1.82,.07),WOOD,.015)
  for x in (-.60,-.30,0,.30,.60):g.beam((x,-.88,.114),(x,.88,.114),.008,.008,'M_WoodRecess')
  box(g,(0,-.65,.13),(.24,.10,.045),STEEL,.012);part('HatchLid',g,(0,.91,.075));K.NOTES.append('2x2 footprint, inset below-deck well. Deck must provide a matching opening. HatchLid sourceX hinge at(0,.91,.075).');return
 elif n=='IceMachine':
  box(g,(0,0,.58),(.78,.76,1.16),IVORY,.035);box(g,(0,.394,.78),(.57,.03,.42),NAVY,.02)
  box(g,(0,.415,.78),(.45,.015,.28),TEAL,.012);box(g,(0,.42,.37),(.50,.08,.26),STEEL,.015)
  for x in (-.15,0,.15):g.ellipsoid((x,.40,.34),(.045,.04,.034),8,3,IVORY)
 elif n=='GuttingTable':
  for x in (-.83,.83):
   for y in (-.32,.32):g.beam((x,y,0),(x,y,.52),.055,.055,NAVY)
  box(g,(0,0,.55),(1.85,.83,.065),STEEL,.015);box(g,(-.40,0,.59),(.65,.60,.025),IVORY,.009)
  a=G();a.rectangle_ring(.50,.55,.03,.59,.68,.02,TEAL);g.merge(a,(.48,0,0));box(g,(.48,0,.60),(.5,.55,.025),TEAL,.004)
  box(g,(-.48,-.15,.62),(.25,.04,.015),STEEL,.003);box(g,(-.28,-.15,.62),(.12,.055,.035),ORANGE,.005)
 elif n=='Crane':
  lathe(g,[(0,.36),(.08,.36),(.12,.22),(.95,.18)],12,NAVY);part('Pedestal',g);g=G()
  g.beam((0,0,.92),(0,-.32,1.65),.14,.14,ORANGE,.018)
  g.tube([(0,-.32,1.65),(0,-.32,.85)],[.015,.015],8,ROPE)
  g.tube([(0,-.32,.85),(0,-.32,.78),(.05,-.32,.73),(.09,-.32,.79)],[.024]*4,8,STEEL)
  part('Boom',g,(0,0,.92));K.NOTES.append('Compact stored Boom inside1x1 footprint; localX hinge. Operational sweep/rope placement require collision handling.');return
 part(n,g)
STATIONS={'NetDrum':(2,1),'PowerHauler':(1,1),'Conveyor_Straight':(1,1),'Conveyor_Corner':(1,1),'SortingChute':(2,1),'FishHold':(2,2),'IceMachine':(1,1),'GuttingTable':(2,1),'Crane':(1,1)}
ASSETS={'DayBoat':('Boats',boat),**{n:('Stations',lambda n=n:station(n)) for n in STATIONS}}
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(ASSETS)
 OUT.mkdir(parents=True,exist_ok=True);p=OUT/'build-metrics.json';data=json.loads(p.read_text()) if p.exists() else {'assets':[]};index={a['asset']:a for a in data['assets']}
 for n in args:index[n]=W.build(n,ASSETS,OUT);data['assets']=list(index.values());data['palette_srgb']=B.PALETTE;p.write_text(json.dumps(data,indent=2)+'\n')

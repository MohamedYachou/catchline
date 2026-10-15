"""Task08 exact day-boat deck and modular 1m-grid stations. Blender5.2."""
import bpy,math,json,sys,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('world',Path(__file__).with_name('build_world_polish.py'));W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)
K=W.K;B=W.B;G=W.G;part=W.part;box=W.box;ring=W.ring;lathe=W.lathe
NAVY=W.NAVY;WOOD=W.WOOD;IVORY=W.IVORY;STEEL=W.STEEL;TEAL=W.TEAL;ORANGE=W.ORANGE;ROPE=W.ROPE;DARK=W.DARK;BLUE=W.BLUE
ROOT=W.ROOT;OUT=ROOT/'Art/Models/DayBoatKit'

def oriented_ring(g,centre,major,minor,colour,axis='Y'):
 a=G();a.torus((0,0,0),major,minor,colour)
 if axis=='X':a.vertices=[(y,x,z) for x,y,z in a.vertices]
 elif axis=='Z':a.vertices=[(x,z,y) for x,y,z in a.vertices]
 g.merge(a,centre)

def ramp(g,x,width,y0,y1,z0,z1,colour):
 v=[(xx,y,z-d) for d in (0,.025) for xx,y,z in [(x-width/2,y0,z0),(x+width/2,y0,z0),(x+width/2,y1,z1),(x-width/2,y1,z1)]]
 g.add(v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],colour)

def cabin_fittings():
 g=G()
 # The authoritative cabin body and six occupied tiles remain unchanged.
 for x in (-1.12,0,1.12):
  for z in (.80,1.44):box(g,(x,-5.057,z),(.89,.045,.055),IVORY,.009)
  for dx in (-.45,.45):box(g,(x+dx,-5.057,1.12),(.05,.045,.69),IVORY,.009)
  g.beam((x-.23,-5.088,.84),(x+.08,-5.088,1.24),.022,.022,DARK)
 for side in (-1,1):
  x=side*1.552
  box(g,(x,-4,.18),(.055,1.94,.30),NAVY,.012)
  for y in (-4.55,-3.53):
   for z in (.77,1.43):box(g,(x,y,z),(.045,.82,.05),IVORY,.008)
   for dy in (-.4,.4):box(g,(x,y+dy,1.10),(.045,.05,.70),IVORY,.008)
  g.beam((side*1.57,-3.15,.32),(side*1.57,-3.15,.78),.035,.035,STEEL)
  oriented_ring(g,(side*1.54,-4.13,.49),.20,.045,ORANGE,'X')
  for z in (.28,.70):box(g,(side*1.54,-4.13,z),(.08,.10,.065),IVORY,.01)
  # Roof trim and navigation-light housings stay within the roof overhang.
  box(g,(side*1.56,-4,1.73),(.065,2.08,.065),ORANGE,.012)
  box(g,(side*1.36,-4.62,1.83),(.21,.24,.13),NAVY,.025)
  box(g,(side*1.36,-4.73,1.84),(.15,.035,.07),ORANGE if side<0 else 'M_KelpGreen',.01)
 for y in (-5.04,-2.96):box(g,(0,y,1.73),(3.13,.065,.065),ORANGE,.012)
 # Door surround, porthole, roof vent and a folded aerial.
 for x in (-.37,.37):box(g,(x,-2.935,.70),(.06,.055,1.45),IVORY,.008)
 box(g,(0,-2.935,1.43),(.79,.055,.055),IVORY,.008)
 box(g,(-.97,-2.965,.28),(.52,.045,.12),NAVY,.012)
 oriented_ring(g,(-.97,-2.965,1.10),.19,.035,STEEL)
 box(g,(.85,-3.58,1.82),(.47,.55,.14),IVORY,.025)
 for y in (-3.74,-3.58,-3.42):box(g,(.85,y,1.897),(.34,.045,.014),DARK,.003)
 g.beam((-.72,-4.10,1.78),(-.72,-4.10,2.55),.025,.025,STEEL)
 part('CabinFittings',g)
 g=G()
 # Cleats and tyres remain on hull margins, outside the rectangular build deck.
 for side in (-1,1):
  for y in (-1.5,1.2):
   oriented_ring(g,(side*2.84,y,.10),.22,.05,DARK,'X')
   g.tube([(side*2.79,y-.12,.64),(side*2.84,y,.34),(side*2.79,y+.12,.64)],[.018]*3,6,ROPE)
  for y in (-4.55,4.65):
   box(g,(side*2.67,y,.63),(.20,.32,.055),NAVY,.012)
   g.beam((side*2.67,y,.65),(side*2.67,y,.77),.055,.055,STEEL)
   g.beam((side*2.67,y-.18,.77),(side*2.67,y+.18,.77),.055,.055,STEEL,.008)
 part('HullFittings',g)
 K.NOTES.append('Pass09 adds CabinFittings and HullFittings only; original boat part geometry, sockets, rail gap and cabin/deck bounds retained. Fittings are static, use existing palette, and stay outside free build tiles.')

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
 cabin_fittings()
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
  g.beam((0,0,.95),(0,-.25,1.16),.12,.12,ORANGE,.015)
  box(g,(0,.13,.76),(.34,.25,.29),NAVY,.03)
  box(g,(0,.267,.79),(.23,.025,.15),STEEL,.012)
  g.beam((0,.25,.10),(0,-.08,.86),.055,.055,STEEL,.009)
  g.tube([(-.20,.20,.72),(-.25,.05,.94),(-.20,-.13,1.21)],[.023]*3,8,DARK)
  g.beam((.17,.18,.63),(.23,.28,.83),.027,.027,STEEL)
  g.ellipsoid((.23,.28,.83),(.05,.05,.05),10,4,ORANGE)
  for x in (-.16,.16):
   g.beam((x,-.18,.98),(x,-.18,1.37),.035,.035,STEEL)
  g.beam((-.16,-.18,1.37),(.16,-.18,1.37),.035,.035,STEEL)
  part('Frame',g);g=G()
  g.tube([(-.075,-.25,1.16),(.075,-.25,1.16)],[.21,.21],20,DARK)
  for x in (-.08,.08):g.tube([(x-.01,-.25,1.16),(x+.01,-.25,1.16)],[.24,.24],20,STEEL)
  for x in (-.108,.108):g.tube([(x-.014,-.25,1.16),(x+.014,-.25,1.16)],[.066,.066],12,ORANGE)
  oriented_ring(g,(0,-.25,1.16),.195,.025,ROPE,'X')
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
  for x in (-.45,.45):
   ramp(g,x,.60,-.26,.25,.70,.62,IVORY if x<0 else TEAL)
   for xx in (x-.305,x+.305):g.beam((xx,-.27,.72),(xx,.25,.65),.025,.025,STEEL)
   for y in (-.16,.02,.18):box(g,(x,y,.706-(y+.26)*.08/.51),(.33,.025,.008),DARK,.002)
  for x in (-.83,.83):
   box(g,(x,-.32,.025),(.10,.12,.05),DARK,.008)
   box(g,(x,.32,.025),(.10,.12,.05),DARK,.008)
   g.beam((x,.30,.62),(x,.43,.69),.026,.026,STEEL)
  g.beam((-.83,-.32,.15),(.83,-.32,.15),.04,.04,NAVY)
  box(g,(0,.425,.49),(.34,.04,.10),NAVY,.012)
 elif n=='FishHold':
  g.rectangle_ring(1.90,1.90,.08,-.62,.04,.04,NAVY);box(g,(0,0,-.64),(1.9,1.9,.04),TEAL,.01)
  g.rectangle_ring(1.94,1.94,.045,0,.07,.04,STEEL);part('HoldWell',g);g=G()
  box(g,(0,0,.075),(1.82,1.82,.07),WOOD,.015)
  for x in (-.60,-.30,0,.30,.60):g.beam((x,-.88,.114),(x,.88,.114),.008,.008,'M_WoodRecess')
  box(g,(0,-.65,.13),(.24,.10,.045),STEEL,.012);part('HatchLid',g,(0,.91,.075));K.NOTES.append('2x2 footprint, inset below-deck well. Deck must provide a matching opening. HatchLid sourceX hinge at(0,.91,.075).');return
 elif n=='IceMachine':
  # Closed casing pieces leave a real recess above the collector, not a tray buried in a solid box.
  box(g,(0,-.075,.58),(.78,.61,1.16),IVORY,.035)
  box(g,(0,.305,.88),(.78,.15,.56),IVORY,.025)
  box(g,(0,.305,.14),(.78,.15,.28),IVORY,.025)
  for x in (-.345,.345):box(g,(x,.305,.44),(.09,.15,.32),IVORY,.015)
  box(g,(0,.394,.78),(.57,.03,.42),NAVY,.02)
  box(g,(0,.415,.78),(.45,.015,.28),TEAL,.012)
  box(g,(0,0,.045),(.84,.80,.09),NAVY,.02)
  box(g,(0,.438,.995),(.62,.105,.08),STEEL,.015)
  box(g,(0,.238,.45),(.57,.015,.31),NAVY,.01)
  box(g,(0,.41,.575),(.26,.05,.07),STEEL,.008)
  a=G();a.rectangle_ring(.60,.25,.035,.32,.46,.025,STEEL);g.merge(a,(0,.34,0))
  box(g,(0,.34,.325),(.58,.23,.025),STEEL,.008)
  box(g,(0,.419,1.08),(.28,.025,.06),NAVY,.008)
  for x,col in ((-.26,ORANGE),(.26,TEAL)):g.ellipsoid((x,.425,1.08),(.035,.018,.035),10,3,col)
  for x in (-.395,.395):
   for z in (.26,.35,.44):box(g,(x,.05,z),(.015,.36,.035),DARK,.005)
   g.beam((x,-.12,.86),(x,.12,.86),.025,.025,STEEL)
  part('IceMachine',g);g=G()
  for x,y in ((-.15,.32),(0,.34),(.15,.32),(-.07,.42),(.08,.42)):
   box(g,(x,y,.37),(.085,.065,.065),IVORY,.015)
  part('OutputIce',g);K.NOTES.append('Pass09 OutputIce is a separate optional mesh at origin; consumer may hide it for an empty collector. No gameplay state or animation is supplied.');return
 elif n=='GuttingTable':
  for x in (-.83,.83):
   for y in (-.32,.32):g.beam((x,y,0),(x,y,.52),.055,.055,NAVY)
  box(g,(0,0,.55),(1.85,.83,.065),STEEL,.015);box(g,(-.40,0,.59),(.65,.60,.025),IVORY,.009)
  a=G();a.rectangle_ring(.50,.55,.03,.59,.68,.02,TEAL);g.merge(a,(.48,0,0));box(g,(.48,0,.60),(.5,.55,.025),TEAL,.004)
  box(g,(-.48,-.15,.62),(.25,.04,.015),STEEL,.003);box(g,(-.28,-.15,.62),(.12,.055,.035),ORANGE,.005)
  for x in (-.83,.83):
   g.beam((x,-.32,.15),(x,.32,.15),.045,.045,NAVY)
   for y in (-.32,.32):box(g,(x,y,.025),(.11,.12,.05),DARK,.008)
  g.beam((-.83,-.32,.15),(.83,-.32,.15),.045,.045,NAVY)
  box(g,(0,-.05,.18),(1.52,.52,.045),WOOD,.009)
  a=G();a.rectangle_ring(.54,.40,.03,.205,.37,.025,TEAL);g.merge(a,(-.43,-.03,0))
  box(g,(-.43,-.03,.21),(.52,.38,.025),TEAL,.008)
  for y in (-.12,0,.12):box(g,(.48,y,.616),(.35,.025,.008),DARK,.002)
  g.tube([(.72,-.20,.64),(.72,-.20,.87),(.61,-.20,.91),(.53,-.20,.85)],[.018]*4,8,STEEL)
  g.beam((-.65,.43,.56),(-.35,.43,.56),.035,.035,STEEL)
 elif n=='Crane':
  lathe(g,[(0,.36),(.08,.36),(.12,.22),(.95,.18)],12,NAVY)
  ring(g,.215,.035,.18,.25,STEEL);ring(g,.20,.035,.84,.92,STEEL)
  box(g,(.21,.12,.73),(.18,.20,.18),STEEL,.02)
  g.beam((.21,.23,.76),(.21,.30,.89),.025,.025,DARK)
  g.ellipsoid((.21,.30,.89),(.04,.04,.04),10,3,ORANGE)
  part('Pedestal',g);g=G()
  g.beam((0,0,.92),(0,-.32,1.65),.14,.14,ORANGE,.018)
  g.beam((0,0,.94),(0,-.17,1.32),.205,.19,ORANGE,.025)
  g.beam((-.13,.02,.97),(-.13,-.16,1.36),.055,.055,DARK,.009)
  g.beam((-.13,-.16,1.36),(-.13,-.25,1.53),.033,.033,STEEL)
  for x in (-.10,.10):g.tube([(x-.02,-.32,1.65),(x+.02,-.32,1.65)],[.105,.105],12,STEEL)
  g.tube([(-.04,-.32,1.65),(.04,-.32,1.65)],[.078,.078],12,DARK)
  g.tube([(.13,0,.96),(.14,-.03,1.20),(.12,-.17,1.40)],[.018]*3,8,DARK)
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

"""Editable sea-lane sculptures, bound to the shared harbour palette/helpers."""
import math
from mathutils import Vector,Matrix

def register(B):
 G,part=B['G'],B['part'];box,beam,tube,ell=B['box'],B['beam'],B['tube'],B['ell'];lathe,rock,crate,ring=B['lathe'],B['rock'],B['crate'],B['ring']
 def prism(g,outline,thickness,mat):
  # Extruded polygon in XZ; narrow Y thickness, closed for both-side visibility.
  vs=[(x,y+side*thickness/2,z) for side in (-1,1) for x,y,z in outline];n=len(outline)
  g.add(vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
 def marker(green=False):
  g=G();m='M_KelpGreen' if green else 'M_SafetyOrange'
  lathe(g,(0,0,0),[(-.62,.08),(-.35,.25),(-.15,.25),(-.08,.16),(1.52,.08)],m,10)
  lathe(g,(0,0,0),[(.05,.1555),(.36,.1400)],'M_RailIvory',10)
  ring(g,(0,0,-.08),.22,.035,'M_Rubber',10)
  # Red can versus green cone topmarks: silhouette does not rely on colour.
  lathe(g,(0,0,0),[(1.57,.22),(1.96,.025)] if green else [(1.57,.20),(1.96,.20)],m,10)
  tube(g,[(0,0,1.96),(0,0,2.02)],.018,'M_Steel',6)
  ring(g,(0,0,2.02),.045,.015,'M_Steel',8)
  part('GreenConeSpar' if green else 'RedCanSpar',g)
  B['NOTES'].append('Root Y0 at water datum: float submerged toY-.62, upper body1.96m. Green cone/red can topmarks differ by silhouette.')
 def bell():
  g=G();lathe(g,(0,0,0),[(-.48,.38),(-.18,.68),(.10,.68),(.32,.40)],'M_OilskinYellow',12)
  lathe(g,(0,0,0),[(.33,.32),(.45,.32)],'M_HullNavy',12)
  for i in range(3):
   a=i*math.tau/3;x,y=.40*math.cos(a),.40*math.sin(a)
   beam(g,(x,y,.25),(x*.45,y*.45,1.72),.07,m='M_HullNavy')
  lathe(g,(0,0,0),[(1.57,.31),(1.73,.15),(1.82,.02)],'M_OilskinYellow',12)
  # The visible bell hangs from the cage, open-rim silhouette, clapper below.
  lathe(g,(0,0,0),[(.86,.22),(.96,.21),(1.21,.095),(1.27,.045)],'M_Rope',12)
  tube(g,[(0,0,1.55),(0,0,1.24)],.022,'M_Steel',6)
  ell(g,(0,0,.84),(.055,.055,.07),'M_HullNavy',8,2)
  part('BellFloatAndCage',g)
  B['NOTES'].append('RootY0; lower float submerges. Bell and clapper physically supported by three-legged cage.')
 def wreck():
  g=G();N=12
  # Eight-metre broken open fishing hull, elliptical sides, no dry deck over water.
  outer=[];inner=[]
  stations=[(-4,.42,-.40),(-3.2,1.25,.18),(-1.4,1.48,.24),(1.3,1.3,-.02),(3.3,.65,-.30),(4,.06,-.60)]
  for x,w,z in stations:
   outer += [(x,s*w,z) for s in (-1,1)]
   inner += [(x,s*(w-.10 if w>.15 else .025),z-.07) for s in (-1,1)]
  vs=outer+inner;fs=[]
  for j in range(5):
   for k in (0,1):
    if j==3 and k==1:continue # Broken-away side bay; ribs remain visible.
    a=2*j+k;b=2*(j+1)+k;fs += [(a,b,b+12,a+12)]
    # Side extends to a drowned keel. Broken gunwale is uneven, not floating.
    q=len(vs);vs += [(vs[a][0],0,-.92),(vs[b][0],0,-.92)]
    fs += [(a,q,q+1,b)]
  g.add(vs,fs,'M_HullNavy')
  for j,x in enumerate((-3.1,-1.7,-.3,1.1,2.5)):
   for a,b in zip(stations,stations[1:]):
    if a[0]<=x<=b[0]:
     t=(x-a[0])/(b[0]-a[0]);w=a[1]+t*(b[1]-a[1]);edge=a[2]+t*(b[2]-a[2]);break
   endz=min(edge-.12,.12-.08*j)
   ribw=w*(endz+.92)/(edge+.92)-.05
   for s in (-1,1):beam(g,(x,0,-.86),(x,s*ribw,endz),.075,m='M_WoodHighlight')
  box(g,(-2.1,0,-.24),(1.20,1.16,.10),'M_DeckWood',.015)
  box(g,(-1.7,.55,.16),(.80,.12,.70),'M_HullBlue',.025)
  for y in (-.62,.62):beam(g,(-2.8,y,-.10),(-.8,y,-.35),.10,m='M_Rope')
  part('BrokenEightMetreHull',g)
  B['NOTES'].append('Half-sunk eight-metre hull, rootY0 water datum, keelY-.92; open broken ribs and aft plank fragment. No sunken preview water is exported.')
 def seals():
  g=G()
  # Whole group spans6m; low rock shoulders overlap beneath each grounded seal.
  for i,(x,y,w,d,h) in enumerate([(-2,0,2.3,2.0,.95),(-.5,.5,2.2,2.2,1.20),(1.55,.2,2.8,2.0,1.0),(.2,-.75,2.1,1.8,.70)]):
   rock(g,(x,y,-.60),(w,d,h),60+i)
  for j,(cx,cy,z,a) in enumerate([(-1.9,-.05,.30,-.3),(-.25,.43,.53,.28),(1.60,.13,.36,-.2)]):
   s=G();ell(s,(0,0,.22),(.68,.27,.25),'M_Rubber' if j==1 else 'M_HullNavy',12,4)
   ell(s,(-.54,0,.35),(.23,.22,.23),'M_Rubber' if j==1 else 'M_HullNavy',10,3)
   ell(s,(-.73,-.005,.29),(.14,.15,.09),'M_FishSilver',8,2)
   ell(s,(-.84,-.005,.31),(.035,.065,.027),'M_Rubber',8,2)
   for side in (-1,1):
    ell(s,(-.61,side*.17,.42),(.027,.018,.025),'M_Rubber',8,2)
    ell(s,(-.18,side*.25,.10),(.30,.13,.06),'M_Rubber',8,2)
    ell(s,(.65,side*.13,.13),(.26,.12,.07),'M_Rubber',8,2)
   rot=Matrix.Rotation(a,4,'Z');s.vertices=[tuple(rot@Vector(v)+Vector((cx,cy,z))) for v in s.vertices];g.merge(s)
  part('RocksAndThreeRestingSeals',g)
  B['NOTES'].append('Three complete resting seal silhouettes sit on overlapping rocks. RootY0 water datum; underwater rock foundation intentional. Approx6m rock group.')
 def floatingcrate():
  g=G();crate(g,(0,0,-.16),(.72,.58,.50),'M_DeckWood')
  for y in (-.15,.15):box(g,(0,y,-.12),(.66,.11,.04),'M_WoodHighlight',.008)
  for x in (-.18,.18):beam(g,(x,-.27,.32),(x,.27,.32),.10,m='M_WoodHighlight',bevel=.012)
  tube(g,[(-.36,-.25,.10),(-.36,.25,.10),(.36,.25,.10),(.36,-.25,.10),(-.36,-.25,.10)],.023,'M_Rope',6)
  part('LashedFloatingCrate',g)
  B['NOTES'].append('RootY0 at floating datum: lower crate -.16, lid .37; no animation/water geometry exported.')
 def dolphin():
  g=G();n=12
  # Continuous arched spindle with blue dorsal half and ivory belly.
  stations=[(-1.10,.025,.025,.27),(-.94,.065,.045,.28),(-.88,.105,.125,.33),(-.72,.19,.165,.32),(-.45,.235,.20,.23),(-.10,.23,.20,.08),(.28,.16,.15,-.08),(.65,.085,.08,-.17),(.95,.035,.032,-.15)]
  vs=[(x,ry*math.cos(i*math.tau/n),zc+rz*math.sin(i*math.tau/n)) for x,ry,rz,zc in stations for i in range(n)]
  fs=[];cols=[]
  for j in range(len(stations)-1):
   for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i));cols.append('M_FishSilver' if i>=7 else 'M_HullBlue')
  for f,c in zip(fs,cols):g.add(vs,[f],c)
  # g.add with full vertex set per face duplicates vertices; part welds them.
  g.add(vs,[tuple(reversed(range(n))),tuple(range((len(stations)-1)*n,len(stations)*n))],'M_HullBlue')
  prism(g,[(-.32,0,.38),(-.18,0,.56),(.07,0,.64),(-.01,0,.44),(.19,0,.25)],.045,'M_HullBlue')
  for s in (-1,1):
   prism(g,[(-.49,s*.14,.18),(-.13,s*.49,-.12),(.02,s*.12,.03)],.035,'M_HullBlue')
   prism(g,[(.82,0,-.15),(1.10,s*.38,-.09),(.99,s*.34,-.22),(.75,0,-.17)],.025,'M_HullBlue')
   ell(g,(-.76,s*.183,.37),(.025,.018,.025),'M_Rubber',8,2)
  part('LeapingDolphinSingleMesh',g,smooth=True)
  B['NOTES'].append('One single mesh object,2.2m nose-to-fluke X envelope, smooth arched leaping silhouette. Root on arc centre; runtime supplies leap and waterline.')
 def gull():
  g=G();ell(g,(0,0,.10),(.12,.24,.13),'M_RailIvory',10,4)
  ell(g,(0,-.21,-.005),(.09,.10,.10),'M_RailIvory',10,3)
  # Folded, swept wing wedges hug the body, black tips and descending beak.
  for s in (-1,1):
   prism(g,[(s*.09,-.12,.14),(s*.24,.10,.18),(s*.12,.35,.19),(s*.04,.14,.05)],.025,'M_RailIvory')
   prism(g,[(s*.16,.19,.19),(s*.12,.35,.19),(s*.05,.32,.13)],.028,'M_HullNavy')
   ell(g,(s*.072,-.24,.013),(.016,.019,.016),'M_Rubber',8,2)
  beam(g,(0,-.26,-.03),(0,-.38,-.16),.055,.035,'M_OilskinYellow',.008)
  prism(g,[(-.08,.16,.10),(0,.43,.20),(.08,.16,.10)],.025,'M_HullNavy')
  pitch=Matrix.Rotation(math.radians(50),4,'X');centre=Vector((0,0,.10))
  g.vertices=[tuple(pitch@(Vector(v)-centre)+centre) for v in g.vertices]
  part('FoldedWingDivingGull',g,smooth=True)
  B['NOTES'].append('Folded diving wings and downward beak, one mesh; runtime supplies dive trajectory. Root at body centre, no ground-contact claim.')
 def handcart():
  g=G();box(g,(0,0,.21),(.80,.70,.10),'M_Steel',.025)
  for x in (-.35,.35):
   beam(g,(x,.26,.19),(x,.35,1.44),.06,m='M_HullNavy')
   beam(g,(x,.35,1.44),(x,.52,1.44),.075,m='M_Rubber')
  for z in (.38,.78):beam(g,(-.35,.31,z),(.35,.31,z),.055,m='M_HullNavy')
  beam(g,(-.53,.18,.18),(.53,.18,.18),.07,m='M_Steel')
  for s in (-1,1):
   w=G();w.torus((0,0,0),.13,.045,'M_Rubber');w.vertices=[(s*.46-v[1],.18+v[0],.175+v[2]) for v in w.vertices];g.merge(w)
   ell(g,(s*.49,.18,.175),(.026,.055,.055),'M_Steel',8,2)
  crate(g,(0,-.05,.26),(.70,.56,.43),'M_SeaTeal');crate(g,(0,-.04,.69),(.67,.53,.40),'M_HullNavy')
  # Three economical silver fish fill the upper crate without crossing its rim.
  for x in (-.18,0,.18):ell(g,(x,-.04,1.015),(.065,.17,.055),'M_FishSilver',8,2)
  part('TwoCrateDockHandTruck',g)
  B['NOTES'].append('Ground-contact root, two rubber wheels and toe plate; two stacked fish crates rest on plate/each other.')
 return {'ChannelMarkerRed':marker,'ChannelMarkerGreen':lambda:marker(True),'BellBuoy':bell,'Wreck':wreck,'SealRocks':seals,'FloatingCrate':floatingcrate,'Dolphin':dolphin,'SeagullDive':gull,'HandCart':handcart}

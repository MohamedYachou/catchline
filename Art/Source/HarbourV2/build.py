"""HARBOUR-ART-1 editable kit. Blender 5.2, metres; no Assets/ writes.

Authoring helpers use X right, -Y front, Z up. Before export the new kit is
turned 180 degrees so its Unity front is -Z, as required by the current brief.
All source geometry is deterministic; preview objects never enter the FBX.
Run -- --name Slipway (one asset at a time, in brief order).
"""
import bpy, bmesh, math, json, hashlib, sys, importlib.util, argparse, random
from pathlib import Path
from mathutils import Vector, Matrix
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Art/Models/GullHarbour/HarbourV2'
spec=importlib.util.spec_from_file_location('kit_helpers',ROOT/'Art/Source/build_crab_coast_props.py')
H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
G=H.Geometry
PALETTE={**H.PALETTE,'M_DeckWood':'#C58B50','M_WoodHighlight':'#DFB77A',
 'M_WoodRecess':'#8C5A36','M_HullBlue':'#2A6685','M_OilskinYellow':'#E6AD38',
 'M_KelpGreen':'#477A56','M_FishSilver':'#BAC9C6'}
H.PALETTE=PALETTE
GROUPS={
 'A':['Slipway','PontoonSegment','PontoonGangway','FuelDock','QuayCrane',
      'BreakwaterWall','BreakwaterEnd','OuterWharf','WharfLight','MouthBeacon'],
 'B':['HarbourMasterHut','NoticeBoard','SuppliesShed','IceHouse','NetLoft','BoatyardShed','BoatCradle'],
 'C':['CompactFisherV1_VariantRed','PrepFisherV1_VariantGreen','Tier5DeepLines103_VariantBlue','Skiff_VariantYellow'],
 'D':['ChannelMarkerRed','ChannelMarkerGreen','BellBuoy','Wreck','SealRocks','FloatingCrate','Dolphin','SeagullDive','HandCart']}
COL=None;ROOTOBJ=None;NOTES=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def box(g,c,s,m='M_DeckWood',bevel=.02):
    # Chamfered section along Z: broad edge highlights, 28 tris instead of
    # expensive per-object modifiers. Use solid unbroken planks, no noisy grain.
    g.beam((c[0],c[1],c[2]-s[2]/2),(c[0],c[1],c[2]+s[2]/2),s[0],s[1],m,bevel)
def beam(g,a,b,w=.07,d=None,m='M_DeckWood',bevel=.01):g.beam(a,b,w,w if d is None else d,m,bevel)
def tube(g,p,r=.025,m='M_Rope',n=8):g.tube(p,[r]*len(p),n,m)
def ell(g,c,s,m='M_Steel',segments=10,rings=3):g.ellipsoid(c,s,segments,rings,m)
def lathe(g,c,profile,m,n=12):
    vs=[(c[0]+r*math.cos(i*math.tau/n),c[1]+r*math.sin(i*math.tau/n),c[2]+z) for z,r in profile for i in range(n)]
    fs=[tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]
    fs += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
    g.add(vs,fs,m)
def ring(g,c,r,minor=.025,m='M_Rubber',n=12):
    g.tube([(c[0]+r*math.cos(i*math.tau/n),c[1]+r*math.sin(i*math.tau/n),c[2]) for i in range(n+1)],[minor]*(n+1),6,m)
def part(n,g,pivot=(0,0,0),parent=None,smooth=False):
    g.vertices=[tuple(Vector(v)-Vector(pivot)) for v in g.vertices]
    o=g.object(n,parent or ROOTOBJ,COL);o.location=pivot
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for p in o.data.polygons:p.use_smooth=smooth
    return o
def cleat(g,x,y,z):
    box(g,(x,y,z+.018),(.24,.12,.036),'M_Steel',.008)
    beam(g,(x,y,z+.035),(x,y,z+.105),.055,m='M_Steel')
    beam(g,(x-.17,y,z+.105),(x+.17,y,z+.105),.052,m='M_Steel')
def bollard(g,x,y,z):
    box(g,(x,y,z+.04),(.35,.30,.08),'M_HullNavy',.035)
    lathe(g,(x,y,z),[(.06,.085),(.35,.085),(.39,.12)],'M_HullNavy')
    beam(g,(x-.20,y,z+.34),(x+.20,y,z+.34),.10,m='M_HullNavy',bevel=.025)
def crate(g,c,s=(.65,.48,.42),colour='M_HullNavy'):
    x,y,z=c;w,d,h=s
    box(g,(x,y,z+.025),(w,d,.05),colour,.008)
    for v in (.12,h-.08):
        for side in (-1,1):
            box(g,(x,y+side*(d/2-.025),z+v),(w,.045,.10),colour,.008)
            box(g,(x+side*(w/2-.025),y,z+v),(.045,d,.10),colour,.008)
    for sx in (-1,1):
        for sy in (-1,1):box(g,(x+sx*(w/2-.03),y+sy*(d/2-.03),z+h/2),(.06,.06,h),colour,.008)
    for side in (-1,1):box(g,(x,y+side*d/2,z+h-.03),(w+.035,.035,.065),'M_RailIvory',.009)
def roof(g,w,d,z,peak,m='M_HullNavy'):
    a=w/2+.13;b=d/2+.13
    vs=[(-a,-b,z),(a,-b,z),(0,-b,peak),(-a,b,z),(a,b,z),(0,b,peak)]
    g.add(vs,[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],m)
    for y in (-b,b):
        for s in (-1,1):beam(g,(s*a,y,z),(0,y,peak),.09,m='M_WoodHighlight')
    beam(g,(0,-b,peak),(0,b,peak),.09,m=m)
    for y in (-d*.25,d*.25):
        for s in (-1,1):beam(g,(s*a,y,z+.02),(0,y,peak+.02),.035,m='M_HullBlue')
def window(g,x,y,z,w=.64,h=.70):
    box(g,(x,y,z),(w,.055,h),'M_HullBlue',.01)
    for sx in (-1,1):box(g,(x+sx*w/2,y-.035,z),(.055,.05,h+.10),'M_RailIvory',.006)
    for sz in (-1,0,1):box(g,(x,y-.035,z+sz*h/2),(w+.10,.05,.05),'M_RailIvory',.006)
def rock(g,c,s,seed=1):
    rng=random.Random(seed);n=8
    phases=[rng.uniform(.88,1.12) for _ in range(n)]
    vs=[(c[0]+math.cos(i*math.tau/n)*s[0]*r*phases[i]/2,
         c[1]+math.sin(i*math.tau/n)*s[1]*r*phases[i]/2,c[2]+z*s[2])
        for z,r in [(0,.65),(.25,1),(.70,.89),(1,.35)] for i in range(n)]
    fs=[tuple(reversed(range(n))),tuple(range(3*n,4*n))]
    fs += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)]
    g.add(vs,fs,'M_FishSilver' if seed%3==0 else 'M_Steel')
def slipway():
    g=G();w=4;length=7;high=.35;low=-.9
    vs=[(-w,0,high),(w,0,high),(-w,-length,low),(w,-length,low),
        (-w,0,high-.22),(w,0,high-.22),(-w,-length,low-.22),(w,-length,low-.22)]
    g.add(vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],'M_FishSilver')
    # Two separate rowboat rail pairs, with shallow broad transverse traction strips.
    for x in (-2.70,-1.70,1.70,2.70):
        beam(g,(x,-.15,high+.045),(x,-6.85,low+.07),.065,.045,'M_Steel')
    for j in range(1,10):
        y=-j*.67;z=high+(low-high)*(-y/length)
        beam(g,(-3.93,y,z+.008),(3.93,y,z+.008),.028,.013,'M_Rope',0)
    for s in (-1,1):
        beam(g,(s*3.94,-.05,.45),(s*3.94,-6.95,-.79),.12,.10,'M_Rope',.025)
        cleat(g,s*3.65,-.12,.35)
    part('RampConcreteAndRails',g)
    NOTES.append('Absolute quay/water datum: root Y=0; 8m wide ramp, rail-pair centres X +/-2.2m for updated rowboat slots. Ramp top at local Y=.35 at Z=0, toe Y=-.9 at Z=-7. Rails are on ramp, submerged toe intentional.')
def pontoon(fuel=False):
    g=G();length=2 if fuel else 4;w=2
    for j in range(round(length/.25)):
        box(g,(0,-length/2+.125+j*.25,-.065),(w,.25,.13),'M_WoodHighlight' if j%5==0 else 'M_DeckWood',.008)
    for s in (-1,1):
        box(g,(s*.83,0,-.23),(.22,length-.18,.32),'M_HullNavy',.045)
        box(g,(s*.92,0,-.11),(.13,length,.13),'M_WoodRecess',.012)
        for y in (-length*.30,length*.30):
            cleat(g,s*.72,y,0)
            # Rubber tyre/fender hangs from a short attachment, not in midair.
            tube(g,[(s*.82,y,-.025),(s*1.01,y,-.21)],.016,'M_Rope',6)
            f=G();f.torus((0,0,0),.115,.035,'M_Rubber')
            f.vertices=[(s*1.035-v[1],y+v[0],-.24+v[2]) for v in f.vertices]
            g.merge(f)
    part('FloatDeck',g)
    if not fuel:return
    g=G();box(g,(.15,.28,.08),(.64,.52,.16),'M_HullNavy',.035)
    box(g,(.15,.28,.67),(.50,.43,1.1),'M_SafetyOrange',.045)
    box(g,(.15,.28,1.18),(.60,.50,.14),'M_RailIvory',.025)
    box(g,(.15,.053,.87),(.32,.02,.26),'M_RailIvory',.012)
    box(g,(.15,.038,.92),(.24,.014,.09),'M_HullNavy',.002)
    tube(g,[(.39,.19,1),(.67,.16,.92),(.71,.11,.39),(.55,.02,.25),(.40,-.03,.44),(.44,-.01,.91)],.026,'M_Rubber',8)
    beam(g,(.44,-.01,.91),(.41,-.02,1.07),.055,m='M_Steel')
    box(g,(-.59,.72,.62),(.045,.045,1.24),'M_HullNavy',.008)
    box(g,(-.59,.72,1.24),(.56,.08,.36),'M_RailIvory',.02)
    # Large fuel-drop pictogram, readable without microtype.
    ell(g,(-.59,.669,1.23),(.085,.008,.10),'M_SafetyOrange',8,2)
    part('PumpHoseAndSign',g)
def gangway():
    g=G();L=3
    for j in range(12):
        y=-.125-j*.25;z=.35*(1+y/L)
        p=G();box(p,(0,0,0),(1.10,.25,.07),'M_WoodHighlight' if j%5==0 else 'M_DeckWood',.007)
        slope=Matrix.Rotation(math.atan(.35/L),4,'X')
        p.vertices=[tuple(slope@Vector(v)) for v in p.vertices];g.merge(p,(0,y,z-.035))
    for s in (-1,1):
        beam(g,(s*.57,0,.30),(s*.57,-L,-.05),.085,.085,'M_Steel')
        beam(g,(s*.57,0,1.08),(s*.57,-L,.73),.045,m='M_RailIvory')
        for j in (0,1,2,3):
            y=-j;z=.35*(1+y/L)
            beam(g,(s*.57,y,z),(s*.57,y,z+.73),.04,m='M_RailIvory')
    beam(g,(-.63,0,.33),(.63,0,.33),.06,m='M_Steel')
    part('HingedRamp',g,pivot=(0,0,.35))
    NOTES.append('Root Y=0 datum. HingedRamp child pivot at quay end Y=.35,Z=0; far end Z=-3,Y=0. Deck width1.1m, centreline length3m.')
def crane():
    g=G();box(g,(0,0,.10),(1.15,1.15,.20),'M_FishSilver',.055)
    lathe(g,(0,0,0),[(.20,.43),(.34,.43),(.41,.32),(2.95,.26),(3.05,.34)],'M_HullNavy')
    for x in (-.28,.28):beam(g,(x,.30,.40),(x,.30,2.75),.055,m='M_Steel')
    for z in (.6,1,1.4,1.8,2.2,2.6):beam(g,(-.28,.31,z),(.28,.31,z),.035,m='M_Steel')
    box(g,(0,0,3.05),(.78,.74,.20),'M_SafetyOrange',.045)
    part('CranePedestal',g)
    j=G();pivot=(0,0,3.16)
    beam(j,(0,.60,3.25),(0,-3.40,4.45),.23,.22,'M_OilskinYellow',.04)
    beam(j,(0,0,4.85),(0,-3.40,4.45),.045,m='M_Steel')
    beam(j,(0,0,3.18),(0,0,4.85),.13,m='M_HullNavy')
    box(j,(0,.72,3.35),(.66,.66,.48),'M_HullNavy',.045)
    lathe(j,(0,-3.4,4.35),[(0,.14),(.15,.14)],'M_Steel')
    tube(j,[(0,-3.40,4.38),(0,-3.40,1.65)],.022,'M_Rope')
    box(j,(0,-3.4,1.65),(.21,.18,.24),'M_OilskinYellow',.028)
    tube(j,[(0,-3.4,1.55),(0,-3.4,1.33),(.13,-3.4,1.26),(.23,-3.4,1.33),(.21,-3.4,1.43)],.035,'M_Steel')
    part('Jib',j,pivot=pivot)
    NOTES.append('Jib is an actual direct child named Jib, origin on slew axis at Y3.16; hook/rope/counterweight follow that child. Height4.85m.')
def breakwater(end=False):
    g=G()
    if end:
        for i in range(8):
            a=math.tau*i/8;rock(g,(1.08*math.cos(a),1.08*math.sin(a),-.95),(1.5,1.4,1.40),100+i)
        lathe(g,(0,0,0),[(.36,1.12),(.60,1.12)],'M_FishSilver',16)
    else:
        for j,x in enumerate((-1.42,-.48,.48,1.42)):
            for s in (-1,1):rock(g,(x,s*.90,-.95),(1.20,1.62,1.36),20+j*2+(s+1)//2)
        box(g,(0,0,.48),(4,1.8,.24),'M_FishSilver',.035)
        for x in (-1,0,1):box(g,(x,0,.602),(.018,1.72,.004),'M_Steel',0)
    part('ArmourAndConcreteCap',g)
    NOTES.append('Root Y=0 harbour datum, rock sole submerged Y=-.95, concrete path topY=.6. Path1.8m wide. Rock apron intentionally broader than cap.')
def outerwharf():
    g=G();box(g,(0,0,.22),(4,1.8,.26),'M_FishSilver',.035)
    box(g,(0,0,-.38),(3.88,1.68,.94),'M_Steel',.035)
    for x in (-1.35,1.35):bollard(g,x,.28,.35)
    for x in (-1.3,0,1.3):
        box(g,(x,-.905,-.02),(.30,.12,.44),'M_Rubber',.03)
    part('ConcreteWharfAndBollards',g)
    NOTES.append('Root Y=0 datum; deck topY=.35, water-facing fenders local -Z. Segment4x1.8m.')
def light(beacon=False):
    g=G()
    if beacon:
        rock(g,(0,0,-.8),(1.9,1.65,1.15),19)
        lathe(g,(0,0,0),[(.28,.34),(.42,.34),(1.55,.18)],'M_RailIvory')
        lathe(g,(0,0,0),[(1.4,.20),(1.68,.20)],'M_KelpGreen')
        z=1.68;r=.24;h=.38
    else:
        box(g,(0,0,.035),(.30,.30,.07),'M_HullNavy',.025)
        lathe(g,(0,0,0),[(.07,.12),(.17,.12),(.22,.055),(2.35,.045)],'M_HullNavy')
        z=2.2;r=.15;h=.35
    lathe(g,(0,0,0),[(z,r*1.3),(z+.065,r*1.3)],'M_HullNavy')
    lathe(g,(0,0,0),[(z+.06,r*.83),(z+h,r*.83)],'M_KelpGreen' if beacon else 'M_BandIvory')
    for i in range(4):
        a=i*math.tau/4;beam(g,(r*math.cos(a),r*math.sin(a),z+.05),(r*math.cos(a),r*math.sin(a),z+h),.025,m='M_HullNavy')
    lathe(g,(0,0,0),[(z+h,r*1.4),(z+h+.16,.025)],'M_KelpGreen' if beacon else 'M_HullNavy')
    part('GreenMouthLight' if beacon else 'WharfLantern',g)
    NOTES.append('Mesh-only lantern, no exported Light. '+('Rock base soleY=-.8; rootY0 harbour datum.' if beacon else 'Ground-contact pivotY0; place on quay/wharf top.'))
def hut():
    g=G();box(g,(0,0,.06),(2.5,2,.12),'M_WoodRecess',.025)
    box(g,(0,0,1.12),(2.46,1.96,2.12),'M_DeckWood',.03)
    for z in (.45,.82,1.19,1.56,1.93):
        for side in (-1,1):box(g,(0,side*.985,z),(2.45,.018,.018),'M_WoodRecess',0)
    for x in (-1.20,1.20):box(g,(x,-1.015,1.13),(.10,.10,2.24),'M_WoodHighlight',.01)
    roof(g,2.5,2,2.20,2.9)
    window(g,-.55,-1.035,1.38,.75,.78)
    box(g,(.62,-1.035,.88),(.66,.07,1.65),'M_HullNavy',.018)
    box(g,(.39,-1.082,.89),(.055,.035,.055),'M_OilskinYellow',.008)
    box(g,(0,-1.10,.065),(2,.26,.13),'M_FishSilver',.015)
    beam(g,(.86,.48,2.3),(.86,.48,3.65),.045,m='M_RailIvory')
    # Thin closed pennant remains visible from both sides after backface culling.
    fv=[(.86,.48,3.62),(1.47,.46,3.55),(1.40,.47,3.23),(.86,.48,3.30)]
    g.add(fv+[(x,y+.018,z) for x,y,z in fv],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'M_SafetyOrange')
    part('TimberHutWindowFlag',g)
def notice():
    g=G()
    for x in (-.86,.86):box(g,(x,0,1.16),(.16,.18,2.32),'M_DeckWood',.02)
    box(g,(0,0,1.51),(1.90,.14,1.31),'M_HullNavy',.025)
    for x in (-.97,.97):box(g,(x,-.08,1.50),(.08,.08,1.40),'M_WoodHighlight',.012)
    for z in (.81,2.20):box(g,(0,-.08,z),(2,.08,.08),'M_WoodHighlight',.012)
    for x,z,w,h in [(-.57,1.70,.44,.54),(-.05,1.46,.43,.64),(.53,1.72,.43,.53),(.50,1.12,.40,.32)]:
        box(g,(x,-.086,z),(w,.016,h),'M_RailIvory',.003)
        lathe(g,(x,0,0),[(0,.01),(.02,.01)],'M_SafetyOrange',6) if False else None
        box(g,(x,-.102,z+h*.38),(.035,.015,.035),'M_SafetyOrange',.004)
        for j in range(2):box(g,(x,-.098,z+.03-j*.10),(w*.62,.006,.022),'M_HullBlue',0)
    roof(g,1.96,.54,2.32,2.60)
    part('RoofedCrewNoticeBoard',g)
def supplies():
    g=G();box(g,(0,0,.06),(3,2.5,.12),'M_WoodRecess',.02)
    box(g,(0,1.17,1.14),(2.94,.14,2.16),'M_DeckWood',.025)
    for s in (-1,1):
        box(g,(s*1.41,0,1.14),(.14,2.46,2.16),'M_DeckWood',.02)
        beam(g,(s*1.39,-1.17,.12),(s*1.39,-1.17,2.30),.14,m='M_WoodHighlight',bevel=.02)
    roof(g,3,2.5,2.28,3.05)
    box(g,(0,.72,.78),(2.7,.70,.12),'M_WoodHighlight',.015)
    for x,z in [(-.95,.13),(-.41,.13),(-.82,.63)]:
        ell(g,(x,.42,z+.24),(.29,.30,.26),'M_Rope',10,3)
        ring(g,(x,.42,z+.45),.07,.018,'M_WoodRecess',8)
    for x in (-.95,-.48):
        box(g,(x,-.66,.15),(.36,.38,.06),'M_WoodHighlight',.008)
        box(g,(x,-.66,.42),(.30,.28,.47),'M_SafetyOrange',.035)
        beam(g,(x-.07,-.66,.66),(x+.07,-.66,.66),.045,m='M_HullNavy')
    crate(g,(.66,-.62,.12),(.80,.58,.42),'M_SeaTeal')
    crate(g,(.70,-.60,.54),(.70,.50,.34),'M_HullNavy')
    box(g,(0,-1.28,2.20),(1.9,.12,.32),'M_RailIvory',.02)
    part('OpenShedSacksCansBait',g)
def icehouse():
    g=G();box(g,(0,0,1.17),(3.5,3,2.34),'M_FishSilver',.04)
    for j in range(4):
        z=.30+j*.52
        box(g,(0,-1.503,z),(3.4,.015,.018),'M_Steel',0)
        for x in [-1.15+(j%2)*.4,-.25+(j%2)*.4,.65+(j%2)*.4]:box(g,(x,-1.51,z+.25),(.018,.015,.48),'M_Steel',0)
    roof(g,3.5,3,2.36,3.14,'M_HullBlue')
    box(g,(-.40,-1.55,1.02),(1.22,.20,1.94),'M_RailIvory',.06)
    for z in (.53,1.52):box(g,(-.40,-1.674,z),(1.22,.055,.085),'M_Steel',.01)
    box(g,(.03,-1.68,1.01),(.09,.065,.40),'M_HullNavy',.015)
    beam(g,(1.27,-1.48,1.72),(1.27,-2.14,.87),.52,.24,'M_Steel',.025)
    for x in (1.01,1.53):
        beam(g,(x,-1.48,1.86),(x,-2.14,1.01),.055,.19,'M_RailIvory',.008)
    box(g,(1.27,-1.526,1.72),(.66,.09,.48),'M_HullNavy',.025)
    for a in (0,math.pi/3,2*math.pi/3):
        beam(g,(-.40+.25*math.cos(a),-1.69,1.02+.25*math.sin(a)),(-.40-.25*math.cos(a),-1.69,1.02-.25*math.sin(a)),.035,m='M_SeaTeal',bevel=0)
    part('StoneInsulatedHouseAndChute',g)
def netloft():
    g=G();box(g,(0,0,1.73),(3,2.6,3.46),'M_DeckWood',.03)
    for x in [-1.2,-.8,-.4,0,.4,.8,1.2]:
        for y in (-1.31,1.31):box(g,(x,y,1.73),(.018,.018,3.36),'M_WoodRecess',0)
    for s in (-1,1):box(g,(s*1.46,-1.32,1.76),(.12,.09,3.5),'M_WoodHighlight',.015)
    roof(g,3,2.6,3.48,4.62)
    for z,h in [(.85,1.7),(2.78,1.05)]:box(g,(0,-1.34,z),(1.20,.08,h),'M_HullNavy',.025)
    beam(g,(-.6,-1.40,2.25),(.6,-1.40,3.31),.075,m='M_WoodHighlight')
    beam(g,(0,-1.35,3.64),(0,-2.1,3.64),.12,m='M_WoodHighlight')
    tube(g,[(0,-2.03,3.6),(0,-2.03,2.5)],.02,'M_Rope',6)
    # Coarse draped net surface; sparse loops keep the net broad at phone size.
    for i in range(7):
        x=-.65+i*.22
        tube(g,[(x,-1.46,2.89),(x*.85,-1.63,2.30),(x*.75,-1.60,1.68),(x*.6,-1.49,1.12)],.017,'M_KelpGreen',5)
    for j in range(6):
        z=2.85-j*.33;f=(z-1.12)/(2.89-1.12)
        tube(g,[(-.39-.26*f,-1.47,z),(0,-1.67,z-.07),(.39+.26*f,-1.47,z)],.017,'M_KelpGreen',5)
    part('TallLoftAndHangingNets',g)
def boatyard():
    g=G();w=9;d=5
    for x in (-4.35,0,4.35):
        for y in (-2.35,2.35):
            box(g,(x,y,.12),(.42,.42,.24),'M_FishSilver',.025)
            beam(g,(x,y,.20),(x,y,3.45),.22,m='M_DeckWood',bevel=.03)
            for s in ((1,) if x<0 else (-1,) if x>0 else (-1,1)):
                beam(g,(x,y,2.6),(x+s*.70,y,3.37),.11,m='M_WoodHighlight')
    for y in (-2.35,2.35):beam(g,(-4.48,y,3.36),(4.48,y,3.36),.23,.20,'M_DeckWood',.03)
    roof(g,9,5,3.5,4.8)
    # Back waist rail and diagonal braces; front remains open for the boat.
    for x in (-4.35,4.35):beam(g,(x,2.35,.6),(0,2.35,3.36),.12,m='M_WoodHighlight')
    part('OpenSidedBoatShed',g)
def cradle():
    g=G()
    for x in (-2.75,0,2.75):
        box(g,(x,0,.12),(.40,3,.24),'M_WoodRecess',.035)
        for s in (-1,1):
            beam(g,(x,s*1.35,.23),(x,s*.65,1.12),.19,m='M_DeckWood',bevel=.025)
            beam(g,(x-.28,s*.65,1.12),(x+.28,s*.65,1.12),.26,.12,'M_Rubber',.02)
        box(g,(x,0,.35),(.40,.55,.46),'M_WoodHighlight',.035)
    for y in (-.58,.58):beam(g,(-3.65,y,.26),(3.65,y,.26),.18,m='M_DeckWood',bevel=.02)
    part('KeelBlocksAndHullProps',g)
    NOTES.append('Long axis X,7.5m supported hull; skid envelope7.48x3m. Hull contact pads Y1.12, keel blocksY.58. Ground pivot0.')
BUILDERS={'Slipway':slipway,'PontoonSegment':pontoon,'PontoonGangway':gangway,'FuelDock':lambda:pontoon(True),
 'QuayCrane':crane,'BreakwaterWall':breakwater,'BreakwaterEnd':lambda:breakwater(True),'OuterWharf':outerwharf,
 'WharfLight':light,'MouthBeacon':lambda:light(True),'HarbourMasterHut':hut,'NoticeBoard':notice,
 'SuppliesShed':supplies,'IceHouse':icehouse,'NetLoft':netloft,'BoatyardShed':boatyard,'BoatCradle':cradle}
landmark_spec=importlib.util.spec_from_file_location('harbour_landmarks',Path(__file__).with_name('landmarks.py'))
landmark_module=importlib.util.module_from_spec(landmark_spec);landmark_spec.loader.exec_module(landmark_module)
BUILDERS.update(landmark_module.register(globals()))
def stage(meshes):
    sc=bpy.context.scene
    H.preview_stage(sc,meshes)
    sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='OPTIX';prefs.get_devices()
        for dev in prefs.devices:dev.use=dev.type=='OPTIX'
        sc.cycles.device='GPU'
    except Exception:sc.cycles.device='CPU'
    sc.render.resolution_x=sc.render.resolution_y=600
    sc.render.resolution_percentage=100
    sc.render.threads_mode='FIXED';sc.render.threads=8
    sc.view_settings.view_transform='Standard'
    pts=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in pts) for i in range(3)));hi=Vector(tuple(max(v[i] for v in pts) for i in range(3)))
    scale=max(1,(hi-lo).length/1.5)
    bpy.data.objects['Preview_Ground'].location.z=lo.z-.015
    for o in bpy.data.collections['PREVIEW_ONLY_NOT_EXPORTED'].objects:
        if o.type=='LIGHT':o.location*=scale;o.data.energy*=scale*scale;o.data.size*=scale
    return sc,lo,hi
def view(sc,meshes,lo,hi,yaw,elev):
    cam=sc.camera;target=(lo+hi)*.5
    ya=math.radians(yaw);el=math.radians(elev)
    direction=Vector((math.sin(ya)*math.cos(el),math.cos(ya)*math.cos(el),math.sin(el)))
    cam.location=target+direction*max(10,(hi-lo).length*3)
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    pr=[cam.matrix_world.inverted()@(o.matrix_world@Vector(v)) for o in meshes for v in o.bound_box]
    cam.data.ortho_scale=max(max(v[i] for v in pr)-min(v[i] for v in pr) for i in (0,1))*1.22
def build(name,render=True):
    global COL,ROOTOBJ
    OUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    H.MATERIALS.clear();H.MATERIALS.update({k:H.material(k,v) for k,v in PALETTE.items()})
    COL=bpy.data.collections.new('ASSET_EXPORT');sc.collection.children.link(COL)
    ROOTOBJ=bpy.data.objects.new(name,None);COL.objects.link(ROOTOBJ)
    ROOTOBJ['unity_front']='-Z';ROOTOBJ['metres']=True;ROOTOBJ['task']='HARBOUR-ART-1'
    NOTES.clear();BUILDERS[name]()
    # Turn finished geometry and pivots; transforms baked into meshes.
    rot=Matrix.Rotation(math.pi,4,'Z')
    for o in COL.objects:
        if o==ROOTOBJ:continue
        if o.type=='MESH':o.data.transform(rot)
        o.location=rot@o.location
    bpy.context.view_layer.update()
    meshes=[o for o in COL.objects if o.type=='MESH']
    stats=[H.mesh_stats(o) for o in meshes];tris=sum(s['triangles'] for s in stats)
    limit=3000 if name in GROUPS['B'] and name!='NoticeBoard' else 1500
    assert tris<limit,(name,tris,limit)
    for o in meshes:
        assert o.scale==Vector((1,1,1))
        assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
    sc,lo,hi=stage(meshes);view(sc,meshes,lo,hi,35,45)
    bpy.ops.object.select_all(action='DESELECT')
    for o in COL.objects:o.select_set(True)
    bpy.context.view_layer.objects.active=ROOTOBJ
    fbx=OUT/(name+'.fbx');blend=OUT/(name+'.blend')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','EMPTY'},
        global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',
        bake_space_transform=True,use_mesh_modifiers=True,use_triangles=True,mesh_smooth_type='FACE',
        bake_anim=False,add_leaf_bones=False,use_custom_props=True,path_mode='AUTO')
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),check_existing=False)
    renderpaths=[]
    if render:
        folder=OUT/'renders'/name;folder.mkdir(parents=True,exist_ok=True)
        for label,yaw,elev in [('front-right',35,45),('back-right',145,35),('back-left',215,35),('front-left',325,35),('top',0,90)]:
            view(sc,meshes,lo,hi,yaw,elev);sc.render.filepath=str(folder/(label+'.png'))
            bpy.ops.render.render(write_still=True);renderpaths.append(str(Path(sc.render.filepath).relative_to(ROOT)))
    row={'name':name,'group':next(k for k,v in GROUPS.items() if name in v),'triangles':tris,'limit':limit,
         'bounds_blender':[list(lo),list(hi)],'dimensions_width_depth_height':list(hi-lo),'parts':stats,
         'front_unity':'-Z','notes':list(NOTES),'blend':str(blend.relative_to(ROOT)),'fbx':str(fbx.relative_to(ROOT)),
         'sha256':{'blend':sha(blend),'fbx':sha(fbx)},'renders':renderpaths,
         'status':'exported, render review and FBX round-trip pending'}
    (OUT/'metrics').mkdir(exist_ok=True)
    (OUT/'metrics'/(name+'.json')).write_text(json.dumps(row,indent=2))
    print('HARBOUR BUILT',name,tris,'triangles',list(hi-lo),flush=True)
    audit_spec=importlib.util.spec_from_file_location('harbour_audit',Path(__file__).with_name('audit.py'))
    audit_mod=importlib.util.module_from_spec(audit_spec);audit_spec.loader.exec_module(audit_mod)
    audit_mod.audit(name)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--name',choices=list(BUILDERS),required=True);ap.add_argument('--no-render',action='store_true')
    a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    build(a.name,not a.no_render)

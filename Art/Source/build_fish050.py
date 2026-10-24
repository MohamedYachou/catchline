"""Four signature Big Common fish. Reuses the approved Fish043 art pipeline.
Run PYTHONPATH=/tmp/catchline-fish043-env blender -b -t 4 --python this_file -- [species].
Editable metre-scale Blender, actual FBX roundtrip, transparent model-rendered portrait.
"""
import bpy, math, sys, json, importlib.util
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('fish043', ROOT/'Art/Source/build_fish043.py')
art = importlib.util.module_from_spec(spec); spec.loader.exec_module(art)
art.OUT = ROOT/'Art/Models/Fish050'; art.OUT.mkdir(parents=True, exist_ok=True)
base = art.base

def ring_body(L, profile, back, side='M_FishSilver', belly='M_RailIvory'):
    # Each station has independent width, height and centre-height. This makes
    # four different silhouettes, instead of recolouring a single body mesh.
    n = 32; verts = []
    for y, w, h, z in profile:
        for i in range(n):
            a = i*math.tau/n
            verts.append((w*math.cos(a)*L, y*L, (z+h*math.sin(a))*L))
    faces = [tuple(reversed(range(n)))]; colors = [back]
    for j in range(len(profile)-1):
        for i in range(n):
            faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
            a = (i+.5)*math.tau/n
            colors.append(back if math.sin(a)>.30 else belly if math.sin(a)<-.58 else side)
    faces.append(tuple(range((len(profile)-1)*n,len(profile)*n))); colors.append(back)
    body = base.mesh('Body',verts,faces,colors)
    for p in body.data.polygons: p.use_smooth = True

def eye(L, x, y, z, size=.019):
    for s in [-1,1]:
        art.ball('Eye',(s*x*L,y*L,z*L),(.013*L,size*L,size*L),'M_Rubber')
        art.ball('EyeGlint',(s*(x+.011)*L,(y-.004)*L,(z+.006)*L),(.003*L,)*3,'M_RailIvory')

def gills(L, x, y, height):
    for s in [-1,1]:
        art.line('GillCover',[(s*(x-.012)*L,(y-.018)*L,-height*.75*L),
                            (s*x*L,y*L,0),(s*(x-.012)*L,(y-.018)*L,height*L)],.0025*L,'M_HullNavy')

def tail(L, poly, color, pivot=.38):
    obj = art.fin('Tail',poly,color,L)
    offset=Vector((0,pivot*L,0))
    for v in obj.data.vertices: v.co-=offset
    obj.location=offset

def pectorals(L, x, y, span, color):
    for s in [-1,1]:
        art.plate('Pectoral',[(s*x,y,0),(s*span,y+.16,-.06),
                             (s*(span*.82),y+.18,-.08),(s*x,y+.07,-.025)],color,L)

def tuna(L):
    ring_body(L,[(-.50,.012,.025,0),(-.44,.066,.080,0),(-.32,.115,.155,0),
                 (-.15,.137,.183,0),(0,.123,.165,0),(.18,.085,.112,0),
                 (.32,.032,.044,0),(.40,.014,.022,0)],'M_HullNavy')
    eye(L,.078,-.405,.035);gills(L,.113,-.30,.10)
    pectorals(L,.10,-.24,.26,'M_HullBlue')
    art.fin('FirstDorsal',[(-.26,.14),(-.18,.31),(-.04,.17),(.03,.14)],'M_OilskinYellow',L)
    art.fin('YellowDorsalSickle',[(.03,.14),(.10,.36),(.16,.40),(.14,.26),(.27,.07)],'M_OilskinYellow',L)
    art.fin('YellowAnalSickle',[(.04,-.14),(.13,-.33),(.19,-.36),(.16,-.23),(.28,-.06)],'M_OilskinYellow',L)
    for i in range(7):
        y=.21+i*.024;z=.088-i*.009
        for sign in [-1,1]:
            art.fin('YellowFinlet',[(y,sign*z),(y+.012,sign*(z+.035)),(y+.026,sign*(z-.003))],'M_OilskinYellow',L,.004)
    for s in [-1,1]:
        art.line('GoldLateralStripe',[(s*x*L,y*L,.015*L) for y,x in [(-.28,.12),(-.12,.139),(.04,.12),(.19,.083),(.29,.045)]],.003*L,'M_OilskinYellow')
    tail(L,[(.38,.02),(.57,.30),(.55,.17),(.47,0),(.55,-.17),(.57,-.30),(.38,-.02)],'M_HullBlue')
    art.line('Mouth',[(.04*L,-.47*L,-.009*L),(.07*L,-.42*L,-.025*L)],.002*L,'M_Rubber')

def barracuda(L):
    ring_body(L,[(-.51,.015,.022,.012),(-.44,.041,.039,.013),(-.34,.061,.066,0),
                 (-.18,.072,.078,0),(.04,.065,.073,0),(.25,.047,.055,0),
                 (.40,.020,.027,0),(.45,.013,.018,0)],'M_CoastWet')
    # Long protruding lower jaw and an open dark mouth, with visible fangs.
    art.ball('ProjectingLowerJaw',(0,-.445*L,-.029*L),(.037*L,.100*L,.016*L),'M_FishSilver')
    for s in [-1,1]:
        art.plate('OpenMouth',[(s*.023,-.523,-.007),(s*.055,-.387,-.012),
                               (s*.043,-.39,-.033),(s*.025,-.52,-.025)],'M_Rubber',L,.002)
        for i in range(7):
            y=-.49+i*.014;x=.028+i*.003
            art.cone('Fang',(s*x*L,y*L,-.007*L),(s*x*L,(y+.003)*L,-(.028 if i%3==0 else .021)*L),.004*L,'M_RailIvory')
        for j in range(9):
            y=-.17+j*.055;x=.073-max(0,y)*.08
            art.line('DarkFlankBar',[(s*x*L,y*L,.048*L),(s*(x+.002)*L,(y+.016)*L,.009*L)],.004*L,'M_HullNavy')
    eye(L,.047,-.394,.035,.016);gills(L,.065,-.295,.055)
    pectorals(L,.058,-.26,.135,'M_CoastWet')
    art.fin('FrontDorsal',[(-.23,.068),(-.16,.17),(-.09,.075)],'M_CoastWet',L)
    art.fin('RearDorsal',[(.21,.058),(.27,.15),(.36,.033)],'M_CoastWet',L)
    art.fin('Anal',[(.21,-.055),(.28,-.14),(.36,-.033)],'M_CoastWet',L)
    tail(L,[(.43,.02),(.59,.16),(.54,0),(.59,-.16),(.43,-.02)],'M_CoastWet',.43)

def mahi(L):
    # Bull mahi's high, nearly vertical forehead is the primary recognition cue.
    ring_body(L,[(-.48,.025,.058,.025),(-.455,.065,.154,.065),(-.39,.080,.177,.060),
                 (-.22,.083,.18,.025),(-.04,.071,.158,0),(.16,.050,.108,0),
                 (.34,.018,.035,0),(.40,.012,.02,0)],'M_SeaTeal','M_OilskinYellow','M_BandIvory')
    eye(L,.073,-.395,.075);gills(L,.086,-.30,.12)
    art.fin('LongDorsalSail',[(-.445,.22),(-.40,.31),(-.24,.31),(-.04,.27),
                             (.15,.20),(.34,.065),(.34,.03),(.15,.10),(-.04,.16),(-.24,.20)],'M_HullBlue',L)
    art.fin('AnalRibbon',[(0,-.15),(.08,-.21),(.26,-.105),(.33,-.035),(.14,-.09)],'M_OilskinYellow',L)
    pectorals(L,.074,-.27,.19,'M_SeaTeal')
    for s in [-1,1]:
        for i in range(16):
            y=-.29+(i%8)*.067;z=-.035+(i//8)*.076
            x=.081-max(0,y+.1)*.13
            art.ball('BlueFlankSpot',(s*x*L,y*L,z*L),(.0035*L,.009*L,.009*L),'M_HullBlue')
    tail(L,[(.38,.02),(.58,.22),(.53,.09),(.46,0),(.53,-.09),(.58,-.22),(.38,-.02)],'M_SeaTeal')
    for s in [-1,1]:
        art.line('Mouth',[(s*.024*L,-.49*L,-.006*L),(s*.065*L,-.43*L,-.021*L)],.002*L,'M_Rubber')

def monk(L):
    ring_body(L,[(-.42,.22,.055,0),(-.32,.29,.105,.015),(-.17,.30,.125,.025),
                 (.02,.22,.10,.018),(.16,.11,.068,0),(.31,.045,.042,0),
                 (.41,.025,.026,0)],'M_CoastWet','M_WoodRecess','M_BandIvory')
    # A broad open mouth, lip rims and deliberately sparse interlocking teeth.
    art.ball('MouthCavity',(0,-.431*L,-.006*L),(.215*L,.021*L,.056*L),'M_Rubber')
    for sign in [-1,1]:
        art.line('LipRim',[(x*L,(-.446+.035*(abs(x)/.22)**2)*L,
                            (sign*.048*(1-(x/.24)**2)-.005)*L) for x in [-.22,-.16,-.08,0,.08,.16,.22]],.009*L,'M_Rope')
        for i in range(9):
            x=-.18+i*.045;z=sign*.044*(1-(x/.24)**2)-.005
            art.cone('MonkfishTooth',(x*L,-.453*L,z*L),(x*L,-.456*L,(z-sign*.035)*L),.006*L,'M_RailIvory')
    for s in [-1,1]:
        art.ball('RaisedEye',(s*.145*L,-.25*L,.126*L),(.026*L,.03*L,.025*L),'M_Rubber')
        art.ball('EyeGlint',(s*.143*L,-.263*L,.146*L),(.004*L,)*3,'M_RailIvory')
        art.plate('WalkingPectoral',[(s*.25,-.17,-.025),(s*.39,-.10,-.04),
                                    (s*.42,.04,-.045),(s*.26,.04,-.035)],'M_CoastWet',L,.012)
        for j in range(6):
            y=-.26+j*.063;x=.29-max(0,y+.10)*.45
            art.line('SkinFringe',[(s*x*L,y*L,0),(s*(x+.038)*L,(y+.021)*L,-.018*L)],.004*L,'M_Rope')
    art.line('FishingLureStalk',[(0,-.26*L,.12*L),(0,-.31*L,.28*L),(0,-.42*L,.29*L),(0,-.46*L,.23*L)],.004*L,'M_CoastWet')
    art.ball('LureTip',(0,-.46*L,.23*L),(.013*L,.016*L,.016*L),'M_BandIvory')
    art.fin('RearDorsal',[(.12,.06),(.20,.13),(.34,.035)],'M_CoastWet',L)
    tail(L,[(.39,.026),(.52,.10),(.57,.07),(.57,-.07),(.52,-.10),(.39,-.026)],'M_CoastWet',.39)

ROWS=[('YellowfinTuna',.82,'tuna',tuna),('Barracuda',.88,'barracuda',barracuda),
      ('MahiMahi',.78,'mahi',mahi),('Monkfish',.68,'monkfish',monk)]

# Keep the established exporter/validation, with the broader top-view camera
# needed for the monkfish's flattened body. No existing generator is changed.
import inspect
delivery=inspect.getsource(art.deliver).replace("['eagle','stingray','manta']","['eagle','stingray','manta','monkfish']")
delivery=delivery.replace("print('FISH043 VERIFIED'","print('FISH050 VERIFIED'")
exec(delivery,art.__dict__)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    for name,L,kind,build in ROWS:
        if args and name not in args: continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.preferences.filepaths.save_version=0
        base.MATS={};art.FEATURES=[]
        bpy.context.scene.unit_settings.system='METRIC'
        base.GROUP=bpy.data.objects.new('Catchline_'+name,None)
        bpy.context.scene.collection.objects.link(base.GROUP)
        build(L);art.deliver(name,L,kind)

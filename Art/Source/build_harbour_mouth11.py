"""ART-011: authored Gull Harbour mouth. Blender5.2 -- preview | export.
Only new geometry/reference output. No Unity code/materials/textures/settings writes.
Connected offset strata follow hand-authored coast plans, informed by Plunder's
owned scenery_cays/cay_biome methodology; no Plunder code or third-party assets copied.
"""
import bpy,bmesh,math,json,sys,random,importlib.util,ast,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/HarbourMouth11'
spec=importlib.util.spec_from_file_location('gull11',Path(__file__).with_name('build_gull_harbour.py'))
K=importlib.util.module_from_spec(spec);spec.loader.exec_module(K);B=K.B;G=K.G
PAL={'M_CoastStone':'#A99A7C','M_CoastStoneLight':'#C9B89A','M_CoastWet':'#696F64',
     'M_CoastGrass':'#729053','M_CoastGrassLight':'#98A96B','M_CoastSand':'#D9C393','M_SeabedSand':'#BEA77D'}
C=math.cos(math.radians(35));S=math.sin(math.radians(35));Q=math.sqrt(.5)
WATER=-.32
PLANS={
 'Headland':[(-.6,3.4),(.3,2.75),(1.2,2.45),(2.15,2.55),(2.55,2.25),(2.85,1.95),(3.0,1.25),(3.5,.95),(4.1,1.05),(4.8,.85),(5.8,.55),(7.8,.8),(8.3,4.6),(.0,5.6)],
 'TidalIslet':[(-8,-1.1),(-6.2,-1.6),(-5.6,-1.45),(-5.2,-1),(-4.6,-.75),(-4.15,-.05),(-4.4,.4),(-5.2,.75),(-6.5,1),(-8,.6)],
 'OuterShelf':[(5,-2.25),(5.6,-1.8),(6.4,-1.7),(7.8,-2),(8,-4),(5.9,-3.7)]}
COL=None;GROUPS={};TERRAIN=None

def point(s,t,h=0):
    """Author in camera ground coordinates, emit canonical Blender x,-UnityZ,up."""
    dx=C*s+S*(t-WATER*Q)/Q;dz=-S*s+C*(t-WATER*Q)/Q
    return (1.35+dx,-(.20+dz),h)

def mesh(name,g,group,bevel=0,weld=True):
    ob=g.object(name,GROUPS[group],COL)
    bm=bmesh.new();bm.from_mesh(ob.data)
    if weld:bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    if bevel:
        bpy.context.view_layer.objects.active=ob;ob.select_set(True)
        mod=ob.modifiers.new('Applied broad coastal edge bevel','BEVEL');mod.width=bevel;mod.segments=1;mod.angle_limit=.5
        bpy.ops.object.modifier_apply(modifier=mod.name);ob.select_set(False)
    return ob

def sample_plan(plan):
    result=[]
    for i,a in enumerate(plan):
        b=plan[(i+1)%len(plan)]
        count=max(1,round(math.dist(a,b)/.65))
        for j in range(count):
            t=j/count;result.append((a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t))
    return result

def land(name,plan,height):
    coast=sample_plan(plan);n=len(coast)
    center=Vector((sum(x for x,y in coast)/n,sum(y for x,y in coast)/n))
    profile=[(1.10,-1.45,'M_CoastWet'),(1.03,-.06,'M_CoastWet'),(1,.07,'M_CoastWet'),
             (.985,.15,'M_CoastStone'),(.99,.22,'M_CoastStoneLight'),(.947,.48,'M_CoastStone'),
             (.965,.53,'M_CoastStoneLight'),(.905,.92,'M_CoastStone'),(.89,1,'M_CoastGrass')]
    g=G();verts=[]
    for level,(scale,h,mat) in enumerate(profile):
        for i,p in enumerate(coast):
            v=center+(Vector(p)-center)*scale
            # Coherent broad fracture/tilt, shared across courses rather than noisy spikes.
            offset=.035*math.sin(i*1.3+2)*max(h,0)
            z=h*height+(.04*math.sin(i*.71)+.025*math.cos(i*.33))*max(h,0)*height
            verts.append(point(v.x+offset,v.y,z))
    for j in range(len(profile)-1):
        for i in range(n):
            ni=(i+1)%n
            mat=profile[j+1][2]
            if j in (3,5) and i%7==0:mat='M_CoastStone'
            g.add([verts[j*n+i],verts[j*n+ni],verts[(j+1)*n+ni],verts[(j+1)*n+i]],[(0,1,2,3)],mat)
    g.add(verts[:n],[tuple(reversed(range(n)))],'M_CoastWet')
    g.add(verts[-n:],[tuple(range(n))],'M_CoastGrass')
    mesh('Land_'+name+'_ConnectedStrata',g,'Shoreline',.025)

def distance(p,plan):
    best=100
    inside=False
    for a,b in zip(plan,plan[1:]+plan[:1]):
        pa=Vector(p)-Vector(a);ba=Vector(b)-Vector(a)
        t=max(0,min(1,pa.dot(ba)/ba.length_squared));best=min(best,(pa-ba*t).length)
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return 0 if inside else best

def bed_depth(s,t):
    d=min(distance((s,t),p) for p in PLANS.values())
    return -.12-2.6*min(1,d/3.0)**.8

def seabed():
    # Covers combined desktop/phone rays with margin, not a giant ocean mesh.
    n,m=65,49;verts=[];g=G()
    for j in range(m):
        t=-6+j*12/(m-1)
        for i in range(n):
            s=-9+i*18/(n-1);h=bed_depth(s,t)
            verts.append(point(s,t,h))
    for j in range(m-1):
        for i in range(n-1):
            ids=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            z=sum(verts[k][2] for k in ids)/4
            mat='M_CoastWet' if z>-.3 else 'M_SeabedSand'
            g.add([verts[k] for k in ids],[(0,1,2,3)],mat)
    # Closed skirt and sole, with exact shared edge coordinates (welded in mesh()).
    edge=list(range(n))+[j*n+n-1 for j in range(1,m)]+list(range((m-1)*n+n-2,(m-1)*n-1,-1))+[j*n for j in range(m-2,0,-1)]
    for a,b in zip(edge,edge[1:]+edge[:1]):
        p,q=verts[a],verts[b];g.add([p,q,(q[0],q[1],-3.5),(p[0],p[1],-3.5)],[(0,1,2,3)],'M_SeabedSand')
    bottom=[(verts[k][0],verts[k][1],-3.5) for k in reversed(edge)]
    g.add(bottom,[tuple(range(len(bottom)))],'M_SeabedSand')
    mesh('Bathymetry_ShallowShelves_DeepChannel',g,'Seabed')

def box(g,s,t,h,size,mat,amount=.025):K.bevel_box(g,point(s,t,h),size,mat,amount)

def shrubs(s,t,h,scale,seed):
    p=Vector(point(s,t,8));hit,normal,index,distance=TERRAIN.ray_cast(p,Vector((0,0,-1)))
    if hit is None or hit.z<.05:return
    h=hit.z-.025
    rng=random.Random(seed);g=G()
    for i,(dx,dt,z,r) in enumerate([(-.23,0,.20,.28),(.12,.05,.29,.35),(.32,-.07,.16,.25),(-.04,-.17,.15,.27)]):
        g.ellipsoid(point(s+dx*scale,t+dt*scale,h+z*scale),(r*scale,r*scale,.22*scale),12,5,'M_CoastGrassLight' if i==1 else 'M_CoastGrass')
    mesh('Vegetation_AuthoredCluster_%02d'%seed,g,'Details')

def details():
    # Connected stone landing with inset broad masonry; timber jetty toward sheltered water.
    g=G();plan=[(3.10,.64),(4.20,.64),(4.20,1.26),(3.10,1.26)]
    vs=[point(s,t,z) for z in (-.08,.49) for s,t in plan]
    g.add(vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'M_CoastStone')
    for i in range(4):
        s=3.24+i*.26;g.beam(point(s,.66,.51),point(s,1.24,.51),.25,.045,'M_CoastStoneLight',.012)
    mesh('Quay_Landing',g,'Details',.025)
    g=G()
    # Physical plan is specified in screen-ground basis so the dock leads into the channel.
    for i in range(9):
        s=2.75+i*.085
        g.beam(point(s,.65,.40),point(s,1.19,.40),.095,.08,'M_DeckWood' if i%4 else 'M_WoodHighlight',.012)
    for s,t in [(2.77,.68),(2.77,1.16),(3.42,.68),(3.42,1.16)]:
        p=point(s,t,0);g.beam((p[0],p[1],-.8),(p[0],p[1],.68),.11,.11,'M_WoodRecess',.015)
    for t in (.68,1.16):g.beam(point(2.77,t,.68),point(3.42,t,.68),.035,.035,'M_Rope')
    mesh('Jetty_Timber_BracedPosts',g,'Details')
    # Low harbour beacon on the grass shoulder, not a second gameplay building.
    g=G();base=point(3.65,.90,.48)
    K.lathe(g,[(0,.29),(.10,.29),(.13,.22),(.83,.18),(.87,.24),(.93,.24)],12,'M_RailIvory',base)
    K.lathe(g,[(.88,.245),(.96,.245)],12,'M_SafetyOrange',base)
    K.lathe(g,[(.97,.16),(1.15,.16)],12,'M_HullNavy',base)
    K.lathe(g,[(1.16,.24),(1.28,0)],12,'M_HullNavy',base)
    for k in range(4):
        a=k*math.pi/2;x=base[0]+.17*math.cos(a);y=base[1]+.17*math.sin(a)
        g.beam((x,y,base[2]+.96),(x,y,base[2]+1.17),.035,.035,'M_Steel')
    g.vertices=[(x,y,base[2]+(z-base[2])*.72) for x,y,z in g.vertices]
    mesh('HarbourBeacon_IvoryOrange',g,'Details')
    # A purposeful path from rear coast to landing, with shallow stone steps.
    g=G()
    section=[(1.04,.05),(1.76,.05)]
    for i in range(5,-1,-1):section.extend([(1.04+(i+1)*.12,.53+i*.10),(1.04+i*.12,.53+i*.10)])
    n=len(section);vs=[point(s,t,h) for s in (3.93,4.37) for t,h in section]
    g.add(vs,[tuple(reversed(range(n))),tuple(range(n,n*2))],'M_CoastStone')
    for i in range(n):
        j=(i+1)%n;mat='M_CoastStoneLight' if abs(section[i][1]-section[j][1])<1e-6 and section[i][1]>.1 else 'M_CoastStone'
        g.add([vs[i],vs[j],vs[n+j],vs[n+i]],[(0,1,2,3)],mat)
    mesh('Landing_StoneSteps',g,'Details',.012)
    # Temperate wind-shaped growth; placed groups, no random detail scatter.
    for seed,(s,t,h,sc) in enumerate([(2.5,2.7,1.0,.75),(3.3,1.9,1.0,.7),(4.1,1.8,1.0,.9),(4.85,1.4,1.0,.7),(5.6,1.8,1,1.1),(6.5,1.3,1,.8),(-5.5,-.20,.42,.7),(-6.2,.05,.42,.9),(6.6,-2.6,.25,.8)],1):shrubs(s,t,h,sc,seed)
    for seed,(s,t,h) in enumerate([(6.6,.98,1.0)],1):
        hit,normal,index,distance=TERRAIN.ray_cast(Vector(point(s,t,8)),Vector((0,0,-1)))
        if hit is None or hit.z<.05:continue
        h=hit.z-.025
        g=G();p=Vector(point(s,t,h));top=p+Vector((.20,.08,1.15))
        g.beam(p,top,.11,.10,'M_WoodRecess',.018)
        for dx,dy,dz,r in [(-.28,0,-.10,.48),(.27,.02,-.03,.45),(.0,.15,.22,.50)]:
            g.ellipsoid(top+Vector((dx,dy,dz)),(r,r*.85,.40),12,6,'M_CoastGrass' if dz<0 else 'M_CoastGrassLight')
        mesh('WindTree_%d'%seed,g,'Details')
    # Three readable grass tufts on connected low ledges, rather than pebble scatter.
    g=G()
    for s,t,h in [(-4.7,-.4,.43),(-6.7,-.1,.43),(6.0,-2.45,.25)]:
        hit,normal,index,distance=TERRAIN.ray_cast(Vector(point(s,t,8)),Vector((0,0,-1)))
        if hit is None or hit.z<.05:continue
        h=hit.z-.015
        p=Vector(point(s,t,h))
        for k in range(5):
            a=k*2.4;tip=p+Vector((.13*math.cos(a),.13*math.sin(a),.24+.02*(k%2)))
            g.beam(p,tip,.026,.018,'M_CoastGrassLight')
    mesh('TidalLedge_GrassTufts',g,'Details')

def plan_box(g,s,t,z,ds,dt,dz,mat,bevel=.012):
    """Timber edges follow the authored quay basis, not unrelated world axes."""
    g.beam(point(s-ds/2,t,z),point(s+ds/2,t,z),dt/Q,dz,mat,bevel)

def rope(g,path,r=.018,mat='M_Rope',sides=6):
    g.tube([point(*v) for v in path],[r]*len(path),sides,mat)

def working_quay():
    # One composed working landing, kept beyond the existing t<=1.7 clear channel.
    # The original Day3 render guides construction/prop grouping, not a new service.
    g=G()
    for i in range(23):
        a=.12+i*.103
        # Tight seams, broad warm planks, restrained variation rather than scratches.
        plan_box(g,a,2.56,.625,.100,1.02,.095,
                 'M_WoodHighlight' if i%7==0 else 'M_DeckWood',.008)
        for t in (2.08,3.02):
            p=point(a,t,.676)
            K.lathe(g,[(0,.012),(.005,.012)],8,'M_Steel',p)
    for t in (2.11,2.95):
        plan_box(g,1.25,t,.50,2.56,.12,.20,'M_WoodRecess',.018)
        plan_box(g,1.25,t,.58,2.62,.045,.16,'M_DeckWood',.012)
    mesh('WorkingQuay_PlankedDeck_Joists',g,'Details')
    g=G();ropegeo=G()
    for s in (.06,1.25,2.48):
        for t in (2.07,3.02):
            p=point(s,t,0)
            K.lathe(g,[(-1.1,.09),(-.06,.105),(.08,.10),(.83,.095),(.875,.08)],12,'M_WoodRecess',p)
            # Warm caps and concentric end grain keep pilings readable from gameplay.
            K.lathe(g,[(.835,.098),(.88,.098)],12,'M_DeckWood',p)
            for radius in (.043,.070):
                K.ring(g,radius,.006,.881,.885,'M_WoodRecess',p[:2],12)
            K.lathe(g,[(-.18,.106),(.06,.106)],12,'M_CoastWet',p)
            spiral=[(s+.106*math.cos(a),t+.106*Q*math.sin(a),.72+a*.009)
                    for a in [i*math.tau/16 for i in range(33)]]
            rope(ropegeo,spiral,.014)
            if t<2.5:
                # Suspended mooring loop, fitted to its post rather than floating.
                path=[(s+.09*math.sin(a),t-.035-.09*math.cos(a),.62-.29*(1-math.cos(a))/2)
                      for a in [i*math.tau/24 for i in range(24)]]
                rope(ropegeo,path,.018)
        # Cross braces meet the posts/joists and extend down through the waterline.
        g.beam(point(s,2.07,-.52),point(s,3.02,.45),.085,.085,'M_DeckWood',.01)
    for a,b in [(.06,1.25),(1.25,2.48)]:
        g.beam(point(a,2.07,-.35),point(b,2.07,.45),.10,.09,'M_WoodRecess',.01)
    mesh('WorkingQuay_WetPilings_Braces',g,'Details')
    mesh('WorkingQuay_FittedMooringRopes',ropegeo,'Details')
    # Coarse hanging net: individual closed strands, no texture or alpha shader.
    g=G()
    for i in range(9):
        s=.17+i*.085
        path=[(s,2.025,.63),(s+.018,1.99,.44),(s+.035,1.97,.23),(s+.045,1.99,.07)]
        rope(g,path,.010,'M_HullNavy',5)
    for i in range(5):
        z=.09+i*.13
        rope(g,[(.17+j*.085+.04*(.63-z)/.56,1.98+.045*((z-.32)/.32)**2,z-.025*math.sin(j*math.pi/8)) for j in range(9)],.010,'M_HullNavy',5)
    rope(g,[(.16,2.025,.65),(.50,1.99,.60),(.90,2.025,.65)],.018)
    for s in (.22,.50,.81):g.ellipsoid(point(s,1.995,.60),(.035,.035,.045),10,4,'M_SafetyOrange')
    mesh('WorkingQuay_DrapedFishingNet',g,'Details')
    # Open, slatted fish crates. Every board has thickness and a visible top rim.
    def crate(s,t,z,ds,dt,height,colour):
        g=G()
        plan_box(g,s,t,z+.025,ds,dt,.05,'M_WoodRecess')
        for layer in range(3):
            h=z+.06+layer*(height-.06)/3
            for side in (-1,1):
                plan_box(g,s,t+side*(dt/2-.025),h,ds,.045,.055,colour,.008)
                plan_box(g,s+side*(ds/2-.025),t,h,.045,dt,.055,colour,.008)
        for a in (-1,1):
            for b in (-1,1):plan_box(g,s+a*(ds/2-.025),t+b*(dt/2-.025),z+height/2,.045,.045,height,'M_WoodRecess',.006)
        for side in (-1,1):
            plan_box(g,s,t+side*dt/2,z+height,ds+.045,.045,.05,colour,.009)
            plan_box(g,s+side*ds/2,t,z+height,.045,dt+.045,.05,colour,.009)
        return g
    g=crate(1.30,2.40,.675,.49,.30,.27,'M_DeckWood')
    g.merge(crate(1.80,2.43,.675,.38,.28,.23,'M_SafetyOrange'))
    g.merge(crate(1.80,2.43,.905,.38,.28,.21,'M_DeckWood'))
    mesh('WorkingQuay_StackedSlattedCrates',g,'Details',weld=False)
    g=G()
    for i in range(3):
        s=1.15+i*.13;t=2.38+(i%2)*.06
        g.ellipsoid(point(s,t,.835),(.055,.14,.040),12,5,'M_FishSilver')
        p=point(s,t-.11,.84);g.ellipsoid(p,(.065,.05,.028),8,3,'M_HullBlue')
    mesh('WorkingQuay_SilverFishInTray',g,'Details')
    # Pair of blue working barrels and warm lids; metal bands are separate courses.
    g=G()
    for s,t in [(2.15,2.44),(2.44,2.44)]:
        p=point(s,t,.675)
        K.lathe(g,[(0,.12),(.045,.145),(.20,.16),(.35,.145),(.39,.12)],14,'M_HullBlue',p)
        for z,rad in [(.06,.151),(.30,.156)]:K.lathe(g,[(z,rad),(z+.028,rad)],14,'M_Steel',p)
        K.lathe(g,[(.39,.12),(.405,.12)],14,'M_DeckWood',p)
        for ds in (-.035,.035):
            g.beam(point(s+ds,t-.075,.675+.408),point(s+ds,t+.075,.675+.408),.007,.004,'M_WoodRecess')
    mesh('WorkingQuay_Barrels_BandedLids',g,'Details')
    # Coiled rope sits on the planks; a small life ring hangs from a dock post.
    g=G()
    spiral=[]
    for i in range(81):
        a=i*math.tau/20;r=.035+.0018*i
        spiral.append((.62+r*math.cos(a),2.68+r*Q*math.sin(a),.693+.001*math.sin(a)))
    rope(g,spiral,.014)
    rope(g,[(.77,2.68,.693),(.87,2.66,.693),(.95,2.75,.693)],.014)
    mesh('WorkingQuay_DeckRopeCoil',g,'Details')
    g=G();center=Vector(point(2.48,2.035,.32))
    tangent=Vector(point(1,0,0))-Vector(point(0,0,0));tangent.normalize()
    # Closed toroidal body, alternating ivory/orange quarters, in quay-front plane.
    verts=[]
    for i in range(24):
        a=i*math.tau/24
        for j in range(8):
            b=j*math.tau/8
            verts.append(center+tangent*((.16+.035*math.cos(b))*math.cos(a))+Vector((0,0,(.16+.035*math.cos(b))*math.sin(a)))+Vector(point(0,-.035*Q*math.sin(b),0))-Vector(point(0,0,0)))
    for i in range(24):
        for j in range(8):
            ids=[i*8+j,((i+1)%24)*8+j,((i+1)%24)*8+(j+1)%8,i*8+(j+1)%8]
            g.add([verts[k] for k in ids],[(0,1,2,3)],'M_RailIvory' if (i//3)%2 else 'M_SafetyOrange')
    rope(g,[(2.48,2.025,.72),(2.48,2.00,.53),(2.48,2.025,.48)],.014)
    mesh('WorkingQuay_Lifering_PostTie',g,'Details')
    # Bounded detail upgrade to existing beacon jetty: wet feet, caps and rope coil.
    g=G()
    for s,t in [(2.77,.68),(2.77,1.16),(3.42,.68),(3.42,1.16)]:
        p=point(s,t,-.11);K.lathe(g,[(0,.075),(.19,.075)],10,'M_CoastWet',p)
        p=point(s,t,.69);K.lathe(g,[(0,.065),(.015,.065)],10,'M_DeckWood',p)
        rope(g,[(s+.076*math.cos(a),t+.076*Q*math.sin(a),.59+a*.004) for a in [i*math.tau/12 for i in range(25)]],.010)
    mesh('BeaconJetty_FittedRopes_Caps_WetFeet',g,'Details')

def fractures():
    for i,(s,t,h) in enumerate([(1.15,2.45,.78),(2.8,1.92,.83),(3.08,1.30,.90),(4.8,.92,.84)]):
        g=G();vs=[]
        for j,(z,f,back) in enumerate([(-.08,1,0),(.18,1.1,.03),(.46,.85,.10),(h,.85,.26)]):
            for k,(dx,dt) in enumerate([(-.20,-.10),(.18,-.14),(.24,.25),(-.15,.28)]):
                vs.append(point(s+dx*f+.035*math.sin(k*2+j+i),t+dt*f+back,z+max(z,0)*.09*math.sin(k*2+i)))
        for j in range(3):
            for k in range(4):g.add([vs[j*4+k],vs[j*4+(k+1)%4],vs[(j+1)*4+(k+1)%4],vs[(j+1)*4+k]],[(0,1,2,3)],'M_CoastStoneLight' if k==0 else 'M_CoastStone')
        g.add(vs[:4],[(3,2,1,0)],'M_CoastWet');g.add(vs[-4:],[(0,1,2,3)],'M_CoastStoneLight')
        mesh('Land_AttachedFracture_%d'%i,g,'Shoreline',.035)

def build():
    global COL,TERRAIN
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    B.PALETTE.update(PAL);B.MATERIALS.update({k:B.material(k,v) for k,v in B.PALETTE.items()})
    COL=bpy.data.collections.new('ENV_EXPORT_ONLY');scene.collection.children.link(COL)
    K.COLLECTION=COL
    root=bpy.data.objects.new('Catchline_GullHarbourMouth',None);COL.objects.link(root)
    root['unity_waterline_y']=0.0
    for name in ('Shoreline','Seabed','Details'):
        ob=bpy.data.objects.new(name,None);COL.objects.link(ob);ob.parent=root;GROUPS[name]=ob
    land('Headland',PLANS['Headland'],1.0);land('TidalIslet',PLANS['TidalIslet'],.43);land('OuterShelf',PLANS['OuterShelf'],.25)
    fractures();bpy.context.view_layer.update()
    verts=[];faces=[]
    for ob in COL.objects:
        if ob.type=='MESH' and ob.parent==GROUPS['Shoreline']:
            off=len(verts);verts.extend(v.co[:] for v in ob.data.vertices)
            faces.extend(tuple(off+i for i in p.vertices) for p in ob.data.polygons)
    TERRAIN=BVHTree.FromPolygons(verts,faces)
    seabed();details();working_quay()
    # Camera review: bring working quay slightly forward; maintain >1.7m clear boundary.
    shift=Vector(point(0,-.20,0))-Vector(point(0,0,0))
    for ob in COL.objects:
        if ob.type=='MESH' and ob.name.startswith('WorkingQuay_'):
            for v in ob.data.vertices:v.co+=shift
            ob.data.update()
    bpy.context.view_layer.update()
    stats=[B.mesh_stats(o) for o in COL.objects if o.type=='MESH']
    (OUT/'build-metrics.json').write_text(json.dumps(dict(asset='GullHarbourMouth',materials=PAL,
       triangles=sum(a['triangles'] for a in stats),parts=stats,waterline_unity_y=0,
       preview_world_offset_unity=[0,WATER,0],coast_plans_screen_ground=PLANS),indent=2)+'\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'GullHarbourMouth.blend'))

def append_environment(scene):
    with bpy.data.libraries.load(str(OUT/'GullHarbourMouth.blend'),link=False) as (src,dst):dst.collections=['ENV_EXPORT_ONLY']
    col=dst.collections[0];scene.collection.children.link(col)
    root=next(o for o in col.objects if o.name=='Catchline_GullHarbourMouth')
    root.scale=(1,-1,1);root.location.z=WATER

def preview(draft=False):
    # Reuse ART-010's exact placement/camera functions read-only. Its standalone
    # mode dispatcher is intentionally omitted, so no ART-010 files are regenerated.
    source=Path(__file__).with_name('render_first_voyage10.py');tree=ast.parse(source.read_text())
    for i,n in enumerate(tree.body):
        if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Name) and n.test.left.id=='MODE':
            tree.body=tree.body[:i];break
    R=types.ModuleType('ref11');R.__file__=str(source);exec(compile(tree,str(source),'exec'),R.__dict__)
    R.MODE='refined';R.make_scene(broad=False,contact=False)
    scene=bpy.context.scene;append_environment(scene)
    bpy.data.objects.remove(bpy.data.objects['REF_Water_NotRuntime'],do_unlink=True)
    # Actual depth-supported reference water. Not exported and not a runtime shader.
    mat=B.material('REF_ONLY_Art011_Water','#168F9F',.36)
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Transmission Weight'].default_value=.60;shader.inputs['IOR'].default_value=1.333
    shader.inputs['Specular IOR Level'].default_value=.16
    shader.inputs['Emission Color'].default_value=B.linear_colour('#168F9F');shader.inputs['Emission Strength'].default_value=.22
    absorption=mat.node_tree.nodes.new('ShaderNodeVolumeAbsorption');absorption.inputs['Color'].default_value=B.linear_colour('#64C7C4');absorption.inputs['Density'].default_value=.10
    mat.node_tree.links.new(absorption.outputs[0],mat.node_tree.nodes.get('Material Output').inputs['Volume'])
    bpy.ops.mesh.primitive_cube_add(size=1,location=(1,0,-3.32));water=bpy.context.object;water.name='REF_ONLY_DepthWater';water.scale=(80,80,6);water.data.materials.append(mat)
    # Tiny broken shoreline contact strokes are illustrative, not exported water effects.
    foam=B.material('REF_ONLY_ShoreContact','#CBE4DB',.8)
    for name,plan in PLANS.items():
        for i,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
            if i%3==0:continue
            p=Vector(a).lerp(Vector(b),.15);q=Vector(a).lerp(Vector(b),.68)
            if (p-q).length>1.1:q=p+(q-p).normalized()*1.1
            # Ribbons sit just seaward of the wet toe, not around every inland surface.
            g=G();vs=[]
            for v in (p,q):
                x,y,z=point(v.x,v.y,0);vs.extend([(x,-y-.025,WATER+.008),(x,-y+.025,WATER+.008)])
            mesh_=bpy.data.meshes.new('Reference contact');mesh_.from_pydata(vs,[],[(0,1,3,2)]);mesh_.materials.append(foam)
            ob=bpy.data.objects.new('REF_ONLY_ShoreFoam',mesh_);scene.collection.objects.link(ob)
    scene.cycles.samples=16 if draft else 32;scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6
    if draft:
        scene.render.resolution_x=960;scene.render.resolution_y=600;scene.camera.data.ortho_scale=10.24
        scene.render.filepath=str(OUT/'Draft-review.png');bpy.ops.render.render(write_still=True);return
    scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.camera.data.ortho_scale=6.4*1440/900
    scene.render.filepath=str(OUT/'Beauty-desktop.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Composition-review.blend'));bpy.ops.render.render(write_still=True)
    scene.render.resolution_x=844;scene.render.resolution_y=390;scene.camera.data.ortho_scale=6.4*844/390
    scene.render.filepath=str(OUT/'Beauty-phone.png');bpy.ops.render.render(write_still=True)
    print('ART-011 composition renders ready',flush=True)

def export():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'GullHarbourMouth.blend'))
    bpy.ops.object.select_all(action='DESELECT');col=bpy.data.collections['ENV_EXPORT_ONLY']
    for ob in col.objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=bpy.data.objects['Catchline_GullHarbourMouth']
    # Explicitly bake Z-up -> Y-up into vertex data exactly once. Blender's
    # experimental bake_space_transform double-converts nested empty groups.
    # All source objects are at the origin with identity transforms.
    for ob in col.objects:
        if ob.type=='MESH':
            for v in ob.data.vertices:
                x,y,z=v.co;v.co=(-x,z,-y)
            # Actual Unity import mirrors FBX X. Compensate in exported vertices only,
            # then reverse winding for the reflection; canonical source stays untouched.
            bm=bmesh.new();bm.from_mesh(ob.data)
            bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
            ob.data.update()
    dest=ROOT/'Assets/Art/Models/Environment/GullHarbourMouth.fbx';dest.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=str(dest),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=False,bake_space_transform=False,use_triangles=True,
        mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,use_custom_props=True)
    print('ART-011 environment exported',flush=True)

def detail(quay=False):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'Composition-review.blend'))
    scene=bpy.context.scene;cam=scene.camera
    p=point(1.28,2.35,.50) if quay else point(3.7,1.35,.50);target=Vector((p[0],-p[1],p[2]+WATER))
    forward=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));cam.location=target-forward*40
    cam.data.ortho_scale=5.4;scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.cycles.samples=32
    scene.render.filepath=str(OUT/('Working-quay-detail.png' if quay else 'Shore-detail.png'));bpy.ops.render.render(write_still=True)

OUT.mkdir(parents=True,exist_ok=True)
if __name__=='__main__':
    mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'preview'
    if mode=='preview':build();preview()
    elif mode=='draft':build();preview(True)
    elif mode=='export':export()
    elif mode=='detail':detail()
    elif mode=='quay-detail':detail(True)
    else:raise ValueError(mode)

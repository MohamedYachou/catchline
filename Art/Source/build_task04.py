"""Task 04 additions. Run in Blender with -- B or -- C (or asset names).
All geometry is source X right, -Y bow, Z up; shop fronts face +Y.
"""
import sys, math, json, importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('gull',Path(__file__).with_name('build_gull_harbour.py'))
K=importlib.util.module_from_spec(spec);spec.loader.exec_module(K)
G=K.G; box=K.bevel_box; lathe=K.lathe; ring=K.ring; part=K.part
NAVY='M_HullNavy'; WOOD='M_DeckWood'; IVORY='M_RailIvory'; STEEL='M_Steel'; ROPE='M_Rope'; TEAL='M_SeaTeal'; ORANGE='M_SafetyOrange'

def grounded(g):
    lo=[min(v[i] for v in g.vertices) for i in range(3)]
    hi=[max(v[i] for v in g.vertices) for i in range(3)]
    shift=[(lo[i]+hi[i])/2 if i<2 else lo[i] for i in range(3)]
    g.vertices=[tuple(v[i]-shift[i] for i in range(3)) for v in g.vertices]

def coil(g,offset=(0,0,0),radius=.28):
    x,y,z=offset
    path=[]
    for i in range(100):
        a=i*math.tau/25; r=radius*(.24+.76*i/99)
        path.append((x+r*math.cos(a),y+r*math.sin(a),z+.026))
    g.tube(path,[.026]*len(path),6,ROPE)
    g.tube([path[-1],(x+radius+.10,y-.12,z+.026)],[.026,.026],6,ROPE)

def anchor(g,offset=(0,0,0),scale=1):
    a=G()
    a.beam((0,0,.10),(0,0,.60),.055,.055,STEEL,.01)
    a.beam((-.20,0,.43),(.20,0,.43),.05,.05,STEEL,.01)
    a.torus((0,0,.64),.055,.015,STEEL)
    a.tube([(-.25,0,.22),(-.18,0,.10),(0,0,.07),(.18,0,.10),(.25,0,.22)],[.04]*5,8,STEEL)
    for side in (-1,1):
        a.extrude_polygon([(side*.17,-.07),(side*.29,0),(side*.17,.07)],.19,.24,STEEL)
    g.merge(a,offset,scale)

def crate(g,offset=(0,0,0),scale=1,fish=False):
    a=G();box(a,(0,0,.025),(.48,.34,.05),WOOD,.009)
    for side in (-1,1):
        for z in (.09,.19,.29):
            box(a,(side*.225,0,z),(.035,.34,.07),WOOD,.005)
            box(a,(0,side*.155,z),(.48,.03,.07),WOOD,.005)
    for x in (-.21,.21):
        for y in (-.14,.14):box(a,(x,y,.18),(.035,.035,.31),'M_WoodHighlight',.005)
    if fish:
        for x in (-.14,0,.14):
            a.ellipsoid((x,0,.28),(.055,.13,.04),10,4,'M_FishSilver')
            a.extrude_polygon([(x,-.08),(x-.05,-.17),(x+.05,-.17)],.265,.285,NAVY)
            a.ellipsoid((x+.038,.075,.30),(.011,.011,.009),8,2,'M_Rubber')
    g.merge(a,offset,scale)

def barrel(g,offset=(0,0,0),scale=1):
    a=G();lathe(a,[(0,.23),(.06,.26),(.32,.29),(.60,.25),(.64,.23)],12,WOOD)
    for z,r in ((.08,.267),(.32,.294),(.56,.263)):ring(a,r,.016,z,z+.045,STEEL,sides=12)
    for i in range(12):
        t=i*math.tau/12
        a.tube([(.257*math.cos(t),.257*math.sin(t),.12),(.292*math.cos(t),.292*math.sin(t),.32),(.255*math.cos(t),.255*math.sin(t),.54)],[.004]*3,4,'M_WoodRecess')
    box(a,(.10,0,.648),(.05,.05,.016),'M_WoodRecess',.003)
    g.merge(a,offset,scale)

def net(g,width,depth,z=.025,offset=(0,0,0),vertical=False):
    a=G();nx=max(2,round(width/.16));ny=max(2,round(depth/.16))
    for i in range(nx+1):
        x=-width/2+i*width/nx
        a.beam((x,-depth/2,z),(x,depth/2,z),.009,.009,TEAL)
    for i in range(ny+1):
        y=-depth/2+i*depth/ny
        a.beam((-width/2,y,z),(width/2,y,z),.009,.009,TEAL)
    if vertical:a.vertices=[(x,zz,y+depth/2) for x,y,zz in a.vertices]
    g.merge(a,offset)

def lantern(g,offset=(0,0,0),scale=1):
    a=G();lathe(a,[(0,.11),(.04,.11),(.07,.085),(.28,.085),(.32,.12),(.38,.02)],12,NAVY)
    lathe(a,[(.07,.07),(.28,.07)],12,'M_OilskinYellow')
    for i in range(4):
        t=i*math.tau/4;a.beam((.08*math.cos(t),.08*math.sin(t),.065),(.08*math.cos(t),.08*math.sin(t),.29),.015,.015,NAVY)
    a.torus((0,0,.42),.055,.012,STEEL);g.merge(a,offset,scale)

def deck_prop(name):
    g=G()
    if name=='RopeCoil':coil(g)
    elif name=='SmallAnchor':anchor(g)
    elif name=='Lantern':lantern(g)
    elif name=='Fender':
        lathe(g,[(0,.05),(.06,.10),(.40,.10),(.47,.05)],12,IVORY)
        ring(g,.102,.01,.12,.16,ORANGE);ring(g,.102,.01,.32,.36,ORANGE)
        g.torus((0,0,.51),.037,.014,ROPE)
    elif name=='TackleBox':
        box(g,(0,0,.11),(.42,.28,.22),NAVY,.025)
        box(g,(0,0,.23),(.44,.30,.055),TEAL,.018)
        g.tube([(-.08,0,.255),(-.08,0,.32),(.08,0,.32),(.08,0,.255)],[.012]*4,8,STEEL)
        for x in (-.12,.12):box(g,(x,-.155,.20),(.035,.018,.07),IVORY,.004)
    elif name=='NetBundle':
        for i in range(5):
            net(g,.55-i*.015,.28,.025+i*.025)
        for x in (-.18,.18):g.tube([(x,-.16,.04),(x,-.16,.17),(x,.16,.17),(x,.16,.04)],[.015]*4,6,ROPE)
    grounded(g);part(name,g)

def plaice():
    body=G();body.ellipsoid((0,-.026,.026),(.115,.154,.025),16,4,'M_WoodRecess')
    # Broad flat fins stop short of the tail; asymmetrical eyes both on upper side.
    for side in (-1,1):
        body.extrude_polygon([(side*.09,-.12),(side*.14,-.04),(side*.13,.06),(side*.06,.12)],.012,.022,'M_DeckWood')
    for x,y in ((.025,-.11),(.053,-.085)):
        body.ellipsoid((x,y,.049),(.012,.015,.008),8,2,IVORY)
        body.ellipsoid((x,y-.003,.056),(.006,.008,.004),8,2,'M_Rubber')
    for x,y in ((-.04,-.08),(-.06,.02),(.04,.04),(.07,-.02)):
        body.ellipsoid((x,y,.047),(.012,.017,.003),8,2,ORANGE)
    tail=G();tail.extrude_polygon([(-.035,.11),(-.065,.18),(.065,.18),(.035,.11)],.012,.024,'M_DeckWood')
    # Nose is -.18, tail +.18: exactly .36 m.
    for geom in (body,tail):geom.vertices=[(x,y,z-.001) for x,y,z in geom.vertices]
    part('PlaiceBody',body);part('PlaiceTail',tail,(0,.11,.017))
    K.NOTES.append('Plaice nose-to-tail 0.36m, flat horizontal body; both eyes on top. Tail pivot at join.')

def cod():
    K.FISH['Cod']=(.70,.145,.135,'M_KelpGreen')
    K.fish('Cod')
    body=K.bpy.data.objects['CodBody']
    # Cod's tiny chin barbel is joined into its existing body part.
    g=G();g.tube([(0,-.25,.055),(0,-.28,.027)],[.008,.004],6,IVORY)
    obj=g.object('_Barbel',K.ASSET_ROOT,K.COLLECTION)
    K.bpy.ops.object.select_all(action='DESELECT');body.select_set(True);obj.select_set(True)
    K.bpy.context.view_layer.objects.active=body;K.bpy.ops.object.join()

def harbour_prop(name):
    g=G()
    if name=='Barrel':barrel(g)
    elif name=='CrateStack':
        crate(g,(-.25,0,0));crate(g,(.25,.08,0));crate(g,(0,.03,.345))
    elif name=='FishCrate':crate(g,fish=True)
    elif name=='Lifebuoy':
        g.torus((0,0,.32),.245,.07,IVORY)
        for x,z in ((-.245,.32),(.245,.32),(0,.075),(0,.565)):
            box(g,(x,-.006,z),(.11,.15,.10),ORANGE,.016)
        g.torus((0,0,.32),.328,.012,ROPE)
    elif name=='NetRack':
        for x in (-.8,.8):g.beam((x,0,0),(x,0,1.6),.085,.085,WOOD,.008)
        g.beam((-.9,0,1.5),(.9,0,1.5),.08,.08,WOOD)
        net(g,1.5,1.15,offset=(0,0,.28),vertical=True)
        for x in (-.8,.8):box(g,(x,0,.035),(.36,.50,.07),WOOD,.01)
    elif name=='MarketStallAwning':
        for x in (-1.1,1.1):
            for y in (-.65,.65):g.beam((x,y,0),(x,y,2.1),.07,.07,WOOD)
        for i in range(8):
            x=-1.05+i*.30
            for y0,y1 in ((-.82,0),(0,.82)):
                roof=G();roof.extrude_polygon([(x-.15,y0),(x+.15,y0),(x+.15,y1),(x-.15,y1)],2.05,2.09,TEAL if i%2 else IVORY)
                roof.vertices=[(xx,yy,zz+.20*(1-abs(yy)/.82)) for xx,yy,zz in roof.vertices];g.merge(roof)
        box(g,(0,-.77,1.98),(2.4,.08,.18),TEAL,.01)
        box(g,(0,0,.90),(2.2,.9,.09),WOOD,.015)
        crate(g,(-.63,0,.945),fish=True);crate(g,(.02,0,.945),fish=True)
    grounded(g);part(name,g)

def seagull():
    g=G()
    g.ellipsoid((0,.025,.17),(.085,.135,.09),12,5,IVORY)
    g.ellipsoid((0,-.085,.275),(.06,.06,.065),12,5,IVORY)
    g.tube([(0,-.12,.27),(0,-.20,.27)],[.025,.002],8,'M_OilskinYellow')
    g.extrude_polygon([(-.04,.10),(-.04,.20),(.04,.20),(.04,.10)],.17,.195,IVORY)
    for side in (-1,1):
        g.beam((side*.035,.015,.02),(side*.035,.015,.12),.013,.013,ORANGE)
        box(g,(side*.035,-.012,.012),(.045,.07,.024),ORANGE,.005)
        g.ellipsoid((side*.053,-.107,.29),(.008,.009,.009),8,2,'M_Rubber')
    part('SeagullBody',g)
    for side,label in ((-1,'L'),(1,'R')):
        w=G();w.ellipsoid((side*.075,.04,.185),(.024,.11,.055),10,4,'M_Steel')
        w.extrude_polygon([(side*.065,.07),(side*.065,.17),(side*.11,.12)],.17,.19,NAVY)
        part('Wing_'+label,w,(side*.07,-.025,.22))
    K.NOTES.append('Perched seagull 0.4m nose-to-tail; Wing_L/Wing_R shoulder pivots for flap.')

def board(g,x,y,width= .70,height=.90,chart=False):
    for dx in (-width*.42,width*.42):g.beam((x+dx,y,0),(x+dx,y,1.45),.055,.055,WOOD)
    box(g,(x,y,1.10),(width,.09,height),WOOD,.012)
    box(g,(x,y+.052,1.10),(width-.08,.016,height-.08),TEAL if chart else 'M_WoodRecess',.004)
    if chart:
        box(g,(x,y+.065,1.1),(width-.12,.015,height-.12),IVORY,.004)
        route=[(x-.22,y+.078,.85),(x-.08,y+.078,.94),(x-.12,y+.078,1.08),(x+.13,y+.078,1.17),(x+.21,y+.078,1.37)]
        g.tube(route,[.012]*len(route),6,TEAL)
        for px,py,pz in (route[0],route[-1]):g.ellipsoid((px,py+.004,pz),(.025,.006,.025),8,2,ORANGE)
        for z in (.90,1.05,1.20,1.35):g.beam((x-.24,y+.077,z),(x+.24,y+.077,z),.004,.004,STEEL)
    else:
        for dx,dz in ((-.14,.14),(.12,.18),(-.06,-.19)):
            box(g,(x+dx,y+.065,1.10+dz),(.18,.015,.23),IVORY,.004)
            g.beam((x+dx-.06,y+.076,1.1+dz),(x+dx+.055,y+.076,1.1+dz),.008,.006,NAVY)

def shop(name):
    g=G()
    if name=='FishMarket':
        crate(g,(-.85,.30,0),fish=True);crate(g,(.85,.30,0),fish=True);crate(g,(-.85,.30,.345),fish=True)
        g.beam((.8,0,0),(.8,0,1.8),.07,.07,WOOD);g.beam((.8,0,1.8),(.45,.30,1.8),.05,.05,STEEL)
        g.tube([(.45,.30,1.8),(.45,.30,1.22)],[.01]*2,8,STEEL)
        lathe(g,[(1.1,.18),(1.14,.18)],12,STEEL,(.45,.30,0))
        g.torus((.45,.30,1.55),.09,.022,IVORY)
    elif name=='HarbourMaster':
        board(g,-.85,.10,chart=True)
        g.beam((.85,.12,0),(.85,.12,2.5),.045,.045,STEEL)
        g.extrude_polygon([(.87,.12),(1.43,.12),(1.43,.145),(.87,.145)],1.9,2.35,ORANGE)
        box(g,(.85,.12,.045),(.30,.30,.09),NAVY,.02)
    elif name=='CrewOffice':board(g,-.85,.20,.90,1.0)
    elif name=='Chandlery':
        anchor(g,(-.9,.28,0));coil(g,(.8,.30,0),.23)
        box(g,(.8,.10,.40),(.7,.09,.80),WOOD,.02)
        # Display loops sit proud of the board toward the water.
        for z in (.26,.54):g.torus((.8,.17,z),.17,.025,ROPE)
    elif name=='Supplies':
        barrel(g,(-.90,.20,0));barrel(g,(-.65,.65,0),.8)
        for x in (.68,1.04):
            g.ellipsoid((x,.35,.23),(.17,.16,.23),10,4,ROPE)
            g.torus((x,.35,.43),.05,.015,'M_WoodRecess')
        lathe(g,[(0,.22),(.30,.25)],12,TEAL,(.85,.80,0),caps=False)
        lathe(g,[(0,.22),(.025,.22)],12,TEAL,(.85,.80,0));ring(g,.26,.02,.28,.32,IVORY,(.85,.80))
    part('ShopFront_'+name,g)
    K.NOTES.append('Ground root at door centre, front source +Y / Unity -Z. Central door approach remains clear.')

def sea(name):
    g=G()
    if name=='SandBank':
        outline=[(-2,-.55),(-1.65,-1),(.9,-1),(2,-.35),(1.7,.7),(.55,1),(-1.3,.85)]
        g.add([(x,y,0) for x,y in outline],[tuple(range(len(outline)))],ROPE)
        K.NOTES.append('4x2m, exactly planar at waterline; upward faces. Use two-sided material if viewed from below.')
    elif name=='SeaRockCluster':
        for i,(x,y,s) in enumerate(((-.65,0,1),(.55,.15,.7),(0,.6,.5))):
            a=G();a.ellipsoid((x,y,.42*s),(.65*s,.5*s,.42*s),9,3,STEEL);g.merge(a)
    elif name=='CliffSegment8m':
        # Constant end cross-sections: modular joins at x=+-4, without end overhang.
        profile=[(-1.4,0),(-1.25,1.45),(-.8,2.3),(.9,2.3),(1.4,0)]
        verts=[(x,y,z) for x in (-4,-2,0,2,4) for y,z in profile]
        g.add(verts,[(4,3,2,1,0),(20,21,22,23,24)],STEEL)
        for j in range(4):
            for i in range(5):
                ni=(i+1)%5;g.add(verts,[(j*5+i,(j+1)*5+i,(j+1)*5+ni,j*5+ni)],'M_KelpGreen' if i==2 else STEEL)
        K.NOTES.append('8m repeat along X; matching end profiles, level grassy top at 2.3m, grounded root.')
    elif name=='ChannelBuoy':
        lathe(g,[(0,.28),(.10,.43),(.25,.43),(.65,.22)],12,ORANGE)
        ring(g,.30,.02,.45,.53,IVORY);g.beam((0,0,.65),(0,0,1.30),.055,.055,NAVY)
        g.add([(-.20,-.03,1.1),(.20,-.03,1.1),(0,-.03,1.5),(-.20,.03,1.1),(.20,.03,1.1),(0,.03,1.5)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],ORANGE)
    elif name=='DistantShip':
        g.extrude_polygon([(-.75,4),(.75,4),(1,3),(1,-2.8),(0,-4),(-1,-2.8)],0,.65,NAVY)
        box(g,(0,1.25,1.1),(1.3,1.6,.9),IVORY,.06)
        box(g,(0,1.24,1.57),(1.4,1.7,.10),ORANGE,.02)
        box(g,(0,.40,1.13),(1.0,.04,.27),'M_HullBlue',.01)
        g.beam((0,1.5,1.62),(0,1.5,2.4),.05,.05,STEEL)
        K.NOTES.append('8m low-detail ship silhouette, grounded/waterline root; no interior.')
    if name=='SeaRockCluster': grounded(g)
    part(name,g)

B_ASSETS={
 **{n:('DeckProps',lambda n=n:deck_prop(n)) for n in ('RopeCoil','TackleBox','NetBundle','SmallAnchor','Fender','Lantern')},
 'Plaice':('Fish',plaice),'Cod':('Fish',cod),
 **{n:('Harbour',lambda n=n:harbour_prop(n)) for n in ('Barrel','CrateStack','FishCrate','Lifebuoy','NetRack','MarketStallAwning')},
 'Seagull':('Harbour',seagull),
 **{'ShopFront_'+n:('Harbour',lambda n=n:shop(n)) for n in ('FishMarket','HarbourMaster','CrewOffice','Chandlery','Supplies')},
 **{n:('Sea',lambda n=n:sea(n)) for n in ('SandBank','SeaRockCluster','CliffSegment8m','ChannelBuoy','DistantShip')},
}
def skiff():
    outline=[(-1.48,3), (1.48,3),(1.75,2.5),(1.75,-2.5),(.95,-3.13),(0,-3.5),(-.95,-3.13),(-1.75,-2.5),(-1.75,2.5)]
    n=len(outline);g=G()
    levels=[(.60,.88,-.65),(.88,.96,-.18),(1,1,.44),(.94,.97,.44),(.78,.90,-.55)]
    verts=[(x*sx,y*sy,z+(.09*(abs(y)/3.5)**2 if z>.4 else 0)) for sx,sy,z in levels for x,y in outline]
    for j in range(4):g.add(verts[j*n:(j+2)*n],[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],NAVY if j<2 else WOOD)
    g.add(verts[:n],[tuple(reversed(range(n)))],NAVY);g.add(verts[-n:],[tuple(range(n))],WOOD)
    v=[(x*sx,y*sy,z) for sx,sy,z in ((.85,.95,-.28),(.91,.973,-.18)) for x,y in outline]
    g.add(v,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],ORANGE)
    part('Hull',g)
    deck=G()
    def plank(x0,x1,y0,y1,col):
        if x1-x0>1e-6:box(deck,((x0+x1)/2,(y0+y1)/2,-.025),(x1-x0,y1-y0,.05),col,.003)
    for i in range(12):
        x0=-1.5+i*.25;x1=x0+.25;col=WOOD if i%3 else 'M_WoodHighlight'
        if x1<=-.4 or x0>=.4:plank(x0,x1,-2.5,2.5,col)
        else:
            plank(x0,x1,-2.5,-1.5,col);plank(x0,x1,-.5,2.5,col)
            if x0<-.4:plank(x0,-.4,-1.5,-.5,col)
            if x1>.4:plank(.4,x1,-1.5,-.5,col)
    part('PlankDeck',deck)
    rail=G()
    for i,(x,y) in enumerate(outline):
        q=outline[(i+1)%n]
        rail.beam((x*.97,y*.985,.47+.09*(abs(y)/3.5)**2),(q[0]*.97,q[1]*.985,.47+.09*(abs(q[1])/3.5)**2),.11,.08,IVORY,.012)
    path=[(x*1.005,y*1.003,.39+.09*(abs(y)/3.5)**2) for x,y in outline]
    rail.tube(path+[path[0]],[.035]*(len(path)+1),8,ROPE);part('IvoryGunwale',rail)
    motor=G();box(motor,(0,3.22,.35),(.45,.42,.40),NAVY,.06)
    box(motor,(0,3.22,.51),(.46,.43,.095),ORANGE,.025)
    motor.beam((0,3.24,.18),(0,3.32,-.60),.13,.15,STEEL,.015)
    box(motor,(0,3.33,-.58),(.23,.32,.08),NAVY,.018)
    motor.beam((0,3.0,.29),(.32,2.77,.30),.035,.04,'M_Rubber');part('OutboardMotor',motor)
    prop=G();prop.tube([(0,3.27,-.60),(0,3.47,-.60)],[.045,.03],10,STEEL)
    for x,z,rx,rz in ((.10,-.60,.10,.045),(-.10,-.60,.10,.045),(0,-.50,.045,.10),(0,-.70,.045,.10)):
        prop.ellipsoid((x,3.40,z),(rx,.015,rz),8,3,STEEL)
    part('Propeller',prop,(0,3.40,-.60))
    console=G();box(console,(1,2,.32),(.72,.62,.64),IVORY,.055)
    box(console,(1,1.98,.65),(.76,.65,.065),NAVY,.018)
    box(console,(1,1.65,.57),(.32,.035,.14),'M_HullBlue',.01)
    console.torus((1,1.60,.48),.17,.024,STEEL)
    for dx,dz in ((-.14,0),(.14,0),(0,.14)):console.beam((1,1.60,.48),(1+dx,1.60,.48+dz),.02,.02,STEEL)
    part('Console',console)
    for i,y in enumerate((1.75,0,-1.75),1):
        sock=G();ring(sock,.065,.016,.45,.61,STEEL,(-1.68,y),12)
        part('RodSocket_'+str(i),sock,(-1.68,y,.45))
    hold=G();tub=G();tub.rectangle_ring(.86,1.06,.035,-.40,.018,.03,TEAL)
    box(tub,(0,0,-.415),(.86,1.06,.03),TEAL,.008)
    tub.rectangle_ring(.90,1.10,.045,.002,.025,.03,STEEL);hold.merge(tub,(0,-1,0));part('FishHold',hold)
    lid=G();box(lid,(0,-1,.046),(.80,1,.042),WOOD,.008)
    for x in (-.25,0,.25):lid.beam((x,-1.45,.069),(x,-.55,.069),.006,.004,'M_WoodRecess')
    box(lid,(0,-1.32,.08),(.16,.07,.035),STEEL,.008)
    part('HoldLid',lid,(0,-.5,.025))
    K.NOTES.append('Hull 6.5m fore-aft x3.5m beam (motor excluded), pointed bow, flat transom. Deck 5x3m at Z=0, with genuine hold opening. Console tile c=2,r=0, Unity centre(1,0,-2). HoldLid pivot Unity(0,.025,.5), open with negative local-X rotation. Port sockets Unity(-1.68,.45,-1.75/0/+1.75). Propeller pivot Unity(0,-.60,-3.40), spins local Z. No standalone FishHold FBX needed.')

def winch():
    g=G();box(g,(0,0,.055),(.70,.62,.11),NAVY,.02)
    for x in (-.26,.26):
        box(g,(x,0,.25),(.07,.44,.39),NAVY,.015)
    g.tube([(-.22,0,.40),(.22,0,.40)],[.135,.135],16,ROPE)
    for x in (-.23,.20):g.tube([(x,0,.40),(x+.03,0,.40)],[.18,.18],16,STEEL)
    for i in range(8):
        x=-.18+i*.05
        a=G();ring(a,.14,.01,x,x+.02,ROPE,sides=16)
        a.vertices=[(z,y,.40+xx) for xx,y,z in a.vertices];g.merge(a)
    part('WinchFrameAndDrum',g)
    crank=G();crank.beam((.29,0,.40),(.29,.21,.40),.04,.04,ORANGE,.008)
    crank.tube([(.29,.21,.40),(.45,.21,.40)],[.032,.032],10,'M_Rubber')
    part('Crank',crank,(.29,0,.40))
    K.NOTES.append('1x1m reserved footprint; Crank Unity pivot(.29,.40,0), spin local X. Drum is static in this first kit.')

def gillnet(name):
    g=G()
    if name=='GillNetCoil':
        for i in range(6):net(g,.72-i*.025,.38,.025+i*.025,offset=(.025*(i%2),0,0))
        for x in (-.22,0,.22):g.ellipsoid((x,-.21,.11),(.045,.045,.075),10,4,ORANGE)
        for x in (-.22,.22):g.tube([(x,-.27,.04),(x,-.27,.19),(x,.25,.19),(x,.25,.04)],[.015]*4,6,ROPE)
        grounded(g)
    elif name=='GillNetFloatLine':
        g.tube([(-1,0,0),(1,0,0)],[.012,.012],8,ROPE)
        for x in (-.75,-.25,.25,.75):
            g.ellipsoid((x,0,0),(.09,.055,.055),12,4,ORANGE)
            g.tube([(x-.016,0,0),(x+.016,0,0)],[.057,.057],12,IVORY)
        K.NOTES.append('2m repeat along X, float line at waterline Z=0; four floats centred between module ends.')
    else:
        net(g,2,1.5,-.18)
        for y in (-.75,.75):g.tube([(-1,y,-.18),(1,y,-.18)],[.015,.015],8,ROPE)
        # Exact 2m longitudinal span despite the mesh's thick border strands.
        lo=min(v[0] for v in g.vertices);hi=max(v[0] for v in g.vertices)
        g.vertices=[((x-(lo+hi)/2)*2/(hi-lo),y,z) for x,y,z in g.vertices]
        K.NOTES.append('2m repeat along X, 1.5m laid span; submerged at source Z=-.18, root is waterline. Coarse strands are geometry, no cloth simulation.')
    part(name,g)

def sort_table():
    g=G()
    for x in (-.80,.22):
        for y in (-.28,.28):box(g,(x,y,.25),(.09,.09,.50),NAVY,.008)
    box(g,(-.3,0,.525),(1.22,.76,.05),STEEL,.02)
    tray=G();box(tray,(0,0,.568),(1.03,.57,.025),TEAL,.008)
    tray.rectangle_ring(1.03,.57,.03,.572,.64,.04,TEAL);g.merge(tray,(-.3,0,0))
    chute=G();chute.extrude_polygon([(.17,-.16),(.48,-.16),(.48,.16),(.17,.16)],.49,.52,STEEL)
    chute.vertices=[(x,y,z-.10*(x-.17)/.31) for x,y,z in chute.vertices];g.merge(chute)
    for y in (-.16,.16):g.beam((.17,y,.56),(.48,y,.46),.025,.025,IVORY)
    bin_geom=G();box(bin_geom,(0,0,.025),(.50,.63,.05),NAVY,.01)
    bin_geom.rectangle_ring(.50,.63,.025,.04,.39,.035,NAVY)
    bin_geom.rectangle_ring(.54,.67,.03,.38,.42,.035,IVORY);g.merge(bin_geom,(.65,0,0))
    part('SortTableFrameTrayChute',g)
    K.NOTES.append('2x1m reserved footprint, .55m worktop. Teal tray and descending steel chute feed an open navy bin within the same footprint; front/operator edge Unity -Z.')

C_ASSETS={
    'Skiff':('Boats',skiff),'HandWinch':('Stations',winch),
    **{n:('Fishing',lambda n=n:gillnet(n)) for n in ('GillNetCoil','GillNetFloatLine','GillNetSection')},
    'SortTable':('Stations',sort_table),
}


def register():
    K.FISH['Cod']=(.70,.145,.135,'M_KelpGreen')
    K.ASSETS.update(B_ASSETS);K.ASSETS.update(C_ASSETS)

if __name__=='__main__':
    register()
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['B']
    names=list(B_ASSETS) if args==['B'] else list(C_ASSETS) if args==['C'] else args
    p=K.OUT/'build-metrics.json';data=json.loads(p.read_text());indexed={a['asset']:a for a in data['assets']}
    for name in names:
        indexed[name]=K.build(name)
        data['assets']=list(indexed.values());data['palette_srgb']=K.B.PALETTE
        p.write_text(json.dumps(data,indent=2)+'\n')

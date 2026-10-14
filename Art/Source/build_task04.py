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
C_ASSETS={}

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

"""MAP8 deterministic angular granite lighthouse rock; Blender --python this -- build|review.

Wildlife, foam race, glow and cardinal buoy are named EMPTY anchors only.
Waterline obstructions are sliced from the real closed granite meshes.
"""
import sys, math, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from sea_v2_layouts import LAYOUTS, grounds
ROOT = Path(__file__).resolve().parents[3]
NAME = 'GullLighthouseRock'
L = LAYOUTS[NAME]
R = (math.cos(math.radians(35)), -math.sin(math.radians(35)))
F = (math.sin(math.radians(35)), math.cos(math.radians(35)))
def offset(x,z,r,f):return x+R[0]*r+F[0]*f,z+R[1]*r+F[1]*f
L['lifeAnchors'] = [
    dict(id='PuffinLedge_1',position=[-16,2.08,-5]),
    dict(id='PuffinLedge_2',position=[-6,3.38,-4.7]),
    dict(id='PuffinLedge_3',position=[8,4.68,-3.8]),
    dict(id='TideRace_1',position=[*offset(40,65,6,-3)[:1],-.285,offset(40,65,6,-3)[1]]),
    dict(id='TideRace_2',position=[*offset(40,65,-6,-4)[:1],-.285,offset(40,65,-6,-4)[1]]),
    dict(id='LighthouseLamp_1',position=[0,22.08,15]),
    dict(id='CardinalBuoy_1',position=[*offset(100,-42,3,-6)[:1],-.32,offset(100,-42,3,-6)[1]])]

def dress(B):
    import bpy,bmesh
    B.K.PALETTE.update({'M_GraniteShadow':'4F626C','M_GraniteWet':'647981',
        'M_GraniteGrey':'8D9C9C','M_GraniteLight':'B6BFB4','M_GraniteLichen':'83917D',
        'M_LighthouseRed':'C84B39','M_LighthouseIvory':'F3F0DC','M_LanternGlass':'447F91'})
    oldisland=B.island
    def prism(name,points,rings,mats,faceted=False):
        n=len(points);cx=sum(p[0] for p in points)/n;cz=sum(p[1] for p in points)/n
        vs=[B.xyz(cx+(x-cx)*scale,cz+(z-cz)*scale,h) for h,scale in rings for x,z in points]
        fs=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(len(rings)-1) for i in range(n)]
        fs += [tuple(reversed(range(n)))]
        cap_start=len(fs)
        if faceted:
            base=(len(rings)-1)*n; h,scale=rings[-1]
            for i,(x,z) in enumerate(points):
                vs[base+i]=B.xyz(cx+(x-cx)*scale,cz+(z-cz)*scale,h+[0,.12,-.08,.03,.15,0,-.04][i%n])
            centre=len(vs);vs.append(B.xyz(cx-.25,cz+.12,h+.42))
            fs += [(base+i,base+(i+1)%n,centre) for i in range(n)]
        else:fs += [tuple(range((len(rings)-1)*n,len(rings)*n))]
        o=B.mesh(name,vs,fs,mats);bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:
            p.material_index=([1,2,4,2,3,2,4][(p.index-cap_start)%n] if faceted and p.index>=cap_start else min(p.index//n,len(mats)-1))
        return o
    outline=[(-1,-.54),(-.67,-1),(-.10,-.89),(.37,-1.02),(.91,-.58),(1,.08),(.65,.78),(.12,1),(-.54,.87),(-.94,.31)]
    def granite(spec):
        if spec not in L['islands']:return oldisland(spec)
        x,z=spec['centre'];rx,rz=spec['radii']
        pts=[(x+rx*a,z+rz*b) for a,b in outline]
        o=prism('Terrain_'+spec['id'],pts,[(-8,1.28),(-1.5,1.16),(.18,1),(2.4,.91),(5.2,.72),(8.4,.56)],
                ['M_GraniteShadow','M_GraniteWet','M_GraniteGrey','M_GraniteLight','M_GraniteLichen'])
        o['navigation_terrain']=True;o['purpose']=spec['purpose'];return o
    def block(name,x,z,h,size,mat,yaw=0):
        o=B.K.box(name,B.xyz(x,z,h),size,mat,.025);o.rotation_euler.z=yaw;return o
    def cyl(name,x,z,h,radius,length,mat):return B.K.cyl(name,B.xyz(x,z,h),radius,length,mat,12)
    def local(name):
        assert name==NAME
        # Tapered, genuinely faceted 14m tower; the top lamp/glow is external.
        cyl('LighthouseFoundation',0,15,8.6,2.65,.4,'M_GraniteLight')
        for j,(h,r,l,mat) in enumerate([(10.6,1.85,3.6,'M_LighthouseIvory'),
                (13.1,1.69,1.4,'M_LighthouseRed'),(15.7,1.54,3.8,'M_LighthouseIvory'),
                (18.2,1.38,1.2,'M_LighthouseRed'),(19.6,1.28,1.6,'M_LighthouseIvory')]):
            cyl('LighthouseTowerCourse',0,15,h,r,l,mat)
        cyl('LighthouseGalleryFloor',0,15,20.48,2.0,.22,'M_HullNavy')
        cyl('LighthouseLanternGlass',0,15,21.6,1.12,1.9,'M_LanternGlass')
        for i in range(8):
            a=i*math.pi/4;x=math.cos(a)*1.14;z=15+math.sin(a)*1.14
            cyl('LanternMullion',x,z,21.6,.065,2.0,'M_HullNavy')
        for i in range(12):
            a=i*math.pi/6;x=math.cos(a)*1.85;z=15+math.sin(a)*1.85
            cyl('GalleryRailPost',x,z,20.98,.045,.8,'M_LighthouseIvory')
        B.K.torus('GalleryUpperRail',B.xyz(0,15,21.35),1.85,.055,'M_LighthouseIvory')
        bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=1.8,radius2=.28,depth=1.1,location=B.xyz(0,15,23.05))
        bpy.context.object.name='LighthouseRedRoof';bpy.context.object.data.materials.append(B.K.material('M_LighthouseRed'))
        cyl('LighthouseFinial',0,15,23.8,.055,.6,'M_HullNavy')
        block('LighthouseDoor',0,13.13,9.8,(.85,.08,1.9),'M_HullNavy')
        for h in (12,16.5,19.2):block('TowerWindow',0,13.30,h,(.45,.08,.7),'M_HullNavy')
        # Keeper cottage on the same summit, broad terracotta gable and chimney.
        B.house(-6.3,15,8.4)
        block('KeeperChimney',-7.8,15.5,13.2,(.65,.70,2.4),'M_GraniteGrey')
        block('KeeperChimneyCap',-7.8,15.5,14.4,(.86,.90,.16),'M_HullNavy')
        # Outward south-facing steps. The 2.64m perch and offset animated bird
        # sit clear of the tapering stack; the long rear facets join its slope.
        for i,a in enumerate(L['lifeAnchors'][:3]):
            x,y,z=a['position'];pts=[(x+dx,z+dz) for dx,dz in [(-2.6,-1.9),(-1.3,-2.3),(2.6,-1.8),(3,1.5),(1.6,3.4),(-2.5,2.7)]]
            prism('StackPuffinShelf',pts,[(y-.9,1.1),(y+.32,1)],['M_GraniteWet','M_GraniteLight'])
        # Broken low ledges, each with two exposed grey tones in the lower corners.
        # All cross waterline surfaces are genuine obstacles, never foam fins.
        for j,g in enumerate(grounds(NAME)):
            x,z=g['centre']['x'],g['centre']['z']
            for side in (-1,1):
                cx,cz=offset(x,z,side*5.8,-3.4)
                pts=[offset(cx,cz,a,b) for a,b in [(-2.1,-1.25),(-1.35,-1.7),(.35,-1.4),(1.9,-.65),(2.1,.5),(.6,1.3),(-1.8,.85)]]
                top=[.72,.30,.42][j]
                o=prism('Terrain_CornerGranite',pts,[(-4,1.12),(-1.4,1.07),(-.08,1),(.12,1),(top,.77)],
                    ['M_GraniteShadow','M_GraniteWet','M_GraniteGrey','M_GraniteLight','M_GraniteLichen'],faceted=True)
                o['navigation_terrain']=True;o['ground']=g['id'];o['purpose']='Low angular granite in lower deck-frame corner; actual waterline sliced.'
                px,pz=offset(cx,cz,.4,-.05)
                small=[offset(px,pz,a,b) for a,b in [(-.8,-.45),(.5,-.65),(1,.1),(.3,.7),(-.8,.4)]]
                prism('GraniteCrownFacet',small,[(top-.06,1),(top+.24,.68)],['M_GraniteGrey','M_GraniteLichen'])
    def open_ocean(name):
        # A lone stack needs open water, without the generic four pale horizon
        # islands or a second lighthouse competing with the actual landmark.
        items=[]
        for i,(x,z,s) in enumerate([(218,190,1),(-211,170,.65)]):
            block('HorizonFreighterHull',x,z,1.1,(20*s,3.7*s,2.2*s),'M_Horizon')
            block('HorizonFreighterBridge',x+5*s,z,3*s,(4*s,3.3*s,2.4*s),'M_HorizonFar')
            block('HorizonFreighterFunnel',x+2*s,z,4.5*s,(1.2*s,1.2*s,1.5*s),'M_Horizon')
            items.append(dict(id='outer-freighter-'+str(i),kind='ship',centre=dict(x=x,z=z),reachable=False))
        return items
    B.island=granite;B.local_dressing=local;B.horizon=open_ocean

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    mode=args[-1];folder=ROOT/'Art/Models/Maps'/NAME
    if mode in ('build','review'):
        import build_sea_v2 as B
        dress(B)
        if mode=='build':
            folder.mkdir(parents=True,exist_ok=True)
            (folder/'grounds.json').write_text(json.dumps(dict(map=NAME,grounds=[dict(id=g['id'],name=g['name'],seabedDepth=g['nominalDepth'],poolId=g['poolId']) for g in grounds(NAME)]),indent=2))
        (B.build if mode=='build' else B.review)(NAME)
    elif mode=='detail':
        import bpy
        from mathutils import Vector
        bpy.ops.wm.open_mainfile(filepath=str(folder/'SeaV2-Review-only.blend'))
        sc=bpy.context.scene;cam=sc.camera;target=Vector((0,12,8))
        cam.location=(44,-58,49);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale=64;sc.render.resolution_x=1440;sc.render.resolution_y=1080
        sc.render.filepath=str(folder/'SeaV2-stack-detail.png');bpy.ops.render.render(write_still=True)
        print('MAP8 STACK DETAIL RENDERED',flush=True)
    elif mode=='audit':
        from audit_sea_v2 import audit,plate,sheet
        nav,rec=audit(NAME);plate(NAME,nav,rec);sheet(NAME,nav)
        print(json.dumps({'passed':sum(c['passed'] for c in rec['checks']),'checks':len(rec['checks']),'failures':[c for c in rec['checks'] if not c['passed']]}))
        sys.exit(0 if rec['allPassed'] else 1)
    else:raise ValueError(mode)


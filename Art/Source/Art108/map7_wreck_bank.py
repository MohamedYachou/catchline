"""MAP7: deterministic metre-scale wreck bank. Blender --python this.py -- build|review.

The wreck, bank and low corner ledges are closed, independently sliced terrain.
Wildlife and the cardinal buoy are declared empty anchors for the runtime owner.
"""
import sys, math, json, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from sea_v2_layouts import LAYOUTS, grounds
ROOT = Path(__file__).resolve().parents[3]
NAME = 'GullWreckBank'
L = LAYOUTS[NAME]
R = (math.cos(math.radians(35)), -math.sin(math.radians(35)))
F = (math.sin(math.radians(35)), math.cos(math.radians(35)))

def offset(x,z,r,f): return x+R[0]*r+F[0]*f, z+R[1]*r+F[1]*f
BOW = offset(-72,-24,5.0,-3.4)

def ship(s,w=0): return offset(*BOW,w,-s)
L['lifeAnchors'] = [dict(id=f'GannetDive_{i+1}',position=[*offset(2,61,r,f)[:1], .8, offset(2,61,r,f)[1]])
    for i,(r,f) in enumerate([(-5,-5),(5,-5),(-9,5),(9,5)])]
gx,gz = ship(11,-2)
cx,cz = ship(5,5)
L['lifeAnchors'] += [dict(id='WreckGulls_1',position=[gx,1.48,gz]),
                     dict(id='CardinalBuoy_1',position=[cx,-.32,cz])]

def dress(B):
    import bpy, bmesh
    from mathutils import Vector
    B.K.PALETTE.update({'M_WreckRust':'A0593D','M_WreckOxide':'733D32',
        'M_WreckLit':'BA7850','M_WreckDark':'343F3D','M_WreckDeck':'665E50',
        'M_BankSand':'D2C297','M_BankLight':'E2D0A4','M_BankWet':'A59F7C',
        'M_BankDeep':'7E9A87','M_WreckWeed':'4F6950'})
    oldisland = B.island
    def normals(o):
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        return o
    def prism(name,points,rings,mats):
        n=len(points);v=[]
        centre=(sum(x for x,z in points)/n,sum(z for x,z in points)/n)
        for h,scale in rings:
            v += [B.xyz(centre[0]+(x-centre[0])*scale,centre[1]+(z-centre[1])*scale,h) for x,z in points]
        faces=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(len(rings)-1) for i in range(n)]
        faces += [tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
        o=normals(B.mesh(name,v,faces,mats))
        for p in o.data.polygons:p.material_index=min(p.index//n,len(mats)-1)
        return o
    def bank(spec):
        if spec not in L['islands']:return oldisland(spec)
        x,z=spec['centre'];rx,rz=spec['radii']
        pts=[(x+rx*a,z+rz*b) for a,b in [(-1,-.6),(-.68,-1),(.3,-.92),(.95,-.55),(1,.44),(.55,1),(-.65,.84)]]
        o=prism('Terrain_'+spec['id'],pts,[(-6,1.28),(-1.5,1.16),(-.08,1),(.14,1),(.14,.86),(.32,.86)],
                ['M_BankDeep','M_BankWet','M_BankSand','M_BankLight'])
        o['navigation_terrain']=True;o['purpose']=spec['purpose'];return o
    def block(name,p,size,mat,yaw=0,bevel=.035):
        o=B.K.box(name,B.xyz(*p),size,mat,bevel);o.rotation_euler.z=yaw;return o
    def deckplate(name,s,w,h,size,mat):
        x,z=ship(s,w);return block(name,(x,z,h),size,mat,math.radians(35))
    def local(name):
        assert name==NAME
        # 30m steamer: long axis away from the nearby bow, with an angular pointed
        # bow, broad broken plating and a low half-flooded dark deck. One closed
        # outer footprint is the real navigation obstacle, not an invisible proxy.
        outline=[ship(s,w) for s,w in [(0,0),(3,-2.5),(9,-2.9),(24,-2.9),(30,-1.9),
                                      (30,1.9),(24,2.9),(9,2.9),(3,2.5)]]
        hull=prism('Terrain_SteamerHull',outline,[(-5,1.08),(-1.4,1.04),(.04,1),(.38,1)],
                   ['M_WreckDark','M_WreckOxide','M_WreckRust'])
        hull['navigation_terrain']=True;hull['purpose']='30m half-sunk steamer: real waterline obstruction beside The wreck.'
        # Separate planar side plates stay inside that sliced hull footprint.
        for side in (-1,1):
            for i,s in enumerate((6,10,14,18,22,26)):
                deckplate('SteamerRustedPlate',s,side*(2.35 if s<25 else 2.0),.66+(i%3)*.19,
                          (.18,3.5,.8+(i%3)*.38),['M_WreckRust','M_WreckLit','M_WreckOxide'][i%3])
                if i in (1,4):
                    deckplate('SteamerPlateSeam',s-.9,side*2.45,.7,(.04,.13,.9),'M_WreckDark')
        deckplate('SteamerFloodedHold',14,0,.40,(3.5,11,.035),'M_WreckDark')
        for s in (8.3,13,17.8,22.6):
            deckplate('SteamerBrokenCrossRib',s,0,.46,(4.9,.20,.20),'M_WreckLit')
        deckplate('SteamerBowDeck',3,0,.45,(2.2,1.7,.14),'M_WreckDeck')
        deckplate('SteamerBowBrokenBulwark',1.6,-.9,1.0,(.16,1.3,1.35),'M_WreckRust')
        # A collapsed ivory wheelhouse and two broad windows distinguish a ship
        # from a row of rocks. The funnel leans; no baked birds or buoy geometry.
        cabin=deckplate('SteamerWheelhouse',23,0,1.25,(3.6,3.0,1.7),'M_BankWet');cabin.rotation_euler.x=.11
        deckplate('SteamerWheelhouseRoof',23,0,2.13,(3.9,3.3,.18),'M_WreckRust')
        for w in (-.9,.9):deckplate('SteamerBridgeWindow',21.48,w,1.60,(.65,.07,.43),'M_WreckDark')
        x,z=ship(18.5,.15)
        funnel=B.K.cyl('SteamerLeaningFunnel',B.xyz(x,z,2.8),.82,4.7,'M_WreckRust',10)
        funnel.rotation_euler=(math.radians(13),math.radians(-10),0)
        top=Vector(B.xyz(x,z,2.8))+funnel.rotation_euler.to_matrix()@Vector((0,0,2.25))
        cap=B.K.cyl('SteamerFunnelBlackLip',top,.84,.38,'M_WreckDark',10);cap.rotation_euler=funnel.rotation_euler
        x,z=ship(10,.1);tip=Vector(B.xyz(x+1.1,z-.45,7.4));base=Vector(B.xyz(x,z,.4))
        B.K.beam('SteamerLeaningMast',base,tip,.105,'M_WreckOxide')
        arm=(tip-base).normalized();cross=Vector((R[0],-R[1],0))*2.0
        B.K.beam('SteamerMastCrossbar',tip-arm*1.0-cross,tip-arm*1.0+cross,.075,'M_WreckLit')
        # Low, stepped sand ledges frame each deck view. Their real slices are
        # exported as obstacles; none is a hidden collider or smooth dome.
        for j,g in enumerate(grounds(NAME)):
            x,z=g['centre']['x'],g['centre']['z']
            for side in (-1,1):
                if j==0 and side==1:continue
                cx,cz=offset(x,z,side*5.8,-4.3)
                pts=[offset(cx,cz,a,b) for a,b in [(-2.7,-1.4),(-2,-2.1),(1.9,-1.9),(2.9,-.6),(2.4,1.1),(-1.7,1.5)]]
                o=prism('Terrain_CornerSandLedge',pts,[(-3,1.10),(-1.4,1.04),(-.08,1),(.14,1),(.14,.86),(.30,.86)],['M_BankDeep','M_BankWet','M_BankSand','M_BankLight'])
                o['navigation_terrain']=True;o['ground']=g['id'];o['purpose']='Low angular sand ledge in deck-camera corner; real navigation obstacle.'
                for i in range(3):
                    px,pz=offset(cx,cz,-1.4+i*1.35,-.30+i*.18)
                    block('SandLedgeRipple',(px,pz,.325),(.13,1.4,.035),'M_BankLight',math.radians(35),.006)
            if j==1:
                for i in range(14):
                    px,pz=offset(x,z,-5+i*.85,6+(i%3)*.4)
                    block('BankSandRipple',(px,pz,-1.6),(.13,2.2,.05),'M_BankSand',math.radians(35),.01)
        # Sparse weed clings to the hull at its far side, clear of the anchor.
        for s in (8,12,16,20,24):
            px,pz=ship(s,-2.7);B.kelp(px,pz,2.3,3)
    B.island=bank;B.local_dressing=local

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
    elif mode=='audit':
        from audit_sea_v2 import audit,plate,sheet
        nav,rec=audit(NAME);plate(NAME,nav,rec);sheet(NAME,nav)
        print(json.dumps({'passed':sum(c['passed'] for c in rec['checks']),'checks':len(rec['checks']),
                          'failures':[c for c in rec['checks'] if not c['passed']]}))
        sys.exit(0 if rec['allPassed'] else 1)
    else:raise ValueError(mode)

"""Additive MAP10 authoring; Blender --background --python this-file -- build|review|anchors.

Injects only this new layout into the shared pipeline; accepted map layouts stay byte-identical.
"""
import sys, math, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from sea_v2_layouts import LAYOUTS, GROUND_NAMES, grounds, island
ROOT = Path(__file__).resolve().parents[3]
NAME = 'GullSealCliffs'
GROUND_NAMES[NAME] = [('arch-pool','Arch pool',3.2),('seal-cove','Seal cove',2.4),('stack-race','Stack race',7.0)]
L = LAYOUTS[NAME] = dict(title='Seal cliffs', size=(340,260), harbour=(-135,-95),
    centres=[(-72,26,12),(5,42,14),(105,20,15)],
    islands=[island('north-cliff-line',(-5,101),(144,20),22,'Tall angular far-north coast with bird-streaked broken faces.',kind='rock'),
             island('race-stack',(32,25),(11,18),12,'Detached angular sea stack divides Arch pool from Stack race.',kind='rock')],
    sealColonyAnchors=[], lifeAnchors=[
        dict(id='SealHaulout_1',position=[-5,.58,68]),
        dict(id='SealHaulout_2',position=[2,.78,68]),
        dict(id='SealHaulout_3',position=[9,.68,68]),
        dict(id='CliffGulls_1',position=[-37,5.68,76]),
        dict(id='CliffGulls_2',position=[67,6.88,77]),
        dict(id='ArchSpray_1',position=[-74,-.32,52])],
    horizon='Unreachable continuation of the tall north coast; no buildings or baked animals.',
    waterShallow='2E8C8A', waterDeep='174D69')

def dress(B):
    import bpy, bmesh
    B.K.PALETTE.update({'M_CliffShadow':'40555E','M_CliffStone':'78868A',
        'M_CliffLight':'A3ADA9','M_CliffBird':'DDDCD0','M_CovePebble':'ACAA97',
        'M_CoveWet':'677A78'})
    outline=[(-1,-.55),(-.65,-1),(.1,-.91),(.77,-.62),(1,.12),(.64,.85),(-.14,1),(-.88,.52)]
    def prism(name, pts, rings, mats, broken=False):
        n=len(pts);cx=sum(x for x,z in pts)/n;cz=sum(z for x,z in pts)/n
        vs=[B.xyz(cx+(x-cx)*s,cz+(z-cz)*s,h) for h,s in rings for x,z in pts]
        fs=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(len(rings)-1) for i in range(n)]
        fs.append(tuple(reversed(range(n))))
        base=(len(rings)-1)*n
        if broken:
            factor=float(broken)
            for i in range(n):vs[base+i]=(vs[base+i][0],vs[base+i][1],vs[base+i][2]+factor*[0,1.3,-.7,.6,-1.1,.4,1.0,-.3][i%8])
            centre=len(vs);vs.append(B.xyz(cx,cz,rings[-1][0]+factor*.6))
            fs.extend((base+i,base+(i+1)%n,centre) for i in range(n))
        else:fs.append(tuple(range(base,base+n)))
        o=B.mesh(name,vs,fs,mats)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.material_index=min(len(mats)-1,p.index//n) if p.index<len(fs)-n else len(mats)-1
        return o
    def rock(name,x,z,rx,rz,h,terrain=True,broken=False):
        o=prism(name,[(x+a*rx,z+b*rz) for a,b in outline],
            [(-6,1.16),(-1.4,1.1),(.15,1),(h*.53,.92),(h,.72)],
            ['M_CoveWet','M_CliffShadow','M_CliffStone','M_CliffLight'],broken)
        o['navigation_terrain']=terrain;return o
    def coast(spec):
        if spec['id']=='race-stack':return rock('Terrain_race-stack',32,25,11,18,12,broken=True)
        pts=[(-152,91),(-120,82),(-97,87),(-75,80),(-52,87),(-28,79),(-5,84),(15,82),
             (34,91),(61,81),(84,88),(112,82),(139,94),(142,119),(-150,120)]
        o=prism('Terrain_north-cliff-line',pts,[(-8,1.025),(-1.5,1.015),(.18,1),(10,.99),(21,.94)],
            ['M_CoveWet','M_CliffShadow','M_CliffStone','M_CliffLight'],True)
        # Offset the concave shoreline along its outward normals. Scaling a
        # concave outline about its centre can leave land beyond the shelf.
        for ring,(height,distance) in enumerate([(-8,3.0),(-1.5,2.0)]):
            for i,(x,z) in enumerate(pts):
                prev=pts[(i-1)%len(pts)];nxt=pts[(i+1)%len(pts)]
                a=(x-prev[0],z-prev[1]);b=(nxt[0]-x,nxt[1]-z)
                al=math.hypot(*a);bl=math.hypot(*b)
                na=(a[1]/al,-a[0]/al);nb=(b[1]/bl,-b[0]/bl)
                scale=distance/(1+na[0]*nb[0]+na[1]*nb[1])
                o.data.vertices[ring*len(pts)+i].co=B.xyz(x+(na[0]+nb[0])*scale,z+(na[1]+nb[1])*scale,height)
        o.data.update()
        o['navigation_terrain']=True;o['purpose']=spec['purpose'];return o
    def local(name):
        # Two closed piers and one closed curved lintel form a genuine open arch.
        for x in (-86,-62):rock('Terrain_ArchPier_'+str(x),x,58,4.8,5.4,10)
        profile=[(-91,10),(-89,13),(-80,14),(-73,13.4),(-65,14.1),(-57,11),
                 (-60,7.2),(-65,6.3),(-69,8.7),(-74,9.5),(-79,8.8),(-83,6.4),(-88,7.2)]
        vs=[B.xyz(x,z,h) for z in (54.5,61.5) for x,h in profile];n=len(profile)
        fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        arch=B.mesh('SeaArch_BrokenLintel',vs,fs,['M_CliffStone','M_CliffLight','M_CliffShadow'])
        bm=bmesh.new();bm.from_mesh(arch.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(arch.data);bm.free()
        for p in arch.data.polygons:p.material_index=p.index%3
        # A scalloped pebble apron and flat surfaced haul-out stones, not baked seals.
        for i,(x,z,rx,rz,h) in enumerate([(-10,72,10,7,.55),(5,73,13,7,.45),(19,73,8,6,.65)]):
            rock('Terrain_CoveApron_'+str(i),x,z,rx,rz,h)
        for i,(x,h) in enumerate([(-5,.9),(2,1.1),(9,1.0)]):
            pts=[(x+a*2.6,68+b*2.0) for a,b in outline]
            o=prism('Terrain_HauloutStone_'+str(i+1),pts,[(-2,1.2),(-1.2,1.1),(.2,1),(h,.88)],
                ['M_CoveWet','M_CliffStone','M_CovePebble']);o['navigation_terrain']=True
        for i,(x,z,h) in enumerate([(-37,79,6),(67,80,7.2)]):
            pts=[(x+a*3,z+b*5) for a,b in outline]
            prism('CliffLedge_'+str(i+1),pts,[(h-1.4,1),(h,.9)],['M_CliffShadow','M_CliffLight'])
        # Uneven ivory guano streaks on the exposed front faces, well above water.
        for i,(x,z,h) in enumerate([(-115,83,12),(-93,87,14),(-51,87,11),(-25,80,13),(13,83,14),(61,82,12),(109,84,14)]):
            pts=[(x-.5,z-.18),(x+.5,z-.18),(x+.3,z+.03),(x-.3,z+.03)]
            prism('BirdStreak_'+str(i),pts,[(h-3.5, .55),(h,1)],['M_CliffBird'])
        # Low real waterline ledges follow MAP8's accepted corner-rock contract.
        r=(math.cos(math.radians(35)),-math.sin(math.radians(35)));f=(math.sin(math.radians(35)),math.cos(math.radians(35)))
        for g in grounds(NAME):
            for side in (-1,1):
                x=g['centre']['x']+r[0]*side*5.7-f[0]*3.7
                z=g['centre']['z']+r[1]*side*5.7-f[1]*3.7
                pts=[(x+r[0]*a+f[0]*b,z+r[1]*a+f[1]*b) for a,b in [(-1.8,-1),(-1.1,-1.5),(.5,-1.3),(1.8,-.4),(1.4,.8),(-.3,1),(-1.6,.6)]]
                o=prism('Terrain_CornerRock_'+g['id']+'_'+str(side),pts,[(-5,1.2),(-1.5,1.1),(.12,1),(.52,.84)],
                    ['M_CliffShadow','M_CoveWet','M_CliffStone','M_CliffLight'],.18)
                o['navigation_terrain']=True;o['purpose']='Low angular lower-corner rock; genuine waterline obstruction with anchor clearance exceeding4m.'
    def horizon(name):
        items=[]
        for i,(x,z,rx,rz,h) in enumerate([(-140,205,85,22,26),(45,214,110,25,30)]):
            o=rock('HorizonNorthCliff_'+str(i),x,z,rx,rz,h,False,True)
            o.data.materials.clear();o.data.materials.append(B.K.material('M_HorizonFar'))
            for p in o.data.polygons:p.material_index=0
            items.append(dict(id=o.name,kind='cliffs',centre=dict(x=x,z=z),reachable=False))
        return items
    B.island=coast;B.local_dressing=local;B.horizon=horizon

def anchors():
    import bpy
    from mathutils import Vector
    import build_sea_v2 as B
    folder=ROOT/'Art/Models/Maps'/NAME
    bpy.ops.wm.open_mainfile(filepath=str(folder/(NAME+'SeaV2.blend')))
    root=bpy.data.objects['Catchline_'+NAME+'SeaV2'];root.scale=(1,-1,1);root.location.z=-.32
    bpy.context.view_layer.update();sc=bpy.context.scene
    results=[]
    for a in L['lifeAnchors']:
        x,y,z=a['position'];hits=[]
        for ob in sc.objects:
            if ob.type!='MESH':continue
            inv=ob.matrix_world.inverted();origin=inv@Vector((x,z,100));direction=inv.to_3x3()@Vector((0,0,-1))
            hit,p,normal,face=ob.ray_cast(origin,direction)
            if hit:hits.append((float((ob.matrix_world@p).z),ob.name))
        top=max(hits,default=(-100,''))
        is_water=a['id'].startswith('ArchSpray')
        passed=top[0]<y+.02 if is_water else abs(top[0]-y)<.015
        results.append(dict(anchor=a['id'],position=a['position'],surface=top,passed=passed))
    (folder/'SeaV2-anchor-audit.json').write_text(json.dumps(dict(allPassed=all(r['passed'] for r in results),anchors=results),indent=2))
    assert all(r['passed'] for r in results),results
    B.setup_render(sc)
    d=bpy.data.lights.new('Anchor sun','SUN');o=bpy.data.objects.new('Anchor sun',d);sc.collection.objects.link(o);d.energy=2;o.rotation_euler=(.4,-.3,-.5)
    d=bpy.data.cameras.new('Anchor camera');d.type='ORTHO';cam=bpy.data.objects.new('Anchor camera',d);sc.collection.objects.link(cam);sc.camera=cam
    B.K.box('REVIEW water',(0,0,-.38),(800,800,.12),'M_SeaTeal',0)
    for a in L['lifeAnchors']:
        x,y,z=a['position'];target=Vector((x,z,y));marker=B.K.cyl('REVIEW marker',(x,z,y+.25),.12,.5,'M_SafetyOrange',8)
        cam.location=target+Vector((8,-12,9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=12
        sc.render.filepath=str(folder/('SeaV2-anchor-'+a['id']+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(marker,do_unlink=True)
    print('MAP10 ANCHORS PASS',flush=True)

if __name__=='__main__':
    mode=(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])[-1]
    if mode=='anchors':anchors()
    else:
        import build_sea_v2 as B
        dress(B);folder=ROOT/'Art/Models/Maps'/NAME;folder.mkdir(parents=True,exist_ok=True)
        if mode=='build':
            (folder/'grounds.json').write_text(json.dumps(dict(map=NAME,grounds=[dict(id=g['id'],name=g['name'],seabedDepth=g['nominalDepth'],poolId=g['poolId']) for g in grounds(NAME)]),indent=2))
            B.build(NAME)
        elif mode=='review':B.review(NAME)
        else:raise ValueError(mode)

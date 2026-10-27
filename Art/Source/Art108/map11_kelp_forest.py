"""MAP11 Kelp forest. Additive SeaV2 pipeline; Blender --background --python ... -- build|review."""
import sys, math, json, random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from sea_v2_layouts import LAYOUTS, GROUND_NAMES, grounds, island
ROOT=Path(__file__).resolve().parents[3]
NAME='GullKelpForest'
R=(math.cos(math.radians(35)),-math.sin(math.radians(35)))
F=(math.sin(math.radians(35)),math.cos(math.radians(35)))
def offset(x,z,r,f):return x+R[0]*r+F[0]*f,z+R[1]*r+F[1]*f
GROUND_NAMES[NAME]=[('kelp-edge','Kelp edge',2.5),('sand-clearing','Sand clearing',3.0),('post-line','Post line',2.6)]
L=LAYOUTS[NAME]=dict(title='Kelp forest',size=(320,260),harbour=(-125,-90),
    centres=[(-85,-28,13),(0,35,14),(85,-25,13)],
    islands=[island('mid-bay-weed-rock',(-42.5,3.5),(6,5),1.25,'Low weed-covered outcrop divides two sailing approaches.',kind='rock'),
             island('north-bay-rim',(0,99),(112,13),2.1,'Low weed-covered northern shelter; no buildings.',kind='rock'),
             island('west-bay-rock',(-125,42),(13,22),1.3,'Low western shelter outside the fishing grounds.',kind='rock'),
             island('east-bay-rock',(125,46),(13,23),1.5,'Broken weed-covered eastern shelter.',kind='rock')],
    sealColonyAnchors=[],lifeAnchors=[],waterShallow='3A8F86',waterDeep='205B64',
    horizon='Low distant rocky bay rim only; no buildings, lighthouse or ships.')
for i,(x,z) in enumerate([offset(-85,-28,-5,-3),offset(-85,-28,5,-3),offset(0,35,6,-3),offset(85,-25,-6,-3)]):
    L['lifeAnchors'].append(dict(id='KelpSway_'+str(i+1),position=[x,-.32,z]))
L['lifeAnchors'].append(dict(id='OtterRaft_1',position=[-92,-.32,-22]))
for i,r in enumerate((-4.7,4.7)):
    x,z=offset(85,-25,r,-2.7)
    L['lifeAnchors'].append(dict(id='PostGulls_'+str(i+1),position=[x,1.28,z]))

def dress(B):
    import bpy,bmesh
    from mathutils import Vector
    B.K.PALETTE.update({'M_ForestStone':'8B9683','M_ForestShadow':'536C64','M_ForestWeed':'477A56',
        'M_KelpGold':'739453','M_ForestSand':'CBBB91','M_ForestTeal':'3A8F86'})
    outline=[(-1,-.48),(-.65,-1),(.18,-.9),(.82,-.55),(1,.13),(.55,.88),(-.2,1),(-.87,.52)]
    def rock(spec):
        x,z=spec['centre'];rx,rz=spec['radii'];h=spec['height'];n=len(outline)
        vs=[B.xyz(x+a*(rx+expand)*scale,z+b*(rz+expand)*scale,y)
            for y,expand,scale in [(-6,5,1),(-1.5,2,1),(.12,0,1),(h,0,.72)] for a,b in outline]
        fs=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(3) for i in range(n)]
        fs += [tuple(reversed(range(n))),tuple(range(3*n,4*n))]
        ob=B.mesh('Terrain_'+spec['id'],vs,fs,['M_ForestShadow','M_ForestStone','M_ForestWeed'])
        for p in ob.data.polygons:p.material_index=0 if p.index<n else 1 if p.index<3*n else 2
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
        ob['navigation_terrain']=True;ob['purpose']=spec['purpose'];return ob
    def frond(x,z,depth,angle,height,width):
        # Broad curved closed ribbons, no alpha cards and no micro-detail.
        vs=[];fs=[]
        drift=(0,.05,.12,.2,.4,.8,1.2,1.6,1.95)
        heights=(-depth,-depth*.6,-depth*.25,-.08,-.035,.025,.045,.025,.005)
        widths=(.05,.07,.08,.09,.22,.26,.20,.12,.01)
        for back in (0,.025):
            for k in range(9):
                sway=.12*math.sin(k*.8)
                for side in (-1,1):
                    dx=drift[k]*math.cos(angle)+(side*width*widths[k]+sway)*math.sin(angle)
                    dz=drift[k]*math.sin(angle)-(side*width*widths[k]+sway)*math.cos(angle)+back
                    vs.append(B.xyz(x+dx,z+dz,heights[k]))
        for k in range(8):
            a=k*2;fs.extend([(a,a+2,a+3,a+1),(a+18,a+19,a+21,a+20),
                           (a,a+18,a+20,a+2),(a+1,a+3,a+21,a+19)])
        fs.extend([(0,1,19,18),(16,34,35,17)])
        ob=B.mesh('RootedForestKelp',vs,fs,['M_ForestWeed','M_KelpGold'])
        for p in ob.data.polygons:p.material_index=1 if p.index%7==0 else 0
        return ob
    def local(name):
        rng=random.Random(11026)
        for j,g in enumerate(grounds(NAME)):
            x,z=g['centre']['x'],g['centre']['z'];depth=g['nominalDepth']
            # A deliberate opening round the hull; the forest thickens toward frame corners.
            for side in (-1,1):
                for i in range(23 if j!=1 else 13):
                    r=side*(4.8+rng.random()*2.4);f=-5.2+rng.random()*7.5
                    xx,zz=offset(x,z,r,f)
                    for blade in range(3):frond(xx+blade*.18,zz,1.15,rng.random()*6.28,min(depth-.3,1.9+rng.random()*.5),.55+rng.random()*.25)
                # Low weed-capped corner stone. Its top stays below -1m, clear for boats.
                xx,zz=offset(x,z,side*5.8,-3.8)
                o=rock(island('submerged-'+g['id']+'-'+str(side),(xx,zz),(1.7,1.15),.7,'Submerged forest stone.',kind='rock'))
                for v in o.data.vertices:v.co.z-=2.1
                o.name='SubmergedForestStone_'+g['id']+'_'+str(side);o['navigation_terrain']=False
            if j==1:
                for i in range(12):
                    xx,zz=offset(x,z,(i%4-1.5)*2.0,(i//4-1)*2.1)
                    # Ridges lie on the raised bed rather than floating above it.
                    rr=math.hypot(xx-x,zz-z)
                    bed=1.15+(depth-1.15)*math.exp(-(rr/3.5)**4)
                    B.K.box('SandClearingRipple',B.xyz(xx,zz,-bed+.025),(1.0,.13,.04),'M_CoastSand',.02)
        # A quiet old post line with no jetty, hut or rope crossing the fishing position.
        for i,r in enumerate((-6.8,-4.7,4.7,6.8)):
            x,z=offset(85,-25,r,-2.7)
            post=B.K.cyl('Terrain_MooringPost_'+str(i),B.xyz(x,z,-.55),.22,4.3,'M_DeckWood',8)
            post['navigation_terrain']=True;post['purpose']='Real narrow wooden post; retained in navigation slices.'
            B.K.cyl('MooringPostWet_'+str(i),B.xyz(x,z,-.45),.226,.8,'M_ForestShadow',8)
            B.K.cyl('MooringPostCap_'+str(i),B.xyz(x,z,1.55),.225,.1,'M_WoodHighlight',8)
        # Forest beyond each local view ties the grounds together without baking animals.
        for i in range(180):
            x=rng.uniform(-105,105);z=rng.uniform(-65,75)
            if any(math.hypot(x-g['centre']['x'],z-g['centre']['z'])<18 for g in grounds(NAME)):continue
            for blade in range(2):frond(x+blade*.2,z,4.2,rng.random()*6.28,2.7,.65)
        # Keep four anchor-near clusters separate so life can sway each at its root.
        cells={}
        for o in list(bpy.context.scene.objects):
            if not o.name.startswith('RootedForestKelp'):continue
            c=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
            near=min(L['lifeAnchors'][:4],key=lambda a:math.hypot(c.x-a['position'][0],-c.y-a['position'][2]))
            dist=math.hypot(c.x-near['position'][0],-c.y-near['position'][2])
            key=near['id'] if dist<3.5 else str(int(c.x//32))+'_'+str(int(c.y//32))
            cells.setdefault(key,[]).append(o)
        for key,objects in cells.items():
            bpy.ops.object.select_all(action='DESELECT')
            for o in objects:o.select_set(True)
            bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
            objects[0].name='RootedForestPatch_'+key
    original_seabed=B.seabed
    def seabed(name):
        original_seabed(name)
        ob=bpy.data.objects['ConnectedBathymetry']
        bm=bmesh.new();bm.from_mesh(ob.data)
        edges=[e for e in bm.edges if all(v.co.z>-24 for v in e.verts) and any(
            math.hypot(v.co.x-g['centre']['x'],-v.co.y-g['centre']['z'])<34
            for v in e.verts for g in grounds(NAME))]
        bmesh.ops.subdivide_edges(bm,edges=edges,cuts=3,use_grid_fill=True)
        bm.to_mesh(ob.data);bm.free()
        # Navigable beds stay deeper than the true -1m shallow slice. The anchor
        # pocket retains the authored depth, with a visible shelf around the hull.
        for v in ob.data.vertices:
            if v.co.z < -24:continue
            x,z=v.co.x,-v.co.y
            for g in grounds(NAME):
                r=math.hypot(x-g['centre']['x'],z-g['centre']['z'])
                shelf=math.exp(-(r/23)**8)
                bed=1.15+(g['nominalDepth']-1.15)*math.exp(-(r/3.5)**4)
                v.co.z=v.co.z*(1-shelf)-bed*shelf
        ob.data.materials.clear()
        ob.data.materials.append(B.K.material('M_CoastSand'))
        ob.data.materials.append(B.K.material('M_ForestTeal'))
        ob.data.update()
        # Material-only clearings: a continuous sand sheet erased the water
        # read in native captures. Preserve every verified bed vertex and face.
        for p in ob.data.polygons:
            x,z=p.center.x,-p.center.y
            p.material_index=1
            for g in grounds(NAME):
                dx,dz=x-g['centre']['x'],z-g['centre']['z']
                angle=math.atan2(dz,dx)
                radius=(9.0 if g['id']=='sand-clearing' else 7.8)+.8*math.sin(3*angle+.5)+.5*math.cos(5*angle)
                if math.hypot(dx,dz)<radius:p.material_index=0;break
    def horizon(name):
        out=[]
        for i,x in enumerate((-125,30,155)):
            o=rock(island('far-bay-'+str(i),(x,210),(80,16),6,'Unreachable low coast.',kind='rock'))
            o.name='HorizonBayRim_'+str(i);o['navigation_terrain']=False
            o.data.materials.clear();o.data.materials.append(B.K.material('M_HorizonFar'))
            for p in o.data.polygons:p.material_index=0
            out.append(dict(id=o.name,kind='low-rock',centre=dict(x=x,z=210),reachable=False))
        return out
    B.island=rock;B.seabed=seabed;B.local_dressing=local;B.horizon=horizon

if __name__=='__main__':
    mode=(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])[-1]
    import build_sea_v2 as B
    dress(B);folder=ROOT/'Art/Models/Maps'/NAME;folder.mkdir(parents=True,exist_ok=True)
    if mode=='build':
        (folder/'grounds.json').write_text(json.dumps(dict(map=NAME,grounds=[dict(id=g['id'],name=g['name'],seabedDepth=g['nominalDepth'],poolId=g['poolId']) for g in grounds(NAME)]),indent=2))
        B.build(NAME)
    elif mode=='review':B.review(NAME)
    else:raise ValueError(mode)

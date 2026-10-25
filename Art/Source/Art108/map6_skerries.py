"""MAP6 granite revision. Blender --python this.py -- build|review; uv ... audit.
Close rocks are actual closed, sliced navigation terrain. Ground centres stay.
"""
import sys, json, math, random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from sea_v2_layouts import LAYOUTS, grounds
ROOT=Path(__file__).resolve().parents[3]
NAME='GullSkerries'
LAYOUT=LAYOUTS[NAME]
RIGHT=(math.cos(math.radians(35)),-math.sin(math.radians(35)))
FORWARD=(math.sin(math.radians(35)),math.cos(math.radians(35)))
LAYOUT['sealColonyAnchors']=[dict(id=f'SealColony_{i+1}',position=[
    -84+side*5.8*RIGHT[0]-5*FORWARD[0],h-.32,
    -25+side*5.8*RIGHT[1]-5*FORWARD[1]])
    for i,(side,h) in enumerate([(-1,.85),(1,1.05)])]
REEF=[(98.258,-43.029),(100.47,-43.36),(107,-42),(110,-41),(111.4,-39),(111.8,-36.5)]
def reef_radius(i):return (2.5,3.4) if i==0 else (2.5,2.2) if i==1 else (1.4+(i%2)*.35,1.3)
LAYOUT['lifeAnchors']=[dict(id=f'ReefBreak_{i+1}',position=[x+.574*(reef_radius(i)[1]+.4),-.24,z+.819*(reef_radius(i)[1]+.4)]) for i,(x,z) in enumerate(REEF)]
LAYOUT['lifeAnchors'] += [dict(id='CrabBuoy_1',position=[-80.0,-.32,-33.8])]

def dress(B):
    import bpy, bmesh
    B.K.PALETTE.update({'M_GraniteGrey':'8E959A','M_GranitePink':'AE9A99','M_GraniteLight':'B9BAB4','M_GraniteShadow':'727A80','M_GraniteWet':'727F7B','M_GranitePaleBand':'C0C5BB','M_GraniteWeed':'354B43','M_Barnacle':'B0B5A2','M_Surf':'D9EBE4','M_FoamTeal':'A2D4C9','M_ReefFoamBase':'6DAFA9'})
    oldisland=B.island;oldbed=B.seabed;olddressing=B.local_dressing
    footprint=[(-1,-.64),(-.48,-1),(.32,-.90),(.53,-.57),(.98,-.43),(.89,.10),(1,.51),(.42,.88),(.11,.69),(-.28,1),(-.86,.61),(-.72,.03)]
    def angular(spec):
        if spec not in LAYOUT['islands']:return oldisland(spec)
        cx,cz=spec['centre'];rx,rz=spec['radii'];hh=spec['height']
        close=spec['id'].startswith(('colony-slab-','gully-wall-'))
        if close:
            # Vertical risers and horizontal terraces, with a broad near-flat top.
            # No concentric rounded shoulders or cap boulders on the colony.
            rings=[(-5,1.06,0,0),(-1.25,1.03,0,0),(-.12,1,0,0),(.14,1,0,0),
                   (.14,.96,0,0),(hh*.56,.96,0,0),(hh*.56,.90,0,0),(hh,.90,0,0)]
            fp=[(-1,-.82),(-.72,-1),(.36,-1),(.56,-.83),(.94,-.83),(1,-.52),
                (.97,.68),(.72,.72),(.6,1),(-.48,.96),(-.52,.79),(-1,.64)]
        else:
            rings=[(-5,1.20,0,0),(-1.25,1.08,0,0),(-.12,1.0,0,0),(.17,.98,0,0),(.38,.95,0,0),(.38+(hh-.38)*.55,.84,.02,-.03),(hh,.66,-.03,.04)]
            fp=footprint if rx>4 else [(math.cos(i*math.tau/12),math.sin(i*math.tau/12)) for i in range(12)]
        v=[];n=len(fp);yaw=math.radians(0 if close else -35 if rx<4 else 0)
        for h,s,dx,dz in rings:
            for x,z in fp:
                u,vv=rx*(x*s+dx),rz*(z*s+dz)
                v.append(B.xyz(cx+u*math.cos(yaw)-vv*math.sin(yaw),cz+u*math.sin(yaw)+vv*math.cos(yaw),h))
        f=[]
        for k in range(len(rings)-1):f += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)]
        f += [tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
        o=B.mesh('Terrain_'+spec['id'],v,f,['M_GraniteWeed','M_GraniteWet','M_GranitePaleBand','M_GraniteGrey','M_GranitePink','M_GraniteLight'])
        for p in o.data.polygons:
            k=p.index//n;p.material_index=0 if k==0 else 1 if k==1 else 2 if k==2 else 3+(p.index%3)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        o['navigation_terrain']=True;o['purpose']=spec['purpose'];o['slice_levels']='0,-1 metres local'
        return o
    def foam(o,breaking=False):
        for loop in B.slice_mesh(o,0):
            cx=sum(x for x,z in loop)/len(loop);cz=sum(z for x,z in loop)/len(loop)
            for i,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
                if i%5==3:continue
                def out(p,w):
                    dx,dz=p[0]-cx,p[1]-cz;d=math.hypot(dx,dz);return (p[0]+dx*w/d,p[1]+dz*w/d)
                width=.14 if not breaking else .23
                v=[B.xyz(*a,.035),B.xyz(*b,.035),B.xyz(*out(b,width),.035),B.xyz(*out(a,width),.035)]
                ob=B.mesh('SkerryContactFoam',v,[(0,3,2,1)],['M_Surf'])
                if ob.data.polygons[0].normal.z<0:
                    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    def slab(name,x,z,rx,rz,h):
        s=dict(id=name,centre=(x,z),radii=(rx,rz),height=h,purpose='Close landmark; real closed navigation obstacle.',kind='rock',phase=0)
        LAYOUT['islands'].append(s);return angular(s)
    def block(name,x,z,y,size,angle=0,mat='M_GraniteGrey',bevel=.06):
        o=B.K.box(name,B.xyz(x,z,y),size,mat,bevel);o.rotation_euler.z=angle;return o
    def bed(name):
        oldbed(name)
        if name==NAME:
            ob=bpy.data.objects['ConnectedBathymetry'];ob.data.materials.clear();ob.data.materials.append(B.K.material('M_GraniteWet'))
            for p in ob.data.polygons:p.material_index=0
    def local(name):
        if name!=NAME:return olddressing(name)
        random.seed(62851)
        original=list(LAYOUT['islands'])
        for j,s in enumerate(original):
            cx,cz=s['centre'];rx,rz=s['radii'];hh=s['height']
            for i in range(9):
                a=i*2.39996+j;rr=.22+(i%3)*.17;x=cx+math.cos(a)*rx*rr;z=cz+math.sin(a)*rz*rr
                block('SplitGranitePlate',x,z,hh+.12+(i%3)*.12,(4.8+(i%3)*1.4,2.6+(i%2)*1.3,.38+(i%3)*.21),a*.18,['M_GraniteGrey','M_GranitePink','M_GraniteLight'][i%3],.08)
                block('GraniteFissure',x-.30,z,hh+.34+(i%3)*.12,(.08,1.8,.025),a*.18,'M_GraniteShadow',0)
        for i,a in enumerate(LAYOUT['sealColonyAnchors']):
            x,y,z=a['position'];slab('colony-slab-'+str(i+1),x,z,2.7,1.8,y+.32)
            # Shallow split seams on the flat top, below the life anchor plane.
            block('ColonyTopFissure',x-.9,z+.3,y+.32+.004,(.055,1.0,.008),.18,'M_GraniteShadow',0)
        for side in (-1,1):
            # Two parallel 13m E-W ridges. Their nearest waterline edge is
            # 9.95m from the anchor, over5m clear of the8.5x4.2m hull's radius.
            x,z=8,57+side*11.2
            slab('gully-wall-'+str(side),x,z,6.5,1.25,2.15 if side<0 else 2.65)
            for j in range(4):
                block('GullyTopFissure',x-4.2+j*2.7,z,2.15 if side<0 else 2.65,
                      (.06,1.4,.012),.12*j,'M_GraniteShadow',0)
        for i,(x,z) in enumerate(REEF):
            rx,rz=reef_radius(i);slab('half-tide-reef-'+str(i+1),x,z,rx,rz,.46+(i%3)*.20)
            # ReefBreak_n empties are the sole breaking-patch source. Claude's
            # runtime spawns/pulses ReefBreak_A/B; never bake a duplicate here.
        x,z=68,64
        for i,(sx,sz,hh) in enumerate([(6,5.4,3.0),(4.7,4.3,2.5),(3.6,3.4,2.0)]):
            block('CairnStackGranite',x+(i%2)*.32,z,.5+sum([3,2.5][:i])+hh/2,(sx,sz,hh),.12+i*.13,['M_GraniteGrey','M_GranitePink','M_GraniteLight'][i],.16)
        for i,(sx,sz,hh) in enumerate([(1.25,.9,.28),(.88,.75,.30),(.56,.48,.35)]):block('LandmarkCairn',x,z,8.12+i*.29,(sx,sz,hh),i*.4,'M_GraniteLight',.045)
        terrain=[o for o in bpy.context.scene.objects if o.get('navigation_terrain')]
        for o in terrain:
            foam(o,'half-tide' in o.name);loop=B.slice_mesh(o,.17)[0]
            for i,((x,z),(xx,zz)) in enumerate(zip(loop,loop[1:]+loop[:1])):
                if i%3==0:
                    # A thin drape clings to the sloping rock face, never a post.
                    t=.15;u=.28;cx=x+(xx-x)*t;cz=z+(zz-z)*t;dx=x+(xx-x)*u;dz=z+(zz-z)*u
                    v=[B.xyz(cx,cz,.18),B.xyz(dx,dz,.18),B.xyz(dx*.996+x*.004,dz*.996+z*.004,.55),B.xyz(cx*.996+x*.004,cz*.996+z*.004,.53)]
                    B.mesh('WaterlineWeedDrape',v,[(0,1,2,3)],['M_GraniteWeed'])
        for g in grounds(name):
            x,z=g['centre']['x'],g['centre']['z'];depth=g['nominalDepth']
            for i in range(30 if g['id']=='kelp-gully' else 10):
                t=i*2.39996;r=3.2+(i%4)*.35;B.kelp(x+math.cos(t)*r,z+math.sin(t)*r,depth,5)
    B.island=angular;B.seabed=bed;B.local_dressing=local

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:];mode=args[-1];folder=ROOT/'Art/Models/Maps'/NAME
    if mode in ('build','review'):
        import build_sea_v2 as B
        dress(B)
        if mode=='build':
            folder.mkdir(parents=True,exist_ok=True)
            (folder/'grounds.json').write_text(json.dumps(dict(map=NAME,grounds=[dict(id=g['id'],name=g['name'],seabedDepth=g['nominalDepth'],poolId=g['poolId']) for g in grounds(NAME)]),indent=2))
        (B.build if mode=='build' else B.review)(NAME)
    elif mode=='audit':
        from audit_sea_v2 import audit,plate,sheet
        nav,rec=audit(NAME);plate(NAME,nav,rec);sheet(NAME,nav);sys.exit(0 if rec['allPassed'] else 1)
    else:raise ValueError(mode)

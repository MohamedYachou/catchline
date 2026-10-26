"""MAP9: open continental shelf, a single exposed bird rock, submerged ledges.

Blender --background --python this-file -- build|review|anchors.
Review-only lights/camera/water never enter the runtime FBX.
"""
import sys, math, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from sea_v2_layouts import LAYOUTS, grounds
ROOT=Path(__file__).resolve().parents[3]
NAME='GullWhaleShelf'
L=LAYOUTS[NAME]
R=(math.cos(math.radians(35)),-math.sin(math.radians(35)))
F=(math.sin(math.radians(35)),math.cos(math.radians(35)))
def offset(x,z,r,f):return x+R[0]*r+F[0]*f,z+R[1]*r+F[1]*f
L['lifeAnchors']=[
    dict(id='GannetDive_1',position=[-89,-.32,-41]),
    dict(id='GannetDive_2',position=[-79,-.32,-38]),
    dict(id='WhaleSpout_1',position=[107,-.32,-48]),
    dict(id='WhaleSpout_2',position=[118,-.32,-44]),
    dict(id='CardinalBuoy_1',position=[*offset(10,70,3,-6)[:1],-.32,offset(10,70,3,-6)[1]]),
    dict(id='WreckGulls_1',position=[-23,1.08,15])]

def dress(B):
    import bpy,bmesh
    from mathutils import Vector
    B.K.PALETTE.update({'M_ShelfShadow':'304F62','M_ShelfStone':'65838B',
        'M_ShelfLight':'8FA8A5','M_ShoalSand':'C7B98B','M_ShoalLight':'D8CDA7',
        'M_BirdIvory':'D8DDD0','M_ShelfTeal':'2A7F96','M_ShelfNavy':'102F4F'})
    def prism(name,pts,rings,mats,fan=False):
        n=len(pts);cx=sum(x for x,z in pts)/n;cz=sum(z for x,z in pts)/n
        vs=[B.xyz(cx+(x-cx)*s,cz+(z-cz)*s,h) for h,s in rings for x,z in pts]
        fs=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(len(rings)-1) for i in range(n)]
        fs.append(tuple(reversed(range(n))));cap=len(fs)
        if fan:
            h,s=rings[-1];base=(len(rings)-1)*n
            for i in range(n):vs[base+i]=(vs[base+i][0],vs[base+i][1],h+[.08,-.12,.04,-.05,.12,-.06,.02][i%n])
            centre=len(vs);vs.append(B.xyz(cx+.2,cz-.15,h+.28))
            fs.extend((base+i,base+(i+1)%n,centre) for i in range(n))
        else:fs.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
        o=B.mesh(name,vs,fs,mats)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.material_index=(len(mats)-2+(p.index%2)) if fan and p.index>=cap else min(p.index//n,len(mats)-1)
        return o
    outline=[(-1,-.5),(-.62,-1),(.12,-.90),(.74,-.65),(1,.05),(.68,.81),(-.10,1),(-.86,.54)]
    def sea_mount(spec):
        x,z=spec['centre'];rx,rz=spec['radii'];pts=[(x+a*rx,z+b*rz) for a,b in outline]
        o=prism('Terrain_'+spec['id'],pts,[(-8,1.3),(-1.5,1.15),(.12,1),(.7,.82),(1.4,.53)],
            ['M_ShelfShadow','M_ShelfStone','M_ShelfLight','M_BirdIvory'])
        o['navigation_terrain']=True;o['purpose']=spec['purpose'];return o
    def shelf_bed(name):
        # A connected uneven terrace and sharp 6m escarpment, sealed below.
        w,h=L['size'];nx,nz=91,71;vs=[];fs=[]
        for j in range(nz):
            z=-h*.72+j*h*1.44/(nz-1)
            for i in range(nx):
                edge=25+.28*z+3*math.sin(z/28)
                # Align a shared mesh column with the shelf break rather than
                # cutting a staircase through a rectangular colour grid.
                x=-w*.72+i/50*(edge+w*.72) if i<=50 else edge+(i-50)/(nx-51)*(w*.72-edge)
                depth=4.6 if x<edge else 15.5
                depth+=.12*math.sin(z/21)+.09*math.sin(x/17)
                for g in grounds(NAME):
                    d=math.hypot(x-g['centre']['x'],z-g['centre']['z'])
                    t=math.exp(-(d/(g['radius']+10))**4)
                    depth=depth*(1-t)+g['nominalDepth']*t
                vs.append(B.xyz(x,z,-depth))
        for j in range(nz-1):
            for i in range(nx-1):a=j*nx+i;fs.append((a,a+nx,a+nx+1,a+1))
        edge=list(range(nx))+[j*nx+nx-1 for j in range(1,nz)]+list(range(nz*nx-2,(nz-1)*nx-1,-1))+[j*nx for j in range(nz-2,0,-1)]
        low=[]
        for i in edge:low.append(len(vs));vs.append((vs[i][0],vs[i][1],-28))
        fs += [(a,edge[(i+1)%len(edge)],low[(i+1)%len(edge)],low[i]) for i,a in enumerate(edge)]
        fs.append(tuple(reversed(low)))
        o=B.mesh('ConnectedBathymetry',vs,fs,['M_ShoalSand','M_ShelfTeal','M_ShelfNavy'])
        for p in o.data.polygons:
            d=-sum(o.data.vertices[i].co.z for i in p.vertices)/len(p.vertices)
            centre=sum((o.data.vertices[i].co for i in p.vertices),start=Vector())/len(p.vertices)
            # Exactly one sandbank patch around Herring shoals. Low-amplitude
            # bed variation must not create unrelated circular sand islands.
            shoal=((centre.x+85)/32)**2+((-centre.y+35)/25)**2
            p.material_index=0 if shoal<1 and d<4.5 else 1 if d<10 else 2
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    def local(name):
        # Rock's flat ivory crown is local1.4/world1.08: the gull empty sits ON it.
        # No extra exposed rocks: camera landmarks are submerged broken shelves.
        for j,g in enumerate(grounds(NAME)):
            x,z=g['centre']['x'],g['centre']['z']
            for side in (-1,1):
                cx,cz=offset(x,z,side*5.3,-3.3)
                pts=[offset(cx,cz,a,b) for a,b in [(-2,-1.2),(-1.3,-1.65),(.35,-1.3),(2,-.5),(1.85,.6),(.5,1.2),(-1.8,.8)]]
                mats=['M_ShelfShadow','M_ShoalSand','M_ShoalLight'] if j==0 else ['M_ShelfShadow','M_ShelfStone','M_ShelfLight']
                o=prism('Terrain_SubmergedShoal' if j==0 else 'Terrain_SubmergedShelfEdge',pts,[(-5,1.2),(-1.5,1.1),(-.3,.9)],mats,fan=True)
                o['navigation_terrain']=True
                o['ground']=g['id'];o['purpose']='Underwater angular lower-corner landmark; actual -1m shallow slice, no waterline obstruction.'
    B.island=sea_mount;B.seabed=shelf_bed;B.local_dressing=local;B.horizon=lambda name:[]

def anchor_review():
    import bpy
    from mathutils import Vector
    import build_sea_v2 as B
    folder=ROOT/'Art/Models/Maps'/NAME
    bpy.ops.wm.open_mainfile(filepath=str(folder/(NAME+'SeaV2.blend')))
    bpy.context.view_layer.update()
    anchor_checks=[]
    for a in L['lifeAnchors']:
        x,y,z=a['position']
        hit,location,normal,index,obj,matrix=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((x,-z,50)),Vector((0,0,-1)))
        top=location.z-.32 if hit else None
        passed=abs(top-y)<.001 if a['id']=='WreckGulls_1' else y==-.32 and (top is None or top<-.32)
        anchor_checks.append(dict(id=a['id'],worldPosition=a['position'],highestTerrainWorldY=top,passed=passed))
    assert all(c['passed'] for c in anchor_checks),anchor_checks
    (folder/'SeaV2-anchor-audit.json').write_text(json.dumps(dict(allPassed=True,checks=anchor_checks,scope='Fresh source downward ray: gull anchor on highest visible crown, water anchors at water level with no overlying rock.'),indent=2))
    sc=bpy.context.scene;root=bpy.data.objects['Catchline_'+NAME+'SeaV2'];root.scale=(1,-1,1);root.location.z=-.32
    bg=B.setup_render(sc);bg.inputs[0].default_value=(.55,.73,.8,1);bg.inputs[1].default_value=.7
    d=bpy.data.lights.new('Anchor review sunlight','SUN');o=bpy.data.objects.new('Anchor review sunlight',d);sc.collection.objects.link(o);o.rotation_euler=(.4,-.3,-.5);d.energy=2
    d=bpy.data.cameras.new('Anchor review camera');d.type='ORTHO';cam=bpy.data.objects.new('Anchor review camera',d);sc.collection.objects.link(cam);sc.camera=cam
    water=B.K.box('REVIEW water',(0,0,-.38),(800,800,.12),'M_SeaTeal',0)
    for a in L['lifeAnchors']:
        x,y,z=a['position'];target=Vector((x,z,y))
        # Temporary orange marker is review evidence only, never saved/exported.
        marker=B.K.cyl('REVIEW anchor marker',(x,z,y+.3),.13,.6,'M_SafetyOrange',8)
        cam.location=target+Vector((7,-10,9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=8
        sc.render.filepath=str(folder/('SeaV2-anchor-'+a['id']+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(marker,do_unlink=True)
    print('MAP9 ANCHOR REVIEW RENDERED',flush=True)

if __name__=='__main__':
    mode=(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])[-1]
    folder=ROOT/'Art/Models/Maps'/NAME
    if mode in ('build','review'):
        import build_sea_v2 as B
        dress(B)
        if mode=='build':
            folder.mkdir(parents=True,exist_ok=True)
            (folder/'grounds.json').write_text(json.dumps(dict(map=NAME,grounds=[dict(id=g['id'],name=g['name'],seabedDepth=g['nominalDepth'],poolId=g['poolId']) for g in grounds(NAME)]),indent=2))
        if mode=='review':
            # Clear-water shelf preview; this modifies review water only.
            import bpy
            def clear_shelf_water(scene):
                water=bpy.data.objects.get('REVIEW water')
                if not water:return
                nodes=water.data.materials[0].node_tree.nodes
                shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
                shader.inputs['Transmission Weight'].default_value=.96
                shader.inputs['Emission Strength'].default_value *= .15
                for n in nodes:
                    if n.type=='VOLUME_ABSORPTION':n.inputs['Density'].default_value=.015
            bpy.app.handlers.render_pre.append(clear_shelf_water)
        (B.build if mode=='build' else B.review)(NAME)
    elif mode=='anchors':anchor_review()
    else:raise ValueError(mode)

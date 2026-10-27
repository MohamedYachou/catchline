"""SeaV2 additive map authoring. Blender 5.2 --background --python ... -- MAP build|review.

Terrain is authored X,-worldZ,height, matching ART108. FBX retains the verified
environment X compensation; navigation is sliced from the saved source mesh.
Never saves or replaces a legacy GroundsV1 file or Unity metadata.
"""
import bpy, bmesh, sys, math, json, hashlib, shutil, random
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).parent))
import build_stations as K
from sea_v2_layouts import LAYOUTS, grounds, perimeter_buoys, point
ROOT=K.ROOT
K.PALETTE.update({'M_SeabedSand':'BEA77D','M_CoastStone':'A99A7C','M_CoastWet':'696F64',
 'M_KelpGreen':'477A56','M_CoastSand':'D9C393','M_CoastGrass':'729053',
 'M_DeepWater':'1B586B','M_ReefWater':'52A8A7','M_BuoyRed':'C84B39','M_Horizon':'608A91',
 'M_HorizonFar':'86A6A6','M_FoamIvory':'B5D8CB','M_Roof':'A96642','M_HullBlue':'2A6685'})

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mesh(name,verts,faces,mats):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob)
    for mat in mats:me.materials.append(K.material(mat))
    return ob
def xyz(x,z,h):return (x,-z,h)
def area(p):return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))/2

def island(spec):
    """Closed concentric terrain: actual shelf, beach, cliff, and grass plateau."""
    n=24;cx,cz=spec['centre'];rx,rz=spec['radii'];phase=spec['phase'];height=spec['height']
    rings=[(-7,13,1),(-1.7,8,1),(.35,0,1),(height*.64,0,.88),(height,0,.64)]
    verts=[]
    for k,(h,expand,scale) in enumerate(rings):
        for i in range(n):
            t=2*math.pi*i/n
            wobble=1+.035*math.sin(t*3+phase)+.025*math.cos(t*5+phase)
            # Broad facets without a sawtooth coast; top rises in soft low shoulders.
            zh=h if k<3 else h+.17*math.sin(t*2+phase)
            verts.append(xyz(cx+(rx*scale+expand)*wobble*math.cos(t),cz+(rz*scale+expand)*wobble*math.sin(t),zh))
    faces=[]
    for k in range(len(rings)-1):
        for i in range(n):
            j=(i+1)%n;faces.append((k*n+i,(k+1)*n+i,(k+1)*n+j,k*n+j))
    faces.append(tuple(reversed(range(n))))
    verts.append(xyz(cx,cz,height+.4));center=len(verts)-1
    for i in range(n):faces.append((center,(len(rings)-1)*n+(i+1)%n,(len(rings)-1)*n+i))
    ob=mesh('Terrain_'+spec['id'],verts,faces,['M_CoastWet','M_CoastSand','M_CoastStone','M_CoastGrass'])
    for p in ob.data.polygons:
        ring=p.index//n
        p.material_index=0 if ring==0 else 1 if ring==1 else 2 if ring==2 else (1 if spec['kind']=='sand' else 2 if spec['kind']=='rock' else 3)
    # Recalculate normals because source X,-Z is reflected relative to World XZ.
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob['navigation_terrain']=True;ob['purpose']=spec['purpose'];ob['slice_levels']='0,-1 metres local'
    return ob

def slice_mesh(ob,height):
    """Intersect actual polygon edges, stitch undirected segments into closed loops."""
    segments=[]
    for poly in ob.data.polygons:
        hits=[];vs=[ob.matrix_world@ob.data.vertices[i].co for i in poly.vertices]
        for a,b in zip(vs,vs[1:]+vs[:1]):
            if (a.z-height)*(b.z-height)<0:
                q=a+(b-a)*((height-a.z)/(b.z-a.z));hits.append((round(q.x,5),round(-q.y,5)))
        if len(hits)==2 and hits[0]!=hits[1]:segments.append(hits)
    if not segments:return []
    adj={}
    def weld(p):
        # Float32 interpolation from opposite edge directions can differ a few
        # micrometres. Weld spatially, not by decimal bucket boundaries.
        return next((q for q in adj if math.dist(p,q)<.00015),p)
    for a,b in segments:
        a=weld(a);adj.setdefault(a,[]);b=weld(b);adj.setdefault(b,[])
        adj[a].append(b);adj[b].append(a)
    assert all(len(v)==2 for v in adj.values()),(ob.name,height,'open slice')
    loops=[];unused=set(adj)
    while unused:
        start=min(unused);p=[start];prev=None;cur=start
        while True:
            nxt=next(n for n in adj[cur] if n!=prev)
            if nxt==start:break
            assert nxt not in p,(ob.name,'slice self loop')
            p.append(nxt);prev,cur=cur,nxt
        unused.difference_update(p)
        if area(p)<0:p.reverse()
        assert len(p)<=64
        loops.append(p)
    return loops

def seabed(name):
    layout=LAYOUTS[name];w,h=layout['size'];gs=grounds(name);nx,ny=65,49;v=[];f=[]
    for j in range(ny):
        z=-h*.72+j*h*1.44/(ny-1)
        for i in range(nx):
            x=-w*.72+i*w*1.44/(nx-1);depth=18 if name=='GullDeepChannel' else 8
            for g in gs:
                dist=math.hypot(x-g['centre']['x'],z-g['centre']['z'])
                t=math.exp(-(dist/(g['radius']+12))**4)
                depth=depth*(1-t)+g['nominalDepth']*t
            depth+=.025*math.sin(x*.5+z*.4)
            v.append(xyz(x,z,-depth))
    for j in range(ny-1):
        for i in range(nx-1):a=j*nx+i;f.append((a,a+nx,a+nx+1,a+1))
    # A sealed skirt below every bathymetric point; not a zero-thickness seabed.
    edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(ny*nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
    low=[]
    for i in edge:low.append(len(v));v.append((v[i][0],v[i][1],-25))
    for i,a in enumerate(edge):j=(i+1)%len(edge);f.append((a,edge[j],low[j],low[i]))
    f.append(tuple(reversed(low)))
    ob=mesh('ConnectedBathymetry',v,f,['M_SeabedSand','M_CoastWet','M_DeepWater'])
    for p in ob.data.polygons:
        avg=sum(ob.data.vertices[i].co.z for i in p.vertices)/len(p.vertices)
        p.material_index=2 if avg<-9 else 1 if name in ('GullRockyPoint','GullDeepChannel') else 0
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()

def buoy(x,z,i):
    stem=K.cyl('OuterMarker_%02d_Red'%i,xyz(x,z,.7),.34,1.8,'M_BuoyRed',10)
    K.cyl('OuterMarker_%02d_White'%i,xyz(x,z,1.12),.345,.52,'M_RailIvory',10)
    K.cyl('OuterMarker_%02d_Float'%i,xyz(x,z,.05),.60,.28,'M_HullNavy',12)
    K.cyl('OuterMarker_%02d_Pole'%i,xyz(x,z,1.90),.045,.65,'M_HullNavy',8)
    K.box('OuterMarker_%02d_Topmark'%i,xyz(x,z,2.24),(.42,.08,.35),'M_BuoyRed',.025)
    stem['world_x']=x;stem['world_z']=z

def rock(x,z,h,s,mat='M_CoastStone'):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=xyz(x,z,h))
    o=bpy.context.object;o.name='CoastBoulder';o.scale=(s,s*.78,s*.68);o.data.materials.append(K.material(mat));return o

def kelp(x,z,depth,n=6):
    for i in range(n):
        dx=(i%3-1)*.33;dz=(i//3-.5)*.42;height=min(depth-.15,1.7)
        a=xyz(x+dx-.10,z+dz,-depth);b=xyz(x+dx+.10,z+dz,-depth)
        c=xyz(x+dx+.25,z+dz+.08,-depth+height*.65);d=xyz(x+dx+.02,z+dz+.22,-depth+height)
        v=[a,b,c,d]+[(p[0],p[1]+.022,p[2]) for p in (a,b,c,d)]
        mesh('RootedKelp',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],['M_KelpGreen'])

def local_dressing(name):
    random.seed(name)
    for j,g in enumerate(grounds(name)):
        x,z=g['centre']['x'],g['centre']['z'];d=g['nominalDepth']
        if 'kelp' in g['id'] or g['id']=='mouth-flats':
            count=24 if g['id']=='kelp-shallows' else 12
            for i in range(count):
                t=i*2.39996;r=2.9+(i%5)*.50
                kelp(x+math.cos(t)*r,z+math.sin(t)*r,d,5)
        if name=='GullSandbar' and j==0 or name=='GullHarbourMouth' and j==0:
            for i in range(16):
                xx=x-4+(i%4)*2.3;zz=z-4+(i//4)*2.0
                K.box('SubmergedSandRipple',xyz(xx,zz,-d+.07),(1.25,.12,.035),'M_CoastSand',.02)
        if name=='GullRockyPoint' and j==0:
            # Pale faceted reef crowns read through the water around the boat.
            # All tops remain below -1m; this is navigable submerged dressing.
            for i in range(10):
                t=i*2.39996;r=3.1+(i%3)*.65
                o=rock(x+math.cos(t)*r,z+math.sin(t)*r,-1.72,1.05,'M_CoastStone')
                o.scale.z=.58
        if name=='GullRockyPoint' and j==1:
            # A real submerged stone ledge ends across the anchored view,
            # exposing the deeper bed on its eastern side. Closed slab, no
            # waterline/shallow crossing; do not invent a collision island.
            K.box('SubmergedDropoffShelf',xyz(x-3.4,z,-2.7),(5.0,12.0,2.7),'M_CoastStone',.25)
            for i in range(5):
                o=rock(x-2.8,z-4+i*2,-1.83,.78,'M_CoastStone');o.scale.z=.42
    if name=='GullHarbourMouth':
        # Solid harbour foundation is navigation terrain, with its own true slices.
        ob=K.box('Terrain_HarbourWall',xyz(-74,49,-.2),(25,9,3.4),'M_CoastStone',.22);ob['navigation_terrain']=True;ob['purpose']='Solid harbour wall; stays outside Quay shallows zone.'
        for i in range(18):K.box('HarbourDeckPlank',xyz(-85.5+i*1.35,48.5,1.55),(1.28,7.7,.18),'M_DeckWood',.04)
        for x in (-84,-76,-68):
            K.cyl('QuayBollard',xyz(x,45.8,1.94),.18,.58,'M_HullNavy')
            K.torus('QuayRope',xyz(x,45.8,1.78),.22,.055,'M_Rope')
        for x,z in [(-73,36),(-58,37),(-52,21)]:
            # Moorings are submerged pads, no unreported collision posts in the zone.
            K.cyl('SubmergedMooringPad',xyz(x,z,-1.25),.42,.15,'M_CoastWet')
        for x in (-70,-68,-66):
            o=K.cyl('Terrain_MooringPost',xyz(x,42,0),.20,2.8,'M_DeckWood',10)
            o['navigation_terrain']=True;o['purpose']='Mooring outside the entire anchor zone and its 2m safety band.'
            K.torus('MooringRope',xyz(x,42,.80),.22,.045,'M_Rope')
        for x,z,mat in [(2.8,-31.8,'M_RailIvory'),(9.2,-36.2,'M_BuoyRed')]:
            K.cyl('ChannelMarker',xyz(x,z,.15),.18,.45,mat,10)
            K.cyl('ChannelMarkerPole',xyz(x,z,.56),.025,.50,'M_HullNavy',8)
        for x in (-70,-42,-10,23,57):
            K.box('HouseStoneFooting',xyz(x,60,1.5),(6.4,5.2,4.0),'M_CoastStone',.10)
            house(x,60,3.5)
        K.cyl('LighthouseStoneFooting',xyz(78,61,1.5),1.5,4.0,'M_CoastStone',12)
        lighthouse(78,61,3.5,1)
    for spec in LAYOUTS[name]['islands']:
        cx,cz=spec['centre'];rx,rz=spec['radii'];hh=spec['height']
        for i in range(7):
            t=2*math.pi*i/7+spec['phase'];r=.37
            rock(cx+math.cos(t)*rx*r,cz+math.sin(t)*rz*r,hh+.35,1.0+(i%3)*.45)

def house(x,z,h):
    K.box('HarbourHouse',xyz(x,z,h+1.8),(6,4.8,3.6),'M_RailIvory',.12)
    # Two sloped faces and closed gables, with broad roof silhouette.
    v=[xyz(x-3.4,z-2.8,h+3.6),xyz(x+3.4,z-2.8,h+3.6),xyz(x-3.4,z,h+5.1),xyz(x+3.4,z,h+5.1),xyz(x-3.4,z+2.8,h+3.6),xyz(x+3.4,z+2.8,h+3.6)]
    mesh('WarmRoof',v,[(0,1,3,2),(2,3,5,4),(0,2,4),(1,5,3),(0,4,5,1)],['M_Roof'])
    K.box('HouseDoor',xyz(x,z-2.43,h+1.0),(1.0,.07,2),'M_HullNavy',.035)
    for dx in (-1.8,1.8):K.box('HouseWindow',xyz(x+dx,z-2.45,h+2.1),(.9,.08,1.1),'M_HullBlue',.04)

def lighthouse(x,z,h,scale=1):
    K.cyl('LighthouseTower',xyz(x,z,h+3*scale),1.05*scale,6*scale,'M_RailIvory',12)
    K.cyl('LighthouseBand',xyz(x,z,h+4.2*scale),1.06*scale,.9*scale,'M_BuoyRed',12)
    K.cyl('LighthouseGallery',xyz(x,z,h+6.05*scale),1.45*scale,.28*scale,'M_HullNavy',12)
    K.cyl('LighthouseLantern',xyz(x,z,h+6.75*scale),.82*scale,1.2*scale,'M_OilskinYellow',10)
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=1.4*scale,radius2=0,depth=.8*scale,location=xyz(x,z,h+7.6*scale))
    bpy.context.object.name='LighthouseRoof';bpy.context.object.data.materials.append(K.material('M_HullNavy'))

def horizon(name):
    w,h=LAYOUTS[name]['size'];items=[]
    for i,(x,z,rx,rz,hh) in enumerate([(-w*.53,h*.79,w*.23,16,9),(w*.39,h*.85,w*.19,20,7),(-w*.85,-h*.2,23,h*.22,6),(w*.84,-h*.27,18,h*.18,5)]):
        spec=dict(id='horizon-'+str(i),centre=(x,z),radii=(rx,rz),height=hh,purpose='Unreachable horizon silhouette beyond the buoy ring.',kind='rock',phase=i)
        ob=island(spec);ob.name='HorizonHeadland_%d'%i;ob['navigation_terrain']=False
        ob.data.materials.clear();ob.data.materials.append(K.material('M_HorizonFar' if i%2 else 'M_Horizon'))
        for p in ob.data.polygons:p.material_index=0
        items.append(dict(id=ob.name,kind='headland',centre=point((x,z)),reachable=False))
    lx,lz=w*.39,h*.85;lighthouse(lx,lz,7,1.0)
    items.append(dict(id='outer-lighthouse',kind='lighthouse',centre=point((lx,lz)),reachable=False))
    sx,sz=w*.64,h*.69
    K.box('HorizonShipHull',xyz(sx,sz,1.25),(20,4,2.5),'M_Horizon',.6)
    K.box('HorizonShipCabin',xyz(sx+5,sz,3.6),(5,3.8,3),'M_HorizonFar',.25)
    K.box('HorizonShipFunnel',xyz(sx+2,sz,5.25),(1.7,1.7,1.4),'M_Horizon',.10)
    items.append(dict(id='outer-freighter',kind='ship',centre=point((sx,sz)),reachable=False))
    return items

def build(name):
    folder=ROOT/'Art/Models/Maps'/name;folder.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    for spec in LAYOUTS[name]['islands']:island(spec)
    seabed(name);local_dressing(name)
    w,h=LAYOUTS[name]['size'];buoys=perimeter_buoys(w,h)
    for i,(x,z) in enumerate(buoys):buoy(x,z,i)
    horizons=horizon(name)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in meshes:
        bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.select_set(False)
    bpy.context.view_layer.update()
    nav=dict(schema=2,map=name,runtimeModelId=name+'SeaV2',runtimeFile=f'Assets/Art/Models/Environment/{name}/{name}SeaV2.fbx',units='metres',
      coordinateSpace='World XZ, same horizontal frame as grounds.json; source Blender X,-Z,height; no recentering.',
      waterlineLocal=0,worldPosition=[0,-.32,0],rotation=[0,0,0],scale=[1,1,1],
      boatDeckY=0,sliceLevels=dict(islands=0,shallows=-1),islands=[],shallows=[],
      border=[point(p) for p in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]],
      grounds=grounds(name),harbour=point(LAYOUTS[name]['harbour']),
      cameraBounds=dict(min=point((-w/2+8,-h/2+8)),max=point((w/2-8,h/2-8))),
      outerBuoys=[dict(id=f'outer-{i:02}',position=point(p),style='red-white-spar',baseRadius=.6) for i,p in enumerate(buoys)],
      fog=dict(inset=30,edgeDensity=1,waterContinuesBeyondBorder=True,horizonSilhouettes=horizons),
      islandPurposes={s['id']:s['purpose'] for s in LAYOUTS[name]['islands']})
    nav['artReviewAnchors']={g['id']:g['centre'] for g in nav['grounds']}
    if name=='GullHarbourMouth':nav['artReviewAnchors']['quay-shallows']=point((-66,38.5))
    for o in meshes:
        if not o.get('navigation_terrain'):continue
        for field,level in [('islands',0),('shallows',-1)]:
            for i,p in enumerate(slice_mesh(o,level)):
                nav[field].append(dict(id=o.name.replace('Terrain_','')+f'-{i}',vertices=[point(a) for a in p],sourceObject=o.name,sliceY=level))
    root=bpy.data.objects.new('Catchline_'+name+'SeaV2',None);bpy.context.scene.collection.objects.link(root)
    root['waterline_local_y']=0;root['world_y']=-.32;root['map_size_x']=w;root['map_size_z']=h
    for o in meshes:o.parent=root
    # Optional additive map anchors share the compensated FBX frame of the terrain.
    anchors=[]
    for anchor in LAYOUTS[name].get('sealColonyAnchors',[])+LAYOUTS[name].get('lifeAnchors',[]):
        x,y,z=anchor['position'];o=bpy.data.objects.new(anchor['id'],None)
        bpy.context.scene.collection.objects.link(o);o.parent=root;o.location=xyz(x,z,y+.32)
        o.empty_display_size=1;anchors.append(o)
    if anchors:nav['sealColonyAnchors']=LAYOUTS[name]['sealColonyAnchors']
    if LAYOUTS[name].get('lifeAnchors'):nav['lifeAnchors']=LAYOUTS[name]['lifeAnchors']
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    blend=folder/f'{name}SeaV2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    (folder/'navigation.json').write_text(json.dumps(nav,indent=2))
    rec=dict(map=name,triangles=K.tris(meshes),meshCount=len(meshes),sourceBounds=K.bounds(meshes),playableSize=[w,h],
       sourceSha256=digest(blend),sliceMethod='actual closed terrain polygon-edge intersections at local Z=0 and -1, transformed to World XZ, CCW',
       islandCount=len(nav['islands']),shallowCount=len(nav['shallows']),buoyCount=len(buoys),
       sourceVertices={o.name:len(o.data.vertices) for o in meshes})
    positions={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in meshes}
    for o in meshes:
        for v in o.data.vertices:x,y,z=v.co;v.co=(-x,z,-y)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for o in anchors:
        x,y,z=o.location;o.location=(-x,z,-y)
    bpy.ops.object.select_all(action='SELECT');fbx=folder/f'{name}SeaV2.fbx'
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',
      apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=False,bake_space_transform=False,use_triangles=True,bake_anim=False,add_leaf_bones=False)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(fbx))
    actual=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert K.tris(actual)==rec['triangles']
    maxerr=0
    for o in actual:
        kd=KDTree(len(o.data.vertices))
        for i,v in enumerate(o.data.vertices):p=o.matrix_world@v.co;kd.insert(Vector((-p.x,p.y,p.z)),i)
        kd.balance();maxerr=max(maxerr,max(kd.find(v)[2] for v in positions[o.name]))
    assert maxerr<.0001,(name,maxerr)
    rec.update(roundTripMaxVertexError=maxerr,actualFbxTriangles=K.tris(actual),fbxSha256=digest(fbx),navigationSha256=digest(folder/'navigation.json'),allPassed=True)
    (folder/'SeaV2-validation.json').write_text(json.dumps(rec,indent=2))
    print('SEAV2 BUILD PASS',name,rec['triangles'],len(nav['islands']),len(buoys),maxerr,flush=True)

def setup_render(sc):
    sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.cycles.max_bounces=6;sc.cycles.transmission_bounces=4
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
        for dev in prefs.devices:dev.use=dev.type=='OPTIX'
        if any(dev.use for dev in prefs.devices):sc.cycles.device='GPU'
    except Exception:pass
    sc.view_settings.view_transform='AgX';sc.render.resolution_x=1440;sc.render.resolution_y=900;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB'
    sc.world=bpy.data.worlds.new('SeaV2 review ambient');sc.world.use_nodes=True
    return next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND')

def review(name):
    folder=ROOT/'Art/Models/Maps'/name;bpy.ops.wm.open_mainfile(filepath=str(folder/f'{name}SeaV2.blend'))
    bpy.context.preferences.filepaths.save_version=0
    sc=bpy.context.scene;nav=json.loads((folder/'navigation.json').read_text());root=bpy.data.objects['Catchline_'+name+'SeaV2']
    root.scale=(1,-1,1);root.location.z=-.32
    src=ROOT/'Art/Models/GullHarbour/Boats/Rowboat.blend'
    with bpy.data.libraries.load(str(src),link=False) as (a,b):b.objects=[n for n in a.objects if n.startswith('Catchline_Rowboat') or n in ['Hull','PlankDeck','IvoryGunwale','CentreThwart','Oar_Port','Oar_Starboard','Oarlock_Port','Oarlock_Starboard','RodSocket_Port_Bow','RodSocket_Port_Stern']]
    for o in b.objects:
        if o:sc.collection.objects.link(o)
    boat=next(o for o in b.objects if o and o.type=='EMPTY');boat.rotation_euler.z=math.pi/2;boat.scale=(1,-1,1)
    bg=setup_render(sc)
    w,h=LAYOUTS[name]['size']
    water=K.box('REVIEW water',(0,0,-13.32),(max(w,h)*6,max(w,h)*6,26),'M_SeaTeal',0)
    mat=water.data.materials[0].copy();water.data.materials[0]=mat
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Transmission Weight'].default_value=.82
    shader.inputs['Roughness'].default_value=.20 if name=='GullRockyPoint' else .32
    shader.inputs['Transmission Weight'].default_value=.96 if name=='GullRockyPoint' else .82
    shader.inputs['IOR'].default_value=1.333
    absorption=mat.node_tree.nodes.new('ShaderNodeVolumeAbsorption');absorption.inputs['Color'].default_value=(.11,.66,.65,1);absorption.inputs['Density'].default_value=.055
    out=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL');mat.node_tree.links.new(absorption.outputs[0],out.inputs['Volume'])
    keydata=bpy.data.lights.new('SeaV2 sun','SUN');key=bpy.data.objects.new('SeaV2 sun',keydata);sc.collection.objects.link(key);key.rotation_euler=(.35,-.45,-.5);keydata.angle=.12
    filldata=bpy.data.lights.new('Boat fill','AREA');fill=bpy.data.objects.new('Boat fill',filldata);sc.collection.objects.link(fill);filldata.size=6
    pools=[]
    for i in range(2):
        d=bpy.data.lights.new('Deck lantern','SPOT');d.energy=45;d.color=(1,.66,.30);d.shadow_soft_size=.08;d.spot_size=math.radians(78);d.spot_blend=.55
        o=bpy.data.objects.new('Deck lantern',d);sc.collection.objects.link(o);pools.append(o)
    d=bpy.data.cameras.new('SeaV2 gameplay camera');d.type='ORTHO';d.ortho_scale=10.24;d.clip_end=2000
    cam=bpy.data.objects.new('SeaV2 gameplay camera',d);sc.collection.objects.link(cam);sc.camera=cam
    pitch,yaw=math.radians(45),math.radians(35);forward=Vector((math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),-math.sin(pitch)))
    cam.rotation_euler=forward.to_track_quat('-Z','Y').to_euler()
    for g in nav['grounds']:
        sample=nav['artReviewAnchors'][g['id']];x,z=sample['x'],sample['z'];boat.location=(x,z,0);target=Vector((x+.35,z-.30,0));cam.location=target-forward*40;cam.data.ortho_scale=10.24
        mix=max(0,min(1,(g['nominalDepth']-1.2)/8));tint=tuple(a+(b-a)*mix for a,b in zip((.025,.48,.50),(.008,.12,.24)))
        if 'waterShallow' in LAYOUTS[name]:
            def linear_hex(value):
                c=[int(value[i:i+2],16)/255 for i in (0,2,4)]
                return [v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
            tint=tuple(a+(b-a)*mix for a,b in zip(linear_hex(LAYOUTS[name]['waterShallow']),linear_hex(LAYOUTS[name]['waterDeep'])))
        shader.inputs['Base Color'].default_value=(*tint,1);shader.inputs['Emission Color'].default_value=(*tint,1)
        fill.location=(x-4,z+2,7);fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
        for i,p in enumerate(pools):p.location=(x+.3+i*1.4,z+.5,1.35)
        for night in (False,True):
            shader.inputs['Emission Strength'].default_value=(.005 if night else .035) if name=='GullRockyPoint' else (.018 if night else .14)
            bg.inputs[0].default_value=(.08,.13,.26,1) if night else (.55,.73,.80,1);bg.inputs[1].default_value=.25 if night else .48
            keydata.energy=.12 if night else 1.5;keydata.color=(.44,.58,1) if night else (1,.90,.74)
            filldata.energy=75 if night else 350;filldata.color=(.32,.46,1) if night else (.66,.84,1)
            for p in pools:p.hide_render=not night
            sc.render.filepath=str(folder/f'SeaV2-{g["id"]}-{"night" if night else "day"}.png');bpy.ops.render.render(write_still=True)
    for o in [boat]+list(boat.children_recursive):o.hide_render=True
    for p in pools:p.hide_render=True
    fill.hide_render=True;keydata.energy=1.5;keydata.color=(1,.9,.74);bg.inputs[0].default_value=(.55,.73,.80,1);bg.inputs[1].default_value=.6
    shader.inputs['Base Color'].default_value=(.025,.35,.38,1);shader.inputs['Emission Color'].default_value=(.025,.35,.38,1);shader.inputs['Emission Strength'].default_value=.10
    # Actual world-scaled mist volumes: transparent centre, 30m band, denser at/beyond edge.
    fogmat=bpy.data.materials.new('REVIEW sea fog');fogmat.use_nodes=True;nodes=fogmat.node_tree.nodes;nodes.clear()
    output=nodes.new('ShaderNodeOutputMaterial');vol=nodes.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.64,.78,.79,1)
    fogmat.node_tree.links.new(vol.outputs['Volume'],output.inputs['Volume'])
    links=fogmat.node_tree.links;geo=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Position'],sep.inputs[0]);ramps=[]
    for axis,span in [('X',w),('Y',h)]:
        ab=nodes.new('ShaderNodeMath');ab.operation='ABSOLUTE';links.new(sep.outputs[axis],ab.inputs[0])
        sub=nodes.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=span/2-30;links.new(ab.outputs[0],sub.inputs[0])
        ramp=nodes.new('ShaderNodeMath');ramp.operation='DIVIDE';ramp.inputs[1].default_value=30;ramp.use_clamp=True;links.new(sub.outputs[0],ramp.inputs[0]);ramps.append(ramp)
    maximum=nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM'
    for i,ramp in enumerate(ramps):links.new(ramp.outputs[0],maximum.inputs[i])
    mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.010;links.new(maximum.outputs[0],mul.inputs[0]);links.new(mul.outputs[0],vol.inputs['Density'])
    o=K.box('REVIEW border fog',(0,0,7),(w*4,h*4,22),'M_RailIvory',0);o.data.materials.clear();o.data.materials.append(fogmat)
    target=Vector((0,0,0));cam.location=(0,-h*1.65,h*.8);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=w*1.85
    sc.render.filepath=str(folder/'SeaV2-wide-day.png');bpy.ops.render.render(write_still=True)
    bg.inputs[0].default_value=(.08,.13,.26,1);bg.inputs[1].default_value=.25;keydata.energy=.18;keydata.color=(.44,.58,1);shader.inputs['Emission Strength'].default_value=.018
    sc.render.filepath=str(folder/'SeaV2-wide-night.png');bpy.ops.render.render(write_still=True)
    # Unannotated true orthographic source for the dimensioned navigation plate.
    for o in sc.objects:
        if o.name.startswith('REVIEW border fog'):o.hide_render=True
    bg.inputs[0].default_value=(.55,.73,.80,1);bg.inputs[1].default_value=.65;keydata.energy=1.3;keydata.color=(1,.92,.8);shader.inputs['Emission Strength'].default_value=.10
    cam.location=(0,0,400);cam.rotation_euler=(0,0,0);cam.data.ortho_scale=w*1.24
    sc.render.resolution_x=1800;sc.render.resolution_y=1400
    sc.render.filepath=str(folder/'SeaV2-top-base.png');bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'SeaV2-Review-only.blend'))
    print('SEAV2 REVIEW RENDERED',name,flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];(build if args[1]=='build' else review)(args[0])

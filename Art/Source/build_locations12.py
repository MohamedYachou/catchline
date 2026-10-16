"""ART-012, Blender 5.2: existing Gull locations, no runtime/water dependencies.

-- GullKelpBank|GullSandbar|GullRockyPoint|GullDeepChannel build|preview|export
Canonical source x,-UnityZ,up. Unity FBX explicitly compensates measured X mirror.
"""
import ast, bpy, bmesh, importlib.util, json, math, sys, types
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('harbour12', Path(__file__).with_name('build_harbour_mouth11.py'))
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)
B, G, K = H.B, H.G, H.K
NAMES = ('GullKelpBank','GullSandbar','GullRockyPoint','GullDeepChannel')
NAME = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else NAMES[0]
OUT = ROOT/'Art/Models/Locations12'/NAME
COL = None
GROUPS = {}
point = H.point
WATER = -.32
BUDGET = 24000
# All contours are deliberate camera-ground plans. No random island scatter.
SAND_PLAN = [(-8.8,-.8),(-5.5,-.65),(-4.1,-.05),(-3.6,1.0),(-3.7,2.0),
             (-2.9,2.45),(-1.8,2.50),(-.4,2.40),(1.0,2.48),(2.1,2.70),
             (3.2,2.30),(4.0,1.95),(4.9,1.90),(5.9,2.45),(6.3,3.5),
             (5.6,4.8),(3.7,5.8),(3.6,4.3),(4.1,3.4),(3.5,3.1),
             (2.6,3.35),(1.5,3.8),(-.2,3.45),(-2.3,3.65),(-3.6,4.6),
             (-5.3,4.7),(-6.8,3.4),(-8.8,2.0)]
ROCK_PLAN = [(2.8,2.35),(3.35,2.10),(3.5,1.4),(3.9,1.1),(4.45,1.35),
             (4.6,2.2),(5.5,2.5),(6.7,2.25),(8.6,2.65),(8.8,5.7),
             (1.4,5.8),(1.3,4.1),(2.2,3.1)]

def gauss(s,t,x,y,wx,wy):
    return math.exp(-((s-x)/wx)**2-((t-y)/wy)**2)

def signed_distance(s,t,plan):
    d=H.distance((s,t),plan)
    if d>0:return -d
    # H.distance returns zero inside; compute nearest segment for smooth inshore slope.
    p=Vector((s,t));distance=100
    for a,b in zip(plan,plan[1:]+plan[:1]):
        a,b=Vector(a),Vector(b);v=b-a
        distance=min(distance,(p-a-v*max(0,min(1,(p-a).dot(v)/v.length_squared))).length)
    return distance

def depth(s,t):
    if NAME=='GullKelpBank':
        # Reef shoulders are one continuous sea floor, joined behind the channel.
        shelf=max(gauss(s,t,-4.5,.45,1.9,3.7),gauss(s,t,4.65,1.55,2.15,3.0),
                  .88*gauss(s,t,.4,3.8,5.0,1.30))
        z=-3.15+2.78*shelf
        z+=.045*math.sin(s*2+t)*shelf
    elif NAME=='GullSandbar':
        d=signed_distance(s,t,SAND_PLAN)
        # Continuous sloping intertidal shoal, broad dry ridge, sheltered lagoons.
        z=.42 if d>=.30 else (.42-(.30-d)*.9 if d>=-.75 else -.525-(abs(d)-.75)*.8)
        z=max(-3.3,z)
        z+=.055*math.sin(s*1.25+t*.8)*max(0,min(1,(d+.55)/.8))
    elif NAME=='GullRockyPoint':
        d=H.distance((s,t),ROCK_PLAN)
        left=gauss(s,t,-5.7,-.8,1.7,2.3)
        z=max(-3.3,-.18-1.2*d,-3.3+2.8*left)
    else:
        # Calm open channel: submerged shoulders framing a clean broad deep trough.
        shoulder=max(gauss(s,t,-7.2,1.0,2.6,5.2),gauss(s,t,7.5,2.0,2.9,5.0))
        z=-4.25+2.35*shoulder
    # Shore plans themselves reserve the channel; do not carve a rectangular
    # clamp into otherwise continuous shoals. Actual mesh rays verify clearance.
    return z

def mesh(name,g,group,bevel=0,weld=True):
    H.COL=COL;H.GROUPS=GROUPS
    return H.mesh(name,g,group,bevel,weld)

def terrain():
    # Connected closed height field. Samples include channel boundaries exactly.
    xs=sorted(set([-9+i*18/72 for i in range(73)]+[-2.85,2.85]))
    ts=sorted(set([-6+j*12/56 for j in range(57)]+[-2.05,1.9]))
    n,m=len(xs),len(ts);vs=[point(s,t,depth(s,t)) for t in ts for s in xs]
    faces=[];mats=[]
    for j in range(m-1):
        for i in range(n-1):
            ids=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            z=sum(vs[k][2] for k in ids)/4
            if NAME=='GullSandbar':
                mat='M_CoastSand' if z>.03 else 'M_SeabedSand'
            elif NAME=='GullKelpBank':
                mat='M_CoastStone' if z>-.6 else 'M_SeabedSand'
            else:mat='M_CoastWet' if z<-1.4 else 'M_CoastStone'
            faces.append(ids);mats.append(mat)
    edge=list(range(n))+[j*n+n-1 for j in range(1,m)]+list(range((m-1)*n+n-2,(m-1)*n-1,-1))+[j*n for j in range(m-2,0,-1)]
    base=-5.1 if NAME=='GullDeepChannel' else -4.2
    for idx in edge:vs.append((vs[idx][0],vs[idx][1],base))
    off=n*m
    for k in range(len(edge)):
        q=(k+1)%len(edge);faces.append((edge[k],off+k,off+q,edge[q]));mats.append('M_CoastWet')
    faces.append(tuple(reversed(range(off,len(vs)))));mats.append('M_CoastWet')
    me=bpy.data.meshes.new('Continuous authored bathymetry');me.from_pydata(vs,[],faces);me.update()
    ob=bpy.data.objects.new('Terrain_ConnectedShoalsAndSeabed',me);COL.objects.link(ob);ob.parent=GROUPS['Seabed']
    used=list(dict.fromkeys(mats))
    for name in used:me.materials.append(B.MATERIALS[name])
    for face,mat in zip(me.polygons,mats):
        face.material_index=used.index(mat)
        # Continuous underwater slopes should not read as a square stair grid.
        # Keep the skirt flat; rock outcrops remain intentionally faceted.
        face.use_smooth=face.index<(n-1)*(m-1)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()

def frond(g,s,t,h,height,width,phase,mat):
    # Closed curved broad leaf, rooted below actual seabed. Low section count, no planes.
    rings=[];seg=9
    for i in range(seg+1):
        f=i/seg
        center=Vector(point(s+.18*height*f*f*math.sin(phase+f*2),t+.10*height*f*f,h+height*f))
        w=max(.009,width*math.sin(math.pi*f)**.7)
        axis=Vector((math.cos(phase+f*.5),math.sin(phase+f*.5),.05*math.sin(f*4)))
        thick=.009
        rings.extend([tuple(center-axis*w+Vector((0,0,-thick))),tuple(center+axis*w+Vector((0,0,-thick))),
                      tuple(center+axis*w+Vector((0,0,thick))),tuple(center-axis*w+Vector((0,0,thick)))])
    fs=[(3,2,1,0)]
    for i in range(seg):
        for k in range(4):fs.append((i*4+k,i*4+(k+1)%4,(i+1)*4+(k+1)%4,(i+1)*4+k))
    fs.append(tuple(range(seg*4,(seg+1)*4)))
    g.add(rings,fs,mat)

def kelp():
    # Five rooted clusters on two shoulders, no mat over the centre or surface discs.
    clusters=[(-4.1,-.6,[-.3,.1,.38]),(-3.65,1.4,[-.22,.14]),
              (3.85,1.15,[-.22,.2]),(4.9,-.5,[-.25,.1,.34]),(.7,3.55,[-.3,.2])]
    for idx,(s,t,offsets) in enumerate(clusters):
        g=G()
        for k,ds in enumerate(offsets):
            a,b=s+ds,t+(k%2)*.25;h=depth(a,b)-.06
            # Mostly underwater. Only three high sheltered tips reach through surface.
            top=.055 if (idx,k) in ((0,1),(2,0),(4,0)) else -.18-.1*(k%2)
            for j in range(2):
                frond(g,a+j*.12,b,h,max(.16,top-h-j*.13),.13+.025*(k%2),idx*1.3+k*.8+j*.7,
                      'M_KelpGreen' if j==0 else 'M_CoastGrass')
            g.ellipsoid(point(a,b,h+.06),(.14,.14,.10),8,4,'M_CoastWet')
        mesh('Kelp_RootedBroadFronds_%02d'%idx,g,'Details')
    # One attached low tide reef spine, rather than floating mats and loose boulders.
    H.land('KelpReefSpine',[(-6.3,.7),(-5.4,.4),(-4.85,.7),(-4.75,1.45),(-5.25,1.95),(-6.6,1.9)],.24)

def sand():
    # A readable old mooring embedded in the one exposed sand ridge; no buildings/new content.
    g=G()
    for i,(s,t) in enumerate([(-4.25,1.0),(-4.02,1.62)]):
        z=depth(s,t)-.09
        g.beam(point(s,t,z),point(s+.03,t+.02,z+.46),.10,.10,'M_WoodRecess',.012)
        K.lathe(g,[(0,.063),(.025,.063)],10,'M_WoodHighlight',point(s+.03,t+.02,z+.46))
    g.beam(point(-4.22,1.02,depth(-4.25,1.0)+.30),point(-3.99,1.64,depth(-4.02,1.62)+.30),.025,.025,'M_Rope')
    mesh('SandRidge_OldMooring',g,'Details')
    g=G()
    for k,(s,t) in enumerate([(-4.4,.9),(-3.95,2.6),(2.4,2.85)]):
        z=depth(s,t)-.02
        for j in range(5):
            a=j*2.4+k
            g.beam(point(s,t,z),point(s+.10*math.cos(a),t+.08*math.sin(a),z+.24+.035*(j%2)),.026,.014,'M_CoastGrassLight')
    mesh('SandRidge_SparseDuneGrass',g,'Details')
    # Bleached driftwood grounded on the shoal; purposefully one small pair.
    g=G()
    for s,t,ds,dt in [(-4.7,.3,.7,.22),(-4.4,.6,.5,-.1)]:
        a=point(s,t,depth(s,t)+.045);b=point(s+ds,t+dt,depth(s+ds,t+dt)+.045)
        g.beam(a,b,.10,.09,'M_WoodHighlight',.018)
    mesh('SandRidge_GroundedDriftwood',g,'Details')

def rocky():
    H.land('RockyPoint_JoinedCliffSpur',ROCK_PLAN,1.05)
    H.land('RockyPoint_LowTidalLedge',[(-7.4,-1.1),(-5.8,-1.4),(-4.55,-.95),(-4.4,-.35),(-5,.2),(-6.7,.6),(-8.2,.1)],.35)
    # Attach broad fracture ribs to the point. No unrelated arch/rock scatter.
    for i,(s,t) in enumerate([(3.65,1.62),(4.0,1.68),(4.45,2.45)]):
        g=G();g.ellipsoid(point(s,t,.37),(.24,.35,.65),7,4,'M_CoastStoneLight')
        mesh('Cliff_AttachedFracture_%d'%i,g,'Shoreline')
    # Simple wind-shaped grass on the broad land behind the point.
    g=G()
    for s,t in [(3.05,3.2),(4.8,3.3),(6.1,3.0)]:
        for j in range(5):
            a=j*2.4;g.beam(point(s,t,.99),point(s+.14*math.cos(a),t+.12*math.sin(a),1.24),.028,.018,'M_CoastGrassLight')
    mesh('RockyPoint_CrestGrass',g,'Details')

def deep():
    # Only submerged toe ribs at the far edges. Centre remains visually open.
    for i,(s,t) in enumerate([(-7.5,2.0),(7.7,2.3)]):
        g=G();z=depth(s,t)-.14
        g.ellipsoid(point(s,t,z),(.4,.9,.25),9,5,'M_CoastWet')
        mesh('Channel_SubmergedShoulder_%d'%i,g,'Shoreline')

def build():
    global COL,GROUPS
    OUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    B.PALETTE.update(H.PAL);B.MATERIALS.clear();B.MATERIALS.update({k:B.material(k,v) for k,v in B.PALETTE.items()})
    COL=bpy.data.collections.new('ENV_EXPORT_ONLY');bpy.context.scene.collection.children.link(COL)
    root=bpy.data.objects.new('Catchline_'+NAME,None);COL.objects.link(root);root['unity_waterline_y']=0.0
    GROUPS={}
    for name in ('Shoreline','Seabed','Details'):
        ob=bpy.data.objects.new(name,None);COL.objects.link(ob);ob.parent=root;GROUPS[name]=ob
    H.COL=COL;H.GROUPS=GROUPS
    terrain()
    {'GullKelpBank':kelp,'GullSandbar':sand,'GullRockyPoint':rocky,'GullDeepChannel':deep}[NAME]()
    bpy.context.view_layer.update()
    stats=[B.mesh_stats(o) for o in COL.objects if o.type=='MESH']
    tris=sum(x['triangles'] for x in stats);assert tris<BUDGET,(NAME,tris)
    (OUT/'build-metrics.json').write_text(json.dumps(dict(asset=NAME,triangles=tris,budget=BUDGET,parts=stats),indent=2)+'\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(NAME+'.blend')))
    print('ART-012 BUILT',NAME,tris,flush=True)

def export():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/(NAME+'.blend')))
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.collections['ENV_EXPORT_ONLY'].objects:
        o.select_set(True)
        if o.type=='MESH':
            for v in o.data.vertices:
                x,y,z=v.co;v.co=(-x,z,-y)
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    bpy.context.view_layer.objects.active=bpy.data.objects['Catchline_'+NAME]
    dest=ROOT/'Assets/Art/Models/Environment'/(NAME+'.fbx');dest.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=str(dest),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=False,bake_space_transform=False,
        use_triangles=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,use_custom_props=True)
    print('ART-012 EXPORTED',NAME,flush=True)

def preview(draft=False):
    # Read-only existing camera/boat/crew reference; never changes its source assets.
    src=Path(__file__).with_name('render_first_voyage10.py');tree=ast.parse(src.read_text())
    for i,node in enumerate(tree.body):
        if isinstance(node,ast.If) and isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.Name) and node.test.left.id=='MODE':
            tree.body=tree.body[:i];break
    r=types.ModuleType('location_reference');r.__file__=str(src);exec(compile(tree,str(src),'exec'),r.__dict__)
    r.MODE='refined';r.make_scene(broad=False,contact=False);scene=bpy.context.scene
    with bpy.data.libraries.load(str(OUT/(NAME+'.blend')),link=False) as (src,dst):dst.collections=['ENV_EXPORT_ONLY']
    col=dst.collections[0];scene.collection.children.link(col)
    root=next(o for o in col.objects if o.name=='Catchline_'+NAME);root.scale=(1,-1,1);root.location.z=WATER
    bpy.data.objects.remove(bpy.data.objects['REF_Water_NotRuntime'],do_unlink=True)
    # Clear reference glass shows authored underwater geometry; this is NOT a
    # proposal to replace Windows' live water shader or its richer layered look.
    mat=B.material('REF_ONLY_LocationWater','#AFE4DE',.23)
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Transmission Weight'].default_value=.98;shader.inputs['IOR'].default_value=1.333
    shader.inputs['Specular IOR Level'].default_value=.14
    shader.inputs['Emission Color'].default_value=B.linear_colour('#168F9F');shader.inputs['Emission Strength'].default_value=.025
    absorption=mat.node_tree.nodes.new('ShaderNodeVolumeAbsorption');absorption.inputs['Color'].default_value=B.linear_colour('#64C7C4');absorption.inputs['Density'].default_value=.065
    mat.node_tree.links.new(absorption.outputs[0],mat.node_tree.nodes.get('Material Output').inputs['Volume'])
    bpy.ops.mesh.primitive_cube_add(size=1,location=(1,0,-3.32));water=bpy.context.object;water.name='REF_ONLY_Water_NotExported';water.scale=(80,80,6);water.data.materials.append(mat)
    scene.cycles.samples=24;scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type='OPTIX';prefs.get_devices()
        for d in prefs.devices:d.use=d.type=='OPTIX'
        if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
        print('Review render device:',scene.cycles.device,flush=True)
    except Exception as exc:print('CPU render fallback:',exc,flush=True)
    if draft:
        scene.cycles.samples=8;scene.render.resolution_x=720;scene.render.resolution_y=450;scene.camera.data.ortho_scale=10.24
        scene.render.filepath=str(OUT/'Draft-review.png');bpy.ops.render.render(write_still=True);return
    for device,w,h in [('desktop',1440,900),('phone',844,390)]:
        scene.render.resolution_x=w;scene.render.resolution_y=h;scene.camera.data.ortho_scale=6.4*w/h
        scene.render.filepath=str(OUT/('Beauty-'+device+'.png'))
        if device=='desktop':bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Composition-review.blend'))
        bpy.ops.render.render(write_still=True)
    # Same camera diagnostic: water hidden, actual heights/materials visible.
    water.hide_render=True;scene.render.engine='CYCLES';scene.cycles.samples=8
    scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.camera.data.ortho_scale=10.24
    scene.render.filepath=str(OUT/'Terrain-without-water.png');bpy.ops.render.render(write_still=True)
    print('ART-012 RENDERED',NAME,flush=True)

if __name__=='__main__':
    assert NAME in NAMES,NAME
    mode=sys.argv[sys.argv.index('--')+2] if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+2 else 'build'
    {'build':build,'export':export,'preview':preview,'draft':lambda:preview(True)}[mode]()

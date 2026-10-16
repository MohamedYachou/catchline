"""ART-012 Blender saved-source and actual FBX verification. -- GullKelpBank etc.
Does not launch Unity. Explicit X normalization follows retained ART-011 Unity evidence.
"""
import bpy,bmesh,hashlib,importlib.util,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from bpy_extras.object_utils import world_to_camera_view
from io_scene_fbx import parse_fbx
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('maps12',Path(__file__).with_name('build_locations12.py'))
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
NAME=M.NAME;OUT=M.OUT
M.B.PALETTE.update(M.H.PAL)
def near(a,b):
    assert len(a)==len(b) and all(abs(x-y)<3e-5 for x,y in zip(a,b)),(a,b)
def bounds(o):
    points=[o.matrix_world@v.co for v in o.data.vertices]
    return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
def props(e):
    return {p.props[0].decode():list(p.props[4:]) for c in e.elems if c.id==b'Properties70' for p in c.elems if p.id==b'P'}
bpy.ops.wm.open_mainfile(filepath=str(OUT/(NAME+'.blend')))
objects=list(bpy.context.scene.objects);names={o.name for o in objects}
assert len(objects)==len(bpy.data.collections['ENV_EXPORT_ONLY'].objects)
assert 'Catchline_'+NAME in names and {'Shoreline','Seabed','Details'}<=names
stats={};topology=[];materials={};verts=[];faces=[];segments=[];positions={}
for o in objects:
    near(o.location,(0,0,0));near(o.rotation_euler,(0,0,0));near(o.scale,(1,1,1))
    assert o.type in ('MESH','EMPTY')
    if o.type!='MESH':continue
    assert o.parent.name in ('Shoreline','Seabed','Details') and not o.modifiers
    assert all(math.isfinite(x) for v in o.data.vertices for x in v.co)
    assert all(p.area>1e-10 for p in o.data.polygons),o.name
    bm=bmesh.new();bm.from_mesh(o.data)
    boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges)
    assert boundary==0 and nonmanifold==0,(o.name,boundary,nonmanifold)
    components=0;unseen=set(bm.verts)
    while unseen:
        components+=1;todo=[unseen.pop()]
        while todo:
            v=todo.pop()
            for e in v.link_edges:
                n=e.other_vert(v)
                if n in unseen:unseen.remove(n);todo.append(n)
    if o.name=='Terrain_ConnectedShoalsAndSeabed':assert components==1
    topology.append(dict(part=o.name,boundary_edges=boundary,nonmanifold_edges=nonmanifold,closed_components=components));bm.free()
    for p in o.data.polygons:
        mat=o.data.materials[p.material_index];assert mat.name in M.B.PALETTE
        assert not any(n.type=='TEX_IMAGE' for n in mat.node_tree.nodes)
        materials[mat.name]=M.B.PALETTE[mat.name]
    positions[o.name]=[tuple(v.co) for v in o.data.vertices]
    stats[o.name]=dict(bounds=bounds(o),triangles=M.B.mesh_stats(o)['triangles'],parent=o.parent.name)
    off=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    faces.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
    o.data.calc_loop_triangles()
    for tri in o.data.loop_triangles:
        vs=[o.data.vertices[i].co for i in tri.vertices];hits=[]
        for a,b in zip(vs,vs[1:]+vs[:1]):
            if (a.z<0)!=(b.z<0):
                p=a.lerp(b,-a.z/(b.z-a.z));hits.append([p.x,-p.y])
        if len(hits)==2 and math.dist(*hits)>1e-6:segments.append(hits)
total=sum(x['triangles'] for x in stats.values());assert total<M.BUDGET
def check_channel(vertices,polygons):
    bvh=BVHTree.FromPolygons(vertices,polygons);samples=0
    for i in range(27):
        for j in range(19):
            s=-2.6+i*5.2/26;t=-1.8+j*3.5/18
            hit,normal,idx,dist=bvh.ray_cast(Vector(M.point(s,t,6)),Vector((0,0,-1)))
            assert hit is not None and hit.z<-.35,('Boat/cast obstruction',s,t,hit)
            samples+=1
    return samples
samples=check_channel(verts,faces)
fbx=ROOT/'Assets/Art/Models/Environment'/(NAME+'.fbx');raw,version=parse_fbx.parse(str(fbx))
settings=props(next(e for e in raw.elems if e.id==b'GlobalSettings'))
assert settings['UpAxis']==[1] and settings['FrontAxis']==[2] and settings['UnitScaleFactor']==[100.0]
content=next(e for e in raw.elems if e.id==b'Objects')
assert not any(e.id in (b'Texture',b'Video') for e in content.elems)
for e in content.elems:
    if e.id==b'Model':
        p=props(e);near(p.get('Lcl Rotation',[0,0,0]),[0,0,0]);near(p.get('Lcl Scaling',[1,1,1]),[1,1,1])
    assert not(e.id==b'NodeAttribute' and e.props[-1] in (b'Light',b'Camera'))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=False)
assert {o.name for o in bpy.context.scene.objects}==names
fbx_total=0;actual_verts=[];actual_faces=[]
for o in bpy.context.scene.objects:
    near(o.matrix_world.translation,(0,0,0))
    if o.type!='MESH':continue
    # Documented Unity compensation is undone ONLY in Blender inspection memory.
    for v in o.data.vertices:v.co.x=-v.co.x
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    near(bounds(o)[0],stats[o.name]['bounds'][0]);near(bounds(o)[1],stats[o.name]['bounds'][1])
    actual=[tuple(o.matrix_world@v.co) for v in o.data.vertices]
    for source,target in [(positions[o.name],actual),(actual,positions[o.name])]:
        kd=KDTree(len(target))
        for i,p in enumerate(target):kd.insert(p,i)
        kd.balance()
        assert all(kd.find(p)[2]<3e-5 for p in source),('Vertex positions differ',o.name,len(source),len(target),max(kd.find(p)[2] for p in source),[(p,kd.find(p)[0][:]) for p in source if kd.find(p)[2]>=3e-5][:4])
    off=len(actual_verts);actual_verts.extend(actual)
    actual_faces.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
    assert o.parent.name==stats[o.name]['parent']
    n=M.B.mesh_stats(o)['triangles'];assert n==stats[o.name]['triangles'],(o.name,n,stats[o.name]['triangles']);fbx_total+=n
assert fbx_total==total
actual_samples=check_channel(actual_verts,actual_faces)
evidence=ROOT/'Art/Models/HarbourMouth11'
protected=json.loads((evidence/'protected-hashes.json').read_text())
for path,sha in protected.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
pts=Path('C:/Users/momoy/Projects/Plunder_The_Seas')
plunder=json.loads((evidence/'plunder-readonly-hashes.json').read_text())
for path,sha in plunder.items():assert hashlib.sha256((pts/path).read_bytes()).hexdigest()==sha,path
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Composition-review.blend'))
scene=bpy.context.scene;cam=scene.camera;bpy.context.view_layer.update();near([cam.data.ortho_scale],[10.24])
near([scene.render.resolution_x,scene.render.resolution_y],[1440,900])
for s,t in [(-5.12,-3.2),(5.12,3.2),(-2.6,1.7),(2.6,-1.8)]:
    p=M.point(s,t,0);actual=world_to_camera_view(scene,cam,Vector((p[0],-p[1],M.WATER)))
    near(actual[:2],[.5+s/10.24,.5+t/6.4])
footprints={}
for device,w,h in [('desktop',1440,900),('phone',844,390)]:
    scene.render.resolution_x=w;scene.render.resolution_y=h;cam.data.ortho_scale=6.4*w/h
    bpy.context.view_layer.update()
    corners=[]
    for s,t in [(-3.2*w/h,-3.2),(3.2*w/h,-3.2),(3.2*w/h,3.2),(-3.2*w/h,3.2)]:
        p=M.point(s,t,0);corners.append([p[0],M.WATER,-p[1]])
        actual=world_to_camera_view(scene,cam,Vector((p[0],-p[1],M.WATER)))
        near(actual[:2],[.5+s/(6.4*w/h),.5+t/6.4])
    footprints[device]=dict(resolution=[w,h],water_plane_corners_unity=corners)
landmarks={}
for name,stat in stats.items():
    a,b=stat['bounds'];p=[(x+y)/2 for x,y in zip(a,b)]
    landmarks[name]=[p[0],p[2],-p[1]]
manifest=dict(asset='Assets/Art/Models/Environment/'+NAME+'.fbx',root='Catchline_'+NAME,
    roots=['Shoreline','Seabed','Details'],unity_waterline_local_y=0,world_position_unity=[0,-.32,0],
    rotation_euler_unity=[0,0,0],scale=[1,1,1],triangles=total,budget=M.BUDGET,
    materials_srgb=materials,new_palette_slots=[],camera_unity=dict(rotation_euler=[45,35,0],orthographic_size=3.2,target=[1.35,0,.20],distance=40),
    camera_footprints=footprints,channel_clear_screen_ground=dict(x=[-2.6,2.6],y=[-1.8,1.7]),
    waterline_segments_unity_xz=segments,expected_unity_mesh_bounds_centres_local=landmarks,
    source_axes='Canonical Blender X,-UnityZ,up. Unity-specific FBX (-x,z,-y) plus reversed winding. Blender inspection normalizes X.',
    runtime_water='None included. Windows owns shader/lighting/depth/foam. Terrain is opaque scene-depth support.',
    collision='Never add whole-root box collider across the clear channel. Seabed terrain includes exposed shores; choose collision per mesh only if needed.',
    unity_import_check='Not run for ART-012: Windows owns scratch. Export handedness follows measured ART-011 positive-X Unity check. Compare expected mesh bounds centres after import.')
serial=json.dumps(manifest,indent=2)+'\n';(OUT/'placement-manifest.json').write_text(serial)
(ROOT/'Assets/Art/Models/Environment'/(NAME+'-placement.json')).write_text(serial)
result=dict(all_passed=True,asset=NAME,blender=bpy.app.version_string,fbx_version=version,mesh_count=len(stats),triangles=total,budget=M.BUDGET,
    saved_source_and_actual_fbx=True,unity_x_compensation=True,blender_roundtrip_x_mirror_normalized=True,
    exact_camera_projection=True,boat_cast_channel_rays=samples,actual_fbx_channel_rays=actual_samples,actual_vertex_positions_match=True,
    protected_files_unchanged=len(protected),plunder_files_unchanged=len(plunder),terrain_connected_components=1,topology=topology,
    waterline_segment_count=len(segments),used_materials=materials,fbx_sha256=hashlib.sha256(fbx.read_bytes()).hexdigest(),
    native_unity_check='Deferred to Windows; no ART-012 scratch run or runtime visual acceptance claimed.')
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS ART-012',NAME,total,'triangles;',samples,'clearance rays; saved source + actual FBX + camera + closed connected terrain',flush=True)

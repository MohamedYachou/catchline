"""Blender5.2: ART-011 source/actual FBX, camera, clearance and provenance checks."""
import bpy,bmesh,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from io_scene_fbx import parse_fbx
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/HarbourMouth11'
spec=importlib.util.spec_from_file_location('art11',Path(__file__).with_name('build_harbour_mouth11.py'))
K=importlib.util.module_from_spec(spec);spec.loader.exec_module(K)
def near(a,b):assert len(a)==len(b) and all(abs(x-y)<2e-5 for x,y in zip(a,b)),(a,b)
def bounds(obs):
    points=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'GullHarbourMouth.blend'))
col=bpy.data.collections['ENV_EXPORT_ONLY'];objects=list(col.objects);meshes=[o for o in objects if o.type=='MESH']
root=bpy.data.objects['Catchline_GullHarbourMouth'];names={o.name for o in objects}
assert {'Shoreline','Seabed','Details'} <= names
assert all(o.type in ('MESH','EMPTY') for o in objects)
assert len(bpy.context.scene.objects)==len(objects),'Review objects leaked into model source'
topology=[];materials={};source_stats={};segments=[]
for o in objects:
    near(o.location,(0,0,0));near(o.rotation_euler,(0,0,0));near(o.scale,(1,1,1))
    if o.type!='MESH':continue
    assert not o.modifiers and o.parent.name in ('Shoreline','Seabed','Details')
    assert all(math.isfinite(x) for v in o.data.vertices for x in v.co)
    assert all(p.area>1e-10 for p in o.data.polygons),o.name
    for m in o.data.materials:
        assert m.name in K.PAL or m.name in K.B.PALETTE,m.name
        assert not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes)
    for polygon in o.data.polygons:
        name=o.data.materials[polygon.material_index].name
        materials[name]=K.PAL.get(name,K.B.PALETTE.get(name))
    bm=bmesh.new();bm.from_mesh(o.data)
    boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges)
    assert boundary==0,(o.name,boundary)
    topology.append(dict(part=o.name,boundary_edges=boundary,nonmanifold_edges=nonmanifold))
    bm.free();source_stats[o.name]=K.B.mesh_stats(o)
    o.data.calc_loop_triangles()
    if o.parent.name=='Shoreline':
        for tri in o.data.loop_triangles:
            vs=[o.data.vertices[i].co for i in tri.vertices];hits=[]
            for a,b in zip(vs,vs[1:]+vs[:1]):
                if (a.z<0)!=(b.z<0):
                    p=a.lerp(b,-a.z/(b.z-a.z));hits.append([p.x,-p.y])
            if len(hits)==2 and math.dist(*hits)>1e-6:segments.append(hits)
count=sum(a['triangles'] for a in source_stats.values());assert count<35000
source_bounds=bounds(meshes)
land=[o for o in meshes if o.parent.name in ('Shoreline','Details')];verts=[];faces=[]
for o in land:
    off=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    faces.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
bvh=BVHTree.FromPolygons(verts,faces)
sample_count=0
for i in range(27):
    for j in range(19):
        s=-2.6+i*5.2/26;t=-1.8+j*3.5/18;p=Vector(K.point(s,t,5))
        hit,normal,idx,dist=bvh.ray_cast(p,Vector((0,0,-1)))
        assert hit is None or hit.z<-.35,('Boat/action channel obstruction',s,t,hit)
        sample_count+=1
depths=[dict(screen_ground=[s,t],depth_m=-K.bed_depth(s,t)) for s,t in [(0,0),(-.46,-.19),(0,-1.5),(2,0),(3.4,.6),(-4.5,-.7)]]
fbx=ROOT/'Assets/Art/Models/Environment/GullHarbourMouth.fbx';raw,version=parse_fbx.parse(str(fbx))
objs=next(e for e in raw.elems if e.id==b'Objects')
def properties(element):
    return {p.props[0].decode():list(p.props[4:]) for container in element.elems if container.id==b'Properties70' for p in container.elems if p.id==b'P'}
settings=properties(next(e for e in raw.elems if e.id==b'GlobalSettings'))
assert settings['UpAxis']==[1] and settings['FrontAxis']==[2] and settings['UnitScaleFactor']==[100.0]
for model in [e for e in objs.elems if e.id==b'Model']:
    props=properties(model);near(props.get('Lcl Rotation',[0,0,0]),[0,0,0]);near(props.get('Lcl Scaling',[1,1,1]),[1,1,1])
assert not any(e.id in (b'Texture',b'Video') for e in objs.elems)
assert not any(e.id==b'NodeAttribute' and e.props[-1] in (b'Light',b'Camera') for e in objs.elems)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=False);bpy.context.view_layer.update()
imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert {o.name for o in bpy.context.scene.objects}==names
near(bounds(imported)[0],source_bounds[0]);near(bounds(imported)[1],source_bounds[1])
assert sum(K.B.mesh_stats(o)['triangles'] for o in imported)==count
for o in bpy.context.scene.objects:
    near(o.matrix_world.translation,(0,0,0))
    if o.type=='MESH':
        assert o.parent.name in ('Shoreline','Seabed','Details')
        near(bounds([o])[0],source_stats[o.name]['bounds_min_blender']);near(bounds([o])[1],source_stats[o.name]['bounds_max_blender'])
protected=json.loads((OUT/'protected-hashes.json').read_text())
for path,sha in protected.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
pts=Path('C:/Users/momoy/Projects/Plunder_The_Seas')
for path,sha in json.loads((OUT/'plunder-readonly-hashes.json').read_text()).items():assert hashlib.sha256((pts/path).read_bytes()).hexdigest()==sha,path
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Composition-review.blend'))
scene=bpy.context.scene;cam=scene.camera;bpy.context.view_layer.update();near([cam.data.ortho_scale],[10.24])
for s,t in [(-5.12,-3.2),(5.12,3.2),(-2.6,1.7),(2.6,-1.8)]:
    p=K.point(s,t,0);v=Vector((p[0],-p[1],K.WATER));actual=world_to_camera_view(scene,cam,v)
    near(actual[:2],[.5+s/10.24,.5+t/6.4])
footprints={}
for device,w,h in [('desktop',1440,900),('phone',844,390)]:
    half=3.2*w/h;corners=[]
    for s,t in [(-half,-3.2),(half,-3.2),(half,3.2),(-half,3.2)]:
        p=K.point(s,t,0);corners.append([p[0],K.WATER,-p[1]])
    footprints[device]=dict(resolution=[w,h],water_plane_corners_unity=corners,vertical_span_m=6.4,horizontal_span_m=half*2)
manifest=dict(asset='Assets/Art/Models/Environment/GullHarbourMouth.fbx',root='Catchline_GullHarbourMouth',
    roots=['Shoreline','Seabed','Details'],unity_waterline_local_y=0,world_position_unity=[0,K.WATER,0],
    rotation_euler_unity=[0,0,0],scale=[1,1,1],source_axes='Blender X right, -Y Unity forward, Z up',
    camera_unity=dict(rotation_euler=[45,35,0],orthographic_size=3.2,target=[1.35,0,.20],distance=40),
    camera_footprints=footprints,materials_srgb=materials,waterline_segments_unity_xz=segments,
    channel_clear_screen_ground=dict(x=[-2.6,2.6],y=[-1.8,1.7]),bathymetry_samples=depths,
    seabed_range_local_y=[-3.5,-.12],collision='Use static mesh collision on Shoreline only if needed; never a whole-root box collider across channel. Seabed is a depth-support mesh.',
    runtime_water='Not included. Set dynamic water to world Y=-.32, or translate the boat/camera frame consistently if changing datum.')
serialized=json.dumps(manifest,indent=2)+'\n'
(OUT/'placement-manifest.json').write_text(serialized)
(ROOT/'Assets/Art/Models/Environment/GullHarbourMouth-placement.json').write_text(serialized)
result=dict(all_passed=True,blender=bpy.app.version_string,fbx_version=version,triangles=count,mesh_count=len(meshes),
    root_count=4,source_and_actual_fbx_roundtrip=True,source_bounds_blender=source_bounds,
    closed_surface_topology=topology,boat_cast_channel_rays=sample_count,protected_files_unchanged=len(protected),
    plunder_inspected_files_unchanged=True,exact_camera_projection_passed=True,waterline_segment_count=len(segments),
    performance='Triangle counts do not establish visual acceptance or device frame rate.')
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS ART-011 source + actual FBX + framing + channel + protected assets and Plunder')

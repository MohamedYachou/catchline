"""Blender 5.2: actual source/FBX, protected-file and camera contract checks."""
import bpy, bmesh, json, math, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from io_scene_fbx import parse_fbx

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/FirstVoyage10'
spec=importlib.util.spec_from_file_location('gullcheck10',Path(__file__).with_name('validate_gull_harbour.py'))
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
old=json.loads((OUT/'baseline-contract.json').read_text())
metadata=json.loads((ROOT/'Art/Models/GullHarbour/build-metrics.json').read_text())
new=next(a for a in metadata['assets'] if a['asset']=='Rowboat')
assert old['pivots_blender']==new['pivots_blender']
assert {p['name'] for p in old['parts']}=={p['name'] for p in new['parts']}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/new['source']))
root=bpy.data.objects['Catchline_Rowboat'];V.near(root.location,(0,0,0));V.near(root.rotation_euler,(0,0,0));V.near(root.scale,(1,1,1))
objects=list(bpy.data.collections['ASSET_EXPORT'].objects);meshes=[o for o in objects if o.type=='MESH']
assert all(o.type in {'EMPTY','MESH'} for o in objects)
oldparts={p['name']:p for p in old['parts']}
topology=[]
for ob in meshes:
    assert ob.parent==root and not ob.modifiers
    V.near(ob.location,new['pivots_blender'][ob.name]);V.near(ob.rotation_euler,(0,0,0));V.near(ob.scale,(1,1,1))
    assert all(math.isfinite(x) for v in ob.data.vertices for x in v.co)
    assert all(p.area>1e-10 for p in ob.data.polygons),ob.name
    assert all(m.name in metadata['palette_srgb'] for m in ob.data.materials)
    assert not any(n.type=='TEX_IMAGE' for m in ob.data.materials for n in m.node_tree.nodes)
    if ob.name.startswith(('Oar','RodSocket')):
        assert V.kit.B.mesh_stats(ob)['mesh_sha256']==oldparts[ob.name]['mesh_sha256'],ob.name
    topology.append(dict(part=ob.name,**V.topology(ob)))
lo,hi=V.bounds([bpy.data.objects['Hull']]);V.near([hi[0]-lo[0],hi[1]-lo[1]],[2.4,4.2])
V.near(lo,oldparts['Hull']['bounds_min_blender']);V.near(hi,oldparts['Hull']['bounds_max_blender'])
lo,hi=V.bounds([bpy.data.objects['PlankDeck']]);V.near(lo,[-1,-1.5,-.05]);V.near(hi,[1,1.5,0])
# Added end panels do not create elevated obstruction inside any walking tile.
thwart=bpy.data.objects['CentreThwart']
for v in thwart.data.vertices:
    if abs(v.co.y)>.14001 and v.co.z>1e-5:
        raise AssertionError(('New elevated walking obstruction',tuple(v.co)))
count=sum(V.kit.B.mesh_stats(o)['triangles'] for o in meshes)
assert count==new['triangles'] and count<=4000,count
source_bounds=V.bounds(meshes)
fbx=ROOT/new['fbx'];raw,version=parse_fbx.parse(str(fbx))
global_settings=V.props(V.children(raw,b'GlobalSettings')[0])
assert global_settings['UpAxis']==[1] and global_settings['FrontAxis']==[2]
assert global_settings['UnitScaleFactor']==[100.0]
rawobjs=V.children(raw,b'Objects')[0]
assert not V.children(rawobjs,b'Texture') and not V.children(rawobjs,b'Video')
for model in V.children(rawobjs,b'Model'):
    name=model.props[1].decode().split('\x00')[0];transform=V.props(model)
    V.near(transform.get('Lcl Rotation',[0,0,0]),[0,0,0]);V.near(transform.get('Lcl Scaling',[1,1,1]),[1,1,1])
    p=new['pivots_blender'].get(name,[0,0,0])
    V.near(transform.get('Lcl Translation',[0,0,0]),[p[0],p[2],-p[1]])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=False)
imported=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.context.view_layer.update()
assert {o.name for o in imported}==set(new['pivots_blender'])
lo,hi=V.bounds(imported);V.near(lo,source_bounds[0]);V.near(hi,source_bounds[1])
assert sum(V.kit.B.mesh_stats(o)['triangles'] for o in imported)==count
for o in imported:V.near(o.matrix_world.translation,new['pivots_blender'][o.name])
protected=json.loads((OUT/'protected-hashes.json').read_text());changed=[]
for path,digest in protected.items():
    if path!=new['fbx']:
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
        changed.append(path)

# Check the reference image projection against Unity camera equations, not eyeballing.
cameras=[]
for label in ('before','after','refined'):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/(label+'-desktop.blend')))
    scene=bpy.context.scene;cam=scene.camera;bpy.context.view_layer.update()
    assert scene.render.resolution_x==1440 and scene.render.resolution_y==900
    V.near([cam.data.ortho_scale],[6.4*1440/900])
    assert cam.data.type=='ORTHO'
    yaw,pitch=math.radians(35),math.radians(45)
    right=Vector((math.cos(yaw),0,-math.sin(yaw)))
    up=Vector((math.sin(yaw)*math.sin(pitch),math.cos(pitch),math.cos(yaw)*math.sin(pitch)))
    target=Vector((1.35,0,.20) if label=='refined' else (1,0,-.7))
    for source in ((-1.115,-1,.44),(-1.115,1,.44),(0,0,0),(1,1.5,0)):
        p=bpy.data.objects['Catchline_Rowboat'].matrix_world@Vector(source)
        u=Vector((p.x,p.z,p.y));delta=u-target
        expected=(.5+delta.dot(right)/(6.4*1440/900),.5+delta.dot(up)/6.4)
        actual=world_to_camera_view(scene,cam,p);V.near(actual[:2],expected)
    for part,want in [('RodSocket_Port_Bow',(0,.44,-.615)),('RodSocket_Port_Stern',(2,.44,-.615))]:
        p=bpy.data.objects[part].matrix_world.translation;V.near((p.x,p.z,p.y),want)
    cameras.append(dict(stage=label,projection_matches_unity=True,camera_matrix=[list(row) for row in cam.matrix_world]))
V.near([x for r in cameras[0]['camera_matrix'] for x in r],[x for r in cameras[1]['camera_matrix'] for x in r])
result=dict(all_passed=True,blender=bpy.app.version_string,fbx_version=version,
    triangles_before=old['triangles'],triangles_after=count,part_count=len(imported),
    original_part_root_pivot_socket_contract_preserved=True,oars_and_socket_meshes_identical=True,
    hull_envelope_m=[4.2,2.4],deck_m=[3,2],palette=sorted({m for p in new['parts'] for m in p['materials']}),
    actual_fbx_reimport_passed=True,untouched_protected_files=len(changed),topology=topology,cameras=cameras)
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS ART-010: source, actual FBX, all contracts, protected files and exact Unity projection')

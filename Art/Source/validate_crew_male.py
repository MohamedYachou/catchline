"""Independent saved Blender and real FBX import contract/regression checks.
Run with Blender 5.2 headless. Writes only the named male folder validation.json.
"""
import argparse, sys
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--name',required=True)
NAME=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).name
OUT=ROOT/'Art/Models/CrewV2'/NAME
ORIGINAL = ROOT/'Art/Models/CrewRig/CrewRig.blend'
manifest = json.loads((OUT/'build-manifest.json').read_text())
result = {}


def channels(a):
    return list(a.layers[0].strips[0].channelbag(a.slots[0]).fcurves)


def digest(a):
    content = [(f.data_path, f.array_index,
                [(tuple(k.co), k.interpolation, tuple(k.handle_left), tuple(k.handle_right))
                 for k in f.keyframe_points]) for f in channels(a)]
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def skeleton(arm):
    return {b.name: {'parent': b.parent.name if b.parent else None,
                    'head': list(b.head_local), 'tail': list(b.tail_local),
                    'matrix': [list(row) for row in b.matrix_local],
                    'deform': b.use_deform} for b in arm.data.bones}


def sample(arm, action, frame):
    arm.data.pose_position = 'POSE'
    arm.animation_data.action = action
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    return {b.name: list(arm.matrix_world@b.head) for b in arm.pose.bones}


def bounds(meshes):
    deps = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in meshes:
        evaluated = ob.evaluated_get(deps)
        data = evaluated.to_mesh()
        pts += [evaluated.matrix_world@v.co for v in data.vertices]
        evaluated.to_mesh_clear()
    assert all(math.isfinite(x) for v in pts for x in v)
    return [[min(v[i] for v in pts) for i in range(3)],
            [max(v[i] for v in pts) for i in range(3)]]


bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL))
original_hash = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
assert original_hash == manifest['original_sha256']
original_arm = bpy.data.objects['CrewRig']
original_bones = skeleton(original_arm)
original_digests = {a.name: digest(a) for a in bpy.data.actions}
assert len(original_bones) == 20 and len(original_digests) == 11
trajectories = {}
for a in list(bpy.data.actions):
    lo, hi = (int(f) for f in a.frame_range)
    for f in sorted(set([lo, lo+(hi-lo)//4, (lo+hi)//2, hi])):
        trajectories[(a.name, f)] = sample(original_arm, a, f)

bpy.ops.wm.open_mainfile(filepath=str(OUT/(NAME+'.blend')))
arm = bpy.data.objects['CrewRig']
assert skeleton(arm) == original_bones, 'Saved rig differs from original'
assert {a.name: digest(a) for a in bpy.data.actions} == original_digests, 'Saved actions differ'
assert tuple(arm.location) == (0, 0, 0) and tuple(arm.scale) == (1, 1, 1)
assert bpy.context.scene.render.fps == 24
assert bpy.context.scene.unit_settings.scale_length == 1
meshes = [bpy.data.objects[n] for n in manifest['meshes']]
assert len(meshes) == 6
counts = {}
max_weights = 0
for ob in meshes:
    assert ob.parent == arm
    assert any(m.type == 'ARMATURE' and m.object == arm for m in ob.modifiers)
    ob.data.calc_loop_triangles()
    counts[ob.name] = len(ob.data.loop_triangles)
    for v in ob.data.vertices:
        assert v.groups and abs(sum(g.weight for g in v.groups)-1) < 1e-5, (ob.name, v.index)
        assert all(ob.vertex_groups[g.group].name in original_bones for g in v.groups)
        max_weights = max(max_weights, sum(g.weight > 1e-6 for g in v.groups))
assert counts == manifest['meshes']
assert sum(counts.values()) <= 20000 and max_weights <= 4
arm.data.pose_position = 'REST'
bpy.context.view_layer.update()
rest_bounds = bounds(meshes)
assert abs(rest_bounds[0][2]) < .001, rest_bounds
scalp = max(v.co.z for v in bpy.data.objects[NAME+'_Face'].data.vertices)
assert abs(scalp-.95) < .001, scalp
source_samples = {}
source_pose_bounds = {}
for (name, frame), original in trajectories.items():
    actual = sample(arm, bpy.data.actions[name], frame)
    error = max((Vector(actual[n])-Vector(original[n])).length for n in original)
    assert error < 1e-6, (name, frame, error)
    source_samples[(name, frame)] = actual
    source_pose_bounds[(name, frame)] = bounds(meshes)
textures = list(OUT.glob('*.png'))
textures = [p for p in textures if p.name.startswith(NAME+'_') and p.name != NAME+'-review.png']
sizes = {}
for path in textures:
    image = bpy.data.images.load(str(path), check_existing=True)
    sizes[path.name] = list(image.size)
assert sum(w*h for w, h in sizes.values()) <= 2048*2048
face = bpy.data.objects[NAME+'_Face']
assert face.data.uv_layers.active is not None
source_face_material = bpy.data.materials[NAME+'_Face']
source_image = next(n.image for n in source_face_material.node_tree.nodes
                    if n.type == 'TEX_IMAGE')
assert Path(bpy.path.abspath(source_image.filepath)).resolve() == (OUT/(NAME+'_Face.png')).resolve()
assert source_image.has_data and tuple(source_image.size) == (512, 512)
result['saved_source'] = {'rig_and_all_action_signatures_exact': True,
    'bones': 20, 'actions': 11, 'triangles': sum(counts.values()), 'mesh_triangles': counts,
    'max_weights_per_vertex': max_weights, 'all_weights_normalized': True,
    'bare_scalp_height_m': scalp, 'bind_bounds_m': rest_bounds,
    'texture_sizes': sizes, 'face_uv_and_relative_texture_resolve': True,
    'pose_samples_matching_original': len(trajectories)}

# New empty scene: verify the actual delivery FBX, not its intended settings.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT/(NAME+'.fbx')), use_anim=True)
arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
assert len(arms) == 1
arm = arms[0]
assert len(arm.data.bones) == 20
assert {b.name: b.parent.name if b.parent else None for b in arm.data.bones} == {
    n: v['parent'] for n, v in original_bones.items()}
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
assert {o.name for o in meshes} == set(manifest['meshes'])
fbx_counts = {}
for ob in meshes:
    assert any(m.type == 'ARMATURE' and m.object == arm for m in ob.modifiers)
    for v in ob.data.vertices:
        assert v.groups and abs(sum(g.weight for g in v.groups)-1) < 1e-4
    ob.data.calc_loop_triangles()
    fbx_counts[ob.name] = len(ob.data.loop_triangles)
assert fbx_counts == counts, (fbx_counts, counts)
assert bpy.data.objects[NAME+'_Face'].data.uv_layers.active is not None
fbx_face_material = bpy.data.materials[NAME+'_Face']
fbx_image = next(n.image for n in fbx_face_material.node_tree.nodes if n.type == 'TEX_IMAGE')
assert Path(bpy.path.abspath(fbx_image.filepath)).is_file(), fbx_image.filepath
assert hashlib.sha256(Path(bpy.path.abspath(fbx_image.filepath)).read_bytes()).hexdigest() == \
       hashlib.sha256((OUT/(NAME+'_Face.png')).read_bytes()).hexdigest()
assert abs((arm.matrix_world@arm.data.bones['Head'].head_local).z-.60) < 1e-4
arm.data.pose_position = 'REST'
bpy.context.view_layer.update()
fbx_rest_bounds = bounds(meshes)
assert max(abs(a-b) for aa, bb in zip(rest_bounds, fbx_rest_bounds)
           for a, b in zip(aa, bb)) < 1e-4
fbx_actions = {a.name.split('|')[-1]: a for a in bpy.data.actions}
assert set(fbx_actions) == set(original_digests)
checks = []
max_position_error = 0
max_bounds_error = 0
for name, contract in manifest['contract']['actions'].items():
    action = fbx_actions[name]
    assert list(action.frame_range) == contract['range']
    fcurves = channels(action)
    assert all(any(f.data_path.startswith('pose.bones["'+bone+'"]') for f in fcurves)
               for bone in original_bones)
    assert all(len(f.keyframe_points) == int(action.frame_range[1]) for f in fcurves)
    checks.append({'action': name, 'frames': list(action.frame_range),
                   'channels': len(fcurves)})
for (name, frame), expected in source_samples.items():
    actual = sample(arm, fbx_actions[name], frame)
    error = max((Vector(actual[n])-Vector(expected[n])).length for n in expected)
    max_position_error = max(max_position_error, error)
    assert error < 2e-4, (name, frame, error)
    actual_bounds = bounds(meshes)
    expected_bounds = source_pose_bounds[(name, frame)]
    error = max(abs(a-b) for aa, bb in zip(actual_bounds, expected_bounds) for a, b in zip(aa, bb))
    max_bounds_error = max(max_bounds_error, error)
    assert error < 4e-4, (name, frame, error)
result['actual_fbx_roundtrip'] = {'bones_and_hierarchy': True, 'metre_scale': True,
    'source_bind_bounds_match': True, 'normalized_weights': True,
    'mesh_triangles': fbx_counts, 'face_uv_and_texture_resolve': True,
    'all_original_actions': checks, 'sampled_poses': len(source_samples),
    'max_bone_position_error_m': max_position_error, 'max_mesh_bounds_error_m': max_bounds_error}
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == original_hash
result['original_crewrig_sha256'] = original_hash
result['all_passed'] = True
result['name'] = NAME
result['revision'] = manifest['revision']
result['delivery_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
    [OUT/(NAME+'.blend'),OUT/(NAME+'.fbx'),OUT/(NAME+'_Face.png')]}
(OUT/'validation.json').write_text(json.dumps(result, indent=2)+'\n')
print('PASS male saved source + real FBX: 20 original bones, 11 unchanged actions,',
      sum(counts.values()), 'triangles; source and imported pose/bounds samples agree', flush=True)

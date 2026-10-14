"""Validate saved Blender sources and exported FBXs without opening Unity."""
from pathlib import Path
import bpy
import importlib.util
import json
import sys
from mathutils import Vector
from io_scene_fbx import parse_fbx

REPO = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('catchline_builder', Path(__file__).with_name('build_crab_coast_props.py'))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def children(element, name):
    return [child for child in element.elems if child.id == name]


def property_map(element):
    result = {}
    for container in children(element, b'Properties70'):
        for prop in children(container, b'P'):
            result[prop.props[0].decode()] = list(prop.props[4:])
    return result


def bounds(objects):
    coords = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
    low = [min(v[i] for v in coords) for i in range(3)]
    high = [max(v[i] for v in coords) for i in range(3)]
    return low, high


def near(actual, expected, tolerance=1e-5):
    assert len(actual) == len(expected)
    assert all(abs(a - b) <= tolerance for a, b in zip(actual, expected)), (actual, expected)


def validate():
    metrics_path = REPO / 'Art/Models/Props/build-metrics.json'
    metrics = json.loads(metrics_path.read_text())
    records = []
    source_hashes = {}
    for prop in metrics['props']:
        name = prop['prop']
        bpy.ops.wm.open_mainfile(filepath=str(REPO / prop['source']))
        collection = bpy.data.collections['ASSET_EXPORT']
        objects = list(collection.objects)
        meshes = [obj for obj in objects if obj.type == 'MESH']
        stats = [builder.mesh_stats(obj) for obj in meshes]
        assert sum(part['triangles'] for part in stats) == prop['triangles'] <= prop['budget']
        for obj in objects:
            near(obj.location, (0, 0, 0))
            near(obj.rotation_euler, (0, 0, 0))
            near(obj.scale, (1, 1, 1))
            assert not obj.modifiers
        for obj in meshes:
            for mat in obj.data.materials:
                assert mat.name in builder.PALETTE
                assert not any(n.type == 'TEX_IMAGE' for n in mat.node_tree.nodes)
        source_low, source_high = bounds(meshes)
        near(source_low, prop['bounds_min_blender'])
        near(source_high, prop['bounds_max_blender'])
        near([source_low[0] + source_high[0], source_low[1] + source_high[1], source_low[2]], (0, 0, 0))
        near([source_high[i] - source_low[i] for i in range(3)], prop['dimensions_width_depth_height_m'])
        for part in stats:
            source_hashes[(name, part['name'])] = part['mesh_sha256']
        root = bpy.data.objects['Catchline_' + name]
        near(root.matrix_world.translation, (0, 0, 0))
        if name == 'BandedCrab':
            assert bpy.data.objects['ClawBands'].parent == root
        if name == 'FullPot':
            assert bpy.data.objects['CrabLoad'].parent == root
            load = next(p for p in stats if p['name'] == 'CrabLoad')
            for i in range(3):
                assert load['bounds_min_blender'][i] >= source_low[i]
                assert load['bounds_max_blender'][i] <= source_high[i]
        fbx_path = REPO / prop['fbx']
        raw, version = parse_fbx.parse(str(fbx_path))
        raw_objects = children(raw, b'Objects')[0]
        raw_models = children(raw_objects, b'Model')
        raw_attributes = children(raw_objects, b'NodeAttribute')
        assert not any(el.props[-1] in (b'Camera', b'Light') for el in raw_attributes)
        assert not children(raw_objects, b'Texture') and not children(raw_objects, b'Video')
        globals_map = property_map(children(raw, b'GlobalSettings')[0])
        raw_coordinates = []
        for geometry in children(raw_objects, b'Geometry'):
            if geometry.props[-1] == b'Mesh':
                xyz = children(geometry, b'Vertices')[0].props[0]
                raw_coordinates.extend(tuple(xyz[i:i + 3]) for i in range(0, len(xyz), 3))
        raw_low = [min(v[i] for v in raw_coordinates) for i in range(3)]
        raw_high = [max(v[i] for v in raw_coordinates) for i in range(3)]
        raw_transforms = {el.props[1].decode(errors='replace').split('\x00')[0]: {
            key: value for key, value in property_map(el).items()
            if key in ('Lcl Translation', 'Lcl Rotation', 'Lcl Scaling')
        } for el in raw_models}
        print('FBX_RAW', name, globals_map, raw_low, raw_high, raw_transforms, flush=True)
        # Verify Y-up mesh data directly: X,Z,-Y is the selected export basis.
        near(raw_low, [source_low[0], source_low[2], -source_high[1]])
        near(raw_high, [source_high[0], source_high[2], -source_low[1]])
        for transform in raw_transforms.values():
            near(transform.get('Lcl Scaling', [1, 1, 1]), (1, 1, 1))
            near(transform.get('Lcl Rotation', [0, 0, 0]), (0, 0, 0))
            near(transform.get('Lcl Translation', [0, 0, 0]), (0, 0, 0))
        # Import into an empty Blender scene and compare physical size and hierarchy.
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.scale_length = 1
        bpy.ops.import_scene.fbx(filepath=str(fbx_path), use_anim=False)
        imported_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        assert len(imported_meshes) == len(meshes)
        bpy.context.view_layer.update()
        imported_low, imported_high = bounds(imported_meshes)
        near(imported_low, source_low)
        near(imported_high, source_high)
        imported_triangles = 0
        for obj in imported_meshes:
            obj.data.calc_loop_triangles()
            imported_triangles += len(obj.data.loop_triangles)
        assert imported_triangles == prop['triangles']
        if name == 'BandedCrab':
            assert bpy.data.objects['ClawBands'].parent.name == 'Catchline_BandedCrab'
        if name == 'FullPot':
            assert bpy.data.objects['CrabLoad'].parent.name == 'Catchline_FullPot'
        records.append({'prop': name, 'passed': True, 'fbx_version': version,
                        'unit_scale_factor': globals_map.get('UnitScaleFactor'),
                        'raw_mesh_bounds_y_up': [raw_low, raw_high],
                        'raw_node_transforms': raw_transforms,
                        'roundtrip_triangles': imported_triangles,
                        'roundtrip_dimensions_width_depth_height_m':
                            [round(imported_high[i] - imported_low[i], 8) for i in range(3)]})
        print('VALIDATED', name, imported_triangles, flush=True)
    assert source_hashes[('Crab', 'CrabBody')] == source_hashes[('BandedCrab', 'CrabBody')]
    assert source_hashes[('EmptyPot', 'PotBody')] == source_hashes[('FullPot', 'PotBody')]
    output = {'blender_version': bpy.app.version_string, 'checks': records,
              'shared_crab_body_identical': True, 'shared_pot_body_identical': True,
              'unity_editor_opened': False,
              'limitation': 'Validated source geometry, raw FBX basis and Blender FBX roundtrip; Unity importer/runtime not executed.'}
    (REPO / 'Art/Models/Props/validation.json').write_text(json.dumps(output, indent=2) + '\n')
    print('ALL_SIX_PROPS_VALIDATED', flush=True)


if __name__ == '__main__':
    validate()

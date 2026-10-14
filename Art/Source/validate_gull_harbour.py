"""Inspect all Gull Harbour .blend files, binary FBXs and animation pivots."""
from pathlib import Path
import bpy
import bmesh
import importlib.util
import json
import sys
from mathutils import Vector
from io_scene_fbx import parse_fbx

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Art/Models/GullHarbour'
spec = importlib.util.spec_from_file_location('gull_builder', Path(__file__).with_name('build_gull_harbour.py'))
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


def near(a, b, tolerance=1e-5):
    assert len(a) == len(b) and all(abs(x - y) <= tolerance for x, y in zip(a, b)), (a, b)


def bounds(objects):
    points = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
    return ([min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)])


def children(element, name):
    return [e for e in element.elems if e.id == name]


def props(element):
    result = {}
    for container in children(element, b'Properties70'):
        for p in children(container, b'P'):
            result[p.props[0].decode()] = list(p.props[4:])
    return result


def topology(obj):
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    remaining = set(mesh.verts)
    components = 0
    while remaining:
        todo = [remaining.pop()]
        components += 1
        while todo:
            v = todo.pop()
            for edge in v.link_edges:
                other = edge.other_vert(v)
                if other in remaining:
                    remaining.remove(other)
                    todo.append(other)
    result = {'faces': len(mesh.faces), 'nonquads': sum(len(f.verts) != 4 for f in mesh.faces),
              'nonmanifold_edges': sum(not e.is_manifold for e in mesh.edges),
              'nonmanifold_vertices': sum(not v.is_manifold for v in mesh.verts),
              'components': components, 'inconsistent_edges': sum(not e.is_contiguous for e in mesh.edges)}
    mesh.free()
    return result


def main():
    metadata = json.loads((OUT / 'build-metrics.json').read_text())
    additions_spec = importlib.util.spec_from_file_location('task04', Path(__file__).with_name('build_task04.py'))
    additions = importlib.util.module_from_spec(additions_spec); additions_spec.loader.exec_module(additions)
    additions.register()
    kit.ASSETS.update(additions.B_ASSETS); kit.ASSETS.update(additions.C_ASSETS)
    kit.FISH.update(additions.K.FISH)
    expected = set(kit.ASSETS)
    assert {a['asset'] for a in metadata['assets']} == expected, 'Missing requested asset'
    baseline = json.loads((ROOT / 'Art/Source/task04-baseline.json').read_text())
    for original in baseline['assets']:
        current = next(a for a in metadata['assets'] if a['asset']==original['asset'])
        assert current['pivots_blender'] == original['pivots_blender'], ('Changed existing names/pivots',original['asset'])
    results = []
    source_hashes = {}
    for asset in metadata['assets']:
        name = asset['asset']
        bpy.ops.wm.open_mainfile(filepath=str(ROOT / asset['source']))
        collection = bpy.data.collections['ASSET_EXPORT']
        objects = list(collection.objects)
        meshes = [o for o in objects if o.type == 'MESH']
        root = bpy.data.objects['Catchline_' + name]
        near(root.location, (0, 0, 0))
        assert not any(o.type == 'ARMATURE' for o in objects)
        source_low, source_high = bounds(meshes)
        near(source_low, asset['bounds_min_blender'])
        near(source_high, asset['bounds_max_blender'])
        for obj in meshes:
            assert obj.parent == root
            near(obj.location, asset['pivots_blender'][obj.name])
            near(obj.rotation_euler, (0, 0, 0))
            near(obj.scale, (1, 1, 1))
            assert not obj.modifiers
            for material in obj.data.materials:
                assert material.name in kit.B.PALETTE
                assert not any(n.type == 'TEX_IMAGE' for n in material.node_tree.nodes)
            source_hashes[(name, obj.name)] = kit.B.mesh_stats(obj)['mesh_sha256']
        count = sum(kit.B.mesh_stats(o)['triangles'] for o in meshes)
        assert count == asset['triangles']
        special = {}
        if name.startswith('BreakwaterRock'):
            assert 150 <= count <= 300
            near([source_low[2]], [0])
            sole = [v for o in meshes for v in o.data.vertices if abs(v.co.z) < 1e-6]
            assert len(sole) >= 12
            special['flat_sole_vertices'] = len(sole)
        if name == 'FishingRod':
            near([source_high[2]], [1.6])
            rod = bpy.data.objects['RodAndReel']
            butt = [v.co for v in rod.data.vertices if v.co.z < .025]
            width = max(v.x for v in butt) - min(v.x for v in butt)
            assert width >= .03
            special['butt_width_m'] = width
            near(bpy.data.objects['ReelHandle'].location, [.107, 0, .24])
        if name == 'CaptainCap':
            assert 'AnchorBadge' in bpy.data.objects
            cap = bpy.data.objects['CaptainCap']
            visor = [v.co for v in cap.data.vertices if v.co.y < -.17 and v.co.z < .02]
            assert len(visor) > 10
            assert max(v.z for v in visor) - min(v.z for v in visor) > .01
            special['curved_visor_vertices'] = len(visor)
        if name == 'KelpPatch':
            near([source_low[2], source_high[2]], [0, 0])
            assert any('bulbs' in note for note in asset['notes'])
            special['flat_mat_max_height_m'] = source_high[2]
        if name in additions.B_ASSETS and not name.startswith('ShopFront_') and name!='SandBank':
            near([source_low[2]],[0])
        if name.startswith('ShopFront_'):
            near([source_low[2]],[0])
            # No geometry in the central 0.7m door approach.
            points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
            assert not any(abs(v.x)<.35 and v.y>.05 and v.z<.9 for v in points)
        if name == 'Skiff':
            lo,hi=bounds([next(o for o in meshes if o.name=='PlankDeck')])
            near(lo,[-1.5,-2.5,-.05]); near(hi,[1.5,2.5,0])
            lo,hi=bounds([next(o for o in meshes if o.name=='Hull')])
            near([hi[0]-lo[0],hi[1]-lo[1]],[3.5,6.5])
            required={'Propeller','HoldLid','RodSocket_1','RodSocket_2','RodSocket_3','FishHold','Console'}
            assert required<={o.name for o in meshes}
            near(kit.bpy.data.objects['HoldLid'].location,[0,-.5,.025])
            for i,y in enumerate((1.75,0,-1.75),1):near(kit.bpy.data.objects['RodSocket_'+str(i)].location,[-1.68,y,.45])
            lo,hi=bounds([kit.bpy.data.objects['Console']])
            assert .5<=lo[0]<hi[0]<=1.5 and 1.5<=lo[1]<hi[1]<=2.5
            deck=kit.bpy.data.objects['PlankDeck']
            # No deck face closes the opening below the animated hold lid.
            for polygon in deck.data.polygons:
                if polygon.normal.z>.5:
                    centre=deck.matrix_world@polygon.center
                    assert not (-.399<centre.x<.399 and -1.499<centre.y<-.501)
            lid=kit.bpy.data.objects['HoldLid'];before=lid.matrix_world.copy()
            lid.rotation_euler.x=-1.745329252;kit.bpy.context.view_layer.update()
            lo,hi=bounds([lid]);assert hi[2]>.9
            lid.matrix_world=before;kit.bpy.context.view_layer.update()
            special['hold_lid_open_pose_checked']=True
        if name in ('HandWinch','SortTable'):
            footprint=(1,1) if name=='HandWinch' else (2,1)
            assert all(source_low[i]>=-footprint[i]/2-1e-5 and source_high[i]<=footprint[i]/2+1e-5 for i in (0,1))
            near([source_low[2]],[0])
            if name=='HandWinch':assert 'Crank' in kit.bpy.data.objects
        if name in ('GillNetFloatLine','GillNetSection'):
            near([source_low[0],source_high[0]],[-1,1])
        if name == 'SandBank':
            near(source_low, [-2,-1,0]); near(source_high, [2,1,0])
        if name == 'CliffSegment8m':
            near([source_low[0],source_high[0]],[-4,4])
            vertices=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
            left=sorted((round(v.y,5),round(v.z,5)) for v in vertices if abs(v.x+4)<1e-5)
            right=sorted((round(v.y,5),round(v.z,5)) for v in vertices if abs(v.x-4)<1e-5)
            assert left==right
        if name in ('Plaice','Seagull','DistantShip'):
            near([source_high[1]-source_low[1]],[{'Plaice':.36,'Seagull':.4,'DistantShip':8}[name]])
            if name=='Seagull': assert {'Wing_L','Wing_R'} <= {o.name for o in meshes}
            if name=='Plaice':
                assert source_high[2]-source_low[2]<.08
                assert 'PlaiceTail' in kit.bpy.data.objects
        if name == 'CrewBody':
            body = bpy.data.objects['CrewBody']
            special['body_topology'] = topology(body)
            topo = special['body_topology']
            assert topo['components'] == 1 and topo['nonquads'] == 0
            assert topo['nonmanifold_edges'] == 0 and topo['nonmanifold_vertices'] == 0 and topo['inconsistent_edges'] == 0
            assert topo['faces'] < 6000
            near([source_low[2], source_high[2]], [0, .95])
            # Extended hands sit at the same shoulder height, separated from the hips.
            hands = [v.co for v in body.data.vertices if abs(v.co.x) > .44]
            assert hands and min(v.z for v in hands) > .48 and max(v.z for v in hands) < .65
        if name == 'Rowboat':
            deck = next(o for o in meshes if o.name == 'PlankDeck')
            lo, hi = bounds([deck])
            near([hi[0] - lo[0], hi[1] - lo[1], hi[2]], [2, 3, 0])
            near(bpy.data.objects['Oar_Port'].location, [-1.12, 0, .49])
            near(bpy.data.objects['Oar_Starboard'].location, [1.12, 0, .49])
            for part_name, distance in (('RodSocket_Port_Stern', .5), ('RodSocket_Port_Bow', 2.5)):
                obj = bpy.data.objects[part_name]
                near([obj.location.x, 1.5 - obj.location.y], [-1.115, distance])
        if name in ('Cooler', 'IceBox'):
            near(bpy.data.objects['HingedLid'].location, [0, .25, .40])
        if name in kit.FISH:
            near([source_high[1] - source_low[1]], [kit.FISH[name][0]])
            assert name + 'Tail' in bpy.data.objects
        fbx_path = ROOT / asset['fbx']
        raw, version = parse_fbx.parse(str(fbx_path))
        raw_objects = children(raw, b'Objects')[0]
        global_settings = props(children(raw, b'GlobalSettings')[0])
        assert global_settings['UpAxis'] == [1] and global_settings['FrontAxis'] == [2]
        assert global_settings['UnitScaleFactor'] == [100.0]
        assert not children(raw_objects, b'Texture') and not children(raw_objects, b'Video')
        # Empty roots may carry a Null display attribute; cameras/lights must not.
        assert all(attribute.props[-1] not in (b'Camera', b'Light')
                   for attribute in children(raw_objects, b'NodeAttribute'))
        model_names = {}
        for model in children(raw_objects, b'Model'):
            model_name = model.props[1].decode().split('\x00')[0]
            transform = props(model)
            near(transform.get('Lcl Rotation', [0, 0, 0]), [0, 0, 0])
            near(transform.get('Lcl Scaling', [1, 1, 1]), [1, 1, 1])
            origin = asset['pivots_blender'].get(model_name, [0, 0, 0])
            near(transform.get('Lcl Translation', [0, 0, 0]), [origin[0], origin[2], -origin[1]])
            model_names[model.props[0]] = model_name
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.scale_length = 1
        bpy.ops.import_scene.fbx(filepath=str(fbx_path), use_anim=False)
        imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        bpy.context.view_layer.update()
        lo, hi = bounds(imported)
        near(lo, source_low)
        near(hi, source_high)
        imported_count = 0
        for obj in imported:
            obj.data.calc_loop_triangles()
            imported_count += len(obj.data.loop_triangles)
            near(obj.matrix_world.translation, asset['pivots_blender'][obj.name])
        assert imported_count == count, (name, count, imported_count)
        if name == 'CrewBody':
            assert all(len(p.vertices) == 4 for p in bpy.data.objects['CrewBody'].data.polygons)
        result = {'asset': name, 'passed': True, 'triangles': count, 'fbx_version': version,
                  'dimensions_width_depth_height_m': asset['dimensions_width_depth_height_m'],
                  'pivots_survive_fbx_roundtrip': True, **special}
        results.append(result)
        print('VALIDATED_GULL', name, count, flush=True)
    assert source_hashes[('Cooler', 'CoolerBody')] == source_hashes[('IceBox', 'CoolerBody')]
    output = {'blender_version': bpy.app.version_string, 'asset_count': len(results), 'checks': results,
              'cooler_base_mesh_shared': True, 'unity_opened': False, 'mixamo_uploaded': False,
              'scope': 'Source topology, dimensions, pivots, palette, raw FBX node axes/transforms and Blender FBX roundtrip. Unity/Mixamo not run.'}
    (OUT / 'validation.json').write_text(json.dumps(output, indent=2) + '\n')
    print('ALL_GULL_ASSETS_VALIDATED', len(results), flush=True)


if __name__ == '__main__':
    main()

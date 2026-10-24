"""Read-only A1 continuation audit; run with Blender --background --python.

Writes only Art/Models/Maps/continuation-audit.json. Geometry is never saved.
The ART108 FBX convention compensates source X on independent Blender import.
Centreline checks are art evidence, not a finite-hull navigation acceptance.
"""
import bpy
import bmesh
import hashlib
import json
import math
import struct
from datetime import datetime, timezone
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[3]
MAPS = ROOT / 'Art/Models/Maps'
NAMES = ['GullHarbourMouth', 'GullKelpBank', 'GullSandbar',
         'GullRockyPoint', 'GullDeepChannel']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def positions():
    return {o.name: [o.matrix_world @ v.co for v in o.data.vertices]
            for o in bpy.context.scene.objects if o.type == 'MESH'}


def bounds(points):
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]]


def triangles():
    result = {}
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles()
            result[o.name] = len(o.data.loop_triangles)
    return result


def tree(points):
    kd = KDTree(len(points))
    for i, point in enumerate(points):
        kd.insert(point, i)
    kd.balance()
    return kd


def max_nearest(points, kd):
    return max((kd.find(p)[2] for p in points), default=0)


def png_record(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    size = struct.unpack('>II', data[16:24])
    assert size[0] >= 900 and size[1] >= 500, (path, size)
    return dict(file=str(path.relative_to(ROOT)), size=list(size), sha256=sha(path))


def audit(name):
    folder = MAPS / name
    source = folder / f'{name}.blend'
    fbx = folder / f'{name}.fbx'
    grounds = load(folder / 'grounds.json')
    presets = load(folder / 'lighting-presets.json')
    old = load(folder / 'validation.json')
    runtime = ROOT / grounds['runtimeFile']
    protected = [source, fbx, folder / 'grounds.json', folder / 'lighting-presets.json',
                 folder / 'validation.json', runtime,
                 runtime.parent / 'grounds.json', runtime.parent / 'lighting-presets.json']
    protected += sorted(runtime.parent.glob('*.meta'))
    protected += [runtime.parent.with_suffix('.meta')]
    # Derived GroundsV1 keys have not yet been imported by Unity. Preserve the
    # original flat Environment model/placement/GUID files without inventing
    # metadata for the new integration keys.
    protected += sorted(p for p in runtime.parent.parent.glob(name + '*') if p.is_file())
    protected = [p for p in protected if p.exists()]
    before = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    assert sha(fbx) == sha(runtime) == old['fbxSha256'], (name, 'FBX delivery differs')
    for filename in ('grounds.json', 'lighting-presets.json'):
        assert sha(folder / filename) == sha(runtime.parent / filename)
    original_meta = runtime.parent.parent / (name + '.fbx.meta')
    assert original_meta.exists(), 'missing original model GUID'
    assert grounds['map'] == name and grounds['runtimeModelId'] == name + 'GroundsV1'
    assert grounds['units'] == 'metres'
    assert grounds['waterlineLocal'] == 0
    assert grounds['worldPosition'] == [0, -.32, 0]
    assert grounds['rotation'] == [0, 0, 0] and grounds['scale'] == [1, 1, 1]
    assert set(presets) >= {'day', 'night'}
    assert presets['day']['keyIntensity'] > presets['night']['keyIntensity'] > 0
    assert presets['night']['keyColor'] == '#FFC875'
    assert presets['night']['ambient'] == '#445C8F'
    pools = presets['night']['deckPools']
    assert len(pools) >= 2 and all(p['range'] > 0 and p['intensity'] > 0 for p in pools)
    assert len(grounds['grounds']) == 3 and len(grounds['paths']) == 3
    anchors = {g['id']: g for g in grounds['grounds']}
    assert len(anchors) == 3
    for g in anchors.values():
        assert len(g['position']) == 3 and g['position'][1] == 0
        assert math.isfinite(g['heading']) and g['seabedDepth'] > 0
        assert g['poolId'] == name + '/' + g['id']
    images = [png_record(folder / f'{g}-{period}.png')
              for g in anchors for period in ('day', 'night')]
    images += [png_record(folder / 'three-grounds-top.png'),
               png_record(folder / 'review-sheet.png')]

    bpy.ops.wm.open_mainfile(filepath=str(source))
    root = bpy.data.objects['Catchline_' + name + 'GroundsV1']
    identity_error = max(abs(root.matrix_world[i][j] - Matrix.Identity(4)[i][j])
                         for i in range(4) for j in range(4))
    assert identity_error < 1e-7
    assert root['waterline_local_y'] == 0 and root['world_y'] == -.32
    assert bpy.context.scene.unit_settings.system == 'METRIC'
    assert bpy.context.scene.unit_settings.scale_length == 1
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert all(o.parent == root for o in meshes)
    assert all(o.type in ('MESH', 'EMPTY') for o in bpy.context.scene.objects)
    src = positions()
    src_tris = triangles()
    assert sum(src_tris.values()) == old['triangles']
    bb = bounds([p for points in src.values() for p in points])
    assert max(abs(bb[a][i] - old['expandedBounds'][a][i])
               for a in (0, 1) for i in range(3)) < .0001
    bm = bmesh.new()
    bm.from_mesh(bpy.data.objects['ExpandedConnectedSeabed'].data)
    bad_edges = sum(not e.is_manifold for e in bm.edges)
    bm.free()
    assert bad_edges == 0, (name, 'extension is not closed')
    verts, faces = [], []
    for o in meshes:
        offset = len(verts)
        verts.extend(o.matrix_world @ v.co for v in o.data.vertices)
        faces.extend(tuple(offset + i for i in f.vertices) for f in o.data.polygons)
    bvh = BVHTree.FromPolygons(verts, faces)

    def surface(position):
        return bvh.ray_cast(Vector((position[0], -position[2], 6)),
                            Vector((0, 0, -1)))[0]

    anchor_results = []
    for g in anchors.values():
        hit = surface(g['position'])
        assert hit is not None and hit.z < -.35, (name, g['id'], 'blocked anchor')
        error = abs(-hit.z - g['physicalAnchorDepth'])
        assert error < .0001
        anchor_results.append(dict(id=g['id'], position=g['position'], heading=g['heading'],
                                   nominal_water_colour_depth_m=g['seabedDepth'],
                                   measured_terrain_depth_m=-hit.z, depth_error_m=error))
    path_results, pairs = [], set()
    for path in grounds['paths']:
        pair = frozenset((path['fromGround'], path['toGround']))
        assert len(pair) == 2 and pair <= set(anchors) and pair not in pairs
        pairs.add(pair)
        points = path['polyline']
        assert points[0] == anchors[path['fromGround']]['position']
        assert points[-1] == anchors[path['toGround']]['position']
        checked = 0
        for a, b in zip(points, points[1:]):
            n = max(1, math.ceil(math.dist(a, b) / .5))
            for j in range(n + 1):
                p = [a[i] + (b[i] - a[i]) * j / n for i in range(3)]
                hit = surface(p)
                assert hit is not None and hit.z < -.35, (name, 'blocked/off-map path', p)
                checked += 1
        assert checked == path['centrelineSamples'] and path['centrelineClear']
        path_results.append(dict(fromGround=path['fromGround'], toGround=path['toGround'],
                                 centreline_samples=checked, clear=True))

    # Reopen the immutable original: recompute its bounds and verify that every
    # visible coastal vertex above the intentionally lowered deep skirt survives.
    baseline = Path(old['baselineSource'])
    assert sha(baseline) == old['baselineSha256']
    bpy.ops.wm.open_mainfile(filepath=str(baseline))
    base = positions()
    base_bounds = bounds([p for points in base.values() for p in points])
    assert max(abs(base_bounds[a][i] - old['baselineBounds'][a][i])
               for a in (0, 1) for i in range(3)) < .0001
    base_area = math.prod(base_bounds[1][i] - base_bounds[0][i] for i in (0, 1))
    area = math.prod(bb[1][i] - bb[0][i] for i in (0, 1))
    assert area / base_area >= 3
    coast_error, coast_count = 0, 0
    for part, points in base.items():
        visible = [p for p in points if p.z >= -2.3]
        if visible:
            assert part in src, (name, 'missing original coastal mesh', part)
            coast_error = max(coast_error, max_nearest(visible, tree(src[part])))
            coast_count += len(visible)
    assert coast_error < .0001, (name, 'changed original visible coastline', coast_error)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    imported = positions()
    assert set(imported) == set(src)
    assert triangles() == src_tris
    max_error = 0
    for part, points in imported.items():
        corrected = [Vector((-p.x, p.y, p.z)) for p in points]
        max_error = max(max_error, max_nearest(src[part], tree(corrected)),
                        max_nearest(corrected, tree(src[part])))
    assert max_error < .0001, (name, 'actual FBX differs', max_error)
    after = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    assert before == after, 'audit changed protected files'
    row = dict(map=name, all_passed=True, triangles=sum(src_tris.values()),
               meshes=len(src), expanded_bounds=bb, original_bounds=base_bounds,
               footprint_ratio=area / base_area, closed_extension_nonmanifold_edges=bad_edges,
               retained_coastal_vertices_checked=coast_count, retained_coast_error_m=coast_error,
               root_identity_error=identity_error, anchors=anchor_results, paths=path_results,
               bidirectional_fbx_max_vertex_error_m=max_error,
               derived_fbx_has_unity_meta=runtime.with_suffix('.fbx.meta').exists(),
               original_baseline_sha256=sha(baseline), protected_sha256=before,
               lighting_presets=presets, renders=images)
    print('A1 CONTINUATION PASS', name, 'tris', row['triangles'],
          'footprint', row['footprint_ratio'], 'FBX error', max_error, flush=True)
    return row


result = dict(audit='ART108 A1 continuation', utc=datetime.now(timezone.utc).isoformat(),
              blender=bpy.app.version_string,
              limits=['Discrete 0.5m centreline sampling; finite hull sweep belongs to M4.',
                      'Blender art-camera review; live Unity HUD, water and all hulls unverified.',
                      'Nominal seabedDepth controls water colour; physicalAnchorDepth is terrain depth.',
                      'FBX import compared with documented ART108 X compensation; no new export.'],
              maps=[])
for name in NAMES:
    result['maps'].append(audit(name))
    result['all_passed'] = len(result['maps']) == len(NAMES)
    (MAPS / 'continuation-audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('ALL FIVE A1 MAPS PASS', flush=True)

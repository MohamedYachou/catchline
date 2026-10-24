"""Read-only source hair-band audit. Run in Blender, -- --name NAME.

Angles run from +X around +Z; -90 degrees is the face. The natural
hairline rises towards the forehead and above each exposed ear. It falls
behind the ear towards the nape. Sampling the face/ear below that line
would mistake intentionally visible skin for a bald patch.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = Path(__file__).resolve().parents[2]
out = root / 'Art/Models/CrewV2' / args.name
manifest = json.loads((out / 'build-manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(out / (args.name + '.blend')))
bpy.data.objects['CrewRig'].data.pose_position = 'REST'
trees = {}
for part in ('Face', 'Hair', 'Hat'):
    ob = bpy.data.objects[args.name + '_' + part]
    trees[part] = BVHTree.FromPolygons(
        [ob.matrix_world @ v.co for v in ob.data.vertices],
        [tuple(p.vertices) for p in ob.data.polygons])
hits = []
gaps = []
for degrees in range(0, 360, 10):
    angle = math.radians(degrees)
    # Independent fixed anatomical envelope, not derived from hair hits.
    # Crown/forehead .885; above ears .80; behind ears/nape down to .70.
    front = max(0, -math.sin(angle))
    rear = max(0, math.sin(angle))
    bottom = .800 + .085 * front - .100 * min(1, rear / .55)
    for row in range(9):
        level = bottom + (.895 - bottom) * row / 8
        outward = Vector((math.cos(angle), math.sin(angle), 0))
        origin = outward * .5 + Vector((0, 0, level))
        distances = {part: tree.ray_cast(origin, -outward, .6)[3]
                     for part, tree in trees.items()}
        cover = [distances[part] for part in ('Hair', 'Hat')
                 if distances[part] is not None]
        skin_first = (distances['Face'] is not None and
                      (not cover or min(cover) > distances['Face'] + .0002))
        hit = {'angle_degrees': degrees, 'z_m': level,
               'outside_in_distance_m': distances, 'skin_first': skin_first}
        hits.append(hit)
        if skin_first:
            gaps.append(hit)
result = {
    'name': args.name, 'revision': manifest['revision'],
    'source_sha256': hashlib.sha256((out / (args.name + '.blend')).read_bytes()).hexdigest(),
    'scope': 'Full circle every 10 degrees, 9 heights per angle, natural forehead/ear boundary to .895m; lower rear band reaches .700m. Exposed face and ears below the fixed anatomical hairline are excluded.',
    'hairline_formula_m': '.800 + .085*max(0,-sin(angle)) - .100*min(1,max(0,sin(angle))/.55)',
    'tolerance_m': .0002, 'rays': len(hits),
    'skin_first_count': len(gaps), 'skin_first_hits': gaps,
    'all_passed': not gaps, 'hits': hits}
(out / 'hair-band-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(args.name, 'FULL BAND', len(hits), 'GAPS', len(gaps),
      [(x['angle_degrees'], round(x['z_m'], 4)) for x in gaps], flush=True)
assert not gaps, 'Skin-first hits in the fixed anatomical hair band'

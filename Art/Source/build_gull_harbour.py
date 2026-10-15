"""Blender 5.2: editable Gull Harbour kit, FBX exports and game-angle previews.

Uses the proven Crab Coast mesh/export helpers. No external generators, textures,
Unity APIs or editor are used. Source coordinates: X right, -Y front, Z up.
"""
from pathlib import Path
import bpy
import bmesh
import importlib.util
import json
import math
import random
import sys
from mathutils import Vector

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Art/Models/GullHarbour'
spec = importlib.util.spec_from_file_location('crab_helpers', Path(__file__).with_name('build_crab_coast_props.py'))
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
B.PALETTE.update({
    'M_DeckWood': '#C58B50', 'M_WoodHighlight': '#DFB77A', 'M_WoodRecess': '#8C5A36',
    'M_HullBlue': '#2A6685', 'M_OilskinYellow': '#E6AD38', 'M_Skin': '#B9784B',
    'M_KelpGreen': '#477A56', 'M_FishSilver': '#BAC9C6',
})
G = B.Geometry
COLLECTION = None
ASSET_ROOT = None
PIVOTS = {}
NOTES = []


def part(name, geometry, pivot=(0, 0, 0), smooth=False):
    geometry.vertices = [tuple(Vector(v) - Vector(pivot)) for v in geometry.vertices]
    obj = geometry.object(name, ASSET_ROOT, COLLECTION)
    obj.location = pivot
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for p in obj.data.polygons:
        p.use_smooth = smooth
    PIVOTS[name] = list(pivot)
    return obj


def bevel_box(g, centre, size, colour, amount=.012):
    temp = G()
    temp.box(centre, size, colour)
    obj = temp.object('_BevelTemporary', None, COLLECTION)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new('Applied_chunky_bevel', 'BEVEL')
    modifier.width = min(amount, min(size) * .24)
    modifier.segments = 1
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    g.add([v.co for v in obj.data.vertices], [tuple(p.vertices) for p in obj.data.polygons], colour)
    bpy.data.objects.remove(obj, do_unlink=True)


def lathe(g, rings, sides, colour, centre=(0, 0, 0), caps=True):
    cx, cy, cz = centre
    verts = [(cx + radius * math.cos(i * math.tau / sides),
              cy + radius * math.sin(i * math.tau / sides), cz + z)
             for z, radius in rings for i in range(sides)]
    faces = []
    if caps:
        faces += [tuple(reversed(range(sides))), tuple(range((len(rings) - 1) * sides, len(rings) * sides))]
    for j in range(len(rings) - 1):
        faces += [(j * sides + i, j * sides + (i + 1) % sides,
                   (j + 1) * sides + (i + 1) % sides, (j + 1) * sides + i) for i in range(sides)]
    g.add(verts, faces, colour)


def ring(g, radius, wall, z0, z1, colour, centre=(0, 0), sides=16):
    cx, cy = centre
    verts = [(cx + r * math.cos(i * math.tau / sides), cy + r * math.sin(i * math.tau / sides), z)
             for r, z in ((radius, z0), (radius, z1), (radius - wall, z0), (radius - wall, z1))
             for i in range(sides)]
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces += [(i, j, j + sides, i + sides),
                  (i + 2 * sides, i + 3 * sides, j + 3 * sides, j + 2 * sides),
                  (i, i + 2 * sides, j + 2 * sides, j),
                  (i + sides, j + sides, j + 3 * sides, i + 3 * sides)]
    g.add(verts, faces, colour)


def rowboat():
    outline = [(-.95, 2.1), (.95, 2.1), (1.15, 1.8), (1.2, 1.3), (1.2, 0),
               (1.2, -1.5), (1., -1.65), (.45, -1.95), (0, -2.1),
               (-.45, -1.95), (-1., -1.65), (-1.2, -1.5), (-1.2, 0), (-1.2, 1.3), (-1.15, 1.8)]
    n = len(outline)
    hull = G()
    # Cross-section loops create a closed hollow hull, not a solid painted block.
    # ART-010: broad outer shoulder and inner lip bevels retain exact hull extents.
    levels = [(.55, .88, -.45), (.91, .96, -.10), (.995, .998, .405),
              (1, 1, .43), (.94, .97, .43), (.935, .965, .405), (.78, .89, -.32)]
    verts = [(x * sx, y * sy, z + (.07 * (abs(y)/2.1)**2 if z > .4 else 0)) for sx, sy, z in levels for x, y in outline]
    for j in range(len(levels) - 1):
        hull.add(verts[j * n:(j + 2) * n],
                 [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)],
                 'M_HullNavy' if j < 3 else 'M_DeckWood')
    hull.add(verts[:n], [tuple(reversed(range(n)))], 'M_HullNavy')
    hull.add(verts[-n:], [tuple(range(n))], 'M_DeckWood')
    # Waterline stripe follows the shell, slightly proud of the navy paint.
    stripe_verts = [(x * sx, y * sy, z) for sx, sy, z in ((.79, .931, -.25), (.875, .95, -.15))
                    for x, y in outline]
    hull.add(stripe_verts, [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)], 'M_SafetyOrange')
    part('Hull', hull)
    deck = G()
    for i in range(8):
        bevel_box(deck, (-.875 + i * .25, 0, -.025), (.25, 3, .05),
                  'M_WoodHighlight' if i in (1, 5) else 'M_DeckWood', .008)
    part('PlankDeck', deck)
    rail = G()
    for i, p in enumerate(outline):
        q = outline[(i + 1) % n]
        rail.beam((p[0] * .97, p[1] * .985, .45 + .07*(abs(p[1])/2.1)**2), (q[0] * .97, q[1] * .985, .45 + .07*(abs(q[1])/2.1)**2),
                  .10, .075, 'M_RailIvory', .022)
    rope_path = [(x*1.012, y*1.005, .39+.07*(abs(y)/2.1)**2) for x,y in outline]
    rail.tube(rope_path + [rope_path[0]], [.032]*(len(rope_path)+1), 8, 'M_Rope')
    # Broad fastening plates stay on existing gunwale, away from sockets/oarlocks.
    for side in (-1, 1):
        for y in (-1.35, 1.35):
            bevel_box(rail, (side*1.164, y, .49), (.075, .13, .025), 'M_Steel', .009)
    part('IvoryGunwale', rail)
    thwart = G()
    bevel_box(thwart, (0, 0, .32), (2.05, .28, .09), 'M_DeckWood', .015)
    # End soles close visible dark voids outside the authoritative walking deck.
    for plan in ([(-.93,1.50),(.93,1.50),(.78,1.82),(-.78,1.82)],
                 [(-.83,-1.50),(.83,-1.50),(.35,-1.73),(0,-1.85),(-.35,-1.73)]):
        count=len(plan)
        vertices=[(x,y,z) for z in (-.05,0) for x,y in plan]
        faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]
        faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
        thwart.add(vertices,faces,'M_DeckWood')
    part('CentreThwart', thwart)
    for side, label in ((-1, 'Port'), (1, 'Starboard')):
        pivot = (side * 1.12, 0, .49)
        lock = G()
        ring(lock, .055, .012, .43, .51, 'M_Steel', (pivot[0], 0), 12)
        part('Oarlock_' + label, lock)
        oar = G()
        oar.tube([(side * .35, -.31, .53), pivot, (side * 1.93, .32, .39)], [.029, .025, .025], 8, 'M_DeckWood')
        bevel_box(oar, (side * 2.05, .37, .39), (.42, .17, .045), 'M_SafetyOrange', .012)
        part('Oar_' + label, oar, pivot)
    for distance, label in ((.5, 'Stern'), (2.5, 'Bow')):
        y = 1.5 - distance
        socket = G()
        ring(socket, .052, .014, .44, .57, 'M_Steel', (-1.115, y), 12)
        part('RodSocket_Port_' + label, socket, (-1.115, y, .44))
    NOTES.append('Deck 2 m across x 3 m fore-aft, top at Z=0. Hull length4.2m/beam2.4m; oars extend beyond hull. Sockets measured from build-deck stern Y=+1.5.')
    NOTES.append('ART-010: broad shell/rail bevels, quieter timber variation, end sole panels and four gunwale plates. Original part set/pivots/socket positions retained; end panels are outside the build rectangle. No props fused into hull.')


def fishing_rod():
    rod = G()
    rod.tube([(0, 0, .015), (0, 0, .34), (0, 0, .85), (0, 0, 1.25), (0, 0, 1.6)],
             [.024, .022, .017, .012, .007], 12, 'M_HullNavy')
    # Exaggerated cork and blank keep the working silhouette at gameplay zoom.
    lathe(rod, [(0, .026), (.025, .031), (.235, .031), (.255, .025)], 16, 'M_DeckWood')
    for z in (.03, .09, .15, .21):
        ring(rod, .0315, .002, z, z + .008, 'M_WoodHighlight', sides=16)
    lathe(rod, [(.26, .025), (.31, .025)], 12, 'M_Steel')
    for z, r in ((.5, .027), (.85, .024), (1.15, .021), (1.40, .018), (1.58, .014)):
        ring(rod, r, .005, z - .005, z + .005, 'M_Steel', (0, -.027), 12)
    rod.beam((0, 0, .28), (.055, 0, .28), .025, .025, 'M_Steel', .004)
    rod.tube([(.035, 0, .24), (.105, 0, .24)], [.051, .051], 16, 'M_HullNavy')
    rod.tube([(.048, 0, .24), (.092, 0, .24)], [.054, .054], 16, 'M_OilskinYellow')
    part('RodAndReel', rod)
    handle = G()
    handle.beam((.107, 0, .24), (.107, -.065, .19), .014, .014, 'M_Steel', .002)
    handle.tube([(.107, -.065, .19), (.147, -.065, .19)], [.015, .015], 10, 'M_DeckWood')
    part('ReelHandle', handle, (.107, 0, .24))
    NOTES.append('1.6m upright rod, 48mm blank butt / 62mm cork grip / 14mm tip; intentionally exaggerated for game zoom. ReelHandle pivot (.107,0,.24), local X spin.')


def bobber():
    g = G()
    lathe(g, [(-.045, .006), (-.035, .027), (0, .040)], 16, 'M_RailIvory', caps=False)
    lathe(g, [(0, .040), (.025, .028), (.035, .008)], 16, 'M_SafetyOrange', caps=False)
    lathe(g, [(.03, .005), (.075, .005)], 8, 'M_SafetyOrange')
    lathe(g, [(-.045, .006), (-.043, .006)], 8, 'M_RailIvory')
    part('BobberBody', g)
    NOTES.append('Overall height0.12m, waterline pivot Z=0; body extends0.045m below water.')


def cooler(ice=False):
    body = G()
    bevel_box(body, (0, 0, .025), (.78, .48, .05), 'M_HullNavy')
    body.rectangle_ring(.78, .48, .035, .045, .395, .035, 'M_HullNavy')
    body.rectangle_ring(.8, .5, .035, .375, .40, .035, 'M_RailIvory')
    for sx in (-1, 1):
        bevel_box(body, (sx * .391, 0, .24), (.018, .15, .055), 'M_Steel', .004)
    bevel_box(body, (0, -.245, .34), (.10, .01, .07), 'M_Steel', .003)
    for sx in (-1,1):
        body.tube([(sx*.397,-.065,.25),(sx*.397,-.065,.17),(sx*.397,.065,.17),(sx*.397,.065,.25)], [.003]*4, 8, 'M_RailIvory')
    body.tube([(.25,-.238,.07),(.25,-.25,.07)],[.024,.024],12,'M_Steel')
    bevel_box(body,(0,-.244,.32),(.065,.012,.10),'M_RailIvory',.003)
    part('CoolerBody', body)
    lid = G()
    bevel_box(lid, (0, 0, .423), (.80, .50, .046 if ice else .054),
              'M_SeaTeal' if ice else 'M_RailIvory', .012)
    if ice:
        for x in (-.22, .22):
            for dx, dy in ((.055, 0), (0, .055), (.035, .035), (.035, -.035)):
                lid.beam((x - dx, -.02 - dy, .448), (x + dx, -.02 + dy, .448),
                         .004, .004, 'M_RailIvory')
    part('HingedLid', lid, (0, .25, .40))
    NOTES.append('Lid origin at rear hinge (0,+0.25,+0.40); local X rotation opens front edge. IceBox shares CoolerBody geometry.')


def bait_bucket():
    g = G()
    lathe(g, [(0, .11), (.025, .12), (.24, .15)], 16, 'M_SeaTeal', caps=False)
    lathe(g, [(0, .11), (.015, .11)], 16, 'M_SeaTeal')
    ring(g, .15, .012, .24, .26, 'M_RailIvory')
    # Open interior; no floating closed top that hides the bait volume.
    lathe(g, [(.02, .105), (.24, .138)], 16, 'M_SeaTeal', caps=False)
    g.tube([(-.14, 0, .22), (-.13, 0, .31), (0, 0, .36), (.13, 0, .31), (.14, 0, .22)],
           [.008] * 5, 6, 'M_Rope')
    part('BaitBucketBody', g)


def lunch_tin():
    body = G()
    bevel_box(body, (0, 0, .05), (.25, .18, .10), 'M_HullNavy', .016)
    bevel_box(body, (0, -.09, .07), (.05, .008, .035), 'M_Steel', .002)
    part('LunchTinBody', body)
    lid = G()
    bevel_box(lid, (0, 0, .11), (.25, .18, .02), 'M_HullBlue', .004)
    part('LunchTinLid', lid, (0, .09, .10))


FISH = {'Herring': (.26, .09, .065, 'M_Steel'), 'Mackerel': (.34, .085, .065, 'M_SeaTeal'),
        'Pollock': (.48, .11, .075, 'M_KelpGreen'), 'SeaBass': (.5, .13, .085, 'M_HullNavy'),
        'CongerEel': (.8, .045, .035, 'M_HullBlue')}


def fish(name):
    length, height_ratio, width_ratio, back = FISH[name]
    eel = name == 'CongerEel'
    centre_z = length * (height_ratio + .015)
    stations = [(-.5, .35), (-.43, .65), (-.30, .90), (-.10, 1), (.08, .85), (.22, .45), (.28, .16)]
    if eel:
        stations = [(-.5, .05), (-.45, .85), (-.30, 1), (-.10, .95), (.10, .8), (.25, .50), (.33, .20)]
    sides = 12
    verts = []
    for y, factor in stations:
        centre_x = math.sin((y + .5) * math.tau) * length * .012 if eel else 0
        verts += [(centre_x + length * width_ratio * factor * math.cos(i * math.tau / sides),
                   y * length, centre_z + length * height_ratio * factor * math.sin(i * math.tau / sides))
                  for i in range(sides)]
    body = G()
    body.add(verts, [tuple(reversed(range(sides))), tuple(range((len(stations) - 1) * sides, len(stations) * sides))], 'M_FishSilver')
    for j in range(len(stations) - 1):
        for i in range(sides):
            colour = back if math.sin((i + .5) * math.tau / sides) > .3 else 'M_FishSilver'
            if math.sin((i + .5) * math.tau / sides) < -.3:
                colour = 'M_RailIvory'
            body.faces.append((j * sides + i, j * sides + (i + 1) % sides,
                               (j + 1) * sides + (i + 1) % sides, (j + 1) * sides + i))
            body.colours.append(colour)
    for side in (-1, 1):
        body.ellipsoid((side * length * width_ratio * .64, -.405 * length,
                        centre_z + length * height_ratio * .25), (length * .013,) * 3, 8, 2, 'M_Rubber')
    def fin(poly, colour, thick=.004):
        temp = G()
        temp.extrude_polygon(poly, -length * thick, length * thick, colour)
        temp.vertices = [(z, y, centre_z + x) for x, y, z in temp.vertices]
        return temp
    dorsal = [(height_ratio * .75 * length, -.22 * length),
              (height_ratio * 1.35 * length, -.12 * length), (height_ratio * .65 * length, .13 * length)]
    body.merge(fin(dorsal, back))
    if not eel:
        for side in (-1, 1):
            points = [(side * width_ratio * length * .7, -.28 * length, centre_z),
                      (side * width_ratio * length * 1.7, -.05 * length, centre_z - .035 * length),
                      (side * width_ratio * length * .7, -.01 * length, centre_z - .015 * length)]
            # Closed thin prism: coincident reverse faces are discarded by FBX import.
            bottom = [(x, y, z - length * .004) for x, y, z in points]
            body.add(points + bottom, [(0, 1, 2), (5, 4, 3),
                                      (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], 'M_Steel')
    if name == 'Mackerel':
        # Solid narrow surface ribbons follow the upper body; no bitmap/alpha stripes.
        for j, (position, factor) in enumerate(((-.26, .90), (-.18, .96), (-.10, 1), (-.02, .94), (.06, .87), (.13, .70))):
            points = []
            for a in range(9):
                angle = .12 + (math.pi - .24) * a / 8
                x = length * width_ratio * factor * math.cos(angle) * 1.018
                z = centre_z + length * height_ratio * factor * math.sin(angle) * 1.018
                y = length * (position + .01 * math.sin(angle * 3 + j))
                points.append((x, y, z))
            body.tube(points, [length * .0035] * len(points), 4, 'M_HullNavy')
    tail_start = .33 if eel else .28
    tail = fin([(0, tail_start * length), (height_ratio * length, .5 * length),
                (0, (.47 if eel else .43) * length), (-height_ratio * length, .5 * length)], back)
    # Shift the complete fish to a grounded pivot without changing the requested length.
    low = min(v[2] for v in body.vertices + tail.vertices)
    for geom in (body, tail):
        geom.vertices = [(x, y, z - low) for x, y, z in geom.vertices]
    part(name + 'Body', body)
    part(name + 'Tail', tail, (0, tail_start * length, centre_z - low))
    NOTES.append(f'Fish faces -Y; nose to tail is {length}m. Tail origin is the body/tail join; rotate local X/Z for a flop. Mackerel stripes are geometry.' if name == 'Mackerel' else f'Fish faces -Y, nose-to-tail length {length}m; separate tail with origin at join.')


def crew_body():
    shape = G()
    shape.ellipsoid((0, 0, .78), (.16, .145, .17), 24, 12, 'M_Skin')
    shape.ellipsoid((0, -.015, .455), (.15, .095, .17), 20, 10, 'M_OilskinYellow')
    shape.ellipsoid((0, 0, .63), (.065, .065, .085), 12, 6, 'M_Skin')
    shape.ellipsoid((0, -.148, .775), (.020, .028, .025), 12, 6, 'M_Skin')
    for side in (-1, 1):
        shape.ellipsoid((side * .156, 0, .78), (.030, .025, .043), 12, 6, 'M_Skin')
        shape.tube([(side * .11, 0, .565), (side * .25, 0, .565), (side * .43, 0, .565)],
                   [.064, .054, .042], 12, 'M_HullNavy')
        shape.ellipsoid((side * .475, -.007, .565), (.060, .043, .041), 12, 6, 'M_Rubber')
        shape.ellipsoid((side * .455, -.040, .548), (.035, .025, .035), 12, 6, 'M_Rubber')
        shape.tube([(side * .075, 0, .32), (side * .085, 0, .20), (side * .09, 0, .08)],
                   [.072, .061, .055], 12, 'M_OilskinYellow')
        shape.ellipsoid((side * .09, -.035, .055), (.067, .095, .055), 16, 8, 'M_Rubber')
    body = part('CrewBody', shape)
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    body.data.remesh_voxel_size = .009
    bpy.ops.object.voxel_remesh()
    # QuadriFlow's absolute 1e-4 edge check rejects small voxel edges at metre scale.
    # Work temporarily at 100x, then restore metres in vertex data, not object scale.
    for v in body.data.vertices:
        v.co *= 100
    body.data.update()
    status = bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=True, use_preserve_sharp=False,
                                   use_preserve_boundary=False, preserve_attributes=False,
                                   smooth_normals=True, mode='FACES', target_faces=2600, seed=23)
    assert status == {'FINISHED'}, status
    for v in body.data.vertices:
        v.co /= 100
    z0 = min(v.co.z for v in body.data.vertices)
    z1 = max(v.co.z for v in body.data.vertices)
    for v in body.data.vertices:
        v.co.z = (v.co.z - z0) * .95 / (z1 - z0)
    body.data.materials.clear()
    for name in B.PALETTE:
        body.data.materials.append(B.MATERIALS[name])
    ids = {name: i for i, name in enumerate(B.PALETTE)}
    for p in body.data.polygons:
        c = p.center
        if c.z > .875 or (c.z > .76 and c.y > .025) or (c.z > .83 and abs(c.x) > .115):
            colour = 'M_Rubber'
        elif c.z > .635:
            colour = 'M_Skin'
        elif c.z < .115 or abs(c.x) > .438:
            colour = 'M_Rubber'
        elif abs(c.x) > .145 and c.z > .43:
            colour = 'M_HullNavy'
        elif c.z < .52 or (c.y < -.060 and abs(c.x) < .12):
            colour = 'M_OilskinYellow'
        else:
            colour = 'M_HullNavy'
        p.material_index = ids[colour]
        p.use_smooth = True
    body.data.update()
    assert all(len(p.vertices) == 4 for p in body.data.polygons), 'Crew body must retain all quads'
    details = G()
    for side in (-1, 1):
        details.ellipsoid((side * .047, -.143, .80), (.011, .008, .017), 12, 4, 'M_Rubber')
        details.ellipsoid((side * .075, -.098, .54), (.009, .006, .009), 8, 3, 'M_HullNavy')
        details.beam((side * .075, -.092, .545), (side * .075, -.080, .60),
                     .020, .010, 'M_OilskinYellow', .002)
    for x, y, z in ((-.075, -.11, .884), (0, -.134, .89), (.075, -.11, .884)):
        details.ellipsoid((x, y, z), (.052, .028, .038), 12, 4, 'M_Rubber')
    details.tube([(-.017, -.15, .755), (0, -.154, .75), (.017, -.15, .755)], [.003] * 3, 5, 'M_Rubber')
    part('FaceAndButtons', details, smooth=True)
    NOTES.append('One continuous closed all-quad CrewBody, symmetric T-pose,0.95m feet-to-scalp. No armature. Separate face/buttons. Hat seat anchor source(0,0,0.91), Unity(0,0.91,0). Mixamo service not run.')


def captain_cap():
    g = G()
    lathe(g, [(0, .15), (.035, .16), (.075, .177), (.11, .15), (.12, .04)], 24, 'M_RailIvory')
    ring(g, .154, .022, -.005, .036, 'M_HullNavy', sides=24)
    # Crescent visor: inner arc intersects the band, outer arc drops toward front.
    n = 17
    verts = []
    for layer in (0, 1):
        for outer in (False, True):
            for i in range(n):
                a = math.radians(-76 + i * 152 / (n - 1))
                r = .149 + ((.067 * math.cos(a)) if outer else 0)
                verts.append((math.sin(a) * r, -math.cos(a) * r,
                              .008 - (.026 * math.cos(a) if outer else 0) - layer * .014))
    faces = []
    for i in range(n - 1):
        faces += [(i, i + 1, n + i + 1, n + i),
                  (2*n+i, 3*n+i, 3*n+i+1, 2*n+i+1),
                  (n+i, n+i+1, 3*n+i+1, 3*n+i),
                  (i, 2*n+i, 2*n+i+1, i+1)]
    faces += [(0, n, 3*n, 2*n), (n-1, 3*n-1, 4*n-1, 2*n-1)]
    g.add(verts, faces, 'M_HullNavy')
    # Fine gold cord and a real anchor badge, both attached to the front.
    g.tube([(-.128,-.086,.035),(-.07,-.146,.031),(0,-.162,.030),(.07,-.146,.031),(.128,-.086,.035)], [.004]*5, 8, 'M_OilskinYellow')
    badge = G()
    badge.ellipsoid((0, -.170, .078), (.027,.008,.031), 16, 6, 'M_HullNavy')
    badge.tube([(0,-.181,.093),(0,-.181,.057)], [.0035]*2, 8, 'M_OilskinYellow')
    badge.tube([(-.016,-.181,.069),(-.012,-.181,.058),(0,-.181,.053),(.012,-.181,.058),(.016,-.181,.069)], [.0035]*5, 8, 'M_OilskinYellow')
    badge.beam((-.012,-.181,.081),(.012,-.181,.081),.004,.004,'M_OilskinYellow')
    part('CaptainCap', g)
    part('AnchorBadge', badge)
    NOTES.append('Peaked cap with attached curved crescent visor, navy band, gold cord and anchor badge. Shared mounting-seat root unchanged.')


def beanie():
    g = G()
    lathe(g, [(0, .155), (.04, .17), (.09, .15), (.14, .09), (.155, .02)], 20, 'M_SafetyOrange')
    ring(g, .174, .028, -.012, .035, 'M_SafetyOrange', sides=20)
    g.ellipsoid((0, 0, .17), (.026, .026, .026), 12, 4, 'M_SafetyOrange')
    g.vertices = [(x, y, z * .65) for x, y, z in g.vertices]
    part('DeckhandBeanie', g)


def hood():
    g = G()
    n = 17
    profiles = [(-.23, .10, .085), (-.12, .18, .15), (.025, .17, .15), (.10, .095, .09)]
    verts = []
    for inner in (False, True):
        for z, rx, ry in profiles:
            verts += [((rx - (.015 if inner else 0)) * math.cos(math.radians(-30 + 240 * i / (n - 1))),
                       (ry - (.015 if inner else 0)) * math.sin(math.radians(-30 + 240 * i / (n - 1))), z)
                      for i in range(n)]
    count = len(profiles) * n
    for side in (0, 1):
        faces = [(side * count + j * n + i, side * count + j * n + i + 1,
                  side * count + (j + 1) * n + i + 1, side * count + (j + 1) * n + i)
                 for j in range(len(profiles) - 1) for i in range(n - 1)]
        g.add(verts, faces, 'M_HullNavy' if side else 'M_OilskinYellow')
    # Close shell boundaries, leaving the intended face opening.
    for j in range(len(profiles) - 1):
        for i in (0, n - 1):
            g.add(verts, [(j * n + i, (j + 1) * n + i, count + (j + 1) * n + i, count + j * n + i)], 'M_OilskinYellow')
    for j in (0, len(profiles) - 1):
        for i in range(n - 1):
            g.add(verts, [(j * n + i, j * n + i + 1, count + j * n + i + 1, count + j * n + i)], 'M_OilskinYellow')
    for side in (-1, 1):
        g.tube([(side * .10, -.055, -.18), (side * .07, -.08, -.255)], [.005, .005], 6, 'M_Rope')
    part('OilskinHood', g)
    NOTES.append('Headgear pivot is common head seat, not ground. Attach at source CrewBody(0,0,0.91); hood extends down toward shoulders.')


def quay():
    g = G()
    for i in range(16):
        bevel_box(g, (-1.875 + i * .25, 0, -.07), (.25, 2, .14),
                  'M_DeckWood' if i % 3 else 'M_WoodHighlight', .008)
    for y in (-.86, .86):
        g.beam((-2, y, -.20), (2, y, -.20), .15, .16, 'M_WoodRecess', .02)
    for x in (-1.75, 1.75):
        for y in (-.75, .75):
            g.beam((x, y, -.9), (x, y, -.12), .23, .23, 'M_DeckWood', .025)
    for x in (-1.5,1.5):
        g.torus((x,-.90,.04),.075,.018,'M_Steel')
    for i in range(12):
        x=-1.75+i*.30
        g.beam((x,-.66,-.002),(x+.055,-.29,-.002),.012,.004,'M_WoodRecess')
    part('Quay4m', g)
    NOTES.append('Quay pivot is walking surface centreZ=0;4m lengthX,2m depth, piles extend0.9m below.')


def bollard():
    g = G()
    bevel_box(g, (0, 0, .04), (.40, .32, .08), 'M_HullNavy', .015)
    lathe(g, [(.08, .10), (.42, .10), (.46, .12)], 12, 'M_HullNavy')
    g.beam((-.22, 0, .42), (.22, 0, .42), .11, .11, 'M_HullNavy', .015)
    ring(g, .113, .012, .23, .25, 'M_Rope', sides=16)
    part('Bollard', g)


def lamp():
    g = G()
    lathe(g, [(0, .15), (.10, .15), (.15, .07), (2.5, .05)], 12, 'M_HullNavy')
    g.tube([(0, 0, 2.45), (0, -.10, 2.70), (0, -.40, 2.72)], [.045] * 3, 8, 'M_HullNavy')
    lathe(g, [(2.25, .18), (2.32, .15), (2.62, .15), (2.70, .20)], 12, 'M_RailIvory', (0, -.40, 0))
    for x in (-.13, .13):
        g.beam((x, -.40, 2.31), (x, -.40, 2.63), .024, .024, 'M_HullNavy', .004)
    lathe(g, [(2.67, .21), (2.77, .08), (2.80, .025)], 12, 'M_SafetyOrange', (0, -.40, 0))
    part('HarbourLamp', g)
    NOTES.append('Lamp is mesh only; no actual Light exported.')


def house(second=False):
    w, d, wall_h, height = (3.4, 2.8, 2.8, 3.9) if second else (3.0, 2.6, 2.5, 3.6)
    walls = G()
    bevel_box(walls, (0, 0, wall_h / 2), (w, d, wall_h), 'M_SeaTeal' if second else 'M_RailIvory', .045)
    part('HouseWalls', walls)
    roof = G()
    a, b = w / 2 + .15, d / 2 + .13
    verts = [(-a, -b, wall_h), (a, -b, wall_h), (0, -b, height),
             (-a, b, wall_h), (a, b, wall_h), (0, b, height)]
    roof.add(verts, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (0, 2, 5, 3), (1, 4, 5, 2)],
             'M_SafetyOrange' if second else 'M_HullNavy')
    for side in (-1, 1):
        roof.beam((side * a, -b, wall_h), (0, -b, height), .08, .08, 'M_DeckWood', .012)
        for y in (-d * .3, 0, d * .3):
            roof.beam((side * a, y, wall_h + .025), (0, y, height + .025), .04, .04, 'M_HullBlue' if not second else 'M_WoodHighlight', .008)
    part('HouseRoof', roof)
    fittings = G()
    bevel_box(fittings, (0, -d / 2 - .03, .85), (.68, .065, 1.7), 'M_HullNavy', .02)
    for x in (-w * .30, w * .30):
        bevel_box(fittings, (x, -d / 2 - .045, 1.6), (.61, .065, .80), 'M_HullBlue', .02)
        for dx in (-.32, .32):
            fittings.beam((x + dx, -d / 2 - .08, 1.17), (x + dx, -d / 2 - .08, 2.03), .055, .045, 'M_RailIvory', .005)
        for z in (1.17, 1.60, 2.03):
            fittings.beam((x - .32, -d / 2 - .08, z), (x + .32, -d / 2 - .08, z), .05, .045, 'M_RailIvory', .005)
    for x in (-w / 2 + .045, w / 2 - .045):
        fittings.beam((x, -d / 2 - .02, .03), (x, -d / 2 - .02, wall_h), .08, .075, 'M_DeckWood', .01)
    bevel_box(fittings,(0,-d/2-.16,.065),(.88,.38,.13),'M_Steel',.025)
    bevel_box(fittings,(w*.20,.35,height-.10),(.34,.36,.75),'M_RailIvory',.025)
    bevel_box(fittings,(w*.20,.35,height+.29),(.43,.45,.08),'M_Steel',.01)
    for side in (-1,1):
        fittings.beam((side*a,-b,wall_h),(side*a,b,wall_h),.10,.10,'M_WoodHighlight',.01)
    part('DoorsWindowsTrim', fittings)
    NOTES.append('House module ground pivot; roof overhang is included in measured bounds. Front door faces-Y.')


def lighthouse():
    g = G()
    lathe(g, [(0, .95), (.15, .95), (.25, .72), (1.8, .64)], 16, 'M_RailIvory')
    for z0, z1, r0, r1, colour in ((1.8, 2.2, .64, .61, 'M_SafetyOrange'),
                                 (2.2, 3.5, .61, .52, 'M_RailIvory'),
                                 (3.5, 3.9, .52, .49, 'M_SafetyOrange'),
                                 (3.9, 4.7, .49, .44, 'M_RailIvory')):
        lathe(g, [(z0, r0), (z1, r1)], 16, colour)
    lathe(g, [(4.68, .70), (4.78, .70)], 16, 'M_HullNavy')
    lathe(g, [(4.78, .42), (5.55, .42)], 12, 'M_HullBlue')
    ring(g,.66,.035,5.08,5.12,'M_RailIvory',sides=16)
    for i in range(16):
        a=i*math.tau/16
        g.beam((.64*math.cos(a),.64*math.sin(a),4.78),(.64*math.cos(a),.64*math.sin(a),5.10),.035,.035,'M_RailIvory')
    for i in range(8):
        a = i * math.tau / 8
        g.beam((.44 * math.cos(a), .44 * math.sin(a), 4.78),
               (.44 * math.cos(a), .44 * math.sin(a), 5.55), .04, .04, 'M_HullNavy', .006)
    lathe(g, [(5.55, .65), (5.95, .08), (6.0, .02)], 16, 'M_HullNavy')
    bevel_box(g, (0, -.72, .72), (.39, .03, 1.2), 'M_HullNavy', .015)
    ring(g,.44,.025,4.79,4.84,'M_RailIvory',sides=12)
    ring(g,.44,.025,5.47,5.55,'M_RailIvory',sides=12)
    part('Lighthouse', g)


def rock(index):
    size = [(1.8, 1.4, 1.0), (1.3, 1.1, .8), (2.1, 1.5, 1.2)][index]
    rng = random.Random(100 + index)
    g = G()
    sides = 12
    # Eight shaped rings: a flat submerged sole and broad, asymmetric shoulders.
    profile = [(0,.73),(.10,.91),(.28,1),(.48,.96),(.68,.84),(.84,.66),(.95,.42),(1,.19)]
    radii = [rng.uniform(.87,1.13) for _ in range(sides)]
    verts = []
    for j,(z,r) in enumerate(profile):
        for i in range(sides):
            a = i * math.tau/sides + .06*math.sin(j+index)
            rr = r * radii[i] * rng.uniform(.96,1.04)
            verts.append((math.cos(a)*rr + z*.13, math.sin(a)*rr - z*.08,
                          z if j in (0,7) else z+rng.uniform(-.035,.035)))
    faces = []
    for j in range(7):
        for i in range(sides):
            a=j*sides+i; b=j*sides+(i+1)%sides; c=b+sides; d=a+sides
            faces += [(a,b,c),(a,c,d)]
    faces += [tuple(reversed(range(sides))),tuple(range(7*sides,8*sides))]
    g.add(verts, faces, 'M_Steel')
    mins=[min(v[i] for v in g.vertices) for i in range(3)]
    maxs=[max(v[i] for v in g.vertices) for i in range(3)]
    g.vertices=[tuple((v[i]-(mins[i] if i==2 else (mins[i]+maxs[i])/2))*size[i]/(maxs[i]-mins[i]) for i in range(3)) for v in g.vertices]
    for i,face in enumerate(g.faces):
        # Broad coherent grey planes; no black speckle.
        g.colours[i] = 'M_FishSilver' if sum(g.vertices[k][0] for k in face)/len(face)<-.15 else 'M_Steel'
    part('BreakwaterRock', g)
    NOTES.append('188 triangles, flat sole at Z=0, faceted silhouette; canonical steel and silver stone greys.')


def kelp():
    g = G()
    # Pre-unioned leaf mat with inset flat bulb disks, no overlapping faces.
    data = json.loads(Path(__file__).with_name('kelp-mat.json').read_text())
    for face in data['faces']:
        g.add(face['triangle'], [(0, 1, 2)], face['material'])
    part('FloatingKelp', g)
    NOTES.append('Exactly flat at waterline Z=0: drift-aligned overlapping leaf silhouettes and four inset flattened bulbs. Planar union avoids z-fighting; no reverse faces. Regenerate JSON with build_kelp_mat.py (Shapely2.1+).')


def quay_ladder():
    quay()
    g=G()
    for x in (-.25,.25):
        g.tube([(x,-.94,.15),(x,-1.10,.15),(x,-1.10,-1.1)],[.03]*3,8,'M_Steel')
    for i in range(6):
        g.beam((-.25,-1.10,-.08-i*.19),(.25,-1.10,-.08-i*.19),.035,.04,'M_Steel')
    part('WaterLadder',g)


ASSETS = {
    'Quay4mLadder': ('Harbour',quay_ladder),
    'Rowboat': ('Boats', rowboat), 'FishingRod': ('Fishing', fishing_rod), 'Bobber': ('Fishing', bobber),
    'Cooler': ('DeckProps', lambda: cooler(False)), 'IceBox': ('DeckProps', lambda: cooler(True)),
    'BaitBucket': ('DeckProps', bait_bucket), 'LunchTin': ('DeckProps', lunch_tin),
    **{name: ('Fish', lambda name=name: fish(name)) for name in FISH},
    'CrewBody': ('Crew', crew_body), 'CaptainCap': ('Crew', captain_cap),
    'DeckhandBeanie': ('Crew', beanie), 'OilskinHood': ('Crew', hood),
    'Quay4m': ('Harbour', quay), 'Bollard': ('Harbour', bollard), 'LampPost': ('Harbour', lamp),
    'HouseA': ('Harbour', lambda: house(False)), 'HouseB': ('Harbour', lambda: house(True)),
    'Lighthouse': ('Harbour', lighthouse),
    **{f'BreakwaterRock{chr(65 + i)}': ('Harbour', lambda i=i: rock(i)) for i in range(3)},
    'KelpPatch': ('Harbour', kelp),
}


def build(name):
    global COLLECTION, ASSET_ROOT
    group, factory = ASSETS[name]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    PIVOTS.clear()
    NOTES.clear()
    B.MATERIALS.clear()
    B.MATERIALS.update({key: B.material(key, value) for key, value in B.PALETTE.items()})
    COLLECTION = bpy.data.collections.new('ASSET_EXPORT')
    scene.collection.children.link(COLLECTION)
    ASSET_ROOT = bpy.data.objects.new('Catchline_' + name, None)
    COLLECTION.objects.link(ASSET_ROOT)
    ASSET_ROOT['location'] = 'Gull Harbour / 1'
    ASSET_ROOT['unity_forward'] = '+Z'
    factory()
    bpy.context.view_layer.update()
    meshes = [o for o in COLLECTION.objects if o.type == 'MESH']
    stats = [B.mesh_stats(o) for o in meshes]
    low = [min(p['bounds_min_blender'][i] for p in stats) for i in range(3)]
    high = [max(p['bounds_max_blender'][i] for p in stats) for i in range(3)]
    # Catch accidental overflows of authoritative dimensions before exporting.
    if name in FISH:
        assert abs(high[1] - low[1] - FISH[name][0]) < 1e-5, (name, low, high)
    if name in ('Cooler', 'IceBox'):
        assert all(abs(high[i] - low[i] - target) < 1e-5 for i, target in enumerate((.8, .5, .45))), (name, low, high)
    if name == 'FishingRod':
        assert abs(high[2] - 1.6) < 1e-5 and abs(low[2]) < 1e-5
    if name == 'Bobber':
        assert abs(high[2] - low[2] - .12) < 1e-5
    if name == 'CrewBody':
        assert abs(high[2] - .95) < 1e-5 and abs(low[2]) < 1e-5
    B.preview_stage(scene, meshes)
    # The reusable prop stage is scaled for larger harbour modules and below-deck hulls.
    scale = max(1, max(high[i] - low[i] for i in range(3)) / .8)
    camera = scene.camera
    target = Vector(((low[0]+high[0])/2, (low[1]+high[1])/2, (low[2]+high[2])*.48))
    yaw, elevation = math.radians(35), math.radians(45)
    direction = Vector((math.sin(yaw)*math.cos(elevation),
                        (1 if name.startswith('ShopFront_') else -1)*math.cos(yaw)*math.cos(elevation),
                        math.sin(elevation)))
    camera.location = target + direction * (3 * scale)
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    projected = [camera.matrix_world.inverted() @ (o.matrix_world @ Vector(p)) for o in meshes for p in o.bound_box]
    camera.data.ortho_scale = max(max(v[i] for v in projected)-min(v[i] for v in projected) for i in (0,1))*1.30
    for light in bpy.data.collections['PREVIEW_ONLY_NOT_EXPORTED'].objects:
        if light.type == 'LIGHT':
            light.location *= scale
            light.data.energy *= scale * scale
            light.data.size *= scale
    bpy.data.objects['Preview_Ground'].location.z = low[2]
    scene.cycles.samples = 24
    for folder in (OUT / group, ROOT / 'Assets/Art/Models' / group, OUT / 'Previews' / group):
        folder.mkdir(parents=True, exist_ok=True)
    source = OUT / group / (name + '.blend')
    fbx = ROOT / 'Assets/Art/Models' / group / (name + '.fbx')
    preview = OUT / 'Previews' / group / (name + '.png')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in COLLECTION.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = ASSET_ROOT
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'MESH', 'EMPTY'},
        global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
        axis_forward='-Z', axis_up='Y', use_space_transform=True, bake_space_transform=True,
        use_mesh_modifiers=True, use_triangles=name != 'CrewBody', mesh_smooth_type='FACE',
        add_leaf_bones=False, bake_anim=False, use_custom_props=True, embed_textures=False)
    scene.render.filepath = str(preview)
    bpy.ops.wm.save_as_mainfile(filepath=str(source), check_existing=False)
    bpy.ops.render.render(write_still=True)
    result = {'asset': name, 'group': group, 'triangles': sum(p['triangles'] for p in stats),
              'dimensions_width_depth_height_m': [round(high[i] - low[i], 8) for i in range(3)],
              'bounds_min_blender': low, 'bounds_max_blender': high,
              'parts': stats, 'pivots_blender': dict(PIVOTS), 'notes': list(NOTES),
              'source': source.relative_to(ROOT).as_posix(), 'fbx': fbx.relative_to(ROOT).as_posix(),
              'preview': preview.relative_to(ROOT).as_posix()}
    if name == 'CrewBody':
        body = bpy.data.objects['CrewBody']
        result['crew_quads'] = len(body.data.polygons)
        result['crew_nonquads'] = sum(len(p.vertices) != 4 for p in body.data.polygons)
    print('GULL_ASSET', name, result['triangles'], result['dimensions_width_depth_height_m'], flush=True)
    return result


if __name__ == '__main__':
    assert bpy.app.version[:2] == (5, 2)
    arguments = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    path = OUT / 'build-metrics.json'
    old = json.loads(path.read_text()) if path.exists() else {'blender_version': bpy.app.version_string, 'assets': []}
    indexed = {a['asset']: a for a in old['assets']}
    for name in arguments or ASSETS:
        indexed[name] = build(name)
        old['assets'] = list(indexed.values())
        old['palette_srgb'] = B.PALETTE
        path.write_text(json.dumps(old, indent=2) + '\n')

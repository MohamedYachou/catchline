"""Build, export and render Catchline's six Crab Coast props in Blender 5.2.

Run with Windows Blender --background --factory-startup --python <this file>.
Geometry is authored in metres, X right / -Y forward / Z up. The FBX export
bakes the conversion to Y up / +Z facing. No external Python packages needed.
"""
from pathlib import Path
import bpy
import bmesh
import hashlib
import json
import math
import sys
from mathutils import Vector

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'Art/Models/Props'
EXPORT = REPO / 'Assets/Art/Models/Props'
PREVIEWS = SOURCE / 'Previews'
PALETTE = {
    'M_HullNavy': '#173F57', 'M_SafetyOrange': '#E36A35',
    'M_RailIvory': '#F3F0DC', 'M_Rope': '#D1AF76',
    'M_Steel': '#8FA6AC', 'M_Rubber': '#28343B',
    'M_SeaTeal': '#168F9F', 'M_BandIvory': '#F3DEA1',
}
MATERIALS = {}


def linear_colour(value):
    rgb = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in rgb) + (1,)


def material(name, colour, roughness=.72):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    rgba = linear_colour(colour)
    mat.diffuse_color = rgba
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = rgba
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = 0
    return mat


class Geometry:
    """Small deterministic mesh builder; all transforms are in vertex data."""
    def __init__(self):
        self.vertices, self.faces, self.colours = [], [], []

    def add(self, vertices, faces, colour):
        offset = len(self.vertices)
        self.vertices.extend(tuple(v) for v in vertices)
        self.faces.extend(tuple(i + offset for i in f) for f in faces)
        self.colours.extend([colour] * len(faces))

    def box(self, centre, size, colour):
        c = Vector(centre)
        sx, sy, sz = [v / 2 for v in size]
        v = [c + Vector((x * sx, y * sy, z * sz))
             for z in (-1, 1) for y in (-1, 1) for x in (-1, 1)]
        self.add(v, [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4),
                     (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)], colour)

    def beam(self, start, end, width, depth, colour, chamfer=0):
        a, b = Vector(start), Vector(end)
        tangent = (b - a).normalized()
        helper = Vector((0, 0, 1)) if abs(tangent.z) < .9 else Vector((0, 1, 0))
        u = helper.cross(tangent).normalized()
        v = tangent.cross(u).normalized()
        w, d = width / 2, depth / 2
        if chamfer:
            t = min(chamfer, w * .8, d * .8)
            profile = [(-w + t, -d), (w - t, -d), (w, -d + t), (w, d - t),
                       (w - t, d), (-w + t, d), (-w, d - t), (-w, -d + t)]
        else:
            profile = [(-w, -d), (w, -d), (w, d), (-w, d)]
        n = len(profile)
        verts = [p + u * x + v * y for p in (a, b) for x, y in profile]
        faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
        faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
        self.add(verts, faces, colour)

    def tube(self, path, radii, sides, colour):
        path = [Vector(v) for v in path]
        verts = []
        for j, p in enumerate(path):
            tangent = (path[min(j + 1, len(path) - 1)] - path[max(j - 1, 0)]).normalized()
            helper = Vector((0, 0, 1)) if abs(tangent.z) < .9 else Vector((0, 1, 0))
            u = helper.cross(tangent).normalized()
            v = tangent.cross(u).normalized()
            verts += [p + radii[j] * (u * math.cos(i * math.tau / sides) +
                                      v * math.sin(i * math.tau / sides)) for i in range(sides)]
        faces = [tuple(reversed(range(sides))), tuple(range((len(path) - 1) * sides, len(path) * sides))]
        for j in range(len(path) - 1):
            faces += [(j * sides + i, j * sides + (i + 1) % sides,
                       (j + 1) * sides + (i + 1) % sides, (j + 1) * sides + i) for i in range(sides)]
        self.add(verts, faces, colour)

    def ellipsoid(self, centre, radii, segments, rings, colour):
        # XY normalisation guarantees the requested diameter with an even segment count.
        angles = [math.pi * (j + 1) / (rings + 1) for j in range(rings)]
        radial_max = max(math.sin(a) for a in angles)
        c = Vector(centre)
        verts = [c + Vector((0, 0, radii[2]))]
        for a in angles:
            verts += [c + Vector((radii[0] * math.sin(a) / radial_max * math.cos(i * math.tau / segments),
                                 radii[1] * math.sin(a) / radial_max * math.sin(i * math.tau / segments),
                                 radii[2] * math.cos(a))) for i in range(segments)]
        verts.append(c + Vector((0, 0, -radii[2])))
        faces = [(0, 1 + i, 1 + (i + 1) % segments) for i in range(segments)]
        for j in range(rings - 1):
            first = 1 + j * segments
            faces += [(first + i, first + segments + i,
                       first + segments + (i + 1) % segments,
                       first + (i + 1) % segments) for i in range(segments)]
        last = 1 + (rings - 1) * segments
        faces += [(len(verts) - 1, last + (i + 1) % segments, last + i) for i in range(segments)]
        self.add(verts, faces, colour)

    def ico(self, centre, radius, colour):
        t = (1 + math.sqrt(5)) / 2
        vertices = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
                    (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
                    (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
        faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
                 (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
                 (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
                 (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
        self.add([Vector(centre) + Vector(v).normalized() * radius for v in vertices], faces, colour)

    def extrude_polygon(self, polygon, z_low, z_high, colour):
        n = len(polygon)
        vertices = [(x, y, z) for z in (z_low, z_high) for x, y in polygon]
        faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
        faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
        self.add(vertices, faces, colour)

    def rectangle_ring(self, width, depth, wall, z0, z1, corner, colour):
        def loop(w, d, r, z):
            w, d = w / 2, d / 2
            return [(-w + r, -d, z), (w - r, -d, z), (w, -d + r, z), (w, d - r, z),
                    (w - r, d, z), (-w + r, d, z), (-w, d - r, z), (-w, -d + r, z)]
        verts = loop(width, depth, corner, z0) + loop(width, depth, corner, z1)
        verts += loop(width - 2 * wall, depth - 2 * wall, max(corner - wall / 2, .002), z0)
        verts += loop(width - 2 * wall, depth - 2 * wall, max(corner - wall / 2, .002), z1)
        faces = []
        for i in range(8):
            j = (i + 1) % 8
            faces += [(i, j, j + 8, i + 8), (i + 16, i + 24, j + 24, j + 16),
                      (i + 8, j + 8, j + 24, i + 24), (i, i + 16, j + 16, j)]
        self.add(verts, faces, colour)

    def strap(self, centre, radius_x, radius_z, thickness, width, colour):
        # Eight-sided closed band around XZ, with width along the claw's Y axis.
        cx, cy, cz = centre
        verts = []
        for inner, y in ((False, cy - width / 2), (False, cy + width / 2),
                         (True, cy - width / 2), (True, cy + width / 2)):
            rx, rz = radius_x - (thickness if inner else 0), radius_z - (thickness if inner else 0)
            verts += [(cx + rx * math.cos(i * math.tau / 8), y,
                       cz + rz * math.sin(i * math.tau / 8)) for i in range(8)]
        faces = []
        for i in range(8):
            j = (i + 1) % 8
            faces += [(i, j, j + 8, i + 8), (i + 16, i + 24, j + 24, j + 16),
                      (i, i + 16, j + 16, j), (i + 8, j + 8, j + 24, i + 24)]
        self.add(verts, faces, colour)

    def torus(self, centre, major, minor, colour):
        cx, cy, cz = centre
        verts = [(cx + (major + minor * math.cos(j * math.tau / 4)) * math.cos(i * math.tau / 8),
                  cy + minor * math.sin(j * math.tau / 4),
                  cz + (major + minor * math.cos(j * math.tau / 4)) * math.sin(i * math.tau / 8))
                 for i in range(8) for j in range(4)]
        self.add(verts, [(i * 4 + j, ((i + 1) % 8) * 4 + j,
                         ((i + 1) % 8) * 4 + (j + 1) % 4, i * 4 + (j + 1) % 4)
                        for i in range(8) for j in range(4)], colour)

    def merge(self, other, offset=(0, 0, 0), scale=1):
        base = len(self.vertices)
        self.vertices += [tuple(Vector(v) * scale + Vector(offset)) for v in other.vertices]
        self.faces += [tuple(base + i for i in face) for face in other.faces]
        self.colours += other.colours

    def object(self, name, parent, collection):
        mesh = bpy.data.meshes.new(name + '_Mesh')
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.update()
        for name_key in PALETTE:
            mesh.materials.append(MATERIALS[name_key])
        indices = {key: i for i, key in enumerate(PALETTE)}
        for polygon, colour in zip(mesh.polygons, self.colours):
            polygon.material_index = indices[colour]
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        obj.parent = parent
        return obj


def crab_geometry():
    g = Geometry()
    g.ellipsoid((0, 0, .056), (.075, .09, .033), 16, 4, 'M_SafetyOrange')
    g.ellipsoid((0, -.005, .032), (.066, .076, .017), 10, 3, 'M_BandIvory')
    for side in (-1, 1):
        for i, y in enumerate((-.050, -.014, .025, .062)):
            g.tube([(side * .060, y, .041), (side * (.102 + .005 * (i % 2)), y + .010, .035),
                    (side * .141, y + .016 + i * .003, .006)], [.014, .011, .004], 5, 'M_SafetyOrange')
        g.tube([(side * .056, -.047, .043), (side * .087, -.076, .034),
                (side * .09, -.105, .042)], [.013, .012, .014], 5, 'M_SafetyOrange')
        g.ellipsoid((side * .09, -.105, .040), (.029, .026, .022), 8, 3, 'M_SafetyOrange')
        for poly in ([(.099, -.111), (.115, -.125), (.111, -.148), (.091, -.157), (.095, -.139)],
                     [(.079, -.114), (.069, -.129), (.078, -.150), (.09, -.157), (.087, -.136)]):
            g.extrude_polygon([(side * x, y) for x, y in poly], .026, .052, 'M_SafetyOrange')
        g.ellipsoid((side * .027, -.084, .061), (.007, .007, .007), 8, 2, 'M_Rubber')
    # Exactly 0.28 m across legs, with the requested 0.18 m shell length unchanged.
    extent = max(v[0] for v in g.vertices) - min(v[0] for v in g.vertices)
    centre_x = (max(v[0] for v in g.vertices) + min(v[0] for v in g.vertices)) / 2
    centre_y = (max(v[1] for v in g.vertices) + min(v[1] for v in g.vertices)) / 2
    g.vertices = [((x - centre_x) * .28 / extent, y - centre_y, z) for x, y, z in g.vertices]
    bottom = min(v[2] for v in g.vertices)
    g.vertices = [(x, y, z - bottom) for x, y, z in g.vertices]
    return g, .28 / extent, bottom, (-centre_x * .28 / extent, -centre_y)


def crab_bands(x_scale, bottom, offset):
    g = Geometry()
    for side in (-1, 1):
        g.strap((side * .09 * x_scale + offset[0], -.137 + offset[1], .039 - bottom),
                .030 * x_scale, .021, .0035, .014, 'M_BandIvory')
    return g


def cargo_crab():
    g = Geometry()
    g.ellipsoid((0, 0, .042), (.068, .065, .026), 8, 2, 'M_SafetyOrange')
    for side in (-1, 1):
        for y in (-.045, -.015, .018, .047):
            g.tube([(side * .05, y, .034), (side * .125, y + .012, .005)],
                   [.009, .003], 3, 'M_SafetyOrange')
        g.ellipsoid((side * .07, -.076, .029), (.024, .03, .018), 8, 2, 'M_SafetyOrange')
    return g


def pot_geometry():
    g = Geometry()
    x, y, radius = .338, .263, .012
    for z in (.012, .334):
        for sign in (-1, 1):
            g.beam((-.325, sign * y, z), (.325, sign * y, z), .022, .022, 'M_HullNavy', .005)
            g.beam((sign * x, -.250, z), (sign * x, .250, z), .022, .022, 'M_HullNavy', .005)
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.beam((sx * x, sy * y, .012), (sx * x, sy * y, .338), .022, .022, 'M_HullNavy', .005)
            g.beam((sx * .335, sy * .260, .318), (sx * .335, sy * .260, .350),
                   .030, .030, 'M_HullNavy', .005)
            g.box((sx * .335, sy * .260, .015), (.030, .030, .030), 'M_HullNavy')
    # Coarse closed solid lattice rather than texture/alpha planes or dense netting.
    for sy in (-1, 1):
        for a in (-.225, -.075, .075, .225):
            g.beam((a, sy * y, .025), (a, sy * y, .325), .006, .006, 'M_Steel')
        for z in (.115, .230):
            g.beam((-.325, sy * y, z), (.325, sy * y, z), .006, .006, 'M_Steel')
    for sx in (-1, 1):
        for a in (-.15, 0, .15):
            g.beam((sx * x, a, .025), (sx * x, a, .325), .006, .006, 'M_Steel')
        for z in (.115, .230):
            g.beam((sx * x, -.25, z), (sx * x, .25, z), .006, .006, 'M_Steel')
    for a in (-.225, -.075, .075, .225):
        g.beam((a, -.25, .338), (a, .25, .338), .006, .006, 'M_Steel')
    for a in (-.15, 0, .15):
        g.beam((-.325, a, .338), (.325, a, .338), .006, .006, 'M_Steel')
    for a in (-.10, .10):
        g.beam((-.325, a, .012), (.325, a, .012), .006, .006, 'M_Steel')
    g.beam((-.035, -.266, .295), (.035, -.266, .295), .018, .038, 'M_SeaTeal', .003)
    g.box((0, -.275 + .004, .294), (.018, .006, .008), 'M_Rubber')
    for sx in (-1, 1):
        g.box((sx * .20, .263, .334), (.025, .022, .012), 'M_SeaTeal')
        # Small cream lashings stay within the agreed outside dimensions.
        for sy in (-1, 1):
            g.beam((sx * .245, sy * .252, .328), (sx * .245, sy * .252, .350),
                   .012, .010, 'M_Rope')
    return g


def crate_geometry():
    g = Geometry()
    g.box((0, 0, .012), (.425, .295, .024), 'M_HullNavy')
    g.rectangle_ring(.44, .31, .017, .025, .070, .014, 'M_HullNavy')
    g.rectangle_ring(.44, .31, .017, .180, .225, .014, 'M_HullNavy')
    g.rectangle_ring(.45, .32, .022, .225, .250, .018, 'M_RailIvory')
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.box((sx * .207, sy * .142, .125), (.023, .024, .20), 'M_HullNavy')
    for sy in (-1, 1):
        for x in (-.14, -.045, .045, .14):
            g.box((x, sy * .148, .125), (.022, .014, .11), 'M_HullNavy')
    for sx in (-1, 1):
        for y in (-.065, .065):
            g.box((sx * .211, y, .125), (.014, .023, .11), 'M_HullNavy')
    return g


def buoy_geometry():
    g = Geometry()
    rings = [(0, .025), (.035, .087), (.09, .119), (.13, .125),
             (.21, .116), (.275, .077), (.315, .027)]
    n = 12
    verts = [(r * math.cos(i * math.tau / n), r * math.sin(i * math.tau / n), z)
             for z, r in rings for i in range(n)]
    g.add(verts, [tuple(reversed(range(n))), tuple(range((len(rings) - 1) * n, len(rings) * n))], 'M_SafetyOrange')
    for j in range(len(rings) - 1):
        colour = 'M_RailIvory' if .10 <= (rings[j][0] + rings[j + 1][0]) / 2 <= .19 else 'M_SafetyOrange'
        # Reuse vertices already inserted above; add faces directly.
        for i in range(n):
            g.faces.append((j * n + i, j * n + (i + 1) % n,
                            (j + 1) * n + (i + 1) % n, (j + 1) * n + i))
            g.colours.append(colour)
    g.torus((0, 0, .341), .028, .011, 'M_HullNavy')
    g.tube([(.020, -.010, .342), (.040, -.014, .325), (.047, -.014, .300), (.037, -.012, .284)],
           [.008, .008, .007, .004], 4, 'M_Rope')
    return g


def mesh_stats(obj):
    obj.data.calc_loop_triangles()
    bounds = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    return {
        'name': obj.name, 'triangles': len(obj.data.loop_triangles),
        'vertices': len(obj.data.vertices),
        'bounds_min_blender': [min(v[i] for v in bounds) for i in range(3)],
        'bounds_max_blender': [max(v[i] for v in bounds) for i in range(3)],
        'mesh_sha256': hashlib.sha256(json.dumps({
            'vertices': [[round(x, 8) for x in v.co] for v in obj.data.vertices],
            'faces': [list(p.vertices) for p in obj.data.polygons],
        }, separators=(',', ':')).encode()).hexdigest(),
        'materials': sorted({obj.data.materials[p.material_index].name for p in obj.data.polygons}),
    }


def preview_stage(scene, asset_objects):
    collection = bpy.data.collections.new('PREVIEW_ONLY_NOT_EXPORTED')
    scene.collection.children.link(collection)
    mins = [min(mesh_stats(o)['bounds_min_blender'][i] for o in asset_objects) for i in range(3)]
    maxs = [max(mesh_stats(o)['bounds_max_blender'][i] for o in asset_objects) for i in range(3)]
    target = Vector((0, 0, (maxs[2] + mins[2]) * .48))
    yaw, elevation = math.radians(35), math.radians(45)
    direction = Vector((math.sin(yaw) * math.cos(elevation),
                        -math.cos(yaw) * math.cos(elevation), math.sin(elevation)))
    cam_data = bpy.data.cameras.new('Preview_Orthographic')
    cam_data.type = 'ORTHO'
    camera = bpy.data.objects.new('Preview_Orthographic', cam_data)
    collection.objects.link(camera)
    camera.location = target + direction * 3
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    projected = [camera.matrix_world.inverted() @ (o.matrix_world @ Vector(p))
                 for o in asset_objects for p in o.bound_box]
    cam_data.ortho_scale = max(max(v[i] for v in projected) - min(v[i] for v in projected)
                               for i in (0, 1)) * 1.30
    scene.camera = camera
    ground = Geometry()
    ground.box((0, 0, -.009), (200, 200, .016), 'M_RailIvory')
    floor = ground.object('Preview_Ground', None, collection)
    floor.data.materials.clear()
    floor.data.materials.append(material('M_PreviewCream', '#F4EFE3'))
    for p in floor.data.polygons:
        p.material_index = 0
    for name, location, energy, size in (
            ('Preview_Key', (-2.5, -3, 4), 180, 3),
            ('Preview_Fill', (3, 1, 3), 70, 4)):
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.shape, data.size = energy, 'DISK', size
        light = bpy.data.objects.new(name, data)
        collection.objects.link(light)
        light.location = location
        light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    world = bpy.data.worlds.new('Preview_Cream_World')
    world.use_nodes = True
    background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    background.inputs['Color'].default_value = linear_colour('#F4EFE3')
    background.inputs['Strength'].default_value = .35
    scene.world = world
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1


def build_one(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    scene.unit_settings.length_unit = 'METERS'
    MATERIALS.clear()
    MATERIALS.update({key: material(key, value) for key, value in PALETTE.items()})
    asset_collection = bpy.data.collections.new('ASSET_EXPORT')
    scene.collection.children.link(asset_collection)
    root = bpy.data.objects.new('Catchline_' + name, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = .05
    root['source_forward'] = '-Y'
    root['unity_forward'] = '+Z'
    root['units'] = 'metres'
    asset_collection.objects.link(root)
    if name in ('Crab', 'BandedCrab'):
        geo, x_scale, bottom, offset = crab_geometry()
        body = geo.object('CrabBody', root, asset_collection)
        body['shell_length_metres'] = .18
        if name == 'BandedCrab':
            crab_bands(x_scale, bottom, offset).object('ClawBands', root, asset_collection)
    elif name in ('EmptyPot', 'FullPot'):
        body = pot_geometry().object('PotBody', root, asset_collection)
        if name == 'FullPot':
            cargo = Geometry()
            small = cargo_crab()
            for x, y in ((-.20, -.07), (0, .06), (.20, -.06)):
                cargo.merge(small, (x, y, .0232), .70)
            cargo.object('CrabLoad', root, asset_collection)
    elif name == 'Crate':
        crate_geometry().object('CrateBody', root, asset_collection)
    elif name == 'Buoy':
        buoy_geometry().object('BuoyBody', root, asset_collection)
    bpy.context.view_layer.update()
    meshes = [o for o in asset_collection.objects if o.type == 'MESH']
    parts = [mesh_stats(o) for o in meshes]
    triangles = sum(p['triangles'] for p in parts)
    limit = {'Crab': 800, 'BandedCrab': 800, 'EmptyPot': 1500,
             'FullPot': 1500, 'Crate': 400, 'Buoy': 300}[name]
    assert triangles <= limit, (name, triangles, limit)
    low = [min(p['bounds_min_blender'][i] for p in parts) for i in range(3)]
    high = [max(p['bounds_max_blender'][i] for p in parts) for i in range(3)]
    dims = [high[i] - low[i] for i in range(3)]
    expected = {'EmptyPot': (.70, .55, .35), 'FullPot': (.70, .55, .35),
                'Crate': (.45, .32, .25), 'Buoy': (.25, .25, .38)}
    if name in expected:
        assert all(abs(a - b) < 1e-6 for a, b in zip(dims, expected[name])), (name, dims)
    else:
        assert abs(dims[0] - .28) < 1e-6
    assert abs(low[2]) < 1e-6, (name, low)
    assert abs(low[0] + high[0]) < 1e-6 and abs(low[1] + high[1]) < 1e-6, (name, low, high)
    for o in asset_collection.objects:
        assert o.location.length < 1e-8 and Vector(o.rotation_euler).length < 1e-8
        assert all(abs(v - 1) < 1e-8 for v in o.scale)
    preview_stage(scene, meshes)
    bpy.ops.object.select_all(action='DESELECT')
    for o in asset_collection.objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    fbx = EXPORT / (name + '.fbx')
    bpy.ops.export_scene.fbx(
        filepath=str(fbx), use_selection=True, object_types={'MESH', 'EMPTY'},
        global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
        axis_forward='-Z', axis_up='Y', use_space_transform=True, bake_space_transform=True,
        use_mesh_modifiers=True, use_triangles=True, mesh_smooth_type='FACE',
        add_leaf_bones=False, bake_anim=False, use_custom_props=True,
        path_mode='AUTO', embed_textures=False)
    scene.render.filepath = str(PREVIEWS / (name + '.png'))
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / (name + '.blend')), check_existing=False)
    bpy.ops.render.render(write_still=True)
    result = {'prop': name, 'triangles': triangles, 'budget': limit,
              'dimensions_width_depth_height_m': [round(v, 8) for v in dims],
              'bounds_min_blender': low, 'bounds_max_blender': high, 'parts': parts,
              'source': f'Art/Models/Props/{name}.blend',
              'fbx': f'Assets/Art/Models/Props/{name}.fbx',
              'preview': f'Art/Models/Props/Previews/{name}.png'}
    print('CATCHLINE_PROP', json.dumps(result), flush=True)
    return result


def main():
    assert bpy.app.version[:2] == (5, 2), bpy.app.version_string
    for folder in (SOURCE, EXPORT, PREVIEWS):
        folder.mkdir(parents=True, exist_ok=True)
    arguments = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    names = arguments or ['Crab', 'BandedCrab', 'EmptyPot', 'FullPot', 'Crate', 'Buoy']
    output = [build_one(name) for name in names]
    path = SOURCE / 'build-metrics.json'
    existing = json.loads(path.read_text()) if path.exists() else {'blender_version': bpy.app.version_string, 'props': []}
    indexed = {p['prop']: p for p in existing['props']}
    indexed.update({p['prop']: p for p in output})
    existing['props'] = list(indexed.values())
    existing['palette_srgb'] = PALETTE
    path.write_text(json.dumps(existing, indent=2) + '\n')


if __name__ == '__main__':
    main()

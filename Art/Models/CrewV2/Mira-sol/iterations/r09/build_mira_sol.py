"""MIRA-3D Sol. Reproducible geometry, unchanged CrewRig/actions, headless review.

Blender 5.2 --background --factory-startup --python build_mira_sol.py --
    --render quick|all|none --samples 32 --revision r01
Only writes Art/Models/CrewV2/Mira-sol. No Unity/Assets dependencies.
"""
import argparse
import bpy
import bmesh
import hashlib
import json
import math
import sys
import struct
import zlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Art/Models/CrewV2/Mira-sol'
ORIGINAL = ROOT / 'Art/Models/CrewRig/CrewRig.blend'
parser = argparse.ArgumentParser()
parser.add_argument('--render', choices=['quick', 'all', 'none'], default='quick')
parser.add_argument('--samples', type=int, default=32)
parser.add_argument('--revision', default='r01')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT.mkdir(parents=True, exist_ok=True)
PRE = OUT / 'iterations' / args.revision
PRE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0


def curves(action):
    return list(action.layers[0].strips[0].channelbag(action.slots[0]).fcurves)


def signature(arm):
    bones = {b.name: {'parent': b.parent.name if b.parent else None,
                     'head': list(b.head_local), 'tail': list(b.tail_local),
                     'matrix': [list(r) for r in b.matrix_local],
                     'deform': b.use_deform} for b in arm.data.bones}
    actions = {}
    for a in bpy.data.actions:
        channels = [(f.data_path, f.array_index,
                     [(tuple(p.co), p.interpolation, tuple(p.handle_left),
                       tuple(p.handle_right)) for p in f.keyframe_points])
                    for f in curves(a)]
        actions[a.name] = {'range': list(a.frame_range), 'curves': len(channels),
                           'sha256': hashlib.sha256(json.dumps(channels, sort_keys=True).encode()).hexdigest()}
    return {'bones': bones, 'actions': actions}


bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL))
scene = bpy.context.scene
arm = bpy.data.objects['CrewRig']
baseline = signature(arm)
original_hash = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
(OUT/'rig-contract.json').write_text(json.dumps({'original_sha256': original_hash, **baseline}, indent=2)+'\n')
for action in bpy.data.actions:
    action.use_fake_user = True
for ob in list(bpy.data.objects):
    if ob != arm:
        bpy.data.objects.remove(ob, do_unlink=True)
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.render.fps = 24
arm.animation_data.action = None
for p in arm.pose.bones:
    p.matrix_basis.identity()
bpy.context.view_layer.update()
col = arm.users_collection[0]
col.name = 'MIRA_EXPORT'

PALETTE = {
    'M_HullNavy': '#173F57', 'M_HullBlue': '#2A6685',
    'M_RailIvory': '#F3F0DC', 'M_OilskinYellow': '#E6AD38',
    'M_Rubber': '#28343B', 'M_Steel': '#8FA6AC',
    'M_SkinMira': '#F29A52', 'M_SkinMiraShadow': '#CE7B47',
    'M_HairMira': '#48271D', 'M_HairMiraLight': '#633727',
    'M_HairMiraDeep': '#321E19', 'M_EyeMira': '#07141F',
    'M_CoatMira': '#103F70', 'M_CoatMiraEdge': '#225681',
    'M_VisorMira': '#102D4A', 'M_BrassMira': '#DF9A24',
    'M_BrassMiraLight': '#F7C754', 'M_LeatherMira': '#74472C',
    'M_BinocularMira': '#213343', 'M_LensMira': '#168FBE',
    'M_LensMiraLight': '#51C9E5', 'M_SoleMira': '#142B3C',
}


def linear(c):
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


mats = {}
for name, hx in PALETTE.items():
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    rgb = tuple(linear(int(hx[i:i+2], 16) / 255) for i in (1, 3, 5))
    mat.diffuse_color = (*rgb, 1)
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = .78
    bs.inputs['Specular IOR Level'].default_value = .22
    if 'Brass' in name:
        bs.inputs['Metallic'].default_value = .38
        bs.inputs['Roughness'].default_value = .31
    if name == 'M_EyeMira':
        bs.inputs['Roughness'].default_value = .36
        bs.inputs['Specular IOR Level'].default_value = .16
    if 'Lens' in name:
        bs.inputs['Roughness'].default_value = .2
        bs.inputs['Metallic'].default_value = .25
    if 'HairMira' in name:
        bs.inputs['Roughness'].default_value = .57
        bs.inputs['Specular IOR Level'].default_value = .27
    mats[name] = mat


class Mesh:
    def __init__(self):
        self.v, self.f, self.mi, self.w = [], [], [], []
        self.materials = []
        self.quality = .80

    def add(self, verts, faces, mat, bone, weights=None):
        n = len(self.v)
        if mat not in self.materials:
            self.materials.append(mat)
        self.v.extend([tuple(v) for v in verts])
        self.f.extend([tuple(n+i for i in f) for f in faces])
        self.mi.extend([self.materials.index(mat)] * len(faces))
        self.w.extend(weights if weights else [{bone: 1.0} for _ in verts])

    def ell(self, c, r, mat, bone, seg=16, rings=8, rot=0):
        seg = max(10, round(seg*self.quality))
        rings = max(6, round(rings*self.quality))
        # Single pole vertices: no degenerate triangles or disconnected normals.
        v = [(c[0], c[1], c[2]+r[2])]
        for j in range(1, rings):
            a = math.pi * j / rings
            for i in range(seg):
                t = math.tau * i / seg
                x, y = r[0]*math.sin(a)*math.cos(t), r[1]*math.sin(a)*math.sin(t)
                v.append((c[0]+x*math.cos(rot)-y*math.sin(rot),
                          c[1]+x*math.sin(rot)+y*math.cos(rot), c[2]+r[2]*math.cos(a)))
        v.append((c[0], c[1], c[2]-r[2]))
        f = [(0, 1+i, 1+(i+1) % seg) for i in range(seg)]
        for j in range(rings-2):
            for i in range(seg):
                a, b = 1+j*seg+i, 1+j*seg+(i+1) % seg
                f.append((a, b, b+seg, a+seg))
        f += [(len(v)-1, 1+(rings-2)*seg+(i+1) % seg,
               1+(rings-2)*seg+i) for i in range(seg)]
        self.add(v, f, mat, bone)

    def sweep(self, path, radii, mat, bone, sides=8, up=(0, 1, 0), weights=None):
        path = [Vector(p) for p in path]
        v = []
        for j, p in enumerate(path):
            d = (path[min(j+1, len(path)-1)] - path[max(0, j-1)]).normalized()
            u = Vector(up).cross(d).normalized()
            if u.length < .5:
                u = Vector((1, 0, 0)).cross(d).normalized()
            vv = d.cross(u).normalized()
            rr = radii[j] if isinstance(radii, list) else radii
            rx, ry = rr if isinstance(rr, tuple) else (rr, rr)
            for i in range(sides):
                a = math.tau*i/sides
                v.append(p + rx*math.cos(a)*u + ry*math.sin(a)*vv)
        f = [tuple(reversed(range(sides)))]
        for j in range(len(path)-1):
            for i in range(sides):
                a = j*sides+i
                b = j*sides+(i+1) % sides
                f.append((a, b, b+sides, a+sides))
        f.append(tuple((len(path)-1)*sides+i for i in range(sides)))
        ww = [weights[j] for j in range(len(path)) for _ in range(sides)] if weights else None
        self.add(v, f, mat, bone, ww)

    def patch(self, points, mat, bone, thickness=.003):
        # Closed bevelled tailoring pieces. Convex outline in front projection.
        centre = sum((Vector(p) for p in points), Vector()) / len(points)
        inside = [centre+(Vector(p)-centre)*.86+Vector((0, -thickness, 0)) for p in points]
        n = len(points)
        f = [tuple(range(n, n*2)), tuple(reversed(range(n)))]
        f += [(i, (i+1) % n, (i+1) % n+n, i+n) for i in range(n)]
        self.add(list(points)+inside, f, mat, bone)

    def object(self, name):
        data = bpy.data.meshes.new(name)
        data.from_pydata(self.v, [], self.f)
        for mat in self.materials:
            data.materials.append(mats[mat])
        for p, i in zip(data.polygons, self.mi):
            p.material_index = i
            p.use_smooth = True
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(data)
        bm.free()
        data.update()
        ob = bpy.data.objects.new(name, data)
        col.objects.link(ob)
        ob.parent = arm
        for bone in arm.data.bones:
            ob.vertex_groups.new(name=bone.name)
        for i, w in enumerate(self.w):
            for bone, weight in w.items():
                if weight > 0:
                    ob.vertex_groups[bone].add([i], weight, 'REPLACE')
        mod = ob.modifiers.new('OriginalCrewRig', 'ARMATURE')
        mod.object = arm
        return ob


def catmull(points, steps=3):
    p = [Vector(x) for x in points]
    out = []
    for j in range(len(p)-1):
        a, b, c, d = p[max(0, j-1)], p[j], p[j+1], p[min(j+2, len(p)-1)]
        for k in range(steps):
            t = k/steps
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return out+[p[-1]]


def cord(g, points, r, mat, bone, steps=3, sides=6):
    g.sweep(catmull(points, steps), r, mat, bone, sides)


def lock(g, points, width, depth, light=False, ridge=True):
    p = catmull(points, 5)
    rr = []
    for i in range(len(p)):
        t = i/(len(p)-1)
        taper = min(1, .3+t*5, max(.045, (1-t)*5))
        rr.append((width*taper, depth*taper))
    g.sweep(p, rr, 'M_HairMiraLight' if light else 'M_HairMira', 'Head', 10)
    if ridge:
        # Sculpted broad tonal ridge, following the front of each lock.
        q = [p[i]+Vector((0, -rr[i][1]*.87, .001)) for i in range(len(p))]
        # Two open strips are a broad sculpted groove/highlight, not extra tubes.
        vv = []
        for i, point in enumerate(q):
            vv += [point+Vector((-rr[i][0]*.025, 0, 0)),
                   point+Vector((rr[i][0]*.025, 0, 0))]
        g.add(vv, [(i*2, i*2+1, i*2+3, i*2+2) for i in range(len(q)-1)],
              'M_HairMiraLight', 'Head')


meshes = []
face = Mesh()
face.quality = .85
# Hand-shaped cheek/chin profile: fuller below the eyes, softly tapered chin.
profile = [(.593, .009, .014, .022), (.604, .053, .055, .055),
           (.623, .097, .085, .086), (.645, .128, .111, .108),
           (.675, .151, .131, .125), (.711, .166, .143, .140),
           (.755, .173, .149, .151), (.799, .172, .146, .155),
           (.840, .164, .136, .150), (.877, .146, .118, .132),
           (.909, .116, .090, .104), (.933, .078, .058, .069),
           (.947, .035, .025, .030), (.950, .003, .003, .003)]
verts = []
N = 40
for z, rx, front, back in profile:
    for i in range(N):
        a = math.tau*i/N
        sy = math.sin(a)
        verts.append((rx*math.cos(a), sy*(front if sy < 0 else back), z))
faces = [tuple(reversed(range(N)))]
for j in range(len(profile)-1):
    for i in range(N):
        a, b = j*N+i, j*N+(i+1) % N
        faces.append((a, b, b+N, a+N))
faces.append(tuple((len(profile)-1)*N+i for i in range(N)))
face.add(verts, faces, 'M_SkinMira', 'Head')
face.ell((0, 0, .571), (.053, .045, .055), 'M_SkinMira', 'Neck', 20, 10)
for s in (-1, 1):
    face.ell((s*.167, -.001, .739), (.032, .029, .044), 'M_SkinMira', 'Head', 20, 12)
    face.ell((s*.182, -.022, .739), (.016, .007, .027), 'M_SkinMiraShadow', 'Head', 16, 8)
    face.ell((s*.179, -.028, .732), (.008, .004, .013), 'M_SkinMira', 'Head', 12, 6)
# One softly rounded nose, intersecting well inside the face at its base.
face.ell((-.004, -.142, .729), (.016, .019, .016), 'M_SkinMira', 'Head', 28, 16)
face_ob = face.object('Mira_Face')
# Authored planar skin UV and small colour-only texture: cheeks have the
# portrait's soft blush, with no baked studio light/shadows or copied photo.
tex_size = 512
raw = bytearray()
for py in range(tex_size):
    raw.append(0)
    z = .98-(py+.5)/tex_size*.43
    for px in range(tex_size):
        x = -.21+(px+.5)/tex_size*.42
        blush = max(math.exp(-((x-cx)/.040)**2-((z-.718)/.031)**2)
                    for cx in (-.113, .113))*.42
        warmth = math.exp(-(x/.125)**2-((z-.785)/.13)**2)*.16
        base, rosy, warm = (242, 154, 82), (226, 109, 83), (255, 176, 99)
        raw.extend(int(round((base[i]*(1-warmth)+warm[i]*warmth)*(1-blush)+rosy[i]*blush))
                   for i in range(3))


def png_chunk(kind, data):
    return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data)&0xffffffff)


texture_path = OUT/'Mira_Face.png'
texture_path.write_bytes(b'\x89PNG\r\n\x1a\n'+
    png_chunk(b'IHDR', struct.pack('>IIBBBBB', tex_size, tex_size, 8, 2, 0, 0, 0))+
    png_chunk(b'sRGB', b'\0')+png_chunk(b'IDAT', zlib.compress(bytes(raw), 9))+
    png_chunk(b'IEND', b''))
skin_mat = mats['M_SkinMira'].copy()
skin_mat.name = 'Mira_Face'
image = bpy.data.images.load(str(texture_path), check_existing=True)
node = skin_mat.node_tree.nodes.new('ShaderNodeTexImage')
node.image = image
skin_mat.node_tree.links.new(node.outputs['Color'],
                             skin_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
face_ob.data.materials[face.materials.index('M_SkinMira')] = skin_mat
uv = face_ob.data.uv_layers.new(name='Mira_SkinUV')
for loop in face_ob.data.loops:
    co = face_ob.data.vertices[loop.vertex_index].co
    uv.data[loop.index].uv = ((co.x+.21)/.42, (co.z-.55)/.43)
meshes.append(face_ob)

detail = Mesh()
detail.quality = 1.0


def face_surface(x, z, lift=.0015):
    """Seat expression curves on the actual shaped cheek, including profile slope."""
    for a, b in zip(profile, profile[1:]):
        if a[0] <= z <= b[0]:
            t = (z-a[0])/(b[0]-a[0])
            rx, front = (a[j]*(1-t)+b[j]*t for j in (1, 2))
            return (x, -front*math.sqrt(max(.01, 1-(x/rx)**2))-lift, z)
    raise ValueError((x, z))


for s in (-1, 1):
    # Large portrait eyes are geometry, including the glints: survive FBX/mobile.
    x, y, z = s*.063, -.138, .771
    detail.ell((x, y, z), (.030, .014, .045), 'M_EyeMira', 'Head', 24, 14, s*.22)
    detail.ell((x-.008, y-.0145, z+.018), (.007, .002, .011), 'M_RailIvory', 'Head', 16, 10, s*.22)
    path = catmull([(x-s*.021, -.143, z+.024), (x-s*.009, -.149, z+.040),
                    (x+s*.014, -.145, z+.037), (x+s*.030, -.136, z+.028),
                    (x+s*.038, -.131, z+.036)], 5)
    detail.sweep(path, [.0007+.0022*math.sin(math.pi*i/(len(path)-1))
                        for i in range(len(path))], 'M_EyeMira', 'Head', 8)
    # Tapered arched brows, rather than simple straight bars.
    path = catmull([face_surface(s*x, z, .002) for x, z in
                    [(.027, .821), (.046, .832), (.071, .831), (.092, .822)]], 4)
    detail.sweep(path, [(.004+.004*math.sin(math.pi*i/(len(path)-1)), .0032)
                        for i in range(len(path))], 'M_HairMiraDeep', 'Head', 7)
# Portrait's closed curved smile, asymmetrical lifted right corner.
cord(detail, [face_surface(x, z) for x, z in
              [(-.049, .683), (-.031, .674), (.003, .672), (.036, .682), (.051, .693)]],
     .0024, 'M_HairMiraDeep', 'Head', 4, 8)
detail.ell(face_surface(.049, .692), (.003, .002, .003), 'M_HairMiraDeep', 'Head', 12, 6)
cord(detail, [face_surface(x, z, .0006) for x, z in
              [(-.019, .666), (.003, .663), (.024, .670)]],
     .0011, 'M_SkinMiraShadow', 'Head', 3)
meshes.append(detail.object('Mira_EyesExpression'))

hair = Mesh()
hair.quality = .8
hair.ell((0, .037, .837), (.168, .125, .111), 'M_HairMiraDeep', 'Head', 26, 12)
# Scalp coverage follows the complete rear head, down to the nape. A small
# crown ellipsoid alone leaves exposed skin behind the ears and ponytail.
back_rows = [(.621, .111, .097), (.645, .145, .119),
             (.680, .163, .140), (.720, .175, .153),
             (.765, .180, .163), (.810, .177, .165),
             (.850, .168, .156), (.890, .143, .133),
             (.922, .101, .099), (.942, .042, .048)]
back_n = 33
bv = [(rx*math.cos(-.12+(math.pi+.24)*i/(back_n-1)),
       depth*math.sin(-.12+(math.pi+.24)*i/(back_n-1)), z)
      for z, rx, depth in back_rows for i in range(back_n)]
bf = [(j*back_n+i, j*back_n+i+1, (j+1)*back_n+i+1, (j+1)*back_n+i)
      for j in range(len(back_rows)-1) for i in range(back_n-1)]
hair.add(bv, bf, 'M_HairMira', 'Head')


def hair_loft(rows, sides=16, steps=3, mat='M_HairMira', grooves=()):
    # Flattened sculpted ribbons with fixed horizontal cross sections. Unlike
    # normal-to-path tubes these do not pinch into beads at each wave inflection.
    cols = list(zip(*rows))
    samples = [catmull([(x, 0, 0) for x in values], steps) for values in cols]
    rows = [tuple(sample[i].x for sample in samples) for i in range(len(samples[0]))]
    v = []
    for z, x, y, rx, ry in rows:
        for i in range(sides):
            a = math.tau*i/sides
            # Broad connected strand ridges follow the wavy lock rather than
            # adding floating tube highlights. Subdivision softens the grooves.
            ridge = 1+.055*math.cos(6*a+z*7)
            v.append((x+max(.0001, rx)*math.cos(a)*ridge,
                      y+max(.0001, ry)*math.sin(a)*ridge, z))
    f = [tuple(reversed(range(sides)))]
    for j in range(len(rows)-1):
        for i in range(sides):
            a, b = j*sides+i, j*sides+(i+1) % sides
            f.append((a, b, b+sides, a+sides))
    f.append(tuple((len(rows)-1)*sides+i for i in range(sides)))
    hair.add(v, f, mat, 'Head')
    # Deliberate shallow sculpted grooves, not disconnected floating outlines.
    for fraction in grooves:
        angle = -math.acos(fraction)
        line = [(x+rx*math.cos(angle), y+ry*math.sin(angle)-.0007, z)
                for z, x, y, rx, ry in rows[1:-1]]
        strip = [Vector(p)+Vector((dx, -.0003, 0)) for p in line for dx in (-.0006, .0006)]
        hair.add(strip, [(j*2, j*2+1, j*2+3, j*2+2) for j in range(len(line)-1)],
                 'M_HairMiraDeep', 'Head')


# Broad fringe is swept sideways, tucked below the continuous hat band.
lock(hair, [(-.014, -.099, .880), (-.057, -.137, .870),
            (-.111, -.127, .854), (-.151, -.085, .822)], .026, .013, True)
lock(hair, [(-.005, -.102, .882), (.041, -.139, .872),
            (.092, -.129, .851), (.143, -.081, .840)], .030, .015)
lock(hair, [(.018, -.096, .888), (.060, -.116, .884),
            (.113, -.105, .868), (.151, -.066, .852)], .019, .011, False, False)
# Loose waves either side leave eyes/brows, cheek and hoop earrings visible.
for side in (-1, 1):
    hair_loft([(z, side*x, y, rx, ry) for z, x, y, rx, ry in [
        (.875, .150, .015, .016, .045), (.835, .174, .021, .027, .052),
        (.794, .178, .027, .025, .047), (.756, .172, .029, .030, .043),
        (.720, .184, .031, .028, .039), (.683, .172, .035, .028, .032),
        (.654, .148, .040, .018, .020), (.642, .127, .043, .001, .002)]],
        16, 3, grooves=(-.28, .37))
    hair_loft([(z, side*x, y, rx, ry) for z, x, y, rx, ry in [
        (.868, .140, -.075, .010, .008), (.834, .159, -.098, .016, .016),
        (.802, .148, -.112, .016, .016), (.772, .162, -.102, .017, .015),
        (.738, .148, -.102, .015, .014), (.707, .160, -.091, .016, .013),
        (.679, .154, -.079, .013, .012), (.663, .131, -.070, .001, .001)]],
        14, 3, grooves=(0,))
# A cohesive high ponytail. Its wavy boundary is supported by a continuous
# volume, with two overlapping broad curls rather than a bundle of sausages.
hair.ell((.075, .145, .877), (.068, .057, .066), 'M_HairMira', 'Head', 18, 10)
hair_loft([
    (.947, .086, .152, .003, .004), (.925, .133, .178, .050, .046),
    (.889, .170, .191, .072, .062), (.847, .174, .201, .075, .067),
    (.806, .159, .208, .074, .066), (.765, .170, .207, .078, .064),
    (.724, .164, .204, .079, .064), (.683, .180, .197, .077, .061),
    (.642, .163, .190, .079, .059), (.600, .172, .183, .074, .055),
    (.558, .154, .175, .067, .047), (.520, .150, .163, .052, .035),
    (.488, .120, .151, .029, .023), (.477, .093, .142, .001, .002)],
    22, 2, grooves=(-.45, .12, .60))
for strand_index, rows in enumerate([
    [(.923, .143, .137, .002, .003), (.885, .198, .137, .029, .020),
     (.837, .215, .141, .030, .023), (.791, .199, .145, .031, .022),
     (.745, .222, .143, .028, .021), (.698, .201, .135, .030, .020),
     (.652, .220, .128, .027, .020), (.604, .199, .119, .025, .018),
     (.563, .198, .109, .024, .017), (.534, .175, .104, .001, .001)],
    [(.902, .098, .239, .002, .003), (.855, .117, .258, .030, .018),
     (.812, .139, .267, .030, .021), (.765, .126, .269, .033, .022),
     (.718, .149, .258, .029, .021), (.670, .130, .251, .030, .020),
     (.622, .151, .230, .028, .018), (.575, .133, .218, .025, .017),
     (.532, .140, .190, .021, .015), (.500, .118, .165, .001, .001)]
]):
    hair_loft(rows, 16, 3,
              mat='M_HairMiraLight' if strand_index == 0 else 'M_HairMiraDeep',
              grooves=(.1,))
# Smaller overlapping S curls break the broad ponytail into flowing locks.
# These are part of the skinned opaque hair mesh, not floating render effects.
for strand in range(4):
    rows = []
    for j in range(12):
        t = j/11
        z = .914-.407*t
        wave = math.sin(t*math.tau*1.6+strand*.75)
        x = .130+strand*.020+.020*wave-.025*t*t
        y = (.128 if strand < 2 else .248)-.025*t
        width = .012*math.sin(math.pi*t)**.55+.0005
        rows.append((z, x, y, width, width*.60))
    hair_loft(rows, 12, 3,
              mat='M_HairMiraLight' if strand % 2 == 0 else 'M_HairMira',
              grooves=(0,))
# Flow from the covered rear scalp into the high gathered ponytail, giving the
# rear view deliberate strand direction rather than a plain helmet surface.
for strand in range(5):
    a = math.pi*.22+strand*math.pi*.14
    lock(hair, [(.156*math.cos(a), .145*math.sin(a), .700),
                (.170*math.cos(a), .160*math.sin(a), .775),
                (.147*math.cos(a), .149*math.sin(a), .845),
                (.080, .159, .888)], .009, .006,
         strand % 2 == 0, False)
meshes.append(hair.object('Mira_HairSculpt'))

cap = Mesh()
# Ring crown is tilted/overhanging like the illustration, rather than a sphere.
def cap_ring(z, rx, ry, tilt=0, shift=0):
    return [(rx*math.cos(math.tau*i/40)+shift, ry*math.sin(math.tau*i/40),
             z+tilt*math.cos(math.tau*i/40)) for i in range(40)]

cap_rows = [(.899, .172, .145, .007, 0), (.925, .181, .150, .009, 0),
            (.959, .201, .162, -.009, -.004), (1.006, .208, .164, -.025, -.013),
            (1.053, .180, .139, -.030, -.020), (1.080, .111, .089, -.024, -.026),
            (1.090, .007, .006, 0, -.027)]
cols = list(zip(*cap_rows))
samples = [catmull([(x, 0, 0) for x in values], 3) for values in cols]
smooth_rows = [tuple(sample[i].x for sample in samples) for i in range(len(samples[0]))]
v = [p for row in smooth_rows for p in cap_ring(*row)]
f = []
for j in range(len(smooth_rows)-1):
    for i in range(40):
        a, b = j*40+i, j*40+(i+1) % 40
        f.append((a, b, b+40, a+40))
f.append(tuple(range((len(smooth_rows)-1)*40, len(smooth_rows)*40)))
cap.add(v, f, 'M_CoatMira', 'HatMount')
# Cream continuous hat band, subtly tilted. Its front remains unobstructed.
v = cap_ring(.901, .175, .149, .007)+cap_ring(.925, .182, .154, .009)
cap.add(v, [(i, (i+1) % 40, (i+1) % 40+40, i+40) for i in range(40)],
        'M_RailIvory', 'HatMount')
for z in (.901, .926):
    p = cap_ring(z, .178 if z < .91 else .184, .151 if z < .91 else .156, .007)
    cap.sweep(p+[p[0]], .003, 'M_VisorMira', 'HatMount', 6)
# A broad curved visor, thickness and highlighted leading edge.
vv = []
count = 25
for lower in (False, True):
    for row in (0, 1, 2):
        for i in range(count):
            t = -math.pi*.47 + math.pi*.94*i/(count-1)
            radius = (.145, .191, .225)[row]
            x = math.sin(t)*radius
            y = -math.cos(t)*radius
            z = .901 - .022*(row/2)**1.4 + .031*math.sin(t)**2
            vv.append((x, y, z-(.008 if lower else 0)))
ff = []
for layer in (0, count*3):
    for row in range(2):
        for i in range(count-1):
            a = layer+row*count+i
            ff.append((a, a+1, a+count+1, a+count))
for i in range(count-1):
    a = 2*count+i
    ff.append((a, a+1, a+1+3*count, a+3*count))
cap.add(vv, ff, 'M_VisorMira', 'HatMount')
cap.sweep(vv[2*count:3*count], .0025, 'M_CoatMiraEdge', 'HatMount', 6)
# The crown is clean tailoring; avoid raised seam wires floating above its arc.


def disk(g, c, radius, depth, mat, bone, seg=24):
    # Front-facing disc axis -Y; sweep uses a stable cross section.
    g.sweep([(c[0], c[1]+depth/2, c[2]), (c[0], c[1]-depth/2, c[2])],
            radius, mat, bone, seg, up=(0, 0, 1))


badge_start = len(cap.v)
disk(cap, (0, -.166, .989), .034, .010, 'M_BrassMira', 'HatMount', 32)
disk(cap, (0, -.173, .989), .029, .006, 'M_RailIvory', 'HatMount', 32)
disk(cap, (0, -.177, .989), .0255, .002, 'M_VisorMira', 'HatMount', 32)
disk(cap, (0, -.179, .989), .023, .002, 'M_RailIvory', 'HatMount', 28)
for i in range(8):
    a = math.tau*i/8
    length = .024 if i % 2 == 0 else .016
    dx, dz = math.sin(a), math.cos(a)
    px, pz = math.cos(a)*.005, -math.sin(a)*.005
    centre = Vector((0, -.183, .989))
    points = [centre+Vector((dx*length, 0, dz*length)),
              centre+Vector((px, 0, pz)), centre,
              centre+Vector((-px, 0, -pz))]
    cap.patch(points, 'M_BrassMiraLight' if i % 2 else 'M_BrassMira', 'HatMount', .0007)
disk(cap, (0, -.187, .989), .004, .003, 'M_BrassMiraLight', 'HatMount', 16)
for i in range(badge_start, len(cap.v)):
    x, y, z = cap.v[i]
    cap.v[i] = (x*1.34, y, .989+(z-.989)*1.34)
for s in (-1, 1):
    cap.ell((s*.166, -.066, .915+s*.004), (.010, .005, .010),
            'M_BrassMiraLight', 'HatMount', 16, 8)
meshes.append(cap.object('Mira_OfficerCap'))

body = Mesh()
body.quality = .85
# Coat body: tailored elliptical rings, fuller hem, continuous front and back.
rows = [(.281, .133, .093), (.292, .148, .100), (.337, .144, .105),
        (.398, .139, .104), (.456, .143, .102), (.500, .150, .089),
        (.530, .131, .074), (.548, .066, .049)]
v, w = [], []
for z, rx, ry in rows:
    for i in range(32):
        a = math.tau*i/32
        v.append((rx*math.cos(a), ry*math.sin(a), z))
        t = max(0, min(1, (z-.32)/.19))
        w.append({'Hips': 1-t, 'Spine1': t})
f = [tuple(reversed(range(32)))]
for j in range(len(rows)-1):
    for i in range(32):
        a, b = j*32+i, j*32+(i+1) % 32
        f.append((a, b, b+32, a+32))
f.append(tuple((len(rows)-1)*32+i for i in range(32)))
body.add(v, f, 'M_CoatMira', 'Spine', w)
# The sweater opening is part of the coat's surface, continuous with the neck
# collar. A separate flat bib previously floated well in front of the neckline.
body.materials.append('M_RailIvory')
for j in range(4, len(rows)-1):
    for i in (range(23, 25) if j == 4 else range(22, 26)):
        body.mi[1+j*32+i] = body.materials.index('M_RailIvory')
# Continuous cream collar, rather than intersecting ellipsoid and floating ribs.
collar_rows = [(.512, .069, .058), (.519, .068, .057),
               (.564, .055, .046), (.576, .053, .044)]
cv = [(rx*math.cos(math.tau*i/32), -.014+ry*math.sin(math.tau*i/32), z)
      for z, rx, ry in collar_rows for i in range(32)]
cf = [(j*32+i, j*32+(i+1)%32, (j+1)*32+(i+1)%32, (j+1)*32+i)
      for j in range(len(collar_rows)-1) for i in range(32)]
cf.append(tuple(range(96,128)))
body.add(cv, cf, 'M_RailIvory', 'Spine1')
for i in range(11):
    a = math.pi+.12+(math.pi-.24)*i/10
    rib = [(rx*math.cos(a), -.014+(ry+.0007)*math.sin(a), z)
           for z, rx, ry in collar_rows]
    cord(body, rib, .0011, 'M_RailIvory', 'Spine1', 2, 5)
def coat_surface(x, z, lift=.0025):
    for a, b in zip(rows, rows[1:]):
        if a[0] <= z <= b[0]:
            t = (z-a[0])/(b[0]-a[0])
            rx, ry = (a[i]*(1-t)+b[i]*t for i in (1, 2))
            return (x, -ry*math.sqrt(max(.01, 1-(x/rx)**2))-lift, z)
    return (x, -.052-lift, z)


for s in (-1, 1):
    # Wide pointed layered lapels, pockets and twin brass button columns.
    # Two clean convex panels make the notched lapel without a concave n-gon
    # or the sharp star-shaped triangulation of the earlier pass.
    collar = [coat_surface(s*x, z) for x, z in
              [(.045, .548), (.109, .529), (.113, .499), (.079, .507)]]
    points = [coat_surface(s*x, z) for x, z in
              [(.077, .507), (.102, .488), (.043, .422), (.047, .500)]]
    body.patch(collar, 'M_CoatMira', 'Spine1', .002)
    body.patch(points, 'M_CoatMira', 'Spine1', .002)
    cord(body, [coat_surface(s*x, z, .005) for x, z in
                [(.045, .547), (.079, .506), (.044, .426)]],
         .0011, 'M_CoatMiraEdge', 'Spine1', 2, 5)
    body.patch([(s*.073, -.099, .337), (s*.122, -.069, .345),
                (s*.121, -.071, .331), (s*.071, -.104, .324)],
               'M_CoatMiraEdge', 'Hips', .0018)
    for z in (.330, .380, .431):
        disk(body, (s*.046, -.108 if z < .40 else -.111, z), .008, .006,
             'M_BrassMira', 'Hips' if z < .35 else 'Spine1', 16)
        body.ell((s*.046-.002, -.113 if z < .40 else -.116, z+.002),
                 (.003, .0015, .003), 'M_BrassMiraLight',
                 'Hips' if z < .35 else 'Spine1', 10, 6)
    # T-pose sleeves with blended shoulder and elbow; source actions lower them.
    side = 'Left' if s > 0 else 'Right'
    # One continuous capsule sleeve: a round shoulder and a material cuff,
    # without intersecting shoulder balls or coplanar nested cuff tubes.
    xx = [.086, .094, .110, .13, .15, .17, .20, .23, .25, .265, .28,
          .295, .31, .33, .36, .365, .390]
    rad = [.003, .026, .042, .049, .051, .051, .050, .049, .048, .047,
           .047, .047, .046, .044, .040, .0398, .038]
    ww = []
    for x in xx:
        t = max(0, min(1, (x-.205)/.15))
        t = t*t*(3-2*t)
        ww.append({side+'Arm': 1-t, side+'ForeArm': t})
    sleeve_start = len(body.f)
    body.sweep([(s*x, 0, .51) for x in xx], rad, 'M_CoatMira', side+'Arm', 20,
               up=(0, 0, 1), weights=ww)
    for i in range(sleeve_start+1+(len(xx)-3)*20, len(body.f)):
        body.mi[i] = body.materials.index('M_CoatMiraEdge')
    body.ell((s*.423, -.001, .51), (.043, .038, .037), 'M_SkinMira', side+'Hand', 20, 12)
    body.ell((s*.408, -.032, .485), (.020, .020, .020), 'M_SkinMira', side+'Hand', 16, 8)
    # Trousers with softened joints and seam down the outside.
    zs = [.315, .278, .235, .198, .180, .16, .12, .085]
    rr = [.063, .062, .057, .052, .050, .048, .046, .044]
    lw = []
    for z in zs:
        t = max(0, min(1, (.205-z)/.06))
        lw.append({side+'UpLeg': 1-t, side+'Leg': t})
    body.sweep([(s*.080, 0, z) for z in zs], rr, 'M_CoatMira', side+'UpLeg',
               16, weights=lw)
    # One coherent rubber boot, with a bevelled sole and round toe. No crossing
    # nested ellipsoids: those produced dark polygon-shaped z-fighting patches.
    boot_rows = [(0, -.028, .046, .075), (.008, -.030, .060, .096),
                 (.019, -.032, .065, .103), (.040, -.033, .064, .102),
                 (.065, -.027, .059, .090), (.087, -.010, .049, .065),
                 (.111, 0, .047, .049), (.119, 0, .047, .049)]
    bv = [(s*.085+rx*math.cos(math.tau*i/28), cy+ry*math.sin(math.tau*i/28), z)
          for z, cy, rx, ry in boot_rows for i in range(28)]
    bf = [(j*28+i, j*28+(i+1)%28, (j+1)*28+(i+1)%28, (j+1)*28+i)
          for j in range(len(boot_rows)-1) for i in range(28)]
    bf += [tuple(reversed(range(28))), tuple(range(196,224))]
    boot_face_start = len(body.f)
    body.add(bv, bf, 'M_HullNavy', side+'Foot')
    if 'M_SoleMira' not in body.materials:
        body.materials.append('M_SoleMira')
    for i in range(boot_face_start, boot_face_start+56):
        body.mi[i] = body.materials.index('M_SoleMira')
meshes.append(body.object('Mira_CoatHandsBoots'))

props = Mesh()
# Jewellery is a real open hoop, readable as a hole from portrait view.
for s in (-1, 1):
    path = [(s*.174+.012*math.cos(math.tau*i/28), -.031,
             .704+.019*math.sin(math.tau*i/28)) for i in range(29)]
    props.sweep(path, .003, 'M_BrassMiraLight', 'Head', 7)
    props.ell((s*.174, -.029, .723), (.004, .0035, .004),
              'M_BrassMiraLight', 'Head', 12, 6)
    # Straps follow coat front; shoulder strap loops never intersect the face.
    cord(props, [(s*.049, .016, .550), (s*.070, -.050, .529),
                 (s*.071, -.104, .481), (s*.062, -.126, .446)],
         .0044, 'M_LeatherMira', 'Spine1', 4, 7)
    disk(props, (s*.063, -.131, .447), .008, .004, 'M_BrassMira', 'Spine1', 16)
    # Barrels slope forward toward their large blue objective lenses.
    p0, p1 = Vector((s*.040, -.130, .436)), Vector((s*.046, -.159, .353))
    props.sweep([p0, p0.lerp(p1, .32), p0.lerp(p1, .70), p1],
                [.022, .024, .027, .027], 'M_BinocularMira', 'Spine1', 20)
    for t in (.12, .78, 1.0):
        a = p0.lerp(p1, t)
        d = (p1-p0).normalized()*.004
        props.sweep([a-d, a+d], .028 if t > .5 else .023,
                    'M_BrassMira' if t == .78 else 'M_VisorMira', 'Spine1', 20)
    d = (p1-p0).normalized()
    props.sweep([p1+d*.004, p1+d*.006], .0225, 'M_LensMira', 'Spine1', 24)
    props.ell(tuple(p1+d*.008+Vector((-.007, -.003, .003))),
              (.009, .003, .004), 'M_LensMiraLight', 'Spine1', 16, 6)
props.sweep([(-.042, -.139, .414), (.042, -.139, .414)], .011,
            'M_BinocularMira', 'Spine1', 12, up=(0, 0, 1))
props.sweep([(0, -.133, .419), (0, -.152, .419)], .012,
            'M_VisorMira', 'Spine1', 16, up=(0, 0, 1))
meshes.append(props.object('Mira_JewelleryBinoculars'))

assert signature(arm) == baseline, 'Original rig or actions changed during authoring'
# Spend topology on face/hair first. Collapse redundant curved-surface samples
# before export, in the bind pose; preserve interpolated original bone weights.
budgets = {'Mira_Face': 2300, 'Mira_EyesExpression': 2500,
           'Mira_HairSculpt': 6400, 'Mira_OfficerCap': 2700,
           'Mira_CoatHandsBoots': 4300, 'Mira_JewelleryBinoculars': 1700}
for ob in meshes:
    if ob.name == 'Mira_HairSculpt':
        bpy.context.view_layer.objects.active = ob
        smooth = ob.modifiers.new('SculptSofteningBindPose', 'SUBSURF')
        smooth.levels = 1
        bpy.ops.object.modifier_move_up(modifier=smooth.name)
        bpy.ops.object.modifier_apply(modifier=smooth.name)
    # Commit Blender's triangulation before FBX, eliminating zero-area compass
    # panel triangles rather than relying on the exporter's silent cleanup.
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    tiny = [f for f in bm.faces if f.calc_area() < 1e-12]
    if tiny:
        bmesh.ops.delete(bm, geom=tiny, context='FACES_ONLY')
    bm.normal_update()
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.validate(verbose=False, clean_customdata=False)
    ob.data.calc_loop_triangles()
    before = len(ob.data.loop_triangles)
    if before > budgets[ob.name]:
        bpy.context.view_layer.objects.active = ob
        mod = ob.modifiers.new('BindTopologyBudget', 'DECIMATE')
        mod.ratio = budgets[ob.name]/before
        bpy.ops.object.modifier_move_up(modifier=mod.name)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    # Decimation can itself introduce zero-area faces (notably flat compass
    # diamonds). Clean its final triangles, so source and exported FBX agree.
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    tiny = [f for f in bm.faces if f.calc_area() < 1e-10]
    if tiny:
        bmesh.ops.delete(bm, geom=tiny, context='FACES_ONLY')
    bm.normal_update()
    bm.to_mesh(ob.data)
    bm.free()
    # Compass spokes can create duplicate triangles after collapse. FBX import
    # validates meshes and removes those duplicates; do it explicitly here so
    # the saved source and actual import have identical topology.
    ob.data.validate(verbose=False, clean_customdata=False)
    ob.data.calc_loop_triangles()
    for p in ob.data.polygons:
        p.use_smooth = True
    print('PART TRIANGLES', ob.name, before, len(ob.data.loop_triangles), flush=True)
for ob in meshes:
    ob.data.calc_loop_triangles()
triangles = sum(len(ob.data.loop_triangles) for ob in meshes)
print('MIRA TRIANGLES', triangles, flush=True)
assert triangles <= 20000, triangles
for ob in meshes:
    for v in ob.data.vertices:
        assert v.groups and abs(sum(g.weight for g in v.groups)-1) < 1e-5

# Export precisely the original CrewRig settings, with original animation takes.
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
for ob in meshes:
    ob.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=str(OUT/'Mira.fbx'), use_selection=True,
    object_types={'MESH', 'ARMATURE'}, axis_forward='-Z', axis_up='Y', global_scale=1,
    apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', use_space_transform=True,
    bake_space_transform=False, add_leaf_bones=False, use_armature_deform_only=False,
    bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0,
    use_custom_props=True, mesh_smooth_type='FACE', path_mode='RELATIVE')
arm.animation_data.action = bpy.data.actions['Idle']
scene.frame_set(1)

stats = {'revision': args.revision, 'original_sha256': original_hash,
         'contract': baseline, 'triangles': triangles,
         'meshes': {o.name: len(o.data.loop_triangles) for o in meshes},
         'textures': [{'file': 'Mira_Face.png', 'size': [512, 512],
                       'use': 'authored skin colour/blush; no baked lighting'}],
         'palette_srgb': PALETTE, 'source_axes': 'X right, -Y forward, Z up',
         'bare_scalp_m': max(v.co.z for v in meshes[0].data.vertices),
         'weight_check': 'every vertex normalized, all bound to original CrewRig'}
(OUT/'build-manifest.json').write_text(json.dumps(stats, indent=2)+'\n')

# Neutral review studio, kept out of FBX; Standard display preserves palette hue.
studio = bpy.data.collections.new('REVIEW_STUDIO_not_exported')
scene.collection.children.link(studio)


def studio_object(ob):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    studio.objects.link(ob)
    return ob


def area(name, location, energy, size, colour):
    light = bpy.data.lights.new(name, 'AREA')
    light.energy, light.shape, light.size, light.color = energy, 'DISK', size, colour
    ob = bpy.data.objects.new(name, light)
    studio.objects.link(ob)
    ob.location = location
    ob.rotation_euler = (Vector((0, 0, .65))-ob.location).to_track_quat('-Z', 'Y').to_euler()


scene.render.engine = 'CYCLES'
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    available = [d for d in prefs.devices if d.type == 'OPTIX']
    if available:
        for d in prefs.devices:
            d.use = d.type == 'OPTIX'
        scene.cycles.device = 'GPU'
        print('RENDER DEVICE', [(d.name, d.type) for d in available], flush=True)
except Exception as exc:
    print('CPU fallback', str(exc), flush=True)
scene.world.color = (.35, .35, .35)
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.43, .47, .53, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45
area('Warm portrait key', (-2, -3, 4), 220, 3.0, (1, .93, .83))
area('Cool broad fill', (3, -1, 2.0), 90, 2.8, (.83, .91, 1))
area('Hair rim', (1, 2, 3), 160, 2.5, (1, .92, .80))
floor = Mesh()
# Use a regular plane for shadow receiving; independent of the export mesh builder.
data = bpy.data.meshes.new('ReviewFloor')
data.from_pydata([(-200, -200, -.004), (200, -200, -.004), (200, 200, -.004), (-200, 200, -.004)], [], [(0, 1, 2, 3)])
ground = bpy.data.objects.new('ReviewFloor', data)
studio.objects.link(ground)
mat = bpy.data.materials.new('Review neutral warm grey')
mat.diffuse_color = (.48, .46, .42, 1)
mat.use_nodes = True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.48, .46, .42, 1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .85
data.materials.append(mat)
camera = bpy.data.objects.new('ReviewCamera', bpy.data.cameras.new('ReviewCamera'))
studio.objects.link(camera)
scene.camera = camera
camera.data.type = 'ORTHO'
camera.data.lens = 55
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.resolution_percentage = 100


def shot(name, angle=0, target=(0, 0, .535), scale=1.19, size=(768, 896),
         action='Idle', frame=1, elevated=.12):
    arm.animation_data.action = bpy.data.actions[action]
    scene.frame_set(frame)
    a = math.radians(angle)
    target = Vector(target)
    camera.location = target+Vector((math.sin(a)*3.4, -math.cos(a)*3.4, elevated))
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = scale
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(PRE/(name+'.png'))
    bpy.ops.render.render(write_still=True)


# Save a useful camera as well as the exact unchanged Idle pose.
camera_target = Vector((0, 0, .535))
camera.location = camera_target+Vector((math.sin(math.radians(27))*3.4,
                                      -math.cos(math.radians(27))*3.4, .22))
camera.rotation_euler = (camera_target-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = 1.19
scene.render.resolution_x, scene.render.resolution_y = 768, 896
image.filepath = '//Mira_Face.png'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Mira.blend'), relative_remap=False)
if args.render != 'none':
    shot('three-quarter', 27, elevated=.22)
    shot('face', 18, (0, -.018, .818), .59, (1024, 1024), elevated=.03)
if args.render == 'all':
    shot('front', 0)
    shot('side', 90)
    shot('back', 180)
    shot('idle', 22, action='Idle', frame=13)
    shot('walk', 22, action='Walk', frame=7)
    # Current original captain, same unmodified rig scale and the same Idle pose.
    with bpy.data.libraries.load(str(ORIGINAL), link=False) as (source, dest):
        dest.objects = ['CrewRig', 'Body', 'Outfit_Captain', 'Hat_CaptainCap']
    reference = []
    ref_arm = next(o for o in dest.objects if o.type == 'ARMATURE')
    for ob in dest.objects:
        studio.objects.link(ob)
        ob.hide_render = False
        ob.hide_viewport = False
        ob.hide_set(False)
        reference.append(ob)
    ref_arm.location.x = -.48
    arm.location.x = .38
    ref_arm.animation_data.action = bpy.data.actions['Idle']
    shot('same-scale', 0, (-.03, 0, .535), 1.85, (1400, 1000))
    arm.location.x = 0
    for ob in reference:
        bpy.data.objects.remove(ob, do_unlink=True)
    for action in list(bpy.data.actions):
        if action.name not in baseline['actions']:
            bpy.data.actions.remove(action)
arm.animation_data.action = bpy.data.actions['Idle']
scene.frame_set(1)
assert signature(arm) == baseline
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == original_hash
print('MIRA BUILD COMPLETE', args.revision, triangles, 'triangles; original contract unchanged', flush=True)

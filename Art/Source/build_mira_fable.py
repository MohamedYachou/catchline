"""Mira (navigator) hero crew member on the shared CrewRig skeleton.

Headless Blender 5.2 (bpy module or blender --background --python).
Source axes X right, -Y forward, Z up. Writes Art/Models/CrewV2/Mira-fable/.
Deterministic: every vertex, UV, weight and texture pixel is generated here.
"""
import bpy, math, json, sys, time
from pathlib import Path
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFilter

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RIG = ROOT / 'Art/Models/CrewRig/CrewRig.blend'
OUT = ROOT / 'Art/Models/CrewV2/Mira-fable'
OUT.mkdir(parents=True, exist_ok=True)
RENDER = OUT / 'renders'
RENDER.mkdir(exist_ok=True)
SAMPLES = int(sys.argv[sys.argv.index('--samples') + 1]) if '--samples' in sys.argv else 48
QUICK = '--quick' in sys.argv

# ----------------------------------------------------------------------------- palette
PALETTE = {
    'M_HullNavy': '#173F57', 'M_RailIvory': '#F3F0DC', 'M_Skin': '#E09660',
    'M_Rubber': '#28343B', 'M_Steel': '#8FA6AC', 'M_Rope': '#D1AF76',
    'M_BandIvory': '#F3DEA1',
    # new for Mira
    'M_HairMira': '#5A3620', 'M_Brass': '#D9A441', 'M_BootNavy': '#12304A',
    'M_LensBlue': '#2E8FE0', 'M_Leather': '#6B4A2B', 'M_SweaterCream': '#F2E7CF',
    'M_CoatNavy': '#1E4A78', 'M_LipRed': '#B9503F',
}
NEW_MATERIALS = {k: PALETTE[k] for k in ('M_HairMira', 'M_Brass', 'M_BootNavy', 'M_LensBlue',
                                         'M_Leather', 'M_SweaterCream', 'M_CoatNavy')}


def srgb_to_linear(c):
    c = c / 255
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def rgba(hexcolour):
    h = hexcolour.lstrip('#')
    return tuple(srgb_to_linear(int(h[i:i + 2], 16)) for i in (0, 2, 4)) + (1,)


def flat_material(name, hexcolour, roughness=.72, metallic=0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = rgba(hexcolour)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = rgba(hexcolour)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat


def textured_material(name, image_path, roughness=.6, gloss_mask=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(str(image_path))
    tex.image.colorspace_settings.name = 'sRGB'
    tex.image.alpha_mode = 'CHANNEL_PACKED'
    tex.interpolation = 'Linear'
    links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = roughness
    if gloss_mask:
        # Separate greyscale map: white = glossy (eyes, lips), black = matte skin.
        g = nodes.new('ShaderNodeTexImage'); g.image = bpy.data.images.load(str(gloss_mask))
        g.image.colorspace_settings.name = 'Non-Color'
        scale = nodes.new('ShaderNodeMath'); scale.operation = 'MULTIPLY_ADD'
        scale.inputs[1].default_value = -.5; scale.inputs[2].default_value = roughness
        links.new(g.outputs['Color'], scale.inputs[0])
        links.new(scale.outputs[0], bsdf.inputs['Roughness'])
    return mat


# ----------------------------------------------------------------------------- textures
def paint_face(path, size=1024):
    """Equirect-ish face map. u: front hemisphere spans 0.1..0.9; v: 1 = top of head."""
    S = size * 2  # supersample
    img = Image.new('RGBA', (S, S), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    skin = (226, 152, 98); skin_dark = (198, 122, 74); skin_light = (240, 176, 122)
    d.rectangle([0, 0, S, S], fill=skin + (255,))
    shade = Image.new('L', (S, S), 0)
    sd = ImageDraw.Draw(shade)
    sd.ellipse([-S * .2, S * .62, S * 1.2, S * 1.5], fill=120)
    sd.rectangle([0, 0, S * .1, S], fill=90); sd.rectangle([S * .9, 0, S, S], fill=90)
    shade = shade.filter(ImageFilter.GaussianBlur(S * .05))
    img.paste(Image.new('RGBA', (S, S), skin_dark + (255,)), (0, 0), shade)
    light = Image.new('L', (S, S), 0)
    ld = ImageDraw.Draw(light)
    ld.ellipse([S * .33, S * .3, S * .67, S * .52], fill=100)
    light = light.filter(ImageFilter.GaussianBlur(S * .07))
    img.paste(Image.new('RGBA', (S, S), skin_light + (255,)), (0, 0), light)

    def u(a_deg):
        return S * (.5 + .4 * a_deg / 90)

    def v(frac):
        return S * frac

    # blush
    blush = Image.new('L', (S, S), 0)
    bd = ImageDraw.Draw(blush)
    for sgn in (-1, 1):
        cx, cy = u(sgn * 42), v(.6)
        bd.ellipse([cx - S * .075, cy - S * .036, cx + S * .075, cy + S * .036], fill=165)
    blush = blush.filter(ImageFilter.GaussianBlur(S * .03))
    img.paste(Image.new('RGBA', (S, S), (228, 116, 92, 255)), (0, 0), blush)

    # brows: thick, arched, confident; slightly raised at the outer end
    brow = (66, 38, 20)
    for sgn in (-1, 1):
        cx, cy = u(sgn * 26), v(.425)
        w, h = S * .072, S * .012
        pts = []
        for i in range(13):
            t = i / 12
            x = cx + sgn * (t - .5) * w * 2
            y = cy - math.sin(t * math.pi) * S * .02 + (t - .5) * S * .006
            pts.append((x, y))
        d.line(pts, fill=brow + (255,), width=int(h * 2.2), joint='curve')
        for k in (0, -1):
            r = h * (1.1 if k == 0 else .8)
            d.ellipse([pts[k][0] - r, pts[k][1] - r, pts[k][0] + r, pts[k][1] + r], fill=brow + (255,))

    # eyes: big dark glossy ovals, thick upper lash line with a wing, two highlights
    ink = (26, 19, 16); liner = (16, 11, 9)
    for sgn in (-1, 1):
        cx, cy = u(sgn * 27), v(.515)
        ew, eh = S * .05, S * .072
        wing = [(cx + sgn * ew * .2, cy - eh * .8), (cx + sgn * ew * 1.7, cy - eh * 1.05), (cx + sgn * ew * 1.05, cy - eh * .35)]
        d.polygon(wing, fill=liner + (255,))
        d.ellipse([cx - ew, cy - eh, cx + ew, cy + eh], fill=ink + (0,))
        d.arc([cx - ew * 1.1, cy - eh * 1.18, cx + ew * 1.1, cy + eh * .95], 195, 345, fill=liner + (0,), width=int(S * .014))
        d.ellipse([cx - ew * .66, cy - eh * .05, cx + ew * .66, cy + eh * .93], fill=(52, 32, 22, 0))
        hx, hy = cx - sgn * ew * .32, cy - eh * .42
        d.ellipse([hx - ew * .34, hy - eh * .24, hx + ew * .34, hy + eh * .24], fill=(255, 255, 255, 0))
        hx2, hy2 = cx + sgn * ew * .32, cy + eh * .42
        d.ellipse([hx2 - ew * .14, hy2 - eh * .1, hx2 + ew * .14, hy2 + eh * .1], fill=(255, 255, 255, 0))
        # lower lash hint
        d.arc([cx - ew * .9, cy - eh * .3, cx + ew * .9, cy + eh * 1.12], 30, 150, fill=(120, 60, 40, 255), width=int(S * .004))

    # nose: small rounded shadow under the 3D bump, tip highlight
    nx, ny = u(0), v(.585)
    nose = Image.new('L', (S, S), 0)
    nd = ImageDraw.Draw(nose)
    nd.ellipse([nx - S * .024, ny - S * .012, nx + S * .024, ny + S * .022], fill=110)
    nose = nose.filter(ImageFilter.GaussianBlur(S * .009))
    img.paste(Image.new('RGBA', (S, S), skin_dark + (255,)), (0, 0), nose)
    d.arc([nx - S * .018, ny - S * .002, nx + S * .018, ny + S * .024], 25, 155, fill=(176, 100, 60, 255), width=int(S * .005))

    # mouth: closed confident smile, lifted to her left (screen right)
    mx, my = u(2), v(.675)
    d.arc([mx - S * .058, my - S * .052, mx + S * .058, my + S * .02], 18, 160, fill=(150, 70, 52, 255), width=int(S * .012))
    d.arc([mx - S * .05, my - S * .028, mx + S * .05, my + S * .018], 28, 150, fill=(222, 118, 96, 0), width=int(S * .009))
    for sgn in (-1, 1):
        cx2 = mx + sgn * S * .057; cy2 = my - S * .008 - (S * .004 if sgn > 0 else 0)
        d.ellipse([cx2 - S * .0075, cy2 - S * .0075, cx2 + S * .0075, cy2 + S * .0075], fill=(150, 70, 52, 255))

    gloss = img.split()[3].point(lambda a: 255 - a).resize((size // 2, size // 2), Image.LANCZOS)
    gloss.save(Path(path).with_name('Mira_Gloss.png'))
    img = img.convert('RGB').resize((size, size), Image.LANCZOS)
    img.save(path)
    return img


def paint_hair(path, size=512):
    S = size * 2
    base = (90, 54, 32)
    img = Image.new('RGB', (S, S), base)
    d = ImageDraw.Draw(img)
    import random
    rnd = random.Random(7)
    for _ in range(160):
        x = rnd.randint(0, S); w = rnd.randint(6, 22)
        shade = rnd.choice([(86, 51, 30), (96, 58, 35), (100, 61, 37), (84, 50, 30)])
        d.line([(x, 0), (x + rnd.randint(-60, 60), S)], fill=shade, width=w)
    img = img.filter(ImageFilter.GaussianBlur(14))
    img = img.resize((size, size), Image.LANCZOS)
    img.save(path)
    return img


# ----------------------------------------------------------------------------- geometry
class Mesh:
    """Deterministic mesh with per-face material, per-loop UVs and per-vertex weights."""
    def __init__(self):
        self.v, self.f, self.m, self.uv, self.w = [], [], [], [], []

    def add(self, verts, faces, material, uvs=None, weights=None):
        o = len(self.v)
        self.v.extend(tuple(p) for p in verts)
        for i, face in enumerate(faces):
            self.f.append(tuple(k + o for k in face))
            self.m.append(material)
            self.uv.append(uvs[i] if uvs else [(0, 0)] * len(face))
        self.w.extend(weights if weights else [{}] * len(verts))

    # -- primitives ---------------------------------------------------------
    def ellipsoid(self, centre, radii, material, seg=20, rings=10, bone=None, weight=None, uv_fn=None):
        c = Vector(centre); rx, ry, rz = radii
        verts, faces, uvs = [], [], []
        for j in range(rings + 1):
            phi = -math.pi / 2 + math.pi * j / rings
            for i in range(seg):
                th = math.tau * i / seg
                verts.append(c + Vector((rx * math.cos(phi) * math.cos(th), ry * math.cos(phi) * math.sin(th), rz * math.sin(phi))))
        for j in range(rings):
            for i in range(seg):
                a = j * seg + i; b = j * seg + (i + 1) % seg
                faces.append((a, b, b + seg, a + seg))
        if uv_fn:
            for face in faces:
                uvs.append([uv_fn(Vector(verts[k]) - c, radii) for k in face])
                # fix wrap-around seams on the face
                us = [p[0] for p in uvs[-1]]
                if max(us) - min(us) > .5:
                    uvs[-1] = [((p[0] + 1) if p[0] < .5 else p[0], p[1]) for p in uvs[-1]]
        ws = [weight or {bone: 1.0}] * len(verts)
        self.add(verts, faces, material, uvs if uv_fn else None, ws)

    def tube(self, path, radii, material, sides=12, bone=None, weight=None, cap=True, uv_scale=(1, 1), twist=0.0, aspect=1.0):
        path = [Vector(p) for p in path]
        verts, faces, uvs = [], [], []
        n = len(path)
        lengths = [0.0]
        for j in range(1, n):
            lengths.append(lengths[-1] + (path[j] - path[j - 1]).length)
        u_prev = None
        for j, p in enumerate(path):
            tangent = (path[min(j + 1, n - 1)] - path[max(j - 1, 0)]).normalized()
            if u_prev is None:
                helper = Vector((0, 0, 1)) if abs(tangent.z) < .9 else Vector((0, 1, 0))
                u_ = helper.cross(tangent).normalized()
            else:
                u_ = (u_prev - tangent * u_prev.dot(tangent))
                u_ = u_.normalized() if u_.length > 1e-6 else Vector((0, 0, 1)).cross(tangent).normalized()
            v_ = tangent.cross(u_).normalized(); u_prev = u_
            r = radii[j] if isinstance(radii, (list, tuple)) else radii
            for i in range(sides):
                a = math.tau * i / sides + twist * j
                verts.append(p + r * (u_ * math.cos(a) + v_ * math.sin(a) * aspect))
        for j in range(n - 1):
            for i in range(sides):
                a = j * sides + i; b = j * sides + (i + 1) % sides
                faces.append((a, b, b + sides, a + sides))
                uvs.append([(i / sides * uv_scale[0], lengths[j] * uv_scale[1]), ((i + 1) / sides * uv_scale[0], lengths[j] * uv_scale[1]),
                            ((i + 1) / sides * uv_scale[0], lengths[j + 1] * uv_scale[1]), (i / sides * uv_scale[0], lengths[j + 1] * uv_scale[1])])
        if cap:
            o = len(verts)
            verts.append(path[0]); verts.append(path[-1])
            for i in range(sides):
                faces.append((o, (i + 1) % sides, i)); uvs.append([(0, 0)] * 3)
                faces.append((o + 1, (n - 1) * sides + i, (n - 1) * sides + (i + 1) % sides)); uvs.append([(0, 0)] * 3)
        ws = [weight or {bone: 1.0}] * len(verts)
        self.add(verts, faces, material, uvs, ws)

    def box(self, centre, size, material, bone=None, weight=None, rot_z=0.0):
        c = Vector(centre); sx, sy, sz = [s / 2 for s in size]
        cz, sn = math.cos(rot_z), math.sin(rot_z)
        verts = []
        for z in (-1, 1):
            for y in (-1, 1):
                for x in (-1, 1):
                    lx, ly = x * sx, y * sy
                    verts.append(c + Vector((lx * cz - ly * sn, lx * sn + ly * cz, z * sz)))
        faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
        self.add(verts, faces, material, None, [weight or {bone: 1.0}] * 8)

    def disc(self, centre, normal, radius, material, sides=24, bone=None, thickness=0.0, inner=0.0):
        c = Vector(centre); nrm = Vector(normal).normalized()
        helper = Vector((0, 0, 1)) if abs(nrm.z) < .9 else Vector((1, 0, 0))
        u_ = helper.cross(nrm).normalized(); v_ = nrm.cross(u_).normalized()
        verts, faces = [], []
        for side, off in ((1, nrm * thickness / 2), (-1, -nrm * thickness / 2)) if thickness else ((1, Vector()),):
            o = len(verts)
            for i in range(sides):
                a = math.tau * i / sides
                verts.append(c + off + radius * (u_ * math.cos(a) + v_ * math.sin(a)))
            if inner:
                for i in range(sides):
                    a = math.tau * i / sides
                    verts.append(c + off + inner * (u_ * math.cos(a) + v_ * math.sin(a)))
                for i in range(sides):
                    f = (o + i, o + (i + 1) % sides, o + sides + (i + 1) % sides, o + sides + i)
                    faces.append(f if side == 1 else tuple(reversed(f)))
            else:
                verts.append(c + off)
                for i in range(sides):
                    f = (o + sides, o + i, o + (i + 1) % sides)
                    faces.append(f if side == 1 else tuple(reversed(f)))
        if thickness:
            o2 = sides + (sides if inner else 1)
            for i in range(sides):
                faces.append((i, i + o2, (i + 1) % sides + o2, (i + 1) % sides))
                if inner:
                    faces.append((sides + (i + 1) % sides, sides + (i + 1) % sides + o2, sides + i + o2, sides + i))
        self.add(verts, faces, material, None, [{bone: 1.0}] * len(verts))

    def star(self, centre, normal, r_out, r_in, points, material, bone, thickness=.004):
        c = Vector(centre); nrm = Vector(normal).normalized()
        helper = Vector((0, 0, 1)) if abs(nrm.z) < .9 else Vector((1, 0, 0))
        u_ = helper.cross(nrm).normalized(); v_ = nrm.cross(u_).normalized()
        ring = []
        for i in range(points * 2):
            a = math.tau * i / (points * 2) + math.pi / 2
            r = r_out if i % 2 == 0 else r_in
            ring.append(u_ * math.cos(a) * r + v_ * math.sin(a) * r)
        verts = [c + p + nrm * thickness for p in ring] + [c + nrm * thickness] + [c + p for p in ring] + [c]
        n2 = len(ring)
        faces = [(n2, i, (i + 1) % n2) for i in range(n2)]
        faces += [(2 * n2 + 1, n2 + 1 + (i + 1) % n2, n2 + 1 + i) for i in range(n2)]
        faces += [(i, n2 + 1 + i, n2 + 1 + (i + 1) % n2, (i + 1) % n2) for i in range(n2)]
        self.add(verts, faces, material, None, [{bone: 1.0}] * len(verts))

    # -- object -------------------------------------------------------------
    def build(self, name, armature, collection, materials):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        me.update()
        mat_index = {}
        for mat_name in dict.fromkeys(self.m):
            mat_index[mat_name] = len(me.materials)
            me.materials.append(materials[mat_name])
        for i, p in enumerate(me.polygons):
            p.material_index = mat_index[self.m[i]]
            p.use_smooth = True
        uv_layer = me.uv_layers.new(name='UVMap')
        for i, p in enumerate(me.polygons):
            for k, li in enumerate(p.loop_indices):
                uv_layer.data[li].uv = self.uv[i][k]
        ob = bpy.data.objects.new(name, me)
        collection.objects.link(ob)
        ob.parent = armature
        for b in armature.data.bones:
            ob.vertex_groups.new(name=b.name)
        for i, w in enumerate(self.w):
            total = sum(w.values()) or 1.0
            for bn, val in w.items():
                ob.vertex_groups[bn].add([i], val / total, 'REPLACE')
        mod = ob.modifiers.new('SharedRig', 'ARMATURE'); mod.object = armature
        return ob

    def tris(self):
        return sum(len(f) - 2 for f in self.f)


def face_uv(local, radii):
    x, y, z = local.x / radii[0], local.y / radii[1], local.z / radii[2]
    a = math.atan2(x, -y)  # 0 = front, +x = left side of the screen (her right)
    if abs(a) <= math.pi / 2:
        u = .5 + .4 * (a / (math.pi / 2))
    else:
        s = 1 if a > 0 else -1
        u = .5 + s * (.4 + .1 * (abs(a) - math.pi / 2) / (math.pi / 2))
    v = .5 + math.asin(max(-1, min(1, z))) / math.pi
    return (u, v)


def wave_path(start, end, n, amp, freq, phase=0.0, axis=Vector((1, 0, 0)), sag=0.0):
    s, e = Vector(start), Vector(end)
    pts = []
    for i in range(n):
        t = i / (n - 1)
        p = s.lerp(e, t)
        p += axis * (amp * math.sin(t * freq * math.tau + phase)) * math.sin(math.pi * min(1, t * 1.6 + .1))
        p.y += sag * math.sin(math.pi * t)
        pts.append(p)
    return pts


def curl_path(start, end, n, side_axis, side_amp, side_freq, out_axis, out_amp, out_freq, phase=0.0, bulge=0.0):
    """Wavy strand: sine offsets along two axes so it reads as a curl, not a ribbon."""
    s, e = Vector(start), Vector(end)
    pts = []
    for i in range(n):
        t = i / (n - 1)
        env = math.sin(math.pi * min(1, .15 + t))
        p = s.lerp(e, t)
        p += Vector(side_axis) * side_amp * math.sin(t * side_freq * math.tau + phase) * env
        p += Vector(out_axis) * out_amp * math.sin(t * out_freq * math.tau + phase * .7 + 1.0) * env
        p += Vector(out_axis) * bulge * math.sin(math.pi * t)
        pts.append(p)
    return pts


# ----------------------------------------------------------------------------- build
t0 = time.time()
bpy.ops.wm.open_mainfile(filepath=str(RIG))
scene = bpy.context.scene
arm = bpy.data.objects['CrewRig']
export_col = arm.users_collection[0]
# Keep the old crew only for the size comparison render; never exported.
reference_crew = [bpy.data.objects[n] for n in ('Body', 'Outfit_Deckhand', 'Hat_Beanie')]
for ob in list(bpy.data.objects):
    if ob.type == 'MESH' and ob.name.startswith(('Outfit_', 'Hat_')) and ob not in reference_crew:
        bpy.data.objects.remove(ob, do_unlink=True)
for ob in reference_crew:
    ob.hide_render = True; ob.hide_viewport = True

materials = {k: flat_material(k, v) for k, v in PALETTE.items()}
materials['M_Brass'] = flat_material('M_Brass', PALETTE['M_Brass'], roughness=.35, metallic=.9)
materials['M_LensBlue'] = flat_material('M_LensBlue', PALETTE['M_LensBlue'], roughness=.15)
materials['M_Rubber'].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .5
face_png = OUT / 'Mira_Face.png'; hair_png = OUT / 'Mira_Hair.png'
paint_face(face_png); paint_hair(hair_png)
materials['Mira_Face'] = textured_material('Mira_Face', face_png, roughness=.62, gloss_mask=OUT / 'Mira_Gloss.png')
materials['Mira_Hair'] = textured_material('Mira_Hair', hair_png, roughness=.55)

HEAD_C = Vector((0, 0, .76)); HEAD_R = (.186, .164, .19)
mira = Mesh()

# ---- head and face
mira.ellipsoid(HEAD_C, HEAD_R, 'Mira_Face', seg=40, rings=20, bone='Head', uv_fn=face_uv)
mira.ellipsoid((0, -.162, .722), (.019, .02, .017), 'M_Skin', 12, 6, bone='Head')  # nose bump under the painted nose
for s in (1, -1):
    mira.ellipsoid((s * .18, .005, .742), (.026, .022, .038), 'M_Skin', 12, 8, bone='Head')
    mira.ellipsoid((s * .183, -.004, .748), (.014, .012, .022), 'M_Skin', 10, 6, bone='Head')
    mira.disc((s * .183, .0, .704), (1, 0, 0), .015, 'M_Brass', sides=18, bone='Head', thickness=.004, inner=.011)
mira.ellipsoid((0, 0, .575), (.058, .052, .07), 'M_Skin', 16, 8, bone='Neck')

# ---- hair
HAIR = 'Mira_Hair'
mira.ellipsoid((0, .012, .795), (.188, .172, .17), HAIR, 28, 12, bone='Head')  # scalp volume under the cap
# fringe: a soft sweep across the forehead to her left, from under the visor
for i, (x0, x1, z1, r, ph) in enumerate([(-.12, -.18, .79, .026, 0), (-.06, -.13, .81, .025, .9), (0, -.07, .822, .024, 1.7), (.06, .0, .83, .022, 2.5), (.12, .08, .83, .02, 3.2)]):
    pts = curl_path((x0, -.14, .87), (x1, -.168, z1), 6, (1, 0, 0), .012, .5, (0, -1, 0), .006, .6, phase=ph)
    mira.tube(pts, [r * .8, r, r * 1.05, r * .9, r * .6, r * .25], HAIR, sides=10, bone='Head', uv_scale=(1, 4), aspect=.85)
# side waves framing the face: three chunky curls per side ending at jaw / collar
for s in (1, -1):
    for k, (y0, z1, r, yoff, x1, amp) in enumerate([(-.1, .63, .046, -.04, .21, .028), (-.02, .585, .05, -.01, .235, .034), (.07, .645, .044, .02, .22, .03)]):
        start = (s * .15, y0, .875); end = (s * x1, y0 + yoff, z1)
        pts = curl_path(start, end, 13, (s, 0, 0), amp, 1.0, (0, -1, 0), .022, 1.3, phase=k * 1.1 + (0 if s > 0 else .8))
        tip = pts[-1]
        pts += [tip + Vector((s * .012, -.012, -.028)), tip + Vector((-s * .018, -.02, -.046)), tip + Vector((-s * .05, -.012, -.042))]
        radii = [r * .55, r * .8, r * .95, r * 1.05, r * 1.08, r * 1.08, r * 1.05, r, r, r * .97, r * .95, r * .9, r * .9, r * .82, r * .65, r * .3]
        mira.tube(pts, radii, HAIR, sides=10, bone='Head', uv_scale=(1, 3), twist=.15, aspect=.9)
# high ponytail: puff behind the cap, strands spring back and up, then cascade in an S down the back
puff = Vector((0, .155, .905))
mira.ellipsoid(puff, (.095, .07, .085), HAIR, 18, 9, bone='Head')
mira.ellipsoid((0, .14, .72), (.12, .06, .12), HAIR, 16, 8, bone='Head')  # nape mass under the tail
for k in range(7):
    a = math.tau * k / 7 + .4
    ox, oz = math.cos(a) * .06, math.sin(a) * .04
    r = .036 + (.008 if k % 2 == 0 else 0)
    spread = 1.0 + .35 * (k % 3)
    p0 = puff + Vector((ox, .04, oz))
    p1 = Vector((ox * 1.2, .25 + .03 * math.cos(a), .92 + oz * .5))
    p2 = Vector((ox * 2.2 * spread, .27 + .04 * math.sin(a), .74 + oz))
    p3 = Vector((ox * 2.0 * spread + (.04 if k % 2 else -.04), .24 + .04 * math.cos(a), .52 + .06 * math.cos(a)))
    p4 = p3 + Vector((ox * .8, -.06, -.08))
    base = [p0.lerp(p1, t) for t in (0, .5)] + [p1.lerp(p2, t) for t in (0, .25, .5, .75)] + [p2.lerp(p3, t) for t in (0, .33, .66)] + [p3.lerp(p4, t) for t in (0, .5, 1)]
    lateral = Vector((math.cos(a + 1.3), 0, math.sin(a + 1.3)))
    pts = [p + lateral * .04 * math.sin(i * .95 + k) * (0 if i < 2 else 1) + Vector((0, .025, 0)) * math.sin(i * 1.3 + k * .5) * (0 if i < 2 else 1) for i, p in enumerate(base)]
    radii = [r * .6, r * .95, r * 1.1, r * 1.15, r * 1.1, r * 1.05, r, r * .98, r * .92, r * .85, r * .65, r * .3]
    mira.tube(pts, radii, HAIR, sides=10, bone='Head', uv_scale=(1, 2.5), twist=.15, aspect=.9)
    mira.ellipsoid(pts[-1] + Vector((0, .01, -.012)), (r * 1.05, r * .9, r * .8), HAIR, 10, 6, bone='Head')
for k, (x, y, z) in enumerate([(-.08, .25, .5), (.08, .26, .47), (0, .29, .55), (-.1, .22, .62), (.1, .23, .64)]):
    mira.ellipsoid((x, y, z), (.04, .034, .034), HAIR, 10, 6, bone='Head')

# ---- torso: double-breasted pea coat over a cream cable-knit sweater
COAT = 'M_CoatNavy'
torso = [(0, .005, .27), (0, .003, .33), (0, 0, .4), (0, -.003, .46), (0, -.006, .515), (0, -.004, .55)]
mira.tube(torso, [.158, .15, .148, .15, .146, .11], COAT, 24, aspect=.68, cap=True,
          weight=None, bone='Spine')
# re-weight the torso tube by height (Hips / Spine / Spine1) after build; see below
# cream sweater at the collar with fine ribs
mira.ellipsoid((0, -.045, .552), (.078, .052, .046), 'M_SweaterCream', 20, 8, bone='Spine1')
for i in range(9):
    x = -.04 + i * .01
    mira.tube([(x, -.088, .535), (x, -.095, .556), (x, -.09, .576)], .0035, 'M_SweaterCream', 6, bone='Spine1', cap=False)
# V-neck of the coat: cream triangle showing, lapels folding out on either side
mira.add([(0, -.108, .47), (-.045, -.104, .54), (.045, -.104, .54), (0, -.1, .555)],
         [(0, 2, 3, 1)], 'M_SweaterCream', None, [{'Spine1': 1.0}] * 4)
for s in (1, -1):
    # lapel as a folded flap: outer navy face, thin cream edge
    lap = [(s * .006, -.112, .445), (s * .1, -.102, .52), (s * .085, -.094, .57), (s * .03, -.108, .52)]
    mira.add([Vector(p) for p in lap] + [Vector(p) + Vector((0, .012, 0)) for p in lap],
             [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2)], COAT, None, [{'Spine1': 1.0}] * 8)
    mira.tube([(s * .008, -.117, .447), (s * .1, -.107, .52)], .0028, 'M_SweaterCream', 6, bone='Spine1')
    for z in (.46, .405, .35):
        mira.ellipsoid((s * .05, -.111 + (z < .45) * .003, z), (.0135, .007, .0135), 'M_Brass', 12, 6, bone='Spine' if z < .5 else 'Spine1')
        mira.ellipsoid((s * .05, -.118 + (z < .45) * .003, z), (.0065, .003, .0065), 'M_BandIvory', 8, 4, bone='Spine' if z < .5 else 'Spine1')
# front overlap edge and hem
mira.box((.012, -.112, .37), (.008, .012, .2), COAT, bone='Spine')
mira.tube([(0, .005, .262), (0, .005, .272)], [.16, .158], COAT, 24, aspect=.68, bone='Hips')
# stand-up collar behind the neck
mira.tube([(-.095, .03, .555), (-.055, .07, .575), (0, .085, .582), (.055, .07, .575), (.095, .03, .555)], [.012, .02, .024, .02, .012], COAT, 10, bone='Spine1')

# ---- arms and mitten hands (crew style)
for s, side in ((1, 'Left'), (-1, 'Right')):
    mira.ellipsoid((s * .14, 0, .515), (.062, .062, .06), COAT, 14, 8, bone=side + 'Shoulder')
    mira.tube([(s * .15, 0, .51), (s * .21, 0, .51), (s * .28, 0, .51)], [.064, .058, .053], COAT, 14, bone=side + 'Arm')
    mira.tube([(s * .28, 0, .51), (s * .34, 0, .51), (s * .392, 0, .51)], [.053, .049, .046], COAT, 14, bone=side + 'ForeArm')
    mira.tube([(s * .385, 0, .51), (s * .398, 0, .51)], [.05, .049], COAT, 14, bone=side + 'ForeArm')  # cuff ridge
    mira.ellipsoid((s * .428, 0, .51), (.046, .042, .04), 'M_Skin', 16, 8, bone=side + 'Hand')
    mira.ellipsoid((s * .412, -.036, .487), (.021, .024, .021), 'M_Skin', 12, 6, bone=side + 'Hand')

# ---- trousers and navy rubber boots
for s, side in ((1, 'Left'), (-1, 'Right')):
    mira.tube([(s * .085, 0, .32), (s * .085, 0, .25), (s * .085, 0, .19)], [.068, .062, .056], 'M_HullNavy', 14, bone=side + 'UpLeg')
    mira.tube([(s * .085, 0, .19), (s * .085, 0, .13), (s * .085, 0, .07)], [.057, .055, .054], 'M_BootNavy', 14, bone=side + 'Leg')
    mira.tube([(s * .085, 0, .185), (s * .085, 0, .2)], [.06, .058], 'M_BootNavy', 14, bone=side + 'Leg')  # boot cuff
    mira.ellipsoid((s * .085, -.03, .052), (.066, .1, .052), 'M_BootNavy', 18, 8, bone=side + 'Foot')
    mira.ellipsoid((s * .085, -.032, .016), (.069, .104, .017), 'M_Rubber', 18, 6, bone=side + 'Foot')

# ---- binoculars on a leather strap around the neck
strap = []
for i in range(15):
    t = i / 14; a = math.pi * (.12 + .76 * t)
    strap.append((math.cos(a) * .1, -.02 - .1 * math.sin(a), .575 - .17 * math.sin(a) ** 1.2))
mira.tube(strap, .006, 'M_Leather', 8, bone='Spine1')
for s in (1, -1):
    mira.tube([(s * .03, -.11, .415), (s * .03, -.17, .415)], [.024, .027], 'M_Rubber', 14, bone='Spine1')
    mira.disc((s * .03, -.171, .415), (0, -1, 0), .021, 'M_LensBlue', 14, bone='Spine1')
    mira.tube([(s * .03, -.14, .415), (s * .03, -.15, .415)], .028, 'M_Brass', 14, bone='Spine1')
    mira.tube([(s * .03, -.112, .415), (s * .03, -.118, .415)], .026, 'M_Brass', 14, bone='Spine1')
mira.box((0, -.138, .418), (.03, .034, .02), 'M_Rubber', bone='Spine1')
mira.tube([(0, -.125, .45), (0, -.13, .432)], .005, 'M_Rubber', 6, bone='Spine1')

body_ob = mira.build('Mira', arm, export_col, materials)
for v in body_ob.data.vertices:
    v.co.z = max(0.0, v.co.z)
    if body_ob.data.polygons and v.index < 40 * 21 + 0:  # head ellipsoid vertices come first
        dz = (v.co.z - HEAD_C.z) / HEAD_R[2]
        if dz < .15:
            cheek = .09 * (1 - abs(dz + .45) / .6) if -1.05 < dz < .15 else 0
            v.co.x *= 1 + max(0, cheek); v.co.y = HEAD_C.y + (v.co.y - HEAD_C.y) * (1 + max(0, cheek) * .5)
# torso weights by height: Hips below .33, Spine to .47, Spine1 above; smooth blends between
for v in body_ob.data.vertices:
    gs = [g.group for g in v.groups]
    names = {body_ob.vertex_groups[g].name for g in gs}
    if names == {'Spine'} and abs(v.co.x) < .17 and v.co.z < .56 and v.co.z > .26 and abs(v.co.y) < .12:
        z = v.co.z
        for g in body_ob.vertex_groups: g.remove([v.index])
        if z < .31: w = {'Hips': 1}
        elif z < .37: t = (z - .31) / .06; w = {'Hips': 1 - t, 'Spine': t}
        elif z < .45: w = {'Spine': 1}
        elif z < .51: t = (z - .45) / .06; w = {'Spine': 1 - t, 'Spine1': t}
        else: w = {'Spine1': 1}
        for bn, val in w.items(): body_ob.vertex_groups[bn].add([v.index], val, 'REPLACE')
for v in body_ob.data.vertices:
    if .25 < abs(v.co.x) < .31 and .45 < v.co.z < .57:
        side = 'Left' if v.co.x > 0 else 'Right'; w = max(0, min(1, (abs(v.co.x) - .25) / .06))
        for g in body_ob.vertex_groups: g.remove([v.index])
        body_ob.vertex_groups[side + 'Arm'].add([v.index], 1 - w, 'REPLACE')
        body_ob.vertex_groups[side + 'ForeArm'].add([v.index], w, 'REPLACE')

# ---- cap: rigid child of HatMount (same convention as the other hats)
cap = Mesh()
cap.ellipsoid((0, .03, .955), (.21, .195, .085), 'M_HullNavy', 28, 10, bone='HatMount')   # soft crown pushed back
cap.ellipsoid((0, .055, .995), (.16, .145, .04), 'M_HullNavy', 20, 6, bone='HatMount')    # crown top
cap.tube([(0, .01, .888), (0, .01, .91)], [.19, .19], 'M_HullNavy', 28, bone='HatMount', aspect=.9)
band = []
for i in range(29):
    a = math.tau * i / 28 - math.pi / 2
    band.append((math.cos(a) * .188, math.sin(a) * .17 + .01, .897))
cap.tube(band, .02, 'M_BandIvory', 10, bone='HatMount', aspect=.8, cap=False)
vv, vf = [], []
for row, (ry, z, w) in enumerate([(.0, .882, .185), (.06, .868, .205), (.115, .852, .195), (.155, .842, .135)]):
    for i in range(9):
        t = i / 8
        vv.append((-w + 2 * w * t, -.15 - ry + .02 * (abs(t - .5) * 2) ** 2, z + .012 * (abs(t - .5) * 2) ** 2))
for row in range(3):
    for i in range(8):
        a = row * 9 + i
        vf.append((a, a + 1, a + 10, a + 9))
top = len(vv)
for v_ in list(vv): vv.append((v_[0], v_[1], v_[2] - .007))
for row in range(3):
    for i in range(8):
        a = top + row * 9 + i
        vf.append((a + 9, a + 10, a + 1, a))
for i in range(8):
    vf.append((i, top + i, top + i + 1, i + 1)); a = 27 + i; vf.append((a + 1, top + a + 1, top + a, a))
for row in range(3):
    a = row * 9; vf.append((a + 9, top + a + 9, top + a, a)); a = row * 9 + 8; vf.append((a, top + a, top + a + 9, a + 9))
cap.add(vv, vf, 'M_Rubber', None, [{'HatMount': 1.0}] * len(vv))
# brass compass-rose badge on the crown front
bn = Vector((0, -1, .3)).normalized(); bc = Vector((0, -.178, .94))
cap.disc(bc, bn, .037, 'M_Brass', 24, bone='HatMount', thickness=.007)
cap.disc(bc + bn * .0045, bn, .03, 'M_BandIvory', 24, bone='HatMount', thickness=.002)
cap.star(bc + bn * .006, bn, .028, .01, 4, 'M_Brass', 'HatMount', thickness=.004)
cap.star(bc + bn * .0075, bn, .016, .005, 4, 'M_HullNavy', 'HatMount', thickness=.0045)
cap.star(bc + bn * .0085, bn, .009, .003, 8, 'M_Brass', 'HatMount', thickness=.0025)
cap.ellipsoid((.172, -.075, .897), (.014, .014, .014), 'M_Brass', 12, 6, bone='HatMount')
cap_ob = cap.build('Mira_Cap', arm, export_col, materials)
cap_ob.modifiers.clear()
for g in list(cap_ob.vertex_groups): cap_ob.vertex_groups.remove(g)
world = cap_ob.matrix_world.copy()
cap_ob.parent = arm; cap_ob.parent_type = 'BONE'; cap_ob.parent_bone = 'HatMount'; cap_ob.matrix_world = world

tri_count = mira.tris() + cap.tris()
print('TRIANGLES', tri_count, 'body', mira.tris(), 'cap', cap.tris())

# ----------------------------------------------------------------------------- save + export
arm.animation_data.action = None
for p in arm.pose.bones:
    p.rotation_quaternion = (1, 0, 0, 0); p.location = (0, 0, 0); p.scale = (1, 1, 1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'Mira.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in (arm, body_ob, cap_ob): ob.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=str(OUT / 'Mira.fbx'), use_selection=True, object_types={'MESH', 'ARMATURE'},
                         axis_forward='-Z', axis_up='Y', global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                         use_space_transform=True, bake_space_transform=False, add_leaf_bones=False, use_armature_deform_only=False,
                         bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
                         bake_anim_simplify_factor=0, use_custom_props=True, mesh_smooth_type='FACE', path_mode='COPY', embed_textures=False)

# ----------------------------------------------------------------------------- renders
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.render.film_transparent = False
world_ = scene.world or bpy.data.worlds.new('World'); scene.world = world_
world_.use_nodes = True
bg = world_.node_tree.nodes['Background']; bg.inputs[0].default_value = (.92, .9, .84, 1); bg.inputs[1].default_value = .9
cam = bpy.data.objects.get('Preview_Orthographic')
if cam is None:
    cam = bpy.data.objects.new('Preview_Orthographic', bpy.data.cameras.new('Preview_Orthographic')); scene.collection.objects.link(cam)
cam.data.type = 'ORTHO'; scene.camera = cam
key = bpy.data.objects.get('Preview_Key'); fill = bpy.data.objects.get('Preview_Fill')
if key: key.data.energy = 3.0
if fill: fill.data.energy = 1.2


def look(target, yaw_deg, elev_deg, dist, ortho, size):
    a, e = math.radians(yaw_deg), math.radians(elev_deg)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    cam.location = Vector(target) + d * dist
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = ortho
    scene.render.resolution_x, scene.render.resolution_y = size


def render(name):
    scene.render.filepath = str(RENDER / name); bpy.ops.render.render(write_still=True)


SIZE = (360, 540) if QUICK else (520, 780)
for ob in reference_crew: ob.hide_render = True
views = [('front', 0), ('threequarter', 40), ('side', 90), ('back', 180)]
for name, yaw in views:
    look((0, 0, .5), yaw, 8, 4, 1.25, SIZE); render(name + '.png')
look((0, -.02, .76), 15, 4, 3, .5, (600, 600) if not QUICK else (360, 360)); render('face.png')
# size comparison next to the current deckhand
for ob in reference_crew: ob.hide_render = False
arm.location.x = 0
# the reference crew shares the armature, so render them separately at the same camera and compose side by side
for ob in (body_ob, cap_ob): ob.hide_render = True
look((0, 0, .5), 20, 8, 4, 1.25, SIZE); render('reference-crew.png')
for ob in (body_ob, cap_ob): ob.hide_render = False
for ob in reference_crew: ob.hide_render = True
look((0, 0, .5), 20, 8, 4, 1.25, SIZE); render('mira-same-camera.png')
# animation frames from the unchanged CrewRig actions
for action, frame in (('Walk', 7), ('Idle', 25)):
    arm.animation_data.action = bpy.data.actions[action]; scene.frame_set(frame)
    look((0, 0, .5), 35, 20, 4, 1.3, SIZE); render(action.lower() + '.png')
arm.animation_data.action = None; scene.frame_set(1)
render_seconds = time.time() - t0

# ----------------------------------------------------------------------------- review sheet
def load(name): return Image.open(RENDER / name).convert('RGB')
tiles = [load(v + '.png') for v, _ in views]
tw, th = tiles[0].size
row2_h = 600
face = load('face.png').resize((row2_h, row2_h))
portrait = Image.open(ROOT / 'docs/screens/crew-styles/mira-ref/mira-portrait.jpg').convert('RGB')
portrait = portrait.resize((int(portrait.width * row2_h / portrait.height), row2_h))
ref = load('reference-crew.png'); same = load('mira-same-camera.png')
pair = Image.new('RGB', (tw * 2, th), (245, 240, 228)); pair.paste(ref, (0, 0)); pair.paste(same, (tw, 0))
pair = pair.resize((int(tw * 2 * row2_h / th), row2_h))
sheet_w = max(tw * 4, row2_h + 10 + portrait.width + 10 + pair.width)
sheet = Image.new('RGB', (sheet_w, th + row2_h + th + 60), (245, 240, 228))
d = ImageDraw.Draw(sheet)
for i, t in enumerate(tiles): sheet.paste(t, (i * tw, 0))
sheet.paste(face, (0, th)); sheet.paste(portrait, (row2_h + 10, th)); sheet.paste(pair, (row2_h + 20 + portrait.width, th))
walk = load('walk.png'); idle = load('idle.png')
sheet.paste(walk, (0, th + row2_h)); sheet.paste(idle, (tw, th + row2_h))
labels = [('front', 0, 0), ('three-quarter', tw, 0), ('side', tw * 2, 0), ('back', tw * 3, 0), ('face close-up', 0, th),
          ('mira-portrait.jpg', row2_h + 10, th), ('current deckhand  |  Mira, same camera', row2_h + 20 + portrait.width, th),
          ('Walk frame 7', 0, th + row2_h), ('Idle frame 25', tw, th + row2_h)]
for text, x, y in labels: d.text((x + 8, y + 6), text, fill=(23, 63, 87))
d.text((tw * 2 + 10, th + row2_h + 10), f'Mira-fable  ·  {tri_count} triangles  ·  textures 1024² face + 512² hair  ·  render {render_seconds:.0f}s', fill=(23, 63, 87))
sheet.save(OUT / 'Mira-review.png')
json.dump({'triangles': tri_count, 'body_triangles': mira.tris(), 'cap_triangles': cap.tris(), 'render_seconds': round(render_seconds, 1),
           'textures': {'Mira_Face.png': 1024, 'Mira_Hair.png': 512}, 'new_materials': NEW_MATERIALS,
           'bones': [b.name for b in arm.data.bones], 'actions': [a.name for a in bpy.data.actions]},
          open(OUT / 'stats.json', 'w'), indent=2)
print('MIRA BUILD COMPLETE', tri_count, 'tris', f'{render_seconds:.0f}s')

# ----------------------------------------------------------------------------- FBX round-trip check
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT / 'Mira.fbx'), use_anim=True)
arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
meshes = {o.name: o for o in bpy.context.scene.objects if o.type == 'MESH'}
check = {'armatures': len(arms), 'bones': sorted(b.name for b in arms[0].data.bones) if arms else [],
         'meshes': sorted(meshes), 'actions': sorted(a.name.split('|')[-1] for a in bpy.data.actions),
         'head_bone_height_m': round((arms[0].matrix_world @ arms[0].data.bones['Head'].head_local).z, 4) if arms else None,
         'mira_scalp_height_m': round(max((meshes['Mira'].matrix_world @ v.co).z for v in meshes['Mira'].data.vertices), 4) if 'Mira' in meshes else None,
         'weights_normalized': all(v.groups and abs(sum(g.weight for g in v.groups) - 1) < 1e-4 for v in meshes['Mira'].data.vertices) if 'Mira' in meshes else None,
         'cap_parent_bone': meshes['Mira_Cap'].parent_bone if 'Mira_Cap' in meshes else None,
         'materials': sorted(m.name for m in bpy.data.materials if m.users)}
stats = json.load(open(OUT / 'stats.json')); stats['fbx_roundtrip'] = check
json.dump(stats, open(OUT / 'stats.json', 'w'), indent=2)
print('FBX ROUNDTRIP', json.dumps(check))

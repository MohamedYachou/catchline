import bpy, sys, math
from mathutils import Vector
out = sys.argv[sys.argv.index('--') + 1]
sc = bpy.context.scene
for o in list(sc.objects):
    if o.type in ('CAMERA', 'LIGHT'):
        o.hide_render = True
meshes = [o for o in sc.objects if o.type == 'MESH' and not o.hide_render and o.visible_get()]
deps = bpy.context.evaluated_depsgraph_get()
pts = []
for o in meshes:
    pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
zmin = min(p.z for p in pts); zmax = max(p.z for p in pts)
h = zmax - zmin
# head centre: top 15% of the figure, x/y from verts in that band
band = [p for p in pts if p.z > zmax - .15 * h]
cx = sum(p.x for p in band) / len(band); cy = sum(p.y for p in band) / len(band)
cz = zmax - .14 * h
arm = next((o for o in sc.objects if o.type == 'ARMATURE'), None)
hb = arm and next((b for b in arm.pose.bones if 'head' in b.name.lower()), None)
if hb:
    hp = arm.matrix_world @ hb.head; tp = arm.matrix_world @ hb.tail
    cx, cy, cz = hp.x, hp.y, (hp.z + zmax) / 2 - .03 * h
c = Vector((cx, cy, cz))
try:
    sc.render.engine = 'BLENDER_EEVEE'
except TypeError:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
sc.render.resolution_x = sc.render.resolution_y = 520
sc.render.film_transparent = False
w = bpy.data.worlds.new('hs'); w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (.85, .82, .76, 1); bg.inputs[1].default_value = 1.0
sc.world = w
sun = bpy.data.objects.new('hs_sun', bpy.data.lights.new('hs_sun', 'SUN'))
sun.data.energy = 3; sun.rotation_euler = (math.radians(40), 0, math.radians(30)); sc.collection.objects.link(sun)
cam = bpy.data.objects.new('hs_cam', bpy.data.cameras.new('hs_cam'))
cam.data.type = 'ORTHO'; cam.data.ortho_scale = .44 * h
sc.collection.objects.link(cam); sc.camera = cam
# Blender front is -Y. Character's left = +X.
views = {'front': (0, -1), 'left': (1, 0), 'back': (0, 1), 'right': (-1, 0), 'q_left': (.7, -.7), 'q_back': (.6, .8)}
for name, (dx, dy) in views.items():
    d = Vector((dx, dy, .18)).normalized()
    cam.location = c + d * h
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sun.rotation_euler = cam.rotation_euler
    sc.render.filepath = f'{out}_{name}.png'
    bpy.ops.render.render(write_still=True)

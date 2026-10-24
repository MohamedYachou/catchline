import bpy, sys
# Usage: blender -b <Name>.blend -P export_glb.py -- <out.glb>   (read-only: the .blend is never saved)
# Exports only the rigged character (armature + meshes bound to it), not review floors or lights.
out = sys.argv[sys.argv.index('--') + 1]
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
for o in bpy.context.scene.objects:
    bound = o.parent == arm or any(m.type == 'ARMATURE' and m.object == arm for m in getattr(o, 'modifiers', []))
    o.hide_set(False); o.select_set(o == arm or (o.type == 'MESH' and bound and not o.hide_render))
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_animations=True, export_apply=False)

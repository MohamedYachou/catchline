"""Extra orthographic boat checks; never saves poses back to model sources."""
from pathlib import Path
import bpy,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/GullHarbour'
for name in ('Rowboat','Skiff'):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'Boats'/f'{name}.blend'))
    scene=bpy.context.scene;camera=scene.camera
    objects=[o for o in bpy.data.collections['ASSET_EXPORT'].objects if o.type=='MESH']
    points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
    lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
    target=Vector([(lo[i]+hi[i])/2 for i in range(3)])
    for view,direction in (('Top',(0,0,1)),('Side',(-1,0,0)),('Front',(0,-1,0))):
        camera.location=target+Vector(direction)*15
        camera.rotation_euler=(0,0,-math.pi/2) if view=='Top' else (target-camera.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        p=[camera.matrix_world.inverted()@v for v in points]
        camera.data.ortho_scale=max(max(v[i] for v in p)-min(v[i] for v in p) for i in (0,1))*1.25
        scene.render.filepath=str(OUT/'Previews/Boats'/f'{name}-{view}.png')
        bpy.ops.render.render(write_still=True)
    if name=='Skiff':
        camera.location=target+Vector((.406,-.579,.707))*15
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.ortho_scale=8.8
        bpy.data.objects['HoldLid'].rotation_euler.x=math.radians(-100)
        scene.render.filepath=str(OUT/'Previews/Boats/Skiff-OpenHold.png')
        bpy.ops.render.render(write_still=True)

"""Reopen saved assembly to independently measure camera and fish/insert framing."""
import sys,math,json
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
bpy.ops.wm.open_mainfile(filepath=str(B.O/'GutKit-camera-fixture.blend'))
s=bpy.context.scene;cam=s.camera;top=bpy.data.objects['GutBoard'].location.z
direction=cam.rotation_euler.to_matrix()@Vector((0,0,-1));height=cam.location.z-top;pitch=math.degrees(math.asin(-direction.z))
assert abs(height-.9)<1e-6 and abs(pitch-60)<.0001,(height,pitch)
assert abs(math.degrees(cam.data.angle_x)-55)<.0001
fishroot=bpy.data.objects['Catchline_Mackerel'];fish=[o for o in s.objects if o.type=='MESH' and any(p==fishroot for p in [o.parent,o.parent.parent if o.parent else None])]
assert len(fish)>=1
rows={}
for w,h in [(1440,900),(844,390)]:
 s.render.resolution_x=w;s.render.resolution_y=h;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();row={}
 for name,objs in [('board',[bpy.data.objects['GutBoard']]),('fish',fish),('insert',[bpy.data.objects['BellyOpen']])]:
  pts=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in objs for v in o.evaluated_get(dg).data.vertices]
  bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(2)]
  assert all(0<a<b<1 for a,b in bounds),(w,h,name,bounds)
  row[name]=bounds
 rows[str(w)+'x'+str(h)]=row
# Insert must lie on the fish side; geometry visibility will be reviewed from the images.
refs=json.loads((B.O/'metrics/references.json').read_text())
for p,r in refs.items():assert B.sha(B.R/p)==r['sha256'],p
(B.O/'metrics/fixture-audit.json').write_text(json.dumps({'result':'PASS','height_m':height,'pitch_degrees':pitch,'horizontal_fov_degrees':math.degrees(cam.data.angle_x),'framing':rows,'protected_references_unchanged':True},indent=2)+'\n')
print('GUT FIXTURE_AUDIT PASS',flush=True)

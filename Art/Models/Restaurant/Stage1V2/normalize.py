"""Apply exact base pivots to existing audited geometry, then repeat explicit exports.
Useful after an older build; current build.py already performs this operation. No UV/light bake changes.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'Stage1V2.blend'))
sc=bpy.context.scene;m=json.loads((O/'build-metrics.json').read_text())
roots={r['root']:bpy.data.objects[r['root']] for r in m['roots']}
for name,root in roots.items():
 root.matrix_basis=Matrix.Identity(4)
 for child in root.children:child.hide_viewport=False;child.hide_render=False
 mesh=next(o for o in root.children if o.type=='MESH')
 if name!='RoomShell':
  zbase=min(v.co.z for v in mesh.data.vertices)
  for vert in mesh.data.vertices:vert.co.z-=zbase
  for child in root.children:
   if child.type=='EMPTY':child.location.z-=zbase
footprints={r['root']:r['footprint_tiles'] for r in m['roots'] if r['footprint_tiles']}
prop_sizes={r['root']:True for r in m['roots'] if r['service_prop']}
placements=m['placements'];waterline=m['waterline_blender_z_m'];AOrows=m['AO'];lantern_locs=m['architectural_lantern_positions_m'];atlas=json.loads((O/'textures/atlas.json').read_text())
def finish(root,loc,rz):root.location=loc;root.rotation_euler.z=math.radians(rz)
bpy.context.view_layer.update()
source=(O/'build.py').read_text();exec(source[source.index('# Export per-item at origin'):])

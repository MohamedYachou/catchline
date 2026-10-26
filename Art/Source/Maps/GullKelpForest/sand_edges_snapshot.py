import bpy,json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=R/'Art/Models/Maps/GullKelpForest';S=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'GullKelpForestSeaV2.blend'));bpy.context.view_layer.update()
def snapshot():
 rows={}
 for o in bpy.context.scene.objects:
  r={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world]}
  if o.type=='MESH':
   o.data.calc_loop_triangles();r.update(loop_triangles=[list(t.vertices) for t in o.data.loop_triangles],triangle_materials=[o.data.polygons[t.polygon_index].material_index for t in o.data.loop_triangles],vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],materials=[m.name for m in o.data.materials],material_indices=[p.material_index for p in o.data.polygons],triangles=sum(len(p.vertices)-2 for p in o.data.polygons))
  rows[o.name]=r
 return rows
(S/'accepted-snapshot.json').write_text(json.dumps({'objects':snapshot(),'navigation_sha256':hashlib.sha256((O/'navigation.json').read_bytes()).hexdigest(),'source_sha256':{e:hashlib.sha256((O/('GullKelpForestSeaV2.'+e)).read_bytes()).hexdigest() for e in ('blend','fbx')}},indent=2))
print('MAP11 SNAPSHOT PASS')

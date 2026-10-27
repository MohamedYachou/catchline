import bpy,json,gzip
from pathlib import Path
from mathutils.kdtree import KDTree
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'Restaurant-V4-check.blend'));bpy.context.view_layer.update()
old=json.loads(gzip.decompress((O/'stages-look2-baseline.json.gz').read_bytes()))['meshes'];rows={}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.name.startswith('REVIEW_'):continue
 points=[o.matrix_world@v.co for v in o.data.vertices];b=old.get('EXPORT_'+o.name)
 tree=KDTree(len(b['points'])) if b else None
 if b:
  for i,p in enumerate(b['points']):tree.insert(p,i)
  tree.balance()
 distance=max((tree.find(v)[2] for v in points),default=1) if b else 1
 rows[o.name]=bool(b and len(points)==len(b['points']) and len(o.data.polygons)==b['triangles'] and distance<.00002)
 print('CHECK',o.name,rows[o.name],'max_nearest_m',distance,flush=True)

result={'pass':len(rows)==len(old) and all(rows.values()),'original_nodes':len(old),'check_nodes':len(rows),'matches':rows,'comparison':'same vertex/triangle counts; source-to-original-FBX nearest world vertex distance <20 micrometres (FBX measurements rounded5)'}
(O/'stages-look2-check-baseline.json').write_text(json.dumps(result,indent=2));assert result['pass'],[n for n,v in rows.items() if not v]
print('ORIGINAL CHECKSCENE GEOMETRY',result['pass'],[n for n,v in rows.items() if not v],flush=True)

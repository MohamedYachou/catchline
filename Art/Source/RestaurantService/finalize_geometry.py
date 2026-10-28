"""Remove invisible collapsed lathe poles from authored blends and re-export only owned meshes."""
import sys,json,hashlib,bpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_service as b
records=json.loads((b.O/'manifest.json').read_text())
for rec in records:
 path=b.O/'blends'/(rec['name']+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path))
 ob=bpy.data.objects[rec['name']];before=rec['tris'];b.clean_geometry(ob);ob.data.calc_loop_triangles()
 rec['tris']=len(ob.data.loop_triangles);rec['vertices']=len(ob.data.vertices)
 b.export(ob,b.R/rec['file']);rec['sha256']=hashlib.sha256((b.R/rec['file']).read_bytes()).hexdigest()
 bpy.ops.wm.save_as_mainfile(filepath=str(path),check_existing=False)
 print('FINALIZED',rec['name'],before,rec['tris'],flush=True)
(b.O/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')

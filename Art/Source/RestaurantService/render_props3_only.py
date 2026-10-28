"""Re-render an existing production blend without exporting/changing its FBX."""
import sys,json,bpy
from pathlib import Path
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import build_props3 as p
name=sys.argv[sys.argv.index('--')+1]
rec=next(r for r in json.loads((O/'props3-manifest.json').read_text()) if r['name']==name)
bpy.ops.wm.open_mainfile(filepath=str(O/'blends'/('props3-'+name+'.blend')))
p.b.MAT=bpy.data.objects[name].data.materials[0]
rec['close_only']='--close-only' in sys.argv
p.render_table(bpy.data.objects[name],rec);rec.pop('close_only',None);rec['render_review']='PENDING — clean GPU pair must be opened';p.save_manifest(rec)
print('RERENDERED',name,flush=True)

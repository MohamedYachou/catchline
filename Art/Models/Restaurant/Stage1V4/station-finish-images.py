import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;rows={}
for d in [O.parent/'Stage1V2',O]:
 bpy.ops.wm.open_mainfile(filepath=(d/(d.name+'.blend')).as_posix())
 rows[d.name]=[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file),'exists':Path(bpy.path.abspath(im.filepath)).is_file()} for im in bpy.data.images if im.source=='FILE']
assert all(r['packed'] or r['exists'] for rows2 in rows.values() for r in rows2),rows
(O/'station-finish-image-links.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)

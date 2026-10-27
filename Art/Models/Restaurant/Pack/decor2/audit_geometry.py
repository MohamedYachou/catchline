"""Read actual binary FBX vertices, independent of Blender importer."""
from pathlib import Path
import json,math
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent;rows=[]
for r in json.loads((O/'manifest.json').read_text())['items']:
 root,version=parse_fbx.parse(str(O/(r['name']+'.fbx')))
 geometries=[a for e in root.elems if e.id==b'Objects' for a in e.elems if a.id==b'Geometry']
 coords=[list(a.props[0]) for g in geometries for a in g.elems if a.id==b'Vertices'][0]
 lo=[min(coords[j::3]) for j in range(3)];hi=[max(coords[j::3]) for j in range(3)]
 dim=[hi[i]-lo[i] for i in range(3)];checks=dict(single_geometry=len(geometries)==1,finite=all(math.isfinite(v) for v in coords),metre_dimensions=max(abs(dim[i]-r['size_unity_m'][i]) for i in range(3))<1e-5,centred_x=abs(lo[0]+hi[0])<1e-5)
 if r['mount']=='wall':checks.update(back_contact=abs(hi[2])<1e-5,front_negative_z=lo[2]<0,height_centred=abs(lo[1]+hi[1])<1e-5)
 else:checks.update(floor_y_zero=abs(lo[1])<1e-5,footprint_centred_z=abs(lo[2]+hi[2])<1e-5)
 rows.append(dict(name=r['name'],raw_fbx_bounds=[lo,hi],checks=checks))
(O/'geometry-audit.json').write_text(json.dumps(dict(pass_all=all(all(r['checks'].values()) for r in rows),items=rows),indent=2));print('GEOMETRY',len(rows),all(all(r['checks'].values()) for r in rows))

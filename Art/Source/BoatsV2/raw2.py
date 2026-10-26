import bpy,sys,json
from pathlib import Path
from io_scene_fbx import parse_fbx
R=Path(__file__).resolve().parents[3]
def prop(e):
 return [p.decode(errors='replace') if isinstance(p,bytes) else p for p in e.props]
def child(e,n):return next((c for c in e.elems if c.id==n),None)
rows={}
for name in ['CompactFisherV1','PrepFisherV1']:
 for version,path in [('old',R/f'Assets/Art/Models/Boats/{name}.fbx'),('new',R/f'Art/Models/BoatsV2/{name}/{name}.fbx')]:
  root,_=parse_fbx.parse(str(path));gs=child(root,b'GlobalSettings');objs=child(root,b'Objects');rec={'settings':[prop(p) for p in child(gs,b'Properties70').elems],'models':[],'geometry':[]}
  for e in objs.elems:
   if e.id==b'Model':
    props=child(e,b'Properties70');rec['models'].append({'identity':prop(e),'properties':[prop(p) for p in props.elems] if props else []})
   if e.id==b'Geometry':
    vs=child(e,b'Vertices');vs=vs.props[0] if vs else [];rec['geometry'].append({'identity':prop(e),'raw_bounds':[[min(vs[i::3]) for i in range(3)],[max(vs[i::3]) for i in range(3)]] if len(vs) else []})
  rows[name+'-'+version]=rec
(R/'Art/Source/BoatsV2/raw2.json').write_text(json.dumps(rows,indent=2));print('RAW FBX PARSE COMPLETE')

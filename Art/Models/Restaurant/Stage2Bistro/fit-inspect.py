import bpy,bmesh,json
from pathlib import Path
O=Path(__file__).resolve().parent
out={}
for s in ['Stage2Bistro','Stage3Restaurant','Stage4Seafood']:
 bpy.ops.wm.open_mainfile(filepath=str(O.parent/s/(s+'.blend')));ob=bpy.data.objects['RoomShell'];bm=bmesh.new();bm.from_mesh(ob.data);pending=set(bm.verts);rows=[]
 while pending:
  seed=pending.pop();comp={seed};stack=[seed]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in pending:pending.remove(v);comp.add(v);stack.append(v)
  p=[ob.matrix_world@v.co for v in comp];lo=[min(v[k] for v in p) for k in range(3)];hi=[max(v[k] for v in p) for k in range(3)]
  rows.append({'verts':len(comp),'lo':lo,'hi':hi})
 out[s]=rows;bm.free()
(O/'fit-shell-inventory.json').write_text(json.dumps(out,indent=2));print('INSPECT PASS')

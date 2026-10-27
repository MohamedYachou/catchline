import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V2'
names=['Stove','Oven','FridgeV2','Fryer','PrepCounter','SoupKettle','SinkDishRack','CoffeeBar']
bpy.ops.wm.open_mainfile(filepath=str(V/'Stage1V2.blend'));out={}
for name in names:
 root=bpy.data.objects[name];ob=next(o for o in root.children if o.type=='MESH');me=ob.data
 parent=list(range(len(me.vertices)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  a,b=map(find,e.vertices);parent[b]=a
 comps={}
 for v in me.vertices:comps.setdefault(find(v.index),[]).append(ob.matrix_basis@v.co)
 uv=me.uv_layers[0].data;cells={}
 for p in me.polygons:
  avg=sum((uv[i].uv for i in p.loop_indices),Vector((0.,0.)))/len(p.loop_indices);idx=min(3,max(0,int((1-avg.y)*4)))*8+min(7,max(0,int(avg.x*8)));cells.setdefault(find(p.vertices[0]),set()).add(idx)
 rows=[]
 for k,pts in comps.items():
  lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];dims=[hi[i]-lo[i] for i in range(3)]
  if set(cells[k])&{0,1,2,7}:rows.append({'component':k,'min':lo,'max':hi,'dim':dims,'cells':sorted(cells[k])})
 out[name]={'object':ob.name,'rootmatrix':list(map(list,root.matrix_world)),'matrixbasis':list(map(list,ob.matrix_basis)),'components':rows}
(O/'station-finish-inventory.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out),flush=True)

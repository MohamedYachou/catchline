import bpy,json,hashlib
from pathlib import Path
S=Path(__file__).resolve().parent;R=S.parents[3];O=R/'Art/Models/BoatsV2/Tier6';data={}
for n in ['Tier5DeepLines103','PrepFisherV1','CompactFisherV1','JigBoatV1']:
 p=R/'Art/Models/BoatsV2'/n/(n+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();rows=[]
 for ob in sorted(bpy.context.scene.objects,key=lambda o:o.name):
  pts=[ob.matrix_world@v.co for v in ob.data.vertices] if ob.type=='MESH' else [ob.matrix_world.translation]
  rows.append({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'position':[float(v) for v in ob.matrix_world.translation],'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons) if ob.type=='MESH' else 0})
 data[n]={'file':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':rows}
(S/'station-inventory.json').write_text(json.dumps(data,indent=2)+'\n')
with (O/'REPORT.md').open('a') as f:
 f.write('\n\n## TIER6-BOAT-1 STEP0 inventory — Codex 2 (WSL CLI)\n\nMo selected C Shelter Boat,10m, all earlier-tier equipment. This inventory was extracted directly from four accepted source blends before modelling. Full names, hierarchy, bounds and source SHA256 in `Art/Source/BoatsV2/Tier6/station-inventory.json`. Source coordinates X right,-Y bow,Z up,metres.\n')
 for n,d in data.items():
  f.write('\n### '+n+'\n\n| Object | Type | Parent | World position (m) |\n|---|---|---|---|\n')
  for v in d['objects']:
   f.write('| '+v['name']+' | '+v['type']+' | '+str(v['parent'])+' | '+str([round(x,4) for x in v['position']])+' |\n')
print('TIER6 INVENTORY PASS', {n:len(d['objects']) for n,d in data.items()})

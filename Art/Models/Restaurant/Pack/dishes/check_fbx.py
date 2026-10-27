import sys,json
from pathlib import Path
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent
rows=[]
for p in sorted(O.glob('Restaurant_*.fbx')):
 root,version=parse_fbx.parse(str(p))
 models=[];settings={}
 for e in root.elems:
  if e.id==b'Objects':
   for a in e.elems:
    if a.id!=b'Model':continue
    props={}
    for b in a.elems:
     if b.id==b'Properties70':
      for c in b.elems:
       if c.id==b'P':props[c.props[0].decode()]=[x.decode(errors='replace') if isinstance(x,bytes) else x for x in c.props[4:]]
    models.append(dict(name=a.props[1].decode(errors='replace'),properties=props))
  if e.id==b'GlobalSettings':
   for a in e.elems:
    if a.id==b'Properties70':
     for b in a.elems:
      if b.id==b'P':settings[b.props[0].decode()]=list(b.props[4:])
 checks=dict(one_model=len(models)==1,identity_rotation=all(max(abs(x) for x in m['properties'].get('Lcl Rotation',[0,0,0]))<1e-6 for m in models),identity_scaling=all(max(abs(x-1) for x in m['properties'].get('Lcl Scaling',[1,1,1]))<1e-6 for m in models),origin=all(max(abs(x) for x in m['properties'].get('Lcl Translation',[0,0,0]))<1e-6 for m in models),y_up=settings.get('UpAxis')==[1],metre_units=settings.get('UnitScaleFactor')==[100.0])
 rows.append(dict(file=p.name,version=version,models=models,global_settings=settings,checks=checks))
(O/'fbx-transform-audit.json').write_text(json.dumps(dict(pass_all=all(all(r['checks'].values()) for r in rows),items=rows),indent=2,default=str))
print('RAW_FBX',len(rows),'PASS',all(all(r['checks'].values()) for r in rows))
print(json.dumps(rows[0],indent=2,default=str))

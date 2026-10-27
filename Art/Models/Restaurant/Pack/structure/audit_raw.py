"""Independent binary FBX transform/geometry checks for four overhead structures."""
import json,math
from pathlib import Path
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent;trans=[];geo=[]
for r in json.loads((O/'manifest.json').read_text())['items']:
 root,ver=parse_fbx.parse(str(O/(r['name']+'.fbx')));models=[];settings={};geometries=[];materials=[]
 for e in root.elems:
  if e.id==b'Objects':
   for a in e.elems:
    if a.id==b'Geometry':geometries.append(a)
    if a.id==b'Material':materials.append(a.props[1].decode(errors='replace').split('\x00')[0])
    if a.id!=b'Model':continue
    props={c.props[0].decode():list(c.props[4:]) for b in a.elems if b.id==b'Properties70' for c in b.elems if c.id==b'P'}
    models.append(dict(name=a.props[1].decode(errors='replace').split('\x00')[0],properties=props,type=a.props[2].decode()))
  if e.id==b'GlobalSettings':
   settings={b.props[0].decode():list(b.props[4:]) for a in e.elems if a.id==b'Properties70' for b in a.elems if b.id==b'P'}
 checks=dict(exact_model_count=len(models)==(2 if r['glow_mesh'] else 1),named_meshes={m['name'] for m in models}==({r['name'],r['glow_mesh']} if r['glow_mesh'] else {r['name']}),only_meshes=all(m['type']=='Mesh' for m in models),identity_rotation=all(max(abs(x) for x in m['properties'].get('Lcl Rotation',[0,0,0]))<1e-6 for m in models),identity_scaling=all(max(abs(x-1) for x in m['properties'].get('Lcl Scaling',[1,1,1]))<1e-6 for m in models),origin=all(max(abs(x) for x in m['properties'].get('Lcl Translation',[0,0,0]))<1e-6 for m in models),y_up=settings.get('UpAxis')==[1],metre_units=settings.get('UnitScaleFactor')==[100.0],glow_material=(r['glow_material'] in materials) if r['glow_mesh'] else not any(m.endswith('_Glow') for m in materials))
 trans.append(dict(name=r['name'],version=ver,checks=checks,models=models,global_settings=settings,materials=materials))
 coords=[list(a.props[0]) for g in geometries for a in g.elems if a.id==b'Vertices'];flat=[c for cs in coords for c in cs]
 lo=[min(min(cs[j::3]) for cs in coords) for j in range(3)];hi=[max(max(cs[j::3]) for cs in coords) for j in range(3)];dim=[hi[i]-lo[i] for i in range(3)]
 c=dict(exact_geometry_count=len(geometries)==(2 if r['glow_mesh'] else 1),nonempty=all(len(cs)>0 for cs in coords),finite=all(math.isfinite(x) for x in flat),metre_dimensions=max(abs(dim[i]-r['size_unity_m'][i]) for i in range(3))<1e-5,centred_x=abs(lo[0]+hi[0])<1e-5)
 if r['mount']=='wall':c.update(back_contact=abs(hi[2])<1e-5,front_negative_z=lo[2]<0,top_mount=abs(hi[1])<1e-5)
 elif r['mount']=='ceiling':c.update(ceiling_contact=abs(hi[1])<1e-5,hanging_below=lo[1]<0,depth_centred=abs(lo[2]+hi[2])<1e-5)
 else:c.update(floor_y_zero=abs(lo[1])<1e-5,depth_centred=abs(lo[2]+hi[2])<1e-5)
 geo.append(dict(name=r['name'],bounds=[lo,hi],checks=c))
for name,rows in [('fbx-transform-audit',trans),('geometry-audit',geo)]:
 result=dict(pass_all=all(all(r['checks'].values()) for r in rows),items=rows);(O/(name+'.json')).write_text(json.dumps(result,indent=2,default=str));print(name,result['pass_all'],flush=True)

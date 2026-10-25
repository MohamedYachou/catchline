"""Assert actual FBX Y-up metre geometry, identity model transforms and Fill."""
import sys,json,math
from pathlib import Path
from io_scene_fbx import parse_fbx
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/NetKit'
def props(e):
    p=next((c for c in e.elems if c.id==b'Properties70'),None)
    return {c.props[0].decode():[v.decode() if isinstance(v,bytes) else v for v in c.props[4:]] for c in p.elems} if p else {}
rows={}
for name in ('NetBunt','NetPanelSet'):
    root,version=parse_fbx.parse(str(O/(name+'.fbx')))
    settings=props(next(e for e in root.elems if e.id==b'GlobalSettings'))
    for key,value in dict(UpAxis=1,UpAxisSign=1,CoordAxis=0,CoordAxisSign=1,FrontAxis=2,FrontAxisSign=1,UnitScaleFactor=100).items():
        assert settings[key]==[value],(name,key,settings[key])
    objects=next(e for e in root.elems if e.id==b'Objects')
    models={e.props[1].split(b'\x00')[0].decode():props(e) for e in objects.elems if e.id==b'Model'}
    metrics=json.loads((O/'metrics'/(name+'.json')).read_text())
    assert set(models)==set(metrics['parents'])
    for n,p in models.items():
        assert max(abs(v) for v in p.get('Lcl Rotation',[0,0,0]))<1e-6,(n,p)
        assert max(abs(v-1) for v in p.get('Lcl Scaling',[1,1,1]))<1e-6,(n,p)
        expected=[0,-.09,.31] if n=='Fill' else [0,0,0]
        assert max(abs(v-w) for v,w in zip(p.get('Lcl Translation',[0,0,0]),expected))<1e-6,(n,p)
    raw={}
    for e in objects.elems:
        if e.id!=b'Geometry' or e.props[-1]!=b'Mesh':continue
        n=e.props[1].split(b'\x00')[0].decode().removesuffix('_Mesh')
        vals=next(c for c in e.elems if c.id==b'Vertices').props[0]
        assert all(math.isfinite(v) for v in vals)
        dimensions=[max(vals[i::3])-min(vals[i::3]) for i in range(3)]
        expected=metrics['model_dimensions_unity'][n]
        error=max(abs(a-b) for a,b in zip(dimensions,expected));assert error<2e-5,(n,dimensions,expected)
        raw[n]={'dimensions_y_up_metres':dimensions,'maximum_dimension_error_metres':error}
    assert set(raw)==set(metrics['model_dimensions_unity'])
    row={'result':'PASS','fbx_version':version,'global_settings':settings,'model_transforms':models,'raw_meshes':raw};rows[name]=row
    print('RAW FBX',name,json.dumps(row),flush=True)
(O/'metrics/fbx-axes.json').write_text(json.dumps(rows,indent=2)+'\n')
print('NET AXES PASS',flush=True)

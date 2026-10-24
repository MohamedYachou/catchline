"""Verify hair-only changes against immutable input and run actual FBX audit."""
import bpy, sys, json, hashlib, argparse
from pathlib import Path
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--name',required=True);N=p.parse_args(sys.argv[sys.argv.index('--')+1:]).name
O=R/'Art/Models/CrewV2'/('Mira-sol' if N=='Mira' else N);B=O/'iterations/hairfix-before'
def digest(ob):
    return hashlib.sha256(repr(([tuple(v.co) for v in ob.data.vertices],
      [(tuple(poly.vertices),poly.material_index) for poly in ob.data.polygons],
      [[(ob.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in ob.data.vertices])).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(B/(N+'.blend')))
m=json.loads((B/'build-manifest.json').read_text())
before={n:digest(bpy.data.objects[n]) for n in m['meshes'] if 'Hair' not in n}
bpy.ops.wm.open_mainfile(filepath=str(O/(N+'.blend')))
assert before=={n:digest(bpy.data.objects[n]) for n in before},'Non-hair changed'
for texture in B.glob(N+'_*.png'):
    assert hashlib.sha256(texture.read_bytes()).digest()==hashlib.sha256((O/texture.name).read_bytes()).digest()
(O/'hairfix-preservation.json').write_text(json.dumps({'all_passed':True,'unchanged_nonhair_meshes':before,'textures_unchanged':True},indent=2))
script=R/'Art/Source'/('validate_mira_sol.py' if N=='Mira' else 'validate_crew_male.py')
exec(compile(script.read_text(),str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
v=json.loads((O/'validation.json').read_text());v['name']=N;v['revision']=json.loads((O/'build-manifest.json').read_text())['revision']
v['delivery_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [O/(N+'.blend'),O/(N+'.fbx')]+list(O.glob(N+'_*.png'))}
(O/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print('HAIRFIX PRESERVATION AND ACTUAL FBX PASS',N,flush=True)

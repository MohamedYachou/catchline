import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
names=['Stage1V4','Stage2Bistro','Stage3Restaurant','Stage4Seafood']
report={}
for name in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    p=R/'Assets/Resources/Restaurant'/f'{name}.fbx'
    bpy.ops.import_scene.fbx(filepath=str(p),use_anim=False)
    obs=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        vs=[o.matrix_world@Vector(v) for v in o.bound_box]
        obs.append(dict(name=o.name,lo=[min(v[i] for v in vs) for i in range(3)],hi=[max(v[i] for v in vs) for i in range(3)],triangles=sum(len(f.vertices)-2 for f in o.data.polygons),materials=[m.name if m else None for m in o.data.materials],uvs=[list(o.data.uv_layers.active.data[j].uv) for j in range(min(4,len(o.data.loops)))] if o.data.uv_layers else []))
    report[name]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),objects=obs)
(OUT/'room-inspection.json').write_text(json.dumps(report,indent=2))
for name,r in report.items():
    print(name,'objects',len(r['objects']))
    for o in r['objects']:
        if any(n in o['name'].lower() for n in ['floor','deck','terrace','wall','jetty','platform']):print(o)

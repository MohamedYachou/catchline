"""FBX round-trip checks, run in Blender. Never imports into Unity."""
import bpy,json,hashlib,math,sys,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from collections import Counter
R=Path(__file__).resolve().parents[3]
O=R/'Art/Models/GullHarbour/HarbourV2'
def geometry():
    bpy.context.view_layer.update()
    rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name.startswith('Preview'):continue
        o.data.calc_loop_triangles()
        rows[o.name]={'vertices':[tuple(o.matrix_world@v.co) for v in o.data.vertices],
          'triangles':[tuple(t.vertices) for t in o.data.loop_triangles],
          'faces':[tuple(p.vertices) for p in o.data.polygons]}
    return rows
def same_geometry(ref,other):
    assert ref.keys()==other.keys(),(ref.keys(),other.keys())
    worst=0
    for name,a in ref.items():
        b=other[name]
        assert len(a['vertices'])==len(b['vertices']) and len(a['triangles'])==len(b['triangles']) and len(a['faces'])==len(b['faces']),name
        # Collapse coincident seam vertices only for point correspondence; full
        # source vertex/triangle counts must still agree. Triangle multiplicities
        # preserve the surface even when FBX reorders vertex/index buffers.
        pts=list(dict.fromkeys(a['vertices']));kd=KDTree(len(pts))
        for i,p in enumerate(pts):kd.insert(p,i)
        kd.balance()
        # Canonical FBXs contain seam duplicates differing by float rounding
        # (e.g. 0.00000006m). Give those points a common correspondence ID so
        # equally close imported vertices cannot choose different seam copies.
        correspondence={}
        for i,p in enumerate(pts):
            if i in correspondence:continue
            for _,j,_ in kd.find_range(p,.000001):
                if j not in correspondence:correspondence[j]=i
        def mapped(row):
            nonlocal worst
            ids=[]
            for p in row['vertices']:
                _,i,d=kd.find(p);worst=max(worst,d)
                assert d<.00002,(name,d)
                ids.append(correspondence[i])
            def cycle(face):
                q=tuple(ids[i] for i in face)
                rev=q[::-1]
                return min([q[i:]+q[:i] for i in range(len(q))]+[rev[i:]+rev[:i] for i in range(len(q))])
            return Counter(cycle(f) for f in row['faces'])
        ca,cb=mapped(a),mapped(b)
        assert ca==cb,('polygon surface differs',name,
          [(tuple(pts[i] for i in t),count) for t,count in list((ca-cb).items())[:2]],
          [(tuple(pts[i] for i in t),count) for t,count in list((cb-ca).items())[:2]])
    return {'result':'PASS','mesh_count':len(ref),'max_vertex_error_metres':worst,
      'method':'world vertices, vertex/face/triangle counts and every ordered polygon cycle/multiplicity;20micrometre match tolerance,1micrometre canonical seam correspondence'}
def snapshot():
    bpy.context.view_layer.update()
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Preview')]
    pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    return {'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),
      'meshes':len(meshes),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],
      'materials':sorted({o.data.materials[p.material_index].name for o in meshes for p in o.data.polygons}),
      'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects if not o.name.startswith('Preview')},
      'finite':all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)}
def audit(name):
    row=json.loads((O/'metrics'/(name+'.json')).read_text())
    bpy.ops.wm.open_mainfile(filepath=str(O/(name+'.blend')))
    src=snapshot()
    assert src['triangles']==row['triangles']
    variant=row.get('canonical_source')
    assert src['triangles']<row['limit'] or (variant and row.get('budget_status')=='INHERITED EXCEPTION: exact released hull geometry')
    srcgeo=geometry() if variant else None
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(O/(name+'.fbx')))
    imp=snapshot()
    assert imp['finite'] and imp['triangles']==src['triangles'] and imp['meshes']==src['meshes'],(name,src,imp)
    delta=max(abs(src['bounds'][a][i]-imp['bounds'][a][i]) for a in range(2) for i in range(3))
    assert delta<.0002,(name,delta)
    assert imp['materials']==src['materials'],(name,src['materials'],imp['materials'])
    assert name in imp['parents'] and imp['parents'][name] is None,(name,imp['parents'])
    if name=='QuayCrane':assert imp['parents']['Jib']==name
    if variant:
        row['geometry_round_trip']=same_geometry(srcgeo,geometry())
        canonical=R/variant['path'].replace('\\','/')
        assert hashlib.sha256(canonical.read_bytes()).hexdigest()==variant['sha256']
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(canonical))
        row['canonical_geometry_identity']=same_geometry(geometry(),srcgeo)
    for k in ('blend','fbx'):
        assert hashlib.sha256((O/(name+'.'+k)).read_bytes()).hexdigest()==row['sha256'][k]
    row['round_trip']={'result':'PASS','bounds_max_error_metres':delta,'source':src,'imported':imp}
    row['status']='source/FBX PASS; visual review recorded separately; assembly/native pending'
    (O/'metrics'/(name+'.json')).write_text(json.dumps(row,indent=2))
    print('HARBOUR AUDIT PASS',name,'tris',imp['triangles'],'metres error',delta,flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--name',required=True)
    a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);audit(a.name)

"""Independent fresh-FBX geometry/material/hierarchy/blendshape checks."""
import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build as B
sys.path.insert(0,str(B.R/'Art/Source/HarbourV2'))
import audit as A
def geometry(state=0):
    if 'Bunt' in bpy.data.objects:
        o=bpy.data.objects['Bunt'];o.data.shape_keys.key_blocks['Taut'].value=state
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        e=o.evaluated_get(dg);m=e.data;m.calc_loop_triangles()
        rows[o.name]={'vertices':[tuple(e.matrix_world@v.co) for v in m.vertices],
          'triangles':[tuple(t.vertices) for t in m.loop_triangles],
          'faces':[tuple(p.vertices) for p in m.polygons]}
    return rows
def dims(geo):
    p=[Vector(p) for row in geo.values() for p in row['vertices']]
    return [max(v[i] for v in p)-min(v[i] for v in p) for i in (0,2,1)]
def run(name):
    path=B.O/'metrics'/(name+'.json');row=json.loads(path.read_text())
    bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')))
    source=B.snapshot();base=geometry();taut=geometry(1) if name=='NetBunt' else None
    assert source['triangles']<row['limit']
    if name=='NetPanelSet':assert all(v['triangles']<800 for v in source['objects'].values())
    protected={o.name:tuple(o.location) for o in bpy.context.scene.objects if o.type=='EMPTY'}
    mats={m.name:tuple(m.diffuse_color) for m in bpy.data.materials if m.users}
    shape_names=[]
    model_dimensions={n:dims({n:g}) for n,g in base.items()}
    assert all(math.isfinite(c) for g in base.values() for p in g['vertices'] for c in p)
    if name=='NetBunt':
        o=bpy.data.objects['Bunt'];shape_names=list(o.data.shape_keys.key_blocks.keys())
        assert shape_names==['Basis','Slack','Taut']
        assert max((a.co-b.co).length for a,b in zip(o.data.shape_keys.key_blocks['Basis'].data,o.data.shape_keys.key_blocks['Slack'].data))<1e-8
        assert 'Fill' in protected and (Vector(protected['Fill'])-Vector(B.to_b((0,-.09,.31)))).length<1e-7
        d0,d1=dims(base),dims(taut)
        assert .98<d0[0]<1.16 and .70<d0[1]<.9 and .69<d0[2]<.83,d0
        assert d1[0]<d0[0]*.9 and d1[2]>d0[2]*1.3,(d0,d1)
        key=o.data.shape_keys.key_blocks
        fixed=[(a.co-b.co).length for a,b in zip(key['Basis'].data,key['Taut'].data) if B.to_u(a.co)[2]<=.045]
        assert fixed and max(fixed)<1e-7,('mouth band moved',max(fixed))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(B.O/(name+'.fbx')))
    imported=B.snapshot();proof=A.same_geometry(base,geometry())
    assert imported['parents']==source['parents'],(source['parents'],imported['parents'])
    assert imported['materials']==source['materials']
    assert imported['triangles']==source['triangles']
    assert all(abs(v-1)<2e-5 for o in bpy.context.scene.objects for v in o.scale)
    for n,p in protected.items():assert (bpy.data.objects[n].matrix_world.translation-Vector(p)).length<2e-5,(n,p)
    colour_error=max(abs(c-d) for m in bpy.data.materials if m.name in mats for c,d in zip(m.diffuse_color,mats[m.name]))
    assert colour_error<1e-5,colour_error
    shape_proof=None
    if name=='NetBunt':
        imported_shapes=list(bpy.data.objects['Bunt'].data.shape_keys.key_blocks.keys())
        assert set(imported_shapes)==set(shape_names),(imported_shapes,shape_names)
        shape_proof=A.same_geometry(taut,geometry(1))
        # Halfway shape must actually deform; no NaNs or silently dropped blendshapes.
        half=geometry(.5);movement=max((Vector(a)-Vector(b)).length for a,b in zip(base['Bunt']['vertices'],half['Bunt']['vertices']))
        assert movement>.10,movement
        shape_proof.update(source_names=shape_names,imported_names=imported_shapes,
                           slack_dimensions_unity=dims(base),taut_dimensions_unity=dims(taut),
                           half_weight_movement_m=movement)
    for ext in ('blend','fbx'):assert B.sha(B.O/(name+'.'+ext))==row['sha256'][ext]
    row.update(status='actual FBX geometry/controls PASS; visual review separate',
      model_dimensions_unity=model_dimensions,
      round_trip={'result':'PASS','geometry':proof,'taut_geometry':shape_proof,
                  'source':source,'imported':imported,'material_colour_max_error':colour_error,
                  'empty_pivots':'PASS','positive_unit_scales':'PASS'})
    path.write_text(json.dumps(row,indent=2)+'\n')
    print('NET AUDIT PASS',name,source['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])

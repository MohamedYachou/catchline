"""Independent FBX reimport. Exact surfaces, weights, animation deformation, budgets."""
import bpy,sys,json,math,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
spec=importlib.util.spec_from_file_location('harbour_geometry',str(B.R/'Art/Source/HarbourV2/audit.py'));A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
def geometry(evaluated=False):
    bpy.context.view_layer.update();rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else o
        e.data.calc_loop_triangles();rows[o.name]={'vertices':[tuple(e.matrix_world@v.co) for v in e.data.vertices],'triangles':[tuple(t.vertices) for t in e.data.loop_triangles],'faces':[tuple(p.vertices) for p in e.data.polygons]}
    return rows

def pose_samples():
    rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');sc=bpy.context.scene;rows={};info={}
    for name in ('Bask','Look','Slide'):
        matches=[a for a in bpy.data.actions if a.name.split('|')[-1]==name];assert len(matches)==1,(name,[a.name for a in bpy.data.actions])
        action=matches[0];rig.animation_data.action=action
        end={'Bask':121,'Look':91,'Slide':37}[name]
        assert abs(action.frame_range[0]-1)<.01 and abs(action.frame_range[1]-end)<.01,(name,list(action.frame_range))
        rows[name]={}
        for f in [1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end]:
            sc.frame_set(f);rows[name][f]=geometry(True)
        pts=lambda f:[v for row in rows[name][f].values() for v in row['vertices']]
        p0=pts(1);pend=pts(end);mid=pts(1+(end-1)//4)
        drift=max((Vector(a)-Vector(b)).length for a,b in zip(p0,pend))
        move=max((Vector(a)-Vector(b)).length for a,b in zip(p0,mid))
        assert move>.003,(name,move)
        if name!='Slide':assert drift<.00002,(name,drift)
        else:assert drift>1.8,(name,drift)
        info[name]={'action':action.name,'frames':[1,end],'seconds':(end-1)/30,'sampled_frames':list(rows[name]),'end_vertex_displacement_max_m':drift,'quarter_vertex_displacement_max_m':move}
    rig.animation_data.action=next(a for a in bpy.data.actions if a.name.split('|')[-1]=='Bask');sc.frame_set(1)
    return rows,info

def run(name):
    path=B.O/'metrics'/(name+'.json');row=json.loads(path.read_text())
    bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));src=B.snapshot();geo=geometry()
    assert src['finite'] and src['triangles']<row['limit']
    root=bpy.data.objects[name];assert root.parent is None and root.location.length<1e-6 and all(abs(v-1)<1e-6 for v in root.scale)
    assert not list(bpy.data.images),[i.name for i in bpy.data.images]
    for o in bpy.context.scene.objects:
        if o.type=='MESH':assert not o.data.validate(verbose=True,clean_customdata=False),('invalid source mesh',o.name)
    animation=None
    if name=='Seal':
        skin=bpy.data.objects['SealSkin'];weights=[]
        for v in skin.data.vertices:
            w=sum(g.weight for g in v.groups);assert abs(w-1)<1e-5,(v.index,w);weights.append(w)
        animation,srcactions=pose_samples()
        assert len(bpy.data.objects['SealRig'].data.bones)==6
    if name.startswith('ReefBreak'):
        o=bpy.data.objects['BrokenWater'];assert o.data.uv_layers.active
        assert max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices)<1e-8
        assert all(p.normal.z>.999 for p in o.data.polygons)
        for p in o.data.polygons:
            for li in p.loop_indices:assert all(-1e-5<=c<=1.00001 for c in o.data.uv_layers.active.data[li].uv)
    if name=='SealSwimHead':assert all(p.normal.z>.999 for p in bpy.data.objects['VWake'].data.polygons)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30
    bpy.ops.import_scene.fbx(filepath=str(B.O/(name+'.fbx')))
    imp=B.snapshot();importgeo=geometry()
    if name.startswith('ReefBreak'):
        o=bpy.data.objects['BrokenWater'];assert o.data.uv_layers.active
        for p in o.data.polygons:
            assert (o.matrix_world.to_3x3().inverted().transposed()@p.normal).z>.999
            for li in p.loop_indices:
                co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
                uv=o.data.uv_layers.active.data[li].uv
                assert abs(uv.x-(co.x+3)/6)<1e-5 and abs(uv.y-(co.y+1)/2)<1e-5
    if name=='SealSwimHead':
        o=bpy.data.objects['VWake']
        assert all((o.matrix_world.to_3x3().inverted().transposed()@p.normal).z>.999 for p in o.data.polygons)
    for n in geo:
        a,b=geo[n],importgeo[n]
        assert [len(a[k]) for k in ('vertices','faces','triangles')]==[len(b[k]) for k in ('vertices','faces','triangles')],(n,'source/import counts',{k:[len(a[k]),len(b[k])] for k in ('vertices','faces','triangles')})
    proof=A.same_geometry(geo,importgeo)
    assert imp['triangles']==src['triangles'] and imp['materials']==src['materials'],(src,imp)
    assert imp['parents']==src['parents'],(src['parents'],imp['parents'])
    assert all(abs(v-1)<2e-5 for o in bpy.context.scene.objects for v in o.scale)
    animproof={}
    if animation:
        samples,impactions=pose_samples()
        for action,frames in samples.items():
            checks={str(f):A.same_geometry(animation[action][f],g) for f,g in frames.items()}
            animproof[action]={'result':'PASS','source':srcactions[action],'imported':impactions[action],'deformed_surface_checks':checks}
        assert all(o.modifiers and any(m.type=='ARMATURE' for m in o.modifiers) for o in bpy.context.scene.objects if o.type=='MESH')
    for e in ('blend','fbx'):assert B.sha(B.O/(name+'.'+e))==row['sha256'][e]
    row['round_trip']={'result':'PASS','source':src,'imported':imp,'geometry':proof,'animation':animproof}
    row['status']='Source and actual FBX PASS; visual review pending'
    path.write_text(json.dumps(row,indent=2)+'\n');print('SKERRIES AUDIT PASS',name,src['triangles'],json.dumps(animproof)[:180],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])

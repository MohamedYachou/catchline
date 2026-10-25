"""Independent fresh FBX readback, topology/world surfaces and deformed animation."""
import sys,json,math,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
spec=importlib.util.spec_from_file_location('geo_audit',str(B.R/'Art/Source/HarbourV2/audit.py'));A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
def geo(evaluate=False):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        e=o.evaluated_get(dg) if evaluate else o;e.data.calc_loop_triangles()
        rows[o.name]={'vertices':[tuple(e.matrix_world@v.co) for v in e.data.vertices],'triangles':[tuple(t.vertices) for t in e.data.loop_triangles],'faces':[tuple(p.vertices) for p in e.data.polygons]}
    return rows

def poses():
    rig=bpy.data.objects['GullRig'];sc=bpy.context.scene;sc.render.fps=30;res={};info={}
    for name,end in [('Idle',121),('Lunge',31)]:
        acts=[a for a in bpy.data.actions if a.name.split('|')[-1]==name];assert len(acts)==1,(name,[a.name for a in bpy.data.actions])
        a=acts[0];assert abs(a.frame_range[0]-1)<.01 and abs(a.frame_range[1]-end)<.01
        rig.animation_data.action=a;res[name]={}
        for f in [1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end]:sc.frame_set(f);res[name][f]=geo(True)
        verts=lambda f:res[name][f]['GullSkin']['vertices']
        delta=lambda f:max((Vector(p)-Vector(q)).length for p,q in zip(verts(1),verts(f)))
        closure=delta(end);motion=max(delta(f) for f in res[name]);assert closure<2e-5 and motion>.003,(name,closure,motion)
        if name=='Lunge':assert motion>.15,(name,motion)
        info[name]={'action':a.name,'frames':[1,end],'seconds':(end-1)/30,'loop':name=='Idle','sampled_frames':list(res[name]),'max_motion_m':motion,'closure_m':closure}
    return res,info

def run():
    bpy.ops.wm.open_mainfile(filepath=str(B.O/'GutKit.blend'));src=B.snapshot();g=geo();posesrc,ainfo=poses()
    assert set(src['meshes'])==set(B.LIMITS)
    assert src['parents']=={'GutKit':None,'GutBoard':'GutKit','GutKnife':'GutKit','BellyOpen':'GutKit','BellyRagged':'GutKit','GutBucket':'GutKit','GullPerch':'GutKit','GullSkin':'GullRig','GullRig':'GullPerch'}
    for n,v in src['meshes'].items():
        assert v['triangles']<=B.LIMITS[n]
        o=bpy.data.objects[n];assert not o.data.validate(verbose=True,clean_customdata=False)
        used=set(i for p in o.data.polygons for i in p.vertices);assert len(used)==len(o.data.vertices),(n,'loose vertices')
        assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
        assert all(p.area>1e-12 for p in o.data.polygons),(n,'zero area')
        assert o.location.length<1e-7 and o.rotation_euler.to_matrix().is_identity and tuple(o.scale)==(1,1,1)
        if n.startswith('Belly'):
            assert all(p.normal.z>.1 for p in o.data.polygons)
            assert abs(v['bounds_unity'][0][0])<1e-6 and abs(v['bounds_unity'][1][0]-1)<1e-6
    assert all(abs(sum(w.weight for w in v.groups)-1)<1e-6 for v in bpy.data.objects['GullSkin'].data.vertices)
    assert len(bpy.data.objects['GullRig'].data.bones)==4
    assert not list(bpy.data.images)
    colors={m.name:list(m.diffuse_color) for m in bpy.data.materials}
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30
    bpy.ops.import_scene.fbx(filepath=str(B.O/'GutKit.fbx'))
    imp=B.snapshot();ig=geo();assert imp['parents']==src['parents'],imp['parents']
    assert imp['triangles']==src['triangles']
    surface=A.same_geometry(g,ig)
    for n in g:assert len(g[n]['vertices'])==len(ig[n]['vertices']) and len(g[n]['faces'])==len(ig[n]['faces'])
    for o in bpy.context.scene.objects:
        assert max(abs(x-1) for x in o.scale)<2e-5,(o.name,list(o.scale))
        if o.type=='MESH':assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
    for m in bpy.data.materials:assert max(abs(a-b) for a,b in zip(m.diffuse_color,colors[m.name]))<1e-5,(m.name,list(m.diffuse_color),colors[m.name])
    poseimp,iinfo=poses();anim={}
    for name,frames in posesrc.items():anim[name]={'result':'PASS','source':ainfo[name],'import':iinfo[name],'geometry_samples':{str(f):A.same_geometry(frames[f],poseimp[name][f]) for f in frames}}
    build=json.loads((B.O/'metrics/build.json').read_text())
    for e in ('blend','fbx'):assert B.sha(B.O/('GutKit.'+e))==build['sha256'][e]
    row={'result':'PASS','source':src,'imported':imp,'surfaces':surface,'animation':anim,'material_colors':colors,'sha256':build['sha256']}
    (B.O/'metrics/roundtrip.json').write_text(json.dumps(row,indent=2)+'\n');print('GUT AUDIT PASS',src['triangles'],json.dumps(ainfo),flush=True)
if __name__=='__main__':run()

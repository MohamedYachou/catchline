"""Five true orthographic studios; actual action samples and fitted45deg fixture."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
sp=importlib.util.spec_from_file_location('skerries_render_reference',str(B.R/'Art/Source/Skerries/render.py'));V=importlib.util.module_from_spec(sp);sp.loader.exec_module(V)

def points():
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    return [o.evaluated_get(dg).matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Review') for v in o.evaluated_get(dg).data.vertices]

def fitted(sc,cam,p,direction):
    cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL'
    centre=Vector(tuple((min(v[i] for v in p)+max(v[i] for v in p))*.5 for i in range(3)))
    V.look(cam,centre,direction);bpy.context.view_layer.update()
    basis=cam.rotation_euler.to_matrix();u=basis@Vector((1,0,0));v=basis@Vector((0,1,0))
    lo_u,hi_u=min(q.dot(u) for q in p),max(q.dot(u) for q in p)
    lo_v,hi_v=min(q.dot(v) for q in p),max(q.dot(v) for q in p)
    centre+=u*((lo_u+hi_u)/2-centre.dot(u))+v*((lo_v+hi_v)/2-centre.dot(v))
    V.look(cam,centre,direction)
    cam.data.ortho_scale=max(hi_u-lo_u,(hi_v-lo_v)*sc.render.resolution_x/sc.render.resolution_y)*1.30
    bpy.context.view_layer.update()

def run(name):
    bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));sc,cam=V.stage();sc.cycles.samples=20
    p=points();floor=min(v.z for v in p)-.014;V.plane(floor,'#18363B' if name=='LighthouseGlow' else '#C9D1CC');rows=[];out=B.O/'renders'/name
    def save(label,size,extra=None):
        sc.render.resolution_x,sc.render.resolution_y=size;path=out/(label+'.png');
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update();cs=[world_to_camera_view(sc,cam,p) for p in points()];margin=[min(v.x for v in cs),min(v.y for v in cs),max(v.x for v in cs),max(v.y for v in cs)]
        assert min(margin[:2])>.03 and max(margin[2:])<.97,('studio crop',name,label,margin)
        V.render(sc,path);rows.append({'file':path.relative_to(B.O).as_posix(),'view':label,'size':size,**(extra or {})})
    sc.render.resolution_x=720;sc.render.resolution_y=600
    for label,direction in [('three-quarter',(1,-1,1)),('front',(0,-1,0)),('right',(1,0,0)),('back',(0,1,0)),('top',(0,0,1))]:
        fitted(sc,cam,p,direction);save(label,(720,600),{'projection':'orthographic'})
    if name in B.CLIPS:
        # Remove the floor under a diving bird; all poses have the same framing.
        bpy.data.objects['ReviewGround'].hide_render=True;rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];sc.render.resolution_x=640;sc.render.resolution_y=480
        allpoints=[]
        for action,(end,_) in B.CLIPS[name].items():
            
            for rig in rigs:
                rig.animation_data.action=bpy.data.actions[action];rig.animation_data.action_slot=rig.animation_data.action.slots[0]
            for f in (1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end):sc.frame_set(f);allpoints+=points()
        fitted(sc,cam,allpoints,(1,-1,1))
        for action,(end,_) in B.CLIPS[name].items():
            
            for rig in rigs:
                rig.animation_data.action=bpy.data.actions[action];rig.animation_data.action_slot=rig.animation_data.action.slots[0]
            for i,f in enumerate((1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end)):
                sc.frame_set(f);save('action-'+action+'-'+str(i),(640,480),{'action':action,'frame':f,'seconds':(f-1)/30})
    if name=='Humpback':
        # Extra opaque waterline samples expose the gesture, not the submerged mesh.
        ground=bpy.data.objects['ReviewGround'];ground.hide_render=False;ground.location.z=0
        ground.data.materials.clear();ground.data.materials.append(B.H.material('ReviewWater','#168F9F',.65))
        out=B.O/'renders'/'FixWater'
        for action in ('Surface','Fluke'):
            rig=rigs[0];rig.animation_data.action=bpy.data.actions[action];rig.animation_data.action_slot=rig.animation_data.action.slots[0]
            end=B.CLIPS[name][action][0];frames=(1,23,46,68,91)
            sc.render.resolution_x=640;sc.render.resolution_y=480
            # Fixed camera for both complete events, centred at the surface.
            fitted(sc,cam,[Vector((x,y,z)) for x in (-3.3,3.3) for y in (-4.3,4.5) for z in (-.2,3.1)],(.574,-.819,1))
            for i,f in enumerate(frames):
                sc.frame_set(f);path=out/(action+'-'+str(i)+'.png');V.render(sc,path)
                rows.append({'file':path.relative_to(B.O).as_posix(),'size':[640,480],'action':action,'frame':f,'opaque_waterline_z_m':0,'camera_down_degrees':45})
    (B.O/'renders'/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n');print('WHALE SHELF RENDERS',name,len(rows),flush=True)

def append_asset(name,location,rename,clip=None,frame=1):
    with bpy.data.libraries.load(str(B.O/(name+'.blend')),link=False) as (src,dst):
        dst.objects=src.objects
        if clip:dst.actions=src.actions
    objects=[o for o in dst.objects if o];root=next(o for o in objects if o.parent is None)
    for o in objects:bpy.context.scene.collection.objects.link(o)
    root.name=rename;root.location=location
    if clip:
        act=next(a for a in dst.actions if a and a.name.split('.')[0]==clip)
        for rig in [o for o in objects if o.type=='ARMATURE']:
            rig.animation_data.action=act;rig.animation_data.action_slot=act.slots[0]
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        for rig in [o for o in objects if o.type=='ARMATURE']:
            bases={pb.name:pb.matrix_basis.copy() for pb in rig.pose.bones};rig.animation_data_clear()
            for n,m in bases.items():rig.pose.bones[n].matrix_basis=m
        root['sampled_clip']=clip;root['sampled_frame']=frame
    return root

def assembly():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    sc,cam=V.stage();sc.cycles.samples=24;V.plane(-.015,'#1C6E7E')
    for name,loc,label,clip,frame in [
        ('Humpback',(0,0,0),'SurfacingWhale','Blow',23),
        ('BlowSpout',(0,-2.6,.17),'Breath',None,1),
        ('KittiwakeFlock',(-4.8,2.3,0),'WheelingFlock','Circle',16),
        ('BaitBall',(-3.5,-1.3,0),'FeedingPatch','Swirl',16)]:append_asset(name,loc,label,clip,frame)
    # A shallow transparent house-teal review surface keeps the bait patch visible.
    water=bpy.data.objects['ReviewGround'];mat=water.data.materials[0]
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Transmission Weight'].default_value=.45;bs.inputs['Roughness'].default_value=.22;bs.inputs['IOR'].default_value=1.08
    p=points();sc.render.resolution_x=844;sc.render.resolution_y=390;fitted(sc,cam,p,(.574,-.819,1));span=cam.data.ortho_scale
    rows=[]
    for label,size in [('deck-1440',(1440,900)),('deck-844',(844,390))]:
        sc.render.resolution_x,sc.render.resolution_y=size;path=B.O/'renders'/'Assembly'/(label+'.png');V.render(sc,path);rows.append({'file':path.relative_to(B.O).as_posix(),'size':size,'down_degrees':45,'camera_direction':[.574,-.819,1],'horizontal_span_m':span})
    bpy.ops.wm.save_as_mainfile(filepath=str(B.O/'WhaleShelfLife-review.blend'))
    (B.O/'renders'/'Assembly.json').write_text(json.dumps({'views':rows,'limit':'Whale feeding composition only; actual map anchors/nav remain lead-owned. Isolated house teal plane, no native shader/HUD/nav acceptance.'},indent=2)+'\n');print('WHALE SHELF RENDERS Assembly',len(rows),flush=True)
if __name__=='__main__':
    name=sys.argv[sys.argv.index('--')+1]
    if name=='Assembly':assembly()
    else:run(name)

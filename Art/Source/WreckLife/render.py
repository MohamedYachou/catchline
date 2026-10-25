"""Five true orthographic studios; actual action samples and 10.24m/45deg fixture."""
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
    bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));sc,cam=V.stage();sc.cycles.samples=32
    p=points();floor=min(v.z for v in p)-.014;V.plane(floor,'#C9D1CC');rows=[];out=B.O/'renders'/name
    def save(label,size,extra=None):
        sc.render.resolution_x,sc.render.resolution_y=size;path=out/(label+'.png');
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update();cs=[world_to_camera_view(sc,cam,p) for p in points()];margin=[min(v.x for v in cs),min(v.y for v in cs),max(v.x for v in cs),max(v.y for v in cs)]
        assert min(margin[:2])>.03 and max(margin[2:])<.97,('studio crop',name,label,margin)
        V.render(sc,path);rows.append({'file':path.relative_to(B.O).as_posix(),'view':label,'size':size,**(extra or {})})
    sc.render.resolution_x=720;sc.render.resolution_y=600
    for label,direction in [('three-quarter',(1,-1,1)),('front',(0,-1,0)),('right',(1,0,0)),('back',(0,1,0)),('top',(0,0,1))]:
        fitted(sc,cam,p,direction);save(label,(720,600),{'projection':'orthographic'})
    if name=='Gannet':
        # Remove the floor under a diving bird; all poses have the same framing.
        bpy.data.objects['ReviewGround'].hide_render=True;rig=bpy.data.objects['GannetRig'];sc.render.resolution_x=640;sc.render.resolution_y=480
        allpoints=[]
        for action,(end,_) in B.CLIPS.items():
            rig.animation_data.action=bpy.data.actions[action]
            for f in (1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end):sc.frame_set(f);allpoints+=points()
        fitted(sc,cam,allpoints,(1,-1,1))
        for action,(end,_) in B.CLIPS.items():
            rig.animation_data.action=bpy.data.actions[action]
            for i,f in enumerate((1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end)):
                sc.frame_set(f);save('action-'+action+'-'+str(i),(640,480),{'action':action,'frame':f,'seconds':(f-1)/30})
    (B.O/'renders'/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n');print('WRECK RENDERS',name,len(rows),flush=True)

def append_asset(name,location,rename,action=None,frame=1):
    with bpy.data.libraries.load(str(B.O/(name+'.blend')),link=False) as (src,dst):
        dst.objects=src.objects
        if action:dst.actions=src.actions
    objects=[o for o in dst.objects if o];root=next(o for o in objects if o.name==name or o.name.startswith(name+'.') and o.parent is None)
    for o in objects:bpy.context.scene.collection.objects.link(o)
    root.name=rename;root.location=location
    if action:
        rig=next(o for o in objects if o.type=='ARMATURE');act=next(a for a in dst.actions if a and a.name.split('.')[0]==action)
        # Each displayed bird owns an independent copied action with static sampled frame.
        rig.animation_data.action=act
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        for pb in rig.pose.bones:pb.matrix_basis=pb.matrix_basis.copy()
        rig.animation_data_clear();root['sampled_action']=action;root['sampled_frame']=frame
    return root,objects

def assembly():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc,cam=V.stage();sc.cycles.samples=48
    V.plane(0,'#1C6E7E')
    placements=[('CardinalBuoy',(-2.7,.4,0),'Buoy',None,1),('HerringBoil',(.1,.3,0),'Shoal',None,1),('Gannet',(1.85,1.0,1.85),'GlidingGannet','Glide',24),('Gannet',(.6,-1.35,1.15),'DivingGannet','Dive',49),('DiveSplash',(.6,-1.35,0),'EntrySplash',None,1)]
    for args in placements:append_asset(*args)
    # Reference camera direction from accepted Skerries fixture; exact45deg down.
    cam.data.type='ORTHO';cam.data.ortho_scale=10.24;V.look(cam,(0,0,.9),(.574,-.819,1));rows=[]
    for label,size in [('deck-1440',(1440,900)),('deck-844',(844,390))]:
        sc.render.resolution_x,sc.render.resolution_y=size;path=B.O/'renders'/'Assembly'/(label+'.png');V.render(sc,path)
        # Record actual projected geometry margin; no asset may be cropped in either size.
        from bpy_extras.object_utils import world_to_camera_view
        coords=[world_to_camera_view(sc,cam,p) for p in points()]
        margin=[min(v.x for v in coords),min(v.y for v in coords),max(v.x for v in coords),max(v.y for v in coords)]
        assert margin[0]>=0 and margin[1]>=0 and margin[2]<=1 and margin[3]<=1,('assembly crop',size,margin)
        rows.append({'file':path.relative_to(B.O).as_posix(),'size':size,'projection':'orthographic','horizontal_span_m':10.24,'down_degrees':45,'reference_direction':[.574,-.819,1],'camera_target_blender':[0,0,.9],'asset_projected_bounds_01':margin})
    bpy.ops.wm.save_as_mainfile(filepath=str(B.O/'WreckLife-assembly-review.blend'))
    (B.O/'renders'/'Assembly.json').write_text(json.dumps({'views':rows,'placements':placements,'limit':'Isolated Blender water fixture; no Unity water, actual map, HUD, import or runtime acceptance.'},indent=2)+'\n');print('WRECK RENDERS Assembly',len(rows),flush=True)
if __name__=='__main__':
    name=sys.argv[sys.argv.index('--')+1]
    if name=='Assembly':assembly()
    else:run(name)

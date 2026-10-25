"""30 studio views and exact height/pitch two-size canonical-fish assembly."""
import sys,math,json,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
# Shared accepted studio setup is read-only; give its geometry functions our local builder.
spec=importlib.util.spec_from_file_location('net_studio',str(B.R/'Art/Source/NetKit/render.py'));V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
B.to_b=lambda p:(p[0],-p[2],p[1]);V.B=B

def studio():
    bpy.ops.wm.open_mainfile(filepath=str(B.O/'GutKit.blend'));sc,cam=V.stage();sc.cycles.samples=24
    sc.view_settings.look='AgX - Medium High Contrast';sc.render.resolution_x=1000;sc.render.resolution_y=800
    subjects=['GutBoard','GutKnife','BellyOpen','BellyRagged','GutBucket','GullSkin'];rows=[]
    for subject in subjects:
        for n in subjects:bpy.data.objects[n].hide_render=n!=subject
        sc.frame_set(1);pts=V.points();plane=V.plane(min(p.z for p in pts)-.008)
        for view,d in [('three-quarter',(1,1,1)),('front',(0,1,.08)),('right',(1,0,.08)),('back',(0,-1,.08)),('top',(0,0,1))]:
            V.fitted(sc,cam,pts,d);path=B.O/'renders'/('GullPerch' if subject=='GullSkin' else subject)/(view+'.png');V.render(sc,path)
            rows.append({'file':path.relative_to(B.O).as_posix(),'subject':subject,'view':view,'size':[1000,800]})
        bpy.data.objects.remove(plane,do_unlink=True)
    # The thin inserts have deliberately edge-on front/back evidence; oblique/top show lip/cavity design.
    bpy.data.objects['GullSkin'].hide_render=False
    for n in subjects[:-1]:bpy.data.objects[n].hide_render=True
    rig=bpy.data.objects['GullRig'];pts=[];frames=[1,8,16,23,31]
    rig.animation_data.action=bpy.data.actions['Lunge']
    for f in frames:sc.frame_set(f);pts+=V.points()
    V.fitted(sc,cam,pts,(1,1,.4));sc.render.resolution_x=600;sc.render.resolution_y=600
    V.fitted(sc,cam,pts,(1,1,.4));ground=V.plane(-.008)
    for f in frames:
        sc.frame_set(f);path=B.O/'renders/action'/('Lunge-%02d.png'%f);V.render(sc,path)
        rows.append({'file':path.relative_to(B.O).as_posix(),'subject':'GullPerch','action':'Lunge','frame':f,'size':[600,600]})
    (B.O/'renders/studio.json').write_text(json.dumps(rows,indent=2)+'\n')
    return rows

def append(rel,rootname=None):
    with bpy.data.libraries.load(str(B.R/rel),link=False) as (a,b):b.objects=a.objects
    for o in b.objects:bpy.context.scene.collection.objects.link(o)
    roots=[o for o in b.objects if o.parent is None and o.type in ('EMPTY','ARMATURE')]
    return next(o for o in roots if rootname is None or o.name.split('.')[0]==rootname),b.objects

def assembly():
    bpy.ops.wm.open_mainfile(filepath=str(B.O/'GutKit.blend'))
    sc=bpy.context.scene;sc.frame_set(1);top=.722
    board=bpy.data.objects['GutBoard'];board.location.z=top
    knife=bpy.data.objects['GutKnife'];knife.location=(-.16,.125,top+.023);knife.rotation_euler.z=math.radians(-15)
    bpy.data.objects['BellyRagged'].hide_render=True
    bucket=bpy.data.objects['GutBucket'];bucket.location=(.52,.16,.25)
    gull=bpy.data.objects['GullPerch'];gull.location=(-.50,-.30,.84);gull.rotation_euler.z=math.radians(45)
    table,objs=append('Art/Models/DayBoatKit/Stations/GuttingTable.blend')
    fish,objs=append('Art/Models/Fish043/Mackerel/Mackerel.blend','Catchline_Mackerel')
    for o in objs:
        if o.type in ('CAMERA','LIGHT'):bpy.data.objects.remove(o,do_unlink=True)
    fish.rotation_euler=(Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Rotation(-math.pi/2,4,'Y')).to_euler();fish.scale=(1.5,)*3;fish.location=(0,0,top+.045696)
    insert=bpy.data.objects['BellyOpen'];insert.location=(-.090,.067,top+.054);insert.scale=(.25,.55,.65)
    # Presentation deck/perch only; excluded from clean source/export.
    B.H.PALETTE=B.P;B.H.MATERIALS={k:bpy.data.materials.get(k) or B.H.material(k,v,.75) for k,v in B.P.items()}
    g=B.G();g.box((0,0,-.04),(3.6,2.6,.08),'M_DeckWood')
    g.beam((-.78,-.30,.81),(-.35,-.30,.81),.08,.06,'M_RailIvory')
    for x in (-.72,-.41):g.beam((x,-.30,0),(x,-.30,.79),.045,.045,'M_Steel')
    g.object('ReviewDeckPerch',None,sc.collection)
    sc,cam=V.stage();sc.cycles.samples=32;V.plane(-.082,'#168F9F')
    cam.data.type='PERSP';cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36
    cam.data.lens=36/(2*math.tan(math.radians(55/2)));cam.location=(0,.9/math.tan(math.radians(60)),top+.9)
    target=Vector((0,0,top));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    rows=[]
    for label,size in [('1440',(1440,900)),('844',(844,390))]:
        sc.render.resolution_x,sc.render.resolution_y=size;path=B.O/'renders/assembly'/('gut-view-'+label+'.png');V.render(sc,path)
        rows.append({'file':path.relative_to(B.O).as_posix(),'size':list(size)})
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(B.O/'GutKit-camera-fixture.blend'))
    data={'evidence':'Isolated Blender assembly, not native acceptance. Existing real GuttingTable and canonical Fish043 Mackerel appended read-only.', 'camera':{'height_above_board_m':.9,'pitch_down_degrees':60,'horizontal_fov_degrees':55,'sensor_fit':'HORIZONTAL','position_blender':list(cam.location),'target_blender':list(target)},'board_top_blender_z':top,'fish':{'root':fish.name,'source':'Art/Models/Fish043/Mackerel/Mackerel.blend','scale':1.5,'rotation_blender':list(fish.rotation_euler),'position_blender':list(fish.location)},'insert':{'position_blender':list(insert.location),'scale':list(insert.scale),'vent_to_gill_length_m':.25},'renders':rows}
    (B.O/'assembly.json').write_text(json.dumps(data,indent=2)+'\n');return rows
if __name__=='__main__':
    rows=studio();rows+=assembly();print('GUT RENDER PASS',len(rows),flush=True)

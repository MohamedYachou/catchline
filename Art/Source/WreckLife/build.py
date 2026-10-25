"""WRECK-LIFE-1. Metres; Blender X,-Y,Z -> Unity X,Z,-Y. Owned trees only."""
import bpy,sys,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/WreckLife'
sys.path.insert(0,str(R/'Art/Source'));import build_crab_coast_props as H
G=H.Geometry
P={'M_GullWhite':'#F1F0EA','M_GullGrey':'#9AA6AD','M_Rubber':'#28343B','M_FishSilver':'#BAC9C6','M_RailIvory':'#F3F0DC','M_GannetBuff':'#E8CF8F','M_CardinalYellow':'#F2C14E','M_CardinalBlack':'#23262B'}
LIMITS={'Gannet':1500,'DiveSplash':300,'CardinalBuoy':700,'HerringBoil':400}
CLIPS={'Glide':(91,True),'Dive':(49,False)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def empty(n,parent=None):
    o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);o.parent=parent;return o

def mesh(g,n,parent):
    o=g.object(n,parent,bpy.context.scene.collection)
    used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];inds=[used.index(p.material_index) for p in o.data.polygons]
    o.data.materials.clear()
    for m in mats:o.data.materials.append(m)
    for p,i in zip(o.data.polygons,inds):p.material_index=i
    return o

def loft(g,rows,col,cap=True):
    n=len(rows[0]);vs=sum(rows,[]);fs=[]
    if cap:fs.append(tuple(reversed(range(n))))
    for j in range(len(rows)-1):fs.extend((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n))
    if cap:fs.append(tuple(range((len(rows)-1)*n,len(rows)*n)))
    g.add(vs,fs,col)

def radial(g,rings,n,col):
    loft(g,[[(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n)] for r,z in rings],col)

def gannet(root):
    g=G();tags=[]
    def tag(st,b):tags.append((st,len(g.vertices),b))
    st=0
    g.ellipsoid((0,0,0),(.071,.180,.067),12,5,'M_GullWhite')
    g.ellipsoid((0,-.159,.014),(.044,.105,.044),10,3,'M_GullWhite')
    # Narrow wedge tail, tapering to a single broad point without needle triangles.
    poly=[(-.044,.115,.012),(.044,.115,.012),(.023,.265,-.015),(-.023,.265,-.015)]
    loft(g,[[(x,y,z-.006) for x,y,z in poly],[(x,y,z+.006) for x,y,z in poly]],'M_GullWhite');tag(st,'Body')
    st=len(g.vertices)
    g.ellipsoid((0,-.258,.034),(.049,.068,.047),12,3,'M_GannetBuff')
    # Pale lower cheek and long silver dagger beak.
    g.ellipsoid((0,-.277,.009),(.039,.049,.023),10,2,'M_GullWhite')
    g.add([(-.025,-.306,.020),(.025,-.306,.020),(0,-.437,.010),(0,-.306,.044),(0,-.306,-.002)],[(0,3,2),(3,1,2),(1,4,2),(4,0,2),(0,4,1,3)],'M_GullGrey')
    for s in (-1,1):
        g.ellipsoid((s*.044,-.277,.044),(.006,.008,.007),8,2,'M_Rubber')
        # Thin black gannet bill line; no eye ring or cartoon eye highlights.
        g.add([(s*.023,-.306,.021),(s*.001,-.424,.011),(s*.023,-.306,.018)],[(0,1,2)],'M_Rubber')
    tag(st,'Head')
    for s,bone in [(-1,'Wing.L'),(1,'Wing.R')]:
        st=len(g.vertices)
        # Long narrow swept wings; connected white inner panel + black primary panel.
        inner=[(s*.052,-.086,.018),(s*.245,-.072,.017),(s*.365,.015,.012),(s*.345,.105,.006),(s*.198,.069,.004),(s*.061,.078,.006)]
        outer=[(s*.365,.015,.012),(s*.457,.092,.005),(s*.5,.188,-.005),(s*.452,.169,-.004),(s*.407,.151,-.001),(s*.345,.105,.006)]
        for poly,col in [(inner,'M_GullWhite'),(outer,'M_Rubber')]:
            loft(g,[[(x,y,z-.006) for x,y,z in poly],[(x,y,z+.006) for x,y,z in poly]],col)
        # Two broad grey feather separations, recessed on the rear edge.
        for x,y in [(.215,.066),(.285,.085)]:
            g.add([(s*(x-.014),y-.022,.018),(s*(x+.025),y+.011,.017),(s*(x+.018),y+.014,.017)],[(0,1,2)],'M_GullGrey')
        tag(st,bone)
    skin=mesh(g,'GannetSkin',root)
    import bmesh
    bm=bmesh.new();bm.from_mesh(skin.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(skin.data);bm.free();skin.data.update()
    # Body/neck/head are softly lit; wing planes retain their broad facets.
    body_end=tags[1][1]
    for p in skin.data.polygons:p.use_smooth=all(i<body_end for i in p.vertices) and p.material_index not in [i for i,m in enumerate(skin.data.materials) if m.name=='M_Rubber']
    ar=bpy.data.armatures.new('GannetSkeleton');rig=bpy.data.objects.new('GannetRig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    spec=[('Root',(0,0,0),None),('Body',(0,0,0),'Root'),('Head',(0,-.20,.02),'Body'),('Wing.L',(-.06,-.025,.012),'Body'),('Wing.R',(.06,-.025,.012),'Body')]
    for n,h,par in spec:
        b=ar.edit_bones.new(n);b.head=h;b.tail=Vector(h)+Vector((0,.06,0))
        if par:b.parent=ar.edit_bones[par]
    bpy.ops.object.mode_set(mode='OBJECT');skin.parent=rig;m=skin.modifiers.new('GannetSkinning','ARMATURE');m.object=rig
    for n,_,_ in spec:skin.vertex_groups.new(name=n);rig.pose.bones[n].rotation_mode='XYZ'
    for lo,hi,b in tags:skin.vertex_groups[b].add(list(range(lo,hi)),1,'REPLACE')
    sc=bpy.context.scene;sc.render.fps=30
    for name,(end,loop) in CLIPS.items():
        a=bpy.data.actions.new(name);a.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=a
        for f in range(1,end+1,3):
            t=(f-1)/(end-1)
            for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
            b=rig.pose.bones['Body']
            if name=='Glide':
                b.rotation_euler=(math.radians(2)*math.sin(math.tau*t),math.radians(6)*math.sin(math.tau*t),math.radians(4)*(1-math.cos(math.tau*t))*.5)
            else:
                # Smooth anticipation then wings sweep back to the body's tail axis.
                q=max(0,min(1,(t-.10)/.72));q=q*q*(3-2*q)
                b.rotation_euler.x=math.radians(82)*q
                for s,n in [(-1,'Wing.L'),(1,'Wing.R')]:
                    rig.pose.bones[n].rotation_euler.z=s*math.radians(79)*q
                    rig.pose.bones[n].rotation_euler.y=-s*math.radians(5)*q
                rig.pose.bones['Head'].rotation_euler.x=math.radians(-5)*q
            for pb in rig.pose.bones:
                for prop in ('location','rotation_euler','scale'):pb.keyframe_insert(prop,frame=f,group=pb.name)
        for fc in a.layers[0].strips[0].channelbag(rig.animation_data.action_slot).fcurves:
            for k in fc.keyframe_points:k.interpolation='LINEAR'
            if loop:fc.modifiers.new('CYCLES')
        a['loop']=loop;a['seconds']=(end-1)/30
    rig.animation_data.action=bpy.data.actions['Glide'];sc.frame_start=1;sc.frame_end=91;sc.frame_set(1)
    root['contract']='Flight pivot at body centre. Forward Unity +Z, up +Y. Root fixed. Legacy Glide3s loop; Dive1.6s one-shot holds arrow pose; runtime owns travel/circle/splash.'
    return {'bones':[n for n,_,_ in spec],'clips':{n:{'frames':[1,end],'seconds':(end-1)/30,'loop':loop} for n,(end,loop) in CLIPS.items()},'flight_pivot':True,'root_motion':False}

def splash(root):
    g=G();n=12
    # Continuous asymmetric crown; broad central jet and six arcing petal jets.
    rows=[]
    for level in range(3):
        ring=[]
        for i in range(n):
            a=i*math.tau/n
            if level==0:r,z=.235,0
            elif level==1:r,z=.185,.12
            else:r,z=(.22,.34) if i%2 else (.145,.16)
            ring.append((r*math.cos(a),r*math.sin(a),z))
        rows.append(ring)
    loft(g,rows,'M_GullWhite',False)
    # Solid central spear with a blunt irregular top, never transparent cards.
    radial(g,[(.105,0),(.078,.20),(.050,.43),(.018,.60)],8,'M_GullWhite')
    for i in range(5):
        a=(i+.35)*math.tau/5;c=(.255*math.cos(a),.255*math.sin(a),.34+(i%2)*.09)
        g.ellipsoid(c,(.021,.021,.036),6,1,'M_RailIvory')
    mesh(g,'DiveSplashMesh',root)
    return {'pivot':'waterline centre','height_m':.6,'static':True,'animation':'Runtime scales/fades whole plume; opaque mesh, no simulation.'}

def buoy(root):
    g=G()
    # Explicit brief: YELLOW OVER BLACK; 2.4m including two upward cone topmarks.
    radial(g,[(.22,-.16),(.31,-.07),(.31,.18),(.25,.30)],12,'M_CardinalBlack')
    radial(g,[(.25,.30),(.25,.38),(.14,.94),(.095,1.02)],12,'M_CardinalYellow')
    radial(g,[(.045,1.00),(.045,2.08)],8,'M_CardinalBlack')
    # Service collar and small lifting eye deliberately share existing slots.
    radial(g,[(.117,.91),(.117,.95)],12,'M_CardinalYellow')
    g.tube([(.09,0,.64),(.12,0,.70),(.09,0,.76)],[.015]*3,5,'M_CardinalBlack')
    for z in (1.58,1.94):
        n=10;ring=[(.15*math.cos(i*math.tau/n),.15*math.sin(i*math.tau/n),z) for i in range(n)];tip=(0,0,z+.30)
        g.add(ring+[tip],[tuple(reversed(range(n)))]+[(i,(i+1)%n,n) for i in range(n)],'M_CardinalBlack')
    mesh(g,'CardinalBuoyMesh',root)
    root['paint']='Yellow upper body / black lower body exactly as brief; both cone topmarks up.'
    return {'pivot':'waterline centre, lower float extends .16m below','top_y_m':2.24,'total_height_m':2.4,'paint':'yellow over black as explicitly requested','topmarks':'two cones pointing UP','static':True}

def boil(root):
    g=G();rng=random.Random(705)
    # Fragmented concentric ellipses, no continuous white target rings or noisy foam carpet.
    for k,(rx,ry) in enumerate([(1.50,.84),(1.17,.66),(.79,.44)]):
        n=36
        for i in range(n):
            if (i+k*3)%9 not in (0,1,2,5,6):continue
            a=(i+.12)*math.tau/n;b=(i+.88)*math.tau/n;w=.020 if k==0 else .028
            g.add([(rx*math.cos(a),ry*math.sin(a),.008),(rx*math.cos(b),ry*math.sin(b),.008),((rx-w)*math.cos(b),(ry-w)*math.sin(b),.008),((rx-w)*math.cos(a),(ry-w)*math.sin(a),.008)],[(0,1,2,3)],'M_RailIvory' if (i+k)%3 else 'M_FishSilver')
    for j in range(20):
        a=rng.uniform(0,math.tau);r=math.sqrt(rng.uniform(.02,.86));x=1.10*r*math.cos(a);y=.60*r*math.sin(a);ang=rng.uniform(-.5,.5)
        axis=Vector((math.cos(ang),math.sin(ang),0));side=Vector((-axis.y,axis.x,0));c=Vector((x,y,.013));L=rng.uniform(.055,.105);w=.020
        vs=[c-axis*L,c+side*w,c+Vector((0,0,.028)),c+axis*L,c-side*w]
        g.add(vs,[(0,1,2),(1,3,2),(3,4,2),(4,0,2),(0,4,3,1)],'M_FishSilver')
        # One broad light face makes each tiny breach readable from the high camera.
        g.add([c-axis*L*.65+Vector((0,0,.001)),c+Vector((0,0,.029)),c+side*w*.7+Vector((0,0,.001))],[(0,1,2)],'M_GullWhite')
    mesh(g,'HerringBoilMesh',root)
    return {'pivot':'waterline centre','ripple_height_m':.008,'static':True,'animation':'Runtime pulses scale/visibility like SurfPulse; no exported clips. Two-sided shader for flat ripples.'}
BUILD={'Gannet':gannet,'DiveSplash':splash,'CardinalBuoy':buoy,'HerringBoil':boil}
def snapshot():
    bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    return {'triangles':sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),'vertices':sum(len(o.data.vertices) for o in meshes),'bounds_unity':[[min((p.x,p.z,-p.y)[i] for p in pts) for i in range(3)],[max((p.x,p.z,-p.y)[i] for p in pts) for i in range(3)]],'meshes':[o.name for o in meshes],'materials':sorted({m.name for o in meshes for m in o.data.materials}),'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects}}
def run(name):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    H.PALETTE=P;H.MATERIALS={n:H.material(n,c,.75) for n,c in P.items()}
    root=empty(name);root['axes']='Blender X,-Y,Z -> Unity X,Z,-Y. Metres, logical zero pivot.'
    contract=BUILD[name](root);row=snapshot();assert row['triangles']<=LIMITS[name],(name,row['triangles'])
    for m in list(bpy.data.materials):
        if m.users==0:bpy.data.materials.remove(m)
    bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=name!='Gannet',use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=False,add_leaf_bones=False,bake_anim=name=='Gannet',bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0,path_mode='AUTO',use_custom_props=True)
    row.update(name=name,contract=contract,limit=LIMITS[name],sha256={e:sha(O/(name+'.'+e)) for e in ('blend','fbx')},palette=P)
    (O/'metrics'/(name+'-build.json')).write_text(json.dumps(row,indent=2)+'\n');print('WRECK BUILT',name,row['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])

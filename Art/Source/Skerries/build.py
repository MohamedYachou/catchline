"""SKERRIES-LIFE-1. Deterministic metre geometry, no Assets/runtime writes.
Blender X right/-Y forward/Z up -> Unity X right/+Z forward/Y up.
Run Windows Blender 5.2: -b -t 6 -P <script> -- Seal (or other BUILD key).
"""
import sys,math,json,hashlib,random
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/Skerries'
sys.path.insert(0,str(R/'Art/Source'))
import build_crab_coast_props as H
G=H.Geometry
P={'M_Steel':'#8FA6AC','M_FishSilver':'#BAC9C6','M_Rubber':'#28343B',
   'M_RailIvory':'#F3F0DC','M_HullNavy':'#173F57','M_SeaTeal':'#168F9F',
   'M_ShallowWater':'#64C7C4','M_Rope':'#D1AF76','M_SafetyOrange':'#E36A35',
   'M_LegalRed':'#CF4232','M_KelpGreen':'#477A56'}
LIMITS={'Seal':2000,'SealColony':3500,'SealSwimHead':900,'ReefBreak_A':300,'ReefBreak_B':300,'CrabBuoySet':900,'PotStack':2250}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def init(name):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    H.PALETTE=P;H.MATERIALS={k:H.material(k,v,.72) for k,v in P.items()}
    root=bpy.data.objects.new(name,None);sc.collection.objects.link(root)
    root['axes']='Blender X,-Y,Z -> Unity X,Z,-Y. Metres. Root base centre.'
    return root

def mesh(g,name,parent,smooth=False):
    o=g.object(name,parent,bpy.context.scene.collection)
    used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];inds=[used.index(p.material_index) for p in o.data.polygons]
    o.data.materials.clear()
    for m in mats:o.data.materials.append(m)
    for p,i in zip(o.data.polygons,inds):p.material_index=i;p.use_smooth=smooth
    return o

def ell(g,c,r,col='M_Steel',n=10,k=3):g.ellipsoid(c,r,n,k,col)
def tube(g,pts,r,col,n=5):g.tube(pts,[r]*len(pts),n,col)
def beam(g,a,b,w,col):g.beam(a,b,w,w,col)
def patch(g,pts,col):g.add(pts,[tuple(range(len(pts)))],col)

def seal_mesh(parent,name='SealSkin',swim=False):
    g=G();groups=[]
    def tag(start,weights):groups.append((start,len(g.vertices),weights))
    # A single connected tapered torso/neck/head, no sphere-stack neck seams.
    rows=[(-.77,.065,.047,.347),(-.70,.145,.105,.371),(-.61,.192,.180,.385),(-.47,.200,.205,.335),(-.32,.240,.235,.260),(-.08,.270,.244,.248),(.21,.242,.207,.213),(.43,.165,.133,.145),(.61,.074,.060,.090),(.68,.035,.031,.064)]
    n=12;vs=[];fs=[];cs=[]
    for y,rx,rz,z in rows:
        for i in range(n):
            a=i*math.tau/n;vs.append((rx*math.cos(a),y,z+rz*math.sin(a)))
    fs=[tuple(reversed(range(n)))];cs=['M_FishSilver']
    for j in range(len(rows)-1):
        for i in range(n):
            fs.append((j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n))
            cs.append('M_FishSilver' if i in (7,8,9,10) else 'M_Steel')
    fs.append(tuple(range((len(rows)-1)*n,len(rows)*n)));cs.append('M_Steel')
    g.vertices=vs;g.faces=fs;g.colours=cs
    for j,(y,rx,rz,z) in enumerate(rows):
        head=max(0,min(1,(-y-.30)/.25));tail=max(0,min(1,(y-.36)/.27))
        groups.append((j*n,(j+1)*n,{'Head':head,'Tail':tail,'Body':1-head-tail}))
    # Paired pale muzzle cushions, modest black nose and two small side-facing eyes.
    st=len(g.vertices)
    for s in (-1,1):
        ell(g,(s*.056,-.733,.348),(.069,.059,.047),'M_FishSilver',8,2)
        ell(g,(s*.162,-.666,.437),(.026,.030,.027),'M_Rubber',8,2)
        ell(g,(s*.171,-.682,.447),(.007,.008,.008),'M_RailIvory',6,2)
        # Two restrained whiskers per cheek: deliberately thick enough at rod distance.
        for j in range(2):tube(g,[(s*.066,-.770,.341-j*.018),(s*.167,-.787+j*.022,.337-j*.015)],.003,'M_Rubber',3)
    ell(g,(0,-.777,.374),(.042,.022,.026),'M_Rubber',8,2);tag(st,{'Head':1})
    # Short front flippers, tucked against the chest; broad split rear hind flippers.
    for s in (-1,1):
        st=len(g.vertices)
        poly=[(s*.17,-.28,.095),(s*.29,-.26,.058),(s*.405,-.025,.026),(s*.335,.03,.021),(s*.235,-.07,.047)]
        g.add(poly+[(x,y,z+.035) for x,y,z in poly],[(0,4,3,2,1),(5,6,7,8,9)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)],'M_Steel')
        tag(st,{'Fore.L' if s<0 else 'Fore.R':1})
        st=len(g.vertices)
        poly=[(s*.015,.57,.075),(s*.095,.59,.074),(s*.186,.78,.035),(s*.154,.83,.014),(s*.034,.76,.033)]
        g.add(poly+[(x,y,z+.032) for x,y,z in poly],[(0,4,3,2,1),(5,6,7,8,9)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)],'M_Steel');tag(st,{'Tail':1})
    # Four broad, grey flank spots identify a harbour seal without texture noise.
    st=len(g.vertices)
    for s in (-1,1):
        for y,rx,z in [(-.12,.263,.265),(.14,.245,.27)]:
            ell(g,(s*rx,y,z),(.008,.052,.034),'M_Rubber',6,2)
    tag(st,{'Body':1})
    o=mesh(g,name,parent,True)
    for bone in ('Root','Body','Head','Fore.L','Fore.R','Tail'):o.vertex_groups.new(name=bone)
    for lo,hi,weights in groups:
        for bone,w in weights.items():
            if w>0:o.vertex_groups[bone].add(list(range(lo,hi)),w,'REPLACE')
    return o

def rig_seal(root,skin):
    ar=bpy.data.armatures.new('SealSkeleton');rig=bpy.data.objects.new('SealRig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    bones=[('Root',(0,0,0),(0,.15,0),None),('Body',(0,0,.18),(0,-.30,.26),'Root'),('Head',(0,-.34,.28),(0,-.65,.41),'Body'),('Fore.L',(-.19,-.26,.08),(-.35,-.04,.04),'Body'),('Fore.R',(.19,-.26,.08),(.35,-.04,.04),'Body'),('Tail',(0,.40,.10),(0,.72,.055),'Body')]
    for name,head,tail,parent in bones:
        b=ar.edit_bones.new(name);b.head=head;b.tail=tail
        if parent:b.parent=ar.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT');skin.parent=rig;mod=skin.modifiers.new('SealSkinning','ARMATURE');mod.object=rig
    for b in rig.pose.bones:b.rotation_mode='XYZ'
    sc=bpy.context.scene;sc.render.fps=30
    durations={'Bask':121,'Look':91,'Slide':37}
    for name,end in durations.items():
        action=bpy.data.actions.new(name);action.use_fake_user=True
        rig.animation_data_create();rig.animation_data.action=action
        frames=range(1,end+1,6) if name!='Slide' else range(1,38,3)
        for f in frames:
            t=(f-1)/(end-1)
            for b in rig.pose.bones:b.location=(0,0,0);b.rotation_euler=(0,0,0);b.scale=(1,1,1)
            body=rig.pose.bones['Body'];head=rig.pose.bones['Head']
            if name=='Bask':
                breath=math.sin(math.tau*t);body.scale=(1+.013*breath,1,1+.025*breath);head.rotation_euler.x=math.radians(-4)*(1-math.cos(math.tau*t))*.5
                rig.pose.bones['Tail'].rotation_euler.z=math.radians(2)*breath
            elif name=='Look':
                head.rotation_euler.x=math.radians(-8)*(math.sin(math.pi*t)**2)
                head.rotation_euler.z=math.radians(32)*math.sin(math.tau*t)
            else:
                ease=t*t*(3-2*t);rig.pose.bones['Root'].location=(0,-1.85*ease,-.48*ease)
                body.rotation_euler.x=math.radians(13)*math.sin(math.pi*t)
                for side,sgn in [('L',-1),('R',1)]:rig.pose.bones['Fore.'+side].rotation_euler.z=sgn*math.radians(16)*math.sin(math.pi*t)
                head.rotation_euler.x=math.radians(8)*ease
            for b in rig.pose.bones:
                b.keyframe_insert('location',frame=f,group=b.name);b.keyframe_insert('rotation_euler',frame=f,group=b.name);b.keyframe_insert('scale',frame=f,group=b.name)
        # Dense FBX sampling preserves easing. Exact endpoints make loop closure testable.
        slot=rig.animation_data.action_slot
        curves=action.layers[0].strips[0].channelbag(slot).fcurves
        for fc in curves:
            for k in fc.keyframe_points:k.interpolation='LINEAR'
            if name!='Slide':fc.modifiers.new('CYCLES')
        action['loop']=name!='Slide';action['seconds']=(end-1)/30
    rig.animation_data.action=bpy.data.actions['Bask'];sc.frame_start=1;sc.frame_end=121;sc.frame_set(1)
    return {'bones':[a[0] for a in bones],'clips':{k:{'frames':[1,e],'seconds':(e-1)/30,'loop':k!='Slide'} for k,e in durations.items()},'slide_displacement_unity':[0,-.48,1.85],'legacy':'Import as Legacy; clips may be named SealRig|Bask etc by FBX. Use each action frame range, loop Bask/Look only. Slide contains root-bone translation, apply no duplicate runtime forward motion.'}

def seal(root):return rig_seal(root,seal_mesh(root))

def slab(root,name='GraniteSlab',width=4.4,depth=2.5,height=.30):
    g=G();n=10;vs=[]
    for z,factor in [(0,.80),(.09,1),(height,.91)]:
        for i in range(n):
            a=math.tau*i/n;rr=1+.045*math.sin(i*2.7);vs.append((width*.5*factor*rr*math.cos(a),depth*.5*factor*rr*math.sin(a),z))
    g.add(vs,[tuple(reversed(range(n))),tuple(range(2*n,3*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(2) for i in range(n)],'M_Steel')
    o=mesh(g,name,root);return o

def static_seal(root,name,loc,angle,scale,head_turn):
    skin=seal_mesh(root,name);bpy.context.view_layer.update()
    # Bake a gentle head turn using the same weights as the rig, no skin rig in static export.
    pivot=Vector((0,-.34,.28));rot=Matrix.Rotation(head_turn,4,'Z')
    for v in skin.data.vertices:
        try:w=skin.vertex_groups['Head'].weight(v.index)
        except RuntimeError:w=0
        p=v.co;v.co=p.lerp(rot@(p-pivot)+pivot,w)
    skin.vertex_groups.clear();skin.location=loc;skin.rotation_euler.z=angle;skin.scale=(scale,)*3
    bpy.context.view_layer.objects.active=skin;skin.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);skin.select_set(False)
    return skin

def colony(root):
    rock=slab(root)
    for name,loc,a,s,h in [('BaskingSeal',(0,-.15,.30),-.24,1,0),('LookoutSeal',(-1.22,.12,.30),.62,.93,-.35),('YoungSeal',(1.15,.14,.30),-.65,.82,.38)]:
        static_seal(root,name,loc,a,s,h)
    return {'static':True,'seals':3,'rock_top_unity_Y':.30,'root':'Place at base on colony anchor, not at seal feet. Rock slab included. Three poses derived from delivered Seal mesh.'}

def swimhead(root):
    # The same face and upper-body form, clipped to a water-level base (no submerged sealed torso).
    o=seal_mesh(root,'SwimmingSeal')
    bm=bmesh.new();bm.from_mesh(o.data)
    cut=.21;bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=(0,0,cut),plane_no=(0,0,1),clear_inner=True,clear_outer=False)
    bm.to_mesh(o.data);bm.free();o.vertex_groups.clear()
    # Rest head/back sit above water; base Z=0, no teeth or under-surface caps visible.
    for v in o.data.vertices:v.co.z-=cut
    g=G()
    for s in (-1,1):
        for j in range(2):
            pts=[(s*.16,-.47+j*.12,.008),(s*.31,-.10+j*.12,.008),(s*.55,.72+j*.12,.008),(s*.47,.68+j*.12,.008),(s*.26,-.08+j*.12,.008)]
            patch(g,pts if s>0 else list(reversed(pts)),'M_RailIvory' if j==0 else 'M_ShallowWater')
    wake=mesh(g,'VWake',root)
    # A volume-based normal recalculation cannot orient disconnected flat foam.
    bm=bmesh.new();bm.from_mesh(wake.data);bm.normal_update()
    bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0])
    bm.to_mesh(wake.data);bm.free();wake.data.update()
    return {'waterline':'Root Y=0; head/back clipped to surface. VWake flat at Y=.008. Forward Unity +Z.','source':'Delivered Seal mesh with submerged portion trimmed.'}

def reef(root,variant):
    g=G();rnd=random.Random(101+variant)
    # Irregular, curved broken crests; continuous broad ribbons rather than rows of lozenges.
    spans=[ [(-2.94,-1.62),(-1.41,.96),(1.27,2.92)],
            [(-2.81,-.38),(-.08,1.48),(1.84,2.76)],
            [(-2.93,-2.16),(-1.91,.28),(.64,2.97)] ]
    for j,parts in enumerate(spans):
        for k,(a,b) in enumerate(parts):
            if variant:a,b=-b,-a
            n=max(3,round((b-a)/.40));upper=[];lower=[]
            for i in range(n+1):
                t=i/n;x=a+(b-a)*t
                y=(-.73+j*.67)+.15*math.sin(x*.88+j*.9+variant*.7)+rnd.uniform(-.025,.025)
                width=(.045+.12*math.sin(math.pi*t)**.6)*rnd.uniform(.8,1.2)
                upper.append((x,y+width*.45,0));lower.append((x,y-width*.55,0))
            for i in range(n):patch(g,[upper[i],upper[i+1],lower[i+1],lower[i]],'M_RailIvory' if (i+j+k)%5 else 'M_ShallowWater')
    # Small uneven foam fragments accompany the crests without filling the water gaps.
    for i in range(15):
        x=rnd.uniform(-2.8,2.7);y=rnd.uniform(-.91,.91);w=rnd.uniform(.08,.24)
        patch(g,[(x,y,0),(x+w*.3,y+.035,0),(x+w,y+.012,0),(x+w*.8,y-.035,0)],'M_RailIvory' if i%4 else 'M_ShallowWater')
    # Exact 6x2 envelope; all vertices stay coplanar for easy UV/scale animation.
    for x,y in [(-3,-1),(2.8,1)]:patch(g,[(x,y,0),(x+.2,y,0),(x+.13,y+(.05 if y<0 else -.05),0)],'M_RailIvory')
    # Independent foam islands have no enclosed volume: orient them explicitly skyward.
    g.faces=[tuple(reversed(f)) if sum(g.vertices[f[i]][0]*g.vertices[f[(i+1)%len(f)]][1]-g.vertices[f[(i+1)%len(f)]][0]*g.vertices[f[i]][1] for i in range(len(f)))<0 else f for f in g.faces]
    o=mesh(g,'BrokenWater',root);uv=o.data.uv_layers.new(name='UVMap')
    for p in o.data.polygons:
        for li in p.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x+3)/6,(co.y+1)/2)
    return {'variant':variant,'footprint_metres':[6,2],'placement':'Root Y=water+.012m. Exact plane at local Y0, normals up; keep above animated surface. UV U=X/6+.5,V=-UnityZ/2+.5. Scroll a shared foam material or pulse transform; no textures supplied. Opaque geometric foam silhouettes retain water gaps.'}

def buoy(root):
    g=G()
    # Broad alternating red and ivory horizontal buoy body, stable waterline base.
    n=12;profile=[(0,.13),(.045,.23),(.16,.23),(.30,.20),(.36,.12),(.40,.08)];vs=[(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for z,r in profile for i in range(n)]
    g.vertices=vs
    for j in range(len(profile)-1):
        g.faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n)]
        g.colours += ['M_RailIvory' if j in (0,2,4) else 'M_LegalRed']*n
    g.faces += [tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))];g.colours += ['M_LegalRed']*2
    tube(g,[(0,0,.32),(0,0,1.32)],.014,'M_HullNavy',6)
    # Double-sided thin, closed swallowtail pennant.
    pts=[(0,-.012,1.29),(.44,-.012,1.25),(.34,-.012,1.12),(.44,-.012,.98),(0,-.012,1.02)]
    g.add(pts+[(x,y+.024,z) for x,y,z in pts],[(4,3,2,1,0),(5,6,7,8,9)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)],'M_LegalRed')
    for a in (-2.2,.9):
        pts=[(.15*math.cos(a),.15*math.sin(a),.012),(.52*math.cos(a+.12),.52*math.sin(a+.12),.009),(1.1*math.cos(a-.08),1.1*math.sin(a-.08),.009)]
        tube(g,pts,.009,'M_Rope',4)
    mesh(g,'BuoyFlagAndLines',root)
    return {'waterline':'Buoy body base Y0; floating lines at Y.009. Place root .015m above mean water.','flag_top_metres':1.32,'palette':'M_LegalRed #CF4232 + M_RailIvory horizontal bands; small solid double-sided flag.'}

def potstack(root):
    src=R/'Art/Models/Fishing/CageKit/CrabCage.blend';before=sha(src)
    slab(root,'GraniteLedge',1.95,1.32,.16)
    with bpy.data.libraries.load(str(src),link=False) as (a,b):b.objects=['CreelFrame','Lid','Bridle']
    cage=b.objects
    for o in cage:
        bpy.context.scene.collection.objects.link(o)
        # Reuse the shared house material slots, without .001 duplicates from library append.
        for i,m in enumerate(o.data.materials):
            key=m.name.split('.')[0];assert key in H.MATERIALS,key;o.data.materials[i]=H.MATERIALS[key]
    bpy.context.view_layer.update()
    # Simplify the actual cage mesh. All five retain frame/hatch/bait/latch colour regions.
    for o in cage:o.parent=None
    bpy.ops.object.select_all(action='DESELECT')
    for o in cage:o.select_set(True)
    bpy.context.view_layer.objects.active=cage[0];bpy.ops.object.join();base=bpy.context.object;base.name='CageLOD'
    mod=base.modifiers.new('Static far-view LOD','DECIMATE');mod.ratio=.32;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(base.data)
    bmesh.ops.dissolve_degenerate(bm,dist=.0000001,edges=list(bm.edges))
    tiny=[f for f in bm.faces if f.calc_area()<1e-10]
    if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(base.data);bm.free();base.data.validate(verbose=True,clean_customdata=False);base.data.update()
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    for i,loc in enumerate([(-.36,-.25,.16),(.36,-.25,.16),(-.36,.25,.16),(.36,.25,.16),(0,0,.50)]):
        o=base if i==0 else base.copy()
        if i>0:o.data=base.data.copy();bpy.context.scene.collection.objects.link(o)
        o.name='CrabCage_'+str(i+1);o.parent=root;o.location=loc
        # The joined base object retains source world coords; root location was0.
    assert sha(src)==before
    return {'source':str(src.relative_to(R)).replace('\\','/'),'source_sha256':before,'cages':5,'triangles_per_cage':sum(len(p.vertices)-2 for p in base.data.polygons),'LOD':'Actual released CreelFrame+Lid+Bridle joined, collapse-decimated32% then degenerate/loose cleanup; static distant stack, no lid controls. Canonical CageKit unchanged.'}
BUILD={'Seal':seal,'SealColony':colony,'SealSwimHead':swimhead,'ReefBreak_A':lambda r:reef(r,0),'ReefBreak_B':lambda r:reef(r,1),'CrabBuoySet':buoy,'PotStack':potstack}

def snapshot(evaluated=False):
    bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[]
    for o in meshes:
        e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else o
        pts += [e.matrix_world@v.co for v in e.data.vertices]
    return {'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),
      'meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'finite':all(math.isfinite(c) for p in pts for c in p),
      'bounds_blender':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],
      'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects},
      'materials':sorted({o.data.materials[p.material_index].name.split('.')[0] for o in meshes for p in o.data.polygons})}
def build(name):
    O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True)
    root=init(name);contract=BUILD[name](root);bpy.context.view_layer.update();row=snapshot()
    assert row['triangles']<LIMITS[name],(name,row['triangles'],LIMITS[name])
    assert row['finite']
    for m in list(bpy.data.materials):
        if m.users==0:bpy.data.materials.remove(m)
    bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},
        axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=False if name=='Seal' else True,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=False,
        add_leaf_bones=False,bake_anim=name=='Seal',bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,
        bake_anim_step=1,bake_anim_simplify_factor=0,path_mode='AUTO',use_custom_props=True)
    row.update(name=name,contract=contract,limit=LIMITS[name],sha256={e:sha(O/(name+'.'+e)) for e in ('blend','fbx')},palette=P,status='Built; FBX/visual checks pending')
    (O/'metrics'/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n');print('SKERRIES BUILT',name,row['triangles'],flush=True)
if __name__=='__main__':build(sys.argv[sys.argv.index('--')+1])

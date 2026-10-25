"""GUT-ART-1 deterministic metre assets. Blender X,-Y,Z -> Unity X,Z,-Y.
Read-only shared geometry helpers; writes exclusively GutKit ownership trees.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/GutKit'
sys.path.insert(0,str(R/'Art/Source'));import build_crab_coast_props as H
G=H.Geometry
P={'M_DeckWood':'#C58B50','M_WoodRecess':'#8C5A36','M_Steel':'#8FA6AC','M_SafetyOrange':'#E36A35','M_RailIvory':'#F3F0DC','M_Rubber':'#28343B','M_Flesh':'#E8B4A0','M_Offal':'#6E2A2A','M_GullWhite':'#F1F0EA','M_GullGrey':'#9AA6AD'}
LIMITS={'GutBoard':900,'GutKnife':300,'BellyOpen':200,'BellyRagged':200,'GutBucket':500,'GullSkin':1500}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def u(p):return (p[0],p[2],-p[1])
def empty(n,parent=None):
    o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);o.parent=parent;o.empty_display_size=.05;return o

def mesh(g,n,parent):
    o=g.object(n,parent,bpy.context.scene.collection)
    used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];ids=[used.index(p.material_index) for p in o.data.polygons]
    o.data.materials.clear()
    for m in mats:o.data.materials.append(m)
    for p,i in zip(o.data.polygons,ids):p.material_index=i
    return o

def loop(w,d,c,z):
    return [(-w/2+c,-d/2,z),(w/2-c,-d/2,z),(w/2,-d/2+c,z),(w/2,d/2-c,z),(w/2-c,d/2,z),(-w/2+c,d/2,z),(-w/2,d/2-c,z),(-w/2,-d/2+c,z)]
def loft(g,rows,col,cap=True):
    n=len(rows[0]);vs=sum(rows,[]);fs=[]
    if cap:fs.append(tuple(reversed(range(n))))
    for k in range(len(rows)-1):fs += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)]
    if cap:fs.append(tuple(range((len(rows)-1)*n,len(rows)*n)))
    g.add(vs,fs,col)
def tube(g,pts,r,col,n=5):g.tube(pts,[r]*len(pts),n,col)

def board(root):
    g=G()
    # Real recessed perimeter: outer bevel, groove floor, inner slope, flat worktop.
    rings=[loop(.678,.338,.025,-.042),loop(.70,.36,.028,-.030),loop(.70,.36,.028,-.008),loop(.684,.344,.024,0),loop(.646,.306,.022,0),loop(.638,.298,.020,-.004),loop(.624,.284,.019,-.004),loop(.616,.276,.018,0)]
    n=8;g.add(rings[0],[tuple(reversed(range(n)))], 'M_WoodRecess')
    for k in range(len(rings)-1):
        g.add(rings[k]+rings[k+1],[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'M_WoodRecess' if k in (4,5) else 'M_DeckWood')
    g.add(rings[-1],[tuple(range(8))],'M_DeckWood')
    # Sparse tapered wear cuts are planar inlays, not noisy grain or large board gaps.
    for x,y,L in [(-.16,-.075,.18),(.055,-.046,.23),(-.055,.053,.20),(.11,.090,.13),(-.23,.018,.07)]:
        g.add([(x-L/2,y,.00015),(x+L/2,y+.001,.00015),(x+L*.22,y+.0022,.00015)],[(0,1,2)],'M_WoodRecess')
    # Steel spring clamp at +X head end; jaw rises above work plane, no blade-like spikes.
    g.box((.285,0,.006),(.080,.100,.012),'M_Steel')
    tube(g,[(.315,-.042,.016),(.285,-.042,.054),(.252,-.042,.052),(.242,-.042,.028)],.007,'M_Steel',6)
    tube(g,[(.315,.042,.016),(.285,.042,.054),(.252,.042,.052),(.242,.042,.028)],.007,'M_Steel',6)
    g.box((.245,0,.027),(.018,.091,.010),'M_Steel')
    g.box((.245,0,.020),(.014,.086,.006),'M_Rubber')
    for y in (-.031,.031):g.ellipsoid((.305,y,.014),(.005,.005,.002),6,1,'M_Rubber')
    o=mesh(g,'GutBoard',root);o['pivot']='Origin is worktop centre, Unity Y=0. Board substrate X .70 / Z .36, below origin; clamp +X.'

def knife(root):
    g=G()
    # Tip at exact zero, curved cutting edge; thickness tapers toward tip.
    poly=[(0,0),(-.036,.014),(-.106,.018),(-.166,.010),(-.168,-.014),(-.110,-.025),(-.048,-.018)]
    g.extrude_polygon(poly,-.0015,.0015,'M_Steel')
    # Broad bevel band on blade faces, using same steel slot and angular normals.
    g.beam((-.175,0,0),(-.286,.006,0),.030,.026,'M_SafetyOrange',.006)
    g.beam((-.166,0,0),(-.180,0,0),.037,.031,'M_Steel',.004)
    for x in (-.204,-.257):g.ellipsoid((x,.002,.015),(.004,.004,.0015),6,1,'M_Rubber')
    o=mesh(g,'GutKnife',root);o['pivot']='Exact blade tip (0,0,0); spine/handle extend -X; blade lies in local XZ plane. Follow drag by tip.'

def belly(root,ragged):
    g=G();n=13
    xs=[i/(n-1) for i in range(n)]
    widths=[.045*math.sin(math.pi*x)**.55 for x in xs]
    # Long shallow cavity with two lifted flesh lips; tip-to-tip length exactly1m.
    for i in range(n-1):
        a,b=xs[i:i+2]
        wa,wb=widths[i:i+2]
        for s in (-1,1):
            ja=(1+(.32 if i%2 else -.22)) if ragged and i not in (0,n-1) else 1
            jb=(1+(.32 if (i+1)%2 else -.22)) if ragged and i+1 not in (0,n-1) else 1
            g.add([(a,s*wa*ja,.004),(b,s*wb*jb,.004),(b,s*wb*.43,.012),(a,s*wa*.43,.012)],[(0,1,2,3)],'M_Flesh')
        g.add([(a,-wa*.43,.011),(b,-wb*.43,.011),(b,wb*.43,.011),(a,wa*.43,.011)],[(0,1,2,3)],'M_Offal')
    o=mesh(g,'BellyRagged' if ragged else 'BellyOpen',root)
    
    import bmesh
    bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0]);bm.to_mesh(o.data);bm.free();o.data.update()
    o['pivot']='Vent endpoint0 to gill endpoint+X1m, Y-up insert thickness .012. Scale X to cut length; optional Z width. One-sided facing +Y.'

def bucket(root):
    g=G();n=12
    rings=[]
    for z,r in [(0,.10),(.012,.116),(.235,.145),(.248,.147),(.248,.134),(.028,.108)]:
        rings.append([(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n)])
    loft(g,rings,'M_Steel',False)
    g.add(rings[0],[tuple(reversed(range(n)))],'M_Steel');g.add(rings[-1],[tuple(range(n))],'M_Rubber')
    # Handle folds to rear and remains within small deck-side footprint.
    tube(g,[(-.137,0,.19),(-.13,.095,.27),(0,.15,.29),(.13,.095,.27),(.137,0,.19)],.007,'M_Steel',4)
    tube(g,[(-.035,.146,.285),(.035,.146,.285)],.013,'M_Rubber',6)
    for c,r in [((-.045,-.025,.075),(.05,.035,.045)),((.035,.026,.080),(.048,.042,.046)),((.015,-.057,.068),(.056,.029,.037))]:g.ellipsoid(c,r,8,2,'M_Offal')
    o=mesh(g,'GutBucket',root);o['pivot']='Base centre Y=0; opening up +Y. Steel hollow bucket, folded handle,3 dark offal lumps.'

def gull(root):
    parent=empty('GullPerch',root);g=G();tags=[]
    def tag(st,b):tags.append((st,len(g.vertices),b))
    # Compact folded-wing adult: white breast/head, broad grey mantle, black primaries.
    st=0;g.ellipsoid((0,.025,.225),(.091,.150,.119),12,4,'M_GullWhite');tag(st,'Body')
    st=len(g.vertices);g.ellipsoid((0,-.080,.310),(.059,.067,.085),10,3,'M_GullWhite');tag(st,'Neck')
    st=len(g.vertices);g.ellipsoid((0,-.127,.377),(.061,.069,.060),12,4,'M_GullWhite')
    # Tapered beak, small darker lower-tip mark using permitted offal.
    loft(g,[[(-.026,-.174,.379),(.026,-.174,.379),(.021,-.174,.350),(-.021,-.174,.350)], [(-.008,-.248,.356),(.008,-.248,.356),(.008,-.248,.347),(-.008,-.248,.347)]],'M_SafetyOrange')
    for s in (-1,1):
        g.ellipsoid((s*.057,-.149,.388),(.009,.010,.010),8,2,'M_Rubber')
        g.ellipsoid((s*.064,-.153,.391),(.002,.003,.003),6,1,'M_GullWhite')
    g.box((.011,-.222,.349),(.010,.012,.004),'M_Offal');tag(st,'Head')
    st=len(g.vertices)
    for s in (-1,1):
        poly=[(s*.055,-.091,.284),(s*.100,-.035,.288),(s*.094,.080,.246),(s*.043,.195,.167),(s*.021,.082,.238)]
        loft(g,[poly,[(x+s*.010,y,z+.018) for x,y,z in poly]],'M_GullGrey')
        tip=[(s*.080,.087,.239),(s*.045,.203,.166),(s*.029,.180,.169),(s*.046,.071,.243)]
        loft(g,[tip,[(x+s*.003,y,z+.006) for x,y,z in tip]],'M_Rubber')
        # Two light feather tips deliberately broad enough for the phone.
        for y,z in [(.147,.197),(.177,.179)]:g.ellipsoid((s*.052,y,z+.009),(.007,.014,.004),6,1,'M_GullWhite')
    tail=[(-.037,.131,.188),(.037,.131,.188),(.046,.224,.159),(-.046,.224,.159)]
    loft(g,[tail,[(x,y,z+.009) for x,y,z in tail]],'M_GullWhite');tag(st,'Body')
    st=len(g.vertices)
    for s in (-1,1):
        tube(g,[(s*.035,.008,.150),(s*.034,.028,.067),(s*.035,.012,.014)],.009,'M_GullGrey',5)
        # Low webbed feet, three broad toe tips.
        poly=[(s*.035-.025,-.054),(s*.035-.009,-.040),(s*.035+.003,-.061),(s*.035+.014,-.039),(s*.035+.025,-.045),(s*.035+.014,.022),(s*.035-.013,.024)]
        g.extrude_polygon(poly,0,.010,'M_SafetyOrange')
    tag(st,'Root')
    skin=mesh(g,'GullSkin',parent)
    # Keep body softly rounded while wing/tail planes stay selected flat.
    for p in skin.data.polygons:p.use_smooth=p.material_index==list(skin.data.materials).index(H.MATERIALS['M_GullWhite']) and len(p.vertices)<=4
    ar=bpy.data.armatures.new('GullSkeleton');rig=bpy.data.objects.new('GullRig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=parent
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    spec=[('Root',(0,0,0),None),('Body',(0,0,.17),'Root'),('Neck',(0,-.062,.28),'Body'),('Head',(0,-.115,.35),'Neck')]
    for name,p,par in spec:
        b=ar.edit_bones.new(name);b.head=p;b.tail=Vector(p)+Vector((0,0,.05))
        if par:b.parent=ar.edit_bones[par]
    bpy.ops.object.mode_set(mode='OBJECT');skin.parent=rig
    m=skin.modifiers.new('GullSkinning','ARMATURE');m.object=rig
    for name,_,_ in spec:skin.vertex_groups.new(name=name);rig.pose.bones[name].rotation_mode='XYZ'
    for lo,hi,name in tags:skin.vertex_groups[name].add(list(range(lo,hi)),1,'REPLACE')
    sc=bpy.context.scene;sc.render.fps=30
    for name,end in [('Idle',121),('Lunge',31)]:
        a=bpy.data.actions.new(name);a.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=a
        for f in range(1,end+1,3):
            t=(f-1)/(end-1)
            for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
            if name=='Idle':
                rig.pose.bones['Body'].scale=(1+.012*math.sin(math.tau*t),1+.018*math.sin(math.tau*t),1)
                rig.pose.bones['Head'].rotation_euler.y=.12*math.sin(math.tau*t)
                rig.pose.bones['Head'].rotation_euler.x=.05*math.sin(2*math.tau*t)
            else:
                q=math.sin(math.pi*t)**3
                rig.pose.bones['Body'].rotation_euler.x=.32*q
                rig.pose.bones['Neck'].rotation_euler.x=.30*q
                rig.pose.bones['Head'].rotation_euler.x=.38*q
                for bn,delta in [('Neck',(0,-.055*q,-.012*q)),('Head',(0,-.045*q,-.008*q))]:rig.pose.bones[bn].location=ar.bones[bn].matrix_local.to_3x3().inverted()@Vector(delta)
            for pb in rig.pose.bones:
                for prop in ('location','rotation_euler','scale'):pb.keyframe_insert(prop,frame=f,group=pb.name)
        for fc in a.layers[0].strips[0].channelbag(rig.animation_data.action_slot).fcurves:
            for k in fc.keyframe_points:k.interpolation='LINEAR'
            if name=='Idle':fc.modifiers.new('CYCLES')
    rig.animation_data.action=bpy.data.actions['Idle'];sc.frame_start=1;sc.frame_end=121;sc.frame_set(1)
    parent['pivot']='Between feet Y=0, forward Unity +Z. Four-bone Legacy rig. Idle4s loop; Lunge1s one-shot returns to perch; no root travel.'

def snapshot():
    bpy.context.view_layer.update();rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        rows[o.name]={'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'bounds_unity':[[min(u(p)[i] for p in pts) for i in range(3)],[max(u(p)[i] for p in pts) for i in range(3)]],'materials':sorted(m.name for m in o.data.materials),'pivot_unity':list(u(o.location))}
    return {'meshes':rows,'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects},'triangles':sum(v['triangles'] for v in rows.values())}
def run():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    H.PALETTE=P;H.MATERIALS={k:H.material(k,v,.75) for k,v in P.items()}
    root=empty('GutKit');root['contract']='Toggle/instantiate individual children; common zero origins are intentional and overlap in clean source. Metres, Unity Y up.'
    for fn in (board,knife,lambda r:belly(r,False),lambda r:belly(r,True),bucket,gull):fn(root)
    row=snapshot()
    for k,v in row['meshes'].items():assert v['triangles']<=LIMITS[k],(k,v['triangles'],LIMITS[k])
    bpy.ops.wm.save_as_mainfile(filepath=str(O/'GutKit.blend'))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(O/'GutKit.fbx'),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=False,add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0,path_mode='AUTO',use_custom_props=True)
    row.update(palette=P,limits=LIMITS,sha256={e:sha(O/('GutKit.'+e)) for e in ('blend','fbx')})
    (O/'metrics/build.json').write_text(json.dumps(row,indent=2)+'\n')
    print('GUT BUILT',json.dumps(row),flush=True)
if __name__=='__main__':run()

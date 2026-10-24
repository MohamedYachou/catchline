"""r10+ overlay on archived r09, preserving approved front and CrewRig exactly.

Blender5.2 headless --python build_mira_r10.py -- --revision r10 --render all
Reads immutable iterations/r09/Mira.blend. Outputs only Mira-sol.
Optional --female/--no-female flag uses shared crew_female_shape.py.
"""
import argparse, ast, bpy, bmesh, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/CrewV2/Mira-sol'
BASE=OUT/'iterations/r09'
ORIGINAL=ROOT/'Art/Models/CrewRig/CrewRig.blend'
sys.path.insert(0,str(ROOT/'Art/Source'))
from crew_female_shape import female_shape, region_for_weights, VERSION
parser=argparse.ArgumentParser()
parser.add_argument('--revision',default='r10')
parser.add_argument('--render',choices=['none','quick','all'],default='all')
parser.add_argument('--samples',type=int,default=40)
parser.add_argument('--female',action=argparse.BooleanOptionalAction,default=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
PRE=OUT/'iterations'/args.revision
PRE.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Mira.blend'))
scene=bpy.context.scene; arm=bpy.data.objects['CrewRig']; col=arm.users_collection[0]
mats={m.name:m for m in bpy.data.materials}
# Reuse the archived geometric primitives, not the old builder's top-level run.
tree=ast.parse((BASE/'build_mira_sol.py').read_text())
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in {'Mesh','catmull','curves','signature'}]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'r09-primitives','exec'),globals())
baseline=signature(arm)
manifest=json.loads((BASE/'build-manifest.json').read_text())
assert baseline==manifest['contract']
original_hash=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
assert original_hash==manifest['original_sha256']
arm.animation_data.action=None
for p in arm.pose.bones: p.matrix_basis.identity()
scene.frame_set(1); bpy.context.view_layer.update()
meshes=[bpy.data.objects[n] for n in manifest['meshes']]
male_vertices={o.name:[tuple(v.co) for v in o.data.vertices] for o in meshes}
unchanged_weights={o.name:[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices] for o in meshes}


def components(me):
    adj=[set() for v in me.vertices]
    for e in me.edges:
        a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    left=set(range(len(adj)));out=[]
    while left:
        seed=min(left);comp={seed};stack=[seed];left.remove(seed)
        while stack:
            for i in adj[stack.pop()]:
                if i in left: left.remove(i);comp.add(i);stack.append(i)
        out.append(comp)
    return out


def digest_front(me,indices):
    # Canonical vertex positions+face positions/materials, independent of new indices.
    vv=sorted(tuple(me.vertices[i].co) for i in indices)
    ff=sorted((tuple(sorted(tuple(me.vertices[i].co) for i in p.vertices)),
               me.materials[p.material_index].name) for p in me.polygons if p.vertices[0] in indices)
    return hashlib.sha256(repr((vv,ff)).encode()).hexdigest()


old=bpy.data.objects['Mira_HairSculpt'];me=old.data; islands=components(me)
# Audit IDs are deterministic by smallest vertex index in the immutable r09.
# 0 crown,2..16 fringe and all front/side locks including their highlight strips.
front_ids=[0]+list(range(2,17))
keep=set().union(*(islands[i] for i in front_ids))
front_digest=digest_front(me,keep)
hair=Mesh();hair.quality=1
ordered=sorted(keep); remap={v:i for i,v in enumerate(ordered)}
for mat in me.materials: hair.materials.append(mat.name)
hair.v=[tuple(me.vertices[i].co) for i in ordered]
hair.w=[{'Head':1.0} for i in ordered]
for p in me.polygons:
    if p.vertices[0] in keep:
        hair.f.append(tuple(remap[i] for i in p.vertices));hair.mi.append(p.material_index)
front_vertices=len(hair.v);front_faces=len(hair.f)
# The new rear geometry alone uses a subtle longitudinal colour texture.
# Existing front material slots/geometry stay byte-for-byte equivalent.
strand_uv={}
tex=bpy.data.images.new('Mira_Hair',width=512,height=512)
pixels=[]
for y in range(512):
    v=y/511
    for x in range(512):
        u=x/511
        phase=math.tau*(u+.018*math.sin(v*math.tau))
        tone=1+.105*math.cos(phase*2)+.035*math.cos(phase*9+.5*math.sin(v*9))+.015*math.sin(x*91.7+y*17.3)
        pixels.extend((min(1,72/255*tone),min(1,39/255*tone),min(1,29/255*tone),1))
# Colour-only sRGB strand variation; no illumination or shadows painted in.
tex.pixels.foreach_set(pixels);tex.filepath_raw=str(OUT/'Mira_Hair.png');tex.file_format='PNG';tex.save()
tex.filepath=str(OUT/'Mira_Hair.png')
rear_mat=bpy.data.materials.new('Mira_Hair');rear_mat.use_nodes=True
bs=rear_mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.63
node=rear_mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=tex
rear_mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);mats['Mira_Hair']=rear_mat


def ribbon(path,widths,depths,mat='Mira_Hair',sides=8):
    """Flattened tapered curl clump with stable horizontal sections, not a rope.
    Vertical path is monotone except the last soft tip. Tonal ridge follows the
    flattened sculpt; no separate round highlight tubes and no alpha sorting.
    """
    vv=[];ff=[];mi=[]
    for j,p in enumerate(path):
        tangent=(Vector(path[min(j+1,len(path)-1)])-Vector(path[max(0,j-1)])).normalized()
        u=Vector((0,1,0)).cross(tangent).normalized()
        if u.length<.5:u=Vector((1,0,0))
        v=tangent.cross(u).normalized()
        for k in range(sides):
            a=math.tau*k/sides
            # Elliptical lobed section: a shallow crease along each broad face.
            lobe=1.0+.11*math.cos(3*a+.25)
            vv.append(Vector(p)+widths[j]*math.cos(a)*lobe*u+depths[j]*math.sin(a)*v)
    ff.append(tuple(reversed(range(sides))))
    for j in range(len(path)-1):
        for k in range(sides):
            a=j*sides+k;b=j*sides+(k+1)%sides
            ff.append((a,b,b+sides,a+sides))
    ff.append(tuple((len(path)-1)*sides+k for k in range(sides)))
    start=len(hair.f);offset=len(hair.v);hair.add(vv,ff,mat,'Head')
    for j in range(len(path)):
        for k in range(sides):strand_uv[offset+j*sides+k]=(k/sides,j/(len(path)-1))
    # Broad, restrained sculpted ridge on rear-facing facet, not hard stripes.
    if mat=='M_HairMira' and False:
        light='M_HairMiraLight'
        if light not in hair.materials: hair.materials.append(light)
        for j in range(len(path)-1):
            hair.mi[start+1+j*sides+1]=hair.materials.index(light)


# Rear scalp is now a gently corrugated surface with13 flowing fine layers.
# Its lower scalloped edge removes the r09 straight bob-like slab silhouette.
profile=[(.622,.111,.097),(.647,.145,.124),(.681,.166,.146),
         (.724,.179,.162),(.769,.183,.173),(.814,.180,.174),
         (.854,.171,.165),(.891,.146,.142),(.924,.102,.101),(.941,.043,.049)]
N=38;vv=[]
for j,(z,rx,ry) in enumerate(profile):
    t=j/(len(profile)-1)
    for k in range(N+1):
        a=-.13+(math.pi+.26)*k/N
        wave=13*a+.45*math.sin(t*math.pi)+t*.8
        ridge=.0030*math.cos(wave)+.0011*math.cos(2*wave)
        taper=math.sin(math.pi*max(.03,min(.97,t)))**.4
        zz=z+(.008*math.sin(11*a)+.005*math.cos(7*a))*(1-t)**4
        vv.append(((rx+ridge*taper)*math.cos(a),(ry+ridge*taper)*math.sin(a),zz))
ff=[]
for j in range(len(profile)-1):
    for k in range(N):
        a=j*(N+1)+k;ff.append((a,a+1,a+N+2,a+N+1))
offset=len(hair.v);hair.add(vv,ff,'Mira_Hair','Head')
for j in range(len(profile)):
    for k in range(N+1):strand_uv[offset+j*(N+1)+k]=(k/N*13,j/(len(profile)-1))

# Six thin overlapping swept layers sit over the scalp, ending individually.
for strand in range(4):
    a=.24+strand*.86
    path=[];ww=[];dd=[]
    for j in range(11):
        t=j/10; z=.909-.263*t
        aa=a+.11*math.sin(math.pi*t)+.06*math.sin(3*math.pi*t+strand)
        # Sample the actual shell profile instead of burying layers in its mass.
        lo=next((i for i in range(len(profile)-1) if profile[i][0]<=z<=profile[i+1][0]),0)
        f=max(0,min(1,(z-profile[lo][0])/(profile[lo+1][0]-profile[lo][0])))
        rx=profile[lo][1]*(1-f)+profile[lo+1][1]*f+.006
        ry=profile[lo][2]*(1-f)+profile[lo+1][2]*f+.006
        path.append((rx*math.cos(aa),ry*math.sin(aa),z))
        taper=min(1,.45+t*5,max(.025,(1-t)*5))
        ww.append(.013*taper);dd.append(.0045*taper)
    ribbon(path,ww,dd,sides=6)

# Nine independently layered wavy locks create the ponytail's actual volume.
# Three depth planes, unequal lengths and phases, narrower than old block locks.
specs=[]
# Fourteen overlapping narrow clumps in three depth layers form one full mass.
for i in range(14):
    layer=i//5;slot=i%5
    cx=.062+slot*.038+(.012 if layer==1 else 0)
    cy=.201+layer*.030+.018*math.sin(slot*1.1)
    specs.append((cx,cy,.0165,.010,.405+.036*math.sin(i*1.8),i*1.67))
for i,(cx,cy,width,depth,length,phase) in enumerate(specs):
    path=[];ww=[];dd=[]
    for j in range(24):
        t=j/23
        grow=math.sin(min(1,t*2.4)*math.pi/2)
        rootx=.080+(i%3)*.007;rooty=.157+(i//5)*.014
        x=rootx+(cx-rootx)*grow+.024*math.sin(t*math.tau*1.65+phase)*math.sin(math.pi*t)**.6
        y=rooty+(cy-rooty)*grow+.018*math.sin(t*math.tau*1.65+phase+.9)*math.sin(math.pi*t)
        z=.916-length*t+.009*math.sin(t*math.tau+phase)*math.sin(math.pi*t)
        # Soft fine outward S-tip, avoiding a blunt cut or sharp rectangular end.
        tip=max(0,(t-.76)/.24)
        x+=.020*(1-math.cos(math.pi*1.2*tip))*(1 if i%2 else -1)
        z+=.042*tip**2+.014*math.sin(math.pi*1.2*tip)
        y+=.013*math.sin(tip*math.pi)
        taper=min(1,.28+5*t,max(.025,(1-t)*5))
        path.append((x,y,z));ww.append(width*taper);dd.append(depth*taper)
    ribbon(path,ww,dd,mat='Mira_Hair',sides=4)

# Sparse separated fine loose ends, both behind the nape and pony silhouette.
for i,(cx,cy,z,length,phase) in enumerate([(.211,.239,.823,.22,0),(.084,.285,.756,.23,1.5),(.174,.289,.883,.19,2.4)]):
    path=[];ww=[];dd=[]
    for j in range(7):
        t=j/6
        path.append((cx+.012*math.sin(t*math.tau*1.2+phase),
                     cy+.009*math.cos(t*math.tau+phase),z-length*t))
        taper=max(.015,math.sin(math.pi*(.07+.93*t))**.7)
        ww.append(.004*taper);dd.append(.0023*taper)
    ribbon(path,ww,dd,mat='Mira_Hair',sides=6)

bpy.data.objects.remove(old,do_unlink=True)
hair_ob=hair.object('Mira_HairSculpt')
uv=hair_ob.data.uv_layers.new(name='RearStrandFlow')
for poly in hair_ob.data.polygons:
    coords=[strand_uv.get(i,(0,0)) for i in poly.vertices]
    seam=all(i in strand_uv for i in poly.vertices) and max(u for u,v in coords)-min(u for u,v in coords)>.6
    for li,co in zip(poly.loop_indices,coords):
        u,v=co
        if seam and u==0:u=1
        uv.data[li].uv=(u,v)
meshes=[bpy.data.objects[n] for n in manifest['meshes']]
# Explicit triangulation only on NEW hair; preserved coordinates remain exact.
bm=bmesh.new();bm.from_mesh(hair_ob.data)
bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(hair_ob.data);bm.free()
hair_ob.data.update();hair_ob.data.calc_loop_triangles()
new_keep=set(range(front_vertices))
assert digest_front(hair_ob.data,new_keep)==front_digest,'Approved front changed'

# Apply shared deformation only to clothes and torso accessories.
changed={}
for name in ('Mira_CoatHandsBoots','Mira_JewelleryBinoculars'):
    ob=bpy.data.objects[name];count=0
    for v in ob.data.vertices:
        weights={ob.vertex_groups[g.group].name:g.weight for g in v.groups}
        region=region_for_weights(weights)
        if region:
            co=female_shape(tuple(v.co),female=args.female,region=region)
            if (v.co-Vector(co)).length>1e-9:count+=1
            v.co=co
    ob.data.update();changed[name]=count
    assert [[(g.group,g.weight) for g in v.groups] for v in ob.data.vertices]==unchanged_weights[name]
for o in meshes:
    if o.name not in {'Mira_HairSculpt','Mira_CoatHandsBoots','Mira_JewelleryBinoculars'}:
        assert [tuple(v.co) for v in o.data.vertices]==male_vertices[o.name]
    o.data.calc_loop_triangles()
counts={o.name:len(o.data.loop_triangles) for o in meshes}; triangles=sum(counts.values())
assert triangles<=20000,(triangles,counts)
print('TRIANGLES',triangles,counts,flush=True)
assert signature(arm)==baseline
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1)
arm['crew_female_shape']=VERSION if args.female else 'male-original'
arm['female_shape_enabled']=args.female
for im in bpy.data.images:
    if im.name.startswith('Mira_Face'): im.filepath='//Mira_Face.png'
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True)
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(OUT/'Mira.fbx'),use_selection=True,
    object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,
    apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,
    bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,
    bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,
    use_custom_props=True,mesh_smooth_type='FACE',path_mode='RELATIVE')
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1)
manifest.update(revision=args.revision,triangles=triangles,meshes=counts,
    female_shape={'version':VERSION,'enabled':args.female,'vertices_changed':changed,
                  'weights_unchanged':True,'z_unchanged':True},
    r09_front_hair={'components':front_ids,'vertices':front_vertices,'sha256':front_digest,'exact':True},
    r09_archive_sha256=json.loads((BASE/'archive-sha256.json').read_text()))
(OUT/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
scene.cycles.samples=args.samples
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as e:print('CPU fallback',e,flush=True)
camera=bpy.data.objects['ReviewCamera'];studio=bpy.data.collections['REVIEW_STUDIO_not_exported']


def shot(name,angle=0,target=(0,0,.535),scale=1.19,size=(768,896),action='Idle',frame=1,elevated=.12):
    arm.animation_data.action=bpy.data.actions[action];scene.frame_set(frame)
    target=Vector(target);a=math.radians(angle)
    camera.location=target+Vector((math.sin(a)*3.4,-math.cos(a)*3.4,elevated))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=scale
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(PRE/(name+'.png'))
    bpy.ops.render.render(write_still=True)


if args.render!='none':
    shot('three-quarter',27,elevated=.22)
    shot('back',180)
    shot('back-hair',155,(.035,.11,.773),.58,(1024,1024),elevated=.10)
if args.render=='all':
    shot('front');shot('side',90)
    shot('face',18,(0,-.018,.818),.59,(1024,1024),elevated=.03)
    shot('idle',22,action='Idle',frame=13)
    shot('walk',22,action='Walk',frame=7)
    shot('carry',27,action='Carry',frame=7)
    shot('cast',27,action='Cast',frame=17)
    shot('walk-side',90,action='Walk',frame=7)
    shot('carry-side',90,action='Carry',frame=7)
    shot('cast-side',90,action='Cast',frame=17)
    # Exact same Mira clothes before/after shared deformation, no extra rig/actions.
    duplicates=[]
    for ob in meshes:
        dup=ob.copy();dup.data=ob.data.copy();studio.objects.link(dup)
        dup.parent=None;dup.location.x=-.34;duplicates.append(dup)
        dup.modifiers.clear()
        # Bake same Idle deformation onto both comparison figures.
        if ob.name in male_vertices and ob.name!='Mira_HairSculpt':
            for v,co in zip(dup.data.vertices,male_vertices[ob.name]):v.co=co
        # Use original rig via duplicate armature modifier, shifted rig in world.
    ref_arm=arm.copy();ref_arm.data=arm.data.copy();studio.objects.link(ref_arm)
    ref_arm.location.x=-.34;ref_arm.animation_data.action=bpy.data.actions['Idle']
    for dup in duplicates:
        dup.parent=ref_arm;dup.location.x=0
        m=dup.modifiers.new('OriginalRigComparison','ARMATURE');m.object=ref_arm
    arm.location.x=.34
    shot('female-body-comparison',0,(0,0,.535),1.54,(1400,1100))
    shot('female-torso-comparison',0,(0,-.02,.37),1.05,(1400,780),elevated=0)
    # Side-by-side profiles, same camera/scale, compare actual garment depth.
    arm.rotation_euler.z=math.pi/2;ref_arm.rotation_euler.z=math.pi/2
    shot('female-profile-comparison',0,(0,0,.37),1.05,(1400,780),elevated=0)
    arm.rotation_euler.z=0;ref_arm.rotation_euler.z=0
    arm.location.x=0
    for ob in duplicates+[ref_arm]:bpy.data.objects.remove(ob,do_unlink=True)
    # Original current deck captain at exactly the unchanged rig scale.
    with bpy.data.libraries.load(str(ORIGINAL),link=False) as (src,dest):
        dest.objects=['CrewRig','Body','Outfit_Captain','Hat_CaptainCap']
    ref=[];ref_arm=next(o for o in dest.objects if o.type=='ARMATURE')
    for ob in dest.objects:
        studio.objects.link(ob);ob.hide_render=False;ob.hide_viewport=False;ob.hide_set(False);ref.append(ob)
    ref_arm.location.x=-.48;arm.location.x=.38
    ref_arm.animation_data.action=bpy.data.actions['Idle']
    shot('same-scale',0,(-.03,0,.535),1.85,(1400,1000))
    arm.location.x=0
    for ob in ref:bpy.data.objects.remove(ob,do_unlink=True)
    for a in list(bpy.data.actions):
        if a.name not in baseline['actions']:bpy.data.actions.remove(a)
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1)
assert signature(arm)==baseline
# Saved scene opens on useful full model view, not the comparison setup.
target=Vector((0,0,.535));camera.location=target+Vector((1.54,-3.03,.22))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.19
scene.render.resolution_x,scene.render.resolution_y=768,896
tex.filepath='//Mira_Hair.png'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Mira.blend'),relative_remap=False)
for filename in ('Mira.blend','Mira.fbx','build-manifest.json','Mira_Face.png','Mira_Hair.png'):
    import shutil
    shutil.copy2(OUT/filename,PRE/filename)
shutil.copy2(Path(__file__),PRE/'build_mira_r10.py')
shutil.copy2(ROOT/'Art/Source/crew_female_shape.py',PRE/'crew_female_shape.py')
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==original_hash
print('MIRA OVERLAY COMPLETE',args.revision,triangles,'triangles; original contract/front exact',flush=True)

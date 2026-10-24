"""Add fitted scalp coverage to completed crew, without touching active builders."""
raise RuntimeError('REJECTED by Mo; original models restored. Original builders own corrections. Do not run this draft.')
import bpy, bmesh, json, math, sys, shutil, argparse, hashlib, time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--quick',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
N=a.name;O=R/'Art/Models/CrewV2'/('Mira-sol' if N=='Mira' else N)
B=O/'iterations/hairfix-before';B.mkdir(exist_ok=True)
if not (B/(N+'.blend')).exists():
    for f in O.iterdir():
        if f.is_file() and f.suffix in ('.blend','.fbx','.png','.json','.md'):shutil.copy2(f,B/f.name)
P=O/'iterations/hairfix-01';P.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(B/(N+'.blend')))
bpy.context.preferences.filepaths.save_version=0
s=bpy.context.scene;arm=bpy.data.objects['CrewRig'];arm.data.pose_position='REST';bpy.context.view_layer.update()
m=json.loads((B/'build-manifest.json').read_text());meshes=[bpy.data.objects[n] for n in m['meshes']]
face=next(o for o in meshes if 'Face' in o.name and 'Expression' not in o.name)
bm=bmesh.new();bm.from_mesh(face.data);tree=BVHTree.FromBMesh(bm)
hair=[o for o in meshes if 'Hair' in o.name]
mat=next((ma for o in hair for ma in o.data.materials if ma and ma.name in ('M_HairCrew','M_HairChestnut','M_Hair')),None)
if mat is None:mat=next(ma for o in hair for ma in o.data.materials if ma and 'Hair' in ma.name and not ma.use_nodes is False)
# Plain, matte base colour under existing detailed strands; never paint the face.
mat=mat.copy();mat.name=N+'_CoverageHair'
if N=='Mira':colour='#503020'
elif N=='Lise':colour='#B63C0A'
elif N=='Dirk':colour='#A9A7A1'
else:colour='#503020'
def lin(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
bs=mat.node_tree.nodes.get('Principled BSDF')
for link in list(mat.node_tree.links):
    if link.to_node==bs and link.to_socket.name=='Base Color':mat.node_tree.links.remove(link)
bs.inputs['Base Color'].default_value=tuple(lin(int(colour[i:i+2],16)/255) for i in (1,3,5))+(1,)
bs.inputs['Roughness'].default_value=.78
if N=='Lise':
    # Existing fine colour fibres also shade the new underlayer, avoiding a flat cap.
    tex=bpy.data.images.load(str(O/'Lise_Hair.png'),check_existing=True)
    node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=tex
    mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
verts=[];faces=[]
def surface(theta,z,offset=.003):
    direction=Vector((math.cos(theta),math.sin(theta),0))
    hit,normal,_,_=tree.ray_cast(Vector((0,0,z)),direction,1)
    assert hit is not None,(theta,z)
    return hit+direction*offset
def patch(lo,hi,bottom,top,nx,nz,scallop=.003):
    start=len(verts)
    for j in range(nz):
        t=j/(nz-1)
        for i in range(nx):
            u=i/(nx-1);theta=lo+(hi-lo)*u
            z0=bottom+scallop*(.5+.5*math.cos(u*math.tau*5))
            z=z0+(top-z0)*t
            verts.append(surface(theta,z,.0055+.0008*math.sin(u*math.tau*6)))
    for j in range(nz-1):
        for i in range(nx-1):
            q=start+j*nx+i;faces.append((q,q+1,q+nx+1,q+nx))
# Both temples, from the hat down to a short scalloped sideburn; no cheeks/eyes.
patch(-.92,.20,.805,.946,12,8,.009)
patch(math.pi-.20,math.pi+.92,.805,.946,12,8,.009)
if N=='Lise':
    # A connected scalp-fitting foundation beneath the fine separated waves.
    patch(-.26,math.pi+.26,.656,.925,34,10,.009)
    patch(-.65,.20,.772,.908,14,5,.014)
    patch(math.pi-.20,math.pi+.65,.772,.908,14,5,.014)
me=bpy.data.meshes.new(N+'_HairCoverage');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
uv=me.uv_layers.new(name='CoverageFibres')
for loop in me.loops:
    v=me.vertices[loop.vertex_index].co
    uv.data[loop.index].uv=(math.atan2(v.y,v.x)/math.tau*5,(v.z-.65)/.30)
ob=bpy.data.objects.new(N+'_HairCoverage',me);arm.users_collection[0].objects.link(ob);ob.parent=arm
vg=ob.vertex_groups.new(name='Head');vg.add(list(range(len(verts))),1,'REPLACE')
mod=ob.modifiers.new('Original CrewRig','ARMATURE');mod.object=arm
for poly in me.polygons:poly.use_smooth=True
# Keep original mesh list and validator contract: join coverage into hair only.
target=max(hair,key=lambda o:len(o.data.polygons))
bpy.ops.object.select_all(action='DESELECT');target.select_set(True);ob.select_set(True);bpy.context.view_layer.objects.active=target;bpy.ops.object.join()
def tris(o):o.data.calc_loop_triangles();return len(o.data.loop_triangles)
total=sum(tris(o) for o in meshes)
if total>19995:
    # Tiny topology reduction on hair alone; face/clothes/rig remain exact.
    keep=tris(target)-(total-19985)
    bpy.context.view_layer.objects.active=target
    md=target.modifiers.new('HairOnlyBudget','DECIMATE');md.ratio=keep/tris(target)
    bpy.ops.object.modifier_move_up(modifier=md.name);bpy.ops.object.modifier_apply(modifier=md.name)
total=sum(tris(o) for o in meshes);assert total<=20000,total
bm.free()
m['revision']='hairfix-01';m['triangles']=total;m['meshes']={o.name:tris(o) for o in meshes}
m['hairfix']={'baseline':str(B.relative_to(R)),'coverage':'both temples; Lise continuous scalp underlayer','face_and_clothing':'unchanged'}
arm.data.pose_position='POSE';arm.animation_data.action=bpy.data.actions['Idle'];s.frame_set(1)
for image in bpy.data.images:
    candidate=O/image.filepath.replace('\\','/').split('/')[-1]
    if candidate.is_file():image.filepath='//'+candidate.name
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True)
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(O/(N+'-hairfix.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,use_custom_props=True,mesh_smooth_type='FACE',path_mode='RELATIVE')
def publish(src,dst):
    for attempt in range(12):
        try:src.replace(dst);return
        except PermissionError:
            if attempt==11:raise
            time.sleep(.5)
publish(O/(N+'-hairfix.fbx'),O/(N+'.fbx'))
bpy.ops.wm.save_as_mainfile(filepath=str(O/(N+'-hairfix.blend')),relative_remap=False)
publish(O/(N+'-hairfix.blend'),O/(N+'.blend'))
(O/'build-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
camera=s.camera;s.cycles.samples=12;s.render.resolution_percentage=100
def shot(name,angle,target=(0,-.018,.807),scale=.53,size=(768,768),action='Idle',frame=1):
    arm.animation_data.action=bpy.data.actions[action];s.frame_set(frame)
    t=Vector(target);angle=math.radians(angle);camera.location=t+Vector((math.sin(angle)*3.4,-math.cos(angle)*3.4,.03))
    camera.rotation_euler=(t-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    s.render.resolution_x,s.render.resolution_y=size;s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
shot('face',18);shot('temple-left',65);shot('temple-right',-65)
if not a.quick:
    shot('back-hair',180);shot('three-quarter',27,(0,0,.52),1.17,(768,896))
    shot('front',0,(0,0,.52),1.17,(768,896));shot('side',90,(0,0,.52),1.17,(768,896));shot('back',180,(0,0,.52),1.17,(768,896))
    shot('walk',22,(0,0,.52),1.17,(768,896),'Walk',7);shot('idle',22,(0,0,.52),1.17,(768,896),'Idle',13)
print('HAIRFIX COMPLETE',N,total,flush=True)

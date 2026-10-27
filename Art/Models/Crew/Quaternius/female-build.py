import bpy, json, math, sys, hashlib, time
from pathlib import Path
from mathutils import Vector

O=Path(__file__).resolve().parent
R=O.parents[3]
S=R/'Art/Downloads/quaternius/base/Universal Base Characters[Standard]'
H=S/'Hairstyles/Rigged to Head Bone/FBX (Unity)'
NAMES=['mira','noor','rosa','tess','ana','lise','ines','tove']
def read_rows(): return json.loads((O/'female-palette.json').read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clear(): bpy.ops.wm.read_factory_settings(use_empty=True)
def imp(p):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(p),use_anim=False)
    return list(set(bpy.data.objects)-before)
def linear(h):
    a=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)
def mat(name,h,texture=None):
    old=bpy.data.materials.get(name)
    if old: bpy.data.materials.remove(old,do_unlink=True)
    m=bpy.data.materials.new(name); m.diffuse_color=(*linear(h),1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*linear(h),1);p.inputs['Roughness'].default_value=.78
    if texture:
        t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texture),check_existing=True)
        m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
    return m
def skeleton(a):
    return {b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(v) for v in b.matrix_local]} for b in a.data.bones}
def build(row):
    clear();gender='Female' if row['gender']=='F' else 'Male'
    src=S/f'Base Characters/Unity/Superhero_{gender}_FullBody.fbx'
    objs=imp(src);a=next(o for o in objs if o.type=='ARMATURE')
    base=max((o for o in objs if o.type=='MESH'),key=lambda o:len(o.data.vertices))
    baseline={'skeleton':skeleton(a),'armature_matrix':[list(v) for v in a.matrix_world],'body_vertices':len(base.data.vertices),'body_polygons':len(base.data.polygons)}
    # Keep the original eyes; replace the included brows with the supplied matching rigged variant.
    for o in objs:
        if o.type=='MESH' and 'Eyebrow' in o.name: bpy.data.objects.remove(o,do_unlink=True)
    skin=mat('Skin',row['skinHex'],O/f"female-{row['name']}-skin.png")
    suit=mat('Suit',row['suitHex']);hair=mat('Hair',row['hairHex']);brows=mat('Brows',row['hairHex'])
    eyes=mat('Eyes',row['eyeHex'],O/f"female-{row['name']}-eyes.png")
    base.data.materials.clear();base.data.materials.append(skin);base.data.materials.append(suit)
    # Partition the untouched body topology by original skinning weights: head/neck and hand/fingers stay bare.
    bare=lambda n:n in ('Head','neck_01','hand_l','hand_r') or any(n.startswith(p) for p in ('thumb_','index_','middle_','ring_','pinky_'))
    weights=[]
    for v in base.data.vertices:
        weights.append(sum(g.weight for g in v.groups if bare(base.vertex_groups[g.group].name)))
    for p in base.data.polygons:p.material_index=0 if sum(weights[i] for i in p.vertices)/len(p.vertices)>.5 else 1
    eyeobj=bpy.data.objects['Eyes'];eyeobj.data.materials.clear();eyeobj.data.materials.append(eyes)
    attachments=[]
    for hn,ma in [(row['hair'],hair),('Eyebrows_Female' if row['gender']=='F' else 'Eyebrows_Regular',brows)]:
        added=imp(H/(hn+'.fbx'));part=next(o for o in added if o.type=='MESH');other=next(o for o in added if o.type=='ARMATURE')
        world=part.matrix_world.copy()
        for mod in list(part.modifiers):
            if mod.type=='ARMATURE':part.modifiers.remove(mod)
        part.parent=a;part.parent_type='BONE';part.parent_bone='Head'
        bpy.context.view_layer.update();part.matrix_world=world
        part.data.materials.clear();part.data.materials.append(ma)
        for ob in added:
            if ob!=part:bpy.data.objects.remove(ob,do_unlink=True)
        attachments.append(part)
    bpy.context.view_layer.update()
    assert skeleton(a)==baseline['skeleton']
    assert not bpy.data.actions
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(meshes)==4
    assert {m.name for o in meshes for m in o.data.materials}=={'Skin','Suit','Hair','Eyes','Brows'}
    for o in bpy.context.scene.objects:o.select_set(True)
    bpy.context.view_layer.objects.active=a
    bpy.ops.export_scene.fbx(filepath=str(O/(row['name']+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=False,path_mode='COPY',embed_textures=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(O/f"female-{row['name']}.blend"))
    baseline.update(name=row['name'],gender=row['gender'],source=str(src.relative_to(R)),source_sha256=sha(src),fbx_sha256=sha(O/(row['name']+'.fbx')),materials=['Skin','Suit','Hair','Eyes','Brows'],skin_faces=sum(p.material_index==0 for p in base.data.polygons),suit_faces=sum(p.material_index==1 for p in base.data.polygons),triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),bone_count=len(a.data.bones))
    (O/f"female-{row['name']}-baseline.json").write_text(json.dumps(baseline,indent=2))
    print('BUILT',row['name'],baseline['bone_count'],baseline['triangles'],flush=True)
    return baseline
def setup_camera(target,scale,w,h):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
    scene.cycles.use_denoising=True;scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100
    if not scene.world:scene.world=bpy.data.worlds.new('ProofWorld')
    scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.45,.45,.45,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.55
    scene.view_settings.view_transform='Standard';scene.view_settings.exposure=.35
    p=math.radians(38);y=math.radians(2)
    direction=Vector((math.sin(y)*math.cos(p),math.cos(y)*math.cos(p),math.sin(p)))
    bpy.ops.object.camera_add(location=Vector(target)+direction*20)
    c=bpy.context.object;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;scene.camera=c
    for loc,power,size in [((-4,5,8),150,5),((4,2,6),80,5),((0,-4,6),100,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector(target)-l.location).to_track_quat('-Z','Y').to_euler()
def floor(xmin,xmax,ymin,ymax):
    m=mat('ProofFloor','#E8E3D8');line=mat('Grid1m','#B6B6AC')
    bpy.ops.mesh.primitive_plane_add(size=2,location=((xmin+xmax)/2,(ymin+ymax)/2,-.015));o=bpy.context.object;o.scale=((xmax-xmin)/2,(ymax-ymin)/2,1);o.data.materials.append(m)
    for x in range(math.ceil(xmin),math.floor(xmax)+1):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(x,(ymin+ymax)/2,-.012));o=bpy.context.object;o.scale=(.006,ymax-ymin,.003);o.data.materials.append(line)
    for y in range(math.ceil(ymin),math.floor(ymax)+1):
        bpy.ops.mesh.primitive_cube_add(size=1,location=((xmin+xmax)/2,y,-.012));o=bpy.context.object;o.scale=(xmax-xmin,.006,.003);o.data.materials.append(line)
def render_row(row):
    bpy.ops.wm.open_mainfile(filepath=str(O/f"female-{row['name']}.blend"))
    floor(-8,8,-8,8);setup_camera((0,0,.86),2.6,900,1100)
    bpy.context.scene.render.image_settings.file_format='PNG';bpy.context.scene.render.filepath=str(O/f"female-{row['name']}-proof.png");bpy.ops.render.render(write_still=True)
def render_grid(rows,do_render=True):
    clear();roster=[]
    for i,row in enumerate(rows):
        added=imp(O/(row['name']+'.fbx'));a=next(o for o in added if o.type=='ARMATURE');a.location.x=(i%4)*2.3-3.45;a.location.y=-(i//4)*3.5;roster.append((row,added,a))
    floor(-6,6,-5,2);setup_camera((0,-1.6,.7),11.1,2400,1500)
    bpy.context.view_layer.update()
    from bpy_extras.object_utils import world_to_camera_view
    scene=bpy.context.scene;bounds={}
    for row,added,a in roster:
        pts=[world_to_camera_view(scene,scene.camera,o.matrix_world@Vector(c)) for o in added if o.type=='MESH' for c in o.bound_box]
        box=[min(p.x for p in pts)*2400,(1-max(p.y for p in pts))*1500,max(p.x for p in pts)*2400,(1-min(p.y for p in pts))*1500]
        assert 0<box[0]<box[2]<2400 and 0<box[1]<box[3]<1500,box
        foot=world_to_camera_view(scene,scene.camera,a.location)
        bounds[row['name']]={'bbox':box,'label':[foot.x*2400,(1-foot.y)*1500+20]}
    (O/'female-grid-bounds.json').write_text(json.dumps(bounds,indent=2))
    if do_render:
        scene.render.image_settings.file_format='PNG';scene.render.filepath=str(O/'female-grid.png');bpy.ops.render.render(write_still=True)
def validate(row):
    baseline=json.loads((O/f"female-{row['name']}-baseline.json").read_text());clear();added=imp(O/(row['name']+'.fbx'));a=next(o for o in added if o.type=='ARMATURE')
    now=skeleton(a);old=baseline['skeleton']
    assert set(now)==set(old),(set(now)-set(old),set(old)-set(now))
    error=max(abs(now[n]['matrix'][i][j]-old[n]['matrix'][i][j]) for n in old for i in range(4) for j in range(4))
    assert error<1e-4,error # FBX float/Euler roundtrip tolerance; no deliberate rig edits.
    assert all(now[n]['parent']==old[n]['parent'] for n in old)
    arm_error=max(abs(a.matrix_world[i][j]-baseline['armature_matrix'][i][j]) for i in range(4) for j in range(4));assert arm_error<1e-5,arm_error
    assert not bpy.data.actions
    pose_error=max(abs(p.matrix_basis[i][j]-(1 if i==j else 0)) for p in a.pose.bones for i in range(4) for j in range(4))
    print('POSE_ERROR',pose_error,flush=True);assert pose_error<1e-4,pose_error
    meshes=[o for o in added if o.type=='MESH'];assert len(meshes)==4
    mats={m.name.split('.')[0] for o in meshes for m in o.data.materials};assert mats=={'Skin','Suit','Hair','Eyes','Brows'},mats
    texture_info=[]
    for o in meshes:
        for m in o.data.materials:
            if m.use_nodes:
                for node in m.node_tree.nodes:
                    if node.type=='TEX_IMAGE':
                        image=node.image;assert image and image.size[0]>0 and len(image.pixels)>0
                        texture_info.append({'material':m.name,'image':image.name,'size':list(image.size)})
    assert len(texture_info)==2,texture_info
    body=max(meshes,key=lambda o:len(o.data.vertices));assert len(body.data.polygons)==baseline['body_polygons']
    parts=[o for o in meshes if o.parent_type=='BONE'];assert len(parts)==2
    assert all(o.parent_bone=='Head' and o.parent==a for o in parts)
    # Exercise head following on the fresh import, then restore pose; exports remain bind pose.
    before=[o.matrix_world.copy() for o in parts];a.pose.bones['Head'].rotation_mode='XYZ';a.pose.bones['Head'].rotation_euler.z=.3;bpy.context.view_layer.update()
    follows=[max(abs(o.matrix_world[i][j]-b[i][j]) for i in range(4) for j in range(4)) for o,b in zip(parts,before)];assert min(follows)>.01
    a.pose.bones['Head'].rotation_euler.z=0
    sourceobjs=imp(R/baseline['source']);sourcebody=max((o for o in sourceobjs if o.type=='MESH'),key=lambda o:len(o.data.vertices))
    # Match source vertices geometrically, allowing only FBX seam splitting and float rounding.
    from mathutils.kdtree import KDTree
    tree=KDTree(len(sourcebody.data.vertices))
    for v in sourcebody.data.vertices:tree.insert(v.co,v.index)
    tree.balance();geom_error=0;weight_error=0
    def vw(o,v):return {o.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>1e-6}
    for v in body.data.vertices:
        _,idx,dist=tree.find(v.co);geom_error=max(geom_error,dist)
        sw=vw(sourcebody,sourcebody.data.vertices[idx]);tw=vw(body,v)
        weight_error=max(weight_error,max([abs(sw.get(n,0)-tw.get(n,0)) for n in set(sw)|set(tw)]+[0]))
    assert geom_error<1e-5,geom_error
    assert weight_error<1e-5,weight_error
    uv_error=max(abs(body.data.uv_layers.active.data[i].uv[j]-sourcebody.data.uv_layers.active.data[i].uv[j]) for i in range(len(body.data.loops)) for j in (0,1))
    assert uv_error<1e-5,uv_error
    result=dict(name=row['name'],PASS=True,bones=len(now),rest_matrix_max_error=error,armature_matrix_max_error=arm_error,pose_identity_max_error=pose_error,head_follow_delta=follows,animation_clips=0,mesh_count=4,materials=sorted(mats),decoded_textures=texture_info,body_geometry_max_error=geom_error,body_skinweight_max_error=weight_error,body_uv_max_error=uv_error,fbx_sha256=sha(O/(row['name']+'.fbx')))
    (O/f"female-{row['name']}-audit.json").write_text(json.dumps(result,indent=2));print('VERIFIED',json.dumps(result),flush=True)
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];mode=args[0];rows=read_rows();selected=[r for r in rows if not args[1:] or r['name'] in args[1:]]
    if mode=='build':
        for row in selected:build(row)
    if mode=='verify':
        for row in selected:validate(row)
    if mode=='render':
        for row in selected:render_row(row)
    if mode=='grid':render_grid(rows)
    if mode=='bounds':render_grid(rows,False)

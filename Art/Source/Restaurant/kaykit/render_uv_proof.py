"""Run with standalone Blender; read-only original Unity FBXs, no production edits."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
SETS={
 'restaurant':['chair_A','table_round_A_decorated','kitchencounter_straight_A_decorated','kitchencounter_sink','oven','fridge_A_decorated','wall_orderwindow_decorated','food_dinner'],
 'furniture':['chair_A','chair_A_wood','couch_pillows','armchair','cabinet_medium_decorated','shelf_B_large_decorated','lamp_standing','table_medium'],
}
inventory=json.loads((OUT/'source-inventory.json').read_text())
records=[]
for pack,names in SETS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=24
    scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.world=bpy.data.worlds.new('Proof neutral world');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.65,0.71,0.74,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.65
    scene.view_settings.view_transform='Standard'
    mat=bpy.data.materials.new('Original UV / atlas-only replacement');mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.8
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.interpolation='Linear'
    mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
    for index,name in enumerate(names):
        before=set(bpy.data.objects)
        file=ROOT/'Art/Downloads/kaykit'/pack/'addons'/f'kaykit_{pack}_bits'/'Assets/fbx(unity)'/(name+'.fbx')
        bpy.ops.import_scene.fbx(filepath=str(file))
        new=[o for o in bpy.data.objects if o not in before];meshes=[o for o in new if o.type=='MESH']
        coords=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
        mn=Vector(tuple(min(p[j] for p in coords) for j in range(3)));mx=Vector(tuple(max(p[j] for p in coords) for j in range(3)))
        factor=1.65/max(mx-mn);centre=(mn+mx)/2
        group=bpy.data.objects.new(name+' proof placement',None);scene.collection.objects.link(group)
        for o in new:
            if o.parent not in new:o.parent=group
        group.scale=(factor,)*3
        group.location=Vector(((index%4-1.5)*2.6,(index//4-.5)*3.0,0))-Vector((centre.x,centre.y,mn.z))*factor
        for o in meshes:
            o.data.materials.clear();o.data.materials.append(mat)
        records.append(dict(pack=pack,model=name,meshes=len(meshes),uv_layers=[len(o.data.uv_layers) for o in meshes],file=str(file.relative_to(ROOT))))
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.02));floor=bpy.context.object
    m=bpy.data.materials.new('Cream proof background');m.diffuse_color=(.78,.75,.68,1);floor.data.materials.append(m)
    bpy.ops.object.light_add(type='AREA',location=(-3,-4,8));bpy.context.object.data.energy=1000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=7
    bpy.ops.object.camera_add(location=(8,-13,13));cam=bpy.context.object
    cam.rotation_euler=(Vector((0,0,.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=13.5;scene.camera=cam
    for variant in ('original','catchline'):
        imagepath=ROOT/inventory[pack]['source'] if variant=='original' else OUT/f'{pack}bits_texture-catchline.png'
        tex.image=bpy.data.images.load(str(imagepath),check_existing=False)
        tex.image.reload()
        assert tuple(tex.image.size)==(1024,1024),str(imagepath)
        tex.image.pack()
        scene.render.filepath=str(OUT/f'{pack}-fbx-{variant}.png')
        bpy.ops.render.render(write_still=True)
(OUT/'fbx-proof-inventory.json').write_text(json.dumps(records,indent=2))
print('UV_PROOF_DONE sixteen original FBXs, four renders, no UV/mesh edits')

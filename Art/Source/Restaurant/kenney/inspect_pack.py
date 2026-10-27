"""Read-only pack inventory and candidate renders. Run in standalone Blender."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
FOOD=['fish','bowl-soup','bowl-broth','plate','plate-dinner','plate-rectangle','lemon-half','fries','bread','loaf-baguette','cup-coffee','cup-tea','cup-saucer','mug','glass','soda-glass','cocktail','mussel-open','onion-half','paprika-slice','meat-cooked','sushi-salmon']
DECOR=['pottedPlant','plantSmall1','plantSmall2','plantSmall3','lampWall','lampRoundFloor','lampRoundTable','bookcaseOpenLow','bookcaseOpen','bench','benchCushion','rugRectangle','rugDoormat','coatRackStanding']
def source(pack,name):
    return ROOT/'Art/Downloads/kenney'/pack/'Models'/('GLB format' if pack=='food' else 'GLTF format')/(name+'.glb')
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def load(path):
    before=set(bpy.data.objects)
    if path.suffix=='.fbx': bpy.ops.import_scene.fbx(filepath=str(path))
    else:bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.data.objects if o not in before]
def bounds(obs):
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(v) for o in obs if o.type=='MESH' for v in o.bound_box]
    return Vector([min(v[i] for v in pts) for i in range(3)]),Vector([max(v[i] for v in pts) for i in range(3)])
def setup(width=500,height=400):
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
    s.render.resolution_x=width;s.render.resolution_y=height;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
    s.world=bpy.data.worlds.new('Soft ambient');s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.73,.79,1)
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015));m=bpy.data.materials.new('Cream');m.diffuse_color=(.84,.81,.73,1);bpy.context.object.data.materials.append(m)
    bpy.ops.object.light_add(type='AREA',location=(-3,-4,7));bpy.context.object.data.energy=750;bpy.context.object.data.size=5
    bpy.ops.object.camera_add(location=(.10,-3.2,2.50));c=bpy.context.object;c.rotation_euler=(Vector((0,0,.5))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=2.6;s.camera=c
    return s
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);(OUT/'candidates').mkdir(exist_ok=True)
    base={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'Art/Downloads/kenney').rglob('*') if p.is_file()}
    (OUT/'preservation-baseline.json').write_text(json.dumps(base,indent=2))
    records=[]
    selections=[('food',n,source('food',n)) for n in FOOD]+[('furniture',n,source('furniture',n)) for n in DECOR]
    selections += [('kaykit','table_round_A',ROOT/'Art/Downloads/kaykit/restaurant/addons/kaykit_restaurant_bits/Assets/fbx(unity)/table_round_A.fbx')]
    for pack,name,path in selections:
        reset();obs=load(path);lo,hi=bounds(obs)
        mats=[]
        for o in obs:
            if o.type!='MESH':continue
            for m in o.data.materials:
                if not m or any(x['name']==m.name for x in mats):continue
                bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
                mats.append(dict(name=m.name,diffuse=list(m.diffuse_color),base=list(bs.inputs['Base Color'].default_value) if bs else None,images=[dict(name=n.image.name,size=list(n.image.size),path=n.image.filepath) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []))
        records.append(dict(pack=pack,name=name,path=str(path.relative_to(ROOT)),min=list(lo),max=list(hi),size=list(hi-lo),materials=mats,meshes=len([o for o in obs if o.type=='MESH'])))
        fac=1.8/max(hi-lo);group=bpy.data.objects.new('inspection only',None);bpy.context.scene.collection.objects.link(group)
        for o in obs:
            if o.parent not in obs:o.parent=group
        group.scale=(fac,)*3;group.location=-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))*fac
        s=setup();s.render.filepath=str(OUT/'candidates'/f'{pack}-{name}.png');bpy.ops.render.render(write_still=True)
        (OUT/'source-inventory.json').write_text(json.dumps(records,indent=2))
    print('INVENTORY_DONE',len(records),'models',len(base),'preserved files')

"""Standalone Blender source-only dish/decor study; exact source recipes, no Assets writes."""
import bpy,bmesh,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from inspect_pack import load,bounds,source,reset
O=Path(__file__).resolve().parent;R=O.parents[3]
for n in ['renders','derived']: (O/n).mkdir(exist_ok=True)
K=R/'Art/Downloads/kaykit/restaurant/addons/kaykit_restaurant_bits/Assets/fbx(unity)'
FM=json.loads((O/'furniture-materials-catchline.json').read_text())['materials']
def srgb(h):
    v=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)
def material(name,h):
    m=bpy.data.materials.new(name);m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*srgb(h),1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.78
    m.diffuse_color=(*srgb(h),1);return m
def apply_palette(obs,variant='catchline',pack='food'):
    for ob in obs:
        if ob.type!='MESH':continue
        for slot in ob.material_slots:
            old=slot.material
            if old is None:continue
            m=old.copy();slot.material=m
            if pack=='furniture':
                key=old.name.split('.')[0]
                if key in FM:
                    bs=m.node_tree.nodes.get('Principled BSDF')
                    bs.inputs['Base Color'].default_value=(*srgb(FM[key]['hex']),1)
                    bs.inputs['Roughness'].default_value=.8
                    m.diffuse_color=(*srgb(FM[key]['hex']),1)
            else:
                for n in m.node_tree.nodes:
                    if n.type=='TEX_IMAGE' and n.image:
                        path=O/f'food-colormap-{variant}.png' if pack=='food' else O.parent/'kaykit'/('furniturebits_texture-catchline.png' if pack=='kaykit-furniture' else 'restaurantbits_texture-catchline.png')
                        n.image=bpy.data.images.load(str(path),check_existing=True);assert n.image.size[0]>0;n.image.pack()
def subset_derivatives():
    reset();obs=load(source('food','sushi-salmon'))
    for ob in obs:
        if ob.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
        # Original exporter places the rice in vertices0..47; retain the complete salmon topping.
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index<48],context='VERTS');bm.to_mesh(ob.data);bm.free()
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs: ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(O/'derived/salmon-fillet.glb'),export_format='GLB',use_selection=True)
    reset();obs=load(source('food','fries'))
    for ob in list(obs):
        if ob.type=='MESH' and ob.name=='fries':bpy.data.objects.remove(ob,do_unlink=True);obs.remove(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(O/'derived/fries-loose.glb'),export_format='GLB',use_selection=True)
    (O/'derived/README.md').write_text('Geometry subsets only. salmon-fillet: original sushi-salmon vertices >=48, rice removed; original UVs and topping faces unchanged. fries-loose: original fries.001 mesh only; carton mesh fries removed. Sources remain untouched. GLB stores Y-up, Blender import restores Z-up. Recipes rotate/scale these immutable subsets. This is salmon-coloured fillet art, not a separately modelled breaded cod fillet.\n')
def component(model,dim,at=(0,0,.015),rot=(0,0,0),pack='food',variant='catchline',role=''):
    return dict(model=model,target_size_m=list(dim),offset_bottom_center_blender_m=list(at),rotation_blender_deg=list(rot),pack=pack,palette=variant,role=role)
plate=lambda size=.29:component('plate',(size,size,.023),(0,0,0),role='cream plate')
lemon=lambda at=(.085,.04,.025):component('lemon-half',(.055,.055,.032),at,role='lemon garnish')
fillet=lambda at=(0,0,.028):component('salmon-fillet',(.095,.18,.036),at,pack='derived',role='salmon topping subset; rice removed')
fish=lambda at=(0,0,.028):component('fish',(.23,.11,.048),at,(0,90,-90),variant='roast',role='whole fish on its side; browned palette')
fries=lambda at=(.075,0,.025):component('fries-loose',(.105,.17,.045),at,(90,0,18),pack='derived',role='loose fries, carton removed')
RECIPES=[
 ('GrilledFish','Grilled fish',[plate(.31),fish(),lemon()], 'Pack whole-fish geometry; roasted palette, not a new grill-mark texture.'),
 ('PanFish','Fillets',[plate(),fillet((-.035,-.005,.024)),component('salmon-fillet',(.075,.14,.031),(.045,.025,.029),(0,0,18),pack='derived'),lemon((.08,-.075,.024))], 'PanFish is the enum for the displayed Fillets dish, not an extra menu item. Salmon topping subset retains its pale bands.'),
 ('FishAndChips','Fish & chips',[plate(.32),component('salmon-fillet',(.105,.19,.045),(-.055,0,.025),(0,0,-15),pack='derived'),fries((.07,.015,.026)),lemon((.085,-.09,.025))], 'Fillet is salmon-coloured, not breaded cod. Best pack-only silhouette; dedicated battered fillet remains an art gap.'),
 ('Soup','Fish soup',[component('bowl-soup',(.24,.24,.10),(0,0,0)),component('bread',(.09,.065,.012),(.15,0,.005))], 'Vegetable soup mesh is a visual stand-in for fish broth; no visible fish chunks in the pack bowl.'),
 ('Platter','Oven platter',[component('plate-rectangle',(.38,.29,.035),(0,0,0)),fish((-.055,.015,.03)),component('mussel-open',(.065,.09,.045),(.09,.065,.033),(0,0,15)),component('mussel-open',(.06,.085,.045),(.085,-.04,.033),(0,0,-20)),lemon((.11,-.09,.035))], 'Fish + two mussels + lemon; best pack seafood combo, not a bespoke oven bake.'),
 ('Crab','Crab',[plate(.32),component('CrabBody',(.23,.22,.070),(0,0,.026),pack='catchline',role='existing Catchline fallback: no crab exists in either pack'),lemon((.105,.065,.028))], 'Explicit non-pack fallback: read-only Art/Models/Props/Crab.blend, CrabBody only. Preview ground excluded. Body/legs shell tint cooked orange; eye rubber retained. If pack-only is required, this dish is blocked.'),
 ('Calamari','Calamari',[plate(.30)]+[component('food_ingredient_onion_rings',(.09,.072,.017),at,(0,0,a),pack='kaykit',variant='golden',role='onion ring geometry reused as battered squid rings') for at,a in [((-.04,-.04,.026),10),((.045,-.02,.031),-20),((-.015,.045,.036),40)]]+[lemon((.09,.07,.026))], 'Ring geometry is reused from KayKit onion rings, material is golden batter. No native squid/calamari mesh in packs.'),
 ('Coffee','Coffee',[component('cup-saucer',(.17,.17,.014),(0,0,0)),component('cup-coffee',(.105,.13,.065),(0,0,.011))], 'Ready-made coffee in cup, cream saucer.'),
 ('Tea','Tea',[component('cup-saucer',(.17,.17,.014),(0,0,0)),component('cup-tea',(.11,.13,.09),(0,0,.012))], 'Ready-made tea/tag in mug, cream saucer.'),
 ('Lemonade','Lemonade',[component('soda-glass',(.09,.09,.17),(0,0,0),variant='lemonade'),lemon((.047,0,.11))], 'Dedicated purple-to-lemon palette gives pale golden lemonade, original glass and straw retained.'),
 ('Beer','Beer',[component('mug',(.13,.11,.12),(0,0,0)),component('beer-liquid',(.075,.075,.004),(0,0,.095),pack='primitive',variant='beer'),component('beer-foam',(.075,.075,.003),(0,0,.099),pack='primitive',variant='foam')], 'Kenney wooden tankard is empty: two declared 8-sided liquid/foam caps, no new complex model.'),
 ('Fries','Fries',[plate(.26),fries((0,0,.024))], 'Loose original fries mesh, rotated onto plate instead of fast-food carton.'),
 ('Bread','Bread',[plate(.26),component('loaf-baguette',(.21,.065,.065),(0,0,.024),(0,0,-15)),component('bread',(.09,.065,.012),(.04,-.065,.025),(0,0,-20))], 'Baguette and cut slice, natural bread palette.')]
def path_for(c):
    p=c['pack'];n=c['model']
    return (O/'derived'/(n+'.glb')) if p=='derived' else (K/(n+'.fbx')) if p=='kaykit' else R/'Art/Models/Props/Crab.blend' if p=='catchline' else source(p,n)
def instantiate(c,label):
    if c['pack']=='primitive':
        bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=1,depth=1)
        obs=[bpy.context.object];obs[0].data.materials.append(material(c['model'],'#F4EFE3' if c['palette']=='foam' else '#C48B32'))
        c['source']='declared 8-sided cylinder: liquid cap' 
    elif c['pack']=='catchline':
        p=path_for(c)
        with bpy.data.libraries.load(str(p),link=False) as (a,b):b.objects=['CrabBody']
        obs=[x for x in b.objects if x]
        for x in obs:bpy.context.scene.collection.objects.link(x)
        # Preserve black eyes; orange shell is a proof-only material copy.
        for x in obs:
            for slot in x.material_slots:
                slot.material=material('Cooked crab shell' if 'Rubber' not in slot.material.name else 'Crab eyes','#D86635' if 'Rubber' not in slot.material.name else '#28343B')
        c['source']=str(p.relative_to(R)).replace('\\','/')
    else:
        p=path_for(c);obs=load(p);c['source']=str(p.relative_to(R)).replace('\\','/')
        if c['palette']=='golden':
            m=material('Golden batter','#D6A34F')
            for x in obs:
                if x.type=='MESH':x.data.materials.clear();x.data.materials.append(m)
        else:apply_palette(obs,c['palette'],'food' if c['pack']=='derived' else c['pack'])
    group=bpy.data.objects.new(label,None);bpy.context.scene.collection.objects.link(group)
    for x in obs:
        if x.parent not in obs:x.parent=group
    # Rotate source first, compute exact evaluated AABB; scale to stated display dimensions.
    group.rotation_euler=[math.radians(v) for v in c['rotation_blender_deg']]
    lo,hi=bounds(obs);extent=hi-lo;scale=Vector([c['target_size_m'][i]/extent[i] if extent[i]>1e-7 else 1 for i in range(3)])
    # A separate parent implements scale in rotated frame. Baked output matrices remove importer ambiguity.
    root=bpy.data.objects.new(label+' sized',None);bpy.context.scene.collection.objects.link(root);group.parent=root;root.scale=scale
    lo,hi=bounds(obs);center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));root.location=Vector(c['offset_bottom_center_blender_m'])-center
    bpy.context.view_layer.update()
    c['scale_after_source_rotation_blender_xyz']=list(scale)
    c['offset_unity_m']=[c['offset_bottom_center_blender_m'][0],c['offset_bottom_center_blender_m'][2],-c['offset_bottom_center_blender_m'][1]]
    c['scale_unity_xyz']=[scale.x,scale.z,scale.y]
    c['source_to_dish_mesh_matrices_blender']={x.name:[list(row) for row in x.matrix_world] for x in obs if x.type=='MESH'}
    lo,hi=bounds(obs);c['verified_bounds_blender_m']={'min':list(lo),'max':list(hi)}
    return [root,group]+obs
def scene_setup(target=(0,0,.70),span=1.55,width=720,height=540):
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
    s.render.resolution_x=width;s.render.resolution_y=height;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.view_settings.view_transform='Standard'
    s.world=bpy.data.worlds.new('Soft harbour ambient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.61,.72,.79,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.008));bpy.context.object.data.materials.append(material('Cream studio quay','#E4DDCE'))
    bpy.ops.object.light_add(type='AREA',location=(-2,-3,6));bpy.context.object.data.energy=550;bpy.context.object.data.size=4
    bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='PERSP';cam.data.lens=58;cam.data.sensor_width=36
    dist=span/(2*math.tan(math.atan(36/(2*58))));pitch=math.radians(38);yaw=math.radians(2)
    direction=Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)))
    cam.location=Vector(target)+direction*dist;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
    return s
def table():
    c=component('table_round_A',(.95,.95,.76),(0,0,0),pack='kaykit',role='same accepted Catchline atlas; .95m diameter/.76m high reference table')
    objs=instantiate(c,'KayKit round table')
    return c,objs
def export_selected(obs,path):
    bpy.ops.object.select_all(action='DESELECT')
    for x in obs:
        if x.name in bpy.data.objects:x.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True)
def dishes(only=None):
    if not only:subset_derivatives()
    records=json.loads((O/'dish-map.json').read_text())['dishes'] if only else []
    for key,label,parts,note in RECIPES:
        if only and key not in only:continue
        reset();foodobs=[]
        for i,c in enumerate(parts):foodobs+=instantiate(c,f'{key} {i} {c["model"]}')
        # Composite output is table-local, pivot0 at tabletop. It contains only this meal.
        export_selected(foodobs,O/'derived'/f'dish-{key}.glb')
        for ob in foodobs:
            if ob.parent is None:ob.location.z+=.762
        tc,_=table();s=scene_setup();s.render.filepath=str(O/'renders'/f'dish-{key}.png');bpy.ops.render.render(write_still=True)
        # Companion detail still sits on the same table, with the same pitch/lens.
        cam=s.camera;target=Vector((0,0,.80));v=cam.location-Vector((0,0,.70));cam.location=target+v*(.58/1.55)
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        s.render.filepath=str(O/'renders'/f'detail-{key}.png');bpy.ops.render.render(write_still=True)
        s.camera.data.lens=58
        bpy.ops.wm.save_as_mainfile(filepath=str(O/'derived'/f'proof-{key}.blend'))
        records=[v for v in records if v['dish']!=key]
        records.append(dict(dish=key,label=label,components=parts,note=note,composite_glb=f'derived/dish-{key}.glb',render=f'renders/dish-{key}.png'))
        (O/'dish-map.json').write_text(json.dumps(dict(schema=1,units='metres',coordinate_contract='Recipe source transforms use evaluated Blender Z-up imports. Offset is bottom-centre above tabletop; Unity offset is [x,z,-y]. Original FBX import scale may differ: use baked GLB composites or reproduce evaluated AABB normalisation. Do not apply Blender scale directly to raw FBX transforms.',camera=dict(pitch_deg=38,yaw_offset_deg=2,lens_mm=58,reference='RestaurantWorld.cs Euler(38,178,0); contact is a close-up, not the whole room camera position'),table=tc,dishes=records),indent=2))
    print('DISHES_DONE',len(records))
DECOR=[
 ('pottedPlant',(.36,.40,1.05),'floor beside reception, outside circulation','Natural upright foliage; harbour-bistro corner'),
 ('plantSmall3',(.13,.12,.20),'sill or shelf, not every dining table','Small muted plant, avoids table clutter'),
 ('lampWall',(.38,.22,.16),'rear wall above booth, wall mounted','Warm wall wash, light steel body'),
 ('lampRoundFloor',(.30,.34,1.65),'reading corner behind bench','Warm cream shade; keep out of service aisle'),
 ('lampRoundTable',(.18,.20,.37),'reception counter or sideboard','Small welcome pool; preserve order-marker clearances'),
 ('bookcaseOpenLow',(1.15,.40,.95),'rear dining wall, away from kitchen','Warm timber sideboard for crockery'),
 ('bookcaseOpen',(.85,.35,1.80),'rear wall, stage2+','Tall shelf rhythm, do not block door/window'),
 ('bench',(1.40,.48,1.05),'quay waiting spot','Plain timber, good outside seating'),
 ('benchCushion',(1.40,.48,1.05),'interior waiting wall','Teal upholstery instead of bright pink'),
 ('rugRectangle',(1.70,1.00,.012),'host waiting nook only','Teal/navy frame; never kitchen/wet route'),
 ('rugDoormat',(.70,.40,.012),'inside entrance threshold','Warm woven mat, low profile'),
 ('coatRackStanding',(.50,.50,1.65),'entrance wall beside host','Useful bistro silhouette, keep queue clear'),
 ('kaykit:pictureframe_medium',(.65,.10,.45),'rear wall beside shelf','KayKit frame; complements Kenney decor. Existing inset art is decorative, not a navigation chart.')]
def decor():
    records=[]
    for name,dim,spot,why in DECOR:
        kk=name.startswith('kaykit:');name=name.split(':')[-1]
        src=R/'Art/Downloads/kaykit/furniture/addons/kaykit_furniture_bits/Assets/fbx(unity)'/(name+'.fbx') if kk else source('furniture',name)
        for variant in ['original','catchline']:
            reset();obs=load(src);lo,hi=bounds(obs);original_size=list(hi-lo)
            g=bpy.data.objects.new('display sizing',None);bpy.context.scene.collection.objects.link(g)
            for x in obs:
                if x.parent not in obs:x.parent=g
            g.scale=Vector([dim[i]/(hi[i]-lo[i]) for i in range(3)]);lo,hi=bounds(obs);g.location=-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
            if variant=='catchline':apply_palette(obs,pack='kaykit-furniture' if kk else 'furniture');export_selected([g]+obs,O/'derived'/f'decor-{name}.glb')
            # Entire height fits. Square frames prevent the earlier candidate top crop.
            s=scene_setup(target=(0,0,dim[2]*.50),span=max(dim[0]*1.65,dim[1]*1.8,dim[2]*1.9,.6),width=600,height=600)
            s.render.filepath=str(O/'renders'/f'decor-{name}-{variant}.png');bpy.ops.render.render(write_still=True)
        records.append(dict(model=name,source=str(src.relative_to(R)).replace('\\','/'),fbx_source=str((src if kk else R/'Art/Downloads/kenney/furniture/Models/FBX format'/(name+'.fbx')).relative_to(R)).replace('\\','/'),display_size_m=list(dim),source_size_blender_m=original_size,scale_blender_xyz=list(g.scale),placement=spot,reason=why,materials='../kaykit/furniturebits_texture-catchline.png' if kk else 'furniture-materials-catchline.json',variant_glb=f'derived/decor-{name}.glb'))
        (O/'decor-map.json').write_text(json.dumps(dict(schema=1,coordinate_contract='Sizes are Blender XYZ (width,depth,height); Unity size = [width,height,depth]. Bottom-centre display origin. GLBs bake display dimensions; verify imported Unity scale once.',decor=records,missing='No Kenney picture-frame asset. Selected KayKit pictureframe_medium instead. No new wall art was painted.'),indent=2))
    print('DECOR_DONE',len(records))
if __name__=='__main__':
    mode=sys.argv[-1]
    if mode=='decor':decor()
    elif mode.startswith('only='):dishes(mode[5:].split(','))
    else:dishes()

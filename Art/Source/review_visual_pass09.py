"""Blender: measured ART-009 compatibility and source-only scale presentation."""
import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Art/Models/VisualPass09'
old = json.loads((OUT / 'baseline-contract.json').read_text())
new = json.loads((ROOT / 'Art/Models/DayBoatKit/build-metrics.json').read_text())
before = {a['asset']: a for a in old['assets']}
after = {a['asset']: a for a in new['assets']}
budgets = dict(DayBoat=9000, Crane=2000, PowerHauler=2000, IceMachine=2200,
               SortingChute=2000, GuttingTable=1800)
checks = []
palette = set(old['palette_srgb'])
for name, previous in before.items():
    current = after[name]
    original_parts = {p['name']: p for p in previous['parts']}
    current_parts = {p['name']: p for p in current['parts']}
    assert original_parts.keys() <= current_parts.keys(), name
    for part, pivot in previous['pivots_blender'].items():
        assert current['pivots_blender'][part] == pivot, (name, part)
    assert all(set(p['materials']) <= palette for p in current['parts']), name
    if name == 'DayBoat':
        assert all(current_parts[p]['mesh_sha256'] == v['mesh_sha256']
                   for p, v in original_parts.items()), 'Boat original geometry changed'
    if name not in budgets:
        assert previous == current, 'Untargeted asset changed: ' + name
    else:
        assert current['triangles'] <= budgets[name], name
    checks.append(dict(asset=name, original_names_and_pivots_preserved=True,
                       triangles=current['triangles'],
                       added_parts=sorted(current_parts.keys() - original_parts.keys()),
                       unchanged_geometry=(name not in budgets or name == 'DayBoat')))
validation = json.loads((ROOT / 'Art/Models/DayBoatKit/validation.json').read_text())
assert validation['all_passed'] and validation['asset_count'] == 10
(OUT / 'compatibility.json').write_text(json.dumps(dict(all_passed=True,
    source_and_actual_fbx_validation='DayBoatKit/validation.json',
    existing_boat_geometry_identical=True, new_material_names=[], assets=checks), indent=2)+'\n')

# Append existing source objects without rescaling. This scene is review-only.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
placements = dict(DayBoat=(0,0,0), Crane=(-2,3.5,0), PowerHauler=(-2,1.5,0),
                  IceMachine=(2,-1.5,0), SortingChute=(-.5,-.5,0),
                  GuttingTable=(1.5,1.5,0))
world = json.loads((ROOT / 'Art/Models/WorldPolish/build-metrics.json').read_text())
assets = after | {a['asset']:a for a in world['assets']}
placements.update(NPC_Fishmonger=(-.5,.5,0), NPC_HarbourMaster=(1.5,2.5,0))
meshes = []
for name, location in placements.items():
    asset = assets[name]
    names = {'Catchline_'+name} | set(asset['pivots_blender'])
    with bpy.data.libraries.load(str(ROOT / asset['source']), link=False) as (src,dst):
        dst.objects = [n for n in src.objects if n in names]
    for ob in dst.objects:
        scene.collection.objects.link(ob)
        if ob.type == 'MESH': meshes.append(ob)
    root = next(ob for ob in dst.objects if ob.name.startswith('Catchline_'+name))
    root.location = location
bpy.context.view_layer.update()

# Reuse approved lighting and color management from the asset preview builder.
import importlib.util
spec = importlib.util.spec_from_file_location('world09', Path(__file__).with_name('build_world_polish.py'))
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)
W.B.MATERIALS.update({k: W.B.material(k,v) for k,v in W.B.PALETTE.items()})
W.B.preview_stage(scene, meshes)
scene.cycles.samples = 32
ground = bpy.data.objects['Preview_Ground']
ground.location.z = -1.12
for light in bpy.data.collections['PREVIEW_ONLY_NOT_EXPORTED'].objects:
    if light.type == 'LIGHT':
        light.location *= 12
        light.data.energy *= 144
        light.data.size *= 12
camera = scene.camera
target = Vector((0,-.25,.25))
camera.location = target + Vector((.406,.579,.707))*36
camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update()
projected = [camera.matrix_world.inverted() @ (o.matrix_world @ Vector(p))
             for o in meshes for p in o.bound_box]
width = max(p.x for p in projected)-min(p.x for p in projected)
height = max(p.y for p in projected)-min(p.y for p in projected)
for label,x,y in [('Desktop',1440,900),('Phone',844,390)]:
    scene.render.resolution_x=x; scene.render.resolution_y=y
    scene.render.resolution_percentage=100
    camera.data.ortho_scale=max(width,height*x/y)*1.14
    scene.render.filepath=str(OUT / (label+'-scale-review.png'))
    if label == 'Desktop':
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scale-review.blend'))
    bpy.ops.render.render(write_still=True)
(OUT/'scale-layout.json').write_text(json.dumps(dict(units='metres',
    models_rescaled=False, preview_only=True, locations_blender=placements),indent=2)+'\n')
print('ART-009 compatibility and scale review passed')

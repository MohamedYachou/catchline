"""TIER033: export the exact approved BOAT032 layout as a game-ready static boat.
Run with Blender --background --python Art/Source/export_tier4_033.py.
The original comparison files are never overwritten.
"""
import bpy, json
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/Tier4Production033'; OUT.mkdir(parents=True,exist_ok=True)
GAME=ROOT/'Assets/Art/Models/Boats'; CX=-3.85
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/Models/Tier4Blockout032/tier4-buckets.blend'))
tier=next(c for c in bpy.data.collections if c.name.startswith('Tier 4'))
keep=list(tier.objects)
for o in list(bpy.data.objects):
    if o not in keep or o.name.startswith(('T4 captain','T4 port fisher','T4 starboard fisher','T4 prep hand')):
        bpy.data.objects.remove(o,do_unlink=True)
for o in list(tier.objects):
    o.location.x-=CX
    if o.name.startswith('T4 '):o.name=o.name[3:]

# Each storage type is a single switchable subtree. The prepared boxes always remain.
def group(name):
    o=bpy.data.objects.new(name,None);tier.objects.link(o);return o
raw=group('RawBuckets'); iced=group('RawIceCoolers'); prepared=group('PreparedHold'); table=group('PrepStation')
for o in list(tier.objects):
    if o.type!='MESH':continue
    if o.name.startswith(('RAW bucket','Raw fish in bucket','Bucket handle')):o.parent=raw
    elif o.name.startswith(('PREPARED freezer','Insulated lid','Recessed lid handle','Storage front latch')):o.parent=prepared
    elif o.name.startswith(('Prep ','Cutting board','Fish on cutting board','Knife ','Worker standing mat','Chum pail')):o.parent=table

# Append just the two upgraded front containers from the separately approved scene.
with bpy.data.libraries.load(str(ROOT/'Art/Models/Tier4Blockout032/tier4-ice-coolers.blend'),link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n.startswith(('RAW ice cooler','Ice marker','Insulated lid','Recessed lid handle','Storage front latch'))]
for o in dst.objects:
    if o is None:continue
    # Front cooler components have y=.14; rear lids/latches are y~2.04.
    if o.location.y>.5:
        bpy.data.objects.remove(o,do_unlink=True);continue
    tier.objects.link(o);o.location.x-=CX;o.parent=iced

# Canonical game palette names ensure URP remapping matches the approved colours.
colors={'032 Navy':'M_HullNavy','032 Ivory':'M_RailIvory','032 Wood':'M_DeckWood','032 Rubber':'M_Rubber',
 '032 Teal':'M_SeaTeal','032 Steel':'M_Steel','032 Orange':'M_SafetyOrange','032 Fish':'M_FishSilver','032 Ice':'M_SeaTeal'}
for o in tier.objects:
    if o.type!='MESH':continue
    for slot in o.material_slots:
        if slot.material and slot.material.name.split('.')[0] in colors:
            name=colors[slot.material.name.split('.')[0]]
            slot.material=bpy.data.materials.get(name) or slot.material
            slot.material.name=name
    # Rotating parts must turn around themselves, never around the boat origin.
    if o.name in ('NetDrum','NetCrank','Propeller') or o.name.startswith('RodSocket_'):
        pivot=sum((Vector(v) for v in o.bound_box),Vector())/8
        if o.name.startswith('RodSocket_'): pivot.z=min(v[2] for v in o.bound_box)
        o.data.transform(Matrix.Translation(-pivot));o.location+=pivot

# Source points are Z-up; runtime importer applies the same transform as tier3.
anchors={
 'PrepWorker_1':(-.36,1.40,0),'PrepWorker_2':(.36,1.40,0),
 'RawInput_1':(-.36,.14,.24),'RawInput_2':(.36,.14,.24),
 'PreparedOutput_1':(-.36,2.04,.24),'PreparedOutput_2':(.36,2.04,.24),
}
for name,position in anchors.items():
    o=group(name);o.location=position
iced.hide_render=True;iced.hide_viewport=True
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.object.select_all(action='DESELECT')
for o in tier.objects:
    o.hide_set(False);o.hide_viewport=False;o.select_set(True)
# FBX must include both variants; runtime chooses the active subtree before routing.
iced.hide_render=False
bpy.context.view_layer.update()
hull=bpy.data.objects['Hull']; bounds=[hull.matrix_world@Vector(v) for v in hull.bound_box]
size=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)]
assert abs(size[0]-3.5)<.002 and abs(size[1]-6.8)<.002,size
assert len([o for o in raw.children if o.name.startswith('RAW bucket')])==2
assert len([o for o in iced.children if o.name.startswith('RAW ice cooler')])==2
assert not any(o.name.startswith(('T3 ','T4 prep hand','Studio')) for o in tier.objects)
bpy.ops.export_scene.fbx(filepath=str(GAME/'PrepFisherV1.fbx'),use_selection=True,object_types={'EMPTY','MESH'},
 axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,
 apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False)
iced.hide_render=True;iced.hide_viewport=True
for child in iced.children:
    child.hide_set(True);child.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'PrepFisherV1.blend'))
manifest={'asset':'PrepFisherV1','approved_reference':'BOAT032 6.8 x 3.5 m','hull_dimensions_source':size,
 'source_axes':'X athwartships, -Y bow, Z up','anchors_source':anchors,'front_variants':['RawBuckets','RawIceCoolers'],
 'prepared_storage':'PreparedHold (always present)','crew_meshes_exported':False,
 'gameplay_status':'Hull/routes/trial integration; processing/chum work orders separate next step'}
(GAME/'PrepFisherV1.placements.json').write_text(json.dumps(manifest,indent=2))
print('TIER033 EXPORT VERIFIED',json.dumps(manifest))

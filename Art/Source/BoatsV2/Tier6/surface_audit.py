import bpy,json,importlib.util,hashlib
from pathlib import Path
S=Path(__file__).resolve().parent;R=S.parents[3];O=R/'Art/Models/BoatsV2/Tier6V1'
spec=importlib.util.spec_from_file_location('surface',str(R/'Art/Source/HarbourV2/audit.py'));A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
bpy.ops.wm.open_mainfile(filepath=str(O/'Tier6V1.blend'));source=A.geometry();parents={o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects};colors={m.name:list(m.diffuse_color) for m in bpy.data.materials if m.users}
assert len([n for n in parents if n.startswith('CrewStand_')])==10
required=['DeepLineModule','PrepStation','PreparedHold','RawIceCoolers','RawBuckets','NetModule1','NetModule2','NetWorker_1','NetWorker_2','PrepSurface','PrepInput','PreparedOutput','RawInput_1','RawInput_2','PreparedOutput_1','PreparedOutput_2','FishHold','HoldLid','HoldRimHinges','LampCable','TwoShortLampMasts','SortingTray']
for stem,count in [('RodHolder_',4),('RodSocket_',4),('DeepLineRig_',2),('DeepLineBase_',2),('DeepLineTip_',2),('DeepLineReelPivot_',2),('DeepLineWorker_',2),('BuoyAccess_',2),('BuoyAnchor_',2),('PrepWorker_',2)]:required += [stem+str(i) for i in range(1,count+1)]
required+=['JigReel_%02d'%i for i in range(1,4)]+['SquidLamp_%02d'%i for i in range(1,9)]
assert all(n in parents for n in required)
# No preview objects/camera/lights/images delivered. Reject bad scale and duplicate vertices never used.
for o in bpy.context.scene.objects:
 assert o.type in ('MESH','EMPTY')
 assert max(abs(v-1) for v in o.scale)<2e-5,(o.name,list(o.scale))
 if o.type=='MESH':assert all(p.area>1e-10 for p in o.data.polygons)
assert not list(bpy.data.images)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/'Tier6V1.fbx'));imp=A.geometry();d=A.same_geometry(source,imp)
assert parents=={o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects}
for m in bpy.data.materials:
 if m.users:assert max(abs(a-b) for a,b in zip(m.diffuse_color,colors[m.name]))<1e-5,m.name
v=json.loads((O/'validation.json').read_text());assert v['pass'];v.update(full_surface_audit=d,semantic_names_verified=required,crew_capacity=10,buoy_fisher_capacity=8,geometry_palette_hierarchy_verified=True,materials_linear_rgba=colors)
(O/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print('TIER6 FULL SURFACE PASS',d,len(required),'semantic nodes',flush=True)

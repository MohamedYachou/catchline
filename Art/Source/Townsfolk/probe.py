import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
def snap():
 a=next(o for o in bpy.data.objects if o.type=='ARMATURE')
 return {'arm':a.name,'parent':a.parent.name if a.parent else None,'matrix':[list(v) for v in a.matrix_world],'bones':{b.name:{'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(v) for v in b.matrix_local]} for b in a.data.bones},'actions':[(a.name,list(a.frame_range),[(s.identifier,s.target_id_type) for s in a.slots]) for a in bpy.data.actions],'meshes':[(o.name,len(o.data.vertices),[m.name for m in o.data.materials]) for o in bpy.data.objects if o.type=='MESH']}
bpy.ops.wm.open_mainfile(filepath=str(R/'Art/Models/CrewRig/CrewRig.blend'));s=snap();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(R/'Assets/Art/Models/Crew/CrewRig.fbx'));i=snap();(R/'Art/Models/Townsfolk/metrics/reference.json').write_text(json.dumps({'source':s,'fbx':i},indent=2));print('TOWN PROBE PASS')

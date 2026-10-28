"""Read-only captain scale/hand-grip review; no source puppet/animation changes."""
import bpy,math,hashlib
from mathutils import Vector,Matrix
from pathlib import Path

def carry_review(at,rack,rec):
 import build_props3 as p
 path=p.R/'Assets/Art/Models/Crew/Quaternius/mira.fbx'
 obs=p.b.load_fbx(path);rig=next(o for o in obs if o.type=='ARMATURE');bpy.context.view_layer.update()
 # Match runtime FitHeight, including hair/eyes. All changes remain only in review memory.
 deps=bpy.context.evaluated_depsgraph_get();vs=[]
 for o in obs:
  if o.type=='MESH':
   ev=o.evaluated_get(deps);me=ev.to_mesh();vs.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 lo=min(v.z for v in vs);height=max(v.z for v in vs)-lo;factor=1.14/height
 anchor=bpy.data.objects.new('REVIEW_CurrentCaptain_Mira',None);bpy.context.scene.collection.objects.link(anchor)
 for o in obs:
  if o.parent is None:o.parent=anchor
 anchor.location=at-Vector((0,0,lo*factor));anchor.scale=(factor,)*3;anchor.rotation_euler.z=math.pi;bpy.context.view_layer.update()
 # Two bone IK reaches the rack's upper hand grip; leave original files unchanged.
 for side,sign in [('l',1),('r',-1)]:
  target=bpy.data.objects.new('REVIEW_CarryGrip_'+side,None);bpy.context.scene.collection.objects.link(target)
  target.location=rack.location+Vector((sign*.075,.075,.307))
  arm=rig.pose.bones['lowerarm_'+side];ik=arm.constraints.new('IK');ik.target=target;ik.chain_count=2;ik.iterations=100
  # No pole target: the authored elbow plane is stable with the hand in front of the body.
 bpy.context.view_layer.update()
 print('REVIEW_FINGERS',[b.name for b in rig.data.bones if any(t in b.name.lower() for t in ['index','middle','thumb','pinky','ring'])],flush=True)
 for side,sign in [('l',1),('r',-1)]:
  hand=rig.pose.bones['hand_'+side];wrist=rig.matrix_world@hand.head
  aim=Vector((-sign,0,0)).to_track_quat('Y','Z');rot=rig.matrix_world.to_quaternion().inverted()@aim
  hand.matrix=Matrix.LocRotScale(rig.matrix_world.inverted()@wrist,rot,Vector((1,1,1)))
 bpy.context.view_layer.update()
 rec['captain_review']={'file':str(path.relative_to(p.R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_height_m':height,'uniform_scale':factor,'game_height_m':1.14,'pose':'Evidence-only forearm IK to rack upper grip; not an exported/native clip'}
 print('CAPTAIN_REVIEW',rec['captain_review'],flush=True)

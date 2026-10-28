import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import build_props3 as p
bpy.ops.wm.read_factory_settings(use_empty=True)
obs=p.b.load_fbx(p.R/'Assets/Art/Models/Crew/Quaternius/mira.fbx');bpy.context.view_layer.update()
print('OBS',[(o.name,o.type,list(o.dimensions)) for o in obs],flush=True)
for o in obs:
 if o.type=='ARMATURE':
  print('BONES',[(b.name,list(b.head_local),list(b.tail_local)) for b in o.data.bones if any(t in b.name.lower() for t in ['arm','hand','spine','head','hips'])],flush=True)
 if o.type=='MESH':print('MAT',o.name,[(m.name,tuple(m.diffuse_color),[(n.name,n.image.filepath if n.image else None) for n in m.node_tree.nodes if n.type=='TEX_IMAGE']) for m in o.data.materials],flush=True)
print('ACTIONS',[(a.name,a.frame_range[:]) for a in bpy.data.actions],flush=True)
print('IMAGES',[(i.name,i.filepath,i.packed_file is not None,list(i.size)) for i in bpy.data.images],flush=True)

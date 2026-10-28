import bpy,sys
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'blends/props3-Restaurant_TipCoins_S.blend'))
o=bpy.data.objects['Restaurant_TipCoins_S'];m=o.data.materials[0]
for im in bpy.data.images:print('IMAGE',im.name,im.colorspace_settings.name)
print('COLRANGE',[(min(d.color[i] for d in o.data.color_attributes['Color'].data),max(d.color[i] for d in o.data.color_attributes['Color'].data)) for i in range(3)])
for p in o.data.polygons:
 if p.center.z>.053 and p.normal.z>.95:
  li=p.loop_indices[0];print('TOP',tuple(p.center),tuple(o.data.uv_layers.active.data[li].uv),tuple(o.data.color_attributes['Color'].data[li].color))
for n in m.node_tree.nodes:
 print('NODE',n.name,n.type)
for l in m.node_tree.links:print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

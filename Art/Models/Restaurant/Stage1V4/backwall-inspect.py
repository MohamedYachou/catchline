import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'Stage1V4.blend'))
m=bpy.data.objects['RearCoping'].data.materials[0]
print('INSPECT',m.name)
for n in m.node_tree.nodes:
 print(n.name,n.type,[(i.name,i.default_value[: ] if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value')],n.image.filepath if n.type=='TEX_IMAGE' else '')
for l in m.node_tree.links:print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for name in ['RearMasonry_0_0','RearCoping','HighKitchenShelf']:
 o=bpy.data.objects[name];m=o.data.materials[0];print('UV',name,[(u.name,u.active_render) for u in o.data.uv_layers],[(n.name,n.uv_map) for n in m.node_tree.nodes if n.type=='UVMAP'],[(a.name,a.domain) for a in o.data.color_attributes],[(n.name,n.layer_name) for n in m.node_tree.nodes if n.type=='VERTEX_COLOR'])

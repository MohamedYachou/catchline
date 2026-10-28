import bpy
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p/'blends/props3-Restaurant_TipCoins_S.blend'))
print([(o.name,len(o.data.vertices),len(o.data.uv_layers)) for o in bpy.context.scene.objects if o.type=='MESH']);o=bpy.data.objects['Restaurant_TipCoins_S'];im=bpy.data.images.get('Restaurant_BaseColor.png')
print('ATTRS',[(a.name,a.domain,a.data_type) for a in o.data.attributes]);print('COLORS',[(a.name,a.domain,a.data_type) for a in o.data.color_attributes])
for a in o.data.color_attributes:
 print(a.name,[tuple(d.color) for d in list(a.data)[:3]])
for col,row in [(1,1),(3,2)]:
 px=int((col+.5)/8*im.size[0]);py=int((1-(row+.5)/4)*im.size[1]);i=(py*im.size[0]+px)*4;print('PIXEL',col,row,list(im.pixels[i:i+4]))

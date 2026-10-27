import bpy,sys
from pathlib import Path
from mathutils import Vector
import json,math
R=Path.cwd();sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import load,reset
reset();p=next((R/'Art/Downloads/kaykit/restaurant').rglob('fbx(unity)'))/'chair_A.fbx';obs=load(p);v=[o.matrix_world@x.co for o in obs if o.type=='MESH' for x in o.data.vertices];lo=min(x.z for x in v);hi=max(x.z for x in v);top=[x for x in v if x.z>lo+(hi-lo)*.8];assert sum(x.y for x in top)/len(top)>0;print('CHAIR BACK +Y, source',p,'back_mean_y',sum(x.y for x in top)/len(top),'allY',min(x.y for x in v),max(x.y for x in v))
O=Path(__file__).resolve().parent;d=json.loads((O/'manifest.json').read_text());rows=[]
for item in d['items']:
 for c in item['components']:
  if c['model']!='chair_A':continue
  a=math.radians(c['rotation_z_deg']+180);back=(-math.sin(a),math.cos(a));pos=[-x for x in c['bottom_centre_blender'][:2]];dot=sum(a*b for a,b in zip(back,pos));assert dot>.2,(item['name'],c,dot)
  rows.append(dict(item=item['name'],chair_centre_final=pos,back_direction_final=back,outward_dot=dot))
(O/'seat-direction-audit.json').write_text(json.dumps(dict(pass_all=True,chairs=len(rows),source_back_mean_y=sum(x.y for x in top)/len(top),test='Chair back points away from table centre after baked assembly rotation; source back geometry measured in +Y.',items=rows),indent=2));print('SEATS_PASS',len(rows))

from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;rows=[]
for name in ['night-water','lantern-reflections-additive']:
 p=O/(name+'-2048.png');im=Image.open(p);assert im.size==(2048,2048) and im.mode=='RGB';a=np.array(im).astype(float)
 row={'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':im.size,'mode':im.mode,'opaque':True,'wrap_edge_mean_abs_rgb_0_255':{'x':float(abs(a[:,0]-a[:,-1]).mean()),'y':float(abs(a[0]-a[-1]).mean())},'adjacent_interior_mean_abs_rgb_0_255':{'x':float(abs(a[:,1:]-a[:,:-1]).mean()),'y':float(abs(a[1:]-a[:-1]).mean())},'pure_black_fraction':float(np.mean(np.max(a,axis=2)==0))}
 rows.append(row);tile=im.resize((512,512),Image.Resampling.LANCZOS);sheet=Image.new('RGB',(1024,1024))
 for x,y in [(0,0),(512,0),(0,512),(512,512)]:sheet.paste(tile,(x,y))
 sheet.save(O/(name+'-2x2.jpg'),quality=95)
(O/'texture-audit.json').write_text(json.dumps({'dimension_format_pass':True,'assets':rows,'seam_metrics_are_measurements_not_visual_acceptance':True,'generated_source_pixels':[1254,1254],'delivery_resampling':'Lanczos2048; no painted content generated procedurally'},indent=2))
print(json.dumps(rows,indent=2))

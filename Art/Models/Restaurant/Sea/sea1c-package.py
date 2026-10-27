"""Imagegen-painted water, mechanically resized and made exactly periodic."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent
previous=json.loads((O/'sea1c-texture-audit.json').read_text()) if (O/'sea1c-texture-audit.json').exists() else None
source=O/'sea1c-provenance/candidate-1.png';im=Image.open(source).convert('RGB');rows=[]
for size in (1024,2048):
 raw=np.asarray(im.resize((size,size),Image.Resampling.LANCZOS),dtype=float);a=raw.copy();band=size//32
 for axis in (1,0):
  z=np.moveaxis(a,axis,0);target=(z[0].copy()+z[-1].copy())/2;dl=target-z[0].copy();dr=target-z[-1].copy()
  for j in range(band):
   t=j/(band-1);w=1-3*t*t+2*t*t*t;z[j]+=w*dl;z[-1-j]+=w*dr
 a=np.rint(np.clip(a,0,255)).astype('uint8');a[:,-1]=a[:,0];a[-1]=a[0]
 assert np.array_equal(a[:,0],a[:,-1]) and np.array_equal(a[0],a[-1])
 tile=Image.fromarray(a);p=O/f'sea1-night-water-{size}.png';tile.save(p)
 proof=Image.fromarray(np.tile(a,(4,4,1)));proof.save(O/f'sea1c-tiling-proof-{size}-4x4.png')
 proof.resize((1280,1280),Image.Resampling.LANCZOS).save(O/f'sea1c-tiling-review-{size}.jpg',quality=97)
 proof.crop((size-96,size-96,size+96,size+96)).resize((768,768),Image.Resampling.NEAREST).save(O/f'sea1c-seam-zoom-{size}.png')
 lum=a@np.array([.2126,.7152,.0722]);old=O/'_sea1c-backup'/p.name
 oldstats=next((r['prior_tile'] for r in previous['textures'] if r['size']==size),None) if previous else None
 if old.exists():
  before=np.asarray(Image.open(old));oldstats={'mean_RGB':before.mean((0,1)).tolist(),'mean_luma_sRGB':float((before@np.array([.2126,.7152,.0722])).mean())}
 rows.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':size,'repair_band_px':band,'exact_X_Y':True,'mean_RGB':a.mean((0,1)).tolist(),'mean_luma_sRGB':float(lum.mean()),'dark_pixel_fraction_luma_under_30':float((lum<30).mean()),'prior_tile':oldstats,'interior_unchanged':bool(np.array_equal(a[band:-band,band:-band],raw[band:-band,band:-band].astype('uint8')))})
(O/'sea1c-texture-audit.json').write_text(json.dumps({'pass':True,'source_size':im.size,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Builtin imagegen repaint; Lanczos resize; symmetric opposing-edge mean correction with cubic smoothstep in1/32-width bands; rounded identical boundaries. No creative raster painting in Python.','textures':rows},indent=2))
print('SEA1C PACKAGE PASS')

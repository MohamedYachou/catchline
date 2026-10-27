"""Exact opposing-edge repair of accepted painting; native 4x4 proofs."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
O=Path(__file__).resolve().parent;B=O/'_sea1b-backup';B.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=O/'sea1-provenance/candidate-4.png';im=Image.open(source).convert('RGB');rows=[]
for size in [1024,2048]:
 p=O/f'sea1-night-water-{size}.png'
 if not (B/p.name).exists():shutil.copy2(p,B/p.name)
 raw=np.asarray(im.resize((size,size),Image.Resampling.LANCZOS),dtype=float);a=raw.copy();band=size//32
 # Endpoint constraints with zero-slope smoothstep falloff into unchanged interior.
 for axis in [1,0]:
  z=np.moveaxis(a,axis,0);target=(z[0].copy()+z[-1].copy())/2;dl=target-z[0].copy();dr=target-z[-1].copy()
  for j in range(band):
   t=j/(band-1);w=1-3*t*t+2*t*t*t;z[j]+=w*dl;z[-1-j]+=w*dr
 a=np.rint(np.clip(a,0,255)).astype('uint8');a[:,-1]=a[:,0];a[-1]=a[0]
 assert np.array_equal(a[:,0],a[:,-1]) and np.array_equal(a[0],a[-1])
 assert np.array_equal(a[band:-band,band:-band],raw[band:-band,band:-band].astype('uint8'))
 tile=Image.fromarray(a);tile.save(p)
 proof=Image.new('RGB',(size*4,size*4))
 for x in range(4):
  for y in range(4):proof.paste(tile,(x*size,y*size))
 proof.save(O/f'sea1b-tiling-proof-{size}-4x4.png');proof.resize((1280,1280),Image.Resampling.LANCZOS).save(O/f'sea1b-tiling-review-{size}.jpg',quality=97)
 # Native seam intersection at repeat boundary, 4x nearest zoom (no filtering).
 crop=proof.crop((size-96,size-96,size+96,size+96));crop.resize((768,768),Image.Resampling.NEAREST).save(O/f'sea1b-seam-zoom-{size}.png')
 Image.fromarray(np.clip(np.abs(a.astype(float)-raw)*10,0,255).astype('uint8')).save(O/f'sea1b-difference-x10-{size}.png')
 rows.append({'file':p.name,'sha256':H(p),'size':[size,size],'mode':'RGB','repair_band_pixels':band,'exact_opposing_edge_equality':{'x':True,'y':True},'max_opposing_edge_RGB_delta':0,'interior_unchanged':True,'mean_absolute_change_RGB':float(abs(a.astype(float)-raw).mean()),'max_absolute_change_RGB':float(abs(a.astype(float)-raw).max()),'native_4x4_proof_size':list(proof.size)})
(O/'sea1b-texture-audit.json').write_text(json.dumps({'pass':True,'source_sha256':H(source),'method':'Lanczos accepted candidate4; symmetric opposing-edge mean correction in 1/32-width bands with cubic smoothstep falloff; rounding plus explicit identical opposing boundary; no creative repaint','textures':rows,'native_Unity_unverified':True},indent=2))
print('SEA1B PACKAGE PASS')

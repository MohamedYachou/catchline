from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((O/'sea1b-texture-audit.json').read_text());assert audit['pass']
for size in [1024,2048]:
 p=O/f'sea1-night-water-{size}.png';a=np.array(Image.open(p));assert a.shape==(size,size,3);assert np.array_equal(a[0],a[-1]);assert np.array_equal(a[:,0],a[:,-1])
 with Image.open(O/f'sea1b-tiling-proof-{size}-4x4.png') as im:
  assert im.size==(size*4,size*4)
  for x in range(4):
   for y in range(4):assert np.array_equal(np.array(im.crop((x*size,y*size,(x+1)*size,(y+1)*size))),a)
(O/'sea1b-REPORT.md').write_text('''# RESTAURANT-SEA-1B\n\nBoth accepted sea1-night-water tiles now have pixel-equal opposing edges in X and Y, including corners. Resolution, opaque RGB format, painted navy/blue ripples and sparse warm glints stay the same.\n\nThe reproducible recipe starts from the accepted candidate4 painting, Lanczos-resizes, then symmetrically blends opposing boundary differences into a 32px / 64px edge band with cubic smoothstep falloff. The remaining interior is bit-identical. No new painting or generated content. sea1-package.py now calls sea1b-package.py so rebuilding cannot restore the previous unequal edges. Numerical change statistics are in sea1b-texture-audit.json.\n\nProofs: native 4x4 PNGs at4096/8192 pixels, compact 4x4 JPGs, and nearest-neighbour 4x seam-intersection crops at both resolutions. Fresh independent reads verify edge equality and every repeated tile in all16 cells. Fine local ripple shapes still repeat with the source painting; exact boundary equality does not claim a new nonrepeating procedural ocean.\n\nThe additive sea1b-V4-check.blend and desktop/phone renders use the current RoomLook3 scene unchanged, the same V4 cameras and the same material recipe as SEA-1. Historical sea1 audits/proofs refer to the previous tile bytes; sea1b-final-audit.json supersedes their tile hashes. Original candidate4 provenance is unchanged.\n\nNo Assets/code/git edits. Native Unity sampling/material/runtime appearance remains lead-owned. Temporary repair backups removed after verification.\n''')
files=[O/'sea1-package.py']+[O/f'sea1-night-water-{s}.png' for s in [1024,2048]]+sorted(O.glob('sea1b-*'))
files=[p for p in files if p.is_file() and p.suffix!='.log' and p.name!='sea1b-final-audit.json']+sorted((O/'sea1b-renders').glob('*.png'))
imgs=[]
for p in files:
 if p.suffix.lower() in ['.png','.jpg']:
  with Image.open(p) as im:im.load();imgs.append({'file':str(p.relative_to(O)),'size':im.size})
(O/'sea1b-final-audit.json').write_text(json.dumps({'pass':True,'opposing_edges_fresh_read_equal':True,'all16proof_cells_identical':True,'files':{str(p.relative_to(O)):H(p) for p in files},'decoded_images':imgs,'native_Unity_unverified':True},indent=2))
print('SEA1B SEAL PASS',len(files),len(imgs))

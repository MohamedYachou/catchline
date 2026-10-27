"""Independent package-level checks; mesh/FBX checks are in separate Blender scripts."""
import json,hashlib,math
from pathlib import Path
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parents[3]
EXPECTED=set('Stove SoupKettle PrepCounter FridgeV2 CoffeeBar TableFor2 TableFor4 Booth TerraceTable ReceptionDesk SinkDishRack Fryer Oven Grill Steamer PassCounter PlantPot1 LampPost Trophy Net Chart Jukebox DrinksFridge TableCandle BigFridge ReliableStove'.split())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((O/'manifest.json').read_text());items={x['name'].removeprefix('Restaurant_'):x for x in d['items']};assert set(items)==EXPECTED
assert set(p.stem.removeprefix('Restaurant_') for p in O.glob('*.fbx'))==EXPECTED
assert len(items)==len(d['items'])==26
assert json.loads((O/'mesh-audit.json').read_text())['pass_all']
assert json.loads((O/'fbx-transform-audit.json').read_text())['pass_all']
for x in items.values():
 assert x['fbx_sha256']==sha(O/(x['name']+'.fbx'))
 assert (O/(x['name']+'.blend')).exists()
 for c in x['components']:assert (R/c['source']).is_file()
assert sum(x['triangles'] for x in items.values())<50000
wide={'TableFor4','Booth','SinkDishRack','PassCounter','BigFridge','ReliableStove'}
for n,x in items.items():
 w,h,dep=x['size_unity'];assert w<= (2.001 if n in wide else 1.001),(n,w)
 assert dep<=1.001,(n,dep)
 assert h<2,(n,h)
 assert abs(x['bounds_blender'][0][2])<1e-5
atlases=[]
for name,src in [('restaurantbits_texture-catchline.png',R/'Art/Source/Restaurant/kaykit'),('furniturebits_texture-catchline.png',R/'Art/Source/Restaurant/kaykit'),('food-colormap-catchline.png',R/'Art/Source/Restaurant/kenney')]:
 assert sha(O/name)==sha(src/name);im=Image.open(O/name);assert im.mode=='RGBA';atlases.append(dict(file=name,size=im.size,sha256=sha(O/name)))
proofs=['before-grid-contact.jpg','after-grid-contact.jpg']+[f'comparison-contact-{i}.jpg' for i in range(1,6)]
proofs += ['comparisons/Restaurant_'+n+'.jpg' for n in EXPECTED]
images=[]
for rel in proofs:
 with Image.open(O/rel) as im:im.load();images.append(dict(file=rel,size=im.size,sha256=sha(O/rel)))
baseline=json.loads((O/'preservation-baseline.json').read_text());changed=[p for p,v in baseline.items() if not (R/p).exists() or sha(R/p)!=v];assert not changed,changed
rec=dict(pass_all=True,exact_names=26,total_triangles=sum(x['triangles'] for x in items.values()),original_files_unchanged=len(baseline),atlases=atlases,decoded_final_proofs=images,footprint_check='26 within declared 1x1 or 2x1 metre footprint; pivot floor contact zero',limits='Source-only. Native Unity facing/import/material/shader/runtime seating not accepted by this audit.')
(O/'audit.json').write_text(json.dumps(rec,indent=2));print('DELIVERY_PASS',len(items),'models',len(images),'proofs',len(baseline),'original files')

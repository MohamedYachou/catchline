from pathlib import Path
import json,hashlib
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((O/'preservation-baseline.json').read_text())
changed=[p for p,h in baseline.items() if not (R/p).exists() or sha(R/p)!=h]
expected={'Restaurant_'+n for n in ['Dish_GrilledFish','Dish_FilletsLemon','Dish_FishSoup','Dish_CoffeeBiscuits','Dish_Lemonade','GrilledFishPlate']}
manifest=json.loads((O/'manifest.json').read_text())
audits={n:json.loads((O/n).read_text()) for n in ['mesh-audit.json','fbx-transform-audit.json','geometry-audit.json']}
images=list((O/'renders').glob('*.png'))+list(O.glob('contact-*.jpg'))
for p in images:
 with Image.open(p) as im:im.load();assert min(im.size)>0
atlases={p.name:sha(p) for p in O.glob('*png')}
atlas_checks=[]
for p in O.glob('*png'):
 original=R/'Art/Source/Restaurant'/('kaykit' if 'restaurantbits' in p.name else 'kenney')/p.name
 atlas_checks.append(sha(original)==sha(p))
checks=dict(exact_names={r['name'] for r in manifest['items']}==expected=={p.stem for p in O.glob('Restaurant_*.fbx')},four_atlases=len(atlases)==4 and all(atlas_checks),originals_unchanged=not changed,three_independent_audits=all(a['pass_all'] for a in audits.values()),twelve_renders_two_contacts=len(images)==14,all_source_components_present=all((R/c['source']).is_file() for r in manifest['items'] for c in r['components']))
result=dict(pass_all=all(checks.values()),checks=checks,original_files=len(baseline),changed_originals=changed,models=len(expected),triangles=sum(r['triangles'] for r in manifest['items']),decoded_proofs=len(images),atlases=atlases,proofs={p.relative_to(O).as_posix():sha(p) for p in images})
(O/'audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert result['pass_all']

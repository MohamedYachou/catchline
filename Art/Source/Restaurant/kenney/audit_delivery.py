"""Source preservation, recipe completeness and image packaging checks."""
from pathlib import Path
from PIL import Image
import hashlib,json,re,math
O=Path(__file__).resolve().parent;R=O.parents[3]
baseline=json.loads((O/'preservation-baseline.json').read_text())
changed=[p for p,h in baseline.items() if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
assert not changed,changed
dm=json.loads((O/'dish-map.json').read_text());decor=json.loads((O/'decor-map.json').read_text())
data=(R/'Assets/Scripts/Game/Restaurant/RestaurantData.cs').read_text()
enum=re.search(r'enum Dish\s*\{([^}]+)',data).group(1)
keys=re.findall(r'\b([A-Za-z]+)\b',re.sub(r'//[^\n]*','',enum))
assert set(keys)=={x['dish'] for x in dm['dishes']},keys
assert len(decor['decor'])==13
sources=0
for recipe in dm['dishes']:
 for c in recipe['components']:
  if c.get('source') and c['pack']!='primitive':
   assert (R/c['source']).is_file(),c['source'];sources+=1
  assert all(math.isfinite(v) and v>0 for v in c['target_size_m'])
mesh=json.loads((O/'mesh-audit.json').read_text());assert mesh['status']=='PASS' and len(mesh['models'])==26
images=[]
for p in sorted((O/'renders').glob('*.png')):
 with Image.open(p) as im:im.verify()
 images.append(p.name)
for dish in keys:
 assert f'dish-{dish}.png' in images and f'detail-{dish}.png' in images
for rec in decor['decor']:
 for variant in ['original','catchline']:assert f'decor-{rec["model"]}-{variant}.png' in images
contacts=['dish-contact-tables.jpg','dish-contact-details.jpg','decor-contact-1.jpg','decor-contact-2.jpg','palette-map.jpg']
for name in contacts:
 with Image.open(O/name) as im:im.verify()
src=Image.open(R/'Art/Downloads/kenney/food/Models/GLB format/Textures/colormap.png').convert('RGBA')
for mode in ['catchline','lemonade','roast']:
 im=Image.open(O/f'food-colormap-{mode}.png').convert('RGBA')
 assert im.size==src.size==(512,512)
 assert im.getchannel('A').tobytes()==src.getchannel('A').tobytes()
food=Image.open(O/'food-colormap-catchline.png').convert('RGBA')
natural=0
for a,b in zip(src.getdata(),food.getdata()):
 r,g,bl,_=a
 if (r>g*1.15 and g>bl*1.15) or (g>r*1.15 and g>bl*1.15) or (r>bl*1.15 and g>bl*1.15):
  assert a==b,(a,b)
  natural+=1
out=dict(status='PASS',original_kenney_files_sha256_unchanged=len(baseline),menu_enum_complete=keys,
 decor_models=13,recipe_source_references_exist=sources,mesh_audit='mesh-audit.json',
 render_images_decoded=len(images),contacts_decoded=contacts,palette_dimensions_alpha_preserved=True,
 natural_orange_brown_yellow_green_pixels_unchanged=natural,
 limits='Standalone Blender source proof. No Unity import, runtime, performance or player acceptance claimed.')
(O/'audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

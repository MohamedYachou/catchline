from pathlib import Path
import json,re,hashlib
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;R=O.parents[3]
rows=json.loads((O/'manifest.json').read_text())['assets'];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
im=Image.new('RGB',(1600,740),(22,39,60));d=ImageDraw.Draw(im)
for i,r in enumerate(rows):
 x=(i%5)*320;y=(i//5)*370;p=Image.open(O/'renders'/(r['name']+'.png')).convert('RGBA');p.thumbnail((310,320));im.paste(p,(x+(320-p.width)//2,y),p);d.text((x+10,y+325),r['name'].removeprefix('Restaurant_'),font=font,fill='white');d.text((x+10,y+350),f"{r['tiles_w']}x{r['tiles_d']} tile | {r['triangles']:,} tris",font=font,fill=(180,203,216))
im.save(O/'kitchen-kit-review.jpg',quality=94)
new={n:n for n in 'Grill Steamer DrinksFridge Trophy Net Chart Jukebox'.split()}
alias={'PrepCounter':'PrepCounter','Stove':'Stove','SoupKettle':'SoupKettle','Fryer':'Fryer','Oven':'Oven','Fridge':'FridgeV2','Sink':'SinkDishRack','CoffeeMachine':'CoffeeBar','BarCounter':'PassCounter','Table2':'TableFor2','Table4':'TableFor4','Booth6':'Booth','TerraceTable':'TerraceTable','Reception':'ReceptionDesk','Lamp':'LampPost','Plant':'PlantPot1'}
items=re.findall(r'I\(ItemId\.(\w+)',(R/'Assets/Scripts/Game/Restaurant/RestaurantData.cs').read_text());coverage=[]
for key in items:
 model=new.get(key,alias.get(key));assert model,key
 path=O/('Restaurant_'+model+'.fbx') if key in new else next((R/'Assets/Art/Models/Restaurant').rglob('Restaurant_'+model+'.fbx'))
 coverage.append({'ItemId':key,'model_key':model,'file':str(path.relative_to(R)),'new_delivery':key in new,'current_runtime_remap_required':key in new})
assert len(coverage)==23
(O/'id-to-file.json').write_text(json.dumps(coverage,indent=2))
report='''# Restaurant kitchen kit 2

Ten placeable FBXs, metre-scale and floor/base-contact Z=0, footprint-centred origin. The original V4 atlas is byte-identical. The three upgrades follow the S8 illustrations: twin cream fridge/navy crown, six-burner range/twin ovens, navy enamel warm pendant. Each has a footprint JSON and mesh/bounds inventory. No presentation meshes, lights, cameras or crew are exported.

Dedicated semantic replacements: Grill (open grate/coals), Steamer (stacked lidded pot), DrinksFridge (bottles/shelves), Chart (coast/islands/compass), Jukebox (brass arch/speaker/controls). Net and Trophy reuse the accepted Upgrades geometry under explicit ItemId filenames. Existing models with legitimate aliases remain in use; no duplicate production files were made for those aliases.

## ItemId coverage

| ItemId | Model key | File | Delivery |
|---|---|---|---|
'''
for r in coverage:report+=f"| {r['ItemId']} | {r['model_key']} | `{r['file']}` | {'NEW; runtime mapping needed' if r['new_delivery'] else 'existing'} |\n"
report+='''
## Integration

New filenames already include `Restaurant_`; do not add that prefix a second time. Update the seven stand-in ItemId mappings to the keys above. BigFridge/ReliableStove/CosyPendantLamp are upgrade variants, not new ItemIds; the lead chooses how to toggle them. Wall props use local base0 and suggested mounting height in footprint JSON; the pendant base is the underside of its shade, suggested Z=1.65m. No invisible floor support is included. Give the pendant a warm point light at its bulb (local0,0,.04), ~8 Blender W / 2m recipe range; preserve Surface.B emission. Lamps/coal are opaque atlas colours, not alpha materials.

Use the shared Restaurant atlas material with BaseColor plus Surface R=roughness,G=metallic,B=emission, suggested emission multiplier2.5. FBX embeds BaseColor; packed source retains Surface too. Axes Blender X,Y,Z -> Unity X,Z,-Y. Footprints reserve occupancy, operator access is adjacent.

## Verification

`validation.json`: ten fresh independent FBX imports; exact mesh inventories, identity transforms, finite bounds/roundtrip<1e-5m, floor-contact0 and footprint containment, all UV face corners inside a single inset atlas cell, correct triangle totals, embedded base loaded and identical V4 texture hashes. `kitchen-kit-review.jpg` shows all ten closeups; exact saved V4 camera lineups at1440x900 and844x390 use neutral review lighting/floor. Native Unity import, mapping, arrange mode, shading and final gameplay visibility remain for Claude. No Assets/code/git edits; no commit.
'''
(O/'REPORT.md').write_text(report)
print('PACKAGED',len(rows),'models',len(coverage),'ItemIds')

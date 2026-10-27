from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import json,hashlib,textwrap,time
O=Path(__file__).resolve().parent;R=O.parents[3]
rows=json.loads((O/'female-palette.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),size)
ink='#193E50';muted='#526570';cream='#F3EFE5'
out=Image.new('RGB',(1600,140+8*400+100),cream);d=ImageDraw.Draw(out)
d.text((42,24),'CATCHLINE / QUATERNIUS CREW',font=font(42,True),fill=ink)
d.text((44,80),'CODEX 1  /  PHASE 1  /  bind pose  /  pitch 38 degrees, yaw 2 degrees  /  1 m grid',font=font(22),fill=muted)
for i,r in enumerate(rows):
 y=140+i*400
 d.rectangle((26,y,1574,y+382),fill='#FFFDFA')
 ref=Image.open(R/f"Assets/Art/UI/Portraits/art108-{r['name']}.png").convert('RGBA')
 ref.thumbnail((235,290));bg=Image.new('RGBA',ref.size,'#153B4C');bg.alpha_composite(ref);out.paste(bg.convert('RGB'),(44,y+65))
 d.text((44,y+25),'PORTRAIT',font=font(18,True),fill=muted)
 proof=Image.open(O/f"female-{r['name']}-proof.png").convert('RGB');small=proof.resize((303,370),Image.Resampling.LANCZOS);out.paste(small,(303,y+6))
 face=proof.crop((300,165,610,390)).resize((310,225),Image.Resampling.LANCZOS);out.paste(face,(635,y+77))
 d.text((635,y+27),'HEAD DETAIL',font=font(18,True),fill=muted)
 x=980
 d.text((x,y+25),r['name'].upper(),font=font(34,True),fill=ink)
 role={'mira':'NAVIGATOR','noor':'DECKHAND','rosa':'FISHER','tess':'FISHER','ana':'DECKHAND','lise':'FISHER','ines':'ENGINEER','tove':'DECKHAND'}[r['name']]
 d.text((x,y+73),f"{role}  /  {r['gender']}  /  {r['hair']}",font=font(20,True),fill=muted)
 for j,key in enumerate(('skinHex','hairHex','eyeHex','suitHex')):
  sx=x+j*139;d.rounded_rectangle((sx,y+117,sx+114,y+151),radius=5,fill=r[key],outline='#CCC6BA')
  d.text((sx,y+161),key.replace('Hex','').upper(),font=font(14,True),fill=muted)
  d.text((sx,y+183),r[key],font=font(16),fill=ink)
 for j,line in enumerate(textwrap.wrap(r['note'],width=61)):
  d.text((x,y+227+j*25),line,font=font(18),fill=ink)
d.text((44,out.height-75),'SOURCE DELIVERY: 8 FBXs / original rigs / Skin + Suit + Hair + Eyes + Brows',font=font(22,True),fill=ink)
d.text((44,out.height-41),'CC0 Quaternius / no outfit meshes / Unity Humanoid retargeting and player acceptance remain with Claude + Mo.',font=font(20),fill=muted)
out.save(O/'crew-contact-1.jpg',quality=94,subsampling=0)
grid=Image.open(O/'female-grid.png').convert('RGB')
canvas=Image.new('RGB',(2400,1640),cream);canvas.paste(grid,(0,100));dr=ImageDraw.Draw(canvas)
dr.text((45,23),'CREW 1 / ORIGINAL SCALE / BIND POSE',font=font(40,True),fill=ink)
dr.text((1250,37),'38 deg pitch / 2 deg yaw / 1 m floor grid',font=font(26),fill=muted)
# Labels use recorded projected pelvis/foot coordinates, not assumed screen row order.
bounds=json.loads((O/'female-grid-bounds.json').read_text())
for r in rows:
 box=bounds[r['name']];x,y=box['label']
 label=r['name'].upper()+(' (M)' if r['gender']=='M' else '')
 tw=dr.textbbox((0,0),label,font=font(27,True))[2]
 dr.rounded_rectangle((x-tw/2-14,y+100-6,x+tw/2+14,y+100+34),radius=9,fill=cream)
 dr.text((x-tw/2,y+100),label,font=font(27,True),fill=ink)
dr.text((45,1600),'Phase 1 only. Real outfits deferred. Rosa follows the male portrait; Mira = brown Buns; Ines = light-blonde Long.',font=font(24),fill=ink)
canvas.save(O/'crew-contact-1-grid.jpg',quality=94,subsampling=0)
canvas.resize((844,round(canvas.height*844/canvas.width)),Image.Resampling.LANCZOS).save(O/'crew-contact-1-844.jpg',quality=94,subsampling=0)
# Shared manifest merges latest rows; never replace the other roster.
p=O/'crew-manifest.json'
existing=json.loads(p.read_text()) if p.exists() else []
if isinstance(existing,dict):
 key='crew' if 'crew' in existing else 'characters';current=existing.setdefault(key,[])
else:current=existing
names={r['name'] for r in rows};current[:]=[r for r in current if r.get('name') not in names]
current.extend({k:r[k] for k in ('name','gender','hair','skinHex','hairHex','eyeHex','suitHex','note')} for r in rows)
p.write_text(json.dumps(existing,indent=2)+'\n')
audits=[json.loads((O/f"female-{r['name']}-audit.json").read_text()) for r in rows]
total=sum(json.loads((O/f"female-{r['name']}-baseline.json").read_text())['triangles'] for r in rows)
report='''

## Codex 1 (Windows) - CREW-QUATERNIUS-F - Phase 1 delivered

Eight crew: mira, noor, rosa, tess, ana, lise, ines, tove. Seven Superhero_Female bases; Rosa uses Superhero_Male because the portrait reads male. CC0 Quaternius Universal Base Characters; no new clothing meshes. The supplied whole-body surface is partitioned into Skin (head/neck/hands/fingers) and one flat role-coloured Suit placeholder. Hair/Eyes/Brows are independent material slots. Hair and replacement matching brows are rigid children of the original Head bone; the accessory skeletons are discarded and the original body skeleton is retained. The original eye mesh and supplied iris/sclera texture are preserved with a dark recoloured iris.

### Art and substitutions

Skin and hair swatches were sampled from the actual art108 PNGs using the recorded contact positions in female-palette.json. Mira's fair skin is an explicit Mo override compensating the warm orange portrait lighting. Skin textures are colour-modulated copies of the supplied diffuse, preserving facial and hand detail. Eyes retain the supplied white sclera, pupil and highlight instead of becoming a single flat dark surface. Hair is matte solid colour. The whole native body scale, rig and weights are untouched; these are human-height bases, not the retired 0.95 m crew proportions.

'''
for r in rows:report+=f"- **{r['name']} ({r['gender']})**: {r['note']}\n"
report+='''
### Deliverables and checks

- `<name>.fbx`: eight bind-pose FBXs, no animation; skin/eye textures embedded and also supplied as adjacent `female-<name>-{skin,eyes}.png` fallbacks. Editable `female-<name>.blend` source files retained.
- `crew-contact-1.jpg`: one labelled row per crew, portrait, fixed-scale game-camera full body on the 1 m grid, enlarged head crop, exact swatches and substitution notes.
- `crew-contact-1-grid.jpg` and `crew-contact-1-844.jpg`: all eight freshly imported FBXs together, original scale, orthographic camera pitch 38/yaw 2, 1 m grid; the overview is exactly 844 pixels wide. Labels and floor are proof-only.
- `female-build.py`, `female-prepare.py`, `female-package.py`, `female-palette.json`, eight `female-<name>-baseline.json` and eight `female-<name>-audit.json` make the result reproducible. Baselines capture the original source bones/hierarchy/rest transforms and hashes before styling.
- Fresh-import audit PASS for all eight: original 65 bone names/hierarchy each; no intentional bone, skeleton scale or rest changes. FBX numeric maximum rest-matrix deviation 0.000026 (tolerance 0.0001); root matrix maximum 0.000000076; bind-pose identity maximum 0.000020. Original body geometry, UVs and skin weights compare exactly (zero maximum error). Zero animation clips. Four mesh objects, exactly five named materials. Both Head children follow a tested Head rotation. No extra accessory rig, duplicate brows, floor or lights exported.
'''
report+=f'\nTotal triangulated geometry for this roster: {total:,}. See female-verify-all.log and per-crew audit JSONs. Final file/proof hashes are in female-delivery-audit.json.\n'
report+='''
### Boundaries and next owner

Phase 1 source delivery only. No Assets/, runtime scripts, git operations or Unity batchmode. Claude owns native Unity import, Humanoid avatar creation, Universal Animation Library retargeting, materials/shader assignment, integration and gameplay checks. Blender import/pose proofs do not establish native Unity acceptance or Mo visual acceptance. Phase 2 boat-work and restaurant clothing remains blocked on Mo's choice of outfit mesh source. No further outfit modelling performed. No commit. Codex 1 releases its named paths and is IDLE after visual/package verification.
'''
rp=O/'REPORT.md';previous=rp.read_text() if rp.exists() else '# Quaternius crew - Phase 1\n'
assert '## Codex 1 (Windows) - CREW-QUATERNIUS-F' not in previous,'Own report already appended; inspect before rerun.'
with rp.open('a',encoding='utf-8') as f:f.write(report)
seal={'owner':'Codex 1 (Windows)','names':[r['name'] for r in rows],'source_delivery_PASS':all(a['PASS'] for a in audits),'total_triangles':total,'proof_dimensions':{},'hashes':{},'original_body_sources_unchanged':{}}
for r in rows:
 baseline=json.loads((O/f"female-{r['name']}-baseline.json").read_text());actual=sha(R/baseline['source'])
 assert actual==baseline['source_sha256']
 seal['original_body_sources_unchanged'][baseline['source']]=actual
 for suffix in ('.fbx',):seal['hashes'][r['name']+suffix]=sha(O/(r['name']+suffix))
for p in [O/'crew-contact-1.jpg',O/'crew-contact-1-grid.jpg',O/'crew-contact-1-844.jpg']+[O/f"female-{r['name']}-proof.png" for r in rows]:
 seal['hashes'][p.name]=sha(p);seal['proof_dimensions'][p.name]=Image.open(p).size
(O/'female-delivery-audit.json').write_text(json.dumps(seal,indent=2))
print(json.dumps({'PASS':seal['source_delivery_PASS'],'crew':len(rows),'triangles':total,'contact':out.size,'overview':seal['proof_dimensions']['crew-contact-1-844.jpg']}))

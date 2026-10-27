"""Reference comparison and delivery seal; no source-image editing."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'mira-match-renders'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
canvas=Image.new('RGB',(1500,900),'#20313a');d=ImageDraw.Draw(canvas)
refs=[R/'Art/Source/Restaurant/exact/s2-call/v2-s2-call-mira.png',R/'Art/Source/Restaurant/exact/coach-card/v2-coach-mira.png',P/'mira-front.png',P/'mira-v4-detail.png']
for i,(p,label) in enumerate(zip(refs,['Call portrait reference','Coach portrait reference','Mira rig / front','V4 lit room / detail'])):
 im=Image.open(p).convert('RGBA');im=im.crop(im.getbbox());im=ImageOps.contain(im,(360,760),Image.Resampling.LANCZOS);x=i*375+(375-im.width)//2;y=65+(760-im.height)//2;canvas.paste(im,(x,y),im);d.text((i*375+12,20),label,fill='white',font=font)
d.text((20,850),'Same shared Body, outfits, 20 bones and all 20 clips. Head/hair live only in Hat_HairUpClip.',fill='white',font=font)
canvas.save(O/'mira-match-review.jpg',quality=96)
# Requested phone-sized front lineup with the face reference adjacent.
sheet=Image.new('RGB',(844,390),'#20313a');dr=ImageDraw.Draw(sheet)
for i,p in enumerate([refs[0],P/'mira-front.png',refs[1]]):
 im=Image.open(p).convert('RGBA');im=im.crop(im.getbbox());im=ImageOps.contain(im,(270,340),Image.Resampling.LANCZOS);sheet.paste(im,(i*281+(281-im.width)//2,40+(340-im.height)//2),im)
for x,t in [(10,'Call Mira'),(291,'3D Mira'),(572,'Coach Mira')]:dr.text((x,10),t,font=font,fill='white')
sheet.save(O/'mira-match-lineup-844.png')
a=json.loads((O/'mira-match-validation.json').read_text());assert a['pass']
(O/'mira-match-REPORT.md').write_text('''# MIRA-3D-MATCH\n\nMira now has shoulder-length wavy chestnut locks, a gold leaf clip, warm brown eyes and a smiling face matched to the call/coach portraits. The existing Hat_HairUpClip toggle includes a closed skinned face overlay: RestaurantWorld already enables this toggle for Mira, so shared crew Body and every Outfit remain unchanged. No runtime code is needed.\n\nFresh FBX import verifies all 20 bones/rest matrices, all 20 animation clips (five sampled poses per clip), mesh names, and all 18 unaffected sibling meshes including positions, materials, UVs and weights. New head weights are normalized and attached to Head. FBX_SCALE_UNITS export matches the accepted rig. See mira-match-validation.json for exact bounds and triangle counts.\n\nReview: mira-match-review.jpg, phone-size face-linked mira-match-lineup-844.png, front/threequarter/back, a diagnostic enlarged V4 detail, and actual 1440x900 + 844x390 V4 room views. Diagnostic studio/detail views are explicitly separate from game-scale evidence. The face retains the game's stylized crew proportions; this is an interpretation of the painted portrait.\n\nNo Assets/code/git edited. Blender source verification only; Unity import, crew colour mapping, runtime clip playback and in-game appearance remain lead-owned. Compressed pre-change measurements retained for independent reruns; temporary source backup removed after final verification.\n''')
files=[O/'CrewRig_Restaurant.blend',O/'CrewRig_Restaurant.fbx']+sorted(O.glob('mira-match-*'))
files=[p for p in files if p.is_file() and p.suffix not in ['.log'] and p.name!='mira-match-final-audit.json']+sorted(P.glob('*.png'))
imgs=[]
for p in files:
 if p.suffix.lower() in ['.jpg','.png']:
  with Image.open(p) as im:im.load();imgs.append({'file':str(p.relative_to(O)),'size':im.size})
(O/'mira-match-final-audit.json').write_text(json.dumps({'pass':True,'files':{str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'decoded_images':imgs,'native_Unity_unverified':True},indent=2))
print('MIRA PACKAGE PASS',len(files),len(imgs))

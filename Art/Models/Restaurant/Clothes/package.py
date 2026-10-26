"""Mechanical contact sheets and source/export handoff, no painted asset generation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders'
rows=json.loads((O/'build-metrics.json').read_text())['assets'];validation=json.loads((O/'validation.json').read_text());assert len(validation['assets'])==8
for row,check in zip(rows,validation['assets']):
 assert row['asset']==check['asset'] and row['fbx_sha256']==check['fbx_sha256']
 assert hashlib.sha256((O/(row['asset']+'.fbx')).read_bytes()).hexdigest()==row['fbx_sha256']
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
def paste_fit(sheet,path,box):
 im=Image.open(path).convert('RGBA');im.thumbnail((box[2],box[3]),Image.Resampling.LANCZOS);sheet.paste(im,(box[0]+(box[2]-im.width)//2,box[1]+(box[3]-im.height)//2),im)
def text(sheet,x,y,s):ImageDraw.Draw(sheet).text((x,y),s,font=font,fill=(243,240,220))
images=[]
for row in rows:
 n=row['asset'];sheet=Image.new('RGB',(1440,500),(38,54,65));text(sheet,18,12,n+' / front | game camera | back | walk')
 for j,label in enumerate(['front','game45','back','walk']):paste_fit(sheet,P/(n+'-'+label+'.png'),(j*360,40,360,445))
 sheet.save(P/(n+'-review.jpg'),quality=94);images.append(n+'-review.jpg')
lineup=Image.new('RGB',(1600,900),(38,54,65))
for i,row in enumerate(rows):
 x=(i%4)*400;y=(i//4)*450;text(lineup,x+12,y+12,row['asset']);paste_fit(lineup,P/(row['asset']+'-game45.png'),(x,y+36,400,408))
lineup.save(P/'job-lineup.jpg',quality=95)
# Make explicit visual comparisons with available same-person 2D, plus target mockup; no write to Codex1 folders.
comparisons=[]
lookup={'Host_Mira':'mira-a','Cook_Dirk':'dirk','Server_Ana':'ana','Barista_Ines':'ines','Handyman_Olaf':'olaf','Helper_Captain':'captain','PrepCook_Dirk':'dirk','Dishwasher_Olaf':'olaf'}
for row in rows:
 n=row['asset'];key=lookup[n];two=R/'Art/Source/Restaurant/clothes/2d'/((key or '')+'-sheet.png');available=key and two.exists()
 sheet=Image.new('RGB',(1440,760),(38,54,65));text(sheet,16,12,n+' / existing CrewRig proportions; original face/hair retained')
 paste_fit(sheet,P/(n+'-front.png'),(0,55,400,680));paste_fit(sheet,P/(n+'-game45.png'),(400,55,400,680))
 if available:paste_fit(sheet,two,(810,55,620,680));label='same-person 2D design: '+key
 else:paste_fit(sheet,R/'Art/Source/Restaurant/concepts/ui-service-desktop.png',(810,100,620,600));label='restaurant light/palette reference; 2D not available at packaging'
 text(sheet,810,40,label);sheet.save(P/(n+'-reference.jpg'),quality=94);comparisons.append({'asset':n,'comparison':n+'-reference.jpg','same_person_2d':str(two.relative_to(R)) if available else None})
(O/'comparison-manifest.json').write_text(json.dumps(comparisons,indent=2))
report=['# Restaurant crew clothes — Codex 2 (WSL CLI)','','Eight source/export pairs: one representative identity per live job, plus two kitchen support alternatives. This is the 3D part; the per-person 2D roster remains Codex1-owned. No runtime files changed.','','| FBX + matching blend | Person | Live job / suggested use | Total triangles |','|---|---|---|---:|']
for row in rows:report.append(f"| [{row['asset']}.fbx]({row['asset']}.fbx) | {row['person']} | {row['job']} | {sum(m['triangles'] for m in row['meshes']):,} |")
report += ['','## Integration','','Use the full FBX when that representative person occupies the role. Each contains exactly four skinned meshes: unchanged face, unchanged expression, unchanged original hair, and the new `*_Outfit`. The outfit can be used as a sibling mesh on the identical CrewRig for other identities; preserve their own face/expression/hair and adapt the person-specific head crown and hand colours to that identity; the crown is part of the outfit mesh, not a universal hairstyle. Do not replace everyone with these six faces.','','`Reception`, `Cook`, `Waiter`, `Barista`, `Handyman`, `Helper` are the current enum. Prep cook and dishwasher are wardrobe alternatives, not new runtime jobs; no bartender enum exists. Mira is the host; Dirk represents Cook; Ana Waiter; Ines Barista; Olaf Handyman; Captain Helper. Actual job mapping was read from RestaurantData.cs, RestaurantSim.cs and Cards.cs.','','Metres, sole-level origin; Blender faces -Y/Z-up. FBX uses -Z forward/Y-up, scale units, no leaf bones. Armature is `CrewRig`, original 20 bones/rest/hierarchy and all 11 original clips at 24 fps. Guest-only additive Sit/Eat clips are not copied. No floor, camera, lights or presentation mesh is exported. Original image textures are embedded in FBX and packed in blend; local copies are in textures/. New cloth uses matte opaque material colours.','','## Visual design and evidence','','Mira follows the navy/ivory 2D option A with gold belt/pin, ivory neckline, dressed hair/barrette and earrings. Women wear smart ivory tops/navy skirts; men navy suits, contrasting lapels, ivory shirts and bow ties. Cooks wear ivory double-breasted coats and toques; prep/dish variants add teal aprons only for kitchen work. Existing compact CrewRig body proportions and original face/hair stay intact; this is not a literal reproduction of the taller illustrated 2D anatomy. Warm key/cool ambient lighting follows ui-service-desktop.png. Ana uses an ivory-top/navy-skirt variation rather than the teal illustrated dress; Ines uses an ivory blouse/navy waistcoat variation. Prep/dish comparisons show the same person’s standard 2D wardrobe for identity and palette, not a dedicated support-role drawing.','','[All jobs at the elevated game view](renders/job-lineup.jpg). Each `renders/*-review.jpg` shows front, game camera, back and Walk; each `*-reference.jpg` compares with available same-person 2D or the desktop mockup. All views render from fresh FBX imports, not source-only geometry. Comparison references are recorded in comparison-manifest.json. All eight final four-view sheets, eight reference sheets and the lineup were opened; visual-review.json records those opens and file hashes. Visual review rejected separated waist primitives, flat crowns, a scalp gap below Ana’s bun and thigh/skirt penetration in Walk. Final exports use a continuous weighted coat, a wider skirt with walking clearance, textured scalp coverage and smooth swept hair locks; original identity geometry remains untouched.','','## Checks and limits','','validation.json records independent fresh FBX import checks against the original Assets/Art/Models/Crew/CrewRig.fbx: exact bone names/parents, rest matrices, Idle and Walk matrices sampled at five frames, all 11 clips present, normalized nonempty skin weights, exactly four meshes, and per-mesh world bounds below 1.5m. build-metrics.json records source identity geometry hashes, source provenance, triangles, rest bounds and byte-identical packaged texture hashes; validation.json confirms those images load after FBX reimport. Relative texture paths that failed after moving the source were corrected before delivery. Source face/expression/hair vertex and polygon signatures were asserted unchanged before export. Native Unity/avatar/material integration and collision-free blending across every runtime transition still need Claude’s game check. No native acceptance is claimed.','','## Exported bounds (fresh FBX import)','','| Asset / mesh | Min XYZ (m) | Max XYZ (m) |','|---|---|---|']
for row in validation['assets']:
 for m in row['meshes']:
  lo,hi=m['world_bounds_rest'];report.append(f"| {row['asset']} / {m['mesh']} | {', '.join(f'{v:.3f}' for v in lo)} | {', '.join(f'{v:.3f}' for v in hi)} |")
report+=['','No Assets/code/.meta/save/watchdog edits. No commit. Source builders and validation scripts are scoped to this folder.']
(O/'REPORT.md').write_text('\n'.join(report)+'\n')
print('PACKAGED',len(rows),'outfit review sheets and reference comparisons')

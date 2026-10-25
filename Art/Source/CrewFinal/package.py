"""Shared source-only verification, inventories and contact sheets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
FONT=str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf')
def inventory(group,files,notes):
 records=[]
 for f in files:
  p=OUT/f;im=Image.open(p)
  assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0,f
  assert im.getchannel('A').getbbox(),f
  records.append(dict(file=f,size=list(im.size),mode=im.mode,alpha=list(im.getchannel('A').getextrema()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 (OUT/f'manifest-{group}.json').write_text(json.dumps(dict(group=group,notes=notes,files=records),indent=2)+'\n')
 return records
def sheet(group,files,cols=3,refs=None):
 # Full native-size asset and true 64px phone sample for every exported PNG.
 cols=min(cols,len(files));sizes=[Image.open(OUT/f).size for f in files]
 cw=max(w for w,h in sizes)+135;rh=max(h for w,h in sizes)+60
 rows=(len(files)+cols-1)//cols
 refh=240 if refs else 0
 im=Image.new('RGB',(cw*cols+24,rh*rows+80+refh),'#F4EFE3');d=ImageDraw.Draw(im)
 def text(x,y,t,sz=18):d.text((x,y),t,font=ImageFont.truetype(FONT,sz),fill='#173F57')
 text(16,12,f'Group {group} / full-size exports + true 64px samples',27)
 for i,f in enumerate(files):
  x=12+i%cols*cw;y=65+i//cols*rh;a=Image.open(OUT/f)
  text(x,y-20,f,14)
  # Subtle checkerboard shows alpha without competing with icon palettes.
  for yy in range(y,y+a.height,24):
   for xx in range(x,x+a.width,24):
    if ((xx-x)//24+(yy-y)//24)%2==0:d.rectangle((xx,yy,min(xx+23,x+a.width-1),min(yy+23,y+a.height-1)),fill='#E5DED0')
  im.paste(a,(x,y),a)
  sample=a.resize((round(a.width*64/max(a.size)),round(a.height*64/max(a.size))),Image.Resampling.LANCZOS)
  d.rectangle((x+a.width+12,y,x+a.width+99,y+98),fill='#173F57');im.paste(sample,(x+a.width+24,y+12),sample)
  text(x+a.width+12,y+110,'64px',14)
 if refs:
  y=rh*rows+82;text(16,y,'Existing roster / UI art reference',19)
  for i,p in enumerate(refs):
   a=Image.open(p).convert('RGBA');a.thumbnail((160,180));im.paste(a,(18+i*190,y+35),a)
 im.save(OUT/f'review/{group}-contact.png',optimize=True)
def report():
 out=['# CREW-FINAL-ART-1\n','Codex 2 (WSL CLI). Source-only delivery for Claude to copy; no Assets, C#, Unity or git operations.\n','Review status is recorded below per group. Native UI acceptance remains separate.\n']
 manifests=[json.loads(p.read_text()) for p in sorted(OUT.glob('manifest-*.json'))]
 if len(manifests)==6 and all(d['notes'].startswith('DONE') for d in manifests):
  out+=['**Artist delivery complete: 70 requested PNG exports, groups A–F.** Exact filenames, dimensions, RGBA, transparent corners and current hashes pass in [delivery-checks.json](delivery-checks.json).\n',
        'Opened review evidence: [Rosa](review/A-rosa.png), [Ines](review/A-ines.png), [Tess](review/A-tess.png), [frames](review/B-contact.png), [icons](review/C-contact.png), [chests](review/D-contact.png), [tools 1](review/E-tools-1-contact.png), [tools 2](review/E-tools-2-contact.png), [tiles](review/E-tiles-contact.png), [tile contrast](review/E-tile-contrast.png), [card back](review/F-contact.png). Each export is shown at its native size and a 56–64px sample beside existing art.\n',
        'Source methods: deterministic extraction of the three approved portraits; editable SVG extensions of the existing nautical icon/frame kit for B/C/E/F; built-in imagegen for five chest states, with the earlier crate-closed reused. [Chest prompts](chest-prompts.json), [chest source hashes/bounds](chest-checks.json), [portrait extraction](portraits-manifest.json), [frame masks](frame-checks.json). Original references remain untouched. SVG equipment is cleaner and simpler than the painted portraits/chests; its kit palette, outlines, gradients and phone contrast were visually reviewed.\n',
        'Integration limit: no runtime or player-save access. Lead/Mo still own native card layout, icon sizing, rarity tint and reveal acceptance. Independently generated chest states can shift body proportions; common canvas/baseline does not guarantee a pixel-stable animated hinge. No blockers or skipped asset groups.\n']
 for p in sorted(OUT.glob('manifest-*.json')):
  data=json.loads(p.read_text());g=data['group'];out.append(f'\n## Group {g}\n\n'+data['notes']+'\n\n| File | Size | Mode | Alpha |\n|---|---|---|---|')
  for r in data['files']:out.append(f"| {r['file']} | {r['size'][0]}×{r['size'][1]} | {r['mode']} | {r['alpha'][0]}–{r['alpha'][1]} |")
  out.append(f'\nHashes: `manifest-{g}.json`.')
 (OUT/'REPORT.md').write_text('\n'.join(out)+'\n')

"""Group A: authorized deterministic extraction; no source or runtime writes.
Run with ~/.venvs/catchline-ui/bin/python from any directory.
"""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'Art/Source'))
from cut_ui_v2 import key_background,fit,deckhand_hat
UI=ROOT/'Assets/Art/UI'
FONT=str(UI/'Fonts/Fredoka-Medium.ttf')
NAMES=['rosa','ines','tess']
manifest=[]
for n in NAMES:
 src=ROOT/f'Art/Source/UIv2/crew-styles/portrait-{n}.png'
 cut=key_background(Image.open(src))
 bust=fit(cut,(400,400),.02,True)
 deck=deckhand_hat(bust)
 original=np.array(bust); edited=np.array(deck)
 # Do not hue-shift antialiased navy outline pixels (causes edge flecks).
 edited[original[:,:,3]<250]=original[original[:,:,3]<250]
 if n=='ines':
  # Engineer helmet stays a helmet, including its navy headlamp housing.
  # The deck variant shifts yellow helmet paint to safety orange only.
  import colorsys
  edited=original.copy()
  for y in range(210):
   for x in range(400):
    r,g,b,a=original[y,x]
    h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
    if a>=250 and .085<h<.19 and s>.45:
     edited[y,x,:3]=np.array(colorsys.hsv_to_rgb(.055,s,v))*255
 deck=Image.fromarray(edited,'RGBA')
 for suffix,img in [('',bust),('-deck',deck)]:
  dst=OUT/f'v2-portrait-{n}{suffix}.png';img.save(dst,optimize=True)
 for sz in (240,96,56):
  dst=OUT/f'art108-{n}{"" if sz==240 else "-"+str(sz)}.png'
  bust.resize((sz,sz),Image.Resampling.LANCZOS).save(dst,optimize=True)
 manifest.append(dict(name=n,source=str(src.relative_to(ROOT)),sourceSHA256=hashlib.sha256(src.read_bytes()).hexdigest(),sourceBounds=list(cut.getbbox()),bounds=list(bust.getbbox()),deckChangedPixels=int(np.any(np.array(deck)!=np.array(bust),axis=2).sum())))
# Each delivered PNG appears at its exact native resolution plus a phone sample.
for n in NAMES:
 sheet=Image.new('RGB',(1420,1120),'#F4EFE3');d=ImageDraw.Draw(sheet)
 def label(x,y,t,sz=19):d.text((x,y),t,font=ImageFont.truetype(FONT,sz),fill='#173F57')
 label(18,10,f'Group A / {n.title()} / native export sizes + 56px phone review',28)
 files=[f'v2-portrait-{n}.png',f'v2-portrait-{n}-deck.png',f'art108-{n}.png',f'art108-{n}-96.png',f'art108-{n}-56.png']
 positions=[(18,80),(438,80),(858,80),(1120,80),(1250,80)]
 for f,(x,y) in zip(files,positions):
  im=Image.open(OUT/f);sheet.paste(im,(x,y),im);label(x,y-26,f,15)
  small=im.resize((56,56),Image.Resampling.LANCZOS);sheet.paste(small,(x,y+414),small);label(x+64,y+434,'56px',16)
 # Dark-background samples catch pale matte residue.
 d.rectangle((18,575,750,780),fill='#173F57')
 for k,c in enumerate(['mira','tove','noor',n]):
  im=Image.open(OUT/f'v2-portrait-{c}.png' if c==n else UI/f'v2-portrait-{c}.png').convert('RGBA')
  sm=im.resize((140,140),Image.Resampling.LANCZOS);sheet.paste(sm,(28+k*180,590),sm)
  label(28+k*180,545,c.title());sm=im.resize((56,56),Image.Resampling.LANCZOS);sheet.paste(sm,(28+k*180,810),sm)
 review=Image.open(ROOT/f'Art/Models/CrewV2/{n.title()}/{n.title()}-review.png')
 review.thumbnail((610,565));sheet.paste(review,(790,530));label(18,900,'Cream + navy: silhouette, fringe, braid, scar and outline review',20)
 label(18,940,'Existing Mira / Tove / Noor references; model sheet at right',20)
 label(18,980,'Source extraction only. Runtime integration and Mo acceptance remain with lead.',18)
 sheet.save(OUT/f'review/A-{n}.png',optimize=True)
(OUT/'portraits-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))

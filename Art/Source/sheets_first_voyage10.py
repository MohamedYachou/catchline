"""Pillow: labelled ART-010 evidence, no runtime/UI asset edits."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/FirstVoyage10'
fontfile=ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'
font=ImageFont.truetype(str(fontfile),24);small=ImageFont.truetype(str(fontfile),19)
cream='#F4EFE3';ink='#173F57'
def panel(image,size):return ImageOps.pad(image.convert('RGB'),size,color=cream)
def open_(name):return Image.open(OUT/name)

# Same source image pixels, camera, scale, lighting, pose and water phase.
sheet=Image.new('RGB',(1440,510),cream);d=ImageDraw.Draw(sheet)
for i,stage in enumerate(('before','after')):
    sheet.paste(open_(stage+'-desktop.png').resize((720,450)),(i*720,60))
    d.text((i*720+20,18),stage.upper()+' / same gameplay camera and lighting',font=font,fill=ink)
sheet.save(OUT/'Before-after-gameplay-camera.png')
crop=(310,65,1000,565)
for stage in ('before','after'):open_(stage+'-desktop.png').crop(crop).save(OUT/(stage+'-close-crop.png'))

# Current capture retains UI; this is labelled evidence, not a fabricated runtime image.
current=open_('Unity-before.jpg').crop((1,29,961,628))
goal=Image.open(ROOT/'Art/Concepts/17-hud-fishing.png')
comparison=Image.new('RGB',(2160,550),cream);d=ImageDraw.Draw(comparison)
for i,(im,title,subtitle) in enumerate([
    (goal,'Goal / supplied fishing concept','Art direction; different composition and UI'),
    (current,'Unity / supplied pre-polish capture','Client crop; UI and environment retained'),
    (open_('after-desktop.png'),'ART-010 / Blender world target','Exact gameplay camera; no UI or scenery; NOT Unity')]):
    comparison.paste(panel(im,(720,450)),(i*720,100))
    d.text((i*720+18,14),title,font=font,fill=ink);d.text((i*720+18,53),subtitle,font=small,fill=ink)
comparison.save(OUT/'Goal-runtime-target-comparison.png')

safe=open_('after-desktop.png').convert('RGBA');overlay=Image.new('RGBA',safe.size)
d=ImageDraw.Draw(overlay)
for bounds,label in [((24,24,400,250),'STATUS / quiet water'),((465,640,975,875),'STRIKE / quiet water')]:
    d.rounded_rectangle(bounds,18,fill=(244,239,227,80),outline=(243,240,220,230),width=3)
    d.text((bounds[0]+14,bounds[1]+12),label,font=small,fill=(23,63,87,255))
Image.alpha_composite(safe,overlay).convert('RGB').save(OUT/'Quiet-area-guide.png')

sheet=Image.new('RGB',(1920,870),cream);d=ImageDraw.Draw(sheet)
variants=[('flat','Flat water / compare contact separation'),('contact','Broad colour + broken contact / stationary'),
          ('rowing','Contact + short wake / rowing only'),('drift-6s','Same contact scene / water phase +6 s')]
for i,(file,title) in enumerate(variants):
    x=(i%2)*960;y=(i//2)*385
    # Crop identical camera views to foreground; no individual reframing or rescaling.
    im=open_('target-'+file+'.png').crop((180,20,780,390)).resize((540,333))
    sheet.paste(im,(x,y+48));d.text((x+16,y+12),title,font=font,fill=ink)
    lines={
      'flat':['Water base #168F9F','Water plane Unity Y = -0.32 m','No contact band or wake','Soft key + cool ambient'],
      'contact':['Broad 0.6 m colour variation','Base #168F9F to #279DA8','Broken 0.04 m contact band','No bright global hull outline'],
      'rowing':['Illustrative speed 0.4–0.6 m/s','Two short spreading ribbons','Trail ~1.4 m; width 0.045 m','Fade out when stationary'],
      'drift-6s':['0.36 × 0.18 m drift / 6 s','24 fps, frame 1 to 145','No wave displacement or glitter','Crew pose fixed between phases']
    }[file]
    for j,line in enumerate(lines):d.text((x+560,y+80+j*48),line,font=small,fill=ink)
d.text((20,790),'LIGHT: warm disk 1100 W / 4.5 m + cool fill 260 W / 6 m; ambient strength 0.45. Standard, exposure 0, gamma 1.',font=font,fill=ink)
d.text((20,830),'Blender reference only. Exact camera: Unity Euler (45,35,0), ortho size 3.2. Full positions, tints and rebuild steps: TARGET.md.',font=small,fill=ink)
sheet.save(OUT/'Lighting-water-contact-target-sheet.png')
print('ART-010 labelled comparisons, close crops, quiet guide and target sheet complete')

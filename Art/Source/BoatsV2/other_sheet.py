from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/BoatsV2/OtherHulls';O.mkdir(exist_ok=True)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26);s=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
im=Image.new('RGB',(1600,2410),'#F4EFE3');d=ImageDraw.Draw(im)
d.text((24,15),'BOAT-REFINE-1 / Other active hulls / review only',font=f,fill='#173F57')
d.text((24,57),'Existing ART108 authoring studies, 23 Oct. Props included; these are not current runtime screenshots.',font=s,fill='#173F57')
notes=[
 ('Propose: two quiet hull strakes, swept rail cap and a softer canopy edge.', 'Protect: hatch, rod sockets, canopy footprint and aft sorting access.'),
 ('Propose: match hull/rail thickness, a broad cabin drip edge and simple timber knees.', 'Protect: central prep worktops, station lanes and cabin dimensions.'),
 ('Propose: consistent hull trim and a calmer rig silhouette, with detail below the rail.', 'Protect: switchable nets/rigs, tip anchors and approved 8.5 x 4.2 m hull.')]
manifest=[]
for i,n in enumerate(['CompactFisherV1','PrepFisherV1','Tier5DeepLines103']):
 y=105+i*760;d.text((24,y),n,font=f,fill='#173F57')
 for j,v in enumerate(['gameplay-camera','top-plan']):
  p=R/f'Art/Models/StationsV1/{n}/{v}.png';pic=Image.open(p).convert('RGB');pic.thumbnail((770,620));im.paste(pic,(15+800*j+(770-pic.width)//2,y+45+(620-pic.height)//2));manifest.append({'image':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 d.text((24,y+674),'Authored gameplay angle',font=s,fill='#173F57');d.text((824,y+674),'Authored top plan / access context',font=s,fill='#173F57')
 d.text((24,y+707),notes[i][0],font=s,fill='#173F57');d.text((24,y+733),notes[i][1],font=s,fill='#173F57')
im.save(O/'review-sheet.png');(O/'provenance.json').write_text(json.dumps(manifest,indent=2));print('Other hulls existing-evidence sheet ready')

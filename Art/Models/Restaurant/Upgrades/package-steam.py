from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
O=Path(__file__).resolve().parent/'Steam';frames=[];rows=[]
for i in range(8):
 p=O/f'steam-{i:02}.png';im=Image.open(p).convert('RGBA');assert im.size==(256,256);a=im.getchannel('A');box=a.getbbox();assert box and box[0]>0 and box[1]>0 and box[2]<256 and box[3]<256;assert 0<a.getextrema()[1]<255
 frames.append(im);rows.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'alpha_bounds_px':box,'alpha_range':a.getextrema()})
sheet=Image.new('RGBA',(2048,256));contact=Image.new('RGB',(1024,552),'#15283b');d=ImageDraw.Draw(contact);gif=[]
for i,im in enumerate(frames):
 sheet.paste(im,(i*256,0));x=(i%4)*256;y=(i//4)*276
 for cy in range(0,256,16):
  for cx in range(0,256,16):d.rectangle((x+cx,y+cy,x+cx+15,y+cy+15),fill='#1d3549' if (cx//16+cy//16)%2 else '#29475c')
 contact.paste(im,(x,y),im);d.text((x+8,y+258),f'Frame {i+1} / 8',fill='white');bg=Image.new('RGBA',im.size,'#19344a');bg.alpha_composite(im);gif.append(bg.convert('RGB'))
sheet.save(O/'steam-sheet.png');contact.save(O/'steam-review.png');gif[0].save(O/'steam-preview.gif',save_all=True,append_images=gif[1:],duration=125,loop=0)
assert len({r['sha256'] for r in rows})==8
(O/'validation.json').write_text(json.dumps({'pass':True,'frames':rows,'sheet_rgba_px':[2048,256],'frame_rects_xywh':[[i*256,0,256,256] for i in range(8)],'no_clipped_alpha':True,'all_frames_unique':True},indent=2));print('STEAM PACKAGE PASS')

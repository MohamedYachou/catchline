"""480x360 transparent kit cards: 6% fit, navy ink, restrained 64-colour post."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageFilter,ImageEnhance,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2];U=D/'ui'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 rows=[]
 for n in ['hull3','hull4']:
  p=U/(n+'-raw.png');im=Image.open(p).convert('RGBA');bbox=im.getbbox();assert bbox
  im=im.crop(bbox);im.thumbnail((418,310),Image.Resampling.LANCZOS)
  rgb=ImageEnhance.Color(ImageEnhance.Contrast(im.convert('RGB')).enhance(1.09)).enhance(1.12)
  rgb=rgb.quantize(colors=64,dither=Image.Dither.NONE).convert('RGB');rgb.putalpha(im.getchannel('A'));im=rgb
  card=Image.new('RGBA',(480,360));pos=((480-im.width)//2,(360-im.height)//2);card.alpha_composite(im,pos)
  a=card.getchannel('A');ink=Image.new('RGBA',card.size,(22,43,53,0));ink.putalpha(a.filter(ImageFilter.MaxFilter(5)));ink.alpha_composite(card)
  target=U/('v2-item-'+n+'.png');ink.save(target)
  rows.append({'file':target.name,'size':list(ink.size),'mode':ink.mode,'sha256':sha(target),'raw_sha256':sha(p),'alpha_bounds':ink.getbbox(),'colours_before_antialias':64,'outer_ink_radius_px':2,'source_render':n+'-render.json'})
 bg=Image.new('RGB',(1040,840),'#E4DFC9');draw=ImageDraw.Draw(bg)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
 files=[R/'Assets/Art/UI/v2-item-skiff.png',R/'Assets/Art/UI/v2-item-compact-fisher.png',U/'v2-item-hull3.png',U/'v2-item-hull4.png']
 labels=['Existing · skiff','Existing · compact fisher','New hull3 · Tier 4 actual FBX','New hull4 · Tier 5 actual FBX']
 for i,(p,label) in enumerate(zip(files,labels)):
  x=20+(i%2)*520;y=16+(i//2)*420;im=Image.open(p).convert('RGBA');assert im.size==(480,360);bg.paste(im,(x,y+35),im);draw.text((x+10,y+8),label,fill='#162B35',font=font)
 comp=U/'comparison.png';bg.save(comp);(U/'post.json').write_text(json.dumps({'cards':rows,'comparison_sha256':sha(comp),'references':[{'file':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in files[:2]]},indent=2)+'\n');print('POST PASS')
if __name__=='__main__':run()

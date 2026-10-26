"""Mechanical inventory, contact layout, nine-slice proofs and receipt checks."""
from pathlib import Path
import json, hashlib, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
CONCEPTS=ROOT.parent/'concepts'
SLICES={
 'v2-sign-plank.png': [110,84,110,80],
 'v2-ticket.png': [250,72,70,70],
 'v2-review-card.png': [40,40,40,40],
 'v2-staff-card.png': [30,28,30,28],
 'v2-stock-card.png': [40,40,40,40],
}
try: FONT=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
except OSError: FONT=ImageFont.load_default()

def expected():
 m=json.loads((ROOT/'expected-assets.json').read_text())
 names=[]
 for key,prefix in [('icons','v2-icon-'),('dishes','v2-dish-'),('busts','v2-bust-'),('items','v2-item-rest-'),('other','')]:
  names += [prefix+n+'.png' for n in m[key].split()]
 return names,m

def aliases():
 a=json.loads((ROOT/'asset-audit.json').read_text()); existing={r['file'] for r in a}
 for target,source in expected()[1]['aliases'].items():
  if not (ROOT/(source+'.png')).exists() or target+'.png' in existing:continue
  shutil.copy2(ROOT/(source+'.png'),ROOT/(target+'.png'))
  row=next(r.copy() for r in a if r['file']==source+'.png')
  row.update(file=target+'.png',method='exact runtime alias of '+source+'.png',opened=False)
  a.append(row)
 (ROOT/'asset-audit.json').write_text(json.dumps(a,indent=2))

def tile(im,size):
 im=im.copy().convert('RGBA');im.thumbnail(size,Image.Resampling.LANCZOS);return im

def contact(name,reference,files):
 files=[n for n in files if (ROOT/n).exists()]
 rows=(len(files)+5)//6
 out=Image.new('RGB',(1440,540+rows*210),'#F4EFE3');d=ImageDraw.Draw(out)
 ref=tile(Image.open(CONCEPTS/reference),(1400,460));out.paste(ref,((1440-ref.width)//2,35),ref)
 d.text((20,8),'Accepted mockup: '+reference+' / delivered candidates below',font=FONT,fill='#173F57')
 for i,n in enumerate(files):
  x=(i%6)*240+10;y=535+(i//6)*210
  im=tile(Image.open(ROOT/n),(220,168));out.paste(im,(x+(220-im.width)//2,y),im)
  d.text((x,y+174),n.replace('v2-',''),font=FONT,fill='#173F57')
 out.save(ROOT/name)

def slice_image(im,border,size):
 l,t,r,b=border;w,h=im.size;ow,oh=size
 assert ow>l+r and oh>t+b
 out=Image.new('RGBA',size)
 sx=[0,l,w-r,w];sy=[0,t,h-b,h];dx=[0,l,ow-r,ow];dy=[0,t,oh-b,oh]
 for y in range(3):
  for x in range(3):
   part=im.crop((sx[x],sy[y],sx[x+1],sy[y+1]))
   part=part.resize((dx[x+1]-dx[x],dy[y+1]-dy[y]),Image.Resampling.LANCZOS)
   out.alpha_composite(part,(dx[x],dy[y]))
 return out

def proof():
 out=Image.new('RGB',(1440,1600),'#E8E0CC');d=ImageDraw.Draw(out)
 d.text((20,12),'9-slice packaging proof / native border pixels; originals and wider/taller forms',font=FONT,fill='#173F57')
 for i,(name,border) in enumerate(SLICES.items()):
  if not (ROOT/name).exists():continue
  im=Image.open(ROOT/name).convert('RGBA');size=(max(im.width+220,sum(border[::2])+20),im.height+100)
  stretched=slice_image(im,border,size)
  y=50+i*305
  d.text((20,y),name+' L/T/R/B '+str(border),font=FONT,fill='#173F57')
  for x,pic in [(20,im),(600,stretched)]:
   pic=tile(pic,(550 if x==20 else 800,260));out.paste(pic,(x,y+28),pic)
 out.save(ROOT/'contact-slice-proof.png')

def audit():
 a=json.loads((ROOT/'asset-audit.json').read_text());names,m=expected();names+= [n+'.png' for n in m['aliases']]
 seen={r['file'] for r in a};issues=[]
 for r in a:
  f=ROOT/r['file'];im=Image.open(f);im.load()
  if im.mode!='RGBA' or list(im.size)!=r['size']:issues.append(r['file']+': mode/size mismatch')
  if hashlib.sha256(f.read_bytes()).hexdigest()!=r['sha256']:issues.append(r['file']+': hash mismatch')
  if not r['opened']:issues.append(r['file']+': not individually opened')
  if not im.getchannel('A').getbbox():issues.append(r['file']+': empty')
  if r['file']!='v2-restaurant-backdrop.png' and im.getchannel('A').getextrema()[0]!=0:issues.append(r['file']+': no transparency')
  r['visibleBoundsAlphaGT8']=list(im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox())
 missing=sorted(set(names)-seen)
 result={'requiredIncludingAliases':len(names),'packaged':len(a),'opened':sum(bool(r['opened']) for r in a),'missing':missing,'issues':issues,'slicesLTRB':SLICES,'explicitSkip':m['skip'],'unityIntegration':'not performed; source art delivery only','pixelIdenticalMockup':'not verified; generated reproductions differ from source painting'}
 (ROOT/'asset-audit.json').write_text(json.dumps(a,indent=2))
 (ROOT/'delivery-audit.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
 return a

if __name__=='__main__':
 aliases();a=audit()
 names=[r['file'] for r in a]
 contact('contact-service.png','ui-service-desktop.png',[n for n in names if 'icon-' in n or 'bust-'in n or n=='v2-mira-wave.png'])
 contact('contact-dishes.png','ui-3-mira-plan.png',[n for n in names if 'dish-'in n or n in ['v2-sign-plank.png','v2-ticket.png','v2-catch-pile.png']])
 contact('contact-arrange.png','ui-1-arrange.png',[n for n in names if 'item-rest-'in n or 'btn-'in n])
 contact('contact-frames.png','ui-5-closing.png',[n for n in names if n not in [r for r in names if any(s in r for s in ['icon-','bust-','dish-','item-rest-','btn-'])]])
 proof()

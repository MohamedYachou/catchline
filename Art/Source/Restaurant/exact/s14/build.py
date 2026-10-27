"""Layered harbour-entry mockup; original harbour canvas preserved outside new entry."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json,hashlib,shutil
P=Path(__file__).resolve().parent;ROOT=next(p for p in P.parents if (p/'Assets').exists());R=P/'provenance';R.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):p.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
sources={
 'button':ROOT/'Assets/Art/UI/v2-btn-secondary.png',
 'facade':Path('C:/Users/momoy/.codex/generated_images/01a17ab4-9da1-77a0-b6b2-cc3b8156a1b1/exec-11fe1757-def6-498a-99cd-f0ba2702315b.png'),
 'badge':ROOT/'Assets/Art/UI/v2-btn-primary.png'}
rects={'button':[36,276,440,146],'facade':[54,282,128,132],'badge':[194,354,252,48]}
entries=[]
for key,source in sources.items():
 shutil.copy2(source,R/(key+'-original.png'))
 im=Image.open(source).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda a:a if a>=8 else 0));crop=im.getbbox();im=im.crop(crop);x,y,w,h=rects[key];im=im.resize((w*3,h*3),Image.Resampling.LANCZOS);im=im.crop(im.getbbox())
 # Tight crop is kept with exactly matched logical placement dimensions.
 if im.size!=(w*3,h*3):im=im.resize((w*3,h*3),Image.Resampling.LANCZOS)
 name='v2-s14-'+('restaurant-icon' if key=='facade' else key);path=P/(name+'.png');im.save(path)
 borders=None if key=='facade' else ([140,100,140,100] if key=='button' else [65,45,65,45])
 entries.append(dict(name=name,file=path.name,screen=14,rect=rects[key],size=list(im.size),borders=borders,border_order='left,bottom,right,top',sha256=sha(path),provenance=dict(source=str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else source.name,sourceSha256=sha(source),sourceAlphaCrop=crop,method='accepted v2 bitmap mechanical crop/resize' if key!='facade' else 'built-in ImageGen painting; alpha8 trim/3x export'),native3xDetailClaim=False,pixelExactClaim=False))
basepath=ROOT/'Art/Concepts/18-hud-harbour.png';base=Image.open(basepath).convert('RGBA');im=base.resize((5760,3240),Image.Resampling.NEAREST)
for i in entries:
 x,y,w,h=i['rect'];im.alpha_composite(Image.open(P/i['file']),(x*3,y*3))
styles=[dict(id='restaurant-name',screen='harbour',text="Mira's",rect=[198,293,242,55],font='Fredoka-Bold',size=49,fill='#173F57',stroke='#F4EFE3',stroke_width=0,shadow_offset=[0,0],shadow_colour='#00000000'),dict(id='service-tonight',screen='harbour',text='Service tonight',rect=[205,360,230,34],font='Fredoka-SemiBold',size=29,fill='#F4EFE3',stroke='#173F57',stroke_width=.6,shadow_offset=[0,1],shadow_colour='#173F5755')]
d=ImageDraw.Draw(im)
for t in styles:
 x,y,w,h=t['rect'];font=ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts'/(t['font']+'.ttf')),round(t['size']*3));sw=round(t['stroke_width']*3);b=d.textbbox((0,0),t['text'],font=font,stroke_width=sw)
 assert b[2]-b[0]<=w*3 and b[3]-b[1]<=h*3
 d.text((x*3-b[0],y*3+(h*3-b[3]+b[1])//2-b[1]),t['text'],font=font,fill=t['fill'],stroke_width=sw,stroke_fill=t['stroke'])
im.save(P/'reconstructed-3x.png');small=im.resize(base.size,Image.Resampling.LANCZOS)
# Copy only the new entry region back: all other original HUD pixels remain byte-for-byte unchanged.
roi=(36,276,476,422);final=base.copy();final.paste(small.crop(roi),roi)
concept=ROOT/'Art/Source/Restaurant/concepts/ui-14-harbour-entry.png';final.convert('RGB').save(concept)
write(P/'manifest.json',entries);write(P/'layout.json',dict(screen=14,canvas=list(base.size),origin='top-left',reference='../../concepts/ui-14-harbour-entry.png',background='../../../../Concepts/18-hud-harbour.png',background_sha256=sha(basepath),placements=[dict(name=i['name'],screen=14,use='restaurant-entry',rect=i['rect'],z=10+k) for k,i in enumerate(entries)],responsiveRule='Anchor below harbour summary, scale group uniformly. 1920x1080 reference; do not reinterpret as844x390. Existing HUD reference is16:9.'))
write(P/'text-styles.json',dict(canvas=list(base.size),styles=styles));write(P/'slices.json',dict(border_order='left,bottom,right,top',sprites=[dict(name=i['name'],borders=i['borders']) for i in entries if i['borders']]))
proof=Image.new('RGB',(1300,850),'#eee7d8');d=ImageDraw.Draw(proof);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
d.text((20,12),'S14: original harbour HUD + restaurant entry (offline art)',font=font,fill='#173f57');proof.paste(final.resize((1280,720)),(10,48));proof.save(P/'context-review.jpg',quality=95)
proof=Image.new('RGB',(1300,540),'#eee7d8');d=ImageDraw.Draw(proof)
for k,i in enumerate(entries):
 sp=Image.open(P/i['file']);sp.thumbnail((600,225));x=20+650*(k%2);y=40+(k//2)*250;proof.paste(sp,(x,y),sp);d.text((x,y-25),i['name']+' / text-free',font=font,fill='#173f57')
proof.save(P/'cuts-review.jpg',quality=95)
measure=final.copy();d=ImageDraw.Draw(measure)
for i in entries+styles:
 x,y,w,h=i['rect'];d.rectangle((x,y,x+w,y+h),outline='#ff00ff',width=2)
measure.crop((20,252,500,445)).resize((1440,579)).convert('RGB').save(P/'text-layout-review.jpg',quality=95)
delta=ImageChops.difference(base.convert('RGB'),final.convert('RGB'));check=delta.copy();ImageDraw.Draw(check).rectangle(roi,fill=0);assert not check.getbbox()
for i in entries:
 sp=Image.open(P/i['file']);assert sp.mode=='RGBA' and sp.getbbox()==(0,0,*sp.size);assert sp.width==i['rect'][2]*3 and sp.height==i['rect'][3]*3
write(P/'audit.json',dict(status='PASS',spriteCount=3,measuredTexts=2,canvas=list(base.size),originalHudPixelsOutsideEntryUnchanged=True,entryRegion=roi,sourceSha256=sha(basepath),conceptSha256=sha(concept),nativeRuntimeVerified=False))
print('S14 PASS:3sprites/2texts,1920x1080; HUD outside new entry unchanged')

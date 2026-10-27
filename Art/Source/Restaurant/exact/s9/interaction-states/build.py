"""Additive S9 states and offline interaction proof; preserve accepted default screen."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil
P=Path(__file__).resolve().parent;D=P.parent;ROOT=next(p for p in P.parents if (p/'Assets').exists());R=P/'provenance';R.mkdir(exist_ok=True)
GEN=Path('C:/Users/momoy/.codex/generated_images/01a17ab4-9da1-77a0-b6b2-cc3b8156a1b1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):p.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
specs=[('chip-drag','exec-4a385b89-0ca2-4aad-946f-b964712a25ab.png',[351,77,159,42],[36,36,36,24]),('slot-target','exec-4efb8bf5-9e15-47dd-a1d2-8d03421aa729.png',[354,88,151,31],[36,24,36,24]),('tooltip','exec-934e53f2-24c5-4ccb-8092-cc7ee4e3b7bc.png',[155,96,290,76],[240,90,60,40])]
items=[]
for key,filename,rect,borders in specs:
 source=GEN/filename;shutil.copy2(source,R/(key+'-generated.png'));im=Image.open(source).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda a:a if a>=8 else 0));crop=im.getbbox();im=im.crop(crop);w,h=rect[2:];im=im.resize((w*3,h*3),Image.Resampling.LANCZOS);im=im.crop(im.getbbox())
 if im.size!=(w*3,h*3):im=im.resize((w*3,h*3),Image.Resampling.LANCZOS)
 path=D/f'v2-s9-{key}.png';im.save(path)
 items.append(dict(name=path.stem,file=path.name,screen=9,rect=rect,size=list(im.size),logicalSize=[w,h],borders=borders,border_order='left,bottom,right,top',sha256=sha(path),sourceAlphaCrop=crop,sourceFile='interaction-states/provenance/'+key+'-generated.png',sourceSha256=sha(source),exportMethod='built-in ImageGen state painting; alpha8trim/3x export; no text baked',native3xDetailClaim=False,pixelExactClaim=False))
items[0]['renderRule']='Replace normal chip visual during drag. Overlay live task label/number/handle; shadow already included. Entire bounds159x42, cream face inset approximately4x3.'
items[1]['renderRule']='Show behind moving chip over legal insertion slot; transparent centre reveals crew row. Hide after drop/cancel.'
items[2]['renderRule']='Show on locked-job press/hover; pointer points down at fixed job. Left slice protects pointer; min logical width120. Clamp group within safe area.'
base=json.loads((P/'baseline-manifest.json').read_text());write(D/'manifest.json',base+items);write(P/'manifest.json',items)
write(P/'layout.json',dict(screen=9,canvas=[844,390],origin='top-left',states=[dict(id='dragging',placements=[dict(name=items[0]['name'],use='dragged-seat-guests',rect=items[0]['rect'],z=100),dict(name=items[1]['name'],use='legal-insertion-target',rect=items[1]['rect'],z=90)]),dict(id='locked-job',placements=[dict(name=items[2]['name'],use='job-explanation',rect=items[2]['rect'],z=100)])],note='State-only sample placements; do not add to static S9 screen.'))
write(P/'slices.json',dict(border_order='left,bottom,right,top',sprites=[dict(name=i['name'],borders=i['borders']) for i in items]))
texts=[dict(id='locked-job-main',screen='crew-priorities',state='locked-job',text='Jobs belong to each card.',rect=[199,108,232,22],font='Fredoka-Bold',size=15,fill='#10263D',stroke='#F4EFE3',stroke_width=0,shadow_offset=[0,0],shadow_colour='#00000000'),dict(id='locked-job-hint',screen='crew-priorities',state='locked-job',text='Drag tasks to reorder.',rect=[199,133,232,20],font='Fredoka-SemiBold',size=14,fill='#173F57',stroke='#F4EFE3',stroke_width=0,shadow_offset=[0,0],shadow_colour='#00000000')]
write(P/'text-styles.json',dict(canvas=[844,390],styles=texts,note='Drag chip uses existing live task label/number/handle from S9; example inherits Seat guests.'))
fontpath=ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
def text(im,t):
 d=ImageDraw.Draw(im);x,y,w,h=t['rect'];f=ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts'/(t.get('font','Fredoka-Bold')+'.ttf')),round(t['size']*3));b=d.textbbox((0,0),t['text'],font=f);assert b[2]-b[0]<=w*3 and b[3]-b[1]<=h*3;d.text((x*3-b[0],y*3+(h*3-b[3]+b[1])//2-b[1]),t['text'],font=f,fill=t['fill'])
original=Image.open(ROOT/'Art/Source/Restaurant/concepts/ui-9-crew-priorities.png').convert('RGBA').resize((2532,1170),Image.Resampling.LANCZOS)
drag=original.copy();slot=Image.open(D/items[1]['file']);drag.alpha_composite(slot,(354*3,88*3))
sp=Image.open(D/items[0]['file']);drag.alpha_composite(sp,(351*3,77*3))
for name,rect in [('number-badge',[360,84,24,24]),('grab-handle',[483,90,12,12])]:
 img=Image.open(D/f'v2-s9-{name}.png');drag.alpha_composite(img.resize((rect[2]*3,rect[3]*3)),(rect[0]*3,rect[1]*3))
text(drag,dict(text='1',rect=[367,87,11,16],size=13,fill='#F4EFE3'));text(drag,dict(text='Seat guests',rect=[391,86,85,18],size=14,fill='#10263D'))
locked=original.copy();locked.alpha_composite(Image.open(D/items[2]['file']),(155*3,96*3));lock=Image.open(D/'v2-s9-job-lock.png');locked.alpha_composite(lock.resize((66,81)),(167*3,113*3))
for t in texts:text(locked,t)
drag.save(P/'drag-context-3x.png');locked.save(P/'locked-context-3x.png')
proof=Image.new('RGB',(1688,445),'#E9E2D2');d=ImageDraw.Draw(proof);f=ImageFont.truetype(str(fontpath),20);d.text((15,7),'Dragging / valid insertion target',font=f,fill='#173F57');d.text((859,7),'Locked fixed job / explanation',font=f,fill='#173F57');proof.paste(drag.resize((844,390)),(0,40));proof.paste(locked.resize((844,390)),(844,40));proof.save(P/'context-review.jpg',quality=95)
proof=Image.new('RGBA',(1300,650),'#E9E2D2');d=ImageDraw.Draw(proof)
for row,i in enumerate(items):
 im=Image.open(D/i['file']);im.thumbnail((1100,160));proof.alpha_composite(im,(20,45+row*205));d.text((20,10+row*205),i['name']+' / text-free',font=f,fill='#173F57')
proof.convert('RGB').save(P/'cuts-review.jpg',quality=95)
proof=Image.new('RGBA',(1700,790),'#EEE7D8');d=ImageDraw.Draw(proof)
for row,i in enumerate(items):
 a=Image.open(D/i['file']);l,b,r,t=i['borders'];sx=[0,l,a.width-r,a.width];sy=[0,t,a.height-b,a.height];d.text((15,row*250+3),i['name'],font=f,fill='#173F57')
 for col,w in enumerate([600,960]):
  h=i['size'][1];out=Image.new('RGBA',(w,h));dx=[0,l,w-r,w];dy=[0,t,h-b,h]
  for yi in range(3):
   for xi in range(3):out.alpha_composite(a.crop((sx[xi],sy[yi],sx[xi+1],sy[yi+1])).resize((dx[xi+1]-dx[xi],dy[yi+1]-dy[yi]),Image.Resampling.LANCZOS),(dx[xi],dy[yi]))
  proof.alpha_composite(out,(15 if col==0 else 700,row*250+35))
proof.convert('RGB').save(P/'slice-proof.jpg',quality=95)
for i in items:
 im=Image.open(D/i['file']);assert im.mode=='RGBA' and im.getbbox()==(0,0,*im.size);assert im.size==tuple(n*3 for n in i['logicalSize'])
for i in base:assert sha(D/i['file'])==i['sha256']
slot=Image.open(D/items[1]['file']);assert slot.getpixel((slot.width//2,slot.height//2))[3]==0
write(P/'audit.json',dict(status='PASS',sprites=3,measuredTexts=2,slices=3,tightRGBA3x=True,slotCentreAlpha=0,acceptedSpriteHashesPreserved=len(base),nativeRuntimeVerified=False))
print('S9 PASS:3sprites/2newtexts/3slices, transparent slot centre, baseline preserved')

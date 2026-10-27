"""Deterministic vector FX and explicitly requested pixel-exact chest cuts.
Accepted CrewFinal source pixels are read only. Outputs are straight-alpha RGBA.
"""
from pathlib import Path
import math, json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg
P=Path(__file__).resolve().parent
F=P.parent/'CrewFinal'
INK='#173F57'; CREAM='#F4EFE3'
rows=[]
def save(name,im):
    im.save(P/(name+'.png'))
    rows.append({'file':name+'.png','size':list(im.size),'mode':im.mode,'sha256':hashlib.sha256((P/(name+'.png')).read_bytes()).hexdigest()})
def svg(name,w,h,body,defs=''):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>'
    (P/'svg'/(name+'.svg')).write_text(s)
    import io
    im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(),output_width=w*3,output_height=h*3))).convert('RGBA').resize((w,h),Image.Resampling.LANCZOS)
    save(name,im)
def rgba(rgb,a):
    x=np.zeros((*a.shape,4),np.uint8);x[:,:,:3]=rgb;x[:,:,3]=np.rint(np.clip(a,0,1)*255).astype(np.uint8);return Image.fromarray(x)
y,x=np.mgrid[:512,:512];r=np.hypot(x-255.5,y-255.5)/248
save('fx-glow',rgba([255,255,255],np.maximum(0,1-r*r)**3*.88))
theta=np.arctan2(y-255.5,x-255.5)
# 12 separate tapered shafts, with a soft angular profile and smooth ends.
a=(np.maximum(0,np.cos(theta*12))**5)*np.clip((r-.12)/.15,0,1)*np.maximum(0,1-r)**1.25*1.3
save('fx-rays',rgba([255,225,156],a))
svg('fx-sparkle',128,128,'<path d="M64 8 Q69 52 77 55 L120 64 Q76 70 73 78 L64 120 Q57 77 50 74 L8 64 Q51 58 55 50Z" fill="url(#s)"/>','<radialGradient id="s"><stop stop-color="#FFE9A3"/><stop offset=".38" stop-color="#FFF7D9"/><stop offset="1" stop-color="white"/></radialGradient>')
# Hollow irregular burst with bold local outline, not global scene outlines.
pts=[]
for i in range(48):
    t=i*math.tau/48;rr=[202,181,225,182][i%4];pts.append((256+math.cos(t)*rr,256+math.sin(t)*rr))
d='M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in pts)+'Z M 256 139 C 322 139 375 190 375 256 C 375 322 322 373 256 373 C 190 373 137 322 137 256 C 137 190 190 139 256 139 Z'
svg('fx-burst',512,512,f'<path d="{d}" fill="{CREAM}" fill-rule="evenodd" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
for i,body in enumerate(['<path d="M25 9 L42 13 L35 55 L18 51Z"/>','<path d="M15 15 L49 15 L49 49 L15 49Z"/>','<path d="M14 15 C51 4 57 29 33 38 C15 44 26 55 47 49 L48 57 C13 64 2 35 29 29 C44 25 40 16 18 24Z"/>','<path d="M32 10 L55 51 L9 51Z"/>'],1):svg('fx-confetti-'+str(i),64,64,'<g fill="white">'+body+'</g>')
y,x=np.mgrid[:32,:128];a=np.exp(-((y-15.5)/5)**2)*np.sin(np.pi*np.clip((x-3)/121,0,1))**1.6
save('fx-coin-trail',rgba([255,237,180],a*.9))
svg('fx-levelup-arrow',256,256,f'<path d="M128 19 Q132 19 138 25 L227 111 Q236 121 224 124 L171 124 L171 224 Q171 235 160 235 L96 235 Q85 235 85 224 L85 124 L32 124 Q20 122 29 112 L118 25 Q124 19 128 19Z" fill="url(#g)" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/><path d="M51 109 L128 35 L203 109 M100 134 L100 219" fill="none" stroke="#FFF0A6" stroke-width="8" stroke-linecap="round"/>','<linearGradient id="g" x2=".3" y2="1"><stop stop-color="#FFDE70"/><stop offset=".55" stop-color="#E6AD38"/><stop offset="1" stop-color="#C78420"/></linearGradient>')
svg('fx-rank-ribbon',640,160,f'<g stroke="{INK}" stroke-width="7" stroke-linejoin="round"><path d="M28 42 L142 42 L142 143 L28 143 L55 93Z M612 42 L498 42 L498 143 L612 143 L585 93Z" fill="#D1AF76"/><path d="M112 113 L142 142 L142 109 M528 113 L498 142 L498 109" fill="#8C5A36"/><path d="M111 20 Q320 8 529 20 L529 115 Q320 103 111 115Z" fill="{CREAM}"/></g><path d="M128 35 Q320 25 512 35" fill="none" stroke="#FFFCF3" stroke-width="6" stroke-linecap="round"/>')
y,x=np.mgrid[:128,:512];r=((x-255.5)/241)**2+((y-63.5)/52)**2
save('fx-chest-shadow',rgba([18,33,43],np.maximum(0,1-r)**2*.38))
(P/'review').mkdir(exist_ok=True)
checks=[]
# Seam points follow the navy gap; the hanging latch follows the moving lid.
config={
'crate':([(64,212),(177,237),(180,275),(192,288),(207,285),(214,249),(322,274),(446,211)],[(79,210),(207,164),(423,205),(319,268)]),
'sea':([(49,219),(179,254),(181,298),(195,314),(211,312),(221,265),(329,301),(477,224)],[(65,215),(197,157),(454,213),(330,292)]),
'captain':([(43,230),(168,270),(169,310),(179,332),(195,341),(215,327),(220,286),(330,318),(480,242)],[(57,225),(190,168),(459,229),(330,307)])}
for tier,(seam,inside) in config.items():
    orig=Image.open(F/f'v2-chest-{tier}-closed.png').convert('RGBA');z=np.array(orig)
    mask=Image.new('L',(512,512));ImageDraw.Draw(mask).polygon([(0,0),(511,0),(511,seam[-1][1])]+list(reversed(seam))+[(0,seam[0][1])],fill=255)
    cut=np.array(mask)>0
    lid=z.copy();lid[~cut,3]=0
    base=z.copy();base[cut,3]=0
    fill=Image.new('L',(512,512));ImageDraw.Draw(fill).polygon(inside,fill=255)
    # Accepted PNG interiors are mostly alpha 251/252, not opaque. Solve
    # straight-alpha source-over instead of silently flattening their alpha.
    wanted=((np.array(fill)>0) | ((yy_grid:=np.indices((512,512))[0])>np.interp(np.indices((512,512))[1],[seam[0][0],seam[-1][0]],[seam[0][1],seam[-1][1]])))&cut&(z[:,:,3]>=240)
    yy,xx=np.mgrid[:512,:512];wood=np.zeros_like(z);v=np.clip((yy-150)/170,0,1)
    for c,(top,bot) in enumerate(zip([66,42,28],[36,25,21])):wood[:,:,c]=top*(1-v)+bot*v
    unresolved=wanted.copy();hidden=np.zeros((512,512),bool)
    A=z[:,:,3].astype(float)/255
    # Largest solvable coverage wins. All accepted channels must recompose
    # exactly under Pillow/Unity's standard straight-alpha source-over.
    for ab in [255,240,220,200,180,160,144,128,112,96,80,64,48,32,16,8,4,2,1]:
        B=ab/255
        al=np.clip(np.rint(np.divide(A-B,1-B,out=np.ones_like(A),where=abs(1-B)>1e-9)*255),0,255)
        if ab==255:al[:]=255
        L=al/255
        numerator=z[:,:,:3].astype(float)*A[:,:,None]-wood[:,:,:3]*B*(1-L[:,:,None])
        rgb=np.rint(np.divide(numerator,L[:,:,None],out=np.zeros_like(numerator),where=L[:,:,None]>0))
        valid=unresolved & np.all((rgb>=0)&(rgb<=255),axis=2)
        trial_l=lid.copy();trial_b=base.copy()
        trial_l[valid,:3]=rgb[valid].astype(np.uint8);trial_l[valid,3]=al[valid].astype(np.uint8)
        trial_b[valid,:3]=wood[valid,:3];trial_b[valid,3]=ab
        comp=np.array(Image.alpha_composite(Image.fromarray(trial_b),Image.fromarray(trial_l)))
        ok=valid & np.all(comp==z,axis=2)
        lid[ok]=trial_l[ok];base[ok]=trial_b[ok];hidden|=ok;unresolved[ok]=False
    assert hidden.sum()>10000,(tier,hidden.sum())
    interior=wood.copy()
    # Rebuild the body behind the hanging latch from adjacent same-face wood.
    # The upper plane stays dark; a dark latch-shaped tongue would look false.
    edge_y=np.interp(xx,[seam[0][0],seam[-1][0]],[seam[0][1],seam[-1][1]])
    front=wanted & (yy>edge_y+4) & (np.array(fill)==0)
    dx,dy={'crate':(48,10),'sea':(52,16),'captain':(55,20)}[tier]
    interior[front,:3]=z[np.minimum(511,yy[front]+dy),np.minimum(511,xx[front]+dx),:3]
    interior[:,:,3]=np.where(wanted,255,0).astype(np.uint8)
    save(f'v2-chest-{tier}-interior',Image.fromarray(interior))
    b=Image.fromarray(base);l=Image.fromarray(lid);save(f'v2-chest-{tier}-base',b);save(f'v2-chest-{tier}-lid',l)
    composite=Image.alpha_composite(b,l);delta=np.abs(np.array(composite).astype(int)-z.astype(int));assert delta.max()==0,(tier,delta.max())
    composite.save(P/'review'/f'{tier}-recomposite.png')
    Image.fromarray(delta.astype(np.uint8),'RGBA').save(P/'review'/f'{tier}-diff.png')
    sheet=Image.new('RGB',(1536,580),CREAM);draw=ImageDraw.Draw(sheet)
    for j,(label,im) in enumerate([('ACCEPTED original',orig),('BASE + LID: exact match',composite),('RGBA DIFF: zero',rgba([0,0,0],np.max(delta,axis=2)/255))]):
        sheet.paste(im,(512*j,35),im);draw.text((512*j+12,10),label,fill=INK)
    sheet.save(P/'review'/f'{tier}-diff-review.png')
    checks.append({'tier':tier,'max_rgba_error':int(delta.max()),'mismatched_pixels':int(np.any(delta,axis=2).sum()),'hidden_dark_wood_pixels':int(hidden.sum()),'unfilled_target_pixels':int(unresolved.sum()),'hidden_alpha_min':int(base[hidden,3].min()),'seam':seam})
(P/'chest-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
# Native-size effects and small samples on each pinned review background.
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
names=[r['file'] for r in rows]
for bg,label,fg in [(CREAM,'cream',INK),(INK,'navy',CREAM)]:
    sheet=Image.new('RGB',(1500,55+310*math.ceil(len(names)/3)),bg);draw=ImageDraw.Draw(sheet)
    draw.text((24,16),'CREW-FX-ART-1 | static layers | '+label,font=font,fill=fg)
    for i,name in enumerate(names):
        col=i%3;row=i//3;px=col*500;py=55+row*310
        im=Image.open(P/name);im.thumbnail((430,245),Image.Resampling.LANCZOS)
        sheet.paste(im,(px+(500-im.width)//2,py),im)
        draw.text((px+15,py+251),name,font=font,fill=fg)
        small=Image.open(P/name);small.thumbnail((64,48),Image.Resampling.LANCZOS);sheet.paste(small,(px+400,py+251),small)
    sheet.save(P/'review'/f'contact-{label}.png')
cream=Image.open(P/'review/contact-cream.png');navy=Image.open(P/'review/contact-navy.png')
contact=Image.new('RGB',(3000,cream.height));contact.paste(cream,(0,0));contact.paste(navy,(1500,0));contact.save(P/'review/contact.png')
# Show the separated base and lifted lid without claiming a finished animation.
sheet=Image.new('RGB',(1536,580),CREAM);draw=ImageDraw.Draw(sheet)
for j,tier in enumerate(config):
    b=Image.open(P/f'v2-chest-{tier}-base.png');l=Image.open(P/f'v2-chest-{tier}-lid.png')
    b=Image.alpha_composite(b,Image.open(P/f'v2-chest-{tier}-interior.png'))
    sheet.paste(b,(j*512,65),b);sheet.paste(l,(j*512,-20),l);draw.text((j*512+15,550),tier+' / lifted + optional opaque interior overlay',fill=INK,font=font)
sheet.save(P/'review/lifted-layers.png')
for row in rows:
    im=Image.open(P/row['file']);assert im.mode=='RGBA';assert im.getextrema()[3][0]==0
(P/'manifest-A.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS',len(rows),'RGBA sprites;',checks)

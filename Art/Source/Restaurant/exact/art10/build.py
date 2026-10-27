"""ART-10 packaging only. Run from project root with uv run --with pillow python <this>."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT=Path(__file__).resolve().parents[5]
E=ROOT/'Art/Source/Restaurant/exact'
OUT=E/'art10'
FONT=ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
R=Image.Resampling.LANCZOS
def write(name,data): (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def im(p): return Image.open(p).convert('RGBA')
def crop(p):
    a=im(p); mask=a.getchannel('A').point(lambda x:0 if x<8 else x)
    a.putalpha(mask);return a.crop(mask.getbbox())
def label(canvas,xy,s,size=14,fill='#173F57'):
    ImageDraw.Draw(canvas).text(xy,s,font=ImageFont.truetype(str(FONT),size),fill=fill)
def sliced(a,size,borders):
    l,b,r,t=borders;w,h=a.size;W,H=size
    assert W>l+r and H>t+b
    out=Image.new('RGBA',size)
    xx=[0,l,w-r,w];yy=[0,t,h-b,h]
    XX=[0,l,W-r,W];YY=[0,t,H-b,H]
    for j in range(3):
        for i in range(3):
            part=a.crop((xx[i],yy[j],xx[i+1],yy[j+1]))
            out.alpha_composite(part.resize((XX[i+1]-XX[i],YY[j+1]-YY[j]),R),(XX[i],YY[j]))
    return out
def save_sprite(a,path):
    a.save(E/path)
    assert a.getchannel('A').getbbox()==(0,0,*a.size),str(path)
    return {'name':Path(path).stem,'file':str(path).replace('\\','/'),'size':list(a.size),
            'logicalSize':[x/3 for x in a.size],'sha256':sha(E/path),'borders':None,
            'native3xDetailClaim':False,'method':'Built-in ImageGen; alpha<8 clean/crop, Lanczos packaging to 3x'}
manifest=[]
glyph=crop(OUT/'provenance/swap.png').resize((39,39),R)
# Brightened duplicate is an interaction tint of the same source, not a new drawing.
selected=ImageEnhance.Brightness(glyph).enhance(1.22)
manifest.append(save_sprite(glyph,Path('s9/v2-s9-swap-glyph.png')))
manifest.append(save_sprite(selected,Path('s9/v2-s9-swap-glyph-selected.png')))
manifest[-1]['method']+='; RGB x1.22 selected-state tint, alpha unchanged'
old=im(E/'s9/v2-s9-grab-handle.png')
chip=im(E/'s9/v2-s9-task-chip.png').resize((453,93),R)
lifted=im(E/'s9/v2-s9-chip-drag.png').resize((453,93),R)
sheet=Image.new('RGB',(844,250),'#E5DFD0')
for n,(title,base,g) in enumerate([('Previous handle',chip,old),('Swap / idle',chip,glyph),('Swap / selected',lifted,selected)]):
    y=35+n*65; label(sheet,(20,y-22),title,13)
    c=base.copy();label(c,(24,17),'1',39);label(c,(78,17),'Serve',39)
    c.alpha_composite(g,(399,27));sheet.paste(c.resize((151,31),R),(220,y),c.resize((151,31),R))
    large=c.resize((453,93),Image.Resampling.NEAREST)
    # Right column is a labelled 2x crop of the glyph for inspection.
    sheet.paste(g.resize((52,52),Image.Resampling.NEAREST),(460,y-8),g.resize((52,52),Image.Resampling.NEAREST))
label(sheet,(540,30),'Left: actual-size chips',13);label(sheet,(540,51),'Right: glyph enlarged 4x',13)
sheet.save(OUT/'swap-actual-size.jpg',quality=95)
layout=json.loads((E/'s9/layout.json').read_text())
swaps=[dict(p,name='v2-s9-swap-glyph') for p in layout['placements'] if p['name']=='v2-s9-grab-handle']
write('swap-layout.json',{'canvas':[844,390],'origin':'top-left','placements':swaps,
    'selectedState':'Replace with v2-s9-swap-glyph-selected at the identical rect; use the existing selected/lifted chip backing. Tap first chip then second to swap. No drag behavior.'})

def bubble_pack():
    bubble=crop(OUT/'provenance/bubble.png').resize((960,186),R)
    entry=save_sprite(bubble,Path('s2-call/v2-s2-call-bubble-2line.png'))
    entry.update(borders=[60,45,120,45],border_order='left,bottom,right,top')
    manifest.append(entry)
    return bubble

TEXT='The coffee station is broken. Can you help with repairs?'
CASES=[TEXT,"We're out of grilled fish. Offer soup instead?",'A birthday table! Let us make their evening special.',
       'Our last guests are leaving. Time to close up!']
fits=[]
styles=[]
screens=[]
def text_lines(text,size,width):
    font=ImageFont.truetype(str(FONT),size*3)
    lines=['']
    for word in text.split():
        test=(lines[-1]+' '+word).strip()
        if font.getlength(test)>width*3 and lines[-1]:lines.append(word)
        else:lines[-1]=test
    return font,lines
def draw_lines(canvas,rect,text,size,lineheight,colour='#173F57',align='left'):
    x,y,w,h=rect;font,lines=text_lines(text,size,w)
    heights=[font.getbbox(line)[3]-font.getbbox(line)[1] for line in lines]
    total=(len(lines)-1)*lineheight*3+max(heights)
    top=y*3+(h*3-total)/2
    boxes=[]
    for j,line in enumerate(lines):
        width=font.getlength(line);xx=x*3 if align=='left' else x*3+(w*3-width)/2
        yy=top+j*lineheight*3
        ImageDraw.Draw(canvas).text((xx,yy),line,font=font,fill=colour,anchor='lt')
        boxes.append([round(xx/3,2),round(yy/3,2),round(width/3,2),round(heights[j]/3,2)])
    record={'text':text,'rect':rect,'size':size,'lineHeight':lineheight,'lines':lines,'inkBoxes':boxes,
            'PASS':len(lines)<=2 and total<=h*3 and all(font.getlength(s)<=w*3 for s in lines)}
    fits.append(record);assert record['PASS'],record
    return record

def call_proofs(bubble):
    for screen,canvas,rect,textrect,size,lh in [
        ('phone',[844,390],[190,50,320,62],[207,63,278,36],14,18),
        ('desktop',[1440,900],[444,86,430,76],[465,103,370,44],18,22)]:
        # Accepted existing call reconstruction supplies unchanged header/Mira/context.
        base=im(E/f's2-call/{screen}-reconstructed-3x.png').resize(tuple(v*3 for v in canvas),R)
        # Restore original world behind the OLD bubble first, including its tail.
        # Otherwise its old centre-tail remains visible beside the taller tail.
        bg='ui-2-service.png' if screen=='phone' else 'ui-service-desktop.png'
        world=im(E.parent/'concepts'/bg).resize(tuple(v*3 for v in canvas),Image.Resampling.NEAREST)
        ox,oy,ow,oh=[190,50,320,44] if screen=='phone' else [444,86,430,54]
        bounds=(ox*3,oy*3,(ox+ow)*3,(oy+oh)*3)
        base.paste(world.crop(bounds),(ox*3,oy*3))
        x,y,w,h=rect; resized=sliced(bubble,(w*3,h*3),[60,45,120,45])
        base.alpha_composite(resized,(x*3,y*3))
        draw_lines(base,textrect,TEXT,size,lh)
        base.save(OUT/f'call-{screen}-reconstructed-3x.png')
        actual=base.resize(tuple(canvas),R).convert('RGB')
        actual.save(OUT/f'call-{screen}-actual-size.jpg',quality=95)
        marked=actual.copy();d=ImageDraw.Draw(marked);d.rectangle((x,y,x+w-1,y+h-1),outline='#E36A35',width=1)
        tx,ty,tw,th=textrect;d.rectangle((tx,ty,tx+tw-1,ty+th-1),outline='#168F9F',width=1)
        marked.save(OUT/f'call-{screen}-measured.jpg',quality=95)
        screens.append({'screen':screen,'canvas':canvas,'origin':'top-left','placements':[
            {'name':'v2-s2-call-bubble-2line','use':'long-call','rect':rect,'z':20}],
            'unchangedHostRect':[511,47,38,52] if screen=='phone' else [879,80,49,67],
            'textRect':textrect})
        styles.append({'id':'mira-call-2line','screen':screen,'rect':textrect,'text':TEXT,
            'font':'Fredoka-Bold','weight':700,'size':size,'fill':'#173F57','align':'left',
            'vertical_align':'middle','wrap':True,'maxLines':2,'lineHeight':lh})
        for sample in CASES:
            test=Image.new('RGBA',tuple(v*3 for v in canvas))
            fit=draw_lines(test,textrect,sample,size,lh);fit['screen']=screen
    write('layout.json',{'screens':screens,'notes':'Long-line state only. Original one-line bubble remains available. Phone panel extends to y112, desktop to y162. Keep supplied host and header; avoid spawning world marker over this reserved HUD region.'})
    write('text-styles.json',{'styles':styles,'notes':'Labels live. If a localized line exceeds two lines, use coach card or split message; do not shrink type.'})
    write('text-fit.json',fits)
    # Visible nine-slice stress tests at phone, desktop and a narrower safe use.
    stress=Image.new('RGB',(1000,350),'#E5DFD0')
    for y,(w,h) in zip([30,130,240],[(320,62),(430,76),(260,62)]):
        patch=sliced(bubble,(w*3,h*3),[60,45,120,45]).resize((w,h),R)
        stress.paste(patch,(20,y),patch);label(stress,(500,y+10),f'{w} x {h}; fixed corners + tail column',14)
    stress.save(OUT/'call-slice-review.jpg',quality=95)

def badge_proofs():
    badge=im(E/'badges/v2-hud-count-badge.png')
    sheet=Image.new('RGB',(844,220),'#E5DFD0')
    measurements=[]
    for n,text in enumerate(['10','99']):
        x=30+n*160;tile=badge.copy()
        fit=draw_lines(tile,[3,2,24,18],text,14,16,'#FFF4DC','center')
        measurements.append(dict(fit,badgeSize=[30,22],innerInset=[3,2]))
        actual=tile.resize((30,22),R)
        sheet.paste(actual,(x,60),actual);label(sheet,(x,30),text+' / actual',13)
        big=tile.resize((120,88),Image.Resampling.NEAREST)
        sheet.paste(big,(x,110),big)
    label(sheet,(400,45),'Original badge, unchanged 30 x 22',16)
    label(sheet,(400,72),'Fredoka Bold 14, live centred numbers',14)
    label(sheet,(400,100),'Top: actual size. Below: 4x inspection.',13)
    sheet.save(E/'badges/art10-two-digit-actual-size.jpg',quality=95)
    write('badge-text-fit.json',measurements)

def audit():
    baseline=json.loads((OUT/'baseline.json').read_text())
    changed=[p for p,h in baseline.items() if sha(Path(p))!=h]
    assert not changed,changed
    checks=[]
    for s in manifest:
        p=E/s['file'];a=im(p)
        check={'file':s['file'],'size':a.size,'mode':a.mode,'alphaBBox':a.getchannel('A').getbbox(),
               'PASS':a.size==tuple(s['size']) and a.getchannel('A').getbbox()==(0,0,*a.size)}
        assert check['PASS'];checks.append(check)
    assert len(swaps)==18
    assert glyph.getchannel('A').tobytes()==selected.getchannel('A').tobytes()
    outputs=[p for p in OUT.rglob('*') if p.is_file() and p.suffix in ['.png','.jpg']]
    decoded=[]
    for p in outputs:
        with Image.open(p) as a:a.load();decoded.append(str(p.relative_to(OUT)))
    write('audit.json',{'PASS':True,'preservedExistingPNGCount':len(baseline),'changedExisting':changed,
        'sprites':checks,'swapPlacements':18,'selectedAlphaIdentical':True,'decodedOutputs':decoded,
        'hashes':{str(p.relative_to(OUT)):sha(p) for p in outputs},
        'externalDeliverables':{str(p.relative_to(E)):sha(p) for p in [E/s['file'] for s in manifest]+[E/'badges/art10-two-digit-actual-size.jpg']},
        'nativeImportVerified':False})

if __name__=='__main__':
    bubble=bubble_pack()
    write('manifest.json',manifest)
    call_proofs(bubble)
    badge_proofs()
    for folder,entries in [('s9',manifest[:2]),('s2-call',manifest[2:])]:
        (E/folder/'art10-manifest.json').write_text(json.dumps([
            dict(e,file=Path(e['file']).name) for e in entries],indent=2)+'\n')
    (E/'s9/art10-layout.json').write_text((OUT/'swap-layout.json').read_text())
    for name in ['layout.json','text-styles.json']:
        (E/'s2-call'/('art10-'+name)).write_text((OUT/name).read_text())
    audit()
    print('PASS: 3 sprites, 18 placements, two-device wrapped text + 10/99, preservation audit')

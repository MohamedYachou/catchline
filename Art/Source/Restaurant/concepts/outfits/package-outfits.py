"""Mechanical packaging of accepted painted art; no character painting."""
from pathlib import Path
import json, hashlib, shutil
from PIL import Image, ImageDraw, ImageFont, ImageOps

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
ART=ROOT/'Art/Source/Restaurant'
IDS=['mira','dirk','ana','sam','ines','olaf']
JOBS=['Host','Cook','Waiter','Waiter','Barista','Handyman']
FONT='C:/Windows/Fonts/arial.ttf'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n): return ImageFont.truetype(FONT,n)
def tight(im): return im.crop(im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox())
def paint_on(board,im,box):
    im=im.copy(); im.thumbnail((box[2],box[3]),Image.Resampling.LANCZOS)
    board.paste(im,(box[0]+(box[2]-im.width)//2,box[1]+(box[3]-im.height)//2),im)
def main():
    records=[]
    board=Image.new('RGB',(3500,1200),'#f4efe3'); d=ImageDraw.Draw(board)
    d.text((35,25),'MIRA\u2019S / CLASSIC RESTAURANT OUTFITS',font=font(44),fill='#173f57')
    d.text((35,83),'Front references / navy, teal, cream / gold tailoring reserved for the host',font=font(25),fill='#173f57')
    contact=Image.new('RGB',(1120,620),'#f4efe3'); cd=ImageDraw.Draw(contact)
    cd.text((20,12),'Restaurant busts / actual UI sizes (1x) + deck identity',font=font(23),fill='#173f57')
    for i,(id,job) in enumerate(zip(IDS,JOBS)):
        stem='mira-d' if id=='mira' else id
        front=ART/f'clothes/2d/{stem}-front.png'
        bustpath=ART/f'clothes/2d/{stem}-bust.png'
        body=tight(Image.open(front).convert('RGBA'))
        body.save(OUT/f'{id}-front.png')
        x=i*500
        d.text((x+25,145),f'{id.title()} / {job}',font=font(27),fill='#173f57')
        paint_on(board,body,(x+10,220,480,700))
        source=tight(Image.open(bustpath).convert('RGBA'))
        ref=Image.open(ART/f'exact/s9/v2-s9-bust-{id}.png')
        # S9 keeps incumbent exact pixel dimensions; old cuts are already 3x.
        # Preserve the entire approved bust (including Dirk's tall toque and
        # chin) within the incumbent frame. Never flatten or clip the face.
        s9crop=(0,0,*source.size)
        contained=ImageOps.contain(source,ref.size,Image.Resampling.LANCZOS)
        s9=Image.new('RGBA',ref.size)
        s9.alpha_composite(contained,((ref.width-contained.width)//2,ref.height-contained.height))
        s9trim=s9.getchannel('A').getbbox()
        s9=s9.crop(s9trim)
        s9=s9.resize(tuple(round(v/3)*3 for v in s9.size),Image.Resampling.LANCZOS)
        name=f'v2-s9-bust-{id}-rest'; s9.save(OUT/f'{name}.png')
        records.append(dict(name=name,file=name+'.png',crew=id,role=job,size=s9.size,logicalSize=[v/3 for v in s9.size],scale=3,source=str(bustpath.relative_to(ROOT)),sourceSize=source.size,sourceBustCrop=s9crop,untrimmedCanvas=ref.size,trimInCanvas=s9trim,method='aspect-preserving contain entire approved bust in incumbent S9 3x canvas, trim transparent margins; trim offset preserves placement',native3xDetailClaim=False))
        # Rail source incumbent has a 400px square canvas. A centered square crop
        # preserves head/neck/shoulder framing without stretching the face.
        crop=(0,0,*source.size)
        contained=ImageOps.contain(source,(1200,1200),Image.Resampling.LANCZOS)
        square=Image.new('RGBA',(1200,1200))
        square.alpha_composite(contained,((1200-contained.width)//2,1200-contained.height))
        trim=square.getchannel('A').getbbox()
        rail=square.crop(trim)
        rail=rail.resize(tuple(round(v/3)*3 for v in rail.size),Image.Resampling.LANCZOS)
        name=f'v2-portrait-{id}-rest'; rail.save(OUT/f'{name}.png')
        records.append(dict(name=name,file=name+'.png',crew=id,role=job,size=rail.size,logicalSize=[v/3 for v in rail.size],scale=3,source=str(bustpath.relative_to(ROOT)),sourceSize=source.size,sourceBustCrop=crop,untrimmedCanvas=[1200,1200],trimInCanvas=trim,method='aspect-preserving contain entire approved bust in 3x incumbent400 canvas, trim transparent canvas; use trim offset for framing',native3xDetailClaim=False))
        cx=20+i*183
        cd.text((cx,58),id.title(),font=font(19),fill='#173f57')
        old=Image.open(ROOT/f'Assets/Art/UI/v2-portrait-{id}-deck.png').convert('RGBA')
        paint_on(contact,old,(cx,92,90,90))
        cd.text((cx,188),'Deck 90px',font=font(13),fill='#173f57')
        paint_on(contact,rail,(cx,224,90,90))
        cd.text((cx,320),'Rail 90px',font=font(13),fill='#173f57')
        mini=s9.resize((s9.width//3,s9.height//3),Image.Resampling.LANCZOS)
        contact.paste(mini,(cx,365),mini)
        cd.text((cx,430),f'S9 {mini.width}x{mini.height}',font=font(13),fill='#173f57')
    dishwasher=tight(Image.open(OUT/'provenance/dirk-dishwasher-original.png').convert('RGBA'))
    dishwasher.save(OUT/'dirk-dishwasher-front.png')
    d.text((3025,145),'Dishwasher',font=font(27),fill='#173f57')
    paint_on(board,dishwasher,(3010,220,480,700))
    d.text((3025,990),'Dirk task variant',font=font(22),fill='#173f57')
    board.save(OUT/'outfit-sheet.jpg',quality=95)
    contact.save(OUT/'contact-actual-size.jpg',quality=95)
    for rec in records:
        im=Image.open(OUT/rec['file']); rec['alphaBounds']=im.getchannel('A').getbbox(); rec['sha256']=sha(OUT/rec['file'])
        assert rec['alphaBounds']==(0,0,*im.size),rec
    (OUT/'manifest.json').write_text(json.dumps(records,indent=2))
    originals={r['name']:r for r in json.loads((ART/'exact/s9/manifest.json').read_text())}
    placements=[]
    for r in records:
        if not r['name'].startswith('v2-s9-'):continue
        old=originals[f"v2-s9-bust-{r['crew']}"]
        x,y,w,h=old['rect'];tx,ty,_,_=r['trimInCanvas']
        placements.append({'name':r['name'],'screen':9,'replaces':old['name'],'incumbentFrame':[x,y,w,h],'trimmedRect':[x+tx/3,y+ty/3,*r['logicalSize']],'note':'draw trimmed rect inside same old frame, or reconstruct canvas using manifest trimInCanvas; do not stretch tight export back across old width'})
    (OUT/'bust-layout.json').write_text(json.dumps({'canvas':[844,390],'origin':'top-left','placements':placements,'rail':'400 logical square incumbent canvas, trim offsets in manifest; actual rail slots scale that canvas to their own UI size.'},indent=2))
    print(json.dumps({'busts':len(records),'sheet':board.size,'preservedSources':'read-only; independent audit pending'}))
if __name__=='__main__': main()

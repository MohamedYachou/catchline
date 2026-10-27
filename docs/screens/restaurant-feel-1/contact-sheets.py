"""Build review sheets from actual native framebuffer frames; no scene or image content changes."""
from pathlib import Path
from PIL import Image, ImageDraw
import re, math, json
root=Path(__file__).resolve().parent
for size in ('1440x900','844x390'):
    for action in ('seating','leaving','serving'):
        folder=root/size/action
        frames=sorted(folder.glob('*.png'))
        if not frames: continue
        texts=[p.with_suffix('.txt').read_text() for p in frames]
        group=re.search(r'group=(\d+)',texts[0]).group(1)
        ids=re.search(r'^group='+group+r' .* guests=([\d,]+)',texts[0],re.M).group(1).split(',')
        names=['Guest '+i for i in ids]+(['Staff ana'] if action=='serving' else [])
        points=[]
        for text in texts:
            for name in names:
                m=re.search(r'actor='+name+r' active=True .* screen=([\d.-]+),([\d.-]+)',text)
                if m: points.append(tuple(map(float,m.groups())))
        w,h=Image.open(frames[0]).size
        box=(max(0,int(min(p[0] for p in points)-100)),max(0,int(min(p[1] for p in points)-180)),min(w,int(max(p[0] for p in points)+100)),min(h,int(max(p[1] for p in points)+60)))
        for part,start in enumerate(range(0,len(frames),24),1):
            subset=frames[start:start+24];cw,ch=440,330;sheet=Image.new('RGB',(cw*4,ch*math.ceil(len(subset)/4)),(14,24,31));draw=ImageDraw.Draw(sheet)
            for n,p in enumerate(subset):
                im=Image.open(p).convert('RGB').crop(box);im.thumbnail((cw-8,ch-44))
                x=(n%4)*cw+(cw-im.width)//2;y=(n//4)*ch+25;sheet.paste(im,(x,y))
                t=p.with_suffix('.txt').read_text();stamp=re.search(r'strip=([\d.]+)',t).group(1);phase=re.search(r'^group='+group+r' phase=(\w+)',t,re.M).group(1)
                draw.text(((n%4)*cw+8,(n//4)*ch+6),f'{action} group {group} | {stamp}s | {phase}',fill=(232,225,202))
                draw.text(((n%4)*cw+8,(n//4)*ch+ch-15),f'{size}/{action}/{p.name} | actual framebuffer crop',fill=(146,175,180))
            sheet.save(root/f'strip-{action}-{size}-{part:02}.png')
        (folder/'crop.json').write_text(json.dumps({'group':group,'actors':names,'box':box,'frames':len(frames),'interval':.1},indent=2))

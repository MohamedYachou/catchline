from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import json,hashlib,textwrap
W=Path(__file__).resolve().parent;O=W.parent;R=W.parents[4]
rows=json.loads((W/'roster.json').read_text());roles={'sam':'Deckhand','dirk':'Fisher','kofi':'Fisher','mats':'Deckhand','olaf':'Engineer','pim':'Fisher'}
def font(s,b=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if b else '')+'.ttf',s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cream='#F3EFE5';ink='#193E50';muted='#526570'
canvas=Image.new('RGB',(1600,140+6*400+95),cream);d=ImageDraw.Draw(canvas)
d.text((40,24),'CATCHLINE / QUATERNIUS CREW',font=font(40,True),fill=ink)
d.text((42,82),'CODEX 2 / PHASE 1 / original-scale bind pose / pitch 38, yaw 2 / 1 m grid',font=font(23),fill=muted)
for i,row in enumerate(rows):
 y=140+i*400;name=row['name'];d.rectangle((24,y,1576,y+384),fill='#FFFDFA')
 ref=Image.open(R/f'Assets/Art/UI/Portraits/art108-{name}.png').convert('RGBA');ref.thumbnail((235,280));bg=Image.new('RGBA',ref.size,'#153B4C');bg.alpha_composite(ref);canvas.paste(bg.convert('RGB'),(42,y+70))
 d.text((42,y+26),'PORTRAIT',font=font(18,True),fill=muted)
 proof=Image.open(W/f'{name}-proof.png').convert('RGB');canvas.paste(proof.resize((365,365),Image.Resampling.LANCZOS),(285,y+10))
 head=Image.open(W/f'{name}-head.png').convert('RGB');canvas.paste(head.resize((275,303),Image.Resampling.LANCZOS),(665,y+64));d.text((665,y+26),'HEAD DETAIL',font=font(18,True),fill=muted)
 x=975;d.text((x,y+22),name.upper(),font=font(32,True),fill=ink);d.text((x,y+65),f"{roles[name].upper()} / M / {row['hair']}",font=font(18,True),fill=muted)
 for j,key in enumerate(('skinHex','hairHex','eyeHex','suitHex')):
  sx=x+j*142;d.rectangle((sx,y+106,sx+116,y+139),fill=row[key],outline='#CCC6BA');d.text((sx,y+148),key[:-3].upper(),font=font(14,True),fill=muted);d.text((sx,y+170),row[key],font=font(16),fill=ink)
 note=row['note'].replace(' Portrait caps/helmet and clothes are deferred; Phase 1 role-colour bodysuit only.','')
 for j,line in enumerate(textwrap.wrap(note,width=56)):d.text((x,y+215+j*25),line,font=font(18),fill=ink)
d.text((42,canvas.height-70),'6 FBXs / original rigs / Skin + Suit + Hair + Eyes + Brows',font=font(23,True),fill=ink)
d.text((42,canvas.height-35),'CC0 Quaternius. Hats and real outfits deferred. Unity import / retargeting / acceptance: Claude + Mo.',font=font(19),fill=muted)
canvas.save(O/'crew-contact-2.jpg',quality=94,subsampling=0)
raw=Image.open(W/'crew-grid.png').convert('RGB');grid=Image.new('RGB',(2880,2180),cream);grid.paste(raw,(0,105));g=ImageDraw.Draw(grid)
g.text((45,24),'CREW 2 / ORIGINAL SCALE / BIND POSE',font=font(44,True),fill=ink);g.text((1750,38),'pitch 38 / yaw 2 / 1 m grid',font=font(34),fill=muted)
anchors=json.loads((W/'render-layout.json').read_text())['anchors']
for a in anchors:
 label=a['name'].upper()+' / '+roles[a['name']].upper();f=font(29,True);box=g.textbbox((0,0),label,font=f);tw=box[2]-box[0];x=a['x'];y=a['y']+105
 g.rounded_rectangle((x-tw/2-16,y-7,x+tw/2+16,y+43),radius=9,fill=cream);g.text((x-tw/2,y),label,font=f,fill=ink)
g.text((45,2121),'Phase 1: portrait colours, supplied hair + brows + facial hair. Kofi: Buns curl substitute. Hats / real outfits deferred.',font=font(29),fill=ink)
grid.save(O/'crew-contact-2-grid.jpg',quality=94,subsampling=0);grid.resize((844,round(grid.height*844/grid.width)),Image.Resampling.LANCZOS).save(O/'crew-contact-2-844.jpg',quality=94,subsampling=0)
# Re-read immediately before additive shared-file merge; preserve the other roster.
p=O/'crew-manifest.json';data=json.loads(p.read_text()) if p.exists() else [];current=data if isinstance(data,list) else data.setdefault('crew',[]);names={r['name'] for r in rows};others=[r for r in current if r.get('name') not in names];current[:]=others+[{k:r[k] for k in ('name','gender','hair','skinHex','hairHex','eyeHex','suitHex','note')} for r in rows];p.write_text(json.dumps(data,indent=2)+'\n')
assert all(r in json.loads(p.read_text()) for r in others)
print(json.dumps({'contact':canvas.size,'grid':grid.size,'overview':Image.open(O/'crew-contact-2-844.jpg').size,'manifestRows':len(current)}))

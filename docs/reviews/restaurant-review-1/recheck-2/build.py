from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, hashlib

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
C = ROOT / 'Art/Source/Restaurant/concepts'
CAP = ROOT / 'docs/screens/restaurant-ui'
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
cases = [
 ('service', 'ui-2-service.png', 'r99/day-service-orders', 'r101/day-service-orders', 'r112/day-service-orders'),
 ('closed', 'ui-closed-sign.png', 'r88/day-service-closed', 'r101/day-service-closed', 'r112/day-service-closed'),
 ('prep', 'ui-4-prep.png', 'r99/day-prep', 'r101/day-prep', 'r112/day-prep'),
 ('market', 'ui-7-market.png', 'r81/day-market', 'r101a/restaurant-market'),
 ('arrange', 'ui-arrange-card-states.png', 'r86/day-arrange', 'r101a/day-arrange'),
 ('arrange-buy', 'ui-arrange-card-states.png', 'r86/day-arrange-buy', 'r101a/day-arrange-buy'),
 ('arrange-kitchen', 'ui-1-arrange.png', 'r86/day-arrange-kitchen', 'r101a/day-arrange-kitchen'),
]
ledger = []
for name, concept, *states in cases:
 for device, size in [('844',(844,390)), ('1440',(1440,900))]:
  ref = 'ui-service-desktop.png' if name == 'service' and device == '1440' else concept
  paths = [C/ref] + [CAP/(s+'-'+device+'.png') for s in states]
  canvas = Image.new('RGB',(size[0]*len(paths),size[1]+26),'#233d4b')
  draw = ImageDraw.Draw(canvas)
  for i,p in enumerate(paths):
   im = Image.open(p).convert('RGB')
   ledger.append(dict(path=p.relative_to(ROOT).as_posix(), size=im.size, sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
   fitted = ImageOps.contain(im,size,Image.Resampling.LANCZOS)
   x = i*size[0]
   canvas.paste(fitted,(x+(size[0]-fitted.width)//2,26+(size[1]-fitted.height)//2))
   draw.text((x+6,4), p.parent.name+'/'+p.name, font=font,fill='white')
   if i:
    im.resize(size,Image.Resampling.LANCZOS).save(OUT/(p.parent.name+'-'+p.stem+'-logical.png'))
  canvas.save(OUT/(name+'-'+device+'.jpg'),quality=95,subsampling=0)
(OUT/'sources.json').write_text(json.dumps(ledger,indent=2)+'\n')
print(json.dumps(dict(comparisons=14,inputs=len(ledger))))

"""Persist built-in ImageGen concepts and source-vs-proposal review evidence."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,shutil,hashlib
P=Path(__file__).resolve().parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=json.loads((P/'corrections.json').read_text())
entries=[]
for r in records:
 kind=r['id'].split('-')[1];n='17' if kind=='fishing' else '18'
 src=Path(r['hint'].split(' as ')[1].split(' by default.')[0]);raw=P/(r['id']+'-corrected.png');shutil.copy2(src,raw)
 final=P.parent/('ui-v3-'+n+'-hud-'+kind+'.png')
 Image.open(raw).convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS).save(final)
 original=ROOT/'Art/Concepts'/(n+'-hud-'+kind+'.png')
 review=Image.new('RGB',(1920,580),'#eee5d1');d=ImageDraw.Draw(review);font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',21)
 for x,p,label in [(0,original,'Original layout reference'),(960,final,'UI v3 concept — for Mo review')]:
  d.text((x+16,10),label,font=font,fill='#173f57');review.paste(Image.open(p).convert('RGB').resize((960,540)),(x,40))
 review.save(P/(kind+'-comparison.jpg'),quality=96)
 entries.append(dict(file=str(final.relative_to(ROOT)),sha256=sha(final),size=[1920,1080],source=str(original.relative_to(ROOT)),sourceSha256=sha(original),correctedRaw=raw.name,rawSha256=sha(raw),status='proposal for Mo review',cuts=False))
(P/'manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
print('Persisted 2 corrected concepts at1920x1080 and reference comparisons. No HUD cuts.')

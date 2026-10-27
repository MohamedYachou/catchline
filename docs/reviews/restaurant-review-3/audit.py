from pathlib import Path
from PIL import Image
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
rows=json.loads((OUT/'sources.json').read_text())
for r in rows:
 p=ROOT/r['path']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],str(p)
 with Image.open(p) as im:
  assert list(im.size)==r['size'];im.verify()
images=[]
for p in OUT.iterdir():
 if p.suffix.lower() in ('.png','.jpg'):
  with Image.open(p) as im: size=list(im.size);im.verify()
  images.append(dict(path=p.name,size=size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
report=ROOT/'docs/reviews/RESTAURANT-REVIEW-3.md'
links=[]
for p in [report,OUT/'index.md',OUT/'annotations.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  assert (p.parent/link).exists() or (p.parent/link).resolve()==(OUT/'audit.json').resolve(),(p,link)
  links.append(link)
result=dict(status='PASS',source_records=len(rows),unique_sources=len({r['path'] for r in rows}),all_source_hashes_unchanged=True,decoded_outputs=len(images),local_links_checked=len(links),images=images,limits='Saved-image review only. No runtime, animation or player acceptance. r134 closing/S9 and r135/r135b kitchen import included; station-finish source work is not represented.')
(OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
for p in [report,OUT/'index.md',OUT/'annotations.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  assert (p.parent/link).exists(),(p,link)
print({k:v for k,v in result.items() if k!='images'})

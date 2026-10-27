"""Independent source-art package audit; no runtime assertions."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
ART=P.parent.parent
EV=P.parent/'s15/events'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def rect_ok(r,canvas):
 x,y,w,h=r
 assert min(x,y)>=0 and min(w,h)>0 and x+w<=canvas[0] and y+h<=canvas[1],r
results=[]
entries=read(P/'manifest.json')+read(EV/'manifest.json')
for e in entries:
 folder=P if e['name'].startswith('v2-s2-') else EV.parent
 f=folder/e['file'];im=Image.open(f)
 assert im.mode=='RGBA' and list(im.size)==e['size']
 assert e['size']==[n*3 for n in e['logicalSize']]
 assert im.getchannel('A').getbbox()==(0,0,*im.size)
 assert sha(f)==e['sha256']
 src=ROOT/e['provenance']['source'];assert sha(src)==e['provenance']['sourceSha256']
 matches=list((ART/'exact').glob('**/'+e['file']))
 assert matches==[f],(e['name'],matches)
 if e['borders']:
  l,b,r,t=e['borders'];assert l+r<im.width and b+t<im.height
 results.append(dict(file=str(f.relative_to(ROOT)),sha256=sha(f),tightRGBA=True,scale=3))
base=read(EV/'baseline-manifest.json');current=read(EV.parent/'manifest.json')
assert current[:len(base)]==base and current[len(base):]==read(EV/'manifest.json')
for e in base:assert sha(EV.parent/e['file'])==e['sha256']
styles=read(P/'text-styles.json')['styles']
assert len(set((s['screen'],s['id']) for s in styles))==len(styles)
for s in read(P/'layout.json')['screens']:
 canvas=s['canvas'];bg=(P/s['background']).resolve()
 assert sha(bg)==s['backgroundSha256']
 original=Image.open(bg).convert('RGBA').resize((canvas[0]*3,canvas[1]*3),Image.Resampling.NEAREST)
 composed=Image.open(P/(s['screen']+'-reconstructed-3x.png')).convert('RGBA')
 allowed=Image.new('L',original.size,0);d=ImageDraw.Draw(allowed)
 rects=[s['headerReflow']['patchRect']]+[p['rect'] for p in s['placements']]+[t['rect'] for t in styles if t['screen']==s['screen']]
 for r in rects:
  rect_ok(r,canvas);x,y,w,h=r;d.rectangle((x*3,y*3,(x+w)*3-1,(y+h)*3-1),fill=255)
 diff=ImageChops.difference(original,composed).convert('RGB');diff.putalpha(ImageChops.invert(allowed))
 assert ImageChops.multiply(diff.convert('RGB'),Image.merge('RGB',(ImageChops.invert(allowed),)*3)).getbbox() is None
 results.append(dict(screen=s['screen'],unchangedOutsideMeasuredRects=True))
for p in read(EV/'layout.json')['placements']:rect_ok(p['rect'],[844,390])
for f in ['text-measurements.json','line-fit.json']:
 for t in read(P/f):
  assert t['passFit'] and t['widthPx']<=t['rect'][2] and t['heightPx']<=t['rect'][3]
assert 40 in [len(' '.join(t['lines'])) for t in read(P/'line-fit.json')]
assert max(len(' '.join(t['lines'])) for t in read(P/'line-fit.json'))>=40
for name,size in [('ui-2-mira-call-phone.png',(844,390)),('ui-2-mira-call-desktop.png',(1440,900))]:assert Image.open(ART/'concepts'/name).size==size
write(P/'delivery-audit.json',dict(status='PASS',exports=len(entries),acceptedS15EntriesPreserved=len(base),results=results,scope='Source art only. Native import, live timing, hit targets and runtime visual acceptance are not tested.'))
print('PASS:',len(entries),'tight RGBA3x exports;',len(base),'accepted S15 entries preserved; text fits; source HUD preserved outside measured edits.')

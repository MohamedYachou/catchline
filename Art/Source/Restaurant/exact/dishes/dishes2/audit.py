"""Independent read-only checks; never rebuild or mutate input assets."""
from pathlib import Path
import hashlib, json, re
from PIL import Image
P=Path(__file__).resolve().parent
ROOT=P.parents[5]
def load(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
entries=load('manifest.json')
assert len(entries)==13 and len({e['key'] for e in entries})==13
look=(ROOT/'Assets/Scripts/Game/VoyageRestaurantDay.cs').read_text(encoding='utf-8-sig').split('DishLook = new()')[1].split('};')[0]
keys=re.findall(r'"(v2-dish-[^"]+)"',look)
assert set(keys)=={e['key'] for e in entries}
for e in entries:
    for kind in ['source','imported']:
        p=ROOT/e[kind]; assert sha(p)==e[kind+'Sha256']
        im=Image.open(p); im.load(); assert im.mode=='RGBA'
        assert list(im.size)==e[kind+'Size']
        bbox=im.getchannel('A').getbbox();assert bbox
        bounds=e['sourceAlphaBounds' if kind=='source' else 'importedAlphaBounds']
        assert list(bbox)==bounds
    if '/dishes/v2-' in e['source']:
        im=Image.open(ROOT/e['source'])
        assert all(v%3==0 for v in im.size)
        assert im.getchannel('A').getbbox()==(0,0,*im.size)
preserved=load('preservation-baseline.json')
for name,digest in preserved.items():assert sha(ROOT/name)==digest,name
layout=load('layout.json')['placements']
for e in entries:
    places=[v for v in layout if v['name']==e['key']]
    assert len(places)==4
    assert [v['rect'][2:] for v in places if v['screen']=='s6']==[[84,47],[74,45],[68,45]]
    assert [v['rect'][2:] for v in places if v['screen']=='s3']==[[110,75]]
    for v in places:
        x,y,w,h=v['rect']; px,py,pw,ph=v['paintedRect3x']
        assert x*3<=px and y*3<=py and px+pw<=(x+w)*3 and py+ph<=(y+h)*3
proofs=[]
for screen,size in [('s6',(844,768)),('s3',(844,683))]:
    for suffix,expected in [('contact-actual-size.jpg',size),('contact-3x.png',tuple(v*3 for v in size))]:
        p=P/f'{screen}-{suffix}'; im=Image.open(p);im.load();assert im.size==expected
        proofs.append(dict(file=p.name,sha256=sha(p),size=list(im.size)))
review=load('visual-review.json')
assert len(review)==2
for v in review:assert v['opened'] is True and sha(P/v['file'])==v['sha256']
result=dict(status='PASS',menuEntries=13,sourceImportPixelMatches=sum(e['sourceEqualsImportPixels'] for e in entries),
    existingPaintingsReused=13,newPaintings=0,preservedFiles=len(preserved),measuredPlacements=len(layout),
    decodedProofs=proofs,openedActualSizeReviews=len(review),
    limits='Four older source/import pairs differ in canvas pixels; both retained and dimensions recorded. No Unity runtime/import metadata or native appearance acceptance.')
(P/'audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(entries),'menu paintings;',len(preserved),'existing PNGs unchanged;',len(layout),'measured placements')

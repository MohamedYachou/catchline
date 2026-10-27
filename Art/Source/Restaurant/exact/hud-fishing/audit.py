from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Assets').exists())
BASE=ROOT/'Art/Source/Restaurant/exact'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 result={'packages':{},'preservation':{}}
 for kind in ['fishing','harbour']:
  p=BASE/('hud-'+kind);es=json.loads((p/'manifest.json').read_text());layouts=json.loads((p/'layout.json').read_text());texts=json.loads((p/'text-styles.json').read_text());fit=json.loads((p/'text-measurements.json').read_text());names={e['name'] for e in es};assert len(names)==len(es)
  files={e['file'] for e in es if 'file' in e}
  for f in p.glob('v3-hud-*.png'):
   if f.name not in files:f.unlink()
  for e in es:
   q=ROOT/e['external'] if 'external' in e else p/e['file'];im=Image.open(q);assert sha(q)==e['sha256'];assert im.mode=='RGBA';assert list(im.size)==e['size']
   if 'file' in e:assert all(v%3==0 for v in im.size);assert im.getchannel('A').getbbox()==(0,0,*im.size),(q,im.getchannel('A').getbbox())
   if e.get('borders'):
    l,b,r,t=e['borders'];assert l+r<im.width and b+t<im.height,(q,e['borders'])
  for sc in layouts:
   assert len({t['id'] for t in texts if t['screen']==sc['screen']})==len([t for t in texts if t['screen']==sc['screen']])
   for u in sc['placements']:
    assert u['name'] in names;x,y,w,h=u['rect'];assert min(x,y)>=0 and w>0 and h>0 and x+w<=sc['canvas'][0] and y+h<=sc['canvas'][1],u
   for suffix in ['actual-size.jpg','reconstructed-3x.png','comparison.jpg']:
    im=Image.open(p/(sc['screen']+'-'+suffix));im.verify()
  assert all(f['fits'] for f in fit)
  result['packages'][kind]={'entries':len(es),'localSprites':len(files),'reused':len(es)-len(files),'placementsPerFrame':len(layouts[0]['placements']),'liveLabelsPerFrame':len(texts)//2,'textFits':len(fit),'pass':True}
 baseline=json.loads((BASE/'hud-fishing/preservation-baseline.json').read_text());changed=[r for r,h in baseline.items() if not (ROOT/r).exists() or sha(ROOT/r)!=h];assert not changed,changed
 result['preservation']={'existingInputsUnchanged':len(baseline),'changed':changed};result['pass']=True
 (BASE/'hud-fishing/audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':run()

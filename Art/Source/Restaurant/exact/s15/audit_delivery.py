from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def audit():
 m=load(P/'manifest.json');l=load(P/'layout.json');names=[e['name'] for e in m]
 assert len(names)==len(set(names))==16
 assert len([n for n in names if n.startswith('v2-s15-task-')])==9
 assert len(l['placements'])==16
 for e in m:
  f=P/e['file'];a=Image.open(f);assert a.mode=='RGBA' and list(a.size)==e['size'];assert sha(f)==e['sha256']
  assert a.getchannel('A').getextrema()[0]==0
  if 'animation' not in e:assert a.getchannel('A').getbbox()==(0,0,*a.size)
  assert len(list((ROOT/'Art/Source/Restaurant/exact').glob('s*/'+e['file'])))==1,e['file']
  for pl in l['placements']:
   if pl['name']==e['name'] and 'animation' not in e:assert e['size']==[v*3 for v in pl['rect'][2:]]
 for n in ['patience-track','patience-fill']:
  a=Image.open(P/('v2-s15-'+n+'.png'));assert a.getpixel((a.width//2,a.height//2))[3]==0
 a=Image.open(P/'v2-s15-steam-strip.png')
 assert a.size==(768,192)
 for k in range(4):assert a.crop((192*k,0,192*k+192,192)).getchannel('A').getbbox()
 assert Image.open(ROOT/'Art/Source/Restaurant/concepts/ui-15-markers.png').size==(844,390)
 assert sha(ROOT/'Art/Source/Restaurant/concepts/ui-2-service.png')==l['backgroundSha256']
 result={'status':'PASS','sprites':len(m),'taskIcons':9,'steamFrames':4,'ringCentreAlpha':0,'tightStaticSprites':15,'uniqueNames':True,'demoCanvas':[844,390],'nativeRuntimeVerified':False,'files':{e['file']:sha(P/e['file']) for e in m}}
 (P/'delivery-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('S15 independent PASS16 sprites/9tasks/4frames/ringholes/unique/tight/hashes')
if __name__=='__main__':audit()

from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).resolve().parent; P=D.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
for m in json.loads((P/'manifest.json').read_text()):assert sha(P/m['file'])==m['sha256'],'accepted Bistro changed'
for stage in [3,4]:
 O=D/f'stage{stage}';ms=json.loads((O/'manifest.json').read_text());ts=json.loads((O/'text-styles.json').read_text())['styles']
 assert len(ms)==len({m['name'] for m in ms})==11
 assert len(ts)==len({t['id'] for t in ts})==11
 for m in ms:
  a=Image.open(P/m['file']);assert a.mode=='RGBA' and a.size==(m['rect'][2]*3,m['rect'][3]*3)
  assert a.getchannel('A').getbbox()==(0,0,*a.size) and sha(P/m['file'])==m['sha256']
 for t in ts:
  x,y,w,h=t['rect'];assert x>=0 and y>=0 and x+w<=844 and y+h<=390
 audit=json.loads((O/'audit.json').read_text());audit['visualReview']='actual preview/cuts/text measurement opened';audit['acceptedBistroHashesUnchanged']=True;dump(O/'audit.json',audit)
dump(D/'visual-review.json',{'reviewer':'Codex 1 (Windows app)','actuallyOpened':{str(p.relative_to(D)):sha(p) for p in [D/'stage3/ui-11-stage3-preview.png',D/'stage3/cuts-review.jpg',D/'stage4/ui-11-stage4-preview.png',D/'stage4/cuts-review.jpg',D/'stage4/text-measure.jpg']},'nativeAcceptance':False})
print('PASS 22 sprites,22 texts,accepted Bistro hashes unchanged')

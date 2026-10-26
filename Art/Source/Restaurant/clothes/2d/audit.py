"""Delivery audit: live roster/role agreement, alpha and real staff source resolution."""
import hashlib,json,re
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parent; project=root.parents[4]
roster=json.loads((root/'roster.json').read_text())
manifest=json.loads((root/'manifest.json').read_text())
cards=dict((n.lower(),r) for n,r in re.findall(r'new CardDef\("([^"]+)",\s*\d+,\s*CardRole\.(\w+)',(project/'Assets/Scripts/Game/Data/Cards.cs').read_text()))
expected=set(cards)|{'captain'}; actual={j['card'] for j in roster}
assert expected==actual, (expected-actual,actual-expected)
assert len(manifest['records'])==len(roster)==16
assert len({j['id'] for j in roster})==16
checks=[]
for j,r in zip(roster,manifest['records']):
    ident=j['id'];assert r['id']==ident
    role='Helper' if j['card']=='captain' else 'Reception' if j['card']=='mira' else 'Barista' if j['card'] in ('ines','mats') else {'Fisher':'Cook','Deckhand':'Waiter','Engineer':'Handyman','Navigator':'Barista'}[cards[j['card']]]
    assert role==j['job'],(ident,role,j['job'])
    assert min(r['bustNativeSize'])>=264, (ident,r['bustNativeSize'])
    files=[]
    for key in ('fullBody','bust','sheet'):
        p=root/r[key];im=Image.open(p)
        alpha=im.getchannel('A').getextrema()
        # Generator originals can peak at254; retain that near-opaque source alpha.
        assert im.mode=='RGBA' and alpha[0]==0 and alpha[1]>=250,(p,im.mode,alpha)
        if key!='sheet': assert im.getchannel('A').getbbox()==(0,0,*im.size)
        if key=='bust':assert min(im.size)>=264
        files.append({'path':p.name,'size':im.size,'alphaRange':alpha,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    assert (root/(ident+'-compare.jpg')).exists()
    assert (root/'provenance'/(ident+'-generated.json')).exists()
    checks.append({'id':ident,'job':role,'nativeAndExportedBust3x':True,'alphaPass':True,'files':files})
out={'pass':True,'liveCards':len(cards),'captainHelperIncluded':True,'people':len(actual),'variants':len(roster),
     'filesVerified':len(checks)*3,'artOnly':True,'staffNativeLimit':[88,88],
     'checks':checks,'limits':'Source/export checks only. Visual review recorded separately; no import/runtime/player acceptance.'}
(root/'audit.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='checks'}))

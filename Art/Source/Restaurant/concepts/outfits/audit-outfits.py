"""Independent decoded-export and accepted-source preservation audit."""
from pathlib import Path
from PIL import Image
import hashlib,json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=json.loads((OUT/'manifest.json').read_text())+json.loads((OUT/'closing-manifest.json').read_text())
checks=[]
for r in records:
    p=OUT/r['file']
    with Image.open(p) as im:
        im.load()
        assert im.mode=='RGBA',p
        assert list(im.size)==r['size'],p
        assert all(n%3==0 for n in im.size),p
        assert im.getchannel('A').getbbox()==(0,0,*im.size),p
        assert im.getchannel('A').getextrema()[0]==0,p
        assert sha(p)==r['sha256'],p
        checks.append({'file':r['file'],'rgba':True,'exact3x':True,'tightAlpha':True,'size':im.size,'sha256':sha(p)})
baseline=json.loads((OUT/'preservation-baseline.json').read_text())
changed=[name for name,digest in baseline.items() if not (ROOT/name).exists() or sha(ROOT/name)!=digest]
refs=json.loads((OUT/'references.json').read_text())
identity_changed=[r['path'] for r in refs if sha(ROOT/r['path'])!=r['sha256']]
assert not changed,changed
assert not identity_changed,identity_changed
assert len(checks)==13
images=[]
for p in sorted(OUT.glob('*.png'))+sorted(OUT.glob('*.jpg')):
    with Image.open(p) as im:
        im.load(); images.append({'file':p.name,'size':im.size,'sha256':sha(p)})
out={'status':'PASS','exports':checks,'acceptedSourcesPreserved':len(baseline),'referenceHashesPreserved':len(refs),'changedAcceptedSources':changed,'changedIdentityReferences':identity_changed,'decodedImages':images,'limits':['Source delivery only; no Unity import or native AFTER acceptance.','Rail exports enlarge accepted painted busts; 3x container size is not a native generated detail claim.','Trim offsets retain incumbent framing, but source bust silhouette differs from deck clothes.','Closing native override differs from measured mockup; lead owns placement and Sleep occlusion.']}
(OUT/'audit.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'status':'PASS','exports':len(checks),'acceptedSourcesPreserved':len(baseline),'referencesPreserved':len(refs),'decodedImages':len(images)}))

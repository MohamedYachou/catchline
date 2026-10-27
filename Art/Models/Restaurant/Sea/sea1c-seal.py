from pathlib import Path
from PIL import Image
import hashlib,json
O=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((O/'sea1b-final-audit.json').read_text());unchanged=[]
for name,h in old['files'].items():
 if name in ('sea1-package.py','sea1-night-water-1024.png','sea1-night-water-2048.png'):continue
 assert H(O/name)==h,name;unchanged.append(name)
check=json.loads((O/'sea1c-blender-check.json').read_text());source=O.parent/'Stage1V4'/check['source'];assert H(source)==check['source_sha256']
assert check['source_sha256']==json.loads((O/'sea1b-blender-check.json').read_text())['source_sha256']
assert json.loads((O/'sea1c-independent-audit.json').read_text())['pass']
assert json.loads((O/'sea1c-packed-audit.json').read_text())['pass']
files=[O/'sea1-package.py',O/'sea1-night-water-1024.png',O/'sea1-night-water-2048.png']
files += [p for p in O.rglob('sea1c-*') if p.is_file() and p.suffix!='.log' and p.name!='sea1c-final-audit.json']
files += [p for folder in ('sea1c-provenance','sea1c-renders') for p in (O/folder).rglob('*') if p.is_file()]
files=sorted(set(files));decoded=[]
for p in files:
 if p.suffix.lower() in ('.png','.jpg'):
  with Image.open(p) as im:im.load();decoded.append({'file':str(p.relative_to(O)),'size':list(im.size),'mode':im.mode})
result={'pass':True,'source_scene_unchanged':True,'prior_sea1b_artifacts_preserved':unchanged,'decoded_images':decoded,'files':{str(p.relative_to(O)):H(p) for p in files},'native_Unity_after_unverified':True}
(O/'sea1c-final-audit.json').write_text(json.dumps(result,indent=2))
for name,h in result['files'].items():assert H(O/name)==h
print('SEA1C FINAL PASS',len(files),'hashes',len(decoded),'images; prior',len(unchanged),'artifacts unchanged')

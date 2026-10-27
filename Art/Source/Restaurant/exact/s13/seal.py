from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent;A=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
review=[A/'concepts/ui-13-first-night.png',P/'cuts-review.jpg',P/'text-measure.jpg',P/'slice-proof.jpg']
dump(P/'visual-review.json',dict(reviewer='Codex 1 (Windows app)',actuallyOpened={str(p.relative_to(A)):sha(p) for p in review},findings='Final four frames, text fit, separate bubble tail and gold pointer, Mira D, cleared-room closing ledger inspected. No inherited Not tonight UI in closing. Slice corners/tail survive both widths.',nativeAcceptance=False))
audit=json.loads((P/'audit.json').read_text());assert audit['passChecks'];audit['visualReview']='PASS actual final preview, contacts, text rects, slice stress proof opened';dump(P/'audit.json',audit)
allfiles=[]
for folder in [A/'clothes/guests',A/'exact/s11/later-stages/stage3',A/'exact/s11/later-stages/stage4',P]:
 ms=json.loads((folder/'manifest.json').read_text())
 # Guest manifest is a list of exports; inspect generic file/name schema below.
 if isinstance(ms,dict):ms=ms.get('portraits',ms.get('assets',ms.get('entries',[])))
 for m in ms:
  fn=m.get('file',m.get('output'))
  if fn is None:continue
  path=(folder.parent.parent/fn) if folder.name in ['stage3','stage4'] else folder/fn
  assert path.is_file(),str(path)
  expected=m.get('sha256',m.get('outputSha256'))
  if expected:assert sha(path)==expected
  allfiles.append(path)
assert len(allfiles)==43,len(allfiles)
assert len({p.name for p in allfiles})==43
for m in json.loads((A/'exact/s11/manifest.json').read_text()):assert sha(A/'exact/s11'/m['file'])==m['sha256']
dump(P/'delivery-audit.json',dict(passChecks=True,sprites=43,uniqueNames=True,acceptedBistroHashesUnchanged=True,hashes={str(p.relative_to(A)):sha(p) for p in allfiles},nativeAcceptance=False))
print('PASS final 43 sprites; unique names/current export hashes; accepted Bistro preserved; review hashes sealed')

"""Independent structural audit; it cannot certify an exact visual match."""
from pathlib import Path
from PIL import Image
import ast,json,hashlib
ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'manifest.json').read_text()); errors=[]; missing=[]; items=[]
byname={e['name']:e for e in M}
for instance in json.loads((ROOT/'layout.json').read_text()).get('repeated_instances',[]):
    e=byname[instance['name']]
    if any(e['size'][i]<instance['rect'][i+2]*3 for i in range(2)):
        errors.append(e['name']+' below 3x repeated placement')
for e in M:
    p=ROOT/(e['name']+'.png')
    if not p.exists(): missing.append(e['name']); continue
    with Image.open(p) as im:
        im.load()
        if list(im.size)!=e['size']: errors.append(e['name']+' canvas')
        if any(im.size[i]<e['rect'][i+2]*3 for i in range(2)): errors.append(e['name']+' below 3x primary placement')
        if im.mode!='RGBA': errors.append(e['name']+' mode')
        alpha=im.getchannel('A').getextrema()
        if not e['opaque'] and (alpha[0]!=0 or alpha[1]!=255): errors.append(e['name']+' alpha')
        if e['opaque'] and alpha!=(255,255): errors.append(e['name']+' opaque background')
    if e['borders']:
        l,t,r,b=e['borders']; w,h=e['size']
        if min(l,t,r,b)<0 or l+r>=w or t+b>=h: errors.append(e['name']+' invalid slices')
    if not (ROOT/'review'/(e['name']+'.png')).exists(): errors.append(e['name']+' no comparison')
    items.append(dict(name=e['name'],sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
for p in ROOT.glob('*.py'): ast.parse(p.read_text(encoding='utf8'))
review_path=ROOT/'visual-review.json'
review=json.loads(review_path.read_text()) if review_path.exists() else {}
opened=set(review.get('opened_assets',[]))
unopened=[e['name'] for e in M if e['name'] not in opened]
changed_since_open=[r['name'] for r in items if review.get('opened_hashes',{}).get(r['name'])!=r['sha256']]
receipt=dict(expected=len(M),present=len(items),errors=errors,missing=missing,unopened=unopened,
    changed_since_open=changed_since_open,
    structural_pass=not errors and not missing,manual_open_coverage=not unopened and not changed_since_open,
    exact_visual_acceptance='NOT CERTIFIED: lead/Mo review required; see visual findings',files=items)
(ROOT/'delivery-audit.json').write_text(json.dumps(receipt,indent=2))
# Inventory receipt includes every delivered file except the receipt itself.
hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='delivery-receipt.json'}
(ROOT/'delivery-receipt.json').write_text(json.dumps(hashes,indent=2))
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
print(json.dumps({k:v for k,v in receipt.items() if k!='files'}))
print('sealed and immediately rechecked',len(hashes),'files')

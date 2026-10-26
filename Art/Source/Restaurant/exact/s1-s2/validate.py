"""Read-only artifact validation; never modifies artwork or claims visual acceptance."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
aud=read('asset-audit.json'); by={r['name']:r for r in aud}
expected={j[0] for j in read('jobs.json')}|{j[0] for j in read('extra-jobs.json')}
crew=['ana','bram','dirk','ines','jo','kofi','lise','mats','mei','mira','noor','olaf','pim','rosa','sam','tess','tove','yusuf']
expected|={'v2-bust-'+c for c in crew}
expected|={'v2-service-card','v2-icon-coin-arrange','v2-meter-fill-orange','v2-meter-fill-yellow','v2-guest-patience-arc'}
expected|={'v2-icon-group','v2-icon-cross','v2-icon-tile1','v2-icon-tile2','v2-icon-order-dish','v2-meter-ring-fill-orange'}
errors=[]; warnings=[]
for n in sorted(expected-set(by)):errors.append('missing '+n)
reviews=read('visual-review.json')
for n,a in by.items():
 p=R/a['file'];im=Image.open(p)
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 if im.mode!='RGBA':errors.append(n+' has no RGBA')
 elif im.getchannel('A').getextrema()!=(0,255):errors.append(n+' missing full alpha range')
 if tuple(a['size'])!=im.size:errors.append(n+' size mismatch')
 if sha!=a['sha256']:errors.append(n+' sha mismatch')
 if not (R/'review'/(n+'-compare.png')).exists():errors.append(n+' missing contact')
 rev=reviews.get(n,{})
 if 'opened' not in rev.get('status',''):errors.append(n+' not opened/reviewed')
 if rev.get('sha256')!=sha:errors.append(n+' visual review hash missing/stale')
 if 'pending' in rev.get('status',''):errors.append(n+' correction pending')
 if a['sourceUpscaled']:warnings.append(n+' source artwork enlarged during export; recorded explicitly')
for p in read('layout.json')['placements']:
 a=by.get(p['asset'])
 if a and any(a['size'][i]<3*p['rect'][i+2] for i in range(2)):errors.append(p['asset']+' below3x placement '+str(p))
for n,s in read('slices.json').items():
 w,h=s['sourceSize'];l,t,r,b=s['borderLTRB']
 if l+r>=w or t+b>=h:errors.append(n+' invalid9slice bands')
out={'expectedSprites':len(expected),'actualSprites':len(by),'crewExpected':len(crew),'crewActual':sum('v2-bust-'+c in by for c in crew),'layoutPlacements':len(read('layout.json')['placements']),'styles':len(read('text-styles.json')['styles']),'errors':errors,'warnings':warnings,'runtimeAcceptance':'not performed; output-only art task','pixelIdenticalToMockup':False,'visualAcceptance':'see individual findings; Mo/lead acceptance outstanding'}
(R/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
sys.exit(bool(errors))

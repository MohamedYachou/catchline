"""Append explicit human-visible agent review only after each named final image set is opened."""
import json,hashlib,sys,struct
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/LighthouseLife';p=O/'visual-review.json'
d=json.loads(p.read_text()) if p.exists() else {'owner':'Codex 2 (WSL CLI)','images':[],'limits':'Final isolated Blender images individually opened; no Unity/native/map/HUD acceptance.'}
notes={'Puffin':'Faceted black back/white face and belly, attached cheek eyes and wing roots, broad banded orange/yellow bill, orange feet; five actual views and ten original action poses opened. Idle head turns/body bob, Flap wings differ, endpoints match.','PuffinGroup':'Three differently facing complete birds on one irregular angular ledge; feet contact, pivot base and all five silhouettes inspected.','TideRace':'Twelve ragged tapered low standing-wave fragments; broad triangular slopes, white foam flush with sloping crest facets. All five views show low profile, no upright fins.','LighthouseGlow':'Soft crossed lantern cards and long thin fading beam; dark studio, true edge/end views retained. Blender source soft emission; native vertex-alpha shader required.','Assembly':'Both deck-angle water fixtures opened, three birds/ledge beside low broken tide crests; all geometry contained. Map/HUD/runtime external.'}
for name in sys.argv[1:]:
 m=json.loads((O/'renders'/(name+'.json')).read_text());rows=m['views'] if name=='Assembly' else m
 old={r['file']:r for r in d['images']}
 for r in rows:
  f=O/r['file'];raw=f.read_bytes();assert list(struct.unpack('>II',raw[16:24]))==r['size']
  old[r['file']]={**r,'asset':name,'sha256':hashlib.sha256(raw).hexdigest(),'opened_individually':True,'review':notes[name]}
 d['images']=sorted(old.values(),key=lambda r:r['file'])
d['production_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in O.glob('*') if f.suffix in ['.blend','.fbx'] and 'review' not in f.stem}
p.write_text(json.dumps(d,indent=2)+'\n');print('REVIEW RECORDED',len(d['images']))

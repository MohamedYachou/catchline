"""Record Codex2's actual five individually opened image reviews.

Call only AFTER all five images have been opened and inspected by the agent.
This records evidence hashes; it does not itself inspect images.
"""
import argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/GullHarbour/HarbourV2'
ap=argparse.ArgumentParser();ap.add_argument('name');ap.add_argument('finding');a=ap.parse_args()
p=O/'reviewed-images.json';rows=json.loads(p.read_text()) if p.exists() else []
for label in ['front-right','back-right','back-left','front-left','top']:
    image=O/'renders'/a.name/(label+'.png')
    rows=[r for r in rows if r['path']!=image.relative_to(R).as_posix()]
    rows.append({'path':image.relative_to(R).as_posix(),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
       'reviewer':'Codex 2 (WSL CLI)','method':'individually opened with view_image','finding':a.finding})
p.write_text(json.dumps(rows,indent=2)+'\n')
print('Recorded five actual reviews',a.name)

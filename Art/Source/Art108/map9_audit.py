"""MAP9 audit with Claude's accepted close-landmark rule; older audits unchanged."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union
from audit_sea_v2 import audit,plate,sheet
ROOT=Path(__file__).resolve().parents[3]
NAME='GullWhaleShelf'
folder=ROOT/'Art/Models/Maps'/NAME
nav,result=audit(NAME)
# Claude 17:47: corner landmarks are intended inside the full ground circle.
# Keep the historic raw result; waive ONLY submerged camera landmark shelves.
(folder/'SeaV2-audit-raw.json').write_text(json.dumps(result,indent=2))
for check in result['checks']:
    if check['check'].endswith('full zone outside shallows (anchoring)'):
        ground=next(g for g in nav['grounds'] if check['check'].startswith(g['id']+' '))
        centre=Point(ground['centre']['x'],ground['centre']['z'])
        zone=centre.buffer(ground['radius'])
        broad=[Polygon([(p['x'],p['z']) for p in s['vertices']]) for s in nav['shallows'] if not s['sourceObject'].startswith('Terrain_Submerged')]
        near=unary_union([Polygon([(p['x'],p['z']) for p in s['vertices']]) for s in nav['shallows']])
        check['originalPassed']=check['passed']
        check['passed']=not unary_union(broad).intersects(zone) and near.distance(centre)>4
        check['check']=ground['id']+' zone clear except approved submerged corner landmarks; anchor4m clear'
        check['detail']=dict(anchorClearance=near.distance(centre),rule='Claude MAP8 ACCEPTED 17:47, applied only to MAP9 submerged camera landmarks')
result['allPassed']=all(c['passed'] for c in result['checks'])
result['limits']+=' MAP9 close-landmark exception is restricted to submerged corner shelves; anchor radius4m remains clear. Raw inherited audit retained.'
(folder/'SeaV2-audit.json').write_text(json.dumps(result,indent=2))
plate(NAME,nav,result);sheet(NAME,nav)
print('MAP9 AUDIT',sum(c['passed'] for c in result['checks']),'/',len(result['checks']),[c for c in result['checks'] if not c['passed']])
sys.exit(0 if result['allPassed'] else 1)

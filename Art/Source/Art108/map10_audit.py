"""MAP10 audit with Claude's accepted close-landmark rule; older audits unchanged."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import map10_seal_cliffs
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union
from audit_sea_v2 import audit,plate,sheet
ROOT=Path(__file__).resolve().parents[3]
NAME='GullSealCliffs'
folder=ROOT/'Art/Models/Maps'/NAME
nav,result=audit(NAME)
# Claude 17:47: corner landmarks are intended inside the full ground circle.
# Keep the raw result; only the six named camera-corner rocks are excepted.
(folder/'SeaV2-audit-raw.json').write_text(json.dumps(result,indent=2))
for check in result['checks']:
    if 'full zone outside shallows' in check['check'] or 'full zone clear of islands' in check['check']:
        ground=next(g for g in nav['grounds'] if check['check'].startswith(g['id']+' '))
        centre=Point(ground['centre']['x'],ground['centre']['z'])
        zone=centre.buffer(ground['radius'])
        field='shallows' if 'shallows' in check['check'] else 'islands'
        broad=[Polygon([(p['x'],p['z']) for p in s['vertices']]) for s in nav[field] if not s['sourceObject'].startswith('Terrain_CornerRock_')]
        near=unary_union([Polygon([(p['x'],p['z']) for p in s['vertices']]) for s in nav[field]])
        check['originalPassed']=check['passed']
        broad_union=unary_union(broad)
        if field=='islands':broad_union=broad_union.buffer(2)
        check['passed']=not broad_union.intersects(zone) and near.distance(centre)>4
        check['check']=ground['id']+' '+field+' zone clear except approved corner rocks; anchor4m clear'
        check['detail']=dict(anchorClearance=near.distance(centre),rule='Claude MAP8 ACCEPTED 17:47 camera-corner rocks; actual waterline obstacles retained in routes')
result['allPassed']=all(c['passed'] for c in result['checks'])
result['limits']+=' MAP10 close-landmark exception is restricted to six named low corner rocks; anchor radius4m remains clear. Real waterline obstacles retained in all route checks; raw inherited audit retained.'
(folder/'SeaV2-audit.json').write_text(json.dumps(result,indent=2))
if '--plate' in sys.argv:plate(NAME,nav,result);sheet(NAME,nav)
print('MAP10 AUDIT',sum(c['passed'] for c in result['checks']),'/',len(result['checks']),[c for c in result['checks'] if not c['passed']])
sys.exit(0 if result['allPassed'] else 1)

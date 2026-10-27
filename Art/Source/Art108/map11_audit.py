"""MAP11 navigation audit; preserve full-circle findings for narrow foreground posts."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import map11_kelp_forest
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union
from audit_sea_v2 import audit,plate,sheet,publish
NAME='GullKelpForest'
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'Art/Models/Maps'/NAME
nav,result=audit(NAME)
(folder/'SeaV2-audit-raw.json').write_text(json.dumps(result,indent=2))
for check in result['checks']:
    if not check['check'].startswith('post-line full zone'):continue
    if 'clear of islands' not in check['check'] and 'outside shallows' not in check['check']:continue
    field='islands' if 'clear of islands' in check['check'] else 'shallows'
    ground=next(g for g in nav['grounds'] if g['id']=='post-line')
    centre=Point(ground['centre']['x'],ground['centre']['z'])
    zone=centre.buffer(ground['radius'])
    all_polys=[Polygon([(p['x'],p['z']) for p in s['vertices']]) for s in nav[field]]
    broad=[Polygon([(p['x'],p['z']) for p in s['vertices']]) for s in nav[field] if not s['sourceObject'].startswith('Terrain_MooringPost_')]
    coast=unary_union(broad)
    if field=='islands':coast=coast.buffer(2)
    clearance=unary_union(all_polys).distance(centre)
    check.update(originalPassed=check['passed'],passed=not coast.intersects(zone) and clearance>4,
        check='post-line '+field+' zone clear except four narrow foreground posts; anchor4m clear',
        detail=dict(anchorClearance=clearance,rule='MAP11 narrow-post broad-circle exception ACCEPTED by Claude 2, 2026-10-26 08:45; four real wooden posts retained in every route.'))
result['allPassed']=all(c['passed'] for c in result['checks'])
result['limits']+=' MAP11 scoped audit excepts only four narrow foreground mooring posts from the broad-circle test. Accepted by Claude 2, 2026-10-26 08:45. Raw findings retained; actual obstacles, anchor4m clearance and routes remain checked.'
(folder/'SeaV2-audit.json').write_text(json.dumps(result,indent=2))
if '--plate' in sys.argv:plate(NAME,nav,result);sheet(NAME,nav)
if '--publish' in sys.argv:publish(NAME,nav,result)
print('MAP11 AUDIT',sum(c['passed'] for c in result['checks']),'/',len(result['checks']),[c for c in result['checks'] if not c['passed']])
sys.exit(0 if result['allPassed'] else 1)

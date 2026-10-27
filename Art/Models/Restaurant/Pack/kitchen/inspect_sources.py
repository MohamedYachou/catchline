import sys
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util,json
O=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('helpers',O.parent/'lights/build.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
rows=[]
for n in ['extractorhood','pan_A','pan_B','pot_A','knife','towelrail','cuttingboard']:
 h.d.reset();p=h.d.base.KR/(n+'.fbx');obs=h.d.base.load(p);lo,hi=h.d.bounds(obs)
 rows.append(dict(name=n,bounds=[list(lo),list(hi)],meshes=[o.name for o in obs if o.type=='MESH']))
(O/'source-inventory.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)

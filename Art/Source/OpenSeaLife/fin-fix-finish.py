from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
S=Path(__file__).resolve().parent;R=S.parents[2];O=R/'Art/Models/OpenSeaLife'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((O/'metrics/BaskingFin-audit.json').read_text());solid=json.loads((O/'metrics/BaskingFin-solid-audit.json').read_text());assert a['result']==solid['result']=='PASS'
p=O/'REPORT.md';text=p.read_text();old=next(l for l in text.splitlines() if l.startswith('| BaskingFin |'));new='| BaskingFin | 184 / 250 | '+' × '.join(f'{v:.3f}' for v in a['dimensions_unity_xyz_m'])+' | Cruise:1–91, 3s, loop |';text=text.replace(old,new)
old=next(l for l in text.splitlines() if l.startswith('| BaskingFin /'))
r=a['imported']['mesh_bounds']['BaskingFinSkin'];text=text.replace(old,f"| BaskingFin / BaskingFinSkin | {tuple(round(v,5) for v in r['world_min_m'])} | {tuple(round(v,5) for v in r['world_max_m'])} | 184 |")
text+='''
## BaskingFin solid-fin correction — 2026-10-26

Supersedes the original 48-triangle constant-thickness fins only. The two closed rounded volumes now total **184/250 triangles**. Each uses six elliptical horizontal sections, a broad fleshy base, gradual backward sweep and a soft small crown; faceted grey-brown shading matches the dolphin family. Dorsal waterline width0.250m, crown0.034m; tail waterline width0.166m, crown0.024m. Both independently reimported components are closed manifold. Root, Rig, Skin, three bone names, origin and Cruise1–91/3s loop unchanged. Full refreshed actual-FBX audit covers hierarchy/palette/skin and five deformed surface samples, with fixed root at all91frames and exact loop closure. See metrics/BaskingFin-solid-audit.json and BaskingFin-audit.json.

All five studio views and five Cruise frames reopened individually after correction. Front/back/top show thickness; quarter and side show taper and sweep. Original assembly and whole-set contact sheets predate this bounded correction; use the revised renders/BaskingFin/ images for this asset. Other eight accepted assets were not rebuilt or reverified. Production camera/water/Legacy import acceptance remains lead scope.
''';p.write_text(text)
p=O/'visual-validation.json';v=json.loads(p.read_text());v['basking_fin_fix']={'result':'PASS source art only','opened':[str(q.relative_to(O)) for q in sorted((O/'renders/BaskingFin').glob('*.png'))],'observation':'All10 individually opened: solid rounded front/top, swept taper in side/quarter; Cruise gentle sway retained.','historical_assemblies_and_contacts':True};p.write_text(json.dumps(v,indent=2)+'\n')
p=S/'opened-images.json';v=json.loads(p.read_text());v['basking_fin_fix_reopened']=json.loads((O/'visual-validation.json').read_text())['basking_fin_fix'];p.write_text(json.dumps(v,indent=2)+'\n')
# Existing accepted receipt entries remain; refresh only changed/new files within owned scope.
p=O/'delivery-receipt.json';v=json.loads(p.read_text());newfiles=[O/'BaskingFin.blend',O/'BaskingFin.fbx',O/'REPORT.md',O/'visual-validation.json',S/'build.py',S/'opened-images.json']+list((O/'metrics').glob('BaskingFin-*.json'))+list((O/'renders/BaskingFin').glob('*.png'))+[O/'renders/BaskingFin.json']+list(S.glob('BaskingFin-*.log'))+list(S.glob('fin-fix*'))
for q in newfiles:
 if q.is_file():v['sha256'][q.relative_to(R).as_posix()]=sha(q)
v['basking_fin_fix']='184 triangles, two solid closed manifold tapered fins; 10 replacement images reopened; historical assembly/contact sheets unchanged';p.write_text(json.dumps(v,indent=2)+'\n');assert all(sha(R/n)==h for n,h in v['sha256'].items());shutil.rmtree('/tmp/catchline-codex2-fin-before');print('FIN FIX SEALED',len(v['sha256']))

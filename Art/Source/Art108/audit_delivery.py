from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];runtime=[]
for p in (R/'Art/Models/StationsV1').glob('*/validation.json'):
 v=json.loads(p.read_text());h=v['hull'];f=R/'Assets/Art/Models/Boats'/f'{h}.fbx';assert sha(f)==v['hullSha256'];assert v['allWorkTilesReachable'];assert json.loads((p.parent/f'{h}.stations.json').read_text())==json.loads((R/'Assets/Art/Models/Boats'/f'{h}.stations.json').read_text());checks.append({'hull':h,'sha256':sha(f),'reachable':v['reachableCount']})
assert len(checks)==5
kit=json.loads((R/'Art/Models/StationsV1/kit-manifest.json').read_text())['assets'];assert len(kit)==33
for a in kit:
 p=R/a['runtimeFile'];assert sha(p)==a['exportSha256'];assert p.stem==a['runtimeModelId'];assert a['roundTripMaxError']<.0001;runtime.append(p)
maps=[]
for p in (R/'Art/Models/Maps').glob('*/validation.json'):
 v=json.loads(p.read_text());assert sha(Path(v['baselineSource']))==v['baselineSha256'];assert v['footprintRatio']>=3 and v['pathCentrelineAllClear'];g=json.loads((p.parent/'grounds.json').read_text());f=R/g['runtimeFile'];assert sha(f)==v['fbxSha256'];assert len(g['grounds'])==3 and len(g['paths'])==3
 for a in g['grounds']:
  for mode in ['day','night']:assert (p.parent/f"{a['id']}-{mode}.png").exists()
 assert (p.parent/'three-grounds-top.png').exists();maps.append(v['map']);runtime.append(f)
assert len(maps)==5
names={}
for f in (R/'Assets/Art/Models').rglob('*.fbx'):names.setdefault(f.stem.lower(),[]).append(f)
for f in runtime:assert len(names[f.stem.lower()])==1,(f,names[f.stem.lower()])
v=json.loads((R/'Art/Models/NavigatorV1/validation.json').read_text());assert sha(R/v['sourceRig'])==v['sourceRigSha256']
# Backup holds former names only; require each rename's final target and absence of old file.
renames=json.loads((R/'Art/Source/Art108/runtime-renames.json').read_text())
for row in renames:assert Path(row['New']).exists() and not Path(row['Old']).exists()
result={'schema':1,'hullsUnchanged':checks,'mapSourcesUnchanged':maps,'kitRuntimeHashesMatch':len(kit),'isolatedRuntimeNames':len(runtime),'renameTargetsVerified':len(renames),'navigatorOriginalRigUnchanged':True,'nativeAcceptance':'Not tested. Art-only output; no C# or live Unity changes.'}
(R/'Art/Source/Art108/final-audit.json').write_text(json.dumps(result,indent=2));print('ART108 AUDIT PASSED: 5 hull hashes,5 baseline map sources,33 kit hashes,38 unique runtime names,shared rig original')

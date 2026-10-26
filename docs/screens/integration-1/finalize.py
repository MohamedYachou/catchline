import json,hashlib,struct,re,shutil
from pathlib import Path
out=Path(__file__).parent;root=out.parents[2];scratch=root.parent/'Catchline-sim'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((out/'source-before.json').read_text())
drift=[p for p,h in before.items() if not (root/p).exists() or sha(root/p)!=h]
matches=[]
for p in (root/'Assets/Scripts/Game').rglob('*.cs'):
 rel=p.relative_to(root).as_posix();sp=scratch/rel
 matches.append({'path':rel,'mainSha256':sha(p),'scratchSha256':sha(sp) if sp.exists() else None,'matches':sp.exists() and sha(sp)==sha(p)})
images=[]
for p in sorted(out.rglob('*.png')):
 width,height=struct.unpack('>II',p.read_bytes()[16:24]);images.append({'path':p.relative_to(out).as_posix(),'width':width,'height':height,'sha256':sha(p)})
for name in ['check-integration-1.log','map10-checks.json','map10-build.txt','check-integration-regression.log','check-integration-native-retry.log','integration-regression.json']:
 p=scratch/'Logs'/name
 if p.exists():shutil.copy2(p,out/name)
log=(out/'check-integration-1.log').read_text(errors='replace')
result={'productionBaselineFiles':len(before),'productionDrift':drift,'gameSourceMatches':matches,'images':images,'initialUnityExitMatches':re.findall(r'Exiting batchmode successfully now!|Exiting batchmode.*?returncode[^\r\n]*',log),'limits':['No production edits. Only scratch editor capture output directories and additive scratch fixtures differed.','The initial driver intentionally catches suite failures, so Unity exit0 is not a clean integration pass.','See suites.tsv and the subsequent original-wrapper regression for actual suite results.']}
(out/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Production drift:',drift,'Game source matches:',sum(x['matches'] for x in matches),'/',len(matches),'Images:',len(images));print([(x['path'],x['width'],x['height']) for x in images])

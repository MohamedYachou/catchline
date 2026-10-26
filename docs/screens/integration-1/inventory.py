import subprocess,json,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3]; out=Path(__file__).parent
def git(*args): return subprocess.check_output(['git',*args],cwd=root).decode('utf-8',errors='replace')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
status=git('status','--porcelain=v1','-uall')
(out/'status-before.txt').write_text(status,encoding='utf-8')
groups={k:[] for k in ['STRIKE-TAP-1','MAP9','MAP10','HARBOUR-PETS-1','shared','other/unassigned']}
shared=['Assets/Editor/ArtImport.cs','Assets/Scripts/Game/Data/Grounds.cs','Assets/Scripts/Game/GameData.cs','Assets/Scripts/Game/Minigame/VoyageRodView.cs','Assets/Scripts/Game/Sea/SeaNav.cs','Assets/Scripts/Game/VoyageGame.cs','Assets/Scripts/Game/VoyageScenery.cs']
for line in status.splitlines():
 p=line[3:].strip('"'); low=p.lower(); group='other/unassigned'
 if p in shared: group='shared'
 elif any(s in low for s in ['strike-fx','striketap','strikefx','voyagestrikefx']): group='STRIKE-TAP-1'
 elif any(s in low for s in ['map9','whaleshelf','whale-shelf']): group='MAP9'
 elif any(s in low for s in ['map10','sealcliffs','seal-cliffs']): group='MAP10'
 elif any(s in low for s in ['harbour-pets','harbourpets','petscapture','assets/art/models/harbourlife']): group='HARBOUR-PETS-1'
 groups[group].append({'status':line[:2],'path':p})
(out/'inventory.json').write_text(json.dumps(groups,indent=2),encoding='utf-8')
diff=git('diff','--unified=0','--',*shared)
(out/'shared-hunks.patch').write_text(diff,encoding='utf-8')
guids={};missing=[];duplicates={};new=[]
for p in (root/'Assets').rglob('*.meta'):
 m=re.search(r'^guid: ([0-9a-f]+)',p.read_text(encoding='utf-8-sig',errors='replace'),re.M)
 if m: guids.setdefault(m[1],[]).append(p.relative_to(root).as_posix())
for line in status.splitlines():
 p=line[3:].strip('"')
 if line[:2]!='??' or not p.startswith('Assets/'):continue
 target=root/p
 if p.endswith('.meta'):continue
 meta=Path(str(target)+'.meta')
 if not meta.exists():missing.append(p)
 else:
  m=re.search(r'^guid: ([0-9a-f]+)',meta.read_text(encoding='utf-8-sig',errors='replace'),re.M)
  new.append({'path':p,'guid':m[1] if m else None})
for g,ps in guids.items():
 if len(ps)>1:duplicates[g]=ps
(out/'meta-audit.json').write_text(json.dumps({'newAssets':new,'missingMetas':missing,'duplicateGuids':duplicates,'metaCount':sum(map(len,guids.values()))},indent=2),encoding='utf-8')
sources={p.relative_to(root).as_posix():sha(p) for p in (root/'Assets').rglob('*') if p.is_file() and p.suffix in ['.cs','.json','.fbx','.shader','.png','.meta']}
(out/'source-before.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
lines=['# Current-tree file inventory','', 'Generated from read-only git status; no index changes. Shared hunks are in shared-hunks.patch. Other/unassigned files are excluded from the four-delivery staging scope.','']
for group,items in groups.items():
 lines+=['## '+group,'','```text']+[x['status']+' '+x['path'] for x in items]+['```','']
(out/'inventory.md').write_text('\n'.join(lines),encoding='utf-8')
print({k:len(v) for k,v in groups.items()});print('missing metas',missing,'duplicate GUIDs',len(duplicates))

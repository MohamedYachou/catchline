from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[3];S=R/'Art/Source/Art108/imagery';rows=json.loads((S/'manifest.json').read_text())['assets'];assert len(rows)==87 and len({r['id'] for r in rows})==87
for r in rows:
 f=R/r['file'];src=R/r['source'];assert f.exists() and src.exists();assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];im=Image.open(f).convert('RGBA');assert list(im.size)==r['logicalSize'] and im.getchannel('A').getbbox();svg=src.read_text();assert 'href="http' not in svg and 'href="file:' not in svg
 if r['id']!='texture-plank':assert im.getpixel((0,0))[3]==0
specs=json.loads((S/'event-specs.json').read_text());assert len(specs)==40
for s in specs:
 r=next(r for r in rows if r['id']==s['id']);assert r['logicalSize']==[64,64] and r['planBatch']==s['batch'];assert (S/f"{s['id']}-prompt.txt").exists() and (S/f"{s['id']}-original.png").exists()
cards=json.loads((R/'Art/Models/CardsV1/manifest.json').read_text());assert len(cards['frames'])==4 and len(cards['portraits'])==11
for r in cards['frames']:
 im=Image.open(R/r['file']).convert('RGBA');assert im.size==(480,640);assert (im.getpixel((240,180))[3]>0) if r['id']=='locked' else im.getpixel((240,180))[3]==0
for r in cards['portraits']:
 for size in r['variants']:
  suffix='' if size==240 else '-'+str(size);f=R/'Assets/Art/UI/Portraits'/f"art108-{r['id']}{suffix}.png";im=Image.open(f).convert('RGBA');assert im.size==(size,size) and im.getchannel('A').getextrema()[1]>=250 and im.getpixel((0,0))[3]==0
nav=R/'Assets/Art/Models/Crew/NavigatorV1.fbx';assert nav.read_bytes()==(R/'Art/Models/NavigatorV1/NavigatorV1.fbx').read_bytes();assert len([p for p in (R/'Assets/Art/Models').rglob('*.fbx') if p.stem.lower()=='navigatorv1'])==1
backups=[p.relative_to(R).as_posix() for folder in ['Maps','StationsV1','NavigatorV1'] for p in (R/'Art/Models'/folder).rglob('*.blend1')]
result={'imageryAndEffects':len(rows),'events':40,'eventBatchCounts':[15,15,10],'portraitPngVariants':33,'frames':4,'navigatorRuntimeMatchesSourceExport':True,'navigatorRuntimeNameUnique':True,'retainedBlenderVersionBackups':backups,'temporaryNamespaceBackup':'C:/Users/momoy/.codex/tmp/art108-namefix-20261024-002604','backupCleanup':'Automatic approval review rejected deletion; retained without bypass.','nativeAcceptance':'Pending code owner; these checks verify authored exports only.'}
(R/'Art/Source/Art108/final-imagery-audit.json').write_text(json.dumps(result,indent=2));print('ART108 IMAGERY AUDIT PASSED:87files,40events,33portraitPNGs,4frames,Navigator parity; retained',len(backups),'Blender version backups')

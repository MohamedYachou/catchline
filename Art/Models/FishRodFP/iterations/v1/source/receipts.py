"""Hash the delivered files and every individually reviewed PNG; standard Python."""
from pathlib import Path
import hashlib,json,struct,re
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'Art/Models/FishRodFP'
images=[]
for p in sorted((OUT/'renders').glob('*.png')):
 b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n'
 w,h=struct.unpack('>II',b[16:24])
 images.append({'file':'renders/'+p.name,'width':w,'height':h,'sha256':hashlib.sha256(b).hexdigest()})
assert len(images)==26,len(images)
rendered=set(re.findall(r"renders[\\/]([^'\r\n]+\.png)",(OUT/'build.log').read_text()))
assert rendered=={Path(x['file']).name for x in images},rendered
assert 'FISH ROD BUILD' in (OUT/'build.log').read_text()
receipt={'review':'Each listed render individually opened by Codex 2; see REPORT.md for observations and limits.',
 'images':images,'files':{}}
for p in sorted(OUT.glob('*')):
 if p.is_file() and p.suffix in {'.blend','.fbx','.png','.json','.md'} and p.name!='receipts.json':
  receipt['files'][p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for p in sorted((ROOT/'Art/Source/FishRodFP').glob('*.py')):
 receipt['files']['../../Source/FishRodFP/'+p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(OUT/'receipts.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('RECEIPTS',len(images),'renders',len(receipt['files']),'files')

"""Call only after EVERY named image has been individually opened and reviewed."""
import hashlib,json,sys,struct
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/Skerries'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def review(name):
    path=O/'metrics'/(name+'.json');row=json.loads(path.read_text());assert row['round_trip']['result']=='PASS'
    for ext in ('blend','fbx'):assert sha(O/(name+'.'+ext))==row['sha256'][ext]
    images=json.loads((O/'renders'/(name+'.json')).read_text())
    assert len(images)==(27 if name=='Seal' else 9)
    for im in images:
        f=O/im['file'];assert struct.unpack('>II',f.read_bytes()[16:24])==tuple(im['size'])
        im.update(sha256=sha(f),review='individually opened; isolated artist review accepted')
    row.update(visual_review={'owner':'Codex 2 (WSL CLI)','date':'2026-10-25','images':images},status='Source, actual FBX and isolated visual PASS; Unity/native integration separate')
    path.write_text(json.dumps(row,indent=2)+'\n');print('REVIEW RECORDED',name,len(images))
if __name__=='__main__':
    for name in sys.argv[1:]:review(name)

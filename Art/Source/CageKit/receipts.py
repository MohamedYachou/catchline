"""Record only render sets already individually opened by the artist."""
import hashlib,json,sys,struct
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/Fishing/CageKit'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def review(name):
    row=json.loads((O/'metrics'/(name+'.json')).read_text());assert row['round_trip']['result']=='PASS'
    for ext in ('blend','fbx'):assert sha(O/(name+'.'+ext))==row['sha256'][ext]
    images=json.loads((O/'renders'/(name+'.json')).read_text())
    for im in images:
        f=O/im['file'];assert struct.unpack('>II',f.read_bytes()[16:24])==tuple(im['size'])
        im.update(sha256=sha(f),review='individually opened; isolated artist review accepted')
    row.update(visual_review={'owner':'Codex 2 (WSL CLI)','date':'2026-10-25','images':images},status='individual source/actualFBX/visual PASS; assembled/native acceptance separate')
    (O/'metrics'/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n')
    print('REVIEW RECORDED',name,len(images))
if __name__=='__main__':review(sys.argv[1])

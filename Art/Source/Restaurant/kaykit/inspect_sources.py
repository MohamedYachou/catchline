from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PACKS={p:ROOT/'Art/Downloads/kaykit'/p/'addons'/f'kaykit_{p}_bits' for p in ('restaurant','furniture')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result={}; baseline={}
for pack,base in PACKS.items():
    tex=next((base/'Assets').glob('texture*/*texture.png'))
    im=Image.open(tex).convert('RGB')
    uses=defaultdict(Counter)
    for obj in (base/'Assets/obj').glob('*.obj'):
        uv=[]
        for line in obj.read_text().splitlines():
            if line.startswith('vt '):uv.append(tuple(map(float,line.split()[1:3])))
            elif line.startswith('f '):
                points=[uv[int(v.split('/')[1])-1] for v in line.split()[1:] if '/' in v and v.split('/')[1]]
                if points:
                    u=sum(p[0] for p in points)/len(points);v=sum(p[1] for p in points)/len(points)
                    c=min(7,max(0,int(u*8)));r=min(3,max(0,int((1-v)*4)))
                    uses[f'R{r+1}C{c+1}'][obj.stem]+=1
    cells=[]
    for r in range(4):
        for c in range(8):
            cell=f'R{r+1}C{c+1}'
            cells.append(dict(id=cell,rect=[c*128,r*256,128,256],top=im.getpixel((c*128+64,r*256)),bottom=im.getpixel((c*128+64,r*256+255)),uses=dict(uses[cell].most_common())))
    result[pack]=dict(source=str(tex.relative_to(ROOT)),cells=cells)
    for p in base.rglob('*'):
        if p.is_file() and '.git' not in p.parts:baseline[str(p.relative_to(ROOT))]=sha(p)
(OUT/'source-inventory.json').write_text(json.dumps(result,indent=2))
(OUT/'preservation-baseline.json').write_text(json.dumps(baseline,indent=2))
for pack,info in result.items():
    print(pack)
    for cell in info['cells']:
        print(cell['id'],cell['top'],cell['bottom'],','.join(list(cell['uses'])[:9]))
print('Sealed',len(baseline),'original files')

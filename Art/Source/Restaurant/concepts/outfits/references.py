from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
IDS=['mira','dirk','ana','sam','ines','olaf']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sources=[]
    board=Image.new('RGB',(1440,1000),'#f4efe3'); d=ImageDraw.Draw(board)
    for col,id in enumerate(IDS):
        paths=[ROOT/f'Assets/Art/UI/v2-portrait-{id}-deck.png',ROOT/f'Art/Source/Restaurant/exact/s9/v2-s9-bust-{id}.png',ROOT/f'Art/Source/Restaurant/clothes/2d/{"mira-d" if id=="mira" else id}-front.png']
        for row,p in enumerate(paths):
            im=Image.open(p).convert('RGBA'); box=im.getbbox(); cut=im.crop(box); cut.thumbnail((220,280))
            board.paste(cut,(col*240+(240-cut.width)//2,row*330+32),cut)
            d.text((col*240+8,row*330+8),f'{id} / '+['deck','S9','restaurant'][row],fill='#173f57')
            sources.append(dict(path=str(p.relative_to(ROOT)),size=im.size,alpha=box,sha256=sha(p)))
    board.save(OUT/'identity-reference.jpg',quality=94)
    (OUT/'references.json').write_text(json.dumps(sources,indent=2))
    baseline={str(p.relative_to(ROOT)):sha(p) for base in [ROOT/'Art/Source/Restaurant/clothes',ROOT/'Art/Source/Restaurant/exact/s9'] for p in base.rglob('*') if p.is_file()}
    (OUT/'preservation-baseline.json').write_text(json.dumps(baseline,indent=2))
    print(json.dumps({'references':len(sources),'preservation':len(baseline),'root':str(ROOT)}))
if __name__=='__main__': main()

"""Export generated master without repainting; annotate a separate evidence sheet."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / 'Assets/Resources/Charts/outer-coast.png'
REFERENCE = ROOT / 'Assets/Resources/Charts/gull-coast.png'
SIZE = (1672, 941)
POINTS = {
    'Kelp forest': (.216, .278), 'Seal skerries': (.40, .24),
    'Lighthouse rock': (.66, .24), 'Whale shelf': (.06, .40),
    'Seal cliffs': (.24, .62), 'Wreck bank': (.72, .56),
    'Home harbour': (.483, .711),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if len(sys.argv) > 1:
        master = Path(sys.argv[1])
        prompt = (HERE / 'prompt-v1.txt').read_text() + '\n\nCORRECTION PASS:\n' + (HERE / 'prompt-v2.txt').read_text() + '\n\nLOCAL KEEP-CLEAR CORRECTION:\n' + (HERE / 'prompt-v3.txt').read_text()
        image = Image.open(master).convert('RGB')
        meta = PngImagePlugin.PngInfo()
        meta.add_text('Generation prompt', prompt)
        meta.add_text('Provenance', 'Built-in imagegen; Gull coast style reference. '
                      'Only Lanczos resize to delivery size; original master retained.')
        image.resize(SIZE, Image.Resampling.LANCZOS).save(OUTPUT, pnginfo=meta)
    chart = Image.open(OUTPUT).convert('RGB')
    assert chart.size == SIZE
    reference = Image.open(REFERENCE).convert('RGB')
    assert reference.size == SIZE
    marked = chart.copy()
    draw = ImageDraw.Draw(marked)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    def rect(box, color, width=3):
        draw.rectangle(tuple(round(v) for v in box), outline=color, width=width)
    for x0,x1 in ((0,.60),(.78,1)):
        rect((x0*SIZE[0],0,x1*SIZE[0]-1,.13*SIZE[1]), '#FFDE70')
    rect((0,.84*SIZE[1],SIZE[0]-1,SIZE[1]-1), '#FFDE70')
    for name,(nx,ny) in POINTS.items():
        x,y=nx*SIZE[0],ny*SIZE[1]
        draw.ellipse((x-8,y-8,x+8,y+8), fill='#E74663', outline='white', width=2)
        if name!='Home harbour':
            # Brief: approximate card keep-clear zone, immediately below pin.
            rect((max(0,x-100),y+31,min(SIZE[0]-1,x+100),y+31+.06*SIZE[1]), '#FFC94F',2)
        text=f'{name} ({nx:.3f}, {ny:.3f})'
        tx=min(max(6,x-100),SIZE[0]-285)
        ty=y-32 if name!='Home harbour' else y+15
        box=draw.textbbox((tx,ty),text,font=small)
        draw.rectangle((box[0]-3,box[1]-3,box[2]+3,box[3]+3),fill='#F4EFE3')
        draw.text((tx,ty),text,font=small,fill='#173F57')
    marked.save(HERE/'annotated.png')
    sheet=Image.new('RGB',(SIZE[0]*2,SIZE[1]+64),'#F4EFE3')
    sheet.paste(reference,(0,64));sheet.paste(marked,(SIZE[0],64))
    sd=ImageDraw.Draw(sheet)
    sd.text((24,12),'GULL COAST — unchanged style reference',font=font,fill='#173F57')
    sd.text((SIZE[0]+24,7),'OUTER COAST — seven pin centres / UI keep-clear bands',font=font,fill='#173F57')
    sd.text((SIZE[0]+24,35),'Pink/white = pin tip; yellow = quiet UI zones; annotations are evidence only.',font=small,fill='#173F57')
    sheet.save(HERE/'review.png')
    info={
        'output':str(OUTPUT.relative_to(ROOT)), 'size':list(chart.size),
        'mode':Image.open(OUTPUT).mode, 'output_sha256':sha(OUTPUT),
        'reference_sha256':sha(REFERENCE),
        'landmark_points':{n:{'normalized':list(p),'pixel':[round(p[0]*SIZE[0],3),round(p[1]*SIZE[1],3)]} for n,p in POINTS.items()},
        'review_size':list(sheet.size), 'review_sha256':sha(HERE/'review.png'),
        'runtime_acceptance':'Not tested; art-only delivery. Native integration belongs to Claude.',
    }
    (HERE/'validation.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info,indent=2))

if __name__ == '__main__':
    main()

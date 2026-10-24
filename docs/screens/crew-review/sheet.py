import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
hs = Path(sys.argv[1]); portraits = Path(sys.argv[2]); out = Path(sys.argv[3])
names = sys.argv[4].split(',')
f = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 30)
s = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 18)
views = ['front', 'q_left', 'left', 'back', 'right']
labels = ['front', '3/4 their left', 'their left side', 'back', 'their right side']
T = 300
for n in names:
    key = n.split('=')[0]; port = n.split('=')[-1]
    sheet = Image.new('RGB', (T * 6 + 70, T + 80), '#F4EFE3'); d = ImageDraw.Draw(sheet)
    d.text((20, 8), key, font=f, fill='#173F57')
    p = portraits / f'portrait-{port.lower()}.png'
    if p.exists():
        im = ImageOps.contain(Image.open(p).convert('RGB'), (T, T)); sheet.paste(im, (10, 55))
    d.text((14, T + 55), '2D portrait', font=s, fill='#173F57')
    for i, v in enumerate(views):
        q = hs / f'{key}_{v}.png'
        if q.exists():
            im = ImageOps.contain(Image.open(q).convert('RGB'), (T, T)); sheet.paste(im, (10 + (i + 1) * (T + 10), 55))
        d.text((14 + (i + 1) * (T + 10), T + 55), labels[i], font=s, fill='#173F57')
    sheet.save(out / f'{key}.png')

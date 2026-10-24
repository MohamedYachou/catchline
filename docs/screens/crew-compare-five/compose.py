from PIL import Image, ImageOps, ImageDraw, ImageFont
from pathlib import Path
import os

root = Path(__file__).resolve().parents[3]
out = root/'docs/screens/crew-compare-five'
fontdir = Path('C:/Windows/Fonts' if os.name == 'nt' else '/mnt/c/Windows/Fonts')
font = ImageFont.truetype(str(fontdir/'segoeui.ttf'), 25)
title = ImageFont.truetype(str(fontdir/'segoeuib.ttf'), 34)
names = [('Pim','Pim','r07'),('Dirk','Dirk','r04'),('Kofi','Kofi','r05'),('Mira','Mira-sol','r16'),('Lise','Lise','r03')]
overview = Image.new('RGB', (800, 5*470), '#F4EFE3')
for i,(name,folder,rev) in enumerate(names):
    pair = Image.new('RGB', (1600, 900), '#F4EFE3')
    d = ImageDraw.Draw(pair)
    d.text((36,16), name, font=title, fill='#173F57')
    for j,(label,path) in enumerate([
        ('Original 2D portrait',root/'Art/Source/UIv2/crew-styles'/f'portrait-{name.lower()}.png'),
        (f'3D model — {rev}',root/'Art/Models/CrewV2'/folder/'iterations'/rev/'face.png')]):
        im = Image.open(path).convert('RGB')
        im = ImageOps.contain(im,(770,770),Image.Resampling.LANCZOS)
        pair.paste(im,(j*800+(800-im.width)//2,75+(770-im.height)//2))
        d.text((j*800+28,853),label,font=font,fill='#173F57')
    pair.save(out/f'{name.lower()}-2d-vs-3d.png')
    small = ImageOps.contain(pair,(800,450),Image.Resampling.LANCZOS)
    overview.paste(small,(0,i*470))
overview.save(out/'five-2d-vs-3d.png')
print('Created five pairs and overview from original portraits and final face renders.')

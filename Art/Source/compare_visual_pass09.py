"""Python/Pillow: retain actual after previews and labelled comparisons."""
from pathlib import Path
import json, shutil
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/VisualPass09'
font=ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),24)
assets=json.loads((ROOT/'Art/Models/DayBoatKit/build-metrics.json').read_text())['assets']
(OUT/'After').mkdir(exist_ok=True)
names=['DayBoat','Crane','PowerHauler','IceMachine','SortingChute','GuttingTable']
sheet=Image.new('RGB',(1024,6*570),'#F4EFE3')
draw=ImageDraw.Draw(sheet)
for row,name in enumerate(names):
    asset=next(a for a in assets if a['asset']==name)
    shutil.copy2(ROOT/asset['preview'],OUT/'After'/f'{name}.png')
    for col,stage in enumerate(['Before','After']):
        sheet.paste(Image.open(OUT/stage/f'{name}.png').convert('RGB'),(col*512,row*570+58))
        draw.text((col*512+16,row*570+14),f'{name} / {stage}',font=font,fill='#173F57')
sheet.save(OUT/'Before-after.png')
print('Comparisons complete; individual views auto-fit each asset, scale review uses real metres.')

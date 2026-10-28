"""Pair native KIT-2 captures for review; originals are never rescaled or overwritten."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SHOTS = ROOT / 'docs/screens/ui-v3/kit-2'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('group')
    parser.add_argument('stages', nargs='+')
    args = parser.parse_args()
    font = ImageFont.truetype(str(ROOT / 'Assets/Resources/Fonts/Fredoka-SemiBold.ttf'), 22)
    for stage in args.stages:
        for size in (1440, 844):
            name = f'{stage}-{size}.png'
            paths = (SHOTS / 'before' / name, SHOTS / args.group / name)
            frames = [Image.open(p).convert('RGB') for p in paths]
            assert frames[0].size == frames[1].size, (name, 'native sizes differ')
            width = 960
            height = round(frames[0].height * width / frames[0].width)
            sheet = Image.new('RGB', (width * 2 + 36, height + 68), '#163A5E')
            draw = ImageDraw.Draw(sheet)
            for i, (label, frame) in enumerate(zip(('Before', 'Restaurant v3 kit'), frames)):
                x = 12 + i * (width + 12)
                draw.text((x, 12), f'{label} · {stage} · {size}', font=font, fill='#F4EFE3')
                sheet.paste(frame.resize((width, height), Image.Resampling.LANCZOS), (x, 52))
            path = paths[1].with_name(f'{stage}-{size}-pair.png')
            sheet.save(path)
            print(path.relative_to(ROOT))

if __name__ == '__main__':
    main()

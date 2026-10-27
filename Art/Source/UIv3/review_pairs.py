"""Build review sheets from untouched native before/after evidence (no game changes)."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SHOTS = ROOT / 'docs/screens/ui-v3'
FONT = ROOT / 'Assets/Resources/Fonts/Fredoka-SemiBold.ttf'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('group')
    parser.add_argument('stages', nargs='+')
    args = parser.parse_args()
    font = ImageFont.truetype(str(FONT), 22)
    for stage in args.stages:
        for size in (1440, 844):
            name = f'{stage}-{size}.png'
            before = SHOTS / 'before' / name
            after = SHOTS / 'after' / args.group / name
            if not before.exists():
                continue  # Additional TEST states have no incumbent fixture.
            frames = [Image.open(p).convert('RGB') for p in (before, after)]
            width = 960
            height = round(frames[0].height * width / frames[0].width)
            sheet = Image.new('RGB', (width * 2 + 36, height + 68), '#163A5E')
            draw = ImageDraw.Draw(sheet)
            for i, (label, frame) in enumerate(zip(('Before', 'Restaurant v3 kit'), frames)):
                x = 12 + i * (width + 12)
                draw.text((x, 12), f'{label} · {stage} · {size}', font=font, fill='#F4EFE3')
                sheet.paste(frame.resize((width, height), Image.Resampling.LANCZOS), (x, 52))
            sheet.save(after.with_name(f'{stage}-{size}-pair.png'))
            print(after.with_name(f'{stage}-{size}-pair.png').relative_to(ROOT))

if __name__ == '__main__':
    main()

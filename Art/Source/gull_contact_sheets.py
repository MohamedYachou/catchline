"""WSL: compose Blender previews, with group sheets and concept comparison."""
from pathlib import Path
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Art/Models/GullHarbour'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
assets = json.loads((OUT / 'build-metrics.json').read_text())['assets']


def compose(items, title, destination, columns, reference=False, caption='Actual meshes / 45 deg down / 35 deg yaw / individually framed'):
    w, card_h = 320, 350
    columns = min(columns, len(items))
    rows = math.ceil(len(items) / columns)
    width, height = columns * w, rows * card_h
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    for item in items:
        args += ['-i', str(ROOT / item['preview'])]
    if reference:
        args += ['-i', str(ROOT / 'Art/Concepts/15-gull-harbour-tier1.png')]
    filters = []
    for i, item in enumerate(items):
        filters.append(f'[{i}:v]scale=320:320,pad=320:350:0:0:color=0xF4EFE3,'
                       f'drawtext=fontfile={FONT}:text=\'{item["asset"]} | {item["triangles"]} tris\':'
                       f'fontcolor=0x173F57:fontsize=15:x=(w-tw)/2:y=327[p{i}]')
    inputs = ''.join(f'[p{i}]' for i in range(len(items)))
    layout = '|'.join(f'{i % columns * w}_{i // columns * card_h}' for i in range(len(items)))
    filters.append(inputs + f'xstack=inputs={len(items)}:layout={layout}:fill=0xF4EFE3[grid]')
    if reference:
        filters.append(f'[{len(items)}:v]scale={width}:-1,pad={width}:{height}:0:(oh-ih)/2:color=0xF4EFE3[concept]')
        filters.append('[grid][concept]hstack=inputs=2[content]')
    else:
        filters.append('[grid]null[content]')
    final_width = width * (2 if reference else 1)
    filters.append(f'[content]pad={final_width}:{height + 100}:0:60:color=0xF4EFE3,'
                   f'drawtext=fontfile={FONT}:text=\'{title}\':fontcolor=0x173F57:fontsize=24:x=20:y=17,'
                   f'drawtext=fontfile={FONT}:text=\'{caption}\':'
                   f'fontcolor=0x173F57:fontsize=17:x=20:y={height + 73}[out]')
    args += ['-filter_complex', ';'.join(filters), '-map', '[out]', '-frames:v', '1', str(destination)]
    subprocess.run(args, check=True)


for group in dict.fromkeys(a['group'] for a in assets):
    chosen = [a for a in assets if a['group'] == group]
    if len(chosen) == 1:
        # xstack needs >=2 inputs. The rowboat already has its own detailed render.
        continue
    compose(chosen, 'GULL HARBOUR / ' + group.upper(), OUT / 'Previews' / f'{group}-contact.png', 4)
compose(assets, 'GULL HARBOUR / ACTUAL ASSETS + CONCEPT REFERENCE', OUT / 'Previews/ContactSheet.png', 6, True)
print('Saved Gull Harbour group and overview contact sheets.')

# Task 04 boat inspection views and a focused build-2 handoff.
by_name={a["asset"]:a for a in assets}
if "Skiff" in by_name:
    kit=[by_name[n] for n in ("Skiff","HandWinch","GillNetCoil","GillNetFloatLine","GillNetSection","SortTable")]
    compose(kit,"GULL HARBOUR / SKIFF KIT",OUT/"Previews/SkiffKit-contact.png",3)
    views=[]
    for name in ("Rowboat","Skiff"):
        views.append(by_name[name])
        for view in ("Top","Side","Front","OpenHold"):
            path=OUT/"Previews/Boats"/f"{name}-{view}.png"
            if path.exists():
                views.append({"asset":f"{name}-{view}","triangles":by_name[name]["triangles"],"preview":path.relative_to(ROOT).as_posix()})
    compose(views,"BOAT SILHOUETTES / ORTHOGRAPHIC CHECKS",OUT/"Previews/BoatViews-contact.png",3,caption="Actual meshes / top, port side, front and open hold / orthographic")

"""Compose Blender-rendered previews beside their approved concept, using ffmpeg.

Run from WSL: python3 Art/Source/make_prop_contact_sheet.py
This does not generate, retouch or substitute model geometry.
"""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PREVIEWS = ROOT / 'Art/Models/Props/Previews'
NAMES = ['Crab', 'BandedCrab', 'EmptyPot', 'FullPot', 'Crate', 'Buoy']
LABELS = ['Crab', 'Banded crab', 'Empty pot', 'Full pot', 'Crate', 'Buoy']
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
data = json.loads((ROOT / 'Art/Models/Props/build-metrics.json').read_text())
counts = {p['prop']: p['triangles'] for p in data['props']}
args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
for name in NAMES:
    args += ['-i', str(PREVIEWS / (name + '.png'))]
args += ['-i', str(ROOT / 'Art/Concepts/13-crab-coast-props.png')]
filters = []
for i, (name, label) in enumerate(zip(NAMES, LABELS)):
    filters.append(f'[{i}:v]scale=512:512,pad=512:552:0:0:color=0xF4EFE3,'
                   f'drawtext=fontfile={FONT}:text=\'{label} | {counts[name]} tris\':'
                   f'fontcolor=0x173F57:fontsize=20:x=(w-tw)/2:y=520[p{i}]')
filters.append('[p0][p1][p2][p3][p4][p5]xstack=inputs=6:'
               'layout=0_0|512_0|1024_0|0_552|512_552|1024_552[left]')
filters.append('[6:v]scale=1536:1024,pad=1536:1104:0:40:color=0xF4EFE3[right]')
filters.append('[left][right]hstack=inputs=2,pad=3072:1204:0:60:color=0xF4EFE3,'
               f'drawtext=fontfile={FONT}:text=\'BLENDER MESHES / ORTHOGRAPHIC GAME CAMERA\':'
               'fontcolor=0x173F57:fontsize=27:x=30:y=17,'
               f'drawtext=fontfile={FONT}:text=\'APPROVED CONCEPT / STYLE REFERENCE\':'
               'fontcolor=0x173F57:fontsize=27:x=1566:y=17,'
               f'drawtext=fontfile={FONT}:text=\'45 deg down / 35 deg yaw. Individually framed; exact sizes and budgets in REPORT.md.\':'
               'fontcolor=0x173F57:fontsize=20:x=30:y=1176[out]')
args += ['-filter_complex', ';'.join(filters), '-map', '[out]', '-frames:v', '1',
         str(PREVIEWS / 'ContactSheet.png')]
subprocess.run(args, check=True)
print(PREVIEWS / 'ContactSheet.png')

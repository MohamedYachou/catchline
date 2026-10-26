"""Independently validate the recovered C export and complete its handoff."""
from pathlib import Path
from PIL import Image
import hashlib
import json
import shutil

S = Path(__file__).resolve().parent
R = S.parents[3]
out = R / 'Art/Source/BoatsV2/ui/v2-item-hull-jig.png'
master = Image.open(S / 'card-master.png')
card = Image.open(out)
assert master.mode == 'RGBA' and card.mode == 'RGBA' and card.size == (480, 360)
alpha = card.getchannel('A')
assert alpha.getextrema() == (0, 255)
assert alpha.getbbox() == (35, 24, 445, 336)
assert all(alpha.getpixel(p) == 0 for p in [(0, 0), (479, 0), (0, 359), (479, 359)])
box = master.getchannel('A').point(lambda x: 255 if x > 8 else 0).getbbox()
crop = master.crop(box)
crop.thumbnail((432, 312), Image.Resampling.LANCZOS)
expected = Image.new('RGBA', (480, 360))
expected.alpha_composite(crop, ((480 - crop.width) // 2, (360 - crop.height) // 2))
assert expected.tobytes() == card.tobytes()
sha = hashlib.sha256(out.read_bytes()).hexdigest()
v = json.loads((S / 'card-validation.json').read_text())
assert v['sha256'] == sha
v['visual_review'] = ('PASS: final card and Skiff/Jig/Prep comparison opened during C resume. '
    'Eight bulbs, cable, three reels, enclosed forward wheelhouse and clear deck read. '
    'Full silhouette and alpha margins clear; navy/ivory/honey palette and shaded volume fit accepted cards. '
    'Subject checked against delivered game-exact-45. Asset-level review only, no native UI acceptance.')
v['independent_checks'] = dict(exact_master_export_pixel_parity=True,
    transparent_corners=True, dimensions_rgba_alpha_margin_sha256=True)
v['provenance'] = ('Existing built-in imagegen master and exact prompt-card.txt recovered from previous '
    'session. No generation this resume.')
(S / 'card-validation.json').write_text(json.dumps(v, indent=2) + '\n')
report = R / 'Art/Models/BoatsV2/JigBoatV1/REPORT.md'
old = '## C. Refit card\nPending B visual review.'
text = report.read_text()
if old in text:
    backup = S / 'REPORT.pre-C.tmp'
    shutil.copy2(report, backup)
    new = f'''## C. Refit card — complete

Delivered `Art/Source/BoatsV2/ui/v2-item-hull-jig.png`, **480×360 RGBA**, alpha0–255, visible bounds(35,24)–(445,336). SHA256 `{sha}`.

Recovered the already generated master and export from the interrupted session; no regeneration or geometry changes in the C resume. Built-in imagegen provenance and exact full prompt are preserved in `Art/Source/BoatsV2/JigBoat/prompt-card.txt`; original1448×1086RGBA output in `card-master.png`. `export_card.py` crops the alpha>8 master bounds, scales within432×312 and centres the asset with Lanczos resampling, preserving alpha. Independent reconstruction matched every output pixel; dimensions, transparent corners, margins and saved SHA checked.

Opened final card individually and `Art/Source/BoatsV2/JigBoat/card-review.png` (1440×410) beside accepted Skiff and Prep cards. Checked subject against delivered `renders/game-exact-45.png`: eight bulbs on one connected wire, two short masts, three rail reels, compact enclosed wheelhouse, sorting tray and open deck all read. Navy/ivory/honey palette, shaded volume and restrained local dark illustration edges match the refit-card family. No clipping, background, stray shadow, text or extra gear visible. Card camera is a different quarter from the neighbouring cards, following the model reference so its lamp wire and reels remain separated and visible; not an equal-scale boat comparison.

`card-validation.json` records the checks; `card-receipt.json` hashes the card, master, exact prompt, exporter, independent finishing script, comparison, validation and this report. No in-game UI placement or native acceptance claimed. A/B remain as previously delivered:5635tri/13000cap, no geometry/export changes.
'''
    report.write_text(text.replace(old, new))
    assert old not in report.read_text()
    backup.unlink()
assert '## C. Refit card — complete' in report.read_text()
paths = [out, S/'card-master.png', S/'prompt-card.txt', S/'export_card.py',
    Path(__file__).resolve(), S/'card-review.png', S/'card-validation.json', report]
receipt = {'task':'JIG-BOAT-1 C', 'owner':'Codex 2 (WSL CLI)', 'files':{
    str(p.relative_to(R)): {'bytes':p.stat().st_size,
    'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths}}
(S/'card-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
for name, entry in receipt['files'].items():
    assert hashlib.sha256((R/name).read_bytes()).hexdigest() == entry['sha256']
print('PASS C: exact pixel reconstruction;480x360RGBA;alpha0-255;transparent corners;margins;8receipt hashes;report complete.', sha)

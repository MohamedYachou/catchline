"""Generate honest integration sheets from measured source manifest and packaging audit."""
from pathlib import Path
from PIL import Image
import json,hashlib,ast
ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'manifest.json').read_text()); S=json.loads((ROOT/'text-styles.json').read_text())
A=json.loads((ROOT/'asset-audit.json').read_text())
lookup={e['name']:e for e in M}
occurrences=[
 ('v2-plan-dish-card',3,[405,162,122,123],'soup card'),
 ('v2-plan-dish-card',3,[533,162,122,123],'coffee card'),
 ('v2-accent-rays',3,[258,169,31,39],'Mira planning emphasis; rotate to source'),
 ('v2-paper-row',3,[275,292,376,61],'bring-back inset'),
 ('v2-divider',3,[512,312,5,33],'catch request separator'),
 ('v2-icon-guests',3,[431,257,21,20],'soup guest forecast'),
 ('v2-icon-guests',3,[550,257,21,20],'coffee guest forecast'),
 ('v2-icon-tick',3,[704,193,25,27],'accept button check; cream glyph'),
 ('v2-btn-back',4,[13,6,53,46],'square back control; nine-slice'),
 ('v2-icon-back',4,[25,16,29,25],'back arrow'),
 ('v2-paper-row',4,[81,207,244,89],'second fish row'),
 ('v2-paper-row',4,[359,112,435,55],'portion row 1; slice to rect'),
 ('v2-paper-row',4,[359,169,435,56],'portion row 2'),
 ('v2-paper-row',4,[359,227,435,55],'portion row 3'),
 ('v2-btn-minus',4,[570,170,52,51],'soup minus'),
 ('v2-btn-minus',4,[570,228,52,51],'fillets minus'),
 ('v2-btn-plus',4,[734,169,57,52],'soup plus'),
 ('v2-btn-plus',4,[734,227,57,52],'fillets plus'),
 ('v2-number-field',4,[629,170,99,38],'soup quantity'),
 ('v2-number-field',4,[629,228,99,38],'fillet quantity'),
 ('v2-bar-track',4,[628,208,102,14],'soup track'),
 ('v2-bar-track',4,[628,266,102,14],'fillets track'),
 ('v2-bar-knob',4,[661,206,12,18],'soup thumb'),
 ('v2-bar-knob',4,[662,264,12,18],'fillet thumb'),
 ('v2-toggle-unselected',4,[692,285,80,30],'+20% selector'),
 ('v2-btn-primary',4,[631,322,200,58],'Prepare button; nine-slice'),
 ('v2-divider',4,[473,331,5,41],'market/captain separator'),
 ('v2-metric-row',5,[129,65,191,31],'served count row'),
 ('v2-metric-row',5,[129,141,191,42],'drinks row'),
 ('v2-metric-row',5,[129,183,191,43],'tips row'),
 ('v2-metric-row',5,[129,290,195,70],'cats row'),
 ('v2-review-card',5,[327,132,219,64],'review row 2'),
 ('v2-review-card',5,[327,200,219,66],'review row 3'),
 ('v2-review-card',5,[327,288,219,70],'crew of the night row'),
 ('v2-icon-guests',5,[148,68,28,26],'served guests'),
 ('v2-dish-closing-fish',5,[140,101,56,34],'closing dishes metric'),
 ('v2-icon-coin-service',5,[276,329,20,20],'cat food value coin'),
 ('v2-btn-primary',5,[531,317,190,57],'Sleep button; nine-slice'),
 ('v2-star-full',5,[681,149,28,28],'progress endpoint star'),
 ('v2-star-full',5,[396,74,18,18],'review 1 stars start; repeat pitch 19.5, count 5'),
 ('v2-star-full',5,[396,142,18,18],'review 2 stars start; repeat pitch 19.5, count 4'),
 ('v2-star-full',5,[396,210,18,18],'review 3 stars start; repeat pitch 19.5, count 4'),
 ('v2-star-empty',5,[474,142,18,18],'review 2 fifth empty star'),
 ('v2-star-empty',5,[474,210,18,18],'review 3 fifth empty star')]
(ROOT/'layout.json').write_text(json.dumps(dict(canvas=[844,390],origin='top-left',
    measured_assets=[{k:e[k] for k in ('name','screen','rect','size','borders')} for e in M],
    repeated_instances=[dict(name=n,screen=s,rect=r,use=u) for n,s,r,u in occurrences]),indent=2))
lines=['# Restaurant exact S3–S5 source-art handoff','',
 'Owner: Codex 1 (Windows app). Reference authority: `../../concepts/ui-3-mira-plan.png`, `ui-4-prep.png`, `ui-5-closing.png`. The r10 captures are comparison evidence, not style authority.','',
 '## Delivery status','',
 f"{A['packaged']}/{len(M)} named pieces packaged. Final visual review status is recorded in `visual-review.json`; inventory/hash checks are in `asset-audit.json`. This report must not be read as lead/Mo acceptance or runtime integration.",'',
 'All artwork uses the built-in imagegen tool. `provenance/<name>.json` records each exact prompt, reference paths and saved original. `provenance/<name>.png` preserves the untouched generator result. Mechanical packaging only trims alpha, proportionately fits/pads the canvas, and builds comparisons; it does not repaint/recolour artwork. The three full-bleed backgrounds and prep top strip are opaque by design. The top strip uses source crop [0,0,2154,275] to exclude unrelated white padding, then a proportional bottom-aligned fit; its untouched original is retained.','',
 '## Integration','',
 'No `Assets/`, `.meta`, `.cs`, Git, player save or watchdog changes. Claude chooses/imports the art and draws all text. Keep original metas on replacement. Shared existing names are retained here; S1/S2 alternatives belong to Codex 2, so the lead must choose shared button/icon/sign variants deliberately.','',
 'Coordinates use top-left origin on the 844×390 mockup, including illustrated overflow/shadows. They are hand-measured outer visual rectangles, typically within 1–3 px, not source layout metadata. `layout.json` lists repeated pieces too. This scope has no separate desktop mockup: S2 1440×900 desktop belongs to Codex 2. Do not multiply these into a desktop layout without checking the lead’s responsive composition.','',
 'Mira originals extend the mockup’s cropped upper-body poses to full figures as requested. Keep the mockup upper-body placement with an appropriate clip; fitting an entire standing figure into the original torso rectangle would shrink her face. Fish are single painted whole species, right-facing, 1024×512; crab/flatfish are shown from above. Extra three guest portraits are companion designs because only three review faces appear in S5.','',
 '## Slice borders','',
 'Borders are exact source-pixel import recommendations **L / T / R / B**, not Unity vector order (L / B / R / T). Rect sizes above are logical pixels. Use the source-pixel borders directly for import; canvases are not universally exactly3x. Use a centered pivot for ordinary cards. Keep all native canvases and avoid import trimming when applying these values.','',
 '| Piece | Canvas | L / T / R / B | Rule |','|---|---:|---|---|']
for e in M:
    if e['borders']:
        lines.append(f"| {e['name']} | {e['size'][0]}×{e['size'][1]} | {' / '.join(map(str,e['borders']))} | Preserve corners; stretch only centre/edges |")
lines+=['','The wood title sign, paper request ticket, Mira speech bubble, fish sign, characters and illustrations are **uniform-scale only**: ropes/lantern/pin/tail are authored decorations and must not be stretched. Panels with header bands preserve that band in their top border. Icons inside plus/minus buttons must remain square. Review panel sizes should remain close to the measured ratio; excessive paper-height stretch changes its shading.','',
 '## Text style sheet','',
 'The mockup contains painted lettering; an exact font identity is unproven. Use Fredoka Bold (700) / SemiBold (600), if available, as the closest runtime starting point, then compare actual captures. Sizes, strokes and shadows below are measured visual estimates in mockup pixels, **not** a verified font raster match. Scale size, outline width and shadow offset together at device resolution. UI text remains live. All general body numerals/labels are heavy navy.','',
 '| Style / screen | Visible text | Weight / px | Fill | Stroke hex / px | Shadow dx,dy / hex |','|---|---|---|---|---|---|']
for s in S['styles']:
    lines.append(f"| {s['id']} / S{s['screen']} | {s['text'].replace(chr(10),'<br>')} | {s['weight']} / {s['size']} | {s['fill']} | {s['stroke']} / {s['stroke_width']} | {s['shadow'][0]},{s['shadow'][1]} / {s['shadow'][2]} |")
lines+=['','Selected forecast pills use #FFF8E8 with ~0.7 px navy outline; unselected use navy. The secondary popularity line uses #687A7D. Each text rectangle and these overrides are in `text-styles.json`.','',
 '## Piece layout and inventory','',
 '| Name | Screen | x,y,w,h at 844×390 | PNG canvas |','|---|---|---|---|']
for e in M: lines.append(f"| {e['name']} | S{e['screen']} | {','.join(map(str,e['rect']))} | {e['size'][0]}×{e['size'][1]} |")
lines+=['','### Additional placements','', '| Piece | Screen | x,y,w,h | Use |','|---|---|---|---|']
for n,s,r,u in occurrences: lines.append(f"| {n} | S{s} | {','.join(map(str,r))} | {u} |")
lines+=['','## Inspection and known limits','',
 'Every review pair in `review/<name>.png` places the actual mockup crop on the left and packaged piece on the right. `review/contact-s3-*.png`, `contact-s4-*.png`, `contact-s5-*.png` group four pairs per sheet. Labels/context in the reference crop are intentionally retained; final live text is removed. The report does not count an image as reviewed merely because a file exists: actual opened sheets and findings are logged in `visual-review.json`.','',
 'Native generator resolution varies by piece; exact original and final dimensions and upscale flags are recorded in `asset-audit.json`. A larger output canvas is not a claim of native painted detail. Generation may vary in contour, face, plate/food detail or backdrop reconstruction; exact-match findings remain part of manual review, rather than being implied by a passing alpha/hash check.','',
 '## Reproduce packaging','',
 '`uv run --with pillow python Art/Source/Restaurant/exact/s3-s5/build_manifest.py` regenerates reference crops/manifest only. `package.py` packages completed generator sources without overwriting finals. `report.py` regenerates these measured handoff tables. `seal.py` performs the final independent file/inventory checks. Original generation is not silently repeated by these helpers.']
lines+=['','## Native resolution disclosure','',
 'These canvases exceed at least one original generator dimension. They meet the requested export sizes through proportionate resampling; they do not contain native detail at the export resolution. Both Mira originals are 1122x1402, exported to 1600x2000.','',
 '| Piece | Original generator pixels | Export canvas |','|---|---|---|']
for r in A['assets']:
    if r['upscaled_canvas']:
        lines.append(f"| {r['name']} | {'x'.join(map(str,r['native_source']))} | {'x'.join(map(str,r['canvas']))} |")
lines+=['','## Art-bounds import copies','', 'Claude requested tightly cropped artwork after integrating the first exports. Use `tight/<name>.png` with `tight-layout.json` for those imports. These retain the SAME90piece names; there are no new sprite keys. Canonical root files retain the requested Mira/fish canvas sizes. Tight copies crop the alpha>=8 artwork bounds and uniformly resample only enough to meet >=3x EACH primary/repeated placement. Their crop, actual dimensions, resample factor, exact source-pixel L/T/R/B borders and hashes are recorded per asset. Low-alpha antialias/shadow inside the crop remains. These larger tight canvases do not add painted detail.', '', 'Canonical slice coordinates now include the measured transparent margins; tight slice coordinates exclude those margins. The tight copy keeps the measured visual placement rectangle; do not add canonical padding offsets again. The conservative border reserves keep header bands/corners; very thin tracks cap vertical borders so the middle remains stretchable. Use the source-pixel table matching the actual imported file.', '', '| Tight import piece | PNG canvas | L / T / R / B |', '|---|---|---|']
for e in json.loads((ROOT/'tight-layout.json').read_text())['assets']:
    if e['borders']: lines.append(f"| {e['name']} | {e['size'][0]}x{e['size'][1]} | {' / '.join(map(str,e['borders']))} |")
lines+=['','### Manual findings','']
for finding in json.loads((ROOT/'visual-review.json').read_text()).get('findings',[]): lines.append('- '+finding)
(ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print('REPORT.md / layout.json updated')

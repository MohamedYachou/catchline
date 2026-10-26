"""Build the handoff tables from measured layouts and audited source receipts."""
from pathlib import Path
import json, math
R=Path(__file__).resolve().parent
def read(n,default=None):
 p=R/n
 return json.loads(p.read_text()) if p.exists() else default
audit=read('asset-audit.json',[])
reviews=read('visual-review.json',{})
styles=read('text-styles.json')['styles']
layout=read('layout.json')
no_slice=('icon','bust','item-rest','bubble','btn-rotate','btn-confirm','btn-cancel','meter-ring','timeline-curve','placement-highlight')
slices={}
for a in audit:
 n=a['name']; w,h=a['size']
 if not any(s in n for s in no_slice):
  # Symmetric conservative edge bands enclose the entire bevel and corners.
  edge=math.ceil(min(w,h)*.30)
  if n.startswith('v2-bar-'): edge=min(48,math.ceil(h*.25))
  side=math.ceil(h*.5) if any(t in n for t in ('wallet','meter-track','meter-fill','speed-pill')) else edge
  slices[n]={'sourceSize':[w,h],'borderLTRB':[side,edge,side,edge],
    'units':'exported PNG source pixels, origin top left',
    'center':'stretch; preserve edge/corner texels',
    'minimumDestinationPx':[2*side+1,2*edge+1]}
(R/'slices.json').write_text(json.dumps(slices,indent=2)+'\n')
lines=['# RESTAURANT-UI-EXACT-1 — Codex 2 (WSL CLI)',
 '', '**Work in progress.** This report is generated from the current artifact set. Final completeness and visual status are recorded below; a generated sprite is not native/runtime acceptance.',
 '', 'Scope: S1 Arrange, S2 phone and desktop Service, service Mira bust, all 18 existing deck crew identities. Output folder only; no Assets, metas, C#, save, git or 3D changes.',
 '', 'Only style references: `Art/Source/Restaurant/concepts/ui-1-arrange.png`, `ui-2-service.png`, `ui-service-desktop.png`. Original deck portraits supply crew identity. `layout.json` records native mockup coordinates: phone 844×390, desktop 1440×900. Rectangles use top-left x/y, width/height. Placement measurements and the font match are visual estimates from raster references, not extracted vector metadata.',
 '', 'Artwork: imagegen with intrinsic alpha. Packaging: FFmpeg crop/resize/transparent padding and technical contacts only. Pillow reads metadata and alpha extents; it does not paint artwork. Every generated source and receipt is retained in `provenance/`. The alpha>=32 contour locates the artwork crop with a 12-source-pixel halo; no alpha keying or recoloring is applied. Six transparent export pixels surround the fitted artwork.',
 '', 'PNG canvas dimensions are at least three times every listed mockup placement. `asset-audit.json` explicitly reports source upscaling: canvas resolution does not imply native generated detail at that size. No UI labels are baked; pictorial currency marks/checks/arrows are integral icons.',
 '', '## Pieces and review status', '', '| Name | Export px | Primary reference x,y,w,h | Screen | Native source enlarged | Open/review |', '|---|---:|---|---|---|---|']
for a in audit:
 r=reviews.get(a['name'],{})
 lines.append(f"| [{a['name']}]({a['file']}) | {'×'.join(map(str,a['size']))} | {','.join(map(str,a['referenceRect']))} | {a.get('referenceScreen') or 'crew identity'} | {'yes' if a['sourceUpscaled'] else 'no'} | {r.get('status','pending')} |")
lines += ['', '## Nine-slice borders', '', 'Values below are L/T/R/B in final PNG source pixels. Do not use normalized values. Preserve corners and stretch the center. Illustrations, circles, arrows, placement balloons, rings, curves and speech bubbles are single sprites; their shapes must not be sliced. Full-width bars may crop their endcaps at the viewport edge.', '', '| Sprite | Source L/T/R/B | Minimum destination px |', '|---|---|---|']
for n,s in slices.items():lines.append(f"| {n} | {' / '.join(map(str,s['borderLTRB']))} | {'×'.join(map(str,s['minimumDestinationPx']))} |")
lines += ['', '## Text style sheet', '', 'Font implementation match: Fredoka Bold / SemiBold (`Assets/Resources/Fonts`) and Fredoka Medium (`Assets/Art/UI/Fonts`), inferred from the mockup. Use the listed native-screen size, fill and stroke; desktop values are measured in 1440×900 pixels, phone values in 844×390 pixels. Weight500 uses Medium, 600 SemiBold, 700 Bold. These labels must be drawn by runtime.', '', '| Screen | Text | Weight | Size px | Fill | Stroke / px | Shadow x,y,color |', '|---|---|---:|---:|---|---|---|']
for s in styles:
 lines.append(f"| {s['screen']} | {s['text']} | {s['weight']} | {s['size']} | {s['fill']} | {s['stroke']} / {s['strokeWidth']} | {', '.join(map(str,s['shadow']))} |")
lines += ['', 'Selected Guests tab: ivory fill #FFF8EB, burnt-orange stroke #8A330C at0.7phone px; unselected category labels navy. Other state-specific overrides are retained in `text-styles.json`.', '', '## Layout sheet', '', '| Screen | Asset | x | y | w | h |', '|---|---|---:|---:|---:|---:|']
for p in layout['placements']:
 lines.append('| '+p['screen']+' | '+p['asset']+' | '+' | '.join(map(str,p['rect']))+' |')
lines += ['', '## Limits and handoff', '', '- `review/<sprite>-compare.png`: actual source reference crop beside the delivered sprite. Crew contacts use the original deck portrait, since the mockup does not depict all18 identities.', '- `visual-review.json`: per-image openings, findings, and corrections. A review can record a mismatch; opening alone does not imply an exact match.', '- Rounded-font identification and source pixel measurements are inferred. Reconstructed art can differ from the raster mockup; do not label source checks as Mo\'s acceptance.', '- No Unity import, runtime HUD screenshot, layout assembly or native-device acceptance performed in this output-only task. Integration belongs to Claude.', '- No commit. No subagents. Source/machinery stays in this owned directory; other agents\' artifacts are preserved.', '']
(R/'REPORT.md').write_text('\n'.join(lines))
print(json.dumps({'reportAssets':len(audit),'sliceEntries':len(slices),'styles':len(styles),'placements':len(layout['placements'])}))

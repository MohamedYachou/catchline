from pathlib import Path
import hashlib,json,math,shutil
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[4];O=R/'Art/Models/Maps/GullKelpForest';S=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((O/'SeaV2-sand-edges-audit.json').read_text());assert a['all_passed']
for ext in ('blend','fbx'):assert sha(O/f'GullKelpForestSeaV2.{ext}')==a['sha256'][ext]
assert sha(O/'navigation.json')==a['navigation_sha256_unchanged']
rows=json.loads((O/'SeaV2-sand-edges-comparisons.json').read_text());assert len(rows)==12
images=[]
for row in rows:
 w,h=row['capture_resolution'];pair=Image.open(O/row['comparison']).convert('RGB');assert pair.size==(w*2,h+40)
 for key,x in [('before',0),('after',w)]:
  im=Image.open(O/row[key]).convert('RGB');assert im.size==(w,h)
  assert ImageChops.difference(pair.crop((x,40,x+w,h+40)),im).getbbox() is None
 for key in ('before','after','comparison'):
  p=O/row[key];images.append({'file':p.name,'size':list(Image.open(p).size),'sha256':sha(p),'opened_individually':True})
assert len(images)==36 and len({v['file'] for v in images})==36
review={'reviewer':'Codex 2 (WSL CLI)','all_36_images_individually_opened':True,'source_sha256':a['sha256'],'images':images,'findings':['Three distinct rounded irregular 24-segment outlines replace orthogonal staircase edges.','Two narrow sand/seabed transition bands visible at both requested image sizes.','Kelp and posts stay fixed; no visible surface holes or seams.'],'limits':['Blender direct surface inspection, without water, boat or HUD. Deck45 and top framing show entire clearing (ortho34m desktop,48m phone); not native camera or optical acceptance.','Footprint tolerance measured by bounds and centroid. Individual staircase-notch boundary displacement exceeds0.5m; see audit and REPORT.','Unity import and native acceptance remain integrating lead scope.']}
(O/'SeaV2-sand-edges-visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
p=O/'REPORT.md';text=p.read_text();text=text.replace('current runtime export GullKelpForestSeaV2.fbx has 71,766 triangles and 299 meshes.','accepted baseline export had 71,766 triangles and 299 meshes; the current sand-edge source export GullKelpForestSeaV2.fbx has 73,242 triangles and the same 299 meshes (see Sand edges below; Unity reimport pending).')
assert '## Sand edges' not in text
lines=['','## Sand edges','', 'MAP11-SAND-EDGES-ART-1 — Codex 2 (WSL CLI), 2026-10-26. Only ConnectedBathymetry geometry and its sand/transition material assignments changed. Each of the three clearings now uses a rounded irregular 24-segment outline, with two inward radial bands of 0.32 m each. Their colours mix the existing sand and seabed at sand factors 0.67 and 0.33; the sand interior and surrounding teal retain the existing materials. Original triangle planes preserve the raised bed, anchor pockets and heights. No navigation data changed.','', 'Independent accepted/new source reopen and actual-FBX import [audit](SeaV2-sand-edges-audit.json) passes: all 306 other objects (298 meshes and eight empties) match exactly, including geometry, materials, transforms and hierarchy. All 299 exported mesh bounds match. Units remain 1.0 and navigation SHA-256 remains `'+a['navigation_sha256_unchanged']+'`. Bidirectional surface deviation maxima are 0.000007634 m and 0.000003815 m; source-to-FBX maximum vertex deviation is 0.000017643 m. The audit contains the complete mesh bounds and anchor matrix tables.','', 'Triangle accounting: 71,766 accepted baseline → 73,242 current export (+1,476, +2.06%). ConnectedBathymetry is 12,298 → 13,774; all other meshes retain their counts. The inherited REPORT gives an actual count, not a separate numerical cap. The working check used 75,000 as a conservative ceiling; this is not a claim that the lead specified that budget.','', '| Clearing | Centroid shift (m) | Maximum bounds shift (m) | Old/new area (m²) | Boundary Hausdorff (m) |','|---|---:|---:|---:|---:|']
for i,v in enumerate(a['patches'],1):
 shift=math.dist(v['centre_before'],v['centre_after']);bd=max(abs(x-y) for x,y in zip(v['bounds_before'],v['bounds_after']))
 lines.append(f"| {i} | {shift:.3f} | {bd:.3f} | {v['area_before']:.2f} / {v['area_after']:.2f} | {v['boundary_hausdorff_m']:.3f} |")
lines+=['', 'Footprint interpretation: the ±0.5 m check applies to bounding extents and centroid position. It does **not** hold for every old staircase boundary point: rounding the deep notches moves individual boundary points by the Hausdorff distances above (1.396–1.891 m). This interpretation and the missing explicit numerical budget were recorded as QUESTION/checkpoint lines for the lead; pointwise footprint compliance is not claimed.','', 'Evidence: [12 old/new comparison pairs](SeaV2-sand-edges-comparisons.json), [visual review](SeaV2-sand-edges-visual-review.json), and [delivery receipt](SeaV2-sand-edges-receipt.json). All 24 captures and 12 unscaled side-by-side sheets were opened individually: three grounds × top/deck45 × 1440×900/844×390. The irregular outlines and narrow two-step transitions read at both sizes, with fixed kelp/posts and no visible holes. These are direct Blender surface inspections without water, boat or HUD, framed to show the full clearing; they do not reproduce native water optics or establish native gameplay acceptance. Claude owns Unity reimport and runtime review. Older audits/native images linked above describe the historical baseline, not this new export.','', 'Reproducible helpers and accepted geometry snapshot live in Art/Source/Maps/GullKelpForest/. The accepted binary backup was temporary and removed after successful audit and evidence checks; rerunning the old-source Blender comparison requires restoring the accepted baseline into the documented scratch location. The JSON snapshot is retained as the exact geometry audit fixture. No Unity, Assets, .meta, C#, git or player-save changes; no commit.','']
p.write_text(text.rstrip()+'\n'+'\n'.join(lines))
backup=R.parent/'Catchline-sim/Backups/codex2-sand-edges-before';assert backup.name=='codex2-sand-edges-before'
if backup.exists():shutil.rmtree(backup)
assert not backup.exists()
files=[O/'GullKelpForestSeaV2.blend',O/'GullKelpForestSeaV2.fbx',O/'REPORT.md']+sorted(x for x in O.glob('SeaV2-sand-edges-*') if x.name!='SeaV2-sand-edges-receipt.json')+sorted(x for x in S.iterdir() if x.is_file())
receipt={'owner':'Codex 2 (WSL CLI)','checks_passed':True,'scratch_binary_backup_removed':True,'no_commit':True,'native_acceptance':False,'files':[{'path':str(x.relative_to(R)),'sha256':sha(x),'bytes':x.stat().st_size} for x in files]}
(O/'SeaV2-sand-edges-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
for v in receipt['files']:assert sha(R/v['path'])==v['sha256']
print('SEALED',len(files),'files; 36 decoded images; 24 exact comparison slices; audit/source/nav hashes PASS; backup removed')

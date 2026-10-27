"""Measured coverage additions and user-requested mechanical tight crops only."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, shutil, hashlib
R=Path(__file__).resolve().parent; S=R.parent/'s1-s2'; C=R.parents[1]/'concepts'
p=S/'layout.json'; bak=R/'layout.before.json'
if not bak.exists(): shutil.copy2(p,bak)
d=json.loads(bak.read_text()); rows=d['placements']; crops=[]; remap={}
for name in sorted({r['asset'] for r in rows}):
    if (S/(name+'.png')).exists(): continue
    src=S/'provenance'/(name+'-generated.png')
    assert src.exists(),src
    dst=name.replace('v2-','v2-s12x-',1); remap[name]=dst
    im=Image.open(src).convert('RGBA'); box=im.getchannel('A').getbbox(); assert box
    art=im.crop(box); used=[r['rect'] for r in rows if r['asset']==name]
    scale=max(max(r[2]*3/art.width,r[3]*3/art.height) for r in used)
    # Preserve source contour and alpha, no painting, no empty canvas allowance.
    wh=(max(1,round(art.width*scale+.499)),max(1,round(art.height*scale+.499)))
    art=art.resize(wh,Image.Resampling.LANCZOS)
    # Lanczos may create a tiny transparent edge; remove it for art-own bounds.
    art=art.crop(art.getchannel('A').getbbox()); art.save(R/(dst+'.png'))
    shutil.copy2(S/'provenance'/(name+'-receipt.json'),R/(dst+'-source-receipt.json'))
    crops.append(dict(asset=dst,source=str(src.relative_to(R.parents[4])),crop=list(box),size=list(art.size),method='exact nonzero-alpha bounding crop then uniform Lanczos upscale; no new art',nativeDetailUpscaled=scale>1))
for r in rows:
    if r['asset'] in remap:r['asset']=remap[r['asset']]

def add(screen,asset,rect,use):
    rows.append(dict(screen=screen,asset=asset,rect=rect,use=use,source='Codex1 native-raster visual measurement'))
for asset,rect,use in [
('v2-item-rest-table2',[663,144,39,25],'selected-table-name-tag-thumbnail'),
('v2-icon-coin-arrange',[432,331,20,21],'catalog-table2-coin'),
('v2-icon-coin-arrange',[591,331,20,21],'catalog-table4-coin'),
('v2-icon-coin-arrange',[756,331,20,21],'catalog-booth-coin'),
('v2-s12x-icon-tile2',[759,355,22,12],'catalog-booth-footprint'),
]:add('arrange',asset,rect,use)
for asset,rect,use in [
('v2-timeline-guest',[235,15,14,17],'timeline-guest-1'),
('v2-timeline-guest',[303,10,15,22],'timeline-guest-3'),
('v2-timeline-guest',[412,10,15,20],'timeline-future-guest-4'),
('v2-timeline-guest',[441,14,14,17],'timeline-future-guest-5'),
('v2-meter-track',[71,162,75,11],'stock-soup-track'),
('v2-meter-track',[71,227,75,11],'stock-coffee-track'),
('v2-meter-fill',[72,228,41,10],'stock-coffee-fill'),
('v2-meter-fill',[81,356,58,11],'cook-progress'),
('v2-meter-fill',[249,356,52,11],'server-progress'),
('v2-meter-fill',[412,356,29,11],'fix-progress-green'),
('v2-meter-fill',[574,356,49,11],'coffee-progress'),
('v2-bust-jo',[22,324,52,50],'cook-portrait'),
('v2-bust-ana',[188,324,52,50],'server-portrait'),
('v2-bust-bram',[354,324,52,50],'fix-portrait'),
('v2-bust-ines',[519,324,52,50],'barista-portrait'),
('v2-icon-cup',[537,154,24,27],'coffee-order-bubble'),
('v2-guest-patience-arc',[402,129,59,18],'fish-table-patience'),
('v2-guest-patience-arc',[524,139,48,17],'coffee-table-patience'),
]:add('phone',asset,rect,use)
for asset,rect,use in [
('v2-meter-ring-fill',[490,785,63,62],'server-ring'),
('v2-meter-ring-fill',[999,785,63,62],'coffee-ring'),
('v2-meter-ring-fill',[1316,785,63,62],'reception-ring'),
('v2-icon-fish-stock',[632,369,36,24],'bottom-left-fish-order'),
('v2-icon-fish-stock',[1001,384,39,26],'bottom-right-fish-order'),
('v2-icon-cup',[953,180,28,26],'upper-coffee-order'),
('v2-bust-jo',[56,770,76,87],'cook-portrait'),
('v2-bust-ana',[311,770,76,87],'server-portrait'),
('v2-bust-bram',[589,770,76,87],'fix-portrait'),
('v2-bust-ines',[842,770,76,87],'barista-portrait'),
('v2-bust-mira',[1104,769,87,88],'reception-portrait'),
('v2-guest-patience-arc',[573,383,53,29],'bottom-left-near-patience'),
('v2-guest-patience-arc',[679,383,55,29],'bottom-left-far-patience'),
('v2-guest-patience-arc',[935,386,53,31],'bottom-right-near-patience'),
('v2-guest-patience-arc',[1015,349,49,28],'bottom-right-far-patience'),
]:add('desktop',asset,rect,use)
# Remove exact duplicate placements from source; retain each genuinely repeated use.
dedup=[]; seen=set(); counts={}
for r in rows:
    key=(r['screen'],r['asset'],tuple(r['rect']))
    if key in seen:continue
    seen.add(key); pair=(r['screen'],r['asset']); counts[pair]=counts.get(pair,0)+1
    r.setdefault('use',f"{r['screen']}-{r['asset'].removeprefix('v2-')}-{counts[pair]:02}")
    dedup.append(r)
d['placements']=dedup
d['assetRoots']=['.','../s1-s2-extra']
d['handoffNotes']=['Do not rerun s1-s2/metadata.py: it predates the Codex1 measured additions. Preserve/merge this file.','v2-s12x-* live in ../s1-s2-extra and are unique names. Other art remains owned by Codex2.','Repeated placements are separately named with use. Composite timeline curves already contain their nodes; no duplicate nodes are added.','Scene furniture/3D staff and diner bodies are world art, not foreground sprite placements. Name-tag thumbnail and catalogue furniture are UI.','Portrait identity slots inferred from the depicted hats; lead may bind the same slot to live crew data. Future timeline guest silhouettes use the same art with lower opacity; fill arcs/progress are runtime-clipped.','Rects are visual estimates in native mockup coordinates; full alpha art crops are disclosed, not vector-perfect match or runtime acceptance.']
issues=[]
for r in dedup:
    sw,sh=d['screens'][r['screen']]['size']; x,y,w,h=r['rect']
    if min(x,y)<0 or min(w,h)<=0 or x+w>sw or y+h>sh:issues.append(['bounds',r])
    if not any((root/(r['asset']+'.png')).exists() for root in (S,R)):issues.append(['missing',r['asset']])
assert not issues,issues
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
(R/'crop-manifest.json').write_text(json.dumps(crops,indent=2)+'\n')
slices={c['asset']:{'sourceSize':c['size'],'borderLTRB':[0,0,0,0],'sliceMode':'single sprite; do not nine-slice icons or arcs'} for c in crops}
(R/'slices.json').write_text(json.dumps(slices,indent=2)+'\n')
(R/'layout-audit.json').write_text(json.dumps(dict(placements=len(dedup),uniqueAssetKeys=len({r['asset'] for r in dedup}),allResolved=True,boundsPass=True,allUsesNamed=True,uniqueNewNames=list(remap.values()),issues=issues),indent=2)+'\n')
# Annotated measurement evidence only; no authored artwork is altered.
t=json.loads((S/'text-styles.json').read_text())
for screen,info in d['screens'].items():
    im=Image.open(C/info['file']).convert('RGB'); draw=ImageDraw.Draw(im)
    for r in t['styles']:
        if r['screen']!=screen or 'instances' in r:continue
        x,y,w,h=r['rect'];draw.rectangle((x,y,x+w,y+h),outline='#ff33dd',width=1)
    im.save(R/f'text-measurements-{screen}.jpg')
    im=Image.open(C/info['file']).convert('RGB'); draw=ImageDraw.Draw(im)
    for r in dedup:
        if r['screen']!=screen:continue
        x,y,w,h=r['rect']; draw.rectangle((x,y,x+w,y+h),outline='#00ff9a',width=1)
    im.save(R/f'layout-measurements-{screen}.jpg')
for c in crops:
    asset=c['asset']; r=next(r for r in dedup if r['asset']==asset)
    x,y,w,h=r['rect']; ref=Image.open(C/d['screens'][r['screen']]['file']).crop((x,y,x+w,y+h)).convert('RGBA')
    art=Image.open(R/(asset+'.png')); board=Image.new('RGB',(600,240),'#d4cec1')
    for n,im in enumerate((ref,art)):
        im.thumbnail((270,190));board.paste(im,(n*300+(300-im.width)//2,20),im)
    ImageDraw.Draw(board).text((10,215),asset+' | source crop / tight generated export',fill='black')
    board.save(R/(asset+'-compare.jpg'))
print('placements',len(dedup),'new tight exports',len(crops),'all resolved')

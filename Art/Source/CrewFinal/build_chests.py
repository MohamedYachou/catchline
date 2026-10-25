"""Export packaging only: retain generated RGBA; fit to transparent 512px canvas."""
from package import *
sources={
 'crate-closed':ROOT/'Art/Source/Chests/generated/v2-chest-t1-closed.png',
 **{n:OUT/'generated'/f'{n}.png' for n in ['crate-open','sea-closed','sea-open','captain-closed','captain-open']}}
files=[];checks={}
for n,p in sources.items():
 im=Image.open(p).convert('RGBA');bbox=im.getchannel('A').getbbox();cut=im.crop(bbox)
 # Uniform max extent and common bottom baseline support the reveal transition.
 cut.thumbnail((448,448),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',(512,512));out.alpha_composite(cut,((512-cut.width)//2,480-cut.height))
 name=f'v2-chest-{n}.png';out.save(OUT/name);files.append(name)
 checks[n]=dict(source=str(p.relative_to(ROOT)),sourceSize=list(im.size),sourceBounds=bbox,exportBounds=out.getchannel('A').getbbox(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
(OUT/'chest-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
inventory('D',files,'BUILT — pending opened contact review. Built-in imagegen: five new images using crate/closed-state references. Existing source crate-closed reused. Generated RGBA preserved; only export fit/resampling onto 512px transparent canvas, common baseline 480. Full prompts in chest-prompts.json, originals in generated/.')
sheet('D',files,cols=2,refs=[ROOT/'Assets/Art/UI/v2-icon-coin.png',ROOT/'Assets/Art/UI/v2-icon-anchor.png',ROOT/'Assets/Art/UI/v2-portrait-mira.png'])
report()

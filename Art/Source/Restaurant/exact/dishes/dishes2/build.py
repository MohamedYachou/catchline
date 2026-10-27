"""Read-only dish inventory and measured source-art proofs for DISHES-2."""
from pathlib import Path
import hashlib, json, re
from PIL import Image, ImageDraw, ImageFont, ImageOps

P = Path(__file__).resolve().parent
ROOT = P.parents[5]
EX = P.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name, value): (P/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
def rel(p): return p.relative_to(ROOT).as_posix()
FONT = ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
source = ROOT/'Assets/Scripts/Game/VoyageRestaurantDay.cs'
body = source.read_text(encoding='utf-8-sig').split('DishLook = new()')[1].split('};')[0]
rows = re.findall(r'\[Dish\.(\w+)\] = \("([^"]+)", "([^"]+)", "([^"]+)"\)', body)
assert len(rows)==13
if not (P/'preservation-baseline.json').exists():
    paths = list(EX.rglob('*.png')) + list((ROOT/'Assets/Art/UI').glob('*dish*.png'))
    dump('preservation-baseline.json', {rel(p):sha(p) for p in paths if P not in p.parents})
entries=[]
for dish, name, key, fallback in rows:
    choices=[EX/'dishes'/(key+'.png'), EX/'s3-s5/tight'/(key+'.png')]
    src=next(p for p in choices if p.is_file())
    imported=ROOT/'Assets/Art/UI'/('rx-'+key[3:]+'.png')
    assert imported.is_file(), key
    a=Image.open(src).convert('RGBA'); b=Image.open(imported).convert('RGBA')
    identical=a.size==b.size and a.tobytes()==b.tobytes()
    entries.append(dict(dish=dish, label=name, key=key, fallback=fallback,
        source=rel(src), sourceSha256=sha(src), sourceSize=list(a.size),
        sourceAlphaBounds=list(a.getchannel('A').getbbox()), importedAlphaBounds=list(b.getchannel('A').getbbox()),
        imported=rel(imported), importedSha256=sha(imported), importedSize=list(b.size),
        sourceEqualsImportPixels=identical,
        nominal3x=all(v%3==0 for v in a.size),
        sourcePolicy='Existing accepted painting reused read-only. No new raster or repaint.'))
dump('manifest.json', entries)

def fit(im, box):
    return ImageOps.contain(im, box, Image.Resampling.LANCZOS)
def text(canvas, xy, s, size=13):
    ImageDraw.Draw(canvas).text(xy,s,font=ImageFont.truetype(str(FONT),size*3),fill='#173F57')
layouts=[]
for screen, slots in [('s6',[(84,47),(74,45),(68,45)]), ('s3',[(110,75)])]:
    # Each cell repeats a dish at every actual screen slot size, not enlarged thumbnails.
    width=844; cellw=274; cellh=142 if screen=='s6' else 125
    height=58+5*cellh
    out=Image.new('RGBA',(width*3,height*3),'#EAE3D4')
    text(out,(18*3,12*3),f'{screen.upper()} menu art - actual device sizes',21)
    text(out,(18*3,39*3),' / '.join(f'{w} x {h} px' for w,h in slots),12)
    for i,e in enumerate(entries):
        x=16+(i%3)*cellw; y=65+(i//3)*cellh
        text(out,(x*3,y*3),e['label'],14)
        im=Image.open(ROOT/e['imported']).convert('RGBA')
        for j,(w,h) in enumerate(slots):
            bx=x+j*88; by=y+27
            scaled=fit(im,(w*3,h*3))
            px=bx*3+(w*3-scaled.width)//2; py=by*3+(h*3-scaled.height)//2
            out.alpha_composite(scaled,(px,py))
            if screen=='s6':text(out,(bx*3,(by+h+6)*3),f'{w}x{h}',10)
            layouts.append(dict(name=e['key'],screen=screen,use=f'contact-{i}-slot-{j}',
                rect=[bx,by,w,h],paintedRect3x=[px,py,*scaled.size]))
    out.convert('RGB').save(P/f'{screen}-contact-3x.png')
    out.resize((width,height),Image.Resampling.LANCZOS).convert('RGB').save(P/f'{screen}-contact-actual-size.jpg',quality=97)
dump('layout.json',dict(origin='top-left',unit='logical device pixels',placements=layouts,
    notes='Contact-sheet cells; screen slots measured from source/mockup. Each dish preserves aspect. Not native screenshots.'))
dump('text-styles.json',dict(styles=[],notes='Dish icons have no baked labels. Contact-sheet captions are review-only.'))
dump('build-result.json',dict(menuEntries=len(entries),newPaintings=0,
    sourceImportPixelMatches=sum(e['sourceEqualsImportPixels'] for e in entries),
    actualSizes=dict(s6=[[84,47],[74,45],[68,45]],s3=[[110,75]]),
    limits='Saved source/import pixels only. HasUi, live appearance, input, import metadata and Unity mapping not runtime-tested.'))
print(json.dumps(json.loads((P/'build-result.json').read_text()),indent=2))

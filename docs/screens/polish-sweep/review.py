"""Record images only AFTER Codex has individually opened them; generate linked index."""
import sys,json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
path=ROOT/'visual-review.json'
data=json.loads(path.read_text()) if path.exists() else {'reviewer':'Codex 1 (Windows app)','method':'Each listed PNG individually opened with view_image; frozen native ScreenCapture, no manual touch/animation acceptance.','frames':{}}
if len(sys.argv)>1:
    section=sys.argv[1]
    for stem in sys.argv[2:]:
        for width in (1440,844):
            p=ROOT/f'section-{section}'/f'{stem}-{width}.png'
            with Image.open(p) as im: size=list(im.size)
            data['frames'][p.relative_to(ROOT).as_posix()]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':size,'individually_opened':True}
    path.write_text(json.dumps(data,indent=2)+'\n')
lines=['| Frame | Desktop | Phone |','|---|---|---|']
stems=sorted({s.rsplit('-',1)[0] for s in data['frames']})
for stem in stems:
    lines.append('| '+stem+' | '+ ' | '.join(f'[{w}]({stem}-{w}.png)' for w in (1440,844))+' |')
(ROOT/'reviewed-index.md').write_text('\n'.join(lines)+'\n')
print(f'{len(data["frames"])} individually opened frames recorded')

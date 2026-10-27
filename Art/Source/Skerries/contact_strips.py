"""Run with catchline-ui venv Python. Compose already rendered action samples."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/Skerries'
out=O/'renders/Seal'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
rows=json.loads((O/'renders/Seal.json').read_text())
rows=[r for r in rows if not r['view'].endswith('contact-strip')]
for action,end in [('Bask',121),('Look',91),('Slide',37)]:
    canvas=Image.new('RGB',(2400,422),'#173F57');d=ImageDraw.Draw(canvas)
    d.text((14,8),f'{action} | '+('loop' if action!='Slide' else 'one shot')+f' | {(end-1)/30:g} s | 30 fps',fill='#F3F0DC',font=font)
    for i,frame in enumerate([1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end]):
        im=Image.open(out/f'action-{action}-{i}.png');canvas.paste(im,(480*i,34));d.text((480*i+12,396),f'f{frame}  {(frame-1)/30:.2f} s',fill='#F3F0DC',font=font)
    path=out/f'{action}-contact-strip.png';canvas.save(path)
    rows.append({'file':path.relative_to(O).as_posix(),'view':f'{action}-contact-strip','size':[2400,422],'action':action})
(O/'renders/Seal.json').write_text(json.dumps(rows,indent=2)+'\n')

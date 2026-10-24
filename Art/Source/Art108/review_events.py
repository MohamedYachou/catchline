from pathlib import Path
import json,textwrap
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];S=R/'Art/Source/Art108/imagery';specs=json.loads((S/'event-specs.json').read_text());summary=[]
for batch in [1,2,3]:
 rows=[s for s in specs if s['batch']==batch];sheet=Image.new('RGB',(1100,((len(rows)+4)//5)*135),'#ede7d9');d=ImageDraw.Draw(sheet);present=0
 for i,row in enumerate(rows):
  x=i%5*220;y=i//5*135;file=R/'Assets/Art/UI/v2'/f"art108-{row['id']}.png"
  if file.exists():
   im=Image.open(file).convert('RGBA');assert im.size==(64,64);d.rectangle((x+110,y+4,x+210,y+90),fill='#12394f');sheet.paste(im,(x+18,y+13),im);sheet.paste(im,(x+128,y+13),im);present+=1
  else:d.text((x+20,y+24),'pending',fill='#98744b')
  label=row['id'].replace('event-','');d.multiline_text((x+8,y+96),'\n'.join(textwrap.wrap(label,26)),fill='#173f57')
 sheet.save(S/f'events-batch-{batch}-review.png');summary.append(dict(batch=batch,delivered=present,expected=len(rows)))
(S/'event-review-counts.json').write_text(json.dumps(summary,indent=2));print(summary)

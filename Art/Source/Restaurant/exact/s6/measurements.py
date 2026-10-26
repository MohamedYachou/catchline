"""Reference rect overlays for human measurement review, not artwork."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
P=Path(__file__).resolve().parent
src=Image.open(P/'../../concepts/ui-6-dashboard.png').convert('RGB').resize((1688,780))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
for kind,key,fn in [('text','styles','text-styles.json'),('layout','placements','layout.json')]:
    data=json.loads((P/fn).read_text(encoding='utf-8'))[key]
    for start in range(0,len(data),18):
        im=src.copy();d=ImageDraw.Draw(im)
        for i,it in enumerate(data[start:start+18],start+1):
            x,y,w,h=it['rect'];box=[2*x,2*y,2*(x+w),2*(y+h)]
            d.rectangle(box,outline='#FF18ED',width=2)
            d.rectangle((2*x,2*y,2*x+25,2*y+15),fill='#FF18ED')
            d.text((2*x+2,2*y),str(i),font=font,fill='white')
        out=Image.new('RGB',(1688,1020),'#F5EDDB');out.paste(im)
        d=ImageDraw.Draw(out)
        for k,it in enumerate(data[start:start+18]):
            d.text((15+(k%3)*558,790+(k//3)*35),str(start+k+1)+' '+it.get('id',it.get('name',''))+' '+it.get('use',''),font=font,fill='#162B42')
        out.save(P/(kind+'-measure-'+str(start//18+1)+'.jpg'),quality=93)
print('measurement sheets written')

from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;G=P.parent
im=Image.new('RGB',(880,235),'#F4EFE3');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
names=['hazel','ada','09','10','11','12','13','14','15','16']
for i,name in enumerate(names):
 x=12+i*87;a=Image.open(G/('v2-guest-'+name+'.png')).convert('RGBA')
 for sz,y in [(64,45),(32,137)]:
  b=a.resize((sz,sz),Image.Resampling.LANCZOS);im.paste(b,(x+(64-sz)//2,y),b)
 d.text((x,17),name,font=font,fill='#173F57')
d.text((12,192),'Accepted Hazel/Ada at left; eight additional guests at 64px and 32px.',font=font,fill='#173F57')
im.save(P/'reference-comparison.jpg',quality=97)

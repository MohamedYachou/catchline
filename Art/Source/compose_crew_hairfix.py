raise RuntimeError('REJECTED recovery draft; do not publish these reviews. Original builders own corrections.')
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json
R=Path(__file__).resolve().parents[2];O=R/'docs/screens/crew-hairfix';O.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',26)
bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',32)
sheet=Image.new('RGB',(1800,4*650),'#F4EFE3');d=ImageDraw.Draw(sheet)
for row,(name,folder,rev) in enumerate([('Pim','Pim','r07'),('Dirk','Dirk','r04'),('Mira','Mira-sol','r16'),('Lise','Lise','r03')]):
    base=R/'Art/Models/CrewV2'/folder;pre=base/'iterations/hair-strands-01';y=row*650
    d.text((20,y+6),name,font=bold,fill='#173F57')
    for col,(path,label) in enumerate([(base/'iterations'/rev/'face.png','Before'),(pre/'face.png','After'),(pre/'temple-left.png','After — side coverage')]):
        im=ImageOps.contain(Image.open(path).convert('RGB'),(580,560),Image.Resampling.LANCZOS)
        sheet.paste(im,(col*600+(600-im.width)//2,y+52));d.text((col*600+20,y+612),label,font=font,fill='#173F57')
    review=Image.new('RGB',(1800,3*650),'#F4EFE3');review.paste(sheet.crop((0,y,1800,y+650)),(0,0));rd=ImageDraw.Draw(review)
    for k,view in enumerate(['temple-right','back-hair','side','front','walk','idle']):
        xx=(k%3)*600;yy=650+(k//3)*650
        im=ImageOps.contain(Image.open(pre/(view+'.png')).convert('RGB'),(580,580),Image.Resampling.LANCZOS)
        review.paste(im,(xx+(600-im.width)//2,yy));rd.text((xx+20,yy+600),view.replace('-',' ').title(),font=font,fill='#173F57')
    review.save(base/(name+'-review.png'));review.save(pre/(name+'-review.png'))
    (base/'hairfix-review.json').write_text(json.dumps({'revision':'hair-strands-01','views':['face','temple-left','temple-right','back-hair','front','side','back','walk','idle'],'review':name+'-review.png'},indent=2))
sheet.save(O/'four-before-after.png')
# Additional side/back evidence for Lise's density correction.
base=R/'Art/Models/CrewV2/Lise';panel=Image.new('RGB',(1800,1280),'#F4EFE3');pd=ImageDraw.Draw(panel)
for k,(rev,view,label) in enumerate([('r03','side','Lise — before'),('hair-strands-01','side','Lise — after'),('hair-strands-01','back-hair','After — back'),('r03','face','Before — face'),('hair-strands-01','face','After — face'),('hair-strands-01','temple-right','After — other side')]):
    x=(k%3)*600;y=(k//3)*640
    im=ImageOps.contain(Image.open(base/'iterations'/rev/(view+'.png')).convert('RGB'),(580,580),Image.Resampling.LANCZOS)
    panel.paste(im,(x+(600-im.width)//2,y));pd.text((x+15,y+593),label,font=font,fill='#173F57')
panel.save(O/'lise-density.png')
print('Hairfix review sheets composed')

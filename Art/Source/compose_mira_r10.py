"""Compose the inspected model renders and supplied portrait into a review sheet."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/CrewV2/Mira-sol'
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);args=p.parse_args()
PRE=OUT/'iterations'/args.revision
W=2400;C=600;G=14;HEADER=126
rows=[780,700,660,540,780];H=HEADER+sum(rows)+G*6
im=Image.new('RGB',(W,H),'#102C41');d=ImageDraw.Draw(im)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',31)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
man=json.loads((OUT/'build-manifest.json').read_text())
d.text((24,18),'MIRA / SOL — '+args.revision.upper(),font=bold,fill='#FFF2D1')
d.text((24,67),f"{man['triangles']:,} triangles  |  original 20-bone CrewRig / 11 actions  |  r09 front preserved",font=font,fill='#DCE7EB')
used=[]
def panel(file,label,x,y,w,h):
    path=file if isinstance(file,Path) else PRE/(file+'.png')
    source=Image.open(path).convert('RGB');source.load();used.append((str(path.relative_to(ROOT)),hashlib.sha256(path.read_bytes()).hexdigest()))
    d.rounded_rectangle((x+G,y,x+w-G,y+h),radius=10,fill='#EAE4D7')
    d.text((x+G+15,y+12),label,font=font,fill='#173F57')
    source.thumbnail((w-G*2-12,h-60),Image.Resampling.LANCZOS)
    im.paste(source,(int(x+(w-source.width)/2),int(y+52+(h-60-source.height)/2)))
y=HEADER+G
for i,(f,t) in enumerate([('front','Front'),('three-quarter','Three-quarter'),('side','Side'),('back','Back')]):panel(f,t,i*C,y,C,rows[0])
y+=rows[0]+G
for i,(f,t) in enumerate([(ROOT/'docs/screens/crew-styles/mira-ref/mira-portrait.jpg','Portrait reference'),('face','Face — r09 unchanged'),('back-hair','Rear hair close-up'),(ROOT/'docs/screens/crew-styles/mira-ref/mira-fullbody.jpg','Full-body reference')]):panel(f,t,i*C,y,C,rows[1])
y+=rows[1]+G
panel('female-body-comparison','Original male shape (left) / female shape (right)',0,y,1200,rows[2])
panel('same-scale','Current crew (left) / Mira (right): same scale',1200,y,1200,rows[2])
y+=rows[2]+G
panel('female-torso-comparison','Torso: male left / female right',0,y,1200,rows[3])
panel('female-profile-comparison','Profile: male left / female right',1200,y,1200,rows[3])
y+=rows[3]+G
for i,(f,t) in enumerate([('idle','Idle / frame 13'),('walk','Walk / frame 7'),('carry','Carry / frame 7'),('cast','Cast / frame 17')]):panel(f,t,i*C,y,C,rows[4])
im.save(OUT/'Mira-review.png',optimize=True)
(OUT/'review-manifest.json').write_text(json.dumps({'revision':args.revision,'inputs':dict(used),'size':im.size},indent=2)+'\n')
print('Review:',im.size,'panels',len(used))

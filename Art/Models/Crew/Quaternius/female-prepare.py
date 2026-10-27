from PIL import Image,ImageStat,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3]
S=R/'Art/Downloads/quaternius/base/Universal Base Characters[Standard]'
spec=[
('mira','F','Hair_Buns','#C8912E',(150,152),(210,158),(141,125),'Navigator. Brown hair, fair skin; mandated Hair_Buns substitutes for portrait curls. Cap omitted in Phase 1.'),
('noor','F','Hair_Buns','#1E3A5F',(457,151),(527,159),(449,130),'Deckhand. Warm tan skin and dark brown tied curls; Hair_Buns substitutes for curly tied-back hair. Beanie omitted.'),
('rosa','M','Hair_SimpleParted','#2F6E6A',(784,151),(737,90),(775,125),'Fisher. Portrait reads male: male base and regular brows used. Short dark brown hair; SimpleParted substitutes for tousled fringe. Beanie omitted.'),
('tess','F','Hair_Long','#2F6E6A',(1089,151),(1187,191),(1090,124),'Fisher. Golden-blonde hair; Hair_Long substitutes for the long side braid. Beanie omitted.'),
('ana','F','Hair_Long','#1E3A5F',(148,515),(202,531),(128,480),'Deckhand. Brown hair and tan skin; Hair_Long substitutes for shoulder-length waves. Beanie omitted.'),
('lise','F','Hair_Long','#2F6E6A',(460,505),(546,502),(450,481),'Fisher. Copper-red hair and fair skin; Hair_Long substitutes for wavy bob. Freckles not reproduced by the supplied base texture. Beanie omitted.'),
('ines','F','Hair_Long','#B5542A',(763,513),(830,544),(771,467),'Engineer. Mandated light-blonde Hair_Long substitutes for twin braids. Hardhat omitted in Phase 1.'),
('tove','F','Hair_Long','#1E3A5F',(1096,503),(1141,470),(1097,465),'Deckhand. Silver-grey hair; Hair_Long substitutes for short bob. Older portrait age is not sculpted onto the untouched base. Cap omitted.')]
contact=Image.open(O/'female-portrait-reference.jpg').convert('RGB')
def sample(xy):
 x,y=xy;values=list(contact.crop((x-2,y-2,x+3,y+3)).getdata());return tuple(sorted(c[k] for c in values)[len(values)//2] for k in range(3))
def hx(c):return '#'+''.join(f'{v:02X}' for v in c)
rows=[]
for name,g,h,s,sk,ha,ey,note in spec:
 # Sample original PNG rather than compressed contact: contact positions map to 300px tiles.
 srcportrait=Image.open(R/f'Assets/Art/UI/Portraits/art108-{name}.png').convert('RGB')
 idx=len(rows);ox=(idx%4)*320;oy=(idx//4)*340
 def original_sample(pos):
  x=round((pos[0]-ox)/300*srcportrait.width);y=round((pos[1]-oy)/300*srcportrait.height)
  return tuple(round(v) for v in ImageStat.Stat(srcportrait.crop((x-2,y-2,x+3,y+3))).median)
 skin=original_sample(sk);hair=original_sample(ha);eye=sample(ey)
 if name=='mira':skin=(240,190,153);note+=' Fair skin follows Mo explicit instruction; warm orange portrait lighting compensated.'
 # Eye portraits are stylized black pupils. Preserve supplied sclera/iris image; recolour only the brown iris.
 eye=(35,24,19) if name!='tove' else (45,49,50)
 row=dict(name=name,gender=g,hair=h,skinHex=hx(skin),hairHex=hx(hair),eyeHex=hx(eye),suitHex=s,note=note)
 source=S/'Base Characters/Textures'/('T_Superhero_Female_Light_BaseColor.png' if g=='F' else 'T_Superhero_Male_Ligh.png')
 im=Image.open(source).convert('RGB');ref=(180,132,92) if g=='F' else (180,133,100)
 # Source diffuse modulation retains lips, ears, nose and hand shading rather than flattening the face.
 for k in range(3):
  channel=im.getchannel(k);channel=channel.point([max(0,min(255,round(v*skin[k]/ref[k]))) for v in range(256)])
  if k==0: channels=[channel]
  else:channels.append(channel)
 Image.merge('RGB',channels).save(O/f'female-{name}-skin.png')
 eyes=Image.open(S/'Base Characters/Textures/T_Eye_Brown.png').convert('RGB')
 pix=eyes.load()
 for y in range(eyes.height):
  for x in range(eyes.width):
   r,gg,b=pix[x,y]
   if r>gg*1.08 and gg>b*1.05:
    lum=(r+gg+b)/3/110;pix[x,y]=tuple(min(255,int(v*lum)) for v in eye)
 eyes.save(O/f'female-{name}-eyes.png')
 row['sampling']={'portrait':f'Assets/Art/UI/Portraits/art108-{name}.png','contactSkinXY':sk,'contactHairXY':ha,'method':'median 5x5 pixels in original PNG at positions mapped from contact coordinates, sRGB; Mira fair-skin override documented; eyes dark iris interpretation preserving source sclera'}
 rows.append(row)
(O/'female-palette.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))

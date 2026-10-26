"""Create comparison sheets from final rendered FBX geometry and accepted references."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders'
PAPER='#F6F0DF';INK='#173F57';MUTED='#61706F'
def font(s):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
def fit(im,box,xy,canvas):
 im=ImageOps.contain(im.convert('RGB'),box,Image.Resampling.LANCZOS);canvas.paste(im,(xy[0]+(box[0]-im.width)//2,xy[1]+(box[1]-im.height)//2))
def txt(d,xy,s,size=26,fill=INK):d.text(xy,s,font=font(size),fill=fill)
kit=['PrepCounter','Stove','SoupKettle','Fridge','SinkDishRack','CoffeeMachine','TableFor2','ReceptionDesk','PassCounter','TrashCan']
labels=['Prep counter · 1×1','Stove · 1×1','Soup kettle · 1×1','Fridge · 1×1','Sink + dish rack · 2×1','Coffee machine · 1×1','Table + 2 chairs · 1×1','Reception + till · 1×1','Pass counter · 2×1','Trash can · 1×1']
im=Image.new('RGB',(2400,1250),PAPER);d=ImageDraw.Draw(im);txt(d,(55,35),'STAGE 1 / EXPORTED 3D KIT',42);txt(d,(55,92),'Native bevelled meshes · navy enamel / ivory / honey timber · original character scale',24,MUTED)
for i,(name,label) in enumerate(zip(kit,labels)):
 x=25+(i%5)*475;y=155+(i//5)*510;fit(Image.open(P/('kit-'+name+'.png')),(460,420),(x,y),im);txt(d,(x+12,y+430),label,23)
txt(d,(55,1190),'Same exported FBX as the room proof. Tile footprints include the chairs. No baked textures or painted render overlay.',22,MUTED);im.save(P/'kit-sheet.png')
def comparison(filename,title,left,lefttitle,right,righttitle,lines):
 im=Image.new('RGB',(2880,1300),PAPER);d=ImageDraw.Draw(im);txt(d,(50,30),title,42);txt(d,(50,104),lefttitle,28);txt(d,(1470,104),righttitle,28)
 fit(Image.open(left),(1370,950),(35,160),im);fit(Image.open(right),(1370,950),(1475,160),im)
 for i,line in enumerate(lines):txt(d,(50,1150+i*39),line,24,MUTED)
 im.save(P/filename)
comparison('compare-interior.png','LOOK MATCH / ROOM',P/'room-1440x900.png','A  EXPORTED 3D · 8×5 · kitchen left · original crew',R/'Art/Source/Restaurant/concepts/interior-1.png','B  ACCEPTED CONCEPT · mood and material target',[
 'The runtime plan moves the kitchen from rear to left; the low walls and 52° / yaw 0 camera follow that plan.',
 'Palette and broad forms transfer. Painterly wear, soft bounce, richer timber and intimate table proportions remain a gap.',
 'Next: painted base-colour + local AO, room lightmaps/probes and a matched Unity grade. No native Unity parity claimed.'])
comparison('compare-kit.png','LOOK MATCH / KIT',P/'kit-sheet.png','A  TEN STAGE-1 TYPES · actual exported geometry',R/'Art/Source/Restaurant/concepts/kit-sheet.png','B  ACCEPTED 23-ITEM CONCEPT · broader future kit',[
 'Only the requested stage-1 ten types are built; higher-stage items on the reference sheet remain outside this brief.',
 'Bevels, enamel, ivory tops, honey timber and rounded silhouettes transfer; irregular wear and painted micro-detail do not.',
 'The 1×1 table includes two chairs, so it is tighter than the painting. Production textures and native lighting are next.'])
print('PACKAGING PASS 3 sheets')

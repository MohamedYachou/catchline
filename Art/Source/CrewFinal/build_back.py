from vector_art import *
from package import inventory,sheet,report,ROOT
import resvg_py
import math
s=rect(17,21,446,610,35,'#173F57','none',0).replace('<rect','<rect opacity=".28"',1)
s+=rect(14,9,452,610,35,'url(#navy)',INK,6)
s+=rect(25,20,430,588,28,'none','#708D96',3)
# Braided rope rim: a light strand and dark diagonal binding rhythm.
s+=rect(36,31,408,566,24,'none','#0F2F43',18)
s+=rect(36,31,408,566,24,'none','url(#gold)',12)
def groove(x,y,tx,ty):
 # A diagonal score follows the local tangent, so the binding reads as twisted rope.
 nx,ny=ty,-tx
 return path(f'M{x-3*tx-5*nx:.2f} {y-3*ty-5*ny:.2f}L{x+3*tx+5*nx:.2f} {y+3*ty+5*ny:.2f}','none','#94672E',2.2)
for x in range(66,420,14):s+=groove(x,31,1,0)+groove(x,597,-1,0)
for y in range(62,574,14):s+=groove(444,y,0,1)+groove(36,y,0,-1)
for cx,cy,start in [(420,55,-90),(420,573,0),(60,573,90),(60,55,180)]:
 for a in range(start+10,start+90,30):
  t=math.radians(a);s+=groove(cx+24*math.cos(t),cy+24*math.sin(t),-math.sin(t),math.cos(t))
s+=rect(49,44,382,540,19,'none','#9BAE9F',1.5)
# Quiet repeating sea lines are contained well within the rope frame.
for y in range(81,559,37):
 s+=path(f'M64 {y}Q86 {y-13} 108 {y}T152 {y}T196 {y}T240 {y}T284 {y}T328 {y}T372 {y}T416 {y}','none','#6A929C',1.5,extra='opacity=".18"')
s+=path('M240 124L400 314L240 504L80 314Z','none','#93B5B0',2,extra='opacity=".4"')
s+=circle(240,315,123,'url(#navy)','#D0B276',5)+circle(240,315,112,'none','#8AABAD',2)
s+='<g transform="translate(67 136) scale(1.35)">'+anchor()+circle(128,57,8,'#28546C','none',0)+'</g>'
# Symmetric small knots at top/bottom avoid a blank-end crop during reveal.
for y in [84,544]:
 s+=path(f'M224 {y}Q240 {y-18} 256 {y}Q240 {y+18} 224 {y}ZM224 {y}H204M256 {y}H276','none','#D7BE84',3)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640">{DEFS}{s}</svg>'
(OUT/'svg/v2-card-back.svg').write_text(svg)
(OUT/'v2-card-back.png').write_bytes(resvg_py.svg_to_bytes(svg_string=svg,width=480,height=640))
inventory('F',['v2-card-back.png'],'BUILT — pending opened review. Navy card back480×640 with braided warm rope border and central anchor. Editable SVG extension of the delivered nautical kit. Transparent rounded outer corners; no lettering.')
sheet('F',['v2-card-back.png'],cols=1,refs=[ROOT/'Assets/Art/UI/Cards/art108-frame-blue.png',ROOT/'Assets/Art/UI/v2-icon-anchor.png',ROOT/'Assets/Art/UI/v2-portrait-mira.png'])
report()

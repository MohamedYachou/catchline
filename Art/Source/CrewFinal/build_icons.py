from vector_art import *
from package import inventory,sheet,report,ROOT
import math
icons={}
# Brass token, with a segmented rope rim and one unambiguous upgrade arrow.
s=circle(128,133,106,'#805437')+circle(128,125,106,'url(#gold)')+circle(128,125,91,'none','#93652F',5)+circle(128,125,98,'none','#FFE6A0',7)
for a in range(0,360,15):
 t=math.radians(a);x=128+98*math.cos(t);y=125+98*math.sin(t)
 s+=path(f'M{x-4*math.cos(t-.8):.2f} {y-4*math.sin(t-.8):.2f}l{8*math.cos(t-.8):.2f} {8*math.sin(t-.8):.2f}','none','#91622D',3)
s+=path('M103 181V125H77L128 68L179 125H153V181Z','url(#paper)',INK,7)+path('M111 168V117H99L128 84','none','#FFF7D8',5)
icons['token']=s
# Rolled plan, broad blue face, rolled cream ends and one diagram with no lettering.
s='<g transform="rotate(-12 128 128)">'+path('M55 48H184Q212 48 212 76V203H74Q51 203 51 181V67Z','url(#navy)')
s+=path('M55 48Q32 48 32 71Q32 94 55 94H75V71Q75 48 55 48Z','url(#paper)')+path('M183 49Q161 50 161 71V181H183Q205 181 205 202Q205 223 183 223H68Q45 222 45 202Q45 181 68 181H161','url(#paper)')
s+=path('M71 63Q60 61 58 71Q59 79 69 78M185 195Q175 194 175 202Q175 210 186 209','none','#AC8D56',4)
s+=path('M88 143V111L113 94L141 111V143ZM88 125H141M115 95V143M99 160H140M90 83H132','none','#BFE7DE',4)+'</g>'
icons['blueprint']=s
# Mythic star, deep red enamel backing and warm brass beveled star.
star='M128 29L156 86L219 95L173 139L184 204L128 174L72 204L83 139L37 95L100 86Z'
s=circle(128,132,102,'url(#red)')+circle(128,128,93,'none','#F0C779',4)+path(star,'url(#gold)',INK,7)
s+=path('M128 29V132L37 95L100 86Z','#FFF0A2','none',0)+path('M128 132L184 204L128 174L72 204Z','#C4893D','none',0)+path('M128 29L156 86L219 95L173 139L184 204L128 174L72 204L83 139L37 95L100 86Z','none',INK,7)
s+=path('M128 103L145 128L128 151L111 128Z','#BEE9DA',INK,4)
icons['star']=s
# Focus heart, navy badge rim helps the pink silhouette read on warm or blue UI.
s=path('M128 24L211 60V137Q207 190 128 231Q49 190 45 137V60Z','url(#gold)')+path('M128 39L196 69V137Q192 181 128 213Q64 181 60 137V69Z','url(#navy)',INK,4)
s+=path('M128 173L82 131C46 95 88 59 117 86L128 97L139 86C168 59 210 95 174 131Z','url(#red)',INK,6)+path('M86 107Q82 86 104 91','none','#FFD0AA',6)
icons['focus']=s
# Laurel leaves frame a compact anchor. Alternate leaf angles make a visible wreath at 64px.
s=path('M82 218Q26 176 45 106M174 218Q230 176 211 106','none',INK,10)+path('M82 218Q26 176 45 106M174 218Q230 176 211 106','none','#D8B866',4)
for side in [0,1]:
 q=''
 for x,y,ang in [(48,111,-20),(43,143,-44),(51,173,-60),(68,198,-80)]:
  q+=f'<g transform="rotate({ang} {x} {y})">'+path(f'M{x} {y+16}Q{x-27} {y-1} {x-13} {y-22}Q{x+8} {y-8} {x} {y+16}Z','url(#teal)',INK,3)+'</g>'
 s+=f'<g transform="translate(256 0) scale(-1 1)">{q}</g>' if side else q
s+=anchor()+path('M97 217Q128 204 158 217L168 237L128 229L88 237Z','url(#red)',INK,4)
icons['renown']=s
files=[]
for n,b in icons.items():files+=export('v2-icon-'+n,b)
inventory('C',files,'BUILT — pending opened visual review. Native SVG extensions of the nautical icon kit; no lettering. 256×256 and 64×64 RGBA with transparent margins.')
sheet('C',files,cols=4,refs=[ROOT/'Assets/Art/UI/v2-icon-coin.png',ROOT/'Assets/Art/UI/v2-icon-anchor.png',ROOT/'Assets/Art/UI/v2-portrait-mira.png'])
report()

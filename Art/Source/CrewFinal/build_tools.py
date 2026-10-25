"""Neutral equipment: editable nautical SVG extensions, with shared palette/lighting."""
from vector_art import *
from package import inventory,sheet,report,ROOT
import math,re
tools={}
# Rod uses the existing kit's curved blank/cork grip/reel composition.
s=path('M43 215Q78 104 211 30','none',INK,12)+path('M74 142Q126 70 210 30','none','#76949D',4)
s+=path('M43 215L69 154','none',INK,28)+path('M43 215L69 154','none','#C9A476',18)+path('M43 207L62 164','none','#E8C996',4)
s+=circle(85,168,27,'url(#steel)')+circle(85,168,17,'url(#navy)',INK,4)+circle(85,168,6,'#D0B47C',INK,3)+path('M85 168L110 178L120 168','none',INK,6)
s+=path('M211 30L220 158','none','#78929B',3)+ellipse(220,172,8,14,'url(#paper)',INK,4)
for x,y in [(101,109),(146,69),(185,44)]:s+=circle(x,y,6,'url(#steel)',INK,3)
tools['rod']=s
# A hand reel / line spool with a visible drum and offset winding crank.
s=rect(71,80,101,94,12,'url(#navy)')+ellipse(75,127,31,61,'url(#steel)')+ellipse(169,127,34,61,'url(#steel)')
for x in range(86,159,9):s+=path(f'M{x} 84V170','none','#CFBE98',6)
s+=ellipse(171,127,24,46,'url(#navy)',INK,4)+ellipse(171,127,13,28,'url(#paper)',INK,4)
s+=path('M171 127L211 151L210 188','none',INK,12)+path('M171 127L211 151L210 188','none','#B9CFCA',5)+rect(195,181,30,40,11,'url(#wood)',INK,5)
s+=path('M83 184L115 209H153','none',INK,12)+rect(112,201,58,17,7,'url(#steel)',INK,4)
tools['reel']=s
# Net needle is a flat long shuttle, with eye and wound twine around the waist.
s='<g transform="rotate(36 128 128)">'+path('M128 20Q158 53 158 93V215Q128 240 98 215V93Q98 53 128 20Z','url(#wood)')
s+=path('M128 53Q143 71 143 93V118H113V93Q113 71 128 53Z','url(#navy)',INK,4)+path('M118 109V72L127 84V116','url(#paper)',INK,3)
s+=rect(95,136,66,64,5,'url(#paper)',INK,4)
for y in range(144,199,9):s+=path(f'M99 {y}L157 {y-4}','none','#AD8C5C',3)
s+=path('M108 206L145 216','none','#F9D6A0',4)+'</g>'
tools['net-needle']=s
def knife(long=False):
 # Short broad bait blade versus slender flexible filleting blade.
 if long:b=path('M112 147Q151 83 216 26Q193 92 137 163Z','url(#steel)')+path('M128 141L202 46','none','#F7FAE7',4)
 else:b=path('M106 131L145 83L193 64Q192 123 137 159Z','url(#steel)')+path('M128 135L177 88','none','#F7FAE7',5)
 b+=path('M99 137L139 167','none',INK,14)+path('M99 137L139 167','none','#ADBFB8',6)
 b+=path('M110 153L129 170L76 229Q62 235 51 224Q43 213 51 202Z','url(#wood)')
 for x,y in [(98,179),(70,211)]:b+=circle(x,y,4,'#EAD0A2',INK,2)
 return b
tools['bait-knife']=knife();tools['fillet-knife']=knife(True)
# Two offset work gloves, each has four clear fingers and a thumb.
def glove():
 return path('M68 200V146L42 111Q35 96 47 90Q58 86 75 109V54Q75 38 87 38Q98 38 98 53V88H102V38Q102 25 114 25Q126 25 126 39V88H130V45Q130 32 142 33Q153 33 153 47V94H157V65Q157 52 169 54Q180 54 180 68V142Q180 167 163 184V205Z','url(#paper)',INK,6)+rect(64,185,103,40,9,'url(#navy)',INK,5)+path('M88 114V154M112 107V152M137 108V150','none','#AA9062',3)+path('M77 198H152','none','#72949D',3)
tools['gloves']='<g transform="translate(77 41) rotate(14 128 128) scale(.74)">'+glove()+'</g><g transform="translate(-9 8) rotate(-10 128 128) scale(.84)">'+glove()+'</g>'
# Gaff: long wood shaft and solid stainless hook, no fishing line.
s=path('M49 221L165 78','none',INK,24)+path('M49 221L165 78','none','#BA915D',14)+path('M49 213L157 82','none','#ECD2A0',4)
s+=path('M160 83L180 59Q204 28 222 49Q237 69 207 93L194 99','none',INK,15)+path('M160 83L180 59Q204 28 222 49Q237 69 207 93L194 99','none','#C2D7D1',7)+path('M194 99L209 79L211 94Z','#B6CBC6',INK,3)
s+=path('M59 194L76 208M68 184L85 198M77 174L94 188','none',INK,4)
tools['gaff']=s
# Rubber deck boots with a low stacked heel and broad toe silhouette.
def boot():
 return path('M93 28H166L158 157Q169 177 210 183Q226 186 226 209V226H71V197Q71 177 86 163Z','url(#navy)')+path('M80 211H224V230H70V218Z','url(#steel)',INK,5)+ellipse(129,29,37,11,'url(#steel)',INK,5)+ellipse(129,29,25,5,'#173F57',INK,2)+path('M104 53L97 155M99 180Q132 186 144 203','none','#729CAB',5)
tools['boots']='<g transform="translate(-24 8) rotate(-11 128 128) scale(.77)">'+boot()+'</g><g transform="translate(65 31) scale(.8)">'+boot()+'</g>'
# Winch crank: offset steel arm with a square socket and upright rotating grip.
s=path('M64 192L127 160L126 93L191 61','none',INK,27)+path('M64 192L127 160L126 93L191 61','none','#B5C8C1',16)+path('M62 185L119 155V88L181 57','none','#F2F2DC',4)
s+=path('M41 184L64 171L85 185L84 211L62 223L41 210Z','url(#steel)',INK,5)+path('M54 189L65 184L74 190V202L64 208L54 202Z','#173F57',INK,3)
s+=rect(175,29,38,76,15,'url(#navy)',INK,6)+path('M186 42V86','none','#89A9B1',5)
tools['winch-handle']=s
# Oil can: thumb pump, long tapering spout and handle opening.
s=path('M79 103Q32 99 34 147Q35 184 80 178','none',INK,22)+path('M79 103Q32 99 34 147Q35 184 80 178','none','#9AAFAA',11)
s+=path('M160 113L200 71L226 43L230 51L213 91L185 145Z','url(#steel)',INK,5)
s+=path('M76 93H154L182 141L178 218H66L63 141Z','url(#navy)')+ellipse(121,94,46,13,'url(#steel)',INK,5)+rect(102,61,37,29,6,'url(#steel)',INK,5)+path('M119 61V43H151','none',INK,10)+path('M120 59V44H149','none','#ADBFB8',4)+path('M81 132V194','none','#80A6AF',6)+path('M85 206H162','none','#F0D8A2',4)
tools['oil-can']=s
# Canvas tool belt: sturdy waist strap with pouches and simple carried tools.
s=path('M29 66Q128 36 227 66L217 103Q128 81 39 104Z','url(#wood)')+rect(106,55,45,36,6,'url(#steel)',INK,5)+rect(117,64,23,18,2,'#805437',INK,3)
s+=path('M55 113L49 43L67 39L81 116','url(#steel)',INK,5)+path('M176 111V40H196V113','url(#wood)',INK,5)+path('M165 40V23H207V40Z','url(#steel)',INK,5)
s+=path('M35 99L105 88L113 201Q78 220 40 204Z','url(#navy)')+path('M146 89L221 99L216 204Q179 221 143 202Z','url(#navy)')+path('M41 133L105 125M148 125L216 133M53 145L55 194M160 145V195','none','#86A7AD',4)
s+=rect(108,111,36,67,6,'url(#paper)',INK,5)
tools['toolbelt']=s
# Compass has a large needle and no letters, only cardinal ticks.
s=circle(128,37,19,'url(#steel)',INK,5)+circle(128,37,8,'#173F57',INK,3)+circle(128,140,96,'url(#steel)')+circle(128,140,80,'url(#paper)',INK,5)
for a in range(0,360,30):
 t=math.radians(a);s+=path(f'M{128+65*math.cos(t):.2f} {140+65*math.sin(t):.2f}L{128+72*math.cos(t):.2f} {140+72*math.sin(t):.2f}','none',INK,4)
s+='<g transform="rotate(28 128 140)">'+path('M128 76L148 140L128 201L108 140Z','url(#navy)',INK,5)+path('M128 76L148 140H108Z','url(#red)',INK,4)+'</g>'+circle(128,140,9,'url(#gold)',INK,4)
tools['compass']=s
# Binoculars: visibly paired flared barrels, bridge and focus wheel.
s=path('M68 66L31 187Q29 219 72 226Q114 232 121 198L117 79Z','url(#navy)')+path('M143 79L139 198Q146 232 188 226Q231 219 229 187L192 66Z','url(#navy)')
s+=rect(88,93,83,41,12,'url(#steel)',INK,5)+rect(112,80,32,60,10,'url(#wood)',INK,5)
for x in [88,171]:s+=ellipse(x,67,27,18,'url(#steel)',INK,5)+ellipse(x,62,22,14,'url(#navy)',INK,4)
s+=ellipse(73,198,44,31,'url(#steel)',INK,5)+ellipse(187,198,44,31,'url(#steel)',INK,5)
for x in [73,187]:s+=ellipse(x,198,33,23,'url(#navy)',INK,4)+path(f'M{x-19} 194Q{x-8} 180 {x+7} 187','none','#9DD0CF',5)
s+=path('M58 108L42 168M174 99L190 163','none','#769BA8',5)
tools['binoculars']=s
# Nautical charts extend the existing folded chart icon, omitting lettering.
s=path('M26 51L92 64L158 40L230 56V215L158 199L92 223L26 208Z','url(#paper)')+path('M92 64L158 40V199L92 223Z','#D1BE92',INK,3)+path('M158 40L230 56V215L158 199Z','#A7C8BD',INK,3)
s+=path('M40 98Q66 76 82 111L75 145L46 154L37 182M174 68L179 100L207 118L217 102M174 176L192 149L213 166L211 192','url(#paper)','#577C80',3)
s+=path('M65 181Q107 113 182 136','none','#527F89',4,extra='stroke-dasharray="7 7"')+circle(182,136,9,'#BE7549',INK,3)
s+=path('M184 78V106M172 92H196','none',INK,3)
tools['charts']=s
order=['rod','reel','net-needle','bait-knife','gloves','gaff','fillet-knife','boots','winch-handle','oil-can','toolbelt','compass','binoculars','charts']
files=[]
gear='<defs><linearGradient id="gear" x2=".3" y2="1"><stop stop-color="#B9D2D0"/><stop offset=".5" stop-color="#7C9FA8"/><stop offset="1" stop-color="#4C7184"/></linearGradient></defs>'
for n in order:files+=export('v2-tool-'+n,gear+tools[n].replace('url(#navy)','url(#gear)'))
# Rarity tiles inherit the actual frame gradients exactly, including untouched original colours.
for n in ['white','green','blue','purple','gold','mythic']:
 p=OUT/'svg'/f'art108-frame-{n}.svg' if n in ['white','green','mythic'] else ROOT/f'Art/Models/CardsV1/art108-frame-{n}.svg'
 svg=p.read_text();gradient=re.search(r'<linearGradient id="rarity".*?</linearGradient>',svg,re.S).group(0)
 stops=re.findall(r'stop-color="(#[A-Fa-f0-9]+)"',gradient);hi,base,lo=stops
 s='<defs>'+gradient+'</defs>'+rect(13,17,230,230,29,lo,INK,6)+rect(13,10,230,230,29,'url(#rarity)',INK,6)+rect(23,20,210,210,22,'none',hi,4)
 s+=path('M31 52V40Q31 29 44 29H202','none',hi,5)
 if n=='mythic':
  for x,y in [(29,29),(227,29),(29,221),(227,221)]:s+=path(f'M{x} {y-7}L{x+5} {y}L{x} {y+7}L{x-5} {y}Z','#BFE8D9',INK,2)
 files+=export('v2-tool-tile-'+n,s,size=192,small=False)
inventory('E',files,'BUILT — pending opened visual review. Fourteen neutral shaded tools, each 256/64 RGBA, plus six 192px rounded rarity tiles sampled from actual frame gradients. Editable SVG extensions of existing rod/chart/nautical kit. No lettering.')
refs=[ROOT/'Assets/Art/UI/v2-icon-coin.png',ROOT/'Assets/Art/UI/v2-icon-anchor.png',ROOT/'Assets/Art/UI/v2-portrait-mira.png']
# Separate manageable full-size sheets retain every exported PNG and true64px samples.
sheet('E-tools-1',files[:14],cols=4,refs=refs)
sheet('E-tools-2',files[14:28],cols=4,refs=refs)
sheet('E-tiles',files[28:],cols=3,refs=refs)
# Actual tool-on-tile contrasts at intended phone size, in addition to transparent exports.
from PIL import ImageDraw,ImageFont
canvas=Image.new('RGB',(840,1040),'#F4EFE3');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),17)
draw.text((16,12),'64px tool + rarity tile contrast check',font=font,fill=INK)
for row,n in enumerate(order):
 y=50+row*69;draw.text((16,y+20),n,font=font,fill=INK)
 for col,r in enumerate(['white','green','blue','purple','gold','mythic']):
  tile=Image.open(OUT/f'v2-tool-tile-{r}.png').resize((64,64),Image.Resampling.LANCZOS)
  icon=Image.open(OUT/f'v2-tool-{n}.png').resize((56,56),Image.Resampling.LANCZOS)
  tile.alpha_composite(icon,(4,4));canvas.paste(tile,(200+col*99,y),tile)
canvas.save(OUT/'review/E-tile-contrast.png')
report()

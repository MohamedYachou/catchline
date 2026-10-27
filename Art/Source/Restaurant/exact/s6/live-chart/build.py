"""Mechanical isolation of accepted chart pixels plus repeatable gradient profile."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math, hashlib, shutil
P=Path(__file__).resolve().parent; D=P.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):p.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
trend=Image.open(D/'v2-s6-trend.png').convert('RGBA')
# Visible jewel pixels are retained; the circular mask excludes connecting strokes.
dot=trend.crop((198,33,234,69)); mask=Image.new('L',dot.size); dr=ImageDraw.Draw(mask)
dr.ellipse((1,1,34,34),fill=255)
dot.putalpha(Image.composite(dot.getchannel('A'),Image.new('L',dot.size),mask))
dot=dot.crop(dot.getbbox());dot=dot.resize((36,36),Image.Resampling.LANCZOS)
dot.save(D/'v2-s6-trend-dot.png')
# Rectify a straight painted interval between two jewels. No jewels in this crop.
segment=trend.transform((96,24),Image.Transform.AFFINE,(.5,0,140,-.5*27/98,.5,76-(140-118)*27/98-6),Image.Resampling.BICUBIC)
# Segment includes only the dark-edged stroke, not the pale area below it.
segment=segment.crop((0,0,96,20));segment=segment.crop(segment.getbbox())
segment=segment.resize((144,18),Image.Resampling.LANCZOS)
# Identical columns make the centre continuously stretchable and remove jagged crop ends.
column=segment.crop((71,0,72,18));segment=column.resize((144,18),Image.Resampling.NEAREST)
segment.save(D/'v2-s6-trend-segment.png')
# Source tint sampled from the accepted pale area. Uniform horizontal rows have exact repeat seams.
sample=trend.getpixel((550,90)); fill=Image.new('RGBA',(24,147))
for y in range(147):
 a=max(1,round(72*(1-y/147)**1.35))
 for x in range(24):fill.putpixel((x,y),(*sample[:3],a))
fill.save(D/'v2-s6-trend-fill.png')
source=Path('C:/Users/momoy/.codex/generated_images/01a17ab4-9da1-77a0-b6b2-cc3b8156a1b1/exec-a8013108-e550-48d6-9fd1-d18ec668655b.png')
shutil.copy2(source,P/'bar-empty-generated.png')
bar=Image.open(source).convert('RGBA');a=bar.getchannel('A').point(lambda n:n if n>=8 else 0);bar.putalpha(a);bar=bar.crop(bar.getbbox()).resize((72,108),Image.Resampling.LANCZOS)
bar=bar.crop(bar.getbbox());bar.save(D/'v2-s6-bar-empty.png')
items=[]
for name,rect,borders,method in [
 ('trend-dot',[315,238,12,12],None,'accepted trend jewel crop/circular isolation'),
 ('trend-segment',[335,230,48,6],[0,0,0,0],'accepted straight stroke affine rectification; centre-column repeat'),
 ('trend-fill',[310,207,8,49],None,'accepted area RGB sample; continuous vertical alpha profile, horizontal rows identical'),
 ('bar-empty',[38,209,24,36],[15,15,15,15],'built-in ImageGen empty variant, alpha trim/3x export')]:
 path=D/f'v2-s6-{name}.png'; im=Image.open(path)
 item=dict(name=path.stem,file=path.name,screen=6,rect=rect,size=list(im.size),borders=borders,border_order='left,bottom,right,top',sha256=sha(path),exportMethod=method,native3xDetailClaim=False,pixelExactClaim=False)
 if name=='bar-empty':item['renderOpacity']=.28
 if name=='trend-segment':item.update(pivot=[.5,.5],horizontalSlice=True,renderRule='Stretch to centre-to-centre distance; rotate about midpoint; draw under nodes. Square ends hidden by nodes.')
 if name=='trend-fill':item.update(wrapX='repeat',wrapY='clamp',renderRule='Clip top to live polyline and bottom to baseline. Never draw as a full rectangle above the curve.')
 items.append(item)
base=json.loads((P/'baseline-manifest.json').read_text());write(D/'manifest.json',base+items);write(P/'manifest.json',items)
write(P/'layout.json',dict(screen=6,canvas=[844,390],origin='top-left',placements=[dict(name=i['name'],screen=6,use='live-chart-reference',rect=i['rect']) for i in items],note='Dynamic primitives are reference uses, not additions to the fixed painted mockup.'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
proof=Image.new('RGB',(1040,650),'#eee8d9');d=ImageDraw.Draw(proof)
def paste(sp,xy):proof.paste(sp,xy,sp)
d.text((20,12),'Accepted S6 reference / reusable live chart parts',font=font,fill='#173f57')
ref=Image.open(D/'../../concepts/ui-6-dashboard.png');proof.paste(ref,(15,42))
for k,i in enumerate(items):
 sp=Image.open(D/i['file']);x=25+k*250;y=460;paste(sp,(x,y));d.text((x,y+115),i['name'].replace('v2-s6-',''),font=font,fill='#173f57')
proof.save(P/'cuts-review.jpg',quality=95)
# Runtime chart stress proof: shifted values, empty income day, exact repeated fill tiles.
proof=Image.new('RGBA',(1040,520),'#fff5df');d=ImageDraw.Draw(proof);d.text((25,15),'Live-data proof: variable points / line rotation / repeated gradient / no-service bar',font=font,fill='#173f57')
points=[(55,220),(200,160),(345,195),(490,80),(635,140),(780,115),(925,55)]
area=Image.new('RGBA',proof.size); tile=fill.resize((24,230))
for x in range(45,950,24):area.alpha_composite(tile,(x,65))
poly=Image.new('L',proof.size);ImageDraw.Draw(poly).polygon(points+[(925,295),(55,295)],fill=255)
area.putalpha(Image.composite(area.getchannel('A'),Image.new('L',proof.size),poly));proof.alpha_composite(area)
for (x1,y1),(x2,y2) in zip(points,points[1:]):
 length=round(math.hypot(x2-x1,y2-y1));sp=segment.resize((length,9));sp=sp.rotate(-math.degrees(math.atan2(y2-y1,x2-x1)),Image.Resampling.BICUBIC,expand=True);proof.alpha_composite(sp,(round((x1+x2-sp.width)/2),round((y1+y2-sp.height)/2)))
for x,y in points:proof.alpha_composite(dot.resize((24,24)),(x-12,y-12))
for k in range(7):
 sp=bar.resize((40,100)) if k==3 else Image.open(D/'v2-s6-bar-teal.png').resize((40,70+k*8))
 if k==3:sp.putalpha(sp.getchannel('A').point(lambda n:round(n*.28)))
 proof.alpha_composite(sp,(80+125*k,470-sp.height))
d=ImageDraw.Draw(proof);d.text((440,480),'No service',font=font,fill='#173f57');proof.convert('RGB').save(P/'live-data-proof.jpg',quality=95)
assert all(fill.getpixel((0,y))==fill.getpixel((23,y)) for y in range(fill.height))
assert all(segment.getpixel((0,y))==segment.getpixel((143,y)) for y in range(segment.height))
for i in items:
 im=Image.open(D/i['file']);assert im.mode=='RGBA';assert im.getbbox()==(0,0,*im.size);assert im.width>=i['rect'][2]*3 and im.height>=i['rect'][3]*3
for i in base:assert sha(D/i['file'])==i['sha256']
write(P/'audit.json',dict(status='PASS',spriteCount=4,acceptedSpriteHashesPreserved=len(base),horizontalSeamDelta=0,segmentCentreSeamDelta=0,hashes={i['file']:i['sha256'] for i in items},nativeRuntimeVerified=False))
print('S6 PASS: 4 new primitives, accepted sprites unchanged, exact horizontal seams')

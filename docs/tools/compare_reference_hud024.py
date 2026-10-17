"""Compare actual ORIGINAL-RESOLUTION native HUD static crops to Mo's source.
Do not compare a scene-only render or an asset assembly study. Report, never
silently declare acceptance: dynamic data/fonts and different portraits are separate.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageStat, ImageDraw, ImageFont
import argparse,json,hashlib
p=argparse.ArgumentParser();p.add_argument('native',type=Path);p.add_argument('--label',default='Native comparison');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[2];source=r/'docs/reference-hud024/fish-original.png'
s=Image.open(source).convert('RGB');n=Image.open(a.native).convert('RGB')
assert n.size==s.size==(1672,941),'Need actual same-resolution game capture'
regions={'sun':(31,36,75,80),'coin-icon':(194,37,232,78),'goal-target':(31,137,55,162),
         'goal-heading':(64,139,170,159),'crew-badge':(1418,31,1458,69),'crew-icon':(1470,39,1498,65),
         'crew-menu':(1620,39,1642,63),'crew-heading':(1395,96,1500,118),'captain-heading':(1454,137,1519,156),
         'captain-wheel':(1608,156,1636,183)}
report={'label':a.label,'native_sha256':hashlib.sha256(a.native.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'regions':{},'pixel_perfect_claim':False}
sheet=Image.new('RGB',(850,70+len(regions)*95),'#173f57');d=ImageDraw.Draw(sheet);f=ImageFont.truetype(str(r/'Assets/Resources/FishReference/ReferenceRegular.ttf'),16)
d.text((18,14),a.label+' — Original / Actual native crop / Difference ×4',font=f,fill='white')
for i,(key,box) in enumerate(regions.items()):
 c=s.crop(box);v=n.crop(box);delta=ImageChops.difference(c,v);stat=ImageStat.Stat(delta)
 exact=sum(1 for pixel in delta.getdata() if pixel==(0,0,0))/float(c.width*c.height)
 report['regions'][key]={'bounds':box,'mean_abs_rgb_error':round(sum(stat.mean)/3,4),'exact_pixel_fraction':round(exact,5),'max_channel_error':max(z[1] for z in delta.getextrema())}
 y=65+i*95;d.text((18,y),key,font=f,fill='white')
 for x,pic in [(190,c),(410,v),(630,delta.point(lambda z:min(255,z*4)))]:
  pic=pic.resize((pic.width*2,pic.height*2),Image.Resampling.NEAREST);sheet.paste(pic,(x,y))
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');sheet.save(a.out.with_suffix('.png'))
print('Native comparison written; errors reported without asserting visual/pixel acceptance')

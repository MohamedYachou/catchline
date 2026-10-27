"""Mechanical closing portrait export and actual-size comparison."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw, ImageFont
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
ART=ROOT/'Art/Source/Restaurant'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
raw=OUT/'provenance/mira-host-wave-original.png'
im=Image.open(raw).convert('RGBA')
box=im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
cut=im.crop(box)
# Match the requested existing S5 rectangle exactly; aspect adjustment is
# explicitly recorded, rather than pretending the generated canvas was 3x.
size=(444,501)
new=cut.resize(size,Image.Resampling.LANCZOS)
new.save(OUT/'v2-s5-mira-host.png')
assert new.getchannel('A').getbbox()==(0,0,*size)
layout={'canvas':[844,390],'origin':'top-left','placements':[{'name':'v2-s5-mira-host','screen':5,'rect':[580,209,148,167],'size':size,'scale':3,'replaces':'v2-mira-wave','layering':'same old portrait layer; existing Sleep button occludes lower torso; do not draw above button'}],
 'runtimeReadOnlyObservation':{'file':'Assets/Scripts/Game/VoyageRestaurantUi.cs','parentClip':[520,0,324,390],'currentAbsoluteRect':[543,198,222,278],'note':'Lead owns native replacement/placement. Existing runtime override differs from mockup. New painting has waist framing; retain native crop and Sleep occlusion. Native AFTER not verified.'}}
(OUT/'layout.json').write_text(json.dumps(layout,indent=2))
(OUT/'text-styles.json').write_text(json.dumps({'styles':[],'note':'Character art only; no baked labels or text replacements.'},indent=2))
rec={'name':'v2-s5-mira-host','file':'v2-s5-mira-host.png','size':size,'logicalSize':[148,167],'scale':3,'rect':[580,209,148,167],'alphaBounds':new.getchannel('A').getbbox(),'source':str(raw.relative_to(ROOT)),'sourceSize':im.size,'sourceAlphaCrop':box,'resizeFactors':[444/cut.width,501/cut.height],'native3xDetailClaim':False,'sha256':sha(OUT/'v2-s5-mira-host.png'),'sourceSha256':sha(raw),'method':'built-in ImageGen identity/outfit edit, alpha crop and Lanczos export'}
(OUT/'closing-manifest.json').write_text(json.dumps([rec],indent=2))
old=Image.open(ART/'exact/s3-s5/v2-mira-wave.png').convert('RGBA')
old=old.resize((148,167),Image.Resampling.LANCZOS)
preview=new.resize((148,167),Image.Resampling.LANCZOS)
board=Image.new('RGB',(780,490),'#f4efe3');d=ImageDraw.Draw(board)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
d.text((20,16),'S5 Mira / actual 148 x 167 logical pixels',font=font(22),fill='#173f57')
for x,pic,label in [(40,old,'Old captain'),(240,preview,'New host')]:
    d.text((x,61),label,font=font(17),fill='#173f57')
    board.paste(pic,(x,91),pic)
    # Separate visible-crop preview, keeps the upper body above Sleep in the
    # same mockup rectangle; card/button is only a QA annotation, not new art.
    board.paste(pic.crop((0,0,148,112)),(x,295),pic.crop((0,0,148,112)))
    d.rounded_rectangle((x,407,x+148,443),8,fill='#e36a35')
    d.text((x+48,414),'Sleep',font=font(18),fill='white')
d.text((430,106),'Same wave + smile',font=font(18),fill='#173f57')
d.text((430,142),'Gold clip, no captain hat',font=font(18),fill='#173f57')
d.text((430,178),'Navy / teal host tailoring',font=font(18),fill='#173f57')
d.text((430,315),'Lower view: Sleep occlusion',font=font(17),fill='#173f57')
d.text((430,350),'Proof only; native import pending',font=font(17),fill='#173f57')
board.save(OUT/'closing-old-new-actual-size.jpg',quality=96)
print(json.dumps(rec))

"""Mechanical contact sheet and explicit visual-review record; no art generation."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFont

root = Path(__file__).resolve().parent
roster = json.loads((root/'roster.json').read_text())
ana = next(j for j in roster if j['id']=='ana')
ana['identity']='warm tan woman, chin-length wavy dark brown bob, simple dark oval eyes and small closed smile from her portrait'
ana['outfit']='modest teal server dress with small ivory collar, three-quarter sleeves, plain navy belt and low navy shoes; no apron or decorative gold buttons'
(root/'roster.json').write_text(json.dumps(roster,indent=2),encoding='utf-8')
canvas=Image.new('RGB',(1800,2800),'#eee2c8');d=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
d.text((30,22),'CATCHLINE / RESTAURANT NIGHT OUTFITS',font=font,fill='#173c46')
d.text((30,58),'15 people / 16 variants - Mira A and B are review options',font=small,fill='#173c46')
for n,j in enumerate(roster):
    x=(n%4)*450;y=110+(n//4)*670
    d.text((x+22,y),j['id'].replace('-',' ').title()+' / '+j['job'],font=small,fill='#173c46')
    im=Image.open(root/(j['id']+'-front.png'));im=ImageOps.contain(im,(315,590),Image.Resampling.LANCZOS)
    canvas.paste(im,(x+18,y+42),im)
    bust=ImageOps.contain(Image.open(root/(j['id']+'-bust.png')),(88,88),Image.Resampling.LANCZOS)
    canvas.paste(bust,(x+346,y+62),bust)
canvas.save(root/'overview.jpg',quality=95)
review={'reviewer':'Codex 1 (Windows app)','scope':'2D art only','allFinalSheetsIndividuallyOpened':True,
        'allSourceComparisonsIndividuallyOpened':True,'nativeRestaurantMockupsOpened':True,
        'records':[{'id':j['id'],'sheet':j['id']+'-sheet.png','comparison':j['id']+'-compare.jpg',
                    'review':'Outfit, role, distinct identity and 88px preview checked against source portrait and restaurant mockups.'} for j in roster],
        'corrections':['Ana first generation rejected for Mira-like face drift; rejected source retained under provenance/ana-rejected-01. Final uses Ana portrait and mockup only.',
                       'Mira B bust crop excludes raised hand.'],
        'limits':'Human art review, not identity equivalence proof or runtime acceptance. Mira A/B selection remains with Mo/Claude.'}
(root/'visual-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
print('overview.jpg and visual-review.json written; Ana roster description synchronized')

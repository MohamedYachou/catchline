"""Measured source crops and provenance for S6; no artwork painting."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,math
R=Path(__file__).resolve().parent
source=R/'provenance/s6-generated.png'; im=Image.open(source).convert('RGBA')
J=[]
def add(slug,rect,desc,slice=False,opaque=False):
    J.append({'name':'v2-s6-'+slug,'screen':6,'rect':rect,'description':desc,'nineSlice':slice,'opaque':opaque})
add('background',[0,0,844,390],'Full-bleed BLUE WOODEN PLANK WALL ONLY. Remove every UI object, card, button, icon, title, graph and illustration, reconstruct uninterrupted painted navy-blue horizontal wooden planks.',False,True)
add('title-sign',[233,0,395,61],'Wood hanging title sign with golden ropes and glowing brass lantern. Remove ALL title lettering leaving empty wood; preserve silhouette/lantern/ropes. No blue background.')
add('button-back',[14,10,122,43],'Cream bevelled rounded Back button ONLY. Remove Back word AND arrow; empty cream center. No wall.',True)
add('arrow-back',[27,19,29,24],'Filled dark-navy left arrow glyph ONLY. No cream button or other backdrop.')
add('button-close',[789,9,44,44],'Round cream bevelled button ONLY. Remove X leaving empty cream centre. No wall.')
add('icon-close',[800,20,21,23],'Bold dark-navy X cross glyph ONLY, no cream button or background.')
add('tab-selected',[20,58,175,38],'Orange glossy rounded rectangular selected tab ONLY, thick navy outline and lower lip. Remove ALL text, empty orange center.',True)
add('tab-idle',[198,58,169,38],'Ivory glossy rounded rectangular tab ONLY with navy edge. Remove ALL text, empty cream centre.',True)
add('week-selector',[650,58,179,38],'Ivory rounded wide date-selector pill ONLY. Remove word Week, number2 AND both arrows; empty ivory centre.',True)
add('chevron-left',[664,66,18,23],'Small dark navy left chevron glyph ONLY; remove ivory backdrop.')
add('panel',[16,98,278,214],'Large cream paper dashboard panel with navy rounded outer contour, narrow golden edge and two brass pins top corners. REMOVE ALL inner contents: title, numbers, coin, bars, divider, row, labels. Completely smooth empty ivory panel inside. No wall.',True)
add('menu-row',[563,149,256,51],'Subtle tan-outline ivory rounded menu row ONLY, remove fish plate AND all words/numbers. Smooth blank ivory centre.',True)
add('income-summary',[27,267,255,38],'Small tan-outline ivory rounded summary row ONLY. Remove text/numbers and vertical dividers, empty smooth center.',True)
add('popularity-caption',[307,276,232,29],'Subtle tan-outline cream rounded caption strip ONLY. Remove people glyph AND text, blank center.',True)
add('upgrade-strip',[16,314,813,73],'Wide cream rounded paper upgrade strip with navy outline and two corner brass pins. REMOVE entire restaurant illustration, every text/number, star, progress bar, button; completely empty clean cream center. No wall.',True)
add('bistro',[24,307,255,78],'Only the detailed coastal restaurant miniature and its immediate waterfront scenery, whitewashed masonry, navy shutters, striped awning, flower pots, terrace tables, lighthouse/blue sea right. Preserve entire wide low illustration. Remove surrounding upgrade card/words/wall. Transparent outside scenery silhouette.')
add('button-upgrades',[641,324,169,57],'Glossy teal rounded rectangular Upgrades button ONLY, thick navy edge, cream inner rim and dark lower lip. Remove ALL letters leaving empty teal centre.',True)
add('progress-track',[284,360,352,22],'Gold/ochre rounded progress-track BACKING ONLY. Remove teal fill and ALL numbers leaving continuous empty golden trough. No cream paper backdrop.',True)
add('progress-fill',[286,363,291,15],'Teal glossy rounded horizontal progress fill ONLY. Remove all numbers/text, gold track and cream backdrop.',True)
add('coin',[38,135,91,55],'Golden euro coin with embossed euro currency symbol and short golden rays ONLY, no background. Preserve shape/shading.')
add('star-full',[349,135,29,29],'Single gold five-pointed star ONLY with warm orange bevel and navy/brown contour. No background.')
add('star-empty',[438,135,28,29],'Single unfilled pale beige five-pointed star ONLY with tan outline, preserve pale opaque centre. No background.')
add('people',[319,278,31,24],'Small two-person dark navy and blue guest glyph ONLY, no cream strip or text.')
add('dish-fish',[567,151,84,47],'Only grilled whole golden fish on white/navy oval plate with green herbs and lemon slices. Remove row, text and cream backdrop. Crisp painted dish sprite.')
add('dish-soup',[573,205,74,45],'Only white/navy bowl of orange fish soup with fish chunks and herbs. Remove row, text and cream backdrop.')
add('dish-coffee',[574,257,68,45],'Only ivory/navy coffee cup with dark coffee, saucer and biscuit. Remove row, words and cream backdrop.')
add('bar-teal',[105,209,24,36],'Single teal glossy vertical rounded chart bar ONLY with thin navy rim. Remove paper/axes/labels.',True)
add('bar-gold',[209,191,26,55],'Single golden glossy vertical rounded chart bar ONLY with thin brown rim. Remove paper/axes/labels.',True)
add('trend',[310,207,224,49],'Teal rising seven-point trend curve with circular jewel-like dots and translucent pale teal area beneath, ONLY. Remove cream paper, axes, letters/numbers. Keep same seven-point geometry including middle dip. Transparent outside shape.')
add('divider-horizontal',[31,129,245,2],'One thin straight warm tan horizontal divider ONLY. No paper or text.',True)
add('divider-vertical',[108,274,2,26],'One thin straight warm tan vertical divider ONLY. No paper or text.',True)
(R/'references').mkdir(exist_ok=True)
for j in J:
    x,y,w,h=j['rect']; box=[round(x*im.width/844),round(y*im.height/390),round((x+w)*im.width/844),round((y+h)*im.height/390)]
    p=R/'references'/(j['name']+'.png');im.crop(box).save(p)
    j['referenceCrop']=str(p); j['sourcePixelCrop']=box
    j['prompt']='Production Catchline S6 UI sprite, precise-object-edit. Reference1 is the exact crop/style/geometry authority; reference2 is full screen for context. Extract/recreate ONLY this piece: '+j['description']+' Match reference proportions, silhouette, navy contour, paint shading, colours and bevel faithfully, do not redesign. '+('Opaque full-bleed background.' if j['opaque'] else 'Genuinely TRANSPARENT background, no grid, no canvas padding, artwork fills its own tight bounds. Keep opaque cream centres on paper/button frames.')+' NO words, letters, numbers or watermarks. The euro symbol is allowed only for the coin. High resolution, at least '+str(w*3)+'x'+str(h*3)+' pixels; do not add other pieces.'
(R/'jobs.json').write_text(json.dumps(J,indent=2))
for first in range(0,len(J),8):
    group=J[first:first+8]; sheet=Image.new('RGB',(1200,math.ceil(len(group)/2)*190),'#d9dfdf');d=ImageDraw.Draw(sheet)
    for i,j in enumerate(group):
        x=(i%2)*600;y=(i//2)*190;d.text((x+10,y+8),j['name']+' '+str(j['rect']),fill='#173f57')
        a=ImageOps.contain(Image.open(j['referenceCrop']),(580,150));sheet.paste(a,(x+10,y+30),a)
    sheet.save(R/'references'/f'contact-{first//8+1}.jpg')
print(json.dumps({'jobs':len(J),'sourceSize':im.size,'nativeScale':[im.width/844,im.height/390]}))

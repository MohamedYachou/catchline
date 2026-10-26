"""Measured S6 placement/text handoff. No runtime or source-art mutation."""
import json
from pathlib import Path
from PIL import ImageFont
P=Path(__file__).resolve().parent
jobs=json.loads((P/'jobs.json').read_text())
placements=[]
def use(name, label, rect=None, **kw):
    job=next(j for j in jobs if j['name']=='v2-s6-'+name)
    placements.append(dict(name=job['name'],screen=6,use=label,rect=rect or job['rect'],**kw))
for j in jobs:
    use(j['name'].removeprefix('v2-s6-'),'primary')
def repeat(name, rows):
    for label,rect in rows: use(name,label,rect)
repeat('tab-idle',[('crew-priorities',[369,58,172,38])])
use('chevron-left','next-week',[799,66,18,23],flipX=True)
repeat('panel',[('popularity',[296,98,252,214]),('menu-performance',[551,98,278,214])])
repeat('menu-row',[('soup',[563,202,256,51]),('coffee',[563,255,256,51])])
repeat('star-full',[('rating-2',[379,135,29,29]),('rating-3',[408,135,29,29]),('bistro-requirement',[482,321,31,32])])
repeat('star-empty',[('rating-5',[467,135,28,29])])
repeat('bar-teal',[('monday',[38,227,24,18]),('tuesday',[71,217,24,28]),('thursday',[140,222,24,23]),('friday',[174,209,25,36]),('sunday',[244,205,25,40])])
repeat('divider-horizontal',[('income-baseline',[28,244,250,1]),('popularity-baseline',[310,255,222,1])])
repeat('divider-vertical',[('summary-second',[197,274,1,26]),('income-axis',[28,192,1,53]),('popularity-axis',[310,207,1,49])])
texts=[]
def text(id,value,rect,size,fill='#080D2E',weight=700,**kw):
    texts.append(dict(id=id,screen=6,text=value,rect=rect,size=size,weight=weight,fill=fill,stroke='#080D2E',stroke_width=0,shadow=[0,0,'#00000000'],**kw))
text('back','Back',[70,19,49,24],20)
text('restaurant-title',"Mira’s restaurant",[279,12,285,38],32,'#FFF4DC',stroke_width_override=2)
text('tab-week','This week',[59,64,100,24],20,'#FFF7E9',stroke_width_override=2)
text('tab-service','Live service',[227,65,112,24],20)
text('tab-crew','Crew priorities',[389,65,132,24],20)
text('week-number','Week 2',[709,66,65,23],19)
text('income-heading','Week income',[44,106,130,24],20)
text('income-value','2,840',[144,132,94,35],31)
text('income-change','+18% last week',[144,169,109,18],15,'#007B78')
for i,(day,x) in enumerate(zip('MTWTFSS',[42,77,111,146,181,216,251])):
    text('income-day-'+str(i+1),day,[x,249,12,13],10)
for key,label,value,x,w in [('dishes','Dishes','2,160',36,58),('drinks','Drinks','480',127,49),('tips','Tips','200',213,52)]:
    text('income-'+key+'-label',label,[x,270,w,13],10)
    text('income-'+key+'-value',value,[x,282,w,20],17)
text('popularity-heading','Popularity',[331,106,108,24],20)
text('popularity-value','46',[400,164,45,32],29)
text('popularity-change','+6 this week',[379,196,89,18],15,'#007B78')
for i,(day,x) in enumerate(zip('MTWTFSS',[315,347,380,414,448,483,519])):
    text('popularity-day-'+str(i+1),day,[x,259,12,13],10)
text('popularity-caption','A warmer welcome',[361,281,152,18],14)
text('menu-heading','Menu performance',[576,106,191,24],20)
text('menu-subtitle','What guests ordered this week',[580,130,206,15],12)
for key,label,n,y in [('fish','Grilled fish','48',165),('soup','Fish soup','32',217),('coffee','Coffee','40',269)]:
    text('menu-'+key+'-label',label,[655,y+1,93,19],15)
    text('menu-'+key+'-sold',n,[752,y-3,33,27],24)
    text('menu-'+key+'-unit','sold',[786,y+3,28,17],13)
text('upgrade-heading','Next: Bistro',[283,319,176,29],25)
text('upgrade-subtitle','More tables and a terrace',[283,345,183,15],12)
text('upgrade-stars','3 stars',[517,325,63,23],20)
text('upgrade-progress','2,840 / 3,500',[425,363,91,16],13)
text('upgrades-button','Upgrades',[670,338,112,28],23,'#FFF7E9',stroke_width_override=2)
for t in texts:
    if 'stroke_width_override' in t: t['stroke_width']=t.pop('stroke_width_override')
    t['align']='left'
    t['vertical_align']='middle'
# Refine individual glyph extents after opening all three measurement sheets.
refined={'income-dishes-label':[53,270,31,13],'income-dishes-value':[42,282,50,20],
 'income-drinks-label':[137,270,30,13],'income-drinks-value':[137,282,31,20],
 'income-tips-label':[226,270,24,13],'income-tips-value':[223,282,32,20],
 'menu-fish-label':[655,166,76,19],'menu-soup-label':[655,218,69,19],
 'menu-coffee-label':[655,270,59,19],'popularity-caption':[361,281,129,18],
 'menu-subtitle':[580,130,174,15],'upgrade-heading':[283,319,135,29],
 'upgrade-subtitle':[283,345,174,15]}
for t in texts:
    if t['id'] in refined:t['rect']=refined[t['id']]
# Calibrate actual Fredoka pixel size to the painted glyph region rather than
# assuming its font metrics equal the generated lettering's nominal size.
fontpath=next(parent for parent in P.parents if (parent/'Assets').exists())/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
for t in texts:
    t['painted_size_estimate']=t['size']
    w,h=t['rect'][2:];stroke=round(t['stroke_width'])
    fitting=1
    for n in range(1,80):
        bb=ImageFont.truetype(str(fontpath),n).getbbox(t['text'],stroke_width=stroke)
        if bb[2]-bb[0]<=w and bb[3]-bb[1]<=h:fitting=n
    t['size']=fitting
layers={'background':0,'title-sign':10,'button-back':10,'button-close':10,
 'tab-selected':10,'tab-idle':10,'week-selector':10,'panel':20,'upgrade-strip':20,
 'menu-row':25,'income-summary':25,'popularity-caption':25,'progress-track':30,
 'progress-fill':35,'button-upgrades':30,'divider-horizontal':30,'divider-vertical':30}
for p in placements:p['z']=layers.get(p['name'].removeprefix('v2-s6-'),40)
placements.sort(key=lambda p:p['z'])
assert len({t['id'] for t in texts})==len(texts)
for item in placements+texts:
    x,y,w,h=item['rect']; assert 0<=x<x+w<=844 and 0<=y<y+h<=390,item
(P/'layout.json').write_text(json.dumps(dict(canvas=[844,390],screen=6,origin='top-left',reference='../../concepts/ui-6-dashboard.png',placements=placements),indent=2)+'\n')
(P/'text-styles.json').write_text(json.dumps(dict(coordinate_system='844x390 mockup pixels, top-left; rects are measured glyph regions, not touch targets',font='Fredoka Bold closest available runtime font; painted source font identity not proven',styles=texts),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(placements=len(placements),text_entries=len(texts))))

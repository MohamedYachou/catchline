"""Codex1 measured additions. Does not run Codex2's metadata generator."""
from pathlib import Path
import json, copy, shutil
R=Path(__file__).resolve().parent
S=R.parent/'s1-s2'
p=S/'text-styles.json'
backup=R/'text-styles.before.json'
if not backup.exists(): shutil.copy2(p,backup)
d=json.loads(backup.read_text(encoding='utf-8-sig'))
# Each original style keeps its text and all styling fields. A grouped source
# style has an envelope plus individual instances/entries for drawing.
groups=[
('title', [('Arrange',[127,7,103,29])]),
('undo',[('Undo',[774,13,38,16])]),
('wallet',[('2,450',[643,12,48,20])]),
('tabs',[('Kitchen',[24,348,42,15]),('Guests',[89,348,44,15]),('Bar',[170,348,21,15]),('Decor',[220,348,37,15]),('Expand',[280,348,45,15])]),
('catalog-name',[('Table for 2',[429,315,61,14]),('Table for 4',[589,315,63,14]),('Booth',[756,315,36,14])]),
('catalog-price',[('120',[455,333,29,17]),('220',[615,333,29,17]),('380',[780,333,29,17])]),
('catalog-size',[('1×1',[455,354,24,13]),('2×1',[624,354,25,13]),('2×1',[788,354,25,13])]),
('world-tag',[('Table for 2 · 1×1',[709,149,101,17])]),
('clock',[('18:40',[61,6,58,23])]),
('subtitle',[('Evening service',[62,28,86,12])]),
('now',[('NOW',[364,5,23,12])]),
('wallet',[('320',[560,13,35,20]),('42',[654,13,25,20])]),
('speed',[('1×',[712,14,22,20]),('2×',[756,14,22,20])]),
('stock-label',[('Fish',[70,63,29,17]),('Soup',[70,127,34,17]),('Coffee',[70,192,44,17])]),
('stock-count',[('8',[70,80,17,20]),('5',[70,144,17,20]),('12',[70,209,27,20])]),
('late-title',[('A late table?',[736,68,84,18])]),
('late-copy',[('A group just arrived.\nShall we seat them?',[737,88,86,25])]),
('seat',[('Seat them',[731,148,68,19])]),
('decline',[('Not tonight',[730,187,82,19])]),
('staff-role',[('Cook',[106,331,29,16]),('Serve',[274,331,35,16]),('Fix',[439,331,20,16]),('Coffee',[601,331,42,16])]),
('title',[("Mira’s · Evening service",[114,20,421,41])]),
('timeline-label',[('18:00',[552,52,44,18]),('20:00',[695,52,46,18]),('23:00',[816,52,46,18])]),
('clock',[('18:40',[638,8,41,21])]),
('wallet',[('320',[993,25,48,30]),('42',[1148,25,33,30])]),
('speed',[('1×',[1308,27,33,30]),('2×',[1370,27,33,30])]),
('stock-title',[("Tonight’s stock",[33,105,153,25])]),
('stock-count',[('8',[124,151,22,34]),('5',[124,215,22,34]),('12',[124,279,39,34])]),
('repair',[('Fryer\nneeds repair',[81,343,97,42])]),
('late-title',[('A late table?',[1289,121,122,27])]),
('late-copy',[('A party of four\nhas arrived.',[1294,153,108,42])]),
('seat',[('Seat them',[1242,241,117,28])]),
('decline',[('Not tonight',[1241,296,119,27])]),
('staff-role',[('Cook',[146,783,44,25]),('Serve',[406,783,56,25]),('Fix',[658,783,30,25]),('Coffee',[931,783,65,25]),('Reception',[1210,783,92,25])]),
]
assert len(d['styles'])==len(groups)
out=[]
for i,(old,(base,instances)) in enumerate(zip(d['styles'],groups)):
    screen={'s1-phone':'arrange','s2-phone':'phone','s2-desktop':'desktop'}[old['screen']]
    xs=[r[0] for _,r in instances]; ys=[r[1] for _,r in instances]
    x=min(xs); y=min(ys)
    rect=[x,y,max(r[0]+r[2] for _,r in instances)-x,max(r[1]+r[3] for _,r in instances)-y]
    row=copy.deepcopy(old); row.update(screen=screen,id=base,rect=rect)
    if len(instances)>1:
        row['measurementRole']='style-group; use child instance entries to draw separately'
        row['instances']=[dict(id=f'{base}-{j+1}',text=t,rect=r) for j,(t,r) in enumerate(instances)]
    out.append(row)
    if len(instances)>1:
        for j,(t,r) in enumerate(instances):
            c=copy.deepcopy(old); c.update(screen=screen,id=f'{base}-{j+1}',text=t,rect=r,styleRef=base)
            out.append(c)
d['styles']=out
d['measurementBasis']+=' Codex1: rects are hand-measured ink envelopes in each named native raster; group styles retain original text and fields, individual children provide separate draw positions. No OCR/font extraction or subpixel exactness claimed.'
d['screens']={'arrange':{'file':'ui-1-arrange.png','size':[844,390]},'phone':{'file':'ui-2-service.png','size':[844,390]},'desktop':{'file':'ui-service-desktop.png','size':[1440,900]}}
d['coverageNotes']=['All foreground UI words/numbers are listed; currency symbols, pause/check/cross/rotate/arrow and sun are integral artwork icons, not live text.','Phone timeline has NOW only; desktop timeline has three clock labels and the orange 18:40 flag.','Visible kitchen/menu scene pictograms are world art, outside the foreground UI text sheet.','The multiplication glyphs in the original grouped texts are retained; instance text transcribes the mockup × glyph.']
ids=set()
for r in out:
    key=(r['screen'],r['id']); assert key not in ids,key; ids.add(key)
    w,h=d['screens'][r['screen']]['size']; x,y,rw,rh=r['rect']
    assert min(x,y)>=0 and min(rw,rh)>0 and x+rw<=w and y+rh<=h,key
for old in json.loads(backup.read_text(encoding='utf-8-sig'))['styles']:
    new=next(r for r in out if r['text']==old['text'] and r['screen']=={'s1-phone':'arrange','s2-phone':'phone','s2-desktop':'desktop'}[old['screen']])
    assert all(new[k]==v for k,v in old.items() if k!='screen'),old['text']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'text-audit.json').write_text(json.dumps({'original_styles':33,'entries':len(out),'unique_ids':True,'bounds_pass':True,'original_style_fields_preserved':True,'method':'visual native-pixel measurement; grouped original styles plus individual draw entries'},indent=2)+'\n')
print('text entries',len(out),'all checks pass')

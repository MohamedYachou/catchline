"""Layout/style documentation, no artwork generation."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
def write(n,v): (R/n).write_text(json.dumps(v,indent=2)+'\n')
jobs=json.loads((R/'jobs.json').read_text())
extras=json.loads((R/'extra-jobs.json').read_text())
arrange={'v2-btn-back','v2-btn-undo','v2-tab-idle','v2-tab-selected','v2-item-card','v2-item-card-idle','v2-name-tag','v2-btn-rotate','v2-btn-cancel','v2-btn-confirm','v2-arrange-tray','v2-wallet-arrange'}
desktop={'v2-stock-slab','v2-stock-row','v2-chip-repair','v2-staff-card','v2-staff-rail','v2-speed-pill','v2-icon-pause','v2-timeline-dot','v2-meter-ring-track','v2-meter-ring-fill','v2-bubble-order','v2-mira-service-bust'}
def screen(n): return 'arrange' if n in arrange else 'desktop' if n in desktop else 'phone'
rows=[dict(asset=n,screen=screen(n),rect=rect,source='manifest measured reference crop') for n,size,desc,rect in jobs]
rows += [dict(asset=n,screen=s,rect=rect,source='manifest measured reference crop') for n,size,desc,rect,s in extras]
def add(s,n,rect,role='instance'):
    rows.append(dict(asset=n,screen=s,rect=rect,source=role))
# Repeated instances and responsive placements measured independently; x/y top-left.
for n,rect in [
 ('v2-bar-service',[0,0,844,46]),('v2-icon-pause',[807,14,17,18]),
 ('v2-speed-pill',[699,5,90,35]),('v2-speed-idle',[797,6,36,34]),
 ('v2-wallet-pill',[616,7,72,32]),('v2-service-card',[654,53,182,170]),
 ('v2-mira-service-bust',[662,58,73,77]),
 ('v2-stock-card',[9,120,149,61]),('v2-stock-card',[9,184,149,63]),
 ('v2-icon-fish-stock',[20,67,41,36]),('v2-icon-soup',[21,133,39,35]),('v2-icon-cup',[20,194,42,41]),
 ('v2-btn-primary',[665,139,161,35]),('v2-btn-secondary',[665,178,161,34]),
 ('v2-bubble-order',[404,131,57,46]),('v2-bubble-order',[524,140,48,47]),
 ('v2-staff-card-phone',[183,323,164,55]),('v2-staff-card-phone',[349,323,160,55]),('v2-staff-card-phone',[512,323,158,55]),
 ('v2-meter-track',[81,356,88,11]),('v2-meter-track',[249,356,88,11]),('v2-meter-track',[412,356,87,11]),('v2-meter-track',[574,356,87,11]),
 ('v2-icon-pan',[81,332,22,15]),('v2-icon-wrench',[413,331,19,20]),('v2-icon-cup',[575,331,20,20])]: add('phone',n,rect)
for n,rect in [
 ('v2-btn-back',[21,12,73,58]),('v2-service-card',[1153,83,275,264]),
 ('v2-btn-primary',[1179,228,233,49]),('v2-btn-secondary',[1179,286,233,45]),
 ('v2-stock-row',[28,201,166,59]),('v2-stock-row',[28,266,166,59]),
 ('v2-icon-cup',[42,270,64,56]),('v2-speed-selected',[1292,15,62,51]),
 ('v2-speed-idle',[1358,15,59,51]),('v2-wallet-pill',[935,14,125,51]),('v2-wallet-pill',[1081,13,120,52]),
 ('v2-timeline-flag',[630,3,56,31]),('v2-timeline-track',[551,20,286,32]),
 ('v2-staff-card',[298,769,270,89]),('v2-staff-card',[575,769,246,89]),
 ('v2-staff-card',[828,769,255,89]),('v2-staff-card',[1090,769,305,89]),
 ('v2-meter-ring-track',[490,785,63,62]),('v2-meter-ring-track',[741,785,63,62]),
 ('v2-meter-ring-track',[999,785,63,62]),('v2-meter-ring-track',[1316,785,63,62]),
 ('v2-bubble-order',[620,355,58,60]),('v2-bubble-order',[988,370,65,62])]: add('desktop',n,rect)
for n,rect in [
 ('v2-tab-idle',[151,310,56,64]),('v2-tab-idle',[211,310,56,64]),('v2-tab-idle',[271,310,60,64]),
 ('v2-item-card-idle',[662,306,165,71]),('v2-icon-coin-arrange',[614,11,23,23]),
 ('v2-icon-chair',[95,7,22,29])]: add('arrange',n,rect)
for n,s,rect in [('v2-meter-fill-orange','phone',[72,98,42,11]),('v2-meter-fill-yellow','phone',[440,356,27,11]),('v2-guest-patience-arc','desktop',[834,302,50,22])]: add(s,n,rect)
for n,s,rect in [('v2-icon-group','phone',[690,145,25,19]),('v2-icon-cross','phone',[692,186,18,18]),('v2-icon-tile1','arrange',[436,355,13,12]),('v2-icon-tile2','arrange',[594,355,23,12]),('v2-icon-order-dish','phone',[413,146,32,19]),('v2-meter-ring-fill-orange','desktop',[741,785,63,62])]: add(s,n,rect)
write('layout.json',{'coordinates':'top-left origin; x,y,width,height in original mockup pixels; rectangles include authored shadow allowance; foreground art only, no scene reconstruction',
 'screens':{'arrange':{'file':'ui-1-arrange.png','size':[844,390]},'phone':{'file':'ui-2-service.png','size':[844,390]},'desktop':{'file':'ui-service-desktop.png','size':[1440,900]}},
 'fontSizes':'text-styles.json uses each native mockup size; desktop sizes are not phone sizes', 'placements':rows})
write('screen-map.json',{n:screen(n) for n,*_ in jobs})
print(json.dumps({'placements':len(rows),'uniqueAssets':len(set(r['asset'] for r in rows))}))

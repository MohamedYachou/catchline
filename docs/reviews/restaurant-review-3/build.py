from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
C=ROOT/'Art/Source/Restaurant/concepts'
CAP=ROOT/'docs/screens/restaurant-ui'
cases=[
 ('plan','r117/restaurant-plan','ui-3-mira-plan.png'),
 ('dashboard','r114/restaurant-dashboard','ui-6-dashboard.png'),
 ('dashboard-stored','r121/day-dash-stored','ui-6-dashboard.png'),
 ('arrange-poor','r122/day-arrange-poor','ui-arrange-card-states.png'),
 ('service-before','r115/day-service-orders','ui-2-service.png'),
 ('service-mid','r127/day-service-orders','ui-2-service.png'),
 ('service-current','r129/day-service-orders','ui-2-service.png'),
 ('bistro','r129b/day-bistro','ui-2-service.png'),
 ('stage3','r133/day-bistro','ui-2-service.png'),
 ('steam','r132/day-service-steam','ui-2-service.png'),
 ('mira3d','r126/day-service-orders','ui-2-service.png'),
 ('bistro-room','r129b/day-service-late','ui-2-service.png'),
 ('stage3-room','r133/day-service-late','ui-2-service.png'),
 ('closing','r134/restaurant-closing','ui-5-closing.png'),
 ('crew','r134/restaurant-crew','ui-9-crew-priorities.png'),
 ('kitchen-after','r135/day-service-orders','ui-2-service.png'),
 ('bistro-after','r135b/day-service','ui-2-service.png'),
]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
ledger=[]
for slug,cap,ref in cases:
 for dev,size in [('844',(844,390)),('1440',(1440,900))]:
  refpath=C/('ui-service-desktop.png' if dev=='1440' and ref=='ui-2-service.png' else ref)
  paths=[refpath,CAP/(cap+'-'+dev+'.png')]
  panes=[]
  for role,path in zip(['REFERENCE','GAME'],paths):
   raw=path.read_bytes(); im=Image.open(path).convert('RGB')
   ledger.append(dict(case=slug,device=dev,role=role,path=path.relative_to(ROOT).as_posix(),size=list(im.size),sha256=hashlib.sha256(raw).hexdigest()))
   if role=='GAME':
    assert im.size==(size[0]*(3 if dev=='844' else 2),size[1]*(3 if dev=='844' else 2)),(path,im.size)
    fit=im.resize(size,Image.Resampling.LANCZOS)
   else:
    fit=ImageOps.contain(im,size,Image.Resampling.LANCZOS)
   pane=Image.new('RGB',(size[0],size[1]+28),'#253b48')
   pane.paste(fit,((size[0]-fit.width)//2,28+(size[1]-fit.height)//2))
   ImageDraw.Draw(pane).text((8,5),f'{role}: {path.name} | {size[0]} x {size[1]} logical',font=font,fill='white')
   panes.append(pane)
  # Stacked so each pane retains its exact logical size in a standalone image.
  sheet=Image.new('RGB',(size[0],(size[1]+28)*2))
  sheet.paste(panes[0],(0,0));sheet.paste(panes[1],(0,size[1]+28))
  sheet.save(OUT/f'{slug}-{dev}.jpg',quality=94,subsampling=0)
  panes[1].crop((0,28,size[0],size[1]+28)).save(OUT/f'{slug}-device-{dev}.png')
(OUT/'sources.json').write_text(json.dumps(ledger,indent=2)+'\n')
index=['# REVIEW-3 comparison evidence','',
 'Each JPG stacks reference above game at the stated logical device dimensions. Phone-only references retain their aspect ratio on desktop; neutral margins are comparison padding.','']
for slug,cap,ref in cases:
 index.append(f'- **{slug}** ({cap}): [844×390]({slug}-844.jpg), [1440×900]({slug}-1440.jpg).')
(OUT/'index.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
details=[('service-current',(435,135,160,110)),('steam',(435,135,160,110)),('arrange-poor',(665,308,160,68)),('plan',(230,140,60,120)),('mira3d',(495,125,105,95))]
sheet=Image.new('RGB',(800,520*len(details)),'#223c4a');draw=ImageDraw.Draw(sheet)
for i,(slug,(x,y,w,h)) in enumerate(details):
 im=Image.open(OUT/f'{slug}-device-844.png')
 sheet.paste(im.crop((x,y,x+w,y+h)).resize((w*4,h*4),Image.Resampling.NEAREST),(0,i*520+25))
 draw.text((4,i*520+4),f'{slug} xywh {[x,y,w,h]} | 4x nearest',font=font,fill='white')
sheet.save(OUT/'details.png')
boxes={
 'service-current': [('R3-01 kitchen',(180,92,281,165)),('R3-03 ring',(509,161,22,22)),('R3-05 table',(482,195,66,48))],
 'steam':[('R3-04 steam',(478,171,22,45))],
 'stage3-room':[('R3-02 water',(180,302,664,88))],
 'plan':[('R3-06 hand',(242,216,24,65))],
 'arrange-poor':[('PASS clearance',(695,355,96,12))],
 'closing':[('R3-07 label',(398,300,102,13))],
}
annotation_index=['# Marked logical-pixel evidence','','Boxes refer to the report; outlines are review overlays, not game pixels.','']
for slug,items in boxes.items():
 im=Image.open(OUT/f'{slug}-device-844.png').convert('RGB');d=ImageDraw.Draw(im)
 for label,(x,y,w,h) in items:
  d.rectangle((x,y,x+w-1,y+h-1),outline='#ff4377',width=2)
  ty=max(0,y-18);d.rectangle((x,ty,min(844,x+len(label)*9),ty+18),fill='#182d40')
  d.text((x+2,ty),label,font=font,fill='white')
 im.save(OUT/f'{slug}-marked.png')
 annotation_index.append(f'- [{slug}]({slug}-marked.png)')
(OUT/'annotations.md').write_text('\n'.join(annotation_index)+'\n')
(OUT/'boxes.json').write_text(json.dumps(boxes,indent=2)+'\n')
print(f'Built {len(cases)*2} comparisons; {len(ledger)} source records')

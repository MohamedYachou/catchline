from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).parent
C='Art/Source/Restaurant/concepts/'; E='Art/Source/Restaurant/exact/'
# Stable screen-specific evidence, not blindly the newest filename.
cases=[
('01-arrange','r86/day-arrange','ui-1-arrange.png',None),
('02-arrange-states','r86/day-arrange-lift','ui-arrange-card-states.png',E+'s1-card-states/reconstructed-3x.png'),
('03-service','r85/day-service-orders','ui-2-service.png',E+'s15/reconstructed-3x.png'),
('04-coach','r88/day-service-coach','ui-coach-phone.png',E+'coach-card/phone-reconstructed-3x.png'),
('05-closed','r88/day-service-closed','ui-closed-sign.png',E+'closed-sign/reconstructed-3x.png'),
('06-plan','r97/day-plan','ui-3-mira-plan.png',None),
('07-prep','r97/day-prep','ui-4-prep.png',None),
('08-closing','r89/restaurant-closing','ui-5-closing.png',None),
('09-moods','r93/day-service-moods','ui-mira-moods-phone.png',E+'mira-moods/phone-reconstructed-3x.png'),
('10-evening','r92/day-evening','ui-transition-evening-phone.png',E+'transition/evening-phone-reconstructed-3x.png'),
('11-morning','r91/day-morning','ui-transition-morning-phone.png',E+'transition/morning-phone-reconstructed-3x.png'),
('12-upgrades','r92/day-upgrades','ui-8-upgrades.png',E+'s8/reconstructed-3x.png'),
('13-pause','r94/day-service-paused','ui-pause-phone.png',E+'s2/pause/phone-reconstructed-3x.png'),
('14-stage2','r95/restaurant-stageup','ui-11-stage-up.png',E+'s11/celebrate/reconstructed-3x.png'),
('15-stage3','r95/restaurant-stageup3',None,E+'s11/later-stages/stage3/reconstructed-3x.png'),
('16-week','r97/day-week','ui-16-week.png',E+'s16/week-reconstructed-3x.png'),
('17-dashboard','r82/day-dashboard','ui-6-dashboard.png',E+'s6/reconstructed-3x.png'),
('18-market','r81/day-market','ui-7-market.png',E+'s7/reconstructed-3x.png'),
('19-crew','r82/restaurant-crew','ui-9-crew-priorities.png',E+'s9/reconstructed-3x.png'),
('20-sleep','r78/restaurant-sleep','ui-12-sleep.png',E+'s12/reconstructed-3x.png'),
('21-firstnight','r91/day-service-late','ui-13-first-night.png',E+'s13/reconstructed-3x.png'),
('22-latest-closing','r97/day-closing','ui-5-closing.png',None),
('23-service-latest','r96/day-service-orders','ui-2-service.png',E+'s15/reconstructed-3x.png'),
('24-harbour-entry','r85/new-harbour','ui-14-harbour-entry.png',E+'s14/reconstructed-3x.png'),
('25-arrange-buy','r86/day-arrange-buy','ui-arrange-card-states.png',E+'s1-card-states/reconstructed-3x.png'),
('26-arrange-store','r86/day-arrange-store','ui-arrange-card-states.png',E+'s1-card-states/reconstructed-3x.png'),
('27-arrange-kitchen','r86/day-arrange-kitchen','ui-1-arrange.png',None),
('28-current-plan','r99/day-plan','ui-3-mira-plan.png',None),
('29-current-prep','r99/day-prep','ui-4-prep.png',None),
('30-current-closing','r99/day-closing','ui-5-closing.png',None),
('31-current-service','r99/day-service-orders','ui-2-service.png',E+'s15/reconstructed-3x.png'),
('32-reservation','r98/restaurant-plan','ui-3-mira-plan.png',E+'s3/reservation/plan-reconstructed-3x.png'),
]
desktop={'03-service':('ui-service-desktop.png',None),'04-coach':('ui-coach-desktop.png',E+'coach-card/desktop-reconstructed-3x.png'),'09-moods':('ui-mira-moods-desktop.png',E+'mira-moods/desktop-reconstructed-3x.png'),'10-evening':('ui-transition-evening-desktop.png',E+'transition/evening-desktop-reconstructed-3x.png'),'11-morning':('ui-transition-morning-desktop.png',E+'transition/morning-desktop-reconstructed-3x.png'),'13-pause':('ui-pause-desktop.png',E+'s2/pause/desktop-reconstructed-3x.png'),'23-service-latest':('ui-service-desktop.png',None)}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
desktop['31-current-service']=desktop['03-service']
selected=set(sys.argv[1:])
ledger=[r for r in json.loads((OUT/'sources.json').read_text()) if r['screen'] not in selected] if selected and (OUT/'sources.json').exists() else []
for slug,cap,concept,proof in cases:
    if selected and slug not in selected: continue
    overview=Image.new('RGB',(2532,1060),'#233d4b'); draw=ImageDraw.Draw(overview)
    for row,(dev,size,scale) in enumerate([('844',(844,390),3),('1440',(1440,900),2)]):
        co,pr=desktop.get(slug,(concept,proof)) if row else (concept,proof)
        paths=[C+co if co else pr,pr,'docs/screens/restaurant-ui/'+cap+'-'+dev+'.png']
        panes=[]; records=[]
        for role,path in zip(['Concept','Reconstruction','Game'],paths):
            p=ROOT/path if path else None
            if p and p.exists():
                im=Image.open(p).convert('RGB'); orig=im.size
                target=(size[0]*scale,size[1]*scale)
                fitted=ImageOps.contain(im,target,Image.Resampling.LANCZOS)
                im=Image.new('RGB',target,'#334955')
                im.paste(fitted,((target[0]-fitted.width)//2,(target[1]-fitted.height)//2))
                records.append(dict(role=role,path=path,size=orig,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reference_is_phone_adapted=row==1 and slug not in desktop))
            else:
                im=Image.new('RGB',(size[0]*scale,size[1]*scale),'#334955'); ImageDraw.Draw(im).text((40,40),'No independent full-frame proof delivered' if role=='Reconstruction' else 'No capture',fill='white',font=font)
                records.append(dict(role=role,path=path,missing=True))
            panes.append(im)
        h=panes[0].height
        full=Image.new('RGB',(panes[0].width*3,h+40),'#233d4b'); d=ImageDraw.Draw(full)
        for i,im in enumerate(panes):
            labels=['CONCEPT / reference' if co else 'REFERENCE = reconstruction (no separate concept)','RECONSTRUCTED proof','SAVED GAME capture']
            full.paste(im,(i*im.width,40)); d.text((i*im.width+12,10),labels[i],fill='white',font=font)
        filename=f'{slug}-{dev}.jpg';full.save(OUT/filename,quality=94,subsampling=0)
        # overview holds equal logical phone frames; desktop row scales uniformly to 844 width.
        tileh=390 if row==0 else 527
        for i,im in enumerate(panes): overview.paste(im.resize((844,tileh),Image.Resampling.LANCZOS),(i*844,30 if row==0 else 485))
        draw.text((10,5 if row==0 else 460),f'{slug} {dev} | CONCEPT (left), PROOF (middle), GAME (right)',fill='white',font=font)
        ledger.append(dict(screen=slug,device=dev,logical_size=size,comparison=filename,sources=records))
    overview.save(OUT/(slug+'-overview.jpg'),quality=94,subsampling=0)
(OUT/'sources.json').write_text(json.dumps(ledger,indent=2))
print(len(cases),'screens;',len(ledger),'comparisons')

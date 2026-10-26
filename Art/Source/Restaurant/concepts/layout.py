"""Frame generated concepts and add requested clean labels; no scene repainting."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import hashlib,json

ROOT=Path(__file__).resolve().parent
FONT=ROOT.parents[3]/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'
CREAM='#F6F0DE'; NAVY='#173F57'; MUTED='#64787C'; GOLD='#C58B50'
def font(size): return ImageFont.truetype(str(FONT),size)
def text(im,xy,s,size=34,fill=NAVY,anchor=None):
    ImageDraw.Draw(im).text(xy,s,font=font(size),fill=fill,anchor=anchor)
def paste_fit(out,path,box):
    src=Image.open(path).convert('RGB'); x,y,w,h=box
    src=ImageOps.contain(src,(w,h),Image.Resampling.LANCZOS)
    out.paste(src,(x+(w-src.width)//2,y+(h-src.height)//2))
def sheet(name,title,sub,footer,labels=()):
    im=Image.new('RGB',(2400,1350),CREAM)
    text(im,(68,27),title,62);text(im,(70,103),sub,28,MUTED)
    source=ROOT/'generated'/name
    for version in (2,3):
        revised=ROOT/'generated'/f'{Path(name).stem}-v{version}.png'
        if revised.exists(): source=revised
    paste_fit(im,source,(30,159,2340,1017))
    if labels:
        step=2340/len(labels)
        for i,(head,body) in enumerate(labels):
            x=30+step*(i+.5)
            text(im,(x,1190),head,34,anchor='mt');text(im,(x,1235),body,24,MUTED,anchor='mt')
    text(im,(70,1300),footer,25,MUTED)
    im.save(ROOT/name)

def kit():
    names=[('Prep counter','1 × 1'),('Stove','1 × 1'),('Grill','1 × 1'),('Fryer','1 × 1'),('Soup kettle','1 × 1'),('Oven','1 × 1'),('Fridge','1 × 1'),('Sink + dish rack','2 × 1'),('Pass counter','2 × 1'),('Coffee machine','1 × 1'),('Drinks fridge','1 × 1'),('Bar + stools','2 × 1'),('Table for 2','1 × 1'),('Table for 4','2 × 1'),('Booth for 6','2 × 1'),('Terrace + parasol','1 × 1'),('Reception desk','1 × 1'),('Trophy fish','Wall'),('Net + floats','Wall'),('Lamp','1 × 1'),('Plant','1 × 1'),('Framed chart','Wall'),('Jukebox','1 × 1'),('Ship-clothes scale','Reference only')]
    im=Image.new('RGB',(2400,1350),CREAM);text(im,(68,24),'A place for every catch',62)
    text(im,(70,101),'23 placeables · navy enamel, ivory tops, honey wood · proposed metre-tile footprints',28,MUTED)
    src=Image.open(ROOT/'generated/kit-sheet.png').convert('RGB')
    # Object-aware row boundaries keep the tall parasol/plant/cap intact without
    # pulling their tips into the neighbouring object's label area.
    y_bounds=[(0,231)]*6+[(235,466),(235,466),(235,466),(235,447),(235,466),(235,466)]+[(478,688),(478,688),(478,687),(449,688),(475,688),(475,680)]+[(697,941),(697,941),(687,941),(697,941),(691,941),(690,941)]
    for idx,(name,foot) in enumerate(names):
        col=idx%6; row=idx//6; x=30+col*390; y=151+row*281
        top,bottom=y_bounds[idx]
        crop=src.crop((round(col*src.width/6)+3,top,round((col+1)*src.width/6)-3,bottom))
        crop=ImageOps.contain(crop,(370,215),Image.Resampling.LANCZOS)
        im.paste(crop,(x+(390-crop.width)//2,y+(215-crop.height)//2))
        text(im,(x+195,y+215),name,29,anchor='mt');text(im,(x+195,y+250),foot,24,MUTED,anchor='mt')
    text(im,(70,1300),'Footprints are design labels; wall art uses wall slots. Plinths illustrate scale, not purchase geometry.',25,MUTED)
    im.save(ROOT/'kit-sheet.png')

def main():
    sheet('look-options.png','Mira’s family restaurant','Three harbour looks · same corner, scale and water-facing terrace','Mo chooses the exterior family; progression below uses option 1 provisionally.',[
        ('01  Whitewashed stone','Blue shutters · navy slate · inherited harbour warmth'),('02  Painted timber','Teal boards · red roof · lighter seaside café'),('03  Harbour brick','Green awning · warm masonry · sturdy quayside pub')])
    sheet('exterior-stages.png','A closed door becomes a harbour landmark','Look 01 · five stages, one camera · expansion joins the neighbouring house','Concept progression, not construction drawings. Window interiors remain illustrative.',[
        ('0  Closed','Faded sign · shutters · crates'),('1  Café','Two inside tables · bench · chalkboard'),('2  Bistro','Three terrace tables · awning'),('3  Restaurant','Knock-through · larger sign · lanterns'),('4  Seafood house','Full frontage · string lights · trophy')])
    sheet('exterior-night.png','The quay stays warm after sunset','Stage 3 · lit windows, terrace company and a welcoming doorway','Warm amber belongs to people and windows; blue dusk keeps the harbour readable.')
    sheet('interior-1.png','A small first service','Stage 1 · approximately 8 × 5 metre tiles · front cutaway, camera about 50° down','Kitchen back/left, low pass, wood-floor dining · two tables for two · alley cats at the kitchen door.')
    sheet('interior-4.png','Room for the whole harbour','Stage 4 · brief’s 14 × 7 mood study + terrace · front-down camera about 52°','New runtime plan is 14 × 5 with low walls; this sheet explores furniture and warmth, not the final grid.')
    kit()
    sheet('service-moment.png','Everyone has a station','Stage 3 · fishers cook, deckhands serve, engineer repairs, navigator pours, Mira welcomes','Ship clothes stay on. Order bubbles are world cues; kitchen tops and crew hands must remain visible.')
    for name in ['ui-1-arrange','ui-2-service','ui-3-mira-plan','ui-4-prep','ui-5-closing','ui-service-desktop']:
        size=(1440,900) if name.endswith('desktop') else (844,390)
        source=ROOT/'generated'/f'{name}.png'
        for version in (2,3):
            revised=ROOT/'generated'/f'{name}-v{version}.png'
            if revised.exists(): source=revised
        im=Image.new('RGB',size,CREAM);paste_fit(im,source,(0,0,*size))
        if name=='ui-1-arrange':
            # Clean footprint label follows the current plan: four seats use 2x1.
            d=ImageDraw.Draw(im);d.rectangle((590,352,652,372),fill='#FFF8E9')
            d.rectangle((594,357,605,368),outline=MUTED,width=1)
            d.rectangle((605,357,616,368),outline=MUTED,width=1)
            text(im,(636,355),'2 × 1',13,anchor='mt')
        if name=='ui-4-prep':
            # Clean illustrative totals: 10 grilled + 8 soup + 12 fillets = 30.
            d=ImageDraw.Draw(im);d.rectangle((690,14,778,43),fill='#FFF5DF')
            text(im,(734,18),'30 / 30',20,anchor='mt')
            d.rectangle((250,348,347,370),fill='#FFF5DF')
            text(im,(291,349),'30 portions',16,anchor='mt')
            d.rectangle((412,348,471,370),fill='#FFF5DF')
            text(im,(441,349),'2 fish',17,anchor='mt')
        if name=='ui-5-closing':
            # Requested clean copy: avoid a generated reward-unlock claim that
            # is absent from the restaurant plan; retain the popularity panel.
            d=ImageDraw.Draw(im);d.rectangle((561,176,710,213),fill='#FFF5DF')
            text(im,(635,180),'Harbour reputation',12,anchor='mt')
            text(im,(635,197),'A warmer welcome',11,MUTED,anchor='mt')
        im.save(ROOT/f'{name}.png')
    names=['look-options','exterior-stages','exterior-night','interior-1','interior-4','kit-sheet','service-moment']
    im=Image.new('RGB',(2400,1350),CREAM);text(im,(48,20),'Mira’s restaurant · concept review',53)
    for i,n in enumerate(names):
        x=35+(i%3)*790;y=107+(i//3)*400
        paste_fit(im,ROOT/f'{n}.png',(x,y,750,365));text(im,(x+14,y+367),n,23)
    text(im,(850,990),'Mo’s choices',43)
    text(im,(850,1050),'Exterior 01 / 02 / 03',32)
    text(im,(850,1100),'Small-room warmth vs full-room bustle',30)
    text(im,(850,1150),'Pass height and phone camera need a prototype',29,MUTED)
    text(im,(850,1210),'Full sheets and UI mockups sit beside this contact.',27,MUTED)
    im.save(ROOT/'contact.png')
    outputs=names+['contact','ui-1-arrange','ui-2-service','ui-3-mira-plan','ui-4-prep','ui-5-closing','ui-service-desktop']
    audit={}
    for n in outputs:
        p=ROOT/f'{n}.png'; pic=Image.open(p); expected=(1440,900) if n.endswith('desktop') else ((844,390) if n.startswith('ui-') else (2400,1350))
        assert pic.size==expected,(n,pic.size)
        audit[p.name]={'size':list(pic.size),'mode':pic.mode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    (ROOT/'dimensions-and-hashes.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(f'{len(audit)} PNG dimensions PASS')
if __name__=='__main__': main()

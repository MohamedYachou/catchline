"""Task 05 review sheets from the actual exported sprites, including nine-slice.
Pillow + bundled Fredoka. Landscape game sizes, not Unity captures.
"""
import json
from PIL import Image
import build_ui_kit as U
U.MAN.update(json.loads((U.OUT/'slices.json').read_text())['sprites'])
CON=U.CON

def label(im,x,y,s,size=22,col=None,anchor='lt'):U.txt(im,x,y,s,size,col,anchor)
def save(im,name):U.save_png(im.convert('RGB'),CON/(name+'.png'),'Art/Source/compose_ui_pass2.py; actual exported Task 05 PNG sprites')
def main():
    im=Image.new('RGBA',(1920,1080),U.C['cream'])
    label(im,44,26,'Catchline / UI pass 2',42)
    label(im,44,83,'Fish portraits · shared 128px logical frames, distinct species silhouettes',23)
    for i,n in enumerate(['herring','mackerel','pollock','seabass','conger','plaice','cod','unknown']):
        x=35+i*233;U.put(im,'fish-'+n,x,124,200,200);label(im,x+100,323,n,22,anchor='mt')
    label(im,44,382,'Equipment & rewards',30)
    names=['rodholder','bigcooler','icebox','lunchtin','rod-fibreglass','rod-carbon','chart','squid','fuel','net','skiff','trophy','gift']
    for i,n in enumerate(names):
        x=35+(i%7)*233;y=437+(i//7)*225
        U.put(im,'icon-'+n,x+20,y,150,150);label(im,x+95,y+158,n,20,anchor='mt')
    label(im,44,924,'Crew / captain · deckhand · fisherman · veteran',26)
    for i,n in enumerate(['captain','deckhand','fisherman','veteran']):U.put(im,'portrait-'+n,710+i*170,883,160,160)
    save(im,'19-ui-pass2')
    im=Image.open(U.OUT/'title-backdrop.png').convert('RGBA')
    U.put(im,'logo-catchline',62,152,600,225)
    U.nine(im,'popup-panel',80,420,480,520)
    label(im,320,453,'Gull Harbour',31,U.C['ivory'],'mt')
    label(im,320,535,'Your next voyage awaits.',24,anchor='mt')
    U.button(im,'Continue',116,600,408,77,size=31)
    U.button(im,'New voyage',116,699,408,77,'secondary',30)
    label(im,320,835,'Settings',24,anchor='mm')
    save(im,'20-title-screen')
    U.save_png(im.convert('RGB').resize((1280,720),Image.Resampling.LANCZOS),CON/'20-title-screen-1280.png','compose_ui_pass2.py; tablet/desktop size review')
    # Landscape phone fit, preserving the complete art rather than cropping safe area.
    phone=Image.new('RGB',(844,390),U.C['navy']); small=im.convert('RGB');small.thumbnail((844,390));phone.paste(small,((844-small.width)//2,0))
    U.save_png(phone,CON/'20-title-screen-phone.png','compose_ui_pass2.py; 844x390 landscape fit review')
    im=Image.new('RGBA',(1920,1080),U.C['cream']);label(im,44,24,'Shops & sailing grounds',38)
    for i,n in enumerate(['market','harbourmaster','crewoffice','chandlery','supplies']):U.put(im,'header-'+n,38,95+i*188,1054,187)
    U.put(im,'sea-chart',1120,101,760,319)
    label(im,1120,446,'No baked pins or labels',24)
    label(im,1120,489,'Area positions and sea rectangle: slices.json',20)
    U.nine(im,'catch-card',1130,566,340,450)
    label(im,1300,592,'You caught',29,U.C['ivory'],'mt')
    U.put(im,'fish-mackerel',1178,664,244,244);label(im,1300,943,'Mackerel',28,anchor='mm')
    U.nine(im,'popup-panel',1510,566,358,450)
    label(im,1689,591,'Daily reward',29,U.C['ivory'],'mt')
    U.put(im,'daily-gift',1570,667,240,240)
    U.button(im,'Collect',1540,916,298,68,size=27)
    U.put(im,'badge-new',1740,526,128,64)
    U.put(im,'coin-pop',1695,432,95,95);U.put(im,'sparkle',1800,432,95,95)
    save(im,'21-ui-shops-chart-feedback')
if __name__=='__main__':main()

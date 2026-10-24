"""Editable SVG card frames + transparent PNGs, and portrait size packaging.
Requires resvg-py, Pillow. Only normalizes generated-image canvas/size, never paints faces.
"""
from pathlib import Path
import sys, json, hashlib, io, base64
sys.path.insert(0,str(Path.home()/'.codex/tmp/art108-python'))
import resvg_py
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'Art/Models/CardsV1';GAME=ROOT/'Assets/Art/UI/Cards';POR=ROOT/'Assets/Art/UI/Portraits'
for p in [SRC,GAME,POR]:p.mkdir(parents=True,exist_ok=True)
def frame(name,color,hi,lo,locked=False):
    slots=''.join(f'<rect x="49" y="{y+4}" width="382" height="62" rx="13" fill="#9B8E71"/><rect x="49" y="{y}" width="382" height="62" rx="13" fill="#E8E0CC" stroke="#173F57" stroke-width="3"/><circle cx="79" cy="{y+31}" r="17" fill="{color}" stroke="#173F57" stroke-width="3"/>' for y in (388,460,532))
    # Portrait window is truly transparent, supplied as a frame mask, not cream pixels.
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640">
<defs><linearGradient id="rarity" x2="0" y2="1"><stop stop-color="{hi}"/><stop offset=".5" stop-color="{color}"/><stop offset="1" stop-color="{lo}"/></linearGradient>
<mask id="window"><rect width="480" height="640" fill="white"/><rect x="51" y="57" width="378" height="270" rx="22" fill="black"/></mask></defs>
<g mask="url(#window)"><rect x="17" y="21" width="446" height="610" rx="35" fill="#173F57" opacity=".28"/>
<rect x="14" y="9" width="452" height="610" rx="35" fill="{lo}" stroke="#173F57" stroke-width="6"/>
<rect x="22" y="15" width="436" height="592" rx="29" fill="url(#rarity)" stroke="{hi}" stroke-width="4"/>
<rect x="37" y="42" width="406" height="553" rx="23" fill="#F4EFE3" stroke="#173F57" stroke-width="4"/>
<rect x="47" y="53" width="386" height="278" rx="24" fill="#173F57" stroke="{hi}" stroke-width="5"/>
<rect x="36" y="332" width="408" height="46" rx="12" fill="{lo}" stroke="#173F57" stroke-width="4"/>
<path d="M53 339 H427" stroke="{hi}" stroke-width="3" opacity=".7"/>{slots}
<path d="M28 45V38Q28 23 44 23H436" fill="none" stroke="white" opacity=".35" stroke-width="4" stroke-linecap="round"/>
</g>'''
    if locked:
        svg+='''<rect x="51" y="57" width="378" height="270" rx="22" fill="#173F57" fill-opacity=".77"/>
<path d="M209 175v-26a31 31 0 0 1 62 0v26" fill="none" stroke="#173F57" stroke-width="23"/>
<path d="M209 175v-26a31 31 0 0 1 62 0v26" fill="none" stroke="#8FA6AC" stroke-width="14"/>
<rect x="195" y="169" width="90" height="73" rx="13" fill="#E8E0CC" stroke="#173F57" stroke-width="5"/>
<circle cx="240" cy="198" r="9" fill="#173F57"/><path d="M240 202v16" stroke="#173F57" stroke-width="8" stroke-linecap="round"/>'''
    svg+='</svg>'
    src=SRC/f'art108-frame-{name}.svg';src.write_text(svg)
    data=resvg_py.svg_to_bytes(svg_string=svg,width=480,height=640)
    dst=GAME/f'art108-frame-{name}.png';dst.write_bytes(data)
    im=Image.open(io.BytesIO(data));assert im.size==(480,640) and im.mode=='RGBA'
    assert im.getpixel((0,0))[3]==0
    assert locked or im.getpixel((240,150))[3]==0
    return dict(id=name,file=dst.relative_to(ROOT).as_posix(),source=src.relative_to(ROOT).as_posix(),size=[480,640],portraitWindow=[51,57,378,270],nameBand=[49,337,382,36],abilitySlots=[[49,y,382,62] for y in (388,460,532)],sha256=hashlib.sha256(data).hexdigest())
def portraits():
    results=[]
    for original in sorted((ROOT/'Art/Source/Art108/portraits').glob('*-original.png')):
        name=original.stem.replace('-original','');im=Image.open(original).convert('RGBA');alpha=im.getchannel('A');bb=alpha.getbbox()
        assert bb and alpha.getextrema()[0]==0 and alpha.getextrema()[1]==255,(name,'no alpha')
        # The editable vector crop gives every bust the same clean shoulder cutoff.
        # Keep the complete original untouched; never paint/reconstruct generated faces.
        canonical=io.BytesIO();im.save(canonical,format='PNG')
        embedded=base64.b64encode(canonical.getvalue()).decode('ascii')
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="240" height="240" viewBox="0 0 1000 1000"><defs><clipPath id="bust"><path d="M0 0H1000V870Q500 1010 0 870Z"/></clipPath></defs><image clip-path="url(#bust)" width="1000" height="1000" xlink:href="data:image/png;base64,{embedded}"/></svg>'
        svgpath=SRC/f'art108-{name}-portrait.svg';svgpath.write_text(svg)
        for sz in (56,96,240):
            dest=POR/f'art108-{name}{"" if sz==240 else "-"+str(sz)}.png'
            dest.write_bytes(resvg_py.svg_to_bytes(svg_path=str(svgpath),width=sz,height=sz))
            check=Image.open(dest);assert check.size==(sz,sz) and check.getpixel((0,0))[3]==0
            extrema=check.getchannel('A').getextrema()
            assert extrema[0]==0 and extrema[1]>=250 and check.getchannel('A').getbbox(),(name,sz,'blank portrait')
            assert sum(1 for a in check.getchannel('A').getdata() if a>128)>sz*sz*.35,(name,sz,'too little visible portrait')
        results.append(dict(id=name,size=[240,240],variants=[56,96,240],original=original.relative_to(ROOT).as_posix(),alphaBounds=list(bb),sha256=hashlib.sha256((POR/f'art108-{name}.png').read_bytes()).hexdigest()))
    return results
if __name__=='__main__':
    frames=[frame('blue','#3B82F6','#B4D7FF','#1F4E79'),frame('purple','#8E44AD','#E0BAF4','#54216E'),frame('gold','#E6B422','#FFF0AA','#936515'),frame('locked','#52747C','#ADB6AF','#173F57',True)]
    manifest={'frames':frames,'portraits':portraits(),'notes':['Frame contains no baked name or ability text; code draws those in marked slots.','Portraits are generated raster art; SVG preserves editable placement, a common shoulder crop and the untouched PNG image source.']}
    (SRC/'manifest.json').write_text(json.dumps(manifest,indent=2))
    # Inspection plate: all frame variants at half-size and each portrait at intended UI sizes.
    sheet=Image.new('RGB',(1080,760),'#1E4D7B')
    for i,f in enumerate(frames):
        im=Image.open(ROOT/f['file']);sheet.paste(im.resize((240,320)),(20+i*265,20),im.resize((240,320)))
    y=375
    for i,p in enumerate(manifest['portraits']):
        im=Image.open(POR/f'art108-{p["id"]}.png');x=20+(i%6)*175;y=375+(i//6)*185
        sheet.paste(im.resize((96,96)),(x,y),im.resize((96,96)))
        small=im.resize((56,56));sheet.paste(small,(x+105,y+40),small)
        ImageDraw.Draw(sheet).text((x,y+103),p['id'],fill='#F4EFE3')
    sheet.save(SRC/'review.png')
    print('ART108 CARDS PASSED',len(frames),'frames',len(manifest['portraits']),'portraits')

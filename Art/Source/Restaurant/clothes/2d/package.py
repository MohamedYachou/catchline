"""Package generated art. Crops/resizing/compositing only; no painted pixels."""
import argparse, base64, hashlib, json, shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[4]

def save(ident, source, receipt):
    raw = ROOT / 'provenance' / (ident + '-generated.png')
    raw.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, raw)
    (raw.with_suffix('.json')).write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'saved':ident, 'source':str(raw)}))

def package():
    roster=json.loads((ROOT/'roster.json').read_text())
    records=[]
    for j in roster:
        ident=j['id']; raw=ROOT/'provenance'/(ident+'-generated.png')
        if not raw.exists(): continue
        image=Image.open(raw).convert('RGBA'); bbox=image.getchannel('A').getbbox()
        assert bbox and image.getchannel('A').getextrema()[0]==0, ident
        body=image.crop(bbox)
        body.save(ROOT/(ident+'-front.png'))
        # Frontal upper torso crop from the very same art: no independent face regeneration.
        # Values are explicit in manifest for downstream anchors and reproducibility.
        w,h=body.size
        frac=j.get('bustCrop',[.13,0,.87,.43])
        rect=(int(w*frac[0]),int(h*frac[1]),int(w*frac[2]),int(h*frac[3]))
        bust=body.crop(rect); tight=bust.getchannel('A').getbbox(); bust=bust.crop(tight)
        native=bust.size
        scale=768/max(bust.size)
        bust=bust.resize((round(bust.width*scale),round(bust.height*scale)),Image.Resampling.LANCZOS)
        bust=bust.crop(bust.getchannel('A').getbbox())
        assert min(bust.size)>=264, (ident,bust.size)
        bust.save(ROOT/(ident+'-bust.png'))
        # Transparent review sheet: body and independent staff-ready crop, no painted marks.
        sheet=Image.new('RGBA',(body.width+80+bust.width,max(body.height,bust.height)),(0,0,0,0))
        sheet.alpha_composite(body,(0,0));sheet.alpha_composite(bust,(body.width+80,0))
        sheet.save(ROOT/(ident+'-sheet.png'))
        record={'id':ident,'card':j['card'],'job':j['job'],'sourceIdentity':j.get('source',f"Assets/Art/UI/v2-portrait-{j['card']}-deck.png"),
                'fullBody':ident+'-front.png','bust':ident+'-bust.png','sheet':ident+'-sheet.png','sourceSize':image.size,'alphaCrop':bbox,
                'bodySize':body.size,'bustCropInBody':rect,'bustTightCrop':tight,'bustNativeSize':native,'bustSize':bust.size,
                'bustResampleScale':scale,'staffDesignMaxPx':[88,88],'bustAtLeast3x':min(bust.size)>=264,
                'rawSha256':hashlib.sha256(raw.read_bytes()).hexdigest()}
        records.append(record)
        # Comparison has source face, new outfit, true 88px staff rail preview and readable crop.
        bg=Image.new('RGB',(1280,1000),'#eee2c8'); d=ImageDraw.Draw(bg)
        d.text((24,16),f"{ident} / {j['job']} - source face | outfit | staff bust + 88px preview",fill='#173c46')
        source=Image.open(PROJECT/record['sourceIdentity']).convert('RGBA')
        source.thumbnail((230,300),Image.Resampling.LANCZOS);bg.paste(source,(18,60),source)
        preview=ImageOps.contain(body,(600,920),Image.Resampling.LANCZOS);bg.paste(preview,(270,56),preview)
        preview=ImageOps.contain(bust,(360,520),Image.Resampling.LANCZOS);bg.paste(preview,(900,55),preview)
        preview=ImageOps.contain(bust,(88,88),Image.Resampling.LANCZOS);bg.paste(preview,(1015,660),preview)
        bg.save(ROOT/(ident+'-compare.jpg'),quality=94)
    (ROOT/'manifest.json').write_text(json.dumps({'rosterCards':14,'captainHelper':True,'variantsExpected':len(roster),'variantsPackaged':len(records),'artOnly':True,'records':records},indent=2),encoding='utf-8')
    print(json.dumps({'packaged':len(records),'expected':len(roster),'alphaAndBust3xPass':True}))

if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('mode'); ap.add_argument('id',nargs='?'); ap.add_argument('source',nargs='?'); ap.add_argument('receipt',nargs='?'); a=ap.parse_args()
    if a.mode=='save': save(a.id,a.source,json.loads(Path(a.receipt).read_text(encoding='utf-8')))
    elif a.mode=='package': package()

"""Audit exact source/export/installed bytes and compose the fish review sheet."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/Fish050'
ROWS=[('YellowfinTuna','Yellowfin tuna'),('Barracuda','Barracuda'),('MahiMahi','Mahi-mahi'),('Monkfish','Monkfish')]
sheet=Image.new('RGB',(1200,650),'#F4EFE3');draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),26)
audit=[]
for i,(name,label) in enumerate(ROWS):
    folder=OUT/name;report=json.loads((folder/'validation.json').read_text())
    for file,sha in report['file_sha256'].items():
        assert hashlib.sha256((folder/file).read_bytes()).hexdigest()==sha,(name,file)
    portrait=folder/('fish-'+name.lower()+'.png')
    assert (folder/(name+'.fbx')).read_bytes()==(ROOT/'Assets/gemini/Models'/(name+'.fbx')).read_bytes()
    assert portrait.read_bytes()==(ROOT/'Assets/gemini/FishRenders'/portrait.name).read_bytes()
    im=Image.open(portrait).convert('RGBA')
    box=im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
    assert box and box[0]>0 and box[1]>0 and box[2]<im.width and box[3]<im.height
    features=report['features']
    if name=='YellowfinTuna': assert features.count('YellowFinlet')==14 and 'YellowDorsalSickle' in features
    if name=='Barracuda': assert features.count('Fang')==14 and 'ProjectingLowerJaw' in features
    if name=='MahiMahi': assert 'LongDorsalSail' in features and features.count('BlueFlankSpot')==32
    if name=='Monkfish': assert features.count('MonkfishTooth')==18 and features.count('RaisedEye')==2 and 'FishingLureStalk' in features
    # UI coordinates are measured from the bottom of the texture.
    uv=[box[0],im.height-box[3],box[2]-box[0],box[3]-box[1]]
    skin=(ROOT/'Assets/Scripts/Game/GeminiUiSkin.cs').read_text()
    assert f'"fish-{name.lower()}" => new Rect({", ".join(map(str,uv))})' in skin,(name,uv)
    audit.append(dict(id=25+i,species=name,label=label,triangles=report['triangles'],alphaBounds=box,spriteRect=uv,sourceFbxPortraitHashes=True,installedBytesMatch=True,anatomy=features))
    im.thumbnail((580,280));x=i%2*600;y=i//2*325
    sheet.paste(im,(x+(600-im.width)//2,y+10),im);draw.text((x+30,y+282),label,font=font,fill='#173F57')
sheet.save(OUT/'four-fish-contact.png')
evidence=ROOT/'docs/screens/fish050';evidence.mkdir(parents=True,exist_ok=True)
(evidence/'asset-audit.json').write_text(json.dumps(audit,indent=2))
sheet.save(evidence/'four-fish-contact.png')
print('FISH050: four source/FBX/portrait hashes, installed copies, alpha/UVs and anatomy passed')

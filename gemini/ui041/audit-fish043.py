from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[2];root=ROOT/'Art/Models/Fish043'
rows=re.findall(r'Species = Species\.(\w+), Name = "([^"]+)"', (ROOT/'Assets/Scripts/Game/GameData.cs').read_text());assert len(rows)==25
font=ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),18)
sheet=Image.new('RGB',(1800,1320),'#F4EFE3');d=ImageDraw.Draw(sheet);audit=[]
for i,(enum,label) in enumerate(rows):
 name='CongerEel' if enum=='Conger' else enum;folder=root/name;report=json.loads((folder/'validation.json').read_text())
 for n,h in report['file_sha256'].items():assert hashlib.sha256((folder/n).read_bytes()).hexdigest()==h
 source=next(folder.glob('fish-*.png'));im=Image.open(source).convert('RGBA');box=im.getchannel('A').point(lambda v:255 if v>32 else 0).getbbox()
 assert box and box[0]>0 and box[1]>0 and box[2]<im.width and box[3]<im.height,(name,box)
 assert (ROOT/'Assets/gemini/Models'/(enum+'.fbx')).read_bytes()==(folder/(name+'.fbx')).read_bytes()
 assert (ROOT/'Assets/gemini/FishRenders'/('fish-'+enum.lower()+'.png')).read_bytes()==source.read_bytes()
 features=report.get('features',[])
 if enum=='GiantSquid':
  assert len([f for f in features if f.startswith('Arm_')])==8
  assert len([f for f in features if f.startswith('FeedingClub_')])==2
 if enum=='GoldenPuffer':assert features.count('ConicalSpine')==30
 if enum=='Lionfish':assert features.count('FannedDorsalSpine')==11 and features.count('SplayedPectoralPlume')==18
 if enum=='ScallopedHammerhead':assert 'Cephalofoil' in features
 if enum=='AbyssalLeviathan':assert features.count('WhiteEyePatch')==2 and features.count('PaddlePectoral')==2
 if enum=='SpottedEagleRay':assert features.count('IvoryOcellus')==24
 audit.append({'id':i,'species':enum,'display':label,'triangles':report['triangles'],'source_fbx_portrait_hashes':'passed','installed_bytes_match_source':True,'alpha_bounds':box,'anatomy':features})
 im.thumbnail((340,210));x=i%5*360;y=26+i//5*258;sheet.paste(im,(x+(360-im.width)//2,y+(210-im.height)//2),im);d.text((x+10,y+218),label,font=font,fill='#173F57')
 d.text((x+10,y+240),f"ID{i} · {report['triangles']} triangles",font=ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),13),fill='#4D6875')
sheet.save(ROOT/'gemini/ui041/all25-model-portraits-final.png');(ROOT/'gemini/ui041/fish043-complete-audit.json').write_text(json.dumps(audit,indent=2));print('Verified all25 actual source/FBX/portrait/import hashes, alpha margins and required distinguishing anatomy')

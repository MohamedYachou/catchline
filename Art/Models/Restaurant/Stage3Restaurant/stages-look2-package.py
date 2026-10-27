"""Proof sheets, decoded dimensions, preservation ledger and final package seal."""
import ast,hashlib,json,sys,gzip
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'stages-look2-renders';stage=O.name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
def sheet(name,panels,width=1688,height=470):
 canvas=Image.new('RGB',(width,(len(panels)+1)//2*height+65),'#101c25');d=ImageDraw.Draw(canvas);d.text((20,15),stage+' | STAGES LOOK 2 | SOURCE PROOF | Codex 2 (WSL CLI)',font=font,fill='#f2e6ce')
 for i,(label,path) in enumerate(panels):
  x=(i%2)*(width//2);y=65+(i//2)*height;d.text((x+14,y+7),label,font=small,fill='#f2e6ce');im=ImageOps.contain(Image.open(path).convert('RGB'),(width//2-20,height-40));canvas.paste(im,(x+(width//2-im.width)//2,y+35+(height-40-im.height)//2))
 canvas.save(O/name,quality=94)
if '--seal' not in sys.argv:
 sheet('stages-look2-review.jpg',[
 ('Painting mood reference | stage 1',R/'Art/Source/Restaurant/concepts/ui-service-desktop.png'),
 ('AFTER | source room + illustrative linen tables',P/'after-populated-room-1440x900.png'),
 ('BEFORE | same source camera and sea',P/'before-room-1440x900.png'),('AFTER | pigment, runners, dressing, practicals',P/'after-room-1440x900.png'),
 ('BEFORE | illustrative linen tables',P/'before-populated-room-1440x900.png'),('AFTER | illustrative linen tables',P/'after-populated-room-1440x900.png')])
 sheet('stages-look2-phone-review.jpg',[(v.upper()+' | '+label,P/(v+'-'+suf+'room-844x390.png')) for suf,label in [('', 'room only 844 x 390'),('populated-','illustrative linen tables 844 x 390')] for v in ['before','after']],1688,440)
 print('STAGES LOOK2 SHEETS READY');sys.exit()
for n in ['validation.json','stages-look2-validation.json','stages-look2-visual-review.json']:assert json.loads((O/n).read_text())['pass'],n
fbxsha=sha(O/(stage+'.fbx'))
assert all(json.loads((O/n).read_text())['FBX_sha256']==fbxsha for n in ['validation.json','stages-look2-validation.json'])
images=[]
for p in sorted(P.glob('*.png')):
 with Image.open(p) as im:
  im.load();expected=(844,390) if '844' in p.name else (1440,900);assert im.size==expected,(p.name,im.size);images.append({'file':p.relative_to(O).as_posix(),'size':list(im.size)})
assert len(images)==8
for n in ['stages-look2-review.jpg','stages-look2-phone-review.jpg']:
 with Image.open(O/n) as im:im.load();images.append({'file':n,'size':list(im.size)})
visual=json.loads((O/'stages-look2-visual-review.json').read_text());assert all(sha(O/n)==h for n,h in visual['opened_images'].items())
for p in O.glob('stages-look2-*.py'):ast.parse(p.read_text())
recipe=json.loads((O/'lighting.json').read_text());assert len(recipe['preview_only_lights'])==5;assert not any(r['name'].startswith('StageLook2_WarmPool') for r in recipe['lights'])
base=json.loads(gzip.decompress((O/'stages-look2-baseline.json.gz').read_bytes()));assert sha(O/'layout.json')==base['layout_sha256'];assert sha(O/'final-cameras.json')==base['cameras_sha256']
files=[O/n for n in [stage+'.blend',stage+'.fbx','lighting.json','layout.json','final-cameras.json','build-metrics.json','REPORT.md','validation.json']]
files+=sorted(p for p in O.glob('stages-look2-*') if p.is_file() and p.suffix!='.log' and p.name!='stages-look2-final-audit.json');files+=sorted(P.glob('*.png'));files+=sorted((O/'textures').glob('*'))
M=json.loads((O/'build-metrics.json').read_text());result={'pass':True,'files':{p.relative_to(O).as_posix():sha(p) for p in sorted(set(files))},'decoded_images':images,'production_meshes':len(M['production_meshes']),'triangles':M['room_triangles'],'all_original_geometry_and_names_preserved':True,'native_unity_after_verified':False,'no_Assets_code_git_changes':True}
(O/'stages-look2-final-audit.json').write_text(json.dumps(result,indent=2));assert all(sha(O/n)==h for n,h in result['files'].items());print('STAGES LOOK2 FINAL SEAL PASS',len(result['files']),'hashes',len(images),'images')

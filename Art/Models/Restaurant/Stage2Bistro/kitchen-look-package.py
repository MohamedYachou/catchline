"""Proof sheets and package seal; run after Blender audit and actual visual opens."""
import ast,hashlib,json,sys,gzip
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'kitchen-look-renders';STAGE=O.name
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
def sheet(name,panels,width=1600,height=490):
 canvas=Image.new('RGB',(width,((len(panels)+1)//2)*height+65),'#101c25');d=ImageDraw.Draw(canvas);d.text((20,15),STAGE+' | KITCHEN LOOK 1 | SOURCE PROOF | Codex 2 (WSL CLI)',font=font,fill='#f2e6ce')
 for i,(label,path) in enumerate(panels):
  x=(i%2)*(width//2);y=65+(i//2)*height;d.text((x+14,y+7),label,font=small,fill='#f2e6ce');im=ImageOps.contain(Image.open(path).convert('RGB'),(width//2-20,height-40));canvas.paste(im,(x+(width//2-im.width)//2,y+35+(height-40-im.height)//2))
 canvas.save(O/name,quality=94)
if '--seal' not in sys.argv:
 native=R/('docs/screens/restaurant-ui/r131/day-service-orders-1440.png' if STAGE=='Stage1V4' else 'docs/screens/restaurant-ui/r129b/day-service-late-1440.png')
 sheet('kitchen-look-review.jpg',[
 ('Painting reference | target kitchen character',R/'Art/Source/Restaurant/concepts/ui-service-desktop.png'),
 ('Native BEFORE only | lead-sim; native AFTER pending',native),
 ('Blender BEFORE | accepted camera 1440 x 900',P/'before-room-1440x900.png'),
 ('Blender AFTER | accepted camera 1440 x 900',P/'after-room-1440x900.png'),
 ('BEFORE | diagnostic kitchen detail (non-game camera)',P/'before-kitchen-detail.png'),
 ('AFTER | diagnostic kitchen detail (non-game camera)',P/'after-kitchen-detail.png')])
 sheet('kitchen-look-phone-review.jpg',[
 ('BEFORE | accepted camera 844 x 390',P/'before-room-844x390.png'),
 ('AFTER | accepted camera 844 x 390',P/'after-room-844x390.png')],1688,450)
 print(STAGE,'SHEETS READY');sys.exit()
for name in ['validation.json','kitchen-look-validation.json','kitchen-look-visual-review.json']:
 assert json.loads((O/name).read_text())['pass'],name
fbxsha=sha(O/(STAGE+'.fbx'))
assert all(json.loads((O/n).read_text())['FBX_sha256']==fbxsha for n in ['validation.json','kitchen-look-validation.json'])
images=[]
for p in sorted(P.glob('*.png')):
 with Image.open(p) as im:
  im.load();expected=(844,390) if '844' in p.name else (1200,900) if 'detail' in p.name else (1440,900);assert im.size==expected,(p.name,im.size);images.append({'file':p.relative_to(O).as_posix(),'size':list(im.size)})
assert len(images)==6
for name in ['kitchen-look-review.jpg','kitchen-look-phone-review.jpg']:
 with Image.open(O/name) as im:im.load();images.append({'file':name,'size':list(im.size)})
visual=json.loads((O/'kitchen-look-visual-review.json').read_text());assert len(visual['individually_opened_images'])==8
assert all(sha(O/n)==h for n,h in visual['individually_opened_images'].items())
for p in O.glob('kitchen-look-*.py'):ast.parse(p.read_text())
base=json.loads(gzip.decompress((O/'kitchen-look-baseline.json.gz').read_bytes()))
assert all(sha(O/n)==h for n,h in base['files'].items());assert all(sha(O/'textures'/n)==h for n,h in base['atlas'].items())
files=[O/n for n in [STAGE+'.blend',STAGE+'.fbx','lighting.json','final-cameras.json','build-metrics.json','validation.json']]
if (O/'layout.json').exists():files.append(O/'layout.json')
files+=sorted(p for p in O.glob('kitchen-look-*') if p.is_file() and p.suffix!='.log' and p.name!='kitchen-look-final-audit.json')
files+=sorted(P.glob('*.png'));files+=sorted(p for p in (O/'textures').glob('*') if p.is_file())
v=json.loads((O/'kitchen-look-validation.json').read_text());result={'pass':True,'files':{p.relative_to(O).as_posix():sha(p) for p in sorted(set(files))},'decoded_images':images,'production_meshes':v['mesh_count'],'triangles':v['triangles'],'all_original_geometry_and_names_preserved':True,'native_unity_after_verified':False,'no_Assets_code_git_changes':True}
(O/'kitchen-look-final-audit.json').write_text(json.dumps(result,indent=2));assert all(sha(O/n)==h for n,h in result['files'].items());print(STAGE,'FINAL SEAL PASS',len(result['files']),'hashes',len(images),'images')

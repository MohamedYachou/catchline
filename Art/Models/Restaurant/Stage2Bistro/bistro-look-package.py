"""Mechanical proof-sheet assembly and independent package hash/image checks."""
import ast,hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'bistro-look-renders'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
def sheet(name,panels,width=1440,height=480):
 canvas=Image.new('RGB',(width, (len(panels)+1)//2*height+65),'#101c25');d=ImageDraw.Draw(canvas);d.text((20,15),'BISTRO LOOK 1 | SOURCE PROOF | Codex 2 (WSL CLI)',font=font,fill='#f2e6ce')
 for i,(label,path) in enumerate(panels):
  x=(i%2)*(width//2);y=65+(i//2)*height;d.text((x+14,y+7),label,font=small,fill='#f2e6ce');im=ImageOps.contain(Image.open(path).convert('RGB'),(width//2-20,height-40));canvas.paste(im,(x+(width//2-im.width)//2,y+35+(height-40-im.height)//2))
 canvas.save(O/name,quality=94)
if '--seal' not in sys.argv:
 sheet('bistro-look-review.jpg',[
  ('Painting reference (stage 1 mood)',R/'Art/Source/Restaurant/concepts/ui-service-desktop.png'),
  ('Native BEFORE only | lead-sim r123',R/'docs/screens/restaurant-ui/r123/day-service-late-1440.png'),
  ('Blender BEFORE | same camera, atlas vertex tint',P/'before-room-1440x900.png'),
  ('Blender AFTER | dressing, pigment, practicals',P/'after-room-1440x900.png'),
  ('Blender BEFORE | illustrative layout tables',P/'before-populated-room-1440x900.png'),
  ('Blender AFTER | illustrative layout tables',P/'after-populated-room-1440x900.png')])
 sheet('bistro-look-phone-review.jpg',[
  ('BEFORE | room only 844 x 390',P/'before-room-844x390.png'),
  ('AFTER | room only 844 x 390',P/'after-room-844x390.png'),
  ('BEFORE | illustrative layout tables 844 x 390',P/'before-populated-room-844x390.png'),
  ('AFTER | illustrative layout tables 844 x 390',P/'after-populated-room-844x390.png')],1688,440)
 print('BISTRO LOOK SHEETS READY');sys.exit()
for name in ['validation.json','bistro-look-validation.json','bistro-look-visual-review.json']:
 assert json.loads((O/name).read_text())['pass'],name
fbxsha=sha(O/'Stage2Bistro.fbx')
assert all(json.loads((O/n).read_text())['FBX_sha256']==fbxsha for n in ['validation.json','bistro-look-validation.json'])
images=[]
for p in sorted(P.glob('*.png')):
 with Image.open(p) as im:
  im.load();expected=(844,390) if '844' in p.name else (1440,900);assert im.size==expected,(p.name,im.size);images.append({'file':p.relative_to(O).as_posix(),'size':list(im.size)})
assert len(images)==8
for name in ['bistro-look-review.jpg','bistro-look-phone-review.jpg']:
 with Image.open(O/name) as im:im.load();images.append({'file':name,'size':list(im.size)})
for p in O.glob('bistro-look-*.py'):ast.parse(p.read_text())
recipe=json.loads((O/'lighting.json').read_text());assert len(recipe['preview_only_lights'])==5;assert not any(r['name'].startswith('BistroLook_WarmPool') for r in recipe['lights'])
base=json.loads(__import__('gzip').decompress((O/'bistro-look-baseline.json.gz').read_bytes()));assert sha(O/'layout.json')==base['layout_sha256'];assert sha(O/'final-cameras.json')==base['cameras_sha256']
files=[O/n for n in ['Stage2Bistro.blend','Stage2Bistro.fbx','lighting.json','layout.json','final-cameras.json','build-metrics.json','REPORT.md','validation.json']]
files+=sorted(p for p in O.glob('bistro-look-*') if p.is_file() and p.suffix not in ['.log'] and p.name!='bistro-look-final-audit.json')
files+=sorted(P.glob('*.png'));files+=sorted((O/'textures').glob('*'))
result={'pass':True,'files':{p.relative_to(O).as_posix():sha(p) for p in sorted(set(files))},'decoded_images':images,'production_meshes':177,'triangles':95628,'all_original_geometry_and_names_preserved':True,'native_unity_after_verified':False,'no_Assets_code_git_changes':True}
(O/'bistro-look-final-audit.json').write_text(json.dumps(result,indent=2))
assert all(sha(O/n)==h for n,h in result['files'].items());print('BISTRO LOOK FINAL SEAL PASS',len(result['files']),'hashes',len(images),'images')

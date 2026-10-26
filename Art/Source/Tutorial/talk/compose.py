"""Composite imagegen facial edits; never modify accepted originals.

Run with /home/mo/.venvs/catchline-ui/bin/python. Authoring is performed by
imagegen; Pillow only retains original pixels and makes audit/review artifacts.
"""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
POSES = ('wave', 'point', 'explain', 'cheer', 'think', 'map')
STATES = ('mouth-mid', 'mouth-open', 'blink')
# Source-pixel coordinates, origin top left, exclusive right/bottom.
# Each feature mask is much smaller than the enclosing face box.
CONFIG = {
 'wave': {'face': [425,365,685,590],
          'mouth': [[505,518],[543,501],[616,481],[641,488],[644,552],[611,583],[534,584],[504,555]],
          'eyes': [[430,390,518,476],[575,366,677,463]]},
 'point': {'face': [390,375,610,570],
           'mouth': [[453,501],[482,492],[552,492],[575,501],[574,553],[536,571],[475,562],[452,542]],
           'eyes': [[390,380,491,472],[543,373,610,462]]},
 'explain': {'face': [450,365,690,590],
             'mouth': [[519,511],[556,496],[625,484],[648,497],[645,560],[610,589],[547,585],[519,551]],
             'eyes': [[451,379,525,471],[583,366,685,465]]},
 'cheer': {'face': [412,360,645,592],
           'mouth': [[466,500],[496,486],[580,469],[606,479],[604,550],[567,588],[506,591],[473,548]],
           'eyes': [[414,374,488,465],[546,363,645,463]]},
 'think': {'face': [410,365,645,570],
           'mouth': [[444,499],[473,489],[539,490],[561,500],[559,548],[516,568],[469,550],[445,532]],
           'eyes': [[410,366,482,452],[530,375,641,471]]},
 'map': {'face': [399,355,638,559],
         'mouth': [[470,499],[507,485],[573,463],[602,466],[602,523],[566,557],[509,556],[473,533]],
         'eyes': [[399,375,479,463],[535,355,638,447]]},
}

def sha(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def protect_inputs():
 target = HERE / 'source-hashes.json'
 paths = [HERE.parent / 'generated' / f'{p}.png' for p in POSES]
 paths += [HERE.parent / f'mira-pose-{p}.png' for p in POSES]
 actual = {str(p.relative_to(ROOT)):sha(p) for p in paths}
 if target.exists():
  assert json.loads(target.read_text()) == actual, 'Accepted input changed!'
 else:
  target.write_text(json.dumps(actual, indent=2)+'\n')

def mask_for(pose, state, size):
 cfg=CONFIG[pose]
 mask=Image.new('L',size)
 draw=ImageDraw.Draw(mask)
 if state=='blink':
  for box in cfg['eyes']: draw.rounded_rectangle(tuple(box), radius=13, fill=255)
 else:
  draw.polygon([tuple(x) for x in cfg['mouth']], fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(3))
 # Clamp exactly to the announced face box, including all blur tails.
 gate=Image.new('L',size)
 x0,y0,x1,y1=cfg['face']
 ImageDraw.Draw(gate).rectangle((x0,y0,x1-1,y1-1),fill=255)
 return Image.fromarray(np.minimum(np.array(mask), np.array(gate)))

def compose(pose):
 source=Image.open(HERE.parent/'generated'/f'{pose}.png').convert('RGBA')
 assert source.size==(1122,1402)
 for state in STATES:
  raw=HERE/'generated'/f'{pose}-{state}.png'
  if not raw.exists(): continue
  edited=Image.open(raw).convert('RGBA')
  assert edited.size==source.size, (raw,edited.size)
  mask=mask_for(pose,state,source.size)
  final=Image.composite(edited,source,mask)
  final.putalpha(source.getchannel('A'))
  final.save(HERE/f'{pose}-{state}.png')

def font(size):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)

def sheets(pose):
 paths=[HERE.parent/'generated'/f'{pose}.png']+[HERE/f'{pose}-{s}.png' for s in STATES]
 if not all(p.exists() for p in paths): return
 frames=[Image.open(p).convert('RGBA') for p in paths]
 face=CONFIG[pose]['face']
 fw,fh=face[2]-face[0],face[3]-face[1]
 cell=max(350,fw*3+24)
 w,h=cell*4,540+fh*3+60
 sheet=Image.new('RGB',(w,h),'#F4EFE3')
 d=ImageDraw.Draw(sheet)
 d.text((20,12),f'MIRA / {pose.upper()} / source-size facial edits',font=font(25),fill='#173F57')
 labels=['CLOSED / accepted rest','MID','OPEN / ah','BLINK / source mouth']
 for i,(im,label) in enumerate(zip(frames,labels)):
  x=i*cell
  d.text((x+14,57),label,font=font(21),fill='#173F57')
  thumb=im.resize((337,421),Image.Resampling.LANCZOS)
  sheet.paste(thumb,(x+(cell-337)//2,91),thumb)
  crop=im.crop(face).resize((fw*3,fh*3),Image.Resampling.NEAREST)
  sheet.paste(crop,(x+12,553),crop)
  d.text((x+14,526),'Face at 3x source pixels',font=font(16),fill='#173F57')
 sheet.save(HERE/f'{pose}-contact-sheet.png')

def validate(require_all=False):
 report={'task':'MIRA-TALK-ART-1','coordinate_system':'source pixels, top-left origin; boxes [left,top,right,bottom), right/bottom exclusive',
         'expected_size':[1122,1402],'source_hashes_unchanged':True,'poses':{},'all_pass':True}
 (HERE/'diff-masks').mkdir(exist_ok=True)
 for pose in POSES:
  src_path=HERE.parent/'generated'/f'{pose}.png'
  source=np.array(Image.open(src_path).convert('RGBA'))
  box=CONFIG[pose]['face']
  x0,y0,x1,y1=box
  inside=np.zeros(source.shape[:2],bool);inside[y0:y1,x0:x1]=True
  entry={'source':str(src_path.relative_to(ROOT)),'source_sha256':sha(src_path),'face_box':box,'frames':{}}
  for state in STATES:
   path=HERE/f'{pose}-{state}.png'
   if not path.exists():
    if require_all: raise AssertionError(f'Missing {path}')
    continue
   im=Image.open(path)
   data=np.array(im.convert('RGBA'))
   assert data.shape==source.shape
   diff=np.any(data!=source,axis=2)
   outside=int(np.count_nonzero(diff&~inside));count=int(diff.sum())
   alpha_same=bool(np.array_equal(data[:,:,3],source[:,:,3]))
   mask_path=HERE/'diff-masks'/f'{pose}-{state}-diff.png'
   Image.fromarray(diff.astype('uint8')*255).save(mask_path)
   ys,xs=np.where(diff)
   changed_box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if count else None
   # Blink must preserve the complete mouth half; mouth edits preserve all eyes.
   invariant_y = {'wave':490,'explain':490,'cheer':480,'map':475,'point':485,'think':485}[pose]
   unchanged_other_features=bool(not np.any(diff[invariant_y:,:])) if state=='blink' else bool(not np.any(diff[:(min(y for x,y in CONFIG[pose]['mouth'])-12),:]))
   passed=outside==0 and count>0 and alpha_same and unchanged_other_features
   entry['frames'][state]={'file':path.name,'sha256':sha(path),'size':list(im.size),'mode':im.mode,
    'changed_pixel_count':count,'changed_bounds':changed_box,'outside_face_changed_pixels':outside,
    'alpha_identical':alpha_same,'opposite_features_identical':unchanged_other_features,
    'diff_mask':str(mask_path.relative_to(HERE)),'pass':passed}
   report['all_pass'] &= passed
  report['poses'][pose]=entry
 protect_inputs()
 report['delivered_frames']=sum(len(v['frames']) for v in report['poses'].values())
 if require_all: assert report['delivered_frames']==18
 (HERE/'talk-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 assert report['all_pass'], 'Pixel invariants failed'
 print(json.dumps({'frames':report['delivered_frames'],'pass':report['all_pass']}))

if __name__=='__main__':
 protect_inputs()
 for p in [p for p in sys.argv[1:] if p!='--final'] or POSES:
  compose(p);sheets(p)
 validate('--final' in sys.argv)

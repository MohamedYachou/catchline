"""ART-4 source-art packaging; no production or Assets mutations."""
from pathlib import Path
import importlib.util,json,hashlib,shutil,sys
from PIL import Image,ImageDraw,ImageFont,ImageOps
P=Path(__file__).resolve().parent
EX=P.parent; ART=EX.parent; ROOT=ART.parents[2]
M=EX/'s15/moods'; C=EX/'s5'
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py')
k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
IDS=['pan-fish','fish-and-chips','platter','crab','calamari','tea','beer','fries','bread']
def meta(folder,entries,layout,styles=[]):
 k.dump(folder/'manifest.json',entries);k.dump(folder/'layout.json',layout)
 k.dump(folder/'text-styles.json',dict(styles=styles,notes='Live labels only; exported paintings contain no words.'))
 k.dump(folder/'slices.json',dict(sprites=[],notes='Preserve aspect. No icon or ribbon slicing; live text scales independently.'))
 k.contact(folder,entries,folder/'contact-sheet.jpg')
def dish():
 entries=[];placements=[]
 for i,id in enumerate(IDS):
  e=k.export(P,'v2-dish-'+id,P/'provenance'/(id+'.png'),contain=(91,75))
  e.update(usage='Menu dish art: aspect-fit in order bubble, plan and closing receipt. Source reference grilled fish is91x51 and soup110x75 logical; new paintings fit91x75 with no stretch.')
  x=22+(i%3)*275;y=65+(i//3)*100;r=[x,y,*e['logicalSize']]
  e['rect']=r;entries.append(e);placements.append(dict(name=e['name'],screen='dish-review',use=id,rect=r,z=10))
 meta(P,entries,dict(screen='dish-review',canvas=[844,390],placements=placements,notes='Catalog demo only; per-screen runtime aspect-fit anchors owned by Claude.'))
 # Each sprite in three real UI roles; 24px order bubble,48px receipt,91px plan.
 out=Image.new('RGBA',(844*3,390*3),'#EAE3D4');d=ImageDraw.Draw(out)
 d.text((30,24),'NEW DISHES - order 24px / receipt 48px / plan 91px',font=ImageFont.truetype(str(k.FONT),54),fill='#173F57')
 for i,e in enumerate(entries):
  x=18+(i%3)*277;y=55+(i//3)*108
  d.text((x*3,y*3),IDS[i],font=ImageFont.truetype(str(k.FONT),36),fill='#173F57')
  im=Image.open(P/e['file']).convert('RGBA')
  for bx,cap in [(x,24),(x+46,48),(x+120,91)]:
   w,h=k.fit_size(im,(cap,65));k.put(out,im,[bx,y+27,w,h])
 out.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(P/'actual-size-review.jpg',quality=96)
 # Direct reference style/visual-weight comparison at matched48px widths.
 review=Image.new('RGBA',(844*3,150*3),'#EAE3D4');dd=ImageDraw.Draw(review)
 paths=[ROOT/'Assets/Art/UI/rx-dish-grilled-fish.png',ROOT/'Assets/Art/UI/rx-dish-fish-soup.png']+[P/e['file'] for e in entries]
 for i,path in enumerate(paths):
  im=Image.open(path).convert('RGBA');w,h=k.fit_size(im,(48,50));k.put(review,im,[12+i*75,35,w,h]);dd.text(((12+i*75)*3,90*3),('ref' if i<2 else IDS[i-2]),font=ImageFont.truetype(str(k.FONT),25),fill='#173F57')
 review.resize((844,150),Image.Resampling.LANCZOS).convert('RGB').save(P/'reference-comparison.jpg',quality=96)
 print('A packaged9 dish sprites')
def moods():
 basepath=M/'baseline-manifest.json'
 if not basepath.exists():shutil.copy2(EX/'s15/manifest.json',basepath)
 base=k.load(basepath);entries=[];placements=[]
 im=Image.open(ART/'concepts/ui-2-service.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
 for kind,slot in zip(['happy','annoyed','leaving'],[[380,142,32,32],[522,210,32,32],[620,258,34,32]]):
  e=k.export(EX/'s15','v2-s15-mood-'+kind,M/'provenance'/('mood-'+kind+'.png'),contain=slot[2:]);e.update(screen=15,mood=kind)
  r=[slot[0],slot[1],*e['logicalSize']];e['rect']=r;entries.append(e);placements.append(dict(name=e['name'],screen='phone',use='table-'+kind,rect=r,z=40));k.put(im,Image.open(EX/'s15'/e['file']),r)
 k.dump(EX/'s15/manifest.json',base+entries)
 k.dump(M/'manifest.json',[dict(e,file='../'+e['file']) for e in entries])
 k.dump(M/'layout.json',dict(screen='phone',canvas=[844,390],background='../../../concepts/ui-2-service.png',backgroundSha256=k.sha(ART/'concepts/ui-2-service.png'),placements=placements,notes='Illustrative world-anchored mood placements. At runtime anchor above actual table; show one mood at a time, avoid order/task markers.'))
 k.dump(M/'text-styles.json',dict(styles=[],notes='Nonverbal markers. Status meaning also communicated by gameplay response.'))
 k.dump(M/'slices.json',dict(sprites=[],notes='Aspect-preserving fixed icons. Existing steam strip unchanged.'))
 k.contact(EX/'s15',entries,M/'contact-sheet.jpg')
 im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(M/'actual-size-context.jpg',quality=96)
 k.dump(M/'steam-reference.json',dict(file='../v2-s15-steam-strip.png',sha256=k.sha(EX/'s15/v2-s15-steam-strip.png'),frames=4,notes='Already delivered, preserved byte-for-byte; existing frame rects remain in parent manifest.'))
 print('B packaged3 mood sprites; existing steam preserved')
def closing():
 entries=[k.export(C,'v2-s5-best-night-ribbon',C/'provenance/best-night.png',contain=(194,43)),k.export(C,'v2-s5-full-house-stamp',C/'provenance/full-house.png',contain=(133,38))]
 placements=[];styles=[];fits=[]
 im=Image.open(ART/'concepts/ui-5-closing.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
 # Two positions in open top band; original title stays intact. Context proof is an overlay demonstration.
 for e,x,y in [(entries[0],18,32),(entries[1],696,34)]:
  r=[x,y,*e['logicalSize']];e['rect']=r;placements.append(dict(name=e['name'],screen='phone',use=e['name'],rect=r,z=50));k.put(im,Image.open(C/e['file']),r)
  if 'best-night' in e['name']:t=k.label('best-night-label','phone','Best night yet!',[x+25,y+9,e['logicalSize'][0]-50,20],17,'center')
  else:t=k.label('full-house-label','phone','Full house',[x+31,y+9,e['logicalSize'][0]-40,16],14,'center')
  styles.append(t);fits.append(k.drawtext(im,t))
 meta(C,entries,dict(screen='phone',canvas=[844,390],background='../../concepts/ui-5-closing.png',backgroundSha256=k.sha(ART/'concepts/ui-5-closing.png'),placements=placements,notes='Optional celebration overlays. Native layout/conditions owned by Claude; shown over reference for art review, not live game state.'),styles)
 k.dump(C/'text-measurements.json',fits)
 im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(C/'actual-size-context.jpg',quality=96)
 print('C packaged2 stamp sprites; live label fits PASS')
if __name__=='__main__':
 {'A':dish,'B':moods,'C':closing}[sys.argv[1]]()

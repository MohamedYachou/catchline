"""Independent source-art delivery audit; does not rewrite art."""
from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw,ImageChops,ImageFont
P=Path(__file__).resolve().parent;EX=P.parent;ART=EX.parent;ROOT=ART.parents[2]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(cond,msg):
 if not cond:raise AssertionError(msg)
folders=[P,EX/'s1-card-states',EX/'closed-sign'];allnames=[];results=[];visuals=[];textFits=[];preserved=0
for file,old in load(P/'preservation-baseline.json').items():
 check(sha(ROOT/file)==old,'Accepted art changed: '+file);preserved+=1
for folder in folders:
 manifest=load(folder/'manifest.json');lookup={e['name']:e for e in manifest}
 for e in manifest:
  path=folder/e['file'];im=Image.open(path)
  check(im.mode=='RGBA',str(path)+' not RGBA')
  check(list(im.size)==e['size']==[v*3 for v in e['logicalSize']],e['name']+' dimensions')
  check(im.getchannel('A').getbbox()==(0,0,*im.size),e['name']+' padded alpha')
  check(im.getchannel('A').getextrema()[0]==0,e['name']+' no transparency')
  check(sha(path)==e['sha256'],e['name']+' export hash')
  prov=e['provenance'];check(sha(ROOT/prov['source'])==prov['sourceSha256'],e['name']+' source hash')
  if e['borders']:
   l,b,r,t=e['borders'];check(l+r<im.width and t+b<im.height,e['name']+' slice caps')
  check(not e['native3xDetailClaim'],'Incorrect painted-detail claim')
  allnames.append(e['name']);results.append(dict(file=str(path.relative_to(ROOT)),size=list(im.size),sha256=sha(path),tight=True))
 for sc in load(folder/'layout.json')['screens']:
  canvas=sc['canvas'];screen=sc['screen'];bg=(folder/sc['background']).resolve()
  check(sha(bg)==sc['backgroundSha256'],'Background changed')
  reconstructed=folder/((screen+'-reconstructed-3x.png') if folder==P else 'reconstructed-3x.png')
  im=Image.open(reconstructed).convert('RGBA');original=Image.open(bg).convert('RGBA').resize(tuple(v*3 for v in canvas),Image.Resampling.NEAREST)
  check(im.size==original.size,'Reconstruction canvas')
  mask=Image.new('L',im.size,0);draw=ImageDraw.Draw(mask)
  for p in sc['placements']:
   x,y,w,h=p['rect'];check(x>=0 and y>=0 and x+w<=canvas[0] and y+h<=canvas[1],str(p)+' out of canvas')
   draw.rectangle((x*3,y*3,(x+w)*3-1,(y+h)*3-1),fill=255)
   if p['name'] not in lookup:
    check((folder/p['file']).exists(),'Missing external painted use')
  diff=ImageChops.difference(im,original).convert('RGB');channels=diff.split();diff=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]);outside=ImageChops.subtract(diff,mask)
  check(outside.getbbox() is None,str(folder)+' modified background outside declared placements')
  for st in load(folder/'text-styles.json')['styles']:
   if st['screen']!=screen:continue
   x,y,w,h=st['rect'];font=ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'),st['size']*3);d=ImageDraw.Draw(Image.new('RGB',(1,1)));parts=['']
   for word in st['text'].split():
    test=(parts[-1]+' '+word).strip()
    if not st.get('wrap') or d.textlength(test,font=font)<=w*3:parts[-1]=test
    else:parts.append(word)
   boxes=[d.textbbox((0,0),s,font=font) for s in parts];width=max(b[2]-b[0] for b in boxes)/3;height=(boxes[0][3]-boxes[0][1])/3+(len(parts)-1)*st['lineHeight']
   check(width<=w and height<=h,st['id']+' text clipped')
   if st['id']=='coaching-line':check(len(st['text'])==110 and len(parts)==3,'Coach capacity')
   textFits.append(dict(id=st['id'],screen=screen,width=width,height=height,lines=len(parts),passFit=True))
  visuals.append(dict(screen=screen,backgroundPreservedOutsidePlacements=True,reconstructionSha256=sha(reconstructed)))
check(len(allnames)==len(set(allnames)),'Duplicate new export names')
for path in EX.rglob('v2-*.png'):
 if path.parent in folders or 'provenance' in path.parts:continue
 check(path.stem not in allnames,'New export collides with '+str(path))
opened=load(P/'visual-review.json')
for record in opened['actuallyOpened']:
 path=ROOT/record['file'];check(sha(path)==record['sha256'],'Visual changed since open: '+str(path))
report=dict(status='PASS',exports=results,exportCount=len(results),preservedAcceptedFiles=preserved,textFits=textFits,sourceBackgroundPreservation=visuals,actuallyOpenedHashes=len(opened['actuallyOpened']),limits=['Source art only; Claude imports/wires; Mo/lead acceptance pending.','3x output uses resampled paintings and sliced accepted kit, not a native3x-detail claim.','Affordability comparison uses illustrative source numbers; runtime binds wallet and price.'])
(P/'delivery-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS',len(results),'tight RGBA3x exports;',preserved,'accepted files unchanged;',len(textFits),'text fits;',len(visuals),'background-preservation checks')

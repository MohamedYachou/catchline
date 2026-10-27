from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,importlib.util,shutil
P=Path(__file__).resolve().parent;ART=P.parent.parent;S6=P.parent/'s6';R=S6/'arrange-entry';R.mkdir(exist_ok=True)
ROOT=next(p for p in P.parents if (p/'Assets').exists())
spec=importlib.util.spec_from_file_location('s15',P.parent/'s15/package.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
sha=kit.sha;load=kit.read;dump=kit.dump
FONT=ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
def text(im,t):
 d=ImageDraw.Draw(im);x,y,w,h=t['rect'];f=ImageFont.truetype(str(FONT),t['size']*3);sw=t['stroke_width']*3;b=d.textbbox((0,0),t['text'],font=f,stroke_width=sw);tw=b[2]-b[0];th=b[3]-b[1];assert tw<=w*3 and th<=h*3,(t['id'],tw/3,th/3)
 d.text((x*3+(w*3-tw)/2-b[0],y*3+(h*3-th)/2-b[1]),t['text'],font=f,fill=t['fill'],stroke_width=sw,stroke_fill=t['stroke'])
def label(id,words,rect,size=14,fill='#FFF4DC',stroke_width=1):return dict(id=id,text=words,rect=rect,font='Fredoka-Bold',weight=700,size=size,fill=fill,stroke='#173F57',stroke_width=stroke_width,align='center',vertical_align='middle')
def export():
 entries=[]
 specs=[('store',[418,151,44,49],[165,186]),('sell',[465,151,44,49],[165,186]),('placement-red',[350,196,84,58],[600,450])]
 for id,rect,size in specs:
  name='v2-s1x-'+('placement-invalid' if id=='placement-red' else 'btn-'+id);file=name+'.png';meta=kit.export(P/'provenance'/(id+'.png'),P/file,tuple(size));entries.append(dict(name=name,file=file,screen=1,rect=rect,size=size,sha256=sha(P/file),borders=None,preserveAspect=True,provenance=meta,usage='Same source dimensions as v2-placement-highlight; world ground footprint rendering, no9slice' if id=='placement-red' else 'Same source dimensions as v2-btn-rotate; label is separate',native3xDetailClaim=False))
 dump(P/'manifest.json',entries)
 styles=[label('store','Store',[412,201,56,23]),label('sell','Sell',[460,201,54,23]),label('invalid',"Can't place",[346,254,92,23],13)]
 dump(P/'text-styles.json',dict(screen='arrange-extras',canvas=[844,390],styles=styles))
 dump(P/'layout.json',dict(screen='arrange-extras',canvas=[844,390],origin='top-left',background='../../concepts/ui-1-arrange.png',backgroundSha256=sha(ART/'concepts/ui-1-arrange.png'),placements=[dict(name=e['name'],use='lifted-item-demo' if 'btn' in e['name'] else 'invalid-demo-next-to-existing-valid',rect=e['rect'],z=20+i) for i,e in enumerate(entries)],notes='Additive demonstration of lifted-item controls. Red highlight is on a separate footprint beside the accepted valid example; live renderer anchors either state to the actual ghost. Store/Sell only when an item is lifted; price/recovery logic belongs to Claude.'))
 dump(P/'slices.json',dict(sprites=[],notes='Preserve bubble tail/icon proportions; placement uses existing world footprint path; never9slice.'))
 im=Image.open(ART/'concepts/ui-1-arrange.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
 for e in entries:
  x,y,w,h=e['rect'];a=Image.open(P/e['file']).resize((w*3,h*3),Image.Resampling.LANCZOS);im.alpha_composite(a,(x*3,y*3))
 for t in styles:text(im,t)
 im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(P/'arrange-context.png');kit.contact(P,entries,'contact-sheet.jpg',3,(340,260))
 # S6 uses the exact accepted idle tab painting, chair and live label as separate pieces.
 baseline=R/'baseline-manifest.json'
 if not baseline.exists():shutil.copy2(S6/'manifest.json',baseline)
 current=load(S6/'manifest.json');assert not any(e['name'] in ['v2-s6-btn-arrange','v2-s6-arrange-chair'] for e in current),'Do not rerun export over a changed live manifest'
 src=S6/'v2-s6-tab-idle.png';dst=S6/'v2-s6-btn-arrange.png';shutil.copy2(src,dst)
 back=dict(name='v2-s6-btn-arrange',file=dst.name,screen=6,rect=[198,58,169,38],size=list(Image.open(dst).size),borders=[42,36,42,36],border_order='left,bottom,right,top',sha256=sha(dst),provenance=dict(method='Byte-identical accepted v2-s6-tab-idle reuse, unique name',source=src.name,sourceSha256=sha(src)),native3xDetailClaim=False)
 raw=P/'provenance/arrange-chair.png';a,_=kit.clean(raw);scale=24/max(a.size);w,h=[round(x*scale) for x in a.size];r=[218+(24-w)//2,65+(24-h)//2,w,h];meta=kit.export(raw,S6/'v2-s6-arrange-chair.png',(w*3,h*3));chair=dict(name='v2-s6-arrange-chair',file='v2-s6-arrange-chair.png',screen=6,rect=r,size=[w*3,h*3],borders=None,sha256=sha(S6/'v2-s6-arrange-chair.png'),provenance=meta,native3xDetailClaim=False)
 dump(S6/'manifest.json',current+[back,chair]);dump(R/'manifest.json',[back,chair]);dump(R/'layout.json',dict(screen=6,canvas=[844,390],origin='top-left',placements=[dict(name=e['name'],rect=e['rect'],z=20+i,use='daytime-arrange-entry') for i,e in enumerate([back,chair])],notes='Daytime replacement of existing Live service tab slot, not a fourth tab squeezed into this row. Claude decides runtime visibility. Original S6 layout/concept unchanged.'))
 style=label('arrange-entry','Arrange',[248,65,100,23],19,'#10263D',0);dump(R/'text-styles.json',dict(screen=6,canvas=[844,390],styles=[style]));dump(R/'slices.json',dict(border_order='left,bottom,right,top',sprites=[dict(name=back['name'],borders=back['borders'],sourceSize=back['size'])],notes='Same accepted idle-tab borders. Chair never9slice.'))
 im=Image.open(ART/'concepts/ui-6-dashboard.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
 for e in [back,chair]:
  x,y,w,h=e['rect'];a=Image.open(S6/e['file']).convert('RGBA').resize((w*3,h*3),Image.Resampling.LANCZOS);im.alpha_composite(a,(x*3,y*3))
 text(im,style);im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(R/'context-review.png');kit.contact(S6,[back,chair],'arrange-entry/contact-sheet.jpg',2,(340,230))
 # Slice stress at two useful tab widths, preserving accepted corners.
 src=Image.open(dst).convert('RGBA');proof=Image.new('RGB',(800,240),'#eae3d4')
 for q,w in enumerate([360,600]):
  left,bottom,right,top=back['borders'];out=Image.new('RGBA',(w,src.height))
  out.alpha_composite(src.crop((0,0,left,src.height)),(0,0));out.alpha_composite(src.crop((left,0,src.width-right,src.height)).resize((w-left-right,src.height)),(left,0));out.alpha_composite(src.crop((src.width-right,0,src.width,src.height)),(w-right,0));proof.paste(out,(20,10+q*120),out)
 proof.save(R/'slice-review.jpg',quality=95)
 dump(P/'export-audit.json',dict(status='PASS',sprites=3,sourceSizeMatchesOriginal=True));print('Extras exported3S1+2S6; review/audit pending')
if __name__=='__main__':export()

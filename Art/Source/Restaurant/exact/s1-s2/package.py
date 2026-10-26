"""Mechanical packaging only. Imagegen creates art; FFmpeg trims/scales/contacts.
Pillow is used read-only for alpha/dimensions/hash audits, never to paint images.
Run with /home/mo/.venvs/catchline-ui/bin/python package.py.
"""
from pathlib import Path
import json, subprocess, hashlib, math
from PIL import Image
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[4]
REF=PROJECT/'Art/Source/Restaurant/concepts'
def run(args):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1',*args],check=True,stdout=subprocess.DEVNULL)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def write(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
def package():
    rows=[]
    prior={v['name']:v for v in read(ROOT/'asset-audit.json')} if (ROOT/'asset-audit.json').exists() else {}
    placements=read(ROOT/'layout.json')['placements'] if (ROOT/'layout.json').exists() else []
    for p in sorted((ROOT/'provenance').glob('*-receipt.json')):
        job=read(p); name=job['name']; raw=ROOT/'provenance'/(name+'-generated.png')
        if not raw.exists(): continue
        im=Image.open(raw)
        if im.mode!='RGBA': raise ValueError(f'{name}: expected intrinsic RGBA')
        # Generated transparency contains faint low-alpha noise far from the
        # intended silhouette. Locate real artwork at alpha>=32, keep12px halo.
        core=im.getchannel('A').point(lambda a:255 if a>=32 else 0).getbbox()
        box=None if core is None else (max(0,core[0]-12),max(0,core[1]-12),min(im.width,core[2]+12),min(im.height,core[3]+12))
        if box is None: raise ValueError(name+' is empty')
        rect=job.get('rect',[0,0,128,128]); size=list(job['size'])
        size=[max(size[i],3*rect[i+2]) for i in range(2)]
        # Every responsive/repeated instance must retain >=3x export pixels,
        # including desktop placements larger than the primary source crop.
        for placement in placements:
            if placement['asset']==name:
                size=[max(size[i],3*placement['rect'][i+2]) for i in range(2)]
        if name=='v2-staff-rail': size=[4122,336]
        out=ROOT/(name+'.png')
        x,y,x2,y2=box; cw,ch=x2-x,y2-y
        # Fixed frames are aspect-normalized to their exact export rectangle.
        # Illustrations preserve aspect with transparent letterbox padding.
        icon=('icon' in name or 'bust' in name or 'item-rest' in name)
        pad=6
        target=(size[0]-pad*2,size[1]-pad*2)
        vf=f'crop={cw}:{ch}:{x}:{y},'
        if icon:
            vf+=f'scale={target[0]}:{target[1]}:force_original_aspect_ratio=decrease:flags=lanczos,pad={size[0]}:{size[1]}:(ow-iw)/2:(oh-ih)/2:color=0x00000000'
        else:
            vf+=f'scale={target[0]}:{target[1]}:flags=lanczos,pad={size[0]}:{size[1]}:{pad}:{pad}:color=0x00000000'
        old=prior.get(name,{})
        if not (out.exists() and old.get('sourceSha256')==sha(raw) and old.get('size')==size and old.get('sha256')==sha(out)):
            run(['-i',str(raw),'-vf',vf,'-frames:v','1',str(out)])
        final=Image.open(out); alpha=final.getchannel('A')
        if final.size!=tuple(size) or alpha.getextrema()[0]!=0: raise ValueError(name+' bad export')
        rows.append({'name':name,'file':out.name,'size':size,'sourceSize':list(im.size),'alphaBounds':list(alpha.getbbox()),'sourceAlphaBounds':list(box),'mode':final.mode,'alpha':list(alpha.getextrema()),'referenceRect':rect,'referenceScreen':job.get('screen'),'sha256':sha(out),'sourceSha256':sha(raw),'sourceReceipt':str(p.relative_to(ROOT)),'method':'imagegen artwork; FFmpeg alpha-bounds trim, aspect-preserving fit' if icon else 'imagegen artwork; FFmpeg alpha-bounds trim, exact-rectangle normalization','sourceUpscaled':cw<target[0] or ch<target[1],'opened':False})
    write(ROOT/'asset-audit.json',rows)
    return rows
def contact(row):
    name=row['name']; job=read(ROOT/row['sourceReceipt']); rect=job.get('rect')
    screen=job.get('screen','phone')
    if name.startswith('v2-bust-'):
        ref=PROJECT/'Assets/Art/UI'/('v2-portrait-'+name.removeprefix('v2-bust-')+'-deck.png'); rect=None
    else:
        ref=REF/({'phone':'ui-2-service.png','arrange':'ui-1-arrange.png','desktop':'ui-service-desktop.png'}[screen])
    crop='' if rect is None else f'crop={rect[2]}:{rect[3]}:{rect[0]}:{rect[1]},'
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    filters=(f'[0:v]{crop}scale=380:220:force_original_aspect_ratio=decrease:flags=lanczos,pad=400:280:(ow-iw)/2:(oh-ih)/2+15:color=0xEEE4CE,format=rgba,drawtext=fontfile={font}:text=REFERENCE:x=12:y=8:fontsize=16:fontcolor=0x0A2546[a];'
    f'[1:v]scale=380:220:force_original_aspect_ratio=decrease:flags=lanczos,pad=400:280:(ow-iw)/2:(oh-ih)/2+15:color=0xD2DDDE,format=rgba,drawtext=fontfile={font}:text={name}:x=10:y=8:fontsize=15:fontcolor=0x0A2546[b];[a][b]hstack=inputs=2[out]')
    out=ROOT/'review'/(name+'-compare.png')
    if not out.exists() or out.stat().st_mtime < max((ROOT/row['file']).stat().st_mtime,(ROOT/row['sourceReceipt']).stat().st_mtime):
        run(['-i',str(ref),'-i',str(ROOT/row['file']),'-filter_complex',filters,'-map','[out]','-frames:v','1',str(out)])
    return out
if __name__=='__main__':
    import sys
    rows=read(ROOT/'asset-audit.json') if '--contacts-only' in sys.argv else package()
    if '--package-only' not in sys.argv:
        for r in rows: contact(r)
    print(json.dumps({'packaged':len(rows),'contacts':len(list((ROOT/'review').glob('*-compare.png')))}))

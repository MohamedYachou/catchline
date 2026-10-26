"""Mechanical sprite packaging only: preserve generated pixels/alpha, trim, fit, audit."""
from pathlib import Path
import json, shutil, hashlib
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
def prepare():
    audit=json.loads((ROOT/'asset-audit.json').read_text()) if (ROOT/'asset-audit.json').exists() else []
    existing={x['file']:x for x in audit}
    for receipt in sorted((ROOT/'provenance').glob('*-receipt.json')):
        job=json.loads(receipt.read_text())
        name=job['name']; out=ROOT/(name+'.png')
        if name+'.png' in existing: continue
        source=Path(job['path']); raw=ROOT/'provenance'/(name+'-generated.png')
        shutil.copy2(source,raw)
        (ROOT/'provenance'/(name+'-prompt.txt')).write_text(job['prompt'],encoding='utf-8')
        im=Image.open(raw).convert('RGBA'); box=im.getchannel('A').getbbox()
        if not box: raise ValueError(name+' empty alpha')
        size=tuple(job['size']); pad=job.get('padding',4)
        if job.get('fullBleed'):
            from PIL import ImageOps
            final=ImageOps.fit(im,size,Image.Resampling.LANCZOS)
        else:
            content=im.crop(box); content.thumbnail((size[0]-2*pad,size[1]-2*pad),Image.Resampling.LANCZOS)
            final=Image.new('RGBA',size); final.alpha_composite(content,((size[0]-content.width)//2,(size[1]-content.height)//2))
        final.save(out)
        row={'file':out.name,'size':list(size),'mode':'RGBA','alpha':list(final.getchannel('A').getextrema()),'source':raw.name,'sourceSize':list(im.size),'originalAlphaBBox':list(box),'method':'built-in imagegen; alpha-bounds trim and downsample only' if not job.get('fullBleed') else 'built-in imagegen; aspect fill/downsample only','opened':False,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
        audit.append(row); existing[out.name]=row
    (ROOT/'asset-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    cols=6; cellw=220; cellh=240; rows=(len(audit)+cols-1)//cols
    sheet=Image.new('RGB',(cols*cellw,80+rows*cellh),'#F4EFE3'); d=ImageDraw.Draw(sheet)
    d.text((20,20),'Restaurant UI art - generated sprites / review contact',fill='#173F57')
    for i,row in enumerate(audit):
        im=Image.open(ROOT/row['file']).convert('RGBA'); im.thumbnail((200,190),Image.Resampling.LANCZOS)
        x=(i%cols)*cellw+(cellw-im.width)//2;y=80+(i//cols)*cellh
        sheet.paste(im,(x,y),im);d.text(((i%cols)*cellw+8,y+200),row['file'],fill='#173F57')
    sheet.save(ROOT/'contact-all.png')
    print(json.dumps({'count':len(audit),'newest':[x['file'] for x in audit[-12:]]}))
if __name__=='__main__':prepare()

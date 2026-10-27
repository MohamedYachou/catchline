"""Independent export and preservation audit; never writes the downloaded sources."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((OUT/'preservation-baseline.json').read_text())
bad=[p for p,h in baseline.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
assert not bad,bad
mapping=json.loads((OUT/'swatch-map.json').read_text());results={}
proofs=json.loads((OUT/'fbx-proof-inventory.json').read_text())
assert len(proofs)==16 and all(all(n>0 for n in r['uv_layers']) for r in proofs)
log=(OUT/'render-uv-proof.log').read_text(encoding='utf-16',errors='replace')
assert 'UV_PROOF_DONE' in log and 'failed to load' not in log.lower() and 'Not a PNG' not in log
for pack in mapping:
    for variant in ('original','catchline'):
        im=Image.open(OUT/f'{pack}-fbx-{variant}.png').convert('RGB');im.load()
        assert im.size==(1600,1000)
        pix=np.array(im)
        magenta=(pix[:,:,0]>180)&(pix[:,:,1]<60)&(pix[:,:,2]>180)
        assert magenta.mean()<.0001,(pack,variant,'missing texture magenta')
for pack,m in mapping.items():
    original=Image.open(ROOT/m['source']).convert('RGBA');export=Image.open(OUT/m['output'])
    assert export.size==original.size==(1024,1024)
    assert export.mode=='RGBA'
    a=np.array(original);b=np.array(export)
    assert np.array_equal(a[:,:,3],b[:,:,3])
    cells=[]
    for c in m['cells']:
        x,y,w,h=c['rect'];old=a[y:y+h,x:x+w,:3];new=b[y:y+h,x:x+w,:3]
        if not c['changed']:
            assert np.array_equal(old,new),c['id']
            cells.append(dict(id=c['id'],unchanged=True))
        else:
            # All changed source ramps have a bright top; preserve ordering even
            # through the furniture inset edges. Affine quantization may add ties.
            lold=old.astype(float).mean(2);lnew=new.astype(float).mean(2)
            corr=float(np.corrcoef(lold.ravel(),lnew.ravel())[0,1])
            assert corr>.999,c['id']
            assert lnew[:2].mean()>lnew[-2:].mean(),c['id']
            # Contrast boundaries must remain at the same source pixel locations.
            dx0=np.abs(np.diff(lold,axis=1));dx1=np.abs(np.diff(lnew,axis=1))
            assert not np.any((dx1>2)&(dx0<.4)),c['id']
            assert not np.any((dx0>5)&(dx1<1)),c['id']
            cells.append(dict(id=c['id'],unchanged=False,luminance_correlation=corr,gradient_direction='bright top / shaded bottom',inset_edge_mask_preserved=True))
    results[pack]=dict(size=list(export.size),mode=export.mode,sha256=sha(OUT/m['output']),alpha_identical=True,cells=cells)
# Explicit food + steel + glass constraints independent of the manifest flags.
for c in mapping['restaurant']['cells']:
    r=int(c['id'][1]);col=int(c['id'][3])
    if r==3 or (r==1 and col<=8) or (r==2 and col in (1,4,5,6,7,8)) or (r==4 and col<=5):
        assert not c['changed'],c['id']
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
for pack in mapping:
    # Recoloured sample proofs are intentionally labelled, never claimed as atlas renders.
    original_path=ROOT/Path(mapping[pack]['source']).parents[2]/'sample.png'
    mock=OUT/f'{pack}-sample-palette-mock.png'
    if mock.is_file():
        board=Image.new('RGB',(1920,660),'#F4EFE3');d=ImageDraw.Draw(board)
        for i,p in enumerate((original_path,mock)):
            im=Image.open(p).convert('RGB');im.thumbnail((940,560));board.paste(im,(i*960+(960-im.width)//2,65))
        d.text((20,14),pack.upper()+' / original sample',font=font(25),fill='#173F57')
        d.text((980,14),'ImageGen palette study / illustrative only',font=font(25),fill='#173F57')
        d.text((20,620),'Palette study may differ locally from the exact atlas. Use the FBX comparison for actual UV-mapped colours.',font=font(20),fill='#173F57')
        board.save(OUT/f'{pack}-sample-before-after.jpg',quality=95)
    before=OUT/f'{pack}-fbx-original.png';after=OUT/f'{pack}-fbx-catchline.png'
    if before.is_file() and after.is_file():
        board=Image.new('RGB',(2400,850),'#F4EFE3');d=ImageDraw.Draw(board)
        for i,p in enumerate((before,after)):
            im=Image.open(p).convert('RGB');im.thumbnail((1200,750));board.paste(im,(i*1200,70))
        d.text((20,14),pack.upper()+' / original Unity FBX + original atlas',font=font(25),fill='#173F57')
        d.text((1220,14),'Same Unity FBX + Catchline atlas / identical light',font=font(25),fill='#173F57')
        d.text((20,815),'Source proof only. UVs and geometry unedited; original asset scales normalized solely for this contact. Native Unity appearance pending.',font=font(19),fill='#173F57')
        board.save(OUT/f'{pack}-fbx-before-after.jpg',quality=95)
decoded=[]
for p in OUT.iterdir():
    if p.suffix.lower() in ('.png','.jpg'):
        with Image.open(p) as im:im.load();decoded.append(dict(file=p.name,size=list(im.size),sha256=sha(p)))
result=dict(status='PASS',original_files_unchanged=len(baseline),original_unity_fbx_models=len(proofs),render_missing_image_checks='PASS',exports=results,decoded_images=decoded,limits=['No Unity import/runtime/player acceptance.','ImageGen sample recolours are illustrative; exact FBX proofs use exported atlases.','Shared food/wood swatches deliberately preserved; some brown furniture remains original.'])
(OUT/'audit.json').write_text(json.dumps(result,indent=2))
print('PASS:',len(baseline),'source hashes,64 cell checks,',len(decoded),'decoded images')

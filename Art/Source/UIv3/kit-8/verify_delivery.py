"""Independent read-only checks of SERVICE-UI-KIT-8's on-disk delivery.

Writes only kit-8/delivery-audit.json. Does not execute any art builder or Unity.
"""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def inside(box,w,h):
    x,y,bw,bh=box
    return x>=0 and y>=0 and bw>0 and bh>0 and x+bw<=w and y+bh<=h


def main():
    manifest=json.loads((HERE/'manifest.json').read_text())
    expected={'serve':(64,64),'coins':(64,64),'perfect':(64,64),'combo':(64,64),
              'upsell':(64,64),'gulls':(64,64),'walkout':(64,64),'critic':(64,64),
              'tick':(32,32),'broken':(32,32),'board':(200,170),'row':(180,40),
              'row-done':(180,40),'tally':(560,360),'allthree':(120,120)}
    assert set(manifest)=={'goal-'+n for n in expected}
    counts={}
    for meta in (ROOT/'Assets/Art/UI').glob('*.meta'):
        match=re.search(r'^guid: (\w+)',meta.read_text(),re.M)
        if match: counts[match[1]]=counts.get(match[1],0)+1
    settings=['spriteMode: 1','spriteMeshType: 1','textureType: 2',
              'enableMipMap: 0','sRGBTexture: 1','alphaIsTransparency: 1',
              'filterMode: 1','nPOTScale: 0','wrapU: 1','wrapV: 1','wrapW: 1',
              'spritePivot: {x: 0.5, y: 0.5}','spritePixelsToUnits: 100']
    for short,(w,h) in expected.items():
        m=manifest['goal-'+short]; p=ROOT/m['png']; image=Image.open(p)
        assert image.mode=='RGBA' and image.size==(w*2,h*2)
        assert digest(p)==m['sha256'] and counts[m['guid']]==1
        alpha=image.getchannel('A')
        assert alpha.getextrema()==(0,255)
        for edge in [(0,0,w*2,1),(0,h*2-1,w*2,h*2),(0,0,1,h*2),(w*2-1,0,w*2,h*2)]:
            assert not alpha.crop(edge).getbbox(),(short,'edge alpha')
        xml=ET.parse(ROOT/m['svg'])
        assert xml.getroot().attrib['viewBox']==f'0 0 {w} {h}'
        assert not any(e.tag.rsplit('}',1)[-1] in ['text','image','foreignObject'] for e in xml.iter())
        meta=p.with_suffix('.png.meta').read_text()
        assert all(s in meta for s in settings),short
        border=[int(v) for v in re.search(r'spriteBorder: \{x: (\d+), y: (\d+), z: (\d+), w: (\d+)\}',meta).groups()]
        logical={'board':[12,12,12,34],'row':[20,18,20,18],'row-done':[20,18,20,18]}.get(short,[0]*4)
        assert border==[v*2 for v in logical]==m['slice_source_pixels_LBRT']
        assert logical==m['slice_logical_LBRT']
        for key,boxes in m['safe_rects_top_left_logical'].items():
            if isinstance(boxes[0],int): boxes=[boxes]
            for box in boxes:
                if key=='rosette': assert box==[475,-28,120,120]
                else: assert inside(box,w,h),(short,key,box)
        if any(logical):
            assert logical[0]+logical[2]<w and logical[1]+logical[3]<h
    incumbent=json.loads((HERE/'preservation.json').read_text())
    changes=json.loads((HERE/'concurrent-incumbent-changes.json').read_text())
    expected=dict(incumbent)
    for change in changes:
        p=change['path']
        assert p.startswith('Assets/Art/UI/') and p.endswith('.meta') and '/v3-goal-' not in p
        assert incumbent[p]==change['before']
        expected[p]=change['current']
    assert all(digest(ROOT/p)==sha for p,sha in expected.items())
    provenance=json.loads((HERE/'capture-provenance.json').read_text())
    assert len(provenance)==3 and not any(v['fallback'] for v in provenance.values())
    assert all(digest(ROOT/v['frozen'])==v['sha256'] for v in provenance.values())
    visual=json.loads((HERE/'visual-review.json').read_text())
    shipping={m['png'] for m in manifest.values()}
    reviews={str(p.relative_to(ROOT)) for p in (HERE/'review').glob('*.png')}
    all_opened=shipping|reviews|{'docs/screens/ui-v3/art-kit-8.png'}
    assert set(visual['personally_opened_images'])==all_opened
    assert all(digest(ROOT/p)==sha for p,sha in visual['personally_opened_images'].items())
    assert digest(HERE/'review/art-kit-8.png')==digest(ROOT/'docs/screens/ui-v3/art-kit-8.png')
    report={'result':'PASS','shipping_sprites':len(manifest),'guid_unique_in_ui_folder':True,
            'transparent_perimeters':True,'exact_dimensions_and_importers':True,
            'safe_rects_in_bounds_except_documented_rosette_overflow':True,
            'personally_opened_images_current':len(all_opened),
            'incumbent_files_unchanged':len(incumbent)-len(changes),
            'concurrent_unowned_meta_updates':len(changes),'frozen_captures_verified':3,
            'runtime_integration_or_player_acceptance':False}
    (HERE/'delivery-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    main()

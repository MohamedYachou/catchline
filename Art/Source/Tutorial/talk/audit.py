"""Independent delivered-pixel audit; does not import the compositor."""
from pathlib import Path
from PIL import Image, ImageChops
import ast, hashlib, json
H = Path(__file__).resolve().parent
R = H.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
v = json.loads((H/'talk-validation.json').read_text())
inputs = json.loads((H/'source-hashes.json').read_text())
assert len(inputs)==12 and all(sha(R/p)==h for p,h in inputs.items())
opened = json.loads((H/'opened-images.json').read_text())
assert len(opened['images'])==42
assert all(sha(H/x['file'])==x['sha256'] for x in opened['images'])
results=[]
for pose, entry in v['poses'].items():
    source = Image.open(R/entry['source'])
    assert source.mode=='RGBA' and source.size==(1122,1402)
    for state, frame in entry['frames'].items():
        path=H/frame['file']; out=Image.open(path)
        assert out.mode=='RGBA' and out.size==source.size
        difference=ImageChops.difference(source,out)
        union=Image.new('L',source.size)
        for band in difference.split(): union=ImageChops.lighter(union,band)
        binary=union.point(lambda x:255 if x else 0)
        count=binary.histogram()[255]
        assert count==frame['changed_pixel_count'] and list(binary.getbbox())==frame['changed_bounds']
        assert ImageChops.difference(binary,Image.open(H/frame['diff_mask']).convert('L')).getbbox() is None
        outside=binary.copy(); outside.paste(0,tuple(entry['face_box']))
        assert outside.getbbox() is None
        assert ImageChops.difference(source.getchannel('A'),out.getchannel('A')).getbbox() is None
        assert sha(path)==frame['sha256']
        results.append({'file':frame['file'],'changed_pixel_count':count,'outside_face_changed_pixels':0,'exact_diff_mask':True,'alpha_identical':True,'pass':True})
assert len(results)==18 and v['all_pass']
for p in H.glob('*.py'): ast.parse(p.read_text())
report={'task':'MIRA-TALK-ART-1','method':'Independent Pillow per-channel RGBA difference, binary-mask equality, source hash and opened-output hash verification; compositor not imported.','source_hashes_verified':len(inputs),'opened_output_hashes_verified':42,'frames':results,'all_pass':True}
(H/'independent-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'frames':18,'unchanged_inputs':12,'reviewed_outputs':42,'all_pass':True}))

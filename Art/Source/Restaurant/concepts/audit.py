"""Independently decode final concepts and verify provenance, links and receipts."""
from pathlib import Path
from PIL import Image
import ast, hashlib, json, re
R=Path(__file__).resolve().parent
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n: json.loads((R/n).read_text())
write=lambda n,o: (R/n).write_text(json.dumps(o,indent=2)+'\n')
large=['look-options.png','exterior-stages.png','exterior-night.png','interior-1.png','interior-4.png','kit-sheet.png','service-moment.png','contact.png']
phones=['ui-1-arrange.png','ui-2-service.png','ui-3-mira-plan.png','ui-4-prep.png','ui-5-closing.png']
expected={**{n:[2400,1350] for n in large},**{n:[844,390] for n in phones},'ui-service-desktop.png':[1440,900]}
manifest=read('dimensions-and-hashes.json')
opened=read('opened-images.json')['images']
assert set(expected)==set(manifest)==set(opened)
for n,size in expected.items():
    with Image.open(R/n) as im:
        im.load()
        assert im.format=='PNG' and im.mode=='RGB' and list(im.size)==size,n
    assert manifest[n]['size']==size and manifest[n]['sha256']==sha(R/n),n
    assert opened[n]['sha256']==sha(R/n) and opened[n]['individually_opened'] is True,n
prompts=read('generation-prompts.json'); receipts=read('generation-receipts.json')
assert len(prompts)==24 and set(prompts)==set(receipts)
raws=list((R/'generated').glob('*.png')); assert len(raws)==24
raw_hashes={sha(p):p.name for p in raws}
assert len(raw_hashes)==24
source_matches={}
for key,receipt in receipts.items():
    m=re.search(r' as (/[^\n]+?\.png) by default',receipt)
    assert m,key
    original=Path(m.group(1)); assert original.is_file(),key
    h=sha(original); assert h in raw_hashes,key
    source_matches[key]=raw_hashes[h]
assert set(source_matches.values())=={p.name for p in raws}
for p in raws:
    with Image.open(p) as im: im.load(); assert im.format=='PNG'
helpers=list(R.glob('*.py'))
for p in helpers: ast.parse(p.read_text(),filename=str(p))
report=(R/'REPORT.md').read_text()
for n in expected: assert f'### [{n}]({n})' in report,n
for key in prompts: assert f'### `{key}`' in report,key
# Receipt is created after audit so include its link in the later seal pass.
links=re.findall(r'\]\(([^)]+)\)',report)
for link in links:
    if link=='delivery-receipt.json': continue
    assert (R/link).is_file(),link
html=(R/'index.html').read_text()
for link in re.findall(r'(?:href|src)="([^"]+)"',html):
    if not link.startswith(('http:','https:','#')): assert (R/link).is_file(),link
result={'status':'PASS','owner':'Codex 2 (WSL CLI)','final_pngs':14,'raw_pngs':24,'exact_prompts_and_receipts':24,'helper_syntax_checks':len(helpers),'source_matches':source_matches,'checks':['PNG full decode, RGB and independent expected sizes','final hashes match dimension and manual-open receipts','24 original imagegen outputs match 24 project-local raw hashes','all final-sheet reviews and exact prompt sections present','report and existing gallery local links resolve (delivery receipt checked after sealing)','Python helper AST parse'],'limits':['Visual review observations are manual, recorded earlier; this audit does not calculate artistic quality.','No Unity/runtime/touch/economy acceptance.','No browser acceptance of existing index.html.']}
write('independent-audit.json',result)
print(json.dumps({k:result[k] for k in ['status','final_pngs','raw_pngs','exact_prompts_and_receipts','helper_syntax_checks']}))

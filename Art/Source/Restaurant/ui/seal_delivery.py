"""Independently validate the delivered files and seal their current bytes."""
from pathlib import Path
import ast, hashlib, json, re
from datetime import datetime, timezone
from PIL import Image

ROOT=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    audit=json.loads((ROOT/'asset-audit.json').read_text())
    contract=json.loads((ROOT/'expected-assets.json').read_text())
    required={}
    for key,prefix,size in [('icons','v2-icon-',(80,80)),('dishes','v2-dish-',(320,240)),('busts','v2-bust-',(240,280)),('items','v2-item-rest-',(320,240))]:
        for n in contract[key].split():required[prefix+n+'.png']=size
    for n in contract['other'].split():required[n+'.png']=None
    for n in contract['aliases']:required[n+'.png']=(320,240)
    assert len(required)==112
    assert set(required)=={r['file']for r in audit}
    for r in audit:
        f=ROOT/r['file'];im=Image.open(f);im.load()
        assert im.mode=='RGBA' and list(im.size)==r['size'],r['file']
        if required[r['file']]:assert im.size==required[r['file']],r['file']
        assert sha(f)==r['sha256'] and r['opened'],r['file']
        assert im.getchannel('A').getbbox(),r['file']
        if r['file']!='v2-restaurant-backdrop.png':assert im.getchannel('A').getextrema()[0]==0,r['file']
        src=ROOT/'provenance'/r['source'];assert src.is_file(),src
        original=Image.open(src);original.load()
        assert list(original.size)==r['sourceSize'],r['file']
        r['sourceSHA256']=sha(src)
    for target,source in contract['aliases'].items():
        assert (ROOT/(target+'.png')).read_bytes()==(ROOT/(source+'.png')).read_bytes(),target
    delivery=json.loads((ROOT/'delivery-audit.json').read_text())
    assert not delivery['missing'] and not delivery['issues']
    report=(ROOT/'REPORT.md').read_text(encoding='utf-8')
    links=re.findall(r'\]\(([^)]+)\)',report)
    for name in links:assert (ROOT/name).is_file(),name
    for name in ['prepare_assets.py','review_delivery.py','seal_delivery.py']:
        ast.parse((ROOT/name).read_text(encoding='utf-8'))
    contacts=['contact-service.png','contact-dishes.png','contact-arrange.png','contact-frames.png','contact-all.png','contact-slice-proof.png']
    for name in contacts:
        im=Image.open(ROOT/name);im.load();assert im.width>0 and im.height>0
    (ROOT/'asset-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    visual={'spriteCount':112,'individuallyOpened':112,'contactsIndividuallyOpened':contacts,'visualAcceptance':'pending lead/Mo; deviations in REPORT.md','finalSpriteSHA256':{r['file']:r['sha256']for r in audit},'contactSHA256':{n:sha(ROOT/n)for n in contacts}}
    (ROOT/'visual-review.json').write_text(json.dumps(visual,indent=2),encoding='utf-8')
    files={str(f.relative_to(ROOT)).replace('\\','/'):sha(f)for f in sorted(ROOT.rglob('*'))if f.is_file()and f.name!='delivery-receipt.json'and '__pycache__'not in f.parts}
    receipt={'sealedAtUTC':datetime.now(timezone.utc).isoformat(),'status':'source-art technical delivery; visual match/integration pending lead review','checks':{'requiredSprites':112,'individuallyOpenedSprites':112,'openedContacts':6,'missing':0,'dimensionModeAlphaHashIssues':0,'runtimeAliasesByteIdentical':3,'sourceImagesDecoded':112,'reportLinksExist':len(links),'helperASTs':3},'files':files,'limits':['generated reproductions are not pixel-identical copies','backdrop upscaled from1672x941','plank height stretch and ticket pin anchor limits','no Assets, Unity, touch, installed build or Git changes']}
    (ROOT/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    for name,digest in files.items():assert sha(ROOT/name)==digest,name
    print(json.dumps({'result':'PASS','checks':receipt['checks'],'sealedFiles':len(files)}))
if __name__=='__main__':main()

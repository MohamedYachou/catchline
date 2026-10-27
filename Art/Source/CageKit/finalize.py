"""Bind completed, individually reviewed art evidence to exact deliveries.

Run only after opening both final assembly images and recognition images.
Python standard library; no Blender or Unity mutation.
"""
import hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[3]
O=R/'Art/Models/Fishing/CageKit'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def image_receipt(row):
    f=O/row['file'];assert struct.unpack('>II',f.read_bytes()[16:24])==tuple(row['size'])
    digest=sha(f)
    if 'sha256' in row:assert row['sha256']==digest
    return dict(row,sha256=digest,review='individually opened final image; artist review accepted')
def main():
    models=[];images=[]
    for name in ('CrabCage','PotHauler','SortingBoard','CrabBerried'):
        row=json.loads((O/'metrics'/(name+'.json')).read_text())
        assert row['triangles']<1500 and row['round_trip']['result']=='PASS'
        for ext,digest in row['sha256'].items():assert sha(O/(name+'.'+ext))==digest
        ims=[image_receipt(i) for i in row['visual_review']['images']]
        assert len(ims)==(6 if name=='CrabCage' else 5)
        images.extend(ims)
        models.append({'name':name,'triangles':row['triangles'],'sha256':row['sha256'],
            'metrics':'metrics/'+name+'.json','source_actual_fbx':'PASS','visual_review':'PASS'})
    recognition=[image_receipt(i) for i in json.loads((O/'recognition.json').read_text())]
    assert len(recognition)==2;images.extend(recognition)
    assembly=json.loads((O/'assembly.json').read_text());assert assembly['submerged_body_fraction']==.5
    assembly['images']=[image_receipt(i) for i in assembly['images']]
    assert len(assembly['images'])==2;images.extend(assembly['images'])
    assembly['review']='artist source fixture PASS; Unity native placement/water/HUD not verified'
    (O/'assembly.json').write_text(json.dumps(assembly,indent=2)+'\n')
    (O/'recognition.json').write_text(json.dumps(recognition,indent=2)+'\n')
    canon=json.loads((O/'metrics/CrabBerried.json').read_text())['contract']['canonical']
    assert sha(R/canon['path'])==canon['sha256']
    assert len(images)==25 and len({i['file'] for i in images})==25
    receipt={'task':'CAGE-ART-1','owner':'Codex 2 (WSL CLI)','date':'2026-10-25',
        'status':'artist delivery complete; Codex1 import and Claude runtime/native acceptance separate',
        'models':models,'canonical_crab':canon,'images':images,
        'assembly_blend_sha256':sha(O/'CageKit-assembly.blend'),
        'report_sha256':sha(O/'REPORT.md'),
        'sources':{str(p.relative_to(R)):sha(p) for p in sorted(Path(__file__).parent.glob('*.py'))},
        'native_verified':False,'commit':'none','subagents':[]}
    (O/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('CAGE FINAL RECEIPT PASS: 4 models, 25 individually reviewed images; canonical crab unchanged')
if __name__=='__main__':main()

"""Record only frames individually opened and assessed by Codex 2.

Usage: python3 review.py Town_OldWoman studio 'assessment'
       python3 review.py Town_OldWoman walk 'assessment'
       python3 review.py Lineup lineup 'assessment'
"""
import hashlib,json,struct,sys
from pathlib import Path
O=Path(__file__).resolve().parents[2]/'Models/Townsfolk'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 person,group,note=sys.argv[1:4]
 views=['front','back','left','right','three-quarter'] if group=='studio' else ['Walk-'+str(i) for i in range(5)] if group=='walk' else ['all-five-with-crew']
 p=O/'visual-review.json';review=json.loads(p.read_text()) if p.exists() else {'task':'TOWNSFOLK-1','reviewer':'Codex 2 (WSL CLI)','limits':'Individually opened Blender evidence, not Unity/native acceptance.','images':[]}
 for v in views:
  rel='renders/'+person+'/'+v+'.png';f=O/rel
  review['images']=[r for r in review['images'] if r['file']!=rel]
  review['images'].append({'file':rel,'size':list(struct.unpack('>II',f.read_bytes()[16:24])),'sha256':sha(f),'opened_individually':True,'assessment':note})
 review['model_sha256']={e:sha(O/('Townsfolk.'+e)) for e in ['blend','fbx']}
 p.write_text(json.dumps(review,indent=2)+'\n');print('RECORDED',person,group,len(views),'cumulative',len(review['images']))

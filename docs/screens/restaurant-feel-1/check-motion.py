"""Read captured transforms; bounds complement, and do not replace, visual acceptance."""
from pathlib import Path
import re, math, json
root=Path(__file__).resolve().parent
results={}
for folder in sorted(root.glob('*x*/*')):
    frames=sorted(folder.glob('[0-9][0-9][0-9].txt'))
    if not frames:continue
    prev={};max_step=0;min_pair=999;max_backward=0;departures=[];times=[]
    for path in frames:
        text=path.read_text();times.append(float(re.search(r'strip=([\d.]+)',text).group(1)))
        group=re.search(r'group=(\d+)',text).group(1);ids=re.search(r'^group='+group+r'.* guests=([\d,]+)',text,re.M).group(1).split(',')
        current={}
        for match in re.finditer(r'actor=(Guest \d+|Staff \w+) active=(\w+) xyz=([\d.,-]+) forward=([\d.,-]+)',text):
            name,active,xyz,forward=match.groups();p=list(map(float,xyz.split(',')));f=list(map(float,forward.split(',')))
            if active!='True':continue
            current[name]=p
            if name in prev:
                delta=[p[i]-prev[name][i] for i in (0,2)];dist=math.hypot(*delta)
                if name.startswith('Guest '):max_step=max(max_step,dist)
                if dist>.02:max_backward=max(max_backward,-sum(a*b for a,b in zip(delta,f))/dist)
        points=[current['Guest '+i] for i in ids if 'Guest '+i in current]
        if len(points)<len(ids):departures.append(path.stem)
        for i,a in enumerate(points):
            for b in points[i+1:]:min_pair=min(min_pair,math.dist(a,b))
        prev=current
    results[str(folder.relative_to(root))]={'frames':len(frames),'intervalMin':min(round(b-a,3) for a,b in zip(times,times[1:])),'intervalMax':max(round(b-a,3) for a,b in zip(times,times[1:])),'maxGuestStepMetres':round(max_step,4),'targetGroupMinPairMetres':round(min_pair,4),'maxReverseFacingCosineAllActors':round(max_backward,4),'firstMissingGuestFrame':departures[0] if departures else None}
(root/'motion-metrics.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))

# Imports Codex's 1:1 mockup pieces (Art/Source/Restaurant/exact) into Assets/Art/UI as rx-* and generates
# Assets/Scripts/Game/RestaurantExact.cs (piece rects/borders, text styles) from their manifests.
import json, os, shutil, uuid, re, glob
R='/mnt/c/Users/momoy/Projects/Catchline/'
X=R+'Art/Source/Restaurant/exact/'
UI=R+'Assets/Art/UI/'
tmpl=open(UI+'v2-icon-pan.png.meta',newline='').read()
def asset_name(n):
    if n.startswith('v2-bust-') or n.startswith('v2-rbust-'): return n
    return 'rx-'+n[3:] if n.startswith('v2-') else 'rx-'+n
def copy(src,name):
    d=UI+name+'.png'
    shutil.copyfile(src,d+'.tmp'); os.replace(d+'.tmp',d)
    if not os.path.exists(d+'.meta'):
        open(d+'.meta','w',newline='').write(re.sub(r'guid: [0-9a-f]{32}','guid: '+uuid.uuid4().hex,tmpl,count=1))
pieces={}; texts=[]; n=0; layouts={}
S12=('arrange','phone','desktop')
# Both Codex agents cut some pieces under the same name; S3-S5 keep the plain rx- name, S1-S2 duplicates get rx-s12-.
s35=set(os.path.basename(f) for f in glob.glob(X+'s3-s5/v2-*.png'))
for part in ('s3-s5','s1-s2','s1-s2-extra','s6','s7','s8','s9','s10','s11','s12','s13','s14','s15','s1-extras','s2-call','coach-card','s1-card-states','closed-sign'):
    before=set(pieces)
    for f in glob.glob(X+part+'/v2-*.png'):
        b=os.path.basename(f); nm=asset_name(b[:-4])
        if part=='s1-s2' and b in s35: nm='rx-s12-'+nm[3:]
        copy(f,nm); n+=1
    man=X+part+'/manifest.json'
    if os.path.exists(man):
        for p in json.load(open(man)):
            if 'rect' not in p: continue  # S13 manifest lists files only; layout.json carries rects
            pieces[(p['screen'],p['name'])]=(p['rect'],p['size'],p.get('borders'))
    lay=X+part+'/layout.json'
    if os.path.exists(lay):
        for p in json.load(open(lay)).get('repeated_instances',[]):
            pieces.setdefault((p['screen'],p['name']+'#'+p.get('use','')),(p['rect'],None,None))
    ts=X+part+'/text-styles.json'
    if os.path.exists(ts):
        t=json.load(open(ts))
        # S1 extras: {"screen": ..., "styles": [...]} with the screen given once for the sheet.
        if isinstance(t,dict): t=[dict(x,screen=x.get('screen',t.get('screen'))) for x in t.get('styles',[])]
        texts+=t
    if os.path.exists(lay):
        lj=json.load(open(lay))
        # S2 call: {"screens": [{screen, placements}, ...]} for phone and desktop in one sheet.
        if isinstance(lj,dict) and isinstance(lj.get('screens'),list) and lj['screens'] and isinstance(lj['screens'][0],dict): lj={'placements':[dict(p,screen=p.get('screen',sc['screen'])) for sc in lj['screens'] for p in sc.get('placements',[])]}
        for p in lj.get('placements',[]) if isinstance(lj,dict) else []: p.setdefault('screen',lj.get('screen'))
        json_lay=lj
        # Codex 2's S1/S2 sheet places every use as asset#use in layout.json's placements.
        for p in json_lay.get('placements',[]):
            pieces.setdefault((p['screen'],(p.get('asset') or p['name'])+'#'+p.get('use','')),(p['rect'],None,None))
            # Codex 2's refreshed sheet names the cut asset separately; the code keys stay on the placement's own name.
            if p.get('name') and p.get('asset') and p['name']!=p['asset']: pieces.setdefault((p['screen'],p['name']+'#'+p.get('use','')),(p['rect'],None,None))
            # ...and its v2-s12x- assets are the S1/S2 twins of S3-S5 pieces the code names without the prefix.
            if (p.get('asset') or '').startswith('v2-s12x-'): pieces.setdefault((p['screen'],'v2-'+p['asset'][8:]+'#'+p.get('use','')),(p['rect'],None,None))
            if part[1:].isdigit() and int(part[1:])>=6: layouts.setdefault(p['screen'],[]).append((p.get('z',0),(p.get('asset') or p['name'])+'#'+p.get('use','')))
    sl=X+part+'/slices.json'
    if os.path.exists(sl) and isinstance(json.load(open(sl)),list):
        # S6+ sheets: a list of sliced sprites, borders already left,bottom,right,top like the manifests
        for v in json.load(open(sl)):
            for key in list(pieces):
                # (the named sheets like coach-card place on phone/arrange screens: match their own new keys)
                if key[1].split('#')[0]==v['name'] and (str(key[0])==part[1:] or key not in before):
                    r,s_,b=pieces[key]; pieces[key]=(r,v.get('size') or s_,v.get('borders') or b)
    elif os.path.exists(sl) and 'sprites' in json.load(open(sl)):
        pass  # S14 slices are fixed in code (HarbourRestaurantEntry)
    elif os.path.exists(sl):
        for k,v in json.load(open(sl)).items():
            for key in list(pieces):
                # only this sheet's own screens: both sheets cut pieces under some of the same names
                if key[1].split('#')[0]==k and (key[0] in S12)==part.startswith('s1-s2'): r,s,b=pieces[key]; pieces[key]=(r,v['sourceSize'],v['borderLTRB'])
# S11 later stages share the Bistro's layout; their wider text rects come in as screen "11-stage3"/"11-stage4".
for st in ('stage3','stage4'):
    f=X+'s11/later-stages/'+st+'/text-styles.json'
    if os.path.exists(f):
        t=json.load(open(f)); t=t if isinstance(t,list) else t.get('styles',[])
        for x in t: x=dict(x); x['screen']='11-'+st; texts.append(x)
# S6 daytime Arrange entry: its own sheet in s6/arrange-entry.
f=X+'s6/arrange-entry/text-styles.json'
if os.path.exists(f):
    t=json.load(open(f)); texts+=[dict(x,screen=t.get('screen')) for x in t.get('styles',[])]
# S15 event markers: their own sheet in s15/events (pieces only).
for f in glob.glob(X+'s15/events/v2-*.png')+glob.glob(X+'s15/v2-s15-event-*.png'):
    copy(f,asset_name(os.path.basename(f)[:-4])); n+=1
# Codex 1's guest review faces (clothes/guests) keep their v2-guest- names.
for f in glob.glob(R+'Art/Source/Restaurant/clothes/guests/v2-guest-*.png')+glob.glob(R+'Art/Source/Restaurant/clothes/busts/v2-rbust-*.png'):
    copy(f,os.path.basename(f)[:-4]); n+=1
def col(h):
    h=h.lstrip('#'); a=int(h[6:8],16)/255 if len(h)==8 else 1
    return f'C({int(h[0:2],16)/255:.3f}f, {int(h[2:4],16)/255:.3f}f, {int(h[4:6],16)/255:.3f}f, {a:.3f}f)'
L=['// Generated by rx_import.py from Codex\'s RESTAURANT-UI-EXACT-1 manifests; do not edit by hand.',
'// Rects are in the mockup\'s own 844x390 frame (top-left), borders are source px (left, top, right, bottom).',
'using System.Collections.Generic;','using UnityEngine;','','namespace Catchline.Game','{','    static class RestaurantExact','    {',
'        static Color C(float r, float g, float b, float a) => new Color(r, g, b, a);',
'        public static readonly Dictionary<string, (Rect rect, Vector2 size, Vector4 border)> Pieces = new()','        {']
for (scr,name),(r,s,b) in sorted(pieces.items(), key=lambda x:(str(x[0][0]),x[0][1])):
    s=s or [0,0]; b=b or [0,0,0,0]
    L.append(f'            ["{scr}:{name}"] = (new Rect({r[0]}, {r[1]}, {r[2]}, {r[3]}), new Vector2({s[0]}, {s[1]}), new Vector4({b[0]}, {b[1]}, {b[2]}, {b[3]})),')
L+=['        };','','        // S6+ sheets: every placement of a screen in paint order, for RxScreen.',
'        public static readonly Dictionary<int, string[]> Layout = new()','        {']
for scr in sorted(layouts):
    L.append(f'            [{scr}] = new[] {{ '+', '.join(json.dumps(k) for z,k in sorted(layouts[scr],key=lambda x:x[0]))+' },')
L+=['        };','','        public sealed class Style { public Rect Rect; public float Size, Stroke, ShadowY; public Color Fill, StrokeColour, Shadow; public bool Bold; public string Text; public TextAnchor Align = TextAnchor.MiddleCenter; }',
'        public static readonly Dictionary<string, Style> Texts = new()','        {']
for t in texts:
    if 'id' not in t or 'rect' not in t: continue  # Codex 2's S1/S2 sheet has no rects yet
    t.setdefault('stroke_width', t.get('strokeWidth',0))
    sh=t.get('shadow') or [0]+list(t.get('shadow_offset',[0,0]))[1:]+[t.get('shadow_colour','#00000000')]
    L.append(f'            ["{t["screen"]}:{t["id"]}"] = new Style {{ Rect = new Rect({t["rect"][0]}, {t["rect"][1]}, {t["rect"][2]}, {t["rect"][3]}), Size = {t["size"]}f, '
             f'Fill = {col(t["fill"])}, StrokeColour = {col(t.get("stroke","#000000"))}, Stroke = {t.get("stroke_width",0)}f, ShadowY = {sh[1]}f, Shadow = {col(sh[2])}, Bold = {"true" if t.get("weight",700)>=700 else "false"}'
             + (f', Text = {json.dumps(t["text"])}' if isinstance(t.get('text'),str) else '')
             + {'left':', Align = TextAnchor.MiddleLeft','right':', Align = TextAnchor.MiddleRight'}.get(t.get('align'),'') + ' },')
L+=['        };','    }','}','']
out=R+'Assets/Scripts/Game/RestaurantExact.cs'
new=not os.path.exists(out)
open(out,'w',newline='\r\n').write('\n'.join(L))
if new:
    m=open(R+'Assets/Scripts/Game/VoyageRestaurantDay.cs.meta',newline='').read()
    open(out+'.meta','w',newline='').write(re.sub(r'guid: [0-9a-f]{32}','guid: '+uuid.uuid4().hex,m,count=1))
print('pngs',n,'pieces',len(pieces),'texts',len(texts))
# Codex padded these canvases with transparent margins; trim so nine-slicing hits the real edge.
import subprocess
TRIM=['rx-paper-row','rx-summary-strip','rx-closing-header','rx-metric-row','rx-progress-track','rx-progress-fill']
subprocess.run(['cmd.exe','/c','python',r'C:\Users\momoy\AppData\Local\Temp\cl-rxtrim.py']+[r'C:\Users\momoy\Projects\Catchline\Assets\Art\UI'+'\\'+t+'.png' for t in TRIM])

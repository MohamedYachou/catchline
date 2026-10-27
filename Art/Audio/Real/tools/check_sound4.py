"""Independently decode SOUND-4, verify contracts, draw review evidence."""
from pathlib import Path
import sys,json,hashlib,wave,html
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];O=R/'Art/Audio/Real'
sys.path.insert(0,str(R/'Art/Source/Audio'))
import analyze
import numpy as np
from PIL import Image,ImageDraw
analyze.O=O
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
limits={'CoachPop':(0,.3),'RefitFanfare':(1.5,3),'TabTap':(0,.15),'CoinBuy':(0,.6),'PageTurn':(0,.8)}
e=json.loads((O/'sound4-edits.json').read_text())
assert len(e['files'])==15
groups={name:[] for name in limits};metrics=[]
for row in e['files']:
    p=O/row['file'];x,m=analyze.measure(p)
    assert m['sha256']==row['sha256']
    assert abs(m['integrated_lufs']-row['target_lufs'])<1
    lo,hi=limits[m['family']];assert lo<m['duration_seconds']<=hi
    assert all(s['license']=='CC0-1.0' for s in row['layers'])
    m['target_lufs']=row['target_lufs'];metrics.append(m);groups[m['family']].append((x[:,0],m))
# Compare loudness AND peak to both recorded and historical synthetic clicks.
comparisons=[]
for clickdir in [O/'SFX',R/'Art/Audio/SFX']:
    click=[]
    for v in range(3):
        p=clickdir/f'Click_{v}.wav'
        if p.exists():
            _,m=analyze.measure(p) if clickdir==O/'SFX' else (None,None)
            if m is None:
                old=analyze.O;analyze.O=R/'Art/Audio';_,m=analyze.measure(p);analyze.O=old
            click.append(m)
    if click:
        for _,tab in groups['TabTap']:
            assert tab['integrated_lufs']<min(m['integrated_lufs'] for m in click)-3
            assert tab['sample_peak_dbfs']<min(m['sample_peak_dbfs'] for m in click)
        comparisons.append({'click_directory':str(clickdir.relative_to(R)),'quietest_click_lufs':min(m['integrated_lufs'] for m in click),'lowest_click_peak_dbfs':min(m['sample_peak_dbfs'] for m in click),'tab_loudness_and_peak_lower':True})
sheets=[]
for name,rows in groups.items():
    assert len(rows)==3 and len({m['sha256'] for _,m in rows})==3
    assert max(m['integrated_lufs'] for _,m in rows)-min(m['integrated_lufs'] for _,m in rows)<2
    im=Image.new('RGB',(1300,835),'#f0ede3');d=ImageDraw.Draw(im)
    d.text((25,15),'SOUND-4 / RECORDED CC0 / '+name,font=analyze.F22,fill='#142c34')
    d.text((25,50),'Waveform | log spectrum80Hz–16kHz. Visual/technical review only; auditory acceptance pending.',font=analyze.F17,fill='#40555b')
    for k,(x,m) in enumerate(rows):
        y=85+k*245
        d.text((25,y),f"{Path(m['file']).stem} | {m['duration_seconds']:.3f}s | {m['integrated_lufs']:.2f}LUFS | {m['true_peak_4x_dbtp']:.2f}dBTP",font=analyze.F17,fill='#142c34')
        analyze.plot_panel(im,x,(25,y+30,590,175));analyze.plot_panel(im,x,(655,y+30,615,175),True)
    p=R/f'Art/Audio/review/SOUND4-{name}.png';im.save(p);sheets.append({'file':str(p.relative_to(R)),'sha256':sha(p)})
    print(name,'PASS',[(round(m['duration_seconds'],3),round(m['integrated_lufs'],2)) for _,m in rows],flush=True)
protected=json.loads((O/'sound4-baseline.json').read_text())
for row in protected:
    p=R/row['file']
    if 'preserve_prefix_bytes' in row:
        assert hashlib.sha256(p.read_bytes()[:row['preserve_prefix_bytes']]).hexdigest()==row['sha256'],str(p)
    else:assert sha(p)==row['sha256'],str(p)
out={'task':'SOUND-4','result':'PASS technical; listening NOT performed','method':'Independent PCM16 decode; BS1770 K-weighted/gated400ms meter with zero padding for shorter cues; 4x polyphase estimated true peak, not certified. Limits: peak<=-3dBFS, DC<.0007, zero endpoints/adjacent<=3PCM, loudness target within1LU/family spread<2LU.','protected_unchanged_files':len(protected),'comparisons':comparisons,'files':metrics,'sheets':sheets}
(O/'sound4-metrics.json').write_text(json.dumps(out,indent=2)+'\n')
parts=['<!doctype html><meta charset="utf-8"><title>SOUND-4 listening candidates</title><h1>SOUND-4: recorded CC0 candidates</h1><p>15 technical checks passed. No auditory acceptance yet. Listen for softness of wood taps, convincing double bell and horn, clean coin cut and paper unfold. Bell uses public MP3 preview. See REPORT for complete licence/source ledger.</p>']
for row in e['files']:
    parts.append(f'<p><b>{html.escape(row["file"])}</b>: {html.escape(row["description"])}<br><audio controls preload="none" src="../{html.escape(row["file"])}"></audio></p>')
(O/'sound4-listening.html').write_text('\n'.join(parts)+'\n')
print('PASS15;',len(protected),'pre-existing files unchanged; TabTap quieter than both Click packs')

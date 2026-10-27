"""Independent PCM decode/analysis of SOUND-3; no source audio generation."""
from pathlib import Path
import json,sys,hashlib
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw
import analyze
O=Path(__file__).resolve().parents[3]/'Art/Audio/Real'
analyze.O=O
def run():
    edits=json.loads((O/'edits.json').read_text());files=[];sheets=[]
    groups={}
    for e in edits['files']:groups.setdefault(Path(e['file']).stem.rsplit('_',1)[0],[]).append(e)
    (O/'review').mkdir(exist_ok=True)
    for family,items in groups.items():
        rows=[];series=[]
        for e in items:
            p=O/e['file'];x,m=analyze.measure(p)
            assert m['sha256']==e['sha256'];m['target_lufs']=e['target_lufs']
            m['target_error_lu']=m['integrated_lufs']-e['target_lufs']
            assert abs(m['target_error_lu'])<1.0,(p,m['target_error_lu'])
            files.append(m);rows.append(m)
            for c in range(x.shape[1]):series.append((p.stem+(' LR'[c+1] if x.shape[1]==2 else ''),x[:,c],m))
        if len(items)==3:
            assert len(set(r['sha256'] for r in rows))==3
            assert max(r['integrated_lufs'] for r in rows)-min(r['integrated_lufs'] for r in rows)<2
        # Plotting is documentary analysis, not UI/game artwork.
        h=100+len(series)*230
        im=Image.new('RGB',(1300,h),'#f0ede3');d=ImageDraw.Draw(im)
        d.text((24,16),'SOUND-3 / REAL RECORDINGS / '+family,font=analyze.F22,fill='#142c34')
        d.text((24,50),'PCM waveform, full scale                       Log spectrogram: 80Hz–16kHz, -100 to -15dBFS',font=analyze.F17,fill='#40555b')
        for k,(label,x,m) in enumerate(series):
            y=85+k*230
            d.text((24,y),f"{label} | {m['duration_seconds']:.3f}s | {m['integrated_lufs']:.1f} LUFS | {m['sample_peak_dbfs']:.1f} dBFS",font=analyze.F17,fill='#142c34')
            analyze.plot_panel(im,x,(25,y+27,590,165));analyze.plot_panel(im,x,(655,y+27,615,165),True)
        p=O/'review'/f'{family}.png';im.save(p)
        sheets.append({'file':str(p.relative_to(O)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'audio_files':[r['file'] for r in rows]})
        print(family,'PASS',flush=True)
    stress={}
    for hz in [8,12]:
        y=np.zeros(2*44100)
        for k,at in enumerate(np.arange(0,1.5,1/hz)):
            x,_,_=analyze.decode(O/f'SFX/Winch_{k%3}.wav');i=round(at*44100);n=min(len(x),len(y)-i);y[i:i+n]+=x[:n,0]
        stress[str(hz)+'Hz']={'gain065_sum_peak_dbfs':analyze.db(np.max(abs(y))*.65)}
    assert all(v['gain065_sum_peak_dbfs']<-3 for v in stress.values()),stress
    metrics={'result':'PASS (technical checks only; listening and native mix pending)','method':'Independent PCM16 WAV decode, BS1770 K weighted gated loudness, short clips zero-padded to400ms; scipy4x truepeak estimate. Same measurement helper as SOUND1. Quantized endpoints, seam value/slope and live seam RMS checked.','files':files,'sheets':sheets,'winch_overlap':stress,'missing_families':edits['missing_families']}
    (O/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print('SOUND3 PASS',len(files),'WAVs',len(sheets),'sheets',stress,flush=True)
if __name__=='__main__':run()

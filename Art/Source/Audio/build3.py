"""SOUND-3: edit scanned CC0 recordings only. Never calls a sound generator.

All source segments and processing are recorded in Real/edits.json. Imports
only measurement/gain/fade helpers from the existing DSP module.
"""
from pathlib import Path
import sys, json, subprocess, hashlib
sys.dont_write_bytecode = True
import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter1d, gaussian_filter1d
from scipy.io import wavfile
from dsp import FS, edge, master

R = Path(__file__).resolve().parents[3]
O = R/'Art/Audio/Real'
D = R/'Art/Audio/Downloads'
INDEX = json.loads((O/'sources/index.json').read_text())
CACHE = {}
ROWS = []
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def src(slug, name): return D/('oga-'+slug)/name
def hundred(name): return src('100-cc0-sfx', 'extracted/'+name+'.ogg')
def cloth(v): return src('202-more-sound-effects',f'extracted/Cloth/Cloth_{v+1:02d}.wav')
def receipt(p):
    for r in INDEX:
        original = R/r['local']
        if p == original or original.suffix == '.zip' and p.is_relative_to(original.parent/'extracted'):
            assert r['clean'] and r['scan_returncode'] == 0 and sha(original) == r['sha256']
            return r
    raise ValueError('Unscanned source '+str(p))
def read(p):
    if p not in CACHE:
        receipt(p)
        # Decode only after the receipt/hash gate. Retain real source stereo.
        b = subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar',str(FS),'-ac','2','pipe:1'])
        CACHE[p] = np.frombuffer(b,dtype='<f4').astype(float).reshape(-1,2)
    return CACHE[p]
def take(p, dur=None, part=0, cut=8000):
    x=read(p).mean(axis=1)
    # Keep the whole event when possible; for montages select an energetic
    # window from the specified third, with 15ms attack preroll.
    start=0; end=len(x)
    if dur is not None and len(x)>round(dur*FS):
        lo=round(part*len(x)/3); hi=round((part+1)*len(x)/3) if part else len(x)
        peak=lo+int(np.argmax(abs(x[lo:hi])))
        start=max(0,min(peak-round(.015*FS),len(x)-round(dur*FS)))
        end=start+round(dur*FS)
    else:
        active=np.flatnonzero(abs(x)>max(abs(x).max()*.008,1e-7))
        if len(active):start=max(0,int(active[0]) - round(.012*FS));end=min(len(x),int(active[-1])+round(.06*FS))
    x=x[start:end]
    x=signal.sosfilt(signal.butter(2,[45,cut],btype='bandpass',fs=FS,output='sos'),x)
    x=edge(x-x.mean(),9)
    r=receipt(p)
    meta={'source':str(p.relative_to(R)), 'source_sha256':sha(p), 'receipt':str((O/'sources'/f"{r['source_page'].rsplit('/',1)[1]}--{r['original_filename']}.scan.json").relative_to(O)),
          'start_seconds':start/FS,'end_seconds':end/FS,'highpass_hz':45,'lowpass_hz':cut,'edge_fade_ms':9}
    return x,meta
def layer(parts):
    n=max(round(at*FS)+len(x) for x,m,at,g in parts)
    y=np.zeros(n); metadata=[]
    for x,m,at,g in parts:
        i=round(at*FS); scale=g/max(np.sqrt(np.mean(x*x)),1e-9)
        y[i:i+len(x)]+=x*scale
        metadata.append(dict(m,end_seconds=m['start_seconds']+len(x)/FS,used_frames=len(x),at_seconds=at,relative_rms_gain=g))
    return edge(y-y.mean(),9),metadata
def write(name,x,meta,target,note):
    crest_passes=0
    if x.ndim==1:
        x=edge(x,9)
        w=edge(np.ones(len(x)),9)
        x-=w*x.sum()/w.sum()
        # Gain-only transient control before normalising recorded impacts.
        # A5ms lookahead envelope/1ms smoothing avoids clipping sharp takes.
        # No generated excitation, saturation, pitch change or replacement.
        for _ in range(12):
            from dsp import loudness
            current,_=loudness(x)
            candidate=x*10**((target-current)/20)
            ceiling=10**(-3.8/20)
            if np.max(abs(signal.resample_poly(candidate,4,1)))<=ceiling:break
            envelope=maximum_filter1d(abs(candidate),size=221,mode='nearest')
            gain=gaussian_filter1d(np.minimum(1,ceiling/np.maximum(envelope,1e-12)),44)
            x=candidate*gain
            x-=w*x.sum()/w.sum()
            crest_passes+=1
    x=master(x,target)
    if x.ndim==1:pass
    else:
        # A 100ms equal-power-free overlap is already applied below. Join
        # values/slopes additionally converge over 2ms, retaining live RMS.
        m=round(.002*FS);u=np.linspace(0,1,m);s=u*u*(3-2*u)
        midpoint=(x[0]+x[-1])/2
        x[:m]=midpoint*(1-s[:,None])+x[m-1]*s[:,None]
        x[-m:]=x[-m]*(1-s[:,None])+midpoint*s[:,None]
        x[:2]=midpoint;x[-2:]=midpoint
        x-=x.mean(axis=0)
    p=O/(('Ambience/' if x.ndim==2 else 'SFX/')+name+'.wav')
    p.parent.mkdir(parents=True,exist_ok=True)
    wavfile.write(p,FS,np.rint(x*32767).astype('<i2'))
    ROWS.append({'file':str(p.relative_to(O)),'sha256':sha(p),'target_lufs':target,'description':note,'transient_gain_control_passes':crest_passes,'layers':meta})
def run():
    animal=src('baby-animals-sounds-pack','extracted')
    spokes=src('bicycle-sounds','extracted/bicycle_spokes-1.wav')
    creak=src('tree-creaking','tree_creak.flac')
    coin=src('coin-sounds','coinsounds011015.wav')
    wavepaths=[src('water-splash-and-sand-footsteps',f'splash{k}_0.wav') for k in [1,2]]+[hundred('splash_01')]
    for v in range(3):
        water,wm=take(wavepaths[v],.72,cut=6500)
        wood,wom=take(hundred(f'wooden_{v+1:02d}'),.32,cut=4200)
        fabric,fm=take(cloth(v),.40,cut=6500)
        cr,cm=take(creak,.65,part=v,cut=4200)
        coins,com=take(coin,.70,part=v,cut=7200)
        click,clm=take(hundred('switch_01' if v!=1 else 'switch_02'),.10,part=v,cut=4500)
        def emit(n,parts,note,target=-24):
            y,m=layer(parts);write(f'{n}_{v}',y,m,target+(v-1)*.2,note)
        air,am=take(src('swishes-sound-pack',f'extracted/swishes/swish-{v+1}.wav'),cut=9000)
        emit('Cast',[(air,am,0,1)],'Recorded stick/hanger swish, rod casting foley.')
        emit('Splash',[(water,wm,0,1)],'Actual water impact recording.')
        emit('Bite',[(wood[:round(.16*FS)],wom,0,.7),(water[:round(.20*FS)],wm,.025,.35)],'Wood touch and bucket-water contact, float-bite foley.')
        reel,rm=take(spokes,.70,part=v,cut=6500)
        emit('Reel',[(reel,rm,0,1)],'Real bicycle-spoke rattle used as reel ratchet foley.')
        emit('Land',[(wood,wom,0,.65),(water[:round(.47*FS)],wm,.035,1)],'Recorded wood and water: fish landing foley.')
        emit('Stow',[(wood,wom,0,1),(fabric,fm,.03,.4)],'Recorded wood contact with cloth movement, crate stow foley.')
        emit('Moor',[(wood,wom,0,.75),(cr,cm,.04,.5)],'Recorded wood contact and tree creak, mooring foley.')
        paper,pm=take(hundred(f'paper_{v+1:02d}'),.40,cut=6500)
        emit('Sale',[(paper,pm,0,.35),(coins,com,.07,1)],'Recorded paper and real coin handling.')
        emit('Select',[(click,clm,0,1)],'Damped recorded physical switch contact.',-32)
        shortcoin,scm=take(coin,.12,part=v,cut=5000)
        emit('Purchase',[(shortcoin,scm,0,1)],'Quiet real coin touch; no tonal reward.',-32)
        emit('Click',[(click,clm,0,1)],'Short recorded switch touch.',-32.6)
        bell,bm=take(hundred(f'bell_{v+1:02d}'),cut=8500)
        emit('Bell',[(bell,bm,0,1)],'Recorded household bell; buoy-bell foley, not an actual buoy.',-27)
        emit('Creak',[(cr,cm,0,1)],'Recorded tree/wood creak.')
        win,winm=take(spokes,.39,part=v,cut=5000)
        emit('Winch',[(win,winm,0,1)],'Recorded bicycle-spoke ratchet; short hauler foley.')
        clack,clkm=take(hundred(f'metal_{v+1:02d}'),.26,cut=6500)
        emit('CrabClack',[(clack,clkm,0,1)],'Small recorded metal contact used as shell/claw foley; not a crab vocalization.')
        emit('NetSlap',[(fabric,fm,0,.45),(water,wm,.025,1)],'Recorded cloth and bucket water, wet net impact foley.')
        gut,gm=take(src('cut-peel-a-pumpkin',f'cut_pumpkin_0{v+1}.ogg'),.65,cut=6000)
        emit('Gut',[(gut,gm,0,1)],'Actual knife cutting pumpkin, wet cutting foley.')
        emit('Coins',[(coins,com,0,1)],'Actual coins recorded by syncopika.')
        for n,orig in [('DogBark','Bark.ogg'),('Meow','Meow.ogg')]:
            a,mm=take(animal/orig,cut=7500-v*350)
            emit(n,[(a,mm,0,1)],'Real juvenile animal call; three subtle EQ/gain edits of ONE source take, not three distinct calls.',-27)
        stitch,sm=take(cloth(v),.20,cut=6000)
        emit('Stitch',[(stitch,sm,0,1)],'Recorded cloth pull, net-mending foley; not a literal needle recording.',-29)
        pot,pom=take(hundred(f'pot_0{v%2+1}'),.25,cut=3500)
        emit('PotDrop',[(pot,pom,0,.65),(fabric[:round(.2*FS)],fm,.04,.22),(water,wm,.16,1)],'Recorded pot contact, cloth and water: pot-over-rail foley.',-25)
    river=src('sea-and-river-wave-sounds','VistulaShort_0.mp3')
    # Five disjoint genuine field-recording excerpts, with short coastal surf
    # takes overlapped at irregular intervals for the exposed locations.
    for k,name in enumerate(['HarbourDay','HarbourDusk','OpenSea','Skerries','LighthouseRock']):
        start=[12,69,126,183,240][k];pad=round(.10*FS);n=30*FS
        y=read(river)[start*FS:start*FS+n+pad].copy()
        meta=[{'source':str(river.relative_to(R)),'source_sha256':sha(river),'start_seconds':start,'end_seconds':start+30.1,'role':'continuous stereo water bed (Vistula river, not location-authentic sea)'}]
        if k>=2:
            y*=.4
            for j,at in enumerate([0,2.7,6.1,9.5,13.0,16.6,20.0,23.4,26.9,29.2]):
                p=src('beach-ocean-waves',f'wave_0{(j+k)%4+1}_cc0-18363__jasinski__alkaibeach.flac')
                a=edge(read(p),180);i=round(at*FS)
                # Wrap source events around the loop; no generated noise.
                for c in range(2):np.add.at(y[:,c],(i+np.arange(len(a)))%n,a[:,c]*.55)
                meta.append({'source':str(p.relative_to(R)),'source_sha256':sha(p),'start_seconds':0,'end_seconds':len(a)/FS,'at_seconds':at,'gain':.55,'fade_ms':180})
        y=signal.sosfilt(signal.butter(2,[35,4000 if k==1 else 8000],btype='bandpass',fs=FS,output='sos'),y,axis=0)
        # Last extra100ms crossfades into the start; derivative-controlled
        # 2ms endpoint correction in write(). No fade-to-silence at join.
        u=np.linspace(0,1,pad);w=(.5-.5*np.cos(np.pi*u))[:,None]
        y[:pad]=y[n:n+pad]*(1-w)+y[:pad]*w;y=y[:n];y-=y.mean(axis=0)
        write(name,y,meta,-30 if k==1 else -28,'Real stereo river-wave bed'+(' with recorded Alki beach surf.' if k>=2 else '.')+' No added animal calls/horn/wind; location ambience candidate, not an authentic field recording at the named game location.')
    (O/'edits.json').write_text(json.dumps({'task':'SOUND-3','method':'Only scanned recordings: trims, bandpass EQ, fades, transient gain control, normalization and layering. No synthesis, saturation, pitch shift or generated noise. Exact layers and source hashes below.','processing':{'one_shots': {'highpass_hz': 45, 'lowpass_hz': 'per source layer', 'initial_edge_fades_ms': 9, 'layer_and_final_edge_fades_ms': 9, 'dc_correction': 'edge-weighted, preserving zero endpoints', 'transient_envelope_ms': 5, 'transient_gain_smoothing_ms': 1, 'transient_ceiling_dbfs': -3.8, 'transient_iterations_max': 12, 'final_peak_cap_dbtp': -3.4}, 'ambience': {'highpass_hz': 35, 'lowpass_hz': 8000, 'HarbourDusk_lowpass_hz': 4000, 'crossfade_ms': 100, 'endpoint_smoothstep_ms': 2, 'live_endpoints': True, 'underlying_river_gain': {'HarbourDay': 1, 'HarbourDusk': 1, 'OpenSea': 0.4, 'Skerries': 0.4, 'LighthouseRock': 0.4}}, 'mastering': 'gain normalization with existing dsp.master; PCM16 rounded after scaling32767'},'files':ROWS,'missing_families':['Gull','SealBark','Puffin','Horn','Foghorn']},indent=2)+'\n')
    print('BUILT',len(ROWS),'recording-derived WAVs',flush=True)
if __name__=='__main__':run()

"""Decode delivered WAVs, measure contracts, plot each file. Pillow only draws analysis."""
from pathlib import Path
import sys,wave,json,hashlib
sys.dont_write_bytecode=True
import numpy as np
from scipy import signal
from PIL import Image,ImageDraw,ImageFont
from dsp import FS,loudness,db,RECIPES,AMBIENCE_RECIPES,UI
R=Path(__file__).resolve().parents[3];O=R/'Art/Audio'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(FONT,n)
F14=font(14);F17=font(17);F22=font(22)
def decode(p):
    with wave.open(str(p),'rb') as w:
        assert w.getframerate()==44100 and w.getsampwidth()==2 and w.getcomptype()=='NONE',p
        channels=w.getnchannels();frames=w.getnframes();raw=w.readframes(frames)
    return np.frombuffer(raw,dtype='<i2').reshape(-1,channels)/32768.,channels,frames

def measure(p):
    x,c,n=decode(p);loop=p.parent.name=='Ambience';family=p.stem if loop else p.stem.rsplit('_',1)[0]
    assert c==(2 if loop else 1)
    if loop:assert n==30*FS
    if family in UI:assert n/FS<.150
    if family=='Winch':assert .35<=n/FS<=.45
    peak=db(np.max(np.abs(x)));true=db(np.max(np.abs(signal.resample_poly(x,4,1,axis=0))))
    assert peak<=-3 and true<=-3,p
    lufs,pad=loudness(x);dc=x.mean(axis=0)
    assert np.max(np.abs(dc))<.0007,(p,dc)
    seam=None
    if loop:
        delta=x[0]-x[-1];diff=np.diff(x,axis=0);p99=np.quantile(np.abs(diff),.99,axis=0)
        ds=(x[1]-x[0])-(x[-1]-x[-2])
        win=round(.020*FS);wrap=np.r_[x[-win:],x[:win]]
        # Compare energy in the join with the bed: no fade-to-silence.
        rms=np.sqrt(np.mean(wrap*wrap,axis=0));whole=np.sqrt(np.mean(x*x,axis=0))
        assert np.max(np.abs(delta))<=1/32768 and np.all(np.abs(ds)<=1/32768),(p,delta,ds,p99)
        assert np.all(rms/whole>.05),(p,'silent seam')
        seam={'value_step_linear':delta.tolist(),'value_step_dbfs':[db(abs(v)) for v in delta],'slope_step_linear':ds.tolist(),'interior_difference_p99':p99.tolist(),'join20ms_rms_dbfs':[db(v) for v in rms],'join_to_whole_rms_ratio':(rms/whole).tolist()}
    else:
        assert np.max(np.abs(x[[0,-1]]))==0,(p,'nonzero endpoint')
        # Endpoint sample/first derivative must be near PCM silence.
        assert np.max(np.abs(x[[1,-2]]))<=3/32768,(p,'abrupt endpoint')
    return x,{'file':p.relative_to(O).as_posix(),'family':family,'sample_rate_hz':FS,'bit_depth':16,'channels':c,'frames':n,'duration_seconds':n/FS,'sample_peak_dbfs':peak,'true_peak_4x_dbtp':true,'integrated_lufs':lufs,'measurement_zero_padding_seconds':pad,'dc_offset_linear':dc.tolist(),'rms_dbfs':[db(v) for v in np.sqrt(np.mean(x*x,axis=0))],'first_last_pcm':np.rint(x[[0,-1]]*32768).astype(int).tolist(),'loop_seam':seam,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def plot_panel(im,x,box,spectrum=False):
    d=ImageDraw.Draw(im);left,top,width,height=box
    d.rectangle((left,top,left+width,top+height),fill='#142c34')
    if spectrum:
        f,t,z=signal.spectrogram(x,FS,nperseg=512,noverlap=384,mode='magnitude',scaling='spectrum')
        z=20*np.log10(np.maximum(z,1e-8))
        # Log-frequency display,80Hz-16kHz, absolute calibrated dBFS palette.
        freqs=np.geomspace(16000,80,height);vals=np.empty((height,z.shape[1]))
        for i,fr in enumerate(freqs):
            k=np.searchsorted(f,fr);k=min(max(1,k),len(f)-1);u=(fr-f[k-1])/(f[k]-f[k-1]);vals[i]=(1-u)*z[k-1]+u*z[k]
        v=np.clip((vals+100)/85,0,1)
        stops=np.array([[10,25,35],[20,83,99],[40,151,151],[224,178,96],[255,237,202]])
        q=v*4;a=np.minimum(q.astype(int),3);w=q-a;rgb=(stops[a]*(1-w[...,None])+stops[a+1]*w[...,None]).astype('uint8')
        panel=Image.fromarray(rgb).resize((width,height),Image.Resampling.BILINEAR);im.paste(panel,(left,top))
        for freq in [100,1000,10000]:
            yy=top+int(np.log(16000/freq)/np.log(16000/80)*(height-1));d.line((left,yy,left+width,yy),fill='#567279',width=1);d.text((left+4,yy-14),f'{freq} Hz',font=F14,fill='white')
    else:
        center=top+height//2;scale=height*.44
        for amp in [-.5,0,.5]:
            yy=center-int(amp*scale);d.line((left,yy,left+width,yy),fill='#35505a');d.text((left+4,yy+2),str(amp),font=F14,fill='#7b969c')
        bounds=np.linspace(0,len(x),width+1,dtype=int)
        for i in range(width):
            segment=x[bounds[i]:max(bounds[i]+1,bounds[i+1])]
            if len(segment):d.line((left+i,center-float(segment.max())*scale,left+i,center-float(segment.min())*scale),fill='#e4b064')
    for j in range(5):
        px=left+j*width//4;d.text((min(px,left+width-55),top+height+4),f'{j*len(x)/FS/4:.2f}s',font=F14,fill='#445e63')

def sheet(name,series,rows,loop=False):
    # One waveform and one spectrogram per variant, or per stereo channel.
    count=len(series);height=100+count*245+58
    im=Image.new('RGB',(1300,height),'#f0ede3');d=ImageDraw.Draw(im)
    d.text((30,18),f'SOUND-1  /  {name}',font=F22,fill='#142c34')
    d.text((30,51),'Waveform (linear full scale)                                   Spectrogram (80 Hz-16 kHz, -100 to -15 dBFS)',font=F17,fill='#40555b')
    for k,(label,x,row) in enumerate(series):
        y=92+k*245
        d.text((30,y),f'{label}  |  {row["duration_seconds"]:.3f}s  |  {row["integrated_lufs"]:.1f} LUFS  |  peak {row["sample_peak_dbfs"]:.1f} dBFS / {row["true_peak_4x_dbtp"]:.1f} dBTP',font=F17,fill='#142c34')
        plot_panel(im,x,(30,y+30,590,175));plot_panel(im,x,(655,y+30,615,175),True)
    note='30s stereo; join has equal endpoint values, derivative and live-bed RMS checked.' if loop else 'Independent PCM16 decode; zero endpoints. Short files use 400ms zero-padded LUFS measurement.'
    d.text((30,height-36),note,font=F14,fill='#40555b')
    p=O/f'review/{name}.png';im.save(p)
    return {'file':p.relative_to(O).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'audio_files':[r['file'] for r in rows]}

def run():
    files=[];sheets=[];family_spread={}
    for name in RECIPES:
        series=[];rows=[]
        for v in range(3):
            x,row=measure(O/f'SFX/{name}_{v}.wav');files.append(row);rows.append(row);series.append((f'{name}_{v}',x[:,0],row))
        assert len({r['sha256'] for r in rows})==3
        spread=max(r['integrated_lufs'] for r in rows)-min(r['integrated_lufs'] for r in rows);assert spread<2,(name,spread)
        family_spread[name]=spread;sheets.append(sheet(name,series,rows));print(name,'analyzed',flush=True)
    for name in AMBIENCE_RECIPES:
        x,row=measure(O/f'Ambience/{name}.wav');files.append(row)
        assert abs(float(np.corrcoef(x.T)[0,1]))<.98,(name,'not stereo')
        row['stereo_correlation']=float(np.corrcoef(x.T)[0,1])
        series=[(f'{name} / '+('left' if c==0 else 'right'),x[:,c],row) for c in range(2)]
        join=np.r_[x[-round(.020*FS):],x[:round(.020*FS)]]
        zoom=dict(row);zoom['duration_seconds']=len(join)/FS
        series.append((name+' / seam +/-20ms (L+R mean)',join.mean(axis=1),zoom))
        sheets.append(sheet(name,series,[row],True));print(name,'analyzed',flush=True)
    # Stress test rapidly repeated winch taps; this is an offline sum, not native playback.
    stress={}
    for hz in [8,12]:
        y=np.zeros(2*FS)
        for k,at in enumerate(np.arange(0,1.5,1/hz)):
            x,_,_=decode(O/f'SFX/Winch_{k%3}.wav');i=round(at*FS);n=min(len(x),len(y)-i);y[i:i+n]+=x[:n,0]
        stress[str(hz)+'Hz']={'unity_gain1_sum_peak_dbfs':db(np.max(abs(y))),'gain035_sum_peak_dbfs':db(np.max(abs(y))*.35),'gain065_sum_peak_dbfs':db(np.max(abs(y))*.65)}
    assert all(v['gain065_sum_peak_dbfs']<-3 for v in stress.values()),stress
    metrics={'result':'PASS','method':'BS.1770 K-weighting and400ms/100ms gating; clips shorter400ms zero-padded toone400msblock, padding explicitly recorded. Peak includes scipy4xpolyphase estimate; not a certified hardware true-peak meter.','files':files,'family_lufs_spread':family_spread,'winch_overlap':stress,'sheets':sheets}
    (O/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print('SOUND ANALYSIS PASS',len(files),'WAV',len(sheets),'sheets',json.dumps(stress),flush=True)
if __name__=='__main__':run()

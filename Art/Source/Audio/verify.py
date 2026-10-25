"""Independent delivery inventory/PCM readback plus known-tone meter calibration."""
from pathlib import Path
import sys,json,wave,hashlib,platform
sys.dont_write_bytecode=True
import numpy as np
import scipy
from dsp import FS,loudness
R=Path(__file__).resolve().parents[3];O=R/'Art/Audio'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((O/'metrics.json').read_text());syn=json.loads((O/'synthesis.json').read_text());assert m['result']=='PASS'
expected={f'SFX/{n}_{v}.wav' for n in ['Cast','Splash','Bite','Reel','Land','Stow','Moor','Sale','Select','Purchase','Gull','Bell','Creak','Horn','Click','Winch','CrabClack','SealBark','NetSlap','Gut','Coins'] for v in range(3)}|{f'Ambience/{n}.wav' for n in ['HarbourDay','OpenSea','Skerries']}
assert len(expected)==66 and {p.relative_to(O).as_posix() for p in O.rglob('*.wav')}==expected
assert {r['file'] for r in syn['files']}==expected=={r['file'] for r in m['files']}
byfile={r['file']:r for r in syn['files']};result=[]
for row in m['files']:
    p=O/row['file'];h=sha(p);assert h==row['sha256']==byfile[row['file']]['sha256']
    with wave.open(str(p),'rb') as w:
        assert w.getnchannels()==row['channels'] and w.getframerate()==FS and w.getsampwidth()==2 and w.getnframes()==row['frames']
        pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,w.getnchannels())
    assert not np.any(np.abs(pcm.astype('int32'))>=32767)
    if row['loop_seam']:
        assert np.array_equal(pcm[0],pcm[-1]) and np.array_equal(pcm[1]-pcm[0],pcm[-1]-pcm[-2])
    else:assert not np.any(pcm[[0,-1]])
    result.append({'file':row['file'],'sha256':h})
assert len(m['sheets'])==24 and {p.relative_to(O).as_posix() for p in (O/'review').glob('*.png')}=={s['file'] for s in m['sheets']}
for s in m['sheets']:assert sha(O/s['file'])==s['sha256']
#1kHz sine at-20dBFSpeak should measure~-23.0LUFS mono/~ -20.0 stereo.
t=np.arange(3*FS)/FS;tone=.1*np.sin(2*np.pi*1000*t);mono,_=loudness(tone);stereo,_=loudness(np.column_stack([tone,tone]))
assert abs(mono+23)<.15 and abs(stereo+20)<.15,(mono,stereo)
receipt={'result':'PASS','files_verified':len(result),'sheets_verified':len(m['sheets']),'known_tone':{'mono_1khz_minus20dbfs_lufs':mono,'stereo_1khz_minus20dbfs_lufs':stereo,'expected_mono':-23,'expected_stereo':-20,'tolerance_lu':.15},'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'decoded_files':result}
(O/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SOUND VERIFY PASS',len(result),'WAV',len(m['sheets']),'PNG','calibration',mono,stereo)

"""SOUND-4 recorded CC0 Foley only; new cues/manifests only."""
from pathlib import Path
import sys, json
sys.dont_write_bytecode = True
R = Path(__file__).resolve().parents[4]; O = R/'Art/Audio/Real'
sys.path.insert(0,str(O/'tools'))
import build_crewfx as recorded
import build3
import numpy as np
from dsp import FS
recorded.INDEX += json.loads((O/'sources/sound4/index.json').read_text())
assert not (O/'sound4-edits.json').exists(), 'Refuse overwrite; explicitly remove own manifest before intentional rebuild.'
def window(p,duration,part=0,low=7000):
    x,r = recorded.read(p)
    assert r['license']=='CC0-1.0'
    lo = round(part*len(x)/3); hi = round((part+1)*len(x)/3)
    n = min(round(duration*FS),hi-lo)
    peak = lo+int(np.argmax(abs(x[lo:hi])))
    a = max(lo,min(peak-round(.010*FS),hi-n))
    return recorded.cut(p,a/FS,(a+n)/FS,low=low)
def beginning(p,duration,low=9000):
    x,r = recorded.read(p); assert r['license']=='CC0-1.0'
    active = np.flatnonzero(abs(x)>max(abs(x))*.015)
    a = max(0,int(active[0])-round(.010*FS))
    return recorded.cut(p,a/FS,min(len(x),a+round(duration*FS))/FS,low=low)
def emit(name,v,parts,target,note):
    assert not (O/f'SFX/{name}_{v}.wav').exists(), 'Refuse existing cue overwrite'
    recorded.emit(name,v,parts,note,target+(v-1)*.2)
def log(text):
    with (R/'comms.md').open('a') as f:f.write('\n'+text+'\n')
def boundary(letter,nextstep):
    rows=build3.ROWS
    (O/'sound4-edits.partial.json').write_text(json.dumps({'task':'SOUND-4','files':rows},indent=2)+'\n')
    log(f'CHECKPOINT / SOUND-4 {letter} / Codex 2 (WSL CLI): three WAVs and source edit manifest written; source CC0/hash/scan/archive-member gates passed. Output format/loudness/visual/listening UNVERIFIED until F. IN PROGRESS {nextstep}.')
hundred=recorded.hundred
for v in range(3):
    wood=beginning(hundred(f'wooden_{v+1:02d}'),.17+v*.01,low=3200)
    paper=beginning(hundred(f'paper_{v+1:02d}'),.12,low=4200)
    emit('CoachPop',v,[(wood,0,1),(paper,.018,.22)],-32,'Softened real wood contact and paper onset; gentle bubble appearance Foley, no synthesized pop.')
boundary('A','B real ship-bell double ring and short horn')
bell=O/'sources/sound4/ShipBell-preview.mp3'
horn=O/'sources/crewfx/ShipHornClean.ogg'
for v in range(3):
    ring=beginning(bell,1.80+v*.08,low=10500)
    toot=beginning(horn,.72+v*.04,low=6500)
    emit('RefitFanfare',v,[(ring,0,.85),(ring,.38+v*.025,1),(toot,1.10+v*.04,.40)],-27,'Two placements of the same recorded ship-bell strike plus cropped real steamboat horn; edited variants share original takes. Bell is public HQ MP3 preview; not original WAV. Horn shortened with fade, natural full horn remains in prior delivery.')
boundary('B','C quiet recorded tab taps')
for v in range(3):
    wood=beginning(hundred(f'wooden_{v+1:02d}'),.075+v*.009,low=2100)
    emit('TabTap',v,[(wood,0,1)],-38,'Very quiet damped real wood contact; target at least5LU below existing Click, no pitch shifting.')
boundary('C','D compact clink then coin drop')
coin=R/'Art/Audio/Downloads/oga-coin-sounds/coinsounds011015.wav'
for v in range(3):
    clink=window(coin,.12,part=v,low=9000)
    drop=window(coin,.30,part=(v+1)%3,low=6500)
    emit('CoinBuy',v,[(clink,0,.65),(drop,.14+v*.015,1)],-24,'Compact two-stage actual coin-handling Foley: short clink followed by offset drop/rattle, shorter and differently layered than existing Coins. Source montage reused with distinct cuts.')
boundary('D','E paper chart turn/unfold')
for v in range(3):
    paper=beginning(hundred(f'paper_{v+1:02d}'),.66+v*.025,low=8000)
    emit('PageTurn',v,[(paper,0,1)],-29,'Distinct recorded paper movement, cut as chart/page-opening Foley. Actual chart material and subjective unfold timbre unverified.')
boundary('E','F independent output verification and evidence')
(O/'sound4-edits.json').write_text(json.dumps({'task':'SOUND-4','method':'Real CC0 source recording crops/layers; mono44100 resample,45Hz highpass, per-cut lowpass,12ms cut/9ms final fades, gain-only transient control and loudness mastering. No synthesis or pitch shift.','files':build3.ROWS},indent=2)+'\n')
(O/'sound4-edits.partial.json').unlink()
print('BUILT',len(build3.ROWS))

"""Original offline foley DSP. Audio uses numpy/scipy only, no recordings."""
import numpy as np
from scipy import signal
FS=44100

def db(x):return float(20*np.log10(max(float(x),1e-12)))
def timeline(seconds):return np.arange(round(seconds*FS))/FS
def norm(x):return x/max(np.sqrt(np.mean(x*x)),1e-9)
def noise(rng,n,lo=70,hi=5000):
    x=rng.normal(size=n)
    sos=signal.butter(2,[lo,hi],btype='bandpass',fs=FS,output='sos')
    return norm(signal.sosfilt(sos,x))
def edge(x,ms=6):
    n=min(round(ms*FS/1000),len(x)//2);w=.5-.5*np.cos(np.linspace(0,np.pi,n))
    x=x.copy();x[:n]*=w.reshape((-1,)+(1,)*(x.ndim-1));x[-n:]*=w[::-1].reshape((-1,)+(1,)*(x.ndim-1));return x

def modes(t,freqs,decays,amps=None):
    if amps is None:amps=np.geomspace(1,.12,len(freqs))
    return sum(a*np.sin(2*np.pi*f*t)*np.exp(-t/d) for f,d,a in zip(freqs,decays,amps))
def strike(rng,dur,base=180,material='wood'):
    t=timeline(dur);j=rng.uniform(.96,1.04)
    if material=='metal':ratios=[1,2.18,2.79,4.16,5.43];ds=[.28,.18,.13,.08,.06];lo,hi=700,7000
    elif material=='plastic':ratios=[1,1.71,2.96,4.43];ds=[.030,.025,.020,.012];lo,hi=500,5000
    else:ratios=[1,2.63,4.07,6.16];ds=[.065,.039,.022,.014];lo,hi=100,2700
    x=modes(t,base*j*np.array(ratios),ds)+.42*noise(rng,len(t),lo,hi)*np.exp(-t/.014)
    return edge(x)
def place(x,y,start,gain=1):
    i=round(start*FS)
    if i<0:y=y[-i:];i=0
    n=min(len(y),len(x)-i)
    if n>0:x[i:i+n]+=y[:n]*gain

def water(rng,dur,force=1):
    t=timeline(dur);n=len(t)
    swell=(1-np.exp(-t/.008))*np.exp(-t/(dur*.27))
    x=noise(rng,n,160,4500)*swell*.34+noise(rng,n,45,650)*swell*.24
    for _ in range(round(9+force*10)):
        d=rng.uniform(.018,.09);u=timeline(d);f=rng.uniform(210,1100)
        y=np.sin(2*np.pi*(f*u-f*.38*u*u/d))*np.exp(-u/(d*.25))
        y+=.15*noise(rng,len(u),600,6500)*np.exp(-u/(d*.19))
        place(x,edge(y,2),rng.uniform(.006,dur*.72),rng.uniform(.025,.10)*force)
    return edge(x)
def rope(rng,dur,rate=35):
    t=timeline(dur);slip=np.mod(np.cumsum(rate*(1+.23*np.sin(t*19)))/FS,1)
    pressure=np.sin(np.pi*t/dur)**1.3
    x=(noise(rng,len(t),85,1900)*.22+np.sin(2*np.pi*(130*t+1.4*np.sin(t*5)))*.13)*(.2+np.exp(-slip*7))*pressure
    return edge(x)
def gull(rng,dur=1.25):
    x=np.zeros(len(timeline(dur)))
    for at,d,g in [(.025,.35,.7),(.43,.3,.52),(.81,.40,.82)]:
        t=timeline(d);u=t/d;f=(850+650*np.sin(np.pi*u)-280*u)*rng.uniform(.94,1.06)
        phase=2*np.pi*np.cumsum(f*(1+.012*np.sin(t*2*np.pi*29)))/FS
        voice=(np.sin(phase)+.40*np.sin(phase*2)+.13*np.sin(phase*3))
        y=(voice*(.8+.2*np.sin(2*np.pi*37*t))+.15*noise(rng,len(t),1000,3500))*np.sin(np.pi*u)**1.7
        place(x,edge(y),at,g)
    return edge(x)
def seal(rng,dur=.85):
    x=np.zeros(len(timeline(dur)))
    for at,d,g in [(.01,.31,1),(.42,.34,.7)]:
        t=timeline(d);u=t/d;f=(130-42*u+5*np.sin(t*2*np.pi*23))*rng.uniform(.9,1.1);p=2*np.pi*np.cumsum(f)/FS
        v=sum(np.sin(p*h)/h**.8 for h in range(1,9));v=signal.sosfilt(signal.butter(2,1800,fs=FS,output='sos'),v)
        y=(v*(.72+.28*np.sin(t*2*np.pi*31))+.23*noise(rng,len(t),180,1900))*np.sin(np.pi*u)**1.3
        place(x,edge(y),at,g)
    return edge(x)

RECIPES={
'Cast':'Air/line band noise sweeping through a smooth arm envelope, soft spool tick and outgoing line hiss.',
'Splash':'Filtered broadband water impact, low displaced-water body and irregular falling bubble grains.',
'Bite':'Two small wood/float knocks above a narrow water plip, short line tension rub.',
'Reel':'Jittered ratchet teeth, quiet low spool modes and an amplitude-shaped rope/friction bed.',
'Land':'Wet low board impact with secondary wooden settling and small water grains.',
'Stow':'Crate-body wood modes, sliding rubber friction and one delayed damped contact.',
'Moor':'Low timber contact, rope stick-slip and a second quieter hull settling knock.',
'Sale':'Paper/receipt rustle followed by an irregular restrained coin stack; no musical progression.',
'Select':'Quiet damped wooden switch touch with low filtered friction, under150ms.',
'Purchase':'Short paper rustle and one muffled coin contact, under150ms.',
'Gull':'Three nasal pitch-curved harmonic calls with breath band noise and rough amplitude modulation.',
'Bell':'Soft clapper contact and five inharmonic buoy-bell modes with unequal decays.',
'Creak':'Pressure-shaped rope/wood stick-slip with wandering pulse rate and low body resonance.',
'Horn':'Slowly swelled low reed/hull harmonics with slight drift and filtered breath.',
'Click':'Quiet plastic latch pair, short inharmonic body and damped friction, under150ms.',
'Winch':'Short rope pull with three irregular damped hauler pawl contacts; tail dies before450ms.',
'CrabClack':'Three staggered dry claw contacts exciting short plastic tray modes.',
'SealBark':'Two low rough harmonic barks with descending pitch and a throaty filtered-noise layer.',
'NetSlap':'Broad wet-net noise impact, low timber modes, scattered water droplets and rope settling.',
'Gut':'Short pressure-shaped wet knife friction with subdued low water grains; no tonal reward.',
'Coins':'Irregular small coin pile with differing inharmonic modes and a low wooden supporting tray.'}
DURATIONS={'Cast':.60,'Splash':.72,'Bite':.30,'Reel':.95,'Land':.55,'Stow':.48,'Moor':.65,'Sale':.72,'Select':.105,'Purchase':.130,'Gull':1.25,'Bell':2.6,'Creak':.65,'Horn':2.7,'Click':.090,'Winch':.39,'CrabClack':.34,'SealBark':.85,'NetSlap':.68,'Gut':.43,'Coins':.8}
UI={'Select','Click','Purchase'}
def cue(name,variant):
    rng=np.random.default_rng(265100+list(RECIPES).index(name)*101+variant*17)
    dur=DURATIONS[name]+(variant-1)*(.01 if name not in UI else .004)
    t=timeline(dur);x=np.zeros(len(t))
    if name=='Cast':
        x=noise(rng,len(t),450,6400)*np.sin(np.pi*t/dur)**2*(.5+.5*t/dur);place(x,strike(rng,.10,340,'plastic'),.025,.09)
    elif name=='Splash':x=water(rng,dur,1.2)
    elif name=='Bite':
        place(x,strike(rng,.18,390),.008,.8);place(x,strike(rng,.12,420),.103,.32);place(x,water(rng,.18,.4),.045,.23)
    elif name in {'Reel','Winch'}:
        x=rope(rng,dur,47)*.35
        times=np.arange(.015,dur-.075,.058) if name=='Reel' else [.012,.108,.214]
        for k,at in enumerate(times):place(x,strike(rng,.095,390+rng.uniform(-30,30),'plastic'),at+rng.uniform(-.004,.004),.18 if name=='Reel' else .30)
        x+=np.sin(2*np.pi*110*t)*np.sin(np.pi*t/dur)**2*.045
    elif name in {'Land','Stow','Moor','NetSlap'}:
        base={'Land':155,'Stow':185,'Moor':105,'NetSlap':125}[name]
        place(x,strike(rng,dur*.8,base),.010,.65);place(x,strike(rng,.16,base*1.18),.16,.24)
        x+=rope(rng,dur,29)*.4
        if name in {'Land','NetSlap'}:x+=water(rng,dur,.7)*(.85 if name=='NetSlap' else .44)
    elif name in {'Sale','Coins'}:
        if name=='Sale':x+=noise(rng,len(t),900,4500)*np.sin(np.pi*t/dur)**2*np.exp(-t/.24)*.35
        for at in [.018,.085,.153,.247,.38,.52]:
            place(x,strike(rng,.25,rng.uniform(1480,2150),'metal'),at+rng.uniform(-.008,.008),rng.uniform(.08,.16))
        place(x,strike(rng,.18,220),.03,.22)
    elif name in UI:
        place(x,strike(rng,dur*.80,270 if name=='Select' else 480,'wood' if name=='Select' else 'plastic'),.004,.32)
        x+=noise(rng,len(t),500,2300)*np.exp(-t/.028)*.035
        if name=='Purchase':place(x,strike(rng,.080,1550,'metal'),.038,.035)
        if name=='Click':place(x,strike(rng,.045,520,'plastic'),.042,.16)
    elif name=='Gull':x=gull(rng,dur)
    elif name=='SealBark':x=seal(rng,dur)
    elif name=='Bell':
        x=modes(t,rng.uniform(.97,1.03)*np.array([420,1008,1286,1680,2285]),[.83,.54,.43,.30,.19]);x+=noise(rng,len(t),180,1600)*np.exp(-t/.018)*.20
    elif name=='Creak':x=rope(rng,dur,29+rng.uniform(-4,4))
    elif name=='Horn':
        f=98*rng.uniform(.97,1.03)*(1+.003*np.sin(2*np.pi*4.2*t));p=2*np.pi*np.cumsum(f)/FS
        swell=np.minimum(1,t/.36)*np.minimum(1,(dur-t)/.65);swell=np.sin(np.pi/2*swell)**2
        x=(sum(np.sin(p*k)/k**1.5 for k in range(1,7))+.06*noise(rng,len(t),80,900))*swell
    elif name=='CrabClack':
        for at,base,g in [(.008,690,.7),(.091,780,.6),(.185,610,.4)]:place(x,strike(rng,.115,base,'plastic'),at,g)
    elif name=='Gut':
        pressure=np.sin(np.pi*t/dur)**2
        x=(noise(rng,len(t),450,3300)*.25+noise(rng,len(t),90,650)*.13)*pressure
        x+=water(rng,dur,.4)*.32
    else:raise ValueError(name)
    # Remove DC before the zero-endpoint taper. No limiter or clipping required.
    return edge(x-x.mean(),7)

AMBIENCE_RECIPES={
'HarbourDay':'Periodic low lapping bed, wet piling laps, distant filtered gull calls and rope creak; broad stereo.',
'OpenSea':'Periodic slow swell and soft high wind, irregular low hull slaps and small water scatter.',
'Skerries':'Periodic surf wash against rocks, filtered distant seal pairs and a darker low water body.'}
def periodic_noise(rng,n,lo,hi):
    # FFT-shaped whole-cycle noise, no filter transient at the seam.
    f=np.fft.rfftfreq(n,1/FS);shape=(1-np.exp(-(f/max(lo,1))**2))*np.exp(-(f/hi)**2)
    x=np.fft.irfft(np.fft.rfft(rng.normal(size=n))*shape,n)
    return norm(x)
def ambience(name):
    rng=np.random.default_rng(809100+list(AMBIENCE_RECIPES).index(name)*199);n=30*FS;t=np.arange(n)/FS
    shared=periodic_noise(rng,n,35,950)
    x=np.zeros((n,2))
    for c in range(2):
        surf=periodic_noise(rng,n,80,3100 if name=='Skerries' else 1700)
        wind=periodic_noise(rng,n,450,5800)
        amp=.40+.23*np.sin(2*np.pi*5*t/30+c*.22)+.12*np.sin(2*np.pi*3*t/30+.4)
        x[:,c]=(.55*shared+.45*surf)*amp+.045*wind*(.75+.25*np.sin(2*np.pi*2*t/30))
    def event(y,at,level,pan):
        idx=(round(at*FS)+np.arange(len(y)))%n
        x[idx,0]+=y*level*np.sqrt((1-pan)/2);x[idx,1]+=y*level*np.sqrt((1+pan)/2)
    for at in np.arange(.15,30,1.35 if name=='HarbourDay' else 2.7):
        y=water(rng,rng.uniform(.6,1.1),.55)
        event(y,at+rng.uniform(-.4,.4),.75 if name=='HarbourDay' else 1.0,rng.uniform(-.8,.8))
    if name=='HarbourDay':
        for at in [5.2,18.3,28.8]:
            y=gull(rng);y=signal.sosfilt(signal.butter(2,1800,fs=FS,output='sos'),y);event(y,at,.032,rng.uniform(-.7,.7))
        for at in [2.4,12.7,23.6]:event(rope(rng,.8,22),at,.24,rng.uniform(-.9,.9))
    elif name=='OpenSea':
        for at in [1.2,6.8,12.2,19.0,25.4,29.7]:event(strike(rng,.42,85),at,.11,rng.uniform(-.7,.7))
    else:
        for at in [6.4,21.5]:
            y=seal(rng);y=signal.sosfilt(signal.butter(3,900,fs=FS,output='sos'),y);event(y,at,.035,rng.uniform(-.75,.75))
    x-=x.mean(axis=0)
    # Smooth an8ms neighbourhood on either side of the circular join.
    # Equal live-bed endpoints and zero slope; no fade-to-silence or limiter.
    m=round(.008*FS);u=np.linspace(0,1,m);smooth=u*u*(3-2*u)
    for c in range(2):
        a=x[-m,c];b=(x[-1,c]+x[0,c])*.5;right=x[m-1,c]
        x[-m:,c]=a*(1-smooth)+b*smooth
        x[:m,c]=b*(1-smooth)+right*smooth
        x[-2:,c]=b;x[:2,c]=b
    x-=x.mean(axis=0)
    return x

# BS.1770 K-weighting per DeMan coefficients. Stereo channels both weight1.
def k_weight(x):
    f=1681.974450955533;G=3.999843853973347;Q=.7071752369554196;K=np.tan(np.pi*f/FS);vh=10**(G/20);vb=vh**.4996667741545416;a0=1+K/Q+K*K
    b=np.array([vh+vb*K/Q+K*K,2*(K*K-vh),vh-vb*K/Q+K*K])/a0;a=np.array([1,2*(K*K-1)/a0,(1-K/Q+K*K)/a0])
    y=signal.lfilter(b,a,x,axis=0)
    K=np.tan(np.pi*38.13547087602444/FS);Q=.5003270373238773;a0=1+K/Q+K*K
    return signal.lfilter([1,-2,1],[1,2*(K*K-1)/a0,(1-K/Q+K*K)/a0],y,axis=0)
def loudness(x):
    original=len(x);block=round(.4*FS);hop=round(.1*FS)
    if x.ndim==1:x=x[:,None]
    if len(x)<block:x=np.pad(x,((0,block-len(x)),(0,0)))
    y=k_weight(x);e=np.sum(y*y,axis=1);integral=np.r_[0,np.cumsum(e)]
    starts=np.arange(0,len(e)-block+1,hop);power=(integral[starts+block]-integral[starts])/block
    ls=-.691+10*np.log10(np.maximum(power,1e-24));g=power[ls>-70]
    if not len(g):return -120.,max(0,block-original)/FS
    relative=-.691+10*np.log10(g.mean())-10;g=power[(ls>-70)&(ls>relative)]
    return float(-.691+10*np.log10(g.mean())),max(0,block-original)/FS

def master(x,target):
    current,_=loudness(x);x=x*10**((target-current)/20)
    tp=np.max(np.abs(signal.resample_poly(x,4,1,axis=0)))
    if tp>10**(-3.4/20):x*=10**(-3.4/20)/tp
    return x

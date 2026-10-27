"""SOUND-2 original offline synthesis; imports SOUND-1 primitives without altering them."""
import numpy as np
from scipy import signal
from dsp import FS,timeline,noise,edge,norm,modes,strike,place,water,rope,gull,periodic_noise
RECIPES={
 'Puffin':'One low purring growl-call: rough low harmonic throat, fluttering pressure, narrow breath and soft terminal exhale.',
 'Foghorn':'One distant low diaphone-inspired blast: 52Hz pulsed pressure, a soft falling release, dark delayed reflections and diffuse tail; quiet.',
 'DogBark':'One friendly small-dog bark: fast rounded onset, descending rough glottal pulse, broad mouth resonances and short breath decay.',
 'Meow':'Short ginger-cat meow: softly swept glottal harmonics, moving nasal/mouth resonances, breath and a tapered closing vowel.',
 'Stitch':'Twine pull through a net mesh: smooth pressure-shaped fibre noise, irregular stick-slip grains and a soft final knot touch.',
 'PotDrop':'One pot over the rail: low wooden thump, rope friction, delayed displaced-water splash and small buoy/bubble settling.'}
AMBIENCE_RECIPES={
 'HarbourDusk':'Warmer, quieter periodic piling laps than HarbourDay, sparse distant gulls and rope, one low church bell stroke at20.1s; no crickets.',
 'LighthouseRock':'Slow open swell, broken surf washes against rock, soft wind and a distant scattered puffin colony; no foghorn.'}
DURATIONS={'Puffin':[.66,.72,.78],'Foghorn':[2.9,3.,3.1],'DogBark':[.25]*3,'Meow':[.4]*3,'Stitch':[.2]*3,'PotDrop':[.8]*3}
TARGETS={'Puffin':-28,'Foghorn':-32,'DogBark':-27,'Meow':-27,'Stitch':-29,'PotDrop':-25,'HarbourDusk':-30,'LighthouseRock':-28}

def low(x,cut,order=2):return signal.sosfilt(signal.butter(order,cut,fs=FS,output='sos'),x,axis=0)
def band(x,lo,hi):return signal.sosfilt(signal.butter(2,[lo,hi],btype='bandpass',fs=FS,output='sos'),x)
def vocal(rng,dur,kind):
 t=timeline(dur);u=t/dur;j=rng.uniform(.94,1.06)
 if kind=='Puffin':
  f=j*(105+24*np.sin(np.pi*u)-19*u+3*np.sin(2*np.pi*21*t));ph=2*np.pi*np.cumsum(f)/FS
  throat=sum(np.sin(k*ph+rng.uniform(-.12,.12))/k**1.15 for k in range(1,13))
  throat=low(throat,1350);flutter=.68+.22*np.sin(2*np.pi*(25*t+2*t*t))+.10*noise(rng,len(t),9,42)
  pressure=np.sin(np.pi*u)**1.35*(.92+.08*np.sin(2*np.pi*7*t))
  x=(throat*flutter+.16*noise(rng,len(t),180,1200))*pressure
 elif kind=='DogBark':
  f=j*(192-80*u+6*np.sin(2*np.pi*39*t));ph=2*np.pi*np.cumsum(f)/FS
  excitation=sum(np.sin(k*ph)/k**.85 for k in range(1,19))
  voiced=.45*low(excitation,2200)+1.4*band(excitation,420,850)+.6*band(excitation,1050,1750)
  env=(1-np.exp(-t/.009))*np.exp(-np.maximum(t-.035,0)/.052)*(1-u)**.4
  x=(voiced*(.78+.22*np.sin(2*np.pi*43*t))+.36*noise(rng,len(t),220,2700))*env
 elif kind=='Meow':
  f=j*(410+200*np.sin(np.pi*u)**.8-125*u+6*np.sin(2*np.pi*25*t));ph=2*np.pi*np.cumsum(f)/FS
  excitation=sum(np.sin(k*ph)/k**1.2 for k in range(1,14))
  # Two broad mouth states crossfade with the closing vowel; no syllable/text model.
  ee=.6*low(excitation,3600)+1.8*band(excitation,850,1450)+.8*band(excitation,2100,3000)
  ow=.8*low(excitation,2200)+1.6*band(excitation,500,1050)+.6*band(excitation,1300,1900)
  transition=np.clip((u-.48)/.40,0,1);pressure=np.sin(np.pi*u)**1.1
  x=((1-transition)*ee+transition*ow+.10*noise(rng,len(t),700,3600))*pressure
 else:raise ValueError(kind)
 return edge(x-x.mean(),7)

def cue(name,variant):
 rng=np.random.default_rng(265200+list(RECIPES).index(name)*191+variant*37);dur=DURATIONS[name][variant];t=timeline(dur);x=np.zeros(len(t))
 if name in {'Puffin','DogBark','Meow'}:x=vocal(rng,dur,name)
 elif name=='Foghorn':
  active=1.85+(variant-1)*.08;f=52*rng.uniform(.96,1.04)*(1+.003*np.sin(2*np.pi*3.2*t))
  # A lower brief release on the same blast, rather than a second horn event.
  f*=1-.12*np.clip((t-(active-.22))/.22,0,1);ph=2*np.pi*np.cumsum(f)/FS
  pulse=sum(np.sin(k*ph)/k**1.5 for k in range(1,12));pulse=low(pulse,720)
  env=(1-np.exp(-t/.18))**2/(1+np.exp(np.clip((t-active)/.11,-60,60)))
  dry=(pulse+.055*noise(rng,len(t),45,650))*env
  x+=dry
  for delay,g in [(.18,.16),(.36,.10),(.58,.07),(.83,.035)]:place(x,low(dry,460),delay,g)
 elif name=='Stitch':
  pressure=np.sin(np.pi*t/dur)**1.8;slips=.65+.35*np.sin(2*np.pi*(75*t+80*t*t))**2
  x=(.72*noise(rng,len(t),550,4200)+.15*noise(rng,len(t),160,850))*pressure*slips
  for at in [.065,.107,.143]:
   d=.018;u=timeline(d);grain=noise(rng,len(u),900,5200)*np.sin(np.pi*u/d)**2;place(x,grain,at+rng.uniform(-.004,.004),.11)
  place(x,strike(rng,.042,650,'plastic'),.153,.035)
 elif name=='PotDrop':
  place(x,strike(rng,.23,128),.012,.85);place(x,strike(rng,.13,205),.065,.17)
  place(x,rope(rng,.28,30),.06,.25);place(x,water(rng,.59,1.35),.19,1.12)
  place(x,water(rng,.19,.38),.57,.15)
 else:raise ValueError(name)
 return edge(x-x.mean(),7)

def smooth_join(x):
 x=x-x.mean(axis=0);m=round(.008*FS);u=np.linspace(0,1,m);s=u*u*(3-2*u)
 for c in range(2):
  a=x[-m,c];b=(x[-1,c]+x[0,c])*.5;right=x[m-1,c]
  x[-m:,c]=a*(1-s)+b*s;x[:m,c]=b*(1-s)+right*s;x[-2:,c]=b;x[:2,c]=b
 return x-x.mean(axis=0)

def ambience(name):
 rng=np.random.default_rng(809200+list(AMBIENCE_RECIPES).index(name)*199);n=30*FS;t=np.arange(n)/FS;x=np.zeros((n,2));events=[]
 shared=periodic_noise(rng,n,32,780 if name=='HarbourDusk' else 1100)
 for c in range(2):
  wash=periodic_noise(rng,n,100,1400 if name=='HarbourDusk' else 4000);wind=periodic_noise(rng,n,400,2700 if name=='HarbourDusk' else 5200)
  amp=.37+.17*np.sin(2*np.pi*4*t/30+c*.18)+.10*np.sin(2*np.pi*7*t/30+.5)
  x[:,c]=(.60*shared+.40*wash)*amp+wind*(.025 if name=='HarbourDusk' else .06)*(.8+.2*np.sin(2*np.pi*2*t/30))
 def event(y,at,g,pan,kind):
  idx=(round(at*FS)+np.arange(len(y)))%n;x[idx,0]+=y*g*np.sqrt((1-pan)/2);x[idx,1]+=y*g*np.sqrt((1+pan)/2)
  events.append({'kind':kind,'start_seconds':float(at),'duration_seconds':len(y)/FS,'raw_gain':g,'pan':float(pan),'wraps':at+len(y)/FS>30 or at<0})
 if name=='HarbourDusk':
  for at in np.arange(.2,30,1.8):event(low(water(rng,rng.uniform(.75,1.1),.45),1600),float(at+rng.uniform(-.25,.25)),.52,rng.uniform(-.8,.8),'piling-lap')
  for at in [6.1,26.3]:event(low(gull(rng),1500,3),at,.018,rng.uniform(-.7,.7),'far-gull')
  for at in [3.4,14.5]:event(low(rope(rng,.8,19),1200),at,.14,rng.uniform(-.7,.7),'rope')
  u=timeline(6.1);bell=modes(u,[238,476,566,713,952,1428],[2.2,2.8,2.3,1.9,1.5,.9],[.65,1,.4,.25,.16,.07]);bell=low(edge(bell,12),1700,3)
  event(bell,20.1,.032,.35,'one-far-church-bell-stroke')
 else:
  for at in [1.2,6.9,13.1,19.4,25.2,29.55]:
   d=rng.uniform(.95,1.55);u=timeline(d);shape=np.sin(np.pi*u/d)**1.8
   y=(noise(rng,len(u),75,1300)*.52+noise(rng,len(u),500,4800)*.32)*shape; y+=water(rng,d,.6)*.4
   event(edge(y),at,.52,rng.uniform(-.85,.85),'rock-surf')
  for at,d,g in [(4.8,.72,.025),(8.2,.64,.016),(16.5,.8,.023),(22.4,.66,.020),(27.3,.74,.018)]:
   event(low(vocal(rng,d,'Puffin'),1000,3),at,g,rng.uniform(-.8,.8),'far-puffin')
 return smooth_join(x),events

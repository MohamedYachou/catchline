from pathlib import Path
O=Path(__file__).resolve().parent
s=(O.parent/'Upgrades/build.py').read_text()
header=s[:s.index('assets=[]')]
body=r'''
assets=[]
def add(name,g,fp=(1,1),**meta):assets.append(('Restaurant_'+name,g,fp,meta))
def box(g,c,d,col):g.box(c,d,col)
def base(g,w=.8,d=.68,h=.62,col='navy'):
 for x in [-w/2+.06,w/2-.06]:
  for y in [-d/2+.06,d/2-.06]:box(g,(x,y,.055),(.07,.07,.11),'dark')
 box(g,(0,0,(h+.11)/2),(w,d,h-.11),col)
 box(g,(0,0,h+.02),(w+.025,d+.025,.045),'steel')
def knob(g,x,y,z):ell(g,(x,y,z),(.027,.018,.027),'dark',10);box(g,(x,y-.016,z),(.007,.008,.025),'ivory')
def handle(g,x,y,z,h=.29):tube(g,(x,y,z-h/2),(x,y,z+h/2),.014,'steel',8)
def ring(g,c,r,col,n=16,rad=.009):
 x,y,z=c;g.tube([(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z) for i in range(n+1)],[rad]*(n+1),6,col)
# Dedicated open grill: thick slotted grate, firebox and orange coals.
g=H.Geometry();base(g)
box(g,(0,0,.68),(.73,.58,.08),'dark')
for x in [-.29,-.14,0,.14,.29]:box(g,(x,0,.722),(.075,.49,.015),'orange')
for x in [-.32+i*.064 for i in range(11)]:tube(g,(x,-.27,.75),(x,.27,.75),.009,'steel',6)
for x in [-.2,0,.2]:knob(g,x,-.365,.52)
box(g,(0,.32,.77),(.83,.045,.20),'steel');add('Grill',g,worktop_z_m=.75)
# Steam cabinet/pot with bamboo-colour stacking rings, perforated lid and handles.
g=H.Geometry();base(g,w=.66,d=.64,h=.57,col='steel');cyl(g,(0,0,.64),.255,.08,'dark')
for z in [.735,.86]:
 cyl(g,(0,0,z),.245,.115,'steel',20);ring(g,(0,0,z+.055),.245,'ivory')
 for a in [0,math.pi]:tube(g,(.25*math.cos(a),0,z),(.31*math.cos(a),0,z),.020,'navy')
ell(g,(0,0,.95),(.245,.245,.055),'steel',20);cyl(g,(0,0,1.01),.04,.035,'navy')
for a in range(6):cyl(g,(.14*math.cos(a*1.047),.14*math.sin(a*1.047),.997),.012,.004,'dark',8)
knob(g,0,-.34,.46);add('Steamer',g,worktop_z_m=.63)
# Glazed drinks display: opaque blue glazing plus physical shelf/bottle cues; no transparency dependency.
g=H.Geometry();base(g,w=.72,d=.62,h=1.15)
box(g,(0,-.323,.65),(.59,.025,.88),'blue');box(g,(0,-.345,.16),(.62,.035,.06),'steel')
for z in [.28,.56,.84]:
 box(g,(0,-.351,z),(.57,.045,.025),'steel')
 for i,x in enumerate([-.21,-.07,.07,.21]):
  cyl(g,(x,-.374,z+.085),.033,.14,'leaf' if i%2 else 'orange',10);cyl(g,(x,-.374,z+.17),.017,.045,'ivory',8);box(g,(x,-.409,z+.085),(.043,.009,.045),'white')
handle(g,.285,-.39,.69,.31);box(g,(0,-.354,1.06),(.55,.015,.065),'glow');add('DrinksFridge',g)
# Framed navigation chart: warm paper, meandering blue coast, small islands and compass rose.
g=H.Geometry();box(g,(0,0,.34),(.88,.065,.68),'wooddark');box(g,(0,-.039,.34),(.80,.018,.60),'brass');box(g,(0,-.053,.34),(.75,.012,.55),'ivory')
coast=[(-.35,-.064,.075),(-.35,-.064,.59),(-.19,-.064,.59),(-.24,-.064,.49),(-.06,-.064,.41),(-.16,-.064,.32),(.02,-.064,.22),(-.09,-.064,.075)]
g.add(coast,[tuple(range(8))],'teal')
for x,z,r in [(.19,.38,.055),(.25,.48,.036),(.08,.14,.025)]:ell(g,(x,-.065,z),(r,.008,r*.62),'leaf',10)
for z in [.18,.30,.42,.54]:tube(g,(-.32,-.066,z),(.32,-.066,z),.002,'rope',5)
for x in [-.24,-.08,.08,.24]:tube(g,(x,-.066,.10),(x,-.066,.57),.002,'rope',5)
for a in range(8):
 r=.055 if a%2==0 else .031;x,z=.24,.18
 tube(g,(x,-.077,z),(x+r*math.sin(a*.785),-.077,z+r*math.cos(a*.785)),.004,'navy',5)
add('Chart',g,mount='wall',recommended_base_height_m=1.0)
# Rounded jukebox with segmented brass arch, warm cream control panel and vertical speaker slats.
g=H.Geometry();box(g,(0,0,.04),(.66,.40,.08),'wooddark');box(g,(0,0,.41),(.61,.36,.72),'navy')
ell(g,(0,0,.76),(.305,.18,.29),'navy',20);box(g,(0,-.19,.48),(.49,.035,.48),'wooddark')
for x in [-.21+i*.047 for i in range(10)]:tube(g,(x,-.218,.25),(x,-.218,.54),.010,'brass',6)
box(g,(0,-.218,.68),(.45,.035,.19),'ivory');box(g,(0,-.241,.73),(.37,.015,.065),'teal')
for x in [-.14,-.07,0,.07,.14]:ell(g,(x,-.248,.63),(.019,.010,.017),'brass',8)
path=[(-.285,-.20,.20),(-.285,-.20,.76)]+[(.285*math.cos(math.pi-i*math.pi/16),-.20,.76+.24*math.sin(math.pi-i*math.pi/16)) for i in range(17)]+[(.285,-.20,.20)]
g.tube(path,[.021]*len(path),8,'brass');add('Jukebox',g)
# Upgrade refrigeration: double doors, chunky latches, crown compressor and brass temperature dial.
g=H.Geometry();base(g,w=1.46,d=.75,h=1.49,col='ivory')
for x in [-.358,.358]:
 box(g,(x,-.391,.83),(.68,.045,1.22),'steel');box(g,(x,-.42,.83),(.61,.02,1.14),'ivory');handle(g,x+(.235 if x<0 else -.235),-.46,.83,.42)
box(g,(0,0,1.57),(1.46,.75,.13),'navy')
for x in [-.52+i*.095 for i in range(12)]:box(g,(x,-.388,1.57),(.05,.01,.065),'dark')
ell(g,(.55,-.451,1.34),(.05,.012,.05),'brass',12);add('BigFridge',g,(2,1),upgrade='S8 fridge')
# Heavy reliable six-burner range with twin oven windows and brass controls.
g=H.Geometry();base(g,w=1.55,d=.75,h=.65,col='ivory');box(g,(0,.37,.77),(1.58,.06,.22),'steel')
for x in [-.52,0,.52]:
 for y in [-.18,.18]:
  cyl(g,(x,y,.708),.12,.025,'dark',16);ring(g,(x,y,.73),.09,'steel',12)
  for a in [0,math.pi/2]:tube(g,(x-.14*math.cos(a),y-.14*math.sin(a),.75),(x+.14*math.cos(a),y+.14*math.sin(a),.75),.012,'steel',6)
for x in [-.38,.38]:
 box(g,(x,-.393,.32),(.65,.04,.34),'navy');box(g,(x,-.418,.32),(.48,.012,.19),'dark');tube(g,(x-.24,-.445,.53),(x+.24,-.445,.53),.016,'steel')
for x in [-.64,-.39,-.13,.13,.39,.64]:ell(g,(x,-.415,.62),(.029,.018,.029),'brass',10)
add('ReliableStove',g,(2,1),upgrade='S8 stove',worktop_z_m=.75)
# Cosy enamel pendant: open underside, ivory reflector, brass socket and warm bulb.
g=H.Geometry();cyl(g,(0,0,.045),.045,.09,'glow',12)
vs=[]
for r,z in [(.27,.01),(.28,.035),(.095,.27),(.06,.30)]:vs.extend([(r*math.cos(i*math.tau/20),r*math.sin(i*math.tau/20),z) for i in range(20)])
for k in range(3):g.add(vs,[tuple([k*20+i,k*20+(i+1)%20,(k+1)*20+(i+1)%20,(k+1)*20+i]) for i in range(20)],'navy' if k else 'ivory')
ring(g,(0,0,.02),.278,'brass',20,rad=.012);cyl(g,(0,0,.32),.055,.06,'brass',12);tube(g,(0,0,.35),(0,0,.89),.012,'dark');cyl(g,(0,0,.91),.09,.04,'navy',12)
add('CosyPendantLamp',g,mount='ceiling',recommended_base_height_m=1.65,upgrade='S8 lighting',emission='glow atlas cell, Surface.B; runtime point light recipe separate')
'''
# Reuse accepted net and trophy geometry verbatim, under dedicated ItemId model filenames.
decor=s[s.index("g=H.Geometry();path="):s.index("g=H.Geometry();g.box((0,0,.32)")]
decor=decor.replace("add('WallNetFloats'","add('Net'").replace("add('WallFishTrophy'","add('Trophy'")
footer=s[s.index('rows=[]'):].replace("O/'RestaurantUpgrades.blend'","O/'RestaurantKitchenKit2.blend'")
(O/'build.py').write_text(header+body+decor+footer)
(O/'validate.py').write_text((O.parent/'Upgrades/validate.py').read_text())

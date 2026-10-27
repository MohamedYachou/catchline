"""Approved MAP-PLAN layouts, World XZ metres. No runtime/source dependencies."""
import math

GROUND_NAMES = {
    'GullHarbourMouth': [('quay-shallows','Quay shallows',1.2),('channel','Channel',3.8),('mouth-flats','Mouth flats',1.4)],
    'GullKelpBank': [('kelp-shallows','Kelp shallows',1.2),('kelp-edge','Kelp edge',2.3),('open','Open',5.2)],
    'GullSandbar': [('the-bar','The bar',1.1),('gully','Gully',3.6),('open','Open',5.2)],
    'GullRockyPoint': [('reef','Reef',1.8),('drop-off','Drop-off',3.7),('open','Open',5.8)],
    'GullDeepChannel': [('drop-off','Drop-off',4.2),('trench','Trench',14.0),('open','Open',9.0)],
    'GullSkerries': [('seal-rocks','Seal rocks',2.3),('kelp-gully','Kelp gully',3.8),('outer-reef','Outer reef',7.0)],
    'GullWreckBank': [('the-wreck','The wreck',4.2),('herring-bank','Herring bank',2.0),('sand-edge','Sand edge',3.2)],
    'GullLighthouseRock': [('the-pinnacle','The pinnacle',4.5),('tide-race','Tide race',3.2),('deep-ledge','Deep ledge',9.0)],
    'GullWhaleShelf': [('herring-shoals','Herring shoals',3.0),('shelf-edge','Shelf edge',12.0),('whale-road','Whale road',8.0)],
}

def island(id, centre, radii, height, purpose, kind='grass', phase=0):
    return dict(id=id,centre=centre,radii=radii,height=height,purpose=purpose,kind=kind,phase=phase)

LAYOUTS = {
 'GullHarbourMouth': dict(title='Harbour mouth',size=(220,160),harbour=(-76,30),
   centres=[(-65,27,12),(6,-34,12),(68,0,14)],
   islands=[island('mainland-coast',(0,61),(95,9),3.6,'Long working coast frames Quay shallows; quay faces the open channel.',phase=.3),
            island('west-islet',(-20,-8),(17,23),3.2,'Blocks the direct Quay shallows to Channel line; west/east passage choice.',phase=1.1),
            island('east-islet',(32,26),(15,13),2.6,'Shelters Mouth flats and defines the eastern channel entrance.',phase=2)],
   horizon='Mainland headlands, outer lighthouse and small coastal freighter.'),
 'GullKelpBank': dict(title='Kelp bank',size=(260,180),harbour=(-99,-58),
   centres=[(-68,-33,14),(5,60,14),(88,-44,18)],
   islands=[island('west-low-island',(-65,12),(25,15),2.3,'Shelters the dense shallow kelp from the open northern water.',phase=.5),
            island('middle-low-island',(-15,5),(23,30),3.2,'Blocks Kelp shallows to Kelp edge; opens two different routes.',phase=1.3),
            island('east-low-island',(65,20),(24,16),2.1,'Broken kelp shelf frames Kelp edge, with open water on the far side.',phase=2.1)],
   horizon='Low distant island chain and an outer lighthouse.'),
 'GullSandbar': dict(title='Sandbar',size=(260,200),harbour=(-92,-61),
   centres=[(-37,5,14),(37,15,14),(86,-53,18)],
   islands=[island('long-sandbar',(0,0),(14,67),.8,'Splits west and east grounds; sail the north or south gully.',kind='sand',phase=.4)],
   horizon='Low dune coast, remote lighthouse and a passing ship.'),
 'GullRockyPoint': dict(title='Rocky point',size=(280,200),harbour=(-105,-70),
   centres=[(-65,-39,14),(48,-57,15),(-89,54,18)],
   islands=[island('rocky-headland',(42,45),(53,28),7.0,'Tall headland frames the reef field and drop-off.',kind='rock',phase=.5),
            island('west-reef',(-75,7),(12,18),1.7,'Blocks Reef to Open; the reef is a real route obstacle.',kind='rock',phase=1),
            island('south-reef',(-5,-38),(11,14),1.0,'Separates the southern passage from the valuable reef shelf.',kind='rock',phase=2),
            island('east-reef',(66,-7),(16,11),1.6,'Shelters the drop-off and breaks the headland approach.',kind='rock',phase=2.6)],
   horizon='Layered offshore headlands, rock stacks and a distant lighthouse.'),
 'GullDeepChannel': dict(title='Deep channel',size=(320,240),harbour=(-106,-86),
   centres=[(-103,-36,16),(-3,77,15),(110,48,18)],
   islands=[island('west-channel-island',(-52,20),(31,61),6.2,'Blocks Drop-off to Trench; defines the western trench wall.',kind='rock',phase=.4),
            island('east-channel-island',(45,-25),(35,62),5.4,'Defines the eastern trench wall and shelters the Open ground.',kind='grass',phase=1.6)],
   horizon='Low outer islands, a lighthouse, and an unreachable freighter in the ship lane.'),
 'GullSkerries': dict(title='Seal skerries',size=(300,240),harbour=(-115,-85),
   centres=[(-84,-25,14),(8,57,15),(99,-35,18)],
   islands=[island('west-seal-skerry',(-62,13),(17,18),1.8,'Low granite basking rock shelters Seal rocks; leave its southern fishing approach open.',kind='rock',phase=.6),
            island('middle-seal-skerry',(-13,8),(22,23),2.5,'Second seal colony divides Seal rocks from Kelp gully; choose either side of its broad reef shelf.',kind='rock',phase=1.4),
            island('east-breaker-skerry',(57,14),(14,18),1.1,'White water marks the granite reef between Kelp gully and Outer reef.',kind='rock',phase=2.2),
            island('north-granite-skerry',(70,65),(12,10),.8,'Low outer granite rock frames the kelp approach without closing the gully.',kind='rock',phase=2.8)],
   sealColonyAnchors=[dict(id='SealColony_1',position=[-62,1.88,13]),dict(id='SealColony_2',position=[-13,2.58,8])],
   horizon='Low granite islets, a distant lighthouse and a passing coastal freighter.'),
}

# MAP7 is additive. The six accepted maps above retain their data and bytes.
LAYOUTS['GullWreckBank'] = dict(title='Wreck bank',size=(300,240),harbour=(-115,-85),
    centres=[(-72,-24,12),(2,61,14),(99,-35,14)],
    islands=[island('bank-spine',(12,13),(18,27),.32,
        'Low angular exposed sand spine divides the wreck and bank approaches.',kind='sand')],
    sealColonyAnchors=[],lifeAnchors=[],
    horizon='Low offshore sandbank, half-sunk steamer and remote outer shipping lane.',
    waterShallow='2E8C8A',waterDeep='1C6E7E')

# MAP8 is additive; accepted map layouts are unchanged.
LAYOUTS['GullLighthouseRock'] = dict(title='Lighthouse rock',size=(320,260),harbour=(-126,-91),
    centres=[(-55,-30,12),(40,65,14),(100,-42,14)],
    islands=[island('lighthouse-stack',(0,12),(21,17),8.4,
        'Lone angular granite stack crowned by white-red lighthouse and keeper cottage.',kind='rock')],
    sealColonyAnchors=[],lifeAnchors=[],
    horizon='Open ocean, distant shipping silhouettes and solitary lighthouse rock.',
    waterShallow='1F5F8C',waterDeep='123F66')

# MAP9 is additive; a low sea mount is the only exposed terrain.
LAYOUTS['GullWhaleShelf'] = dict(title='Whale shelf',size=(360,280),harbour=(-142,-105),
    centres=[(-85,-35,14),(10,70,14),(112,-42,16)],
    islands=[island('bird-seamount',(-23,15),(15,24),1.1,
        'Low bird-whitened angular sea mount divides shoals from the shelf approach.',kind='rock')],
    sealColonyAnchors=[],lifeAnchors=[],
    horizon='Open continental shelf, one low bird sea mount and submerged sand shoal. No buildings.',
    waterShallow='2A7F96',waterDeep='102F4F')

def perimeter_buoys(w,h):
    corners=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]
    points=[]
    for a,b in zip(corners,corners[1:]+corners[:1]):
        n=math.ceil(math.dist(a,b)/28)
        for j in range(n):
            t=j/n;points.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t))
    return points

def point(p):
    return dict(x=round(float(p[0]),5),z=round(float(p[1]),5))

def grounds(name):
    return [dict(id=id,name=title,centre=point((x,z)),radius=r,nominalDepth=depth,
                 poolId=f'{name}/{id}',position=[x,0,z],heading=0)
            for (id,title,depth),(x,z,r) in zip(GROUND_NAMES[name],LAYOUTS[name]['centres'])]

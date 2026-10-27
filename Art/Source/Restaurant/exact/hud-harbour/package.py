"""Harbour exact source package. Shared deterministic operations in hud-fishing/package.py."""
from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('hudkit',P.parent/'hud-fishing/package.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
Image=m.Image

def harbour():
 k=m.Pack('harbour')
 k.base('status-board',[35,30,533,250],[32,32,32,32])
 for id,txt,r,sz in [('title','Gull Harbour',[81,49,443,55],52),('voyage','Voyage 3  ·  380 coins',[139,112,390,39],32),('next-hull','Next hull: skiff refit',[77,158,438,36],29),('goal','Land 16 fish (best 6) + 1,500 coins',[78,234,463,30],24)]:k.label(id,txt,r,sz)
 k.icon('coin',[82,109,42,42]);k.icon('status-rope',[20,18,64,94])
 n=k.cut('refit-fill',[79,200,192,25],'panel',borders=[12,8,12,8]);k.use(n,[79,200,192,25],z=16)
 n=k.reuse('refit-track','s3-s5/v2-bar-track.png',[77,198,459,27],[15,10,15,10]);k.use(n,[77,198,459,27],z=15)
 k.base('shop-panel',[976,112,920,942],[40,40,40,40])
 # Full rope beam is an ornamental cut; tab bodies and icons remain independent.
 k.icon('shop-rope',[963,20,935,32])
 tabs=[('catch','Catch',[990,49,173,69],[1019,63,42,37],[1064,65,86,39]),('map','Map',[1163,49,164,69],[1197,64,39,36],[1240,65,75,39]),('contracts','Contracts',[1329,49,183,69],[1357,64,36,37],[1394,65,110,39]),('crew','Crew',[1512,49,171,69],[1546,65,37,36],[1587,65,83,39]),('shop','Shop',[1683,29,210,90],[1717,55,51,45],[1777,62,99,41])]
 for id,txt,r,ir,tr in tabs:
  if id=='shop':
   a=k.im.crop(m.rectbox(r));alpha=m.matte(a,'panel').getchannel('A');a.paste(k.donor.crop((1555,42,1614,79)).resize((a.width-40,a.height-34)),(20,17));a.putalpha(alpha);n=k.export('tab-selected',a,r,[28,20,28,24],method='original selected tab rim, textless built-in ImageGen navy centre');k.use(n,r,z=3)
  else:
   if id=='catch':tab=k.cut('tab-idle',r,'panel',True,[22,18,22,22])
   k.use(tab,r,role='tab-'+id,z=3)
  k.icon('tab-'+id+'-icon',ir);k.label('tab-'+id,txt,tr,23 if id=='contracts' else 27,'center','#FFF4DC' if id=='shop' else '#173F57')
 k.label('supplies','Supplies',[1005,133,833,54],48)
 k.label('upgrades','Boat upgrades',[1004,441,833,53],45)
 row=k.cut('shop-row',[1002,194,869,104],'panel',True,[32,30,32,30])
 # Existing orange restaurant primary is the same reusable action family.
 coin=k.cut('buy-coin',[82,109,42,42],'icon')
 r=[1611,216,238,63];a=m.matte(k.im.crop(m.rectbox(r)),'panel');a.paste(k.donor.crop((1110,839,1562,887)).resize((a.width-28,a.height-22)),(14,11));buy=k.export('buy-button',a,r,[20,20,20,20],method='original orange rounded buy rim with textless orange interior')
 rows=[('bait',194,[1026,193,136,98],'Bait · 12 in the bucket','One per cast. Miss the bite, lose the bait.','+10 for 10'),('food',314,[1023,309,146,106],'Food · 4.2 / 6 min','Each sailor eats one minute per minute.','Fill up for 4'),('rod',501,[1033,500,134,95],'Rod holder','A second rod. Unattended self-hook: 35%.','250 coins'),('cooler',610,[1032,607,131,99],'Big cooler','Holds 16 fish instead of 10.','200 coins'),('ice',720,[1033,724,133,89],'Ice box','Keep the full value of your catch.','250 coins'),('lunch',830,[1037,835,122,91],'Lunch tin','Carry 12 minutes of food instead of 6.','100 coins')]
 for id,y,ir,title,desc,price in rows:
  k.use(row,[1002,y,869,104],role='row-'+id,z=3);n=k.cut('item-'+id,ir,'cream');k.use(n,ir,z=20);k.label(id+'-name',title,[1181,y+14,422,39],33);k.label(id+'-description',desc,[1181,y+56,430,32],22)
  r=[1611,y+22,238,63];k.use(buy,r,role='buy-'+id,z=12);k.use(coin,[1631,y+32,39,41],role='buy-'+id+'-coin',z=20);k.label('buy-'+id,price,[1678,y+30,160,45],28,'center','#FFF4DC')
 # Sail button keeps its concept rim and hardware, generated orange donor removes live caption.
 r=[1001,945,871,90];a=m.matte(k.im.crop(m.rectbox(r)),'panel');alpha=a.getchannel('A');a.paste(k.donor.crop((1110,839,1562,887)).resize((a.width-70,a.height-26)),(35,13));a.putalpha(alpha);n=k.export('sail-button',a,r,[40,29,40,29],method='original sail frame plus textless built-in ImageGen orange donor');k.use(n,r,z=4)
 k.icon('sail-boat',[1140,952,72,72]);k.label('sail','Set sail  ·  Harbour mouth',[1235,967,603,53],42,'center','#FFF4DC')
 k.finish()
if __name__=='__main__':harbour()

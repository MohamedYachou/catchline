"""Bounded additive MAP10 import; run only after art review and data backup."""
import json, re, shutil, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
NAME='GullSealCliffs'
def meta(p):
    m=p.with_name(p.name+'.meta')
    if not m.exists():m.write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\n')
def change(path,old,new):
    p=ROOT/path;s=p.read_text(encoding='utf-8-sig');assert s.count(old)==1,(path,'unique context');p.write_text(s.replace(old,new))
def prepare():
    p=ROOT/'Assets/Scripts/Game/GameData.cs';s=p.read_text();assert 'Name = "Seal cliffs"' not in s
    end=s.index('\n        public static readonly UpgradeDef[] Upgrades');i=s.rindex('        };',0,end)
    s=s[:i]+'''            new()
            {
                Name = "Seal cliffs", Blurb = "Cliffs, a sea arch and seals on the stones. Wrasse in the pool, cod in the race.", RowSeconds = 36f, BiteWait = 1.5f, Water = Palette.Hex("2A7F96"),
                ChartCost = 2600, MapPos = new Vector2(.08f, .88f),
                Table = new[] { (Species.Pollock, 70f), (Species.RedMullet, 33f), (Species.Conger, 30f), (Species.Crab, 2f), (Species.Mackerel, 40f), (Species.Herring, 30f), (Species.SeaBass, 20f), (Species.Cod, 35f), (Species.Turbot, 1f) },
            },
'''+s[i:];p.write_text(s)
    for path in ['Assets/Scripts/Game/Sea/SeaNav.cs','Assets/Scripts/Game/VoyageScenery.cs']:
        change(path,'"GullLighthouseRock", "GullWhaleShelf"','"GullLighthouseRock", "GullWhaleShelf", "GullSealCliffs"')
    pools='''            // Seal cliffs (MAP10): append without moving saved richness slots.
            new[] {
                G("arch-pool", "Arch pool", "arch", (Species.Pollock, 40f), (Species.RedMullet, 30f), (Species.Conger, 15f), (Species.Crab, 2f)),
                G("seal-cove", "Seal cove", "cove", (Species.Mackerel, 40f), (Species.Herring, 30f), (Species.SeaBass, 20f), (Species.RedMullet, 3f)),
                G("stack-race", "Stack race", "stack", (Species.Cod, 35f), (Species.Pollock, 30f), (Species.Conger, 15f), (Species.Turbot, 1f)) },
'''
    change('Assets/Scripts/Game/Data/Grounds.cs','        };\n\n        static readonly int[][] offsets;',pools+'        };\n\n        static readonly int[][] offsets;')
    source=ROOT/'Art/Models/Maps'/NAME;dest=ROOT/'Assets/Art/Models/Environment'/NAME
    dest.mkdir(parents=True,exist_ok=True);meta(dest)
    for name in [NAME+'SeaV2.fbx','navigation.json','grounds.json']:
        shutil.copy2(source/name,dest/name);target=dest/(name+'.meta')
        if not target.exists():
            old='GullWhaleShelfSeaV2.fbx' if name.endswith('.fbx') else name
            m=(ROOT/'Assets/Art/Models/Environment/GullWhaleShelf'/f'{old}.meta').read_text()
            target.write_text(re.sub(r'guid: [a-f0-9]+','guid: '+uuid.uuid4().hex,m,count=1))
    fixtures()
def fixtures():
    fixture=(ROOT/'Assets/Editor/WhaleShelfMapChecks.cs').read_text()
    # Remove historical single-map recapture entrypoint; ten-map acceptance uses Run.
    a=fixture.index('        public static void ChartHandoffAndBuild()');b=fixture.index('        public static void BuildNative()',a)
    fixture=fixture[:a]+fixture[b:]
    for a,b in [('WhaleShelfMapChecks','SealCliffsMapChecks'),('GullWhaleShelf',NAME),('MAP9','MAP10'),('Map9','Map10'),('map9','map10'),('nine maps','ten maps'),('all nine','all ten'),('nine SeaLanes','ten SeaLanes'),('nine real','ten real'),('540','600'),('27 lanes','30 lanes'),('lanes = 27','lanes = 30'),('maps = 9','maps = 10'),('Length == 9','Length == 10'),('Maps[8]','Maps[9]'),('Spots[8]','Spots[9]'),('BuyChart(8)','BuyChart(9)'),('Known(8)','Known(9)'),('SelectedSpot = 8','SelectedSpot = 9'),('ForMap(8)','ForMap(9)'),('1919','2599'),('1920','2600'),('"Whale shelf"','"Seal cliffs"'),('RowSeconds == 34f','RowSeconds == 36f'),('herring-shoals','arch-pool'),('shelf-edge','seal-cove'),('whale-road','stack-race')]:fixture=fixture.replace(a,b)
    # The accepted MAP9-only open-water exception stays on MAP9.
    fixture=fixture.replace('if (map != "GullSealCliffs")','if (map != "GullWhaleShelf")')
    a=fixture.index('                string[] anchorNames =');b=fixture.index('                for (int i = 0; i < anchorNames.Length;',a)
    anchors=json.loads((ROOT/'Art/Models/Maps'/NAME/'navigation.json').read_text())['lifeAnchors']
    names=', '.join('"'+x['id']+'"' for x in anchors)
    pos=', '.join('new Vector3('+','.join(f'{p:.7f}f' for p in x['position'])+')' for x in anchors)
    fixture=fixture[:a]+f'                string[] anchorNames = {{ {names} }};\n                var expected = new[] {{ {pos} }};\n'+fixture[b:]
    a=fixture.index('            var expectedPools = new[] {');b=fixture.index('            for (int i=0;i<3;i++)',a)
    fixture=fixture[:a]+'''            var expectedPools = new[] {
                new[] { (Species.Pollock,40f),(Species.RedMullet,30f),(Species.Conger,15f),(Species.Crab,2f) },
                new[] { (Species.Mackerel,40f),(Species.Herring,30f),(Species.SeaBass,20f),(Species.RedMullet,3f) },
                new[] { (Species.Cod,35f),(Species.Pollock,30f),(Species.Conger,15f),(Species.Turbot,1f) } };
'''+fixture[b:]
    fixture=fixture.replace('Runtime gannets/whale spouts/gulls/buoy life','Runtime seals/gulls/spray life')
    p=ROOT/'Assets/Editor/SealCliffsMapChecks.cs';p.write_text(fixture);meta(p)
    capture=(ROOT/'Assets/Scripts/Game/Map9Capture.cs').read_text()
    for a,b in [('Map9','Map10'),('MAP9','MAP10'),('map9','map10'),('chartFocus = 8','chartFocus = 9'),('Known(8)','Known(9)'),('SelectedSpot != 8','SelectedSpot != 9'),('1920','2600'),('herring-shoals','arch-pool'),('Herring shoals','Arch pool'),('shelf-edge','seal-cove'),('whale-road','stack-race')]:capture=capture.replace(a,b)
    p=ROOT/'Assets/Scripts/Game/Map10Capture.cs';p.write_text(capture);meta(p)
    print('MAP10 additive import/data/fixtures prepared; runtime UNVERIFIED')
if __name__=='__main__':prepare()

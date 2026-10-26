"""Additive MAP9 import and bounded data edits; refuse an already appended map."""
import json,re,shutil,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
NAME='GullWhaleShelf'
def meta(p):
    target=p.with_name(p.name+'.meta')
    if not target.exists():target.write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\n')
def change(path,old,new):
    p=ROOT/path;s=p.read_text(encoding='utf-8-sig');assert s.count(old)==1,(path,'unique context');p.write_text(s.replace(old,new))
POOLS='''            // Whale shelf (MAP9): append without moving saved richness slots.
            new[] {
                G("herring-shoals", "Herring shoals", "shoals", (Species.Herring, 50f), (Species.Mackerel, 35f), (Species.Whiting, 12f), (Species.FlyingFish, 2f)),
                G("shelf-edge", "Shelf edge", "shelf", (Species.Cod, 30f), (Species.Pollock, 30f), (Species.Conger, 20f), (Species.Turbot, 10f), (Species.AbyssalGreatWhite, 1f)),
                G("whale-road", "Whale road", "whales", (Species.Mackerel, 35f), (Species.SeaBass, 25f), (Species.Pollock, 20f), (Species.SpottedEagleRay, 3f)) },
'''
def prepare():
    p=ROOT/'Assets/Scripts/Game/GameData.cs';s=p.read_text();assert 'Name = "Whale shelf"' not in s
    end=s.index('\n        public static readonly UpgradeDef[] Upgrades');i=s.rindex('        };',0,end)
    s=s[:i]+'''            new()
            {
                Name = "Whale shelf", Blurb = "Out where the shelf drops away. Herring shoals, cod on the edge, whales passing through.", RowSeconds = 34f, BiteWait = 1.5f, Water = Palette.Hex("2A7F96"),
                ChartCost = 1920, MapPos = new Vector2(.88f, .04f),
                Table = new[] { (Species.Herring, 50f), (Species.Mackerel, 70f), (Species.Whiting, 12f), (Species.FlyingFish, 2f), (Species.Cod, 30f), (Species.Pollock, 50f), (Species.Conger, 20f), (Species.Turbot, 10f), (Species.AbyssalGreatWhite, 1f), (Species.SeaBass, 25f), (Species.SpottedEagleRay, 3f) },
            },
'''+s[i:];p.write_text(s)
    for path in ['Assets/Scripts/Game/Sea/SeaNav.cs','Assets/Scripts/Game/VoyageScenery.cs']:
        change(path,'"GullWreckBank", "GullLighthouseRock"','"GullWreckBank", "GullLighthouseRock", "GullWhaleShelf"')
    change('Assets/Scripts/Game/Data/Grounds.cs','        };\n\n        static readonly int[][] offsets;',POOLS+'        };\n\n        static readonly int[][] offsets;')
    import_art();fixtures()
def import_art():
    source=ROOT/'Art/Models/Maps'/NAME;dest=ROOT/'Assets/Art/Models/Environment'/NAME
    dest.mkdir(parents=True,exist_ok=True);meta(dest)
    for name in [NAME+'SeaV2.fbx','navigation.json','grounds.json']:
        shutil.copy2(source/name,dest/name)
        target=dest/(name+'.meta')
        if not target.exists():
            old='GullLighthouseRockSeaV2.fbx' if name.endswith('.fbx') else name
            m=(ROOT/'Assets/Art/Models/Environment/GullLighthouseRock'/f'{old}.meta').read_text()
            target.write_text(re.sub(r'guid: [a-f0-9]+','guid: '+uuid.uuid4().hex,m,count=1))
def fixtures():
    fixture=(ROOT/'Assets/Editor/LighthouseRockMapChecks.cs').read_text()
    first=fixture.index('        // The chart point landed')
    last=fixture.index('        static string NewGroundTrip',first)
    fixture=fixture[:first]+fixture[last:]
    first=fixture.index('                Check(UnityEngine.Object.FindObjectsByType<PuffinLife>')
    last=fixture.index('                var rod =',first)
    fixture=fixture[:first]+fixture[last:]
    for a,b in [('LighthouseRockMapChecks','WhaleShelfMapChecks'),('GullLighthouseRock',NAME),('MAP8','MAP9'),('Map8','Map9'),('map8','map9'),('eight maps','nine maps'),('eight SeaLanes','nine SeaLanes'),('480','540'),('24 lanes','27 lanes'),('lanes = 24','lanes = 27'),('maps = 8','maps = 9'),('Length == 8','Length == 9'),('Maps[7]','Maps[8]'),('Spots[7]','Spots[8]'),('BuyChart(7)','BuyChart(8)'),('Known(7)','Known(8)'),('SelectedSpot = 7','SelectedSpot = 8'),('ForMap(7)','ForMap(8)'),('1369','1919'),('1370','1920'),('"Lighthouse rock"','"Whale shelf"'),('RowSeconds == 30f','RowSeconds == 34f'),('BiteWait == 1.4f','BiteWait == 1.5f'),('the-pinnacle','herring-shoals'),('tide-race','shelf-edge'),('deep-ledge','whale-road')]:fixture=fixture.replace(a,b)
    first=fixture.index('                string[] anchorNames =');last=fixture.index('                for (int i = 0; i < anchorNames.Length;',first)
    anchors=json.loads((ROOT/'Art/Models/Maps'/NAME/'navigation.json').read_text())['lifeAnchors']
    names=', '.join('"'+a['id']+'"' for a in anchors)
    pos=', '.join('new Vector3('+','.join(f'{p:.7f}f' for p in a['position'])+')' for a in anchors)
    fixture=fixture[:first]+f'                string[] anchorNames = {{ {names} }};\n                var expected = new[] {{ {pos} }};\n'+fixture[last:]
    first=fixture.index('            var expectedPools = new[] {');last=fixture.index('            for (int i=0;i<3;i++)',first)
    fixture=fixture[:first]+'''            var expectedPools = new[] {
                new[] { (Species.Herring,50f),(Species.Mackerel,35f),(Species.Whiting,12f),(Species.FlyingFish,2f) },
                new[] { (Species.Cod,30f),(Species.Pollock,30f),(Species.Conger,20f),(Species.Turbot,10f),(Species.AbyssalGreatWhite,1f) },
                new[] { (Species.Mackerel,35f),(Species.SeaBass,25f),(Species.Pollock,20f),(Species.SpottedEagleRay,3f) } };
'''+fixture[last:]
    fixture=fixture.replace('Runtime puffins/tide race/lighthouse glow/buoy life','Runtime gannets/whale spouts/gulls/buoy life')
    p=ROOT/'Assets/Editor/WhaleShelfMapChecks.cs';p.write_text(fixture);meta(p)
    capture=(ROOT/'Assets/Scripts/Game/Map8Capture.cs').read_text()
    for a,b in [('Map8','Map9'),('MAP8','MAP9'),('map8','map9'),('chartFocus = 7','chartFocus = 8'),('Known(7)','Known(8)'),('SelectedSpot != 7','SelectedSpot != 8'),('1370','1920'),('the-pinnacle','herring-shoals'),('The pinnacle','Herring shoals'),('tide-race','shelf-edge'),('deep-ledge','whale-road')]:capture=capture.replace(a,b)
    p=ROOT/'Assets/Scripts/Game/Map9Capture.cs';p.write_text(capture);meta(p)
    print('MAP9 import/data/fixtures prepared; runtime UNVERIFIED')
if __name__=='__main__':prepare()


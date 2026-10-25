"""Additive MAP8 data/fixtures/import preparation; run once after the art review."""
import json, re, shutil, uuid, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def change(path,old,new):
    p=ROOT/path;s=p.read_text(encoding='utf-8-sig')
    assert s.count(old)==1,(path,'expected unique edit context')
    p.write_text(s.replace(old,new),encoding='utf-8')
def meta(p):
    if p.with_name(p.name+'.meta').exists():return
    p.with_name(p.name+'.meta').write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\n',encoding='utf-8')
def prepare():
    p=ROOT/'Assets/Scripts/Game/GameData.cs';s=p.read_text()
    end=s.index('\n        public static readonly UpgradeDef[] Upgrades')
    before=s[:end];tail=s[end:];i=before.rindex('        };')
    before=before[:i]+'''            new()
            {
                Name = "Lighthouse rock", Blurb = "A lighthouse on a lone rock. Bass in the tide race, cod and monkfish down the ledge.", RowSeconds = 30f, BiteWait = 1.4f, Water = Palette.Hex("1F5F8C"),
                ChartCost = 1370, MapPos = new Vector2(.85f, .08f),
                Table = new[] { (Species.Pollock, 40f), (Species.SeaBass, 65f), (Species.Conger, 20f), (Species.GoldTipShark, 1f), (Species.Mackerel, 45f), (Species.YellowfinTuna, 3f), (Species.Cod, 35f), (Species.Monkfish, 30f), (Species.Turbot, 10f), (Species.AtlanticSwordfish, 1f) },
            },
'''+before[i:]
    assert s.count('Name = "Lighthouse rock"')==0
    p.write_text(before+tail)
    for path in ['Assets/Scripts/Game/Sea/SeaNav.cs','Assets/Scripts/Game/VoyageScenery.cs']:
        change(path,'"GullSkerries", "GullWreckBank"','"GullSkerries", "GullWreckBank", "GullLighthouseRock"')
    change('Assets/Scripts/Game/Data/Grounds.cs','''        };

        static readonly int[][] offsets;''','''            // Lighthouse rock (MAP8). Preserve all prior map richness slots.
            new[] {
                G("the-pinnacle", "The pinnacle", "pinnacle", (Species.Pollock, 40f), (Species.SeaBass, 30f), (Species.Conger, 20f), (Species.GoldTipShark, 1f)),
                G("tide-race", "Tide race", "race", (Species.Mackerel, 45f), (Species.SeaBass, 35f), (Species.YellowfinTuna, 3f)),
                G("deep-ledge", "Deep ledge", "ledge", (Species.Cod, 35f), (Species.Monkfish, 30f), (Species.Turbot, 10f), (Species.AtlanticSwordfish, 1f)) },
        };

        static readonly int[][] offsets;''')
    source=ROOT/'Art/Models/Maps/GullLighthouseRock';dest=ROOT/'Assets/Art/Models/Environment/GullLighthouseRock'
    dest.mkdir(parents=True,exist_ok=True);meta(dest)
    for name in ['GullLighthouseRockSeaV2.fbx','navigation.json','grounds.json']:
        shutil.copy2(source/name,dest/name)
        old='GullWreckBankSeaV2.fbx' if name.endswith('.fbx') else 'navigation.json'
        m=(ROOT/'Assets/Art/Models/Environment/GullWreckBank'/f'{old}.meta').read_text()
        (dest/(name+'.meta')).write_text(re.sub(r'guid: [a-f0-9]+','guid: '+uuid.uuid4().hex,m,count=1))
    fixtures(source)

def fixtures(source):
    fixture=(ROOT/'Assets/Editor/WreckBankMapChecks.cs').read_text()
    start=fixture.index('        // Claude changed spot6')
    stop=fixture.index('        static string NewGroundTrip',start)
    fixture=fixture[:start]+fixture[stop:]
    fixture=fixture.replace('WreckBankMapChecks','LighthouseRockMapChecks').replace('GullWreckBank','GullLighthouseRock').replace('MAP7','MAP8').replace('Map7','Map8').replace('map7','map8')
    fixture=fixture.replace('== 7 && GameData.Spots.Length == 7 && SeaNav.Maps[6]','== 8 && GameData.Spots.Length == 8 && SeaNav.Maps[7]')
    fixture=fixture.replace('seven maps','eight maps').replace('seven SeaLanes','eight SeaLanes').replace('maps = 7','maps = 8').replace('hullRoutes = 420','hullRoutes = 480').replace('lanes = 21','lanes = 24').replace('420 hull routes, 21 lanes','480 hull routes, 24 lanes')
    fixture=fixture.replace('GameData.Spots[6]','GameData.Spots[7]').replace('spot.Name == "Wreck bank" && spot.RowSeconds == 26f && spot.BiteWait == 1.3f && Mathf.Approximately(spot.ChartCost, GameData.Spots[5].ChartCost * 1.4f)','spot.Name == "Lighthouse rock" && spot.RowSeconds == 30f && spot.BiteWait == 1.4f && spot.ChartCost == 1370')
    fixture=fixture.replace('Coins = 979','Coins = 1369').replace('Coins == 979','Coins == 1369').replace('Coins = 980','Coins = 1370').replace('980-coin','1370-coin').replace('BuyChart(6)','BuyChart(7)').replace('Known(6)','Known(7)').replace('SelectedSpot = 6','SelectedSpot = 7').replace('Grounds.ForMap(6)','Grounds.ForMap(7)')
    for a,b in [('the-wreck','the-pinnacle'),('herring-bank','tide-race'),('sand-edge','deep-ledge')]:fixture=fixture.replace(a,b)
    first=fixture.index('                string[] anchorNames =')
    last=fixture.index('                for (int i = 0; i < anchorNames.Length;',first)
    nav=json.loads((source/'navigation.json').read_text());anchors=nav['lifeAnchors']
    names=', '.join('"'+a['id']+'"' for a in anchors)
    pos=', '.join('new Vector3('+','.join(f'{p:.7f}f' for p in a['position'])+')' for a in anchors)
    fixture=fixture[:first]+f'                string[] anchorNames = {{ {names} }};\n                var expected = new[] {{ {pos} }};\n'+fixture[last:]
    first=fixture.index('            var expectedPools = new[] {')
    last=fixture.index('            for (int i=0;i<3;i++)',first)
    fixture=fixture[:first]+'''            var expectedPools = new[] {
                new[] { (Species.Pollock,40f),(Species.SeaBass,30f),(Species.Conger,20f),(Species.GoldTipShark,1f) },
                new[] { (Species.Mackerel,45f),(Species.SeaBass,35f),(Species.YellowfinTuna,3f) },
                new[] { (Species.Cod,35f),(Species.Monkfish,30f),(Species.Turbot,10f),(Species.AtlanticSwordfish,1f) } };
'''+fixture[last:]
    # The optional MAP7-only post-life component block is absent from this fixture.
    first=fixture.index('                if (requireLife)')
    last=fixture.index('                var rod =',first)
    fixture=fixture[:first]+fixture[last:]
    fixture=fixture.replace('string id, bool requireLife = false','string id')
    fixture=fixture.replace('Runtime gulls/gannets/buoy life','Runtime puffins/tide race/lighthouse glow/buoy life')
    p=ROOT/'Assets/Editor/LighthouseRockMapChecks.cs';p.write_text(fixture);meta(p)
    capture=(ROOT/'Assets/Scripts/Game/Map7Capture.cs').read_text()
    capture=capture.replace('Map7','Map8').replace('MAP7','MAP8').replace('map7','map8').replace('chartFocus = 6','chartFocus = 7').replace('Known(6)','Known(7)').replace('SelectedSpot != 6','SelectedSpot != 7').replace('980-coin','1370-coin')
    for a,b in [('the-wreck','the-pinnacle'),('The wreck','The pinnacle'),('herring-bank','tide-race'),('sand-edge','deep-ledge')]:capture=capture.replace(a,b)
    p=ROOT/'Assets/Scripts/Game/Map8Capture.cs';p.write_text(capture);meta(p)
    print('MAP8 additive data/import/fixtures prepared; compile/runtime UNVERIFIED')
if __name__=='__main__':
    if '--fixtures' in sys.argv:
        meta(ROOT/'Assets/Art/Models/Environment/GullLighthouseRock/grounds.json')
        fixtures(ROOT/'Art/Models/Maps/GullLighthouseRock')
    else:prepare()

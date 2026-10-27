from pathlib import Path
import re,shutil
base=Path('Assets/Scripts/Game');backup=Path('../Catchline-sim/Backups/jig-boat-before')
with Path('comms.md').open('a',encoding='utf-8') as f:f.write('''\nCHECKPOINT / JIG-BOAT-WIRE-1 A VERIFIED / Codex 1: scratch native measurement wrapper0/Unity0; jig-native-measure.txt records all43 meshes with transformed bounds. Hull7x3.336m; cabin x[-2.69,-1.21] z[-.65,.65], hatch x[.075,1.025] z[-.34,.34], reels three at x[-.3,.055]/[.9,1.255]/[2.07,2.425], z[1.24,1.681]. B IN PROGRESS.\nUPDATE / JIG-BOAT-WIRE-1 dependency scope / Codex 1: the brief explicitly requires EVERY ladder comparison converted. To fulfil that instruction, extend reservation only to minimal tier substitutions in CatchExpectation.cs,DeepLineRules.cs,VoyageCards.cs,VoyageCrabPots.cs; VoyageNet.cs only Jig basket coordinate; Assets/Editor/CardPacingSim.cs only new step/report; new flat JigBoatV1.stations.json/meta (ArtImport discovers flat station files). No held Claude UI/capture/time files edited. Prior QUESTION records this discovered dependency, this UPDATE makes expansion explicit.\n''')
changes=[]
def edit(name,fn):
 p=base/name;s=p.read_text(encoding='utf-8-sig');old=s;n=fn(s)
 if n==s:return
 dst=backup/p;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(p,dst)
 p.write_text(n,encoding='utf-8')
 # full old/new changed lines captured for REPORT later
 import difflib
 changes.append((str(p),''.join(difflib.unified_diff(old.splitlines(True),n.splitlines(True),fromfile='before',tofile='after'))))
def subs(s, pairs):
 for a,b in pairs:
  if a not in s:raise Exception('missing '+a[:80])
  s=s.replace(a,b)
 return s
edit('GameData.cs',lambda s:subs(s,[('public static int MinimumHull(Species s) => s switch','public static int MinimumHull(Species s) => s switch'),('Species.Crab => 4,','Species.Crab => 5,'),('Species.GiantSquid => 3,','Species.GiantSquid => 4,'),('public static readonly HullDef[] Hulls =','// Saved IDs remain append-only; tiers describe progression, never save identity.\n        public static int HullTier(int hullId) => hullId switch { 0 => 0, 1 => 1, 2 => 2, 3 => 4, 4 => 5, 5 => 3, _ => 0 };\n\n        public static readonly HullDef[] Hulls ='),('        // Legacy pack constants retained', '        // Legacy pack constants retained')]).replace('        };\n\n        // Legacy pack constants', '''            // Appended saved ID 5: Jig slots measured from the native imported FBX, bow -X.
            new() { Name = "Jig boat", Model = "JigBoatV1", SailSpeed = 10f, Width = 61, Height = 25, CellSize = .1f,
                Capacity = 130, CrewCap = 5, TravelMultiplier = .5f,
                Hold = new(36,12), HoldAccess = new(36,5), Seat = new(20,12), Rest = new(28,5), NetAccess = new(56,5),
                CrewRest = new[] { new Vector2Int(28,5), new Vector2Int(43,12), new Vector2Int(18,21), new Vector2Int(45,20), new Vector2Int(53,12) },
                Blocked = System.Array.Empty<Vector2Int>(),
                RodTiles = new[] { new Vector2Int(29,20), new Vector2Int(41,20), new Vector2Int(52,20) },
                RodBases = new[] { new Vector3(2.88f,.64f,2.7f), new Vector3(4.08f,.64f,2.7f), new Vector3(5.25f,.64f,2.7f) } },
        };

        // Legacy pack constants'''))
# Convert comparisons inside released scope; equality 3/4 means Prep/Buoy tier4/5 except explicit layout selectors.
for name in ['GameState.cs','GameStateProgression.cs','GameStateBoatModules.cs','GameStateTier5.cs','VoyageCompactFisher.cs','VoyagePrepFisher.cs','VoyageGame.cs','VoyageInterfaceShop.cs','VoyageManagement.cs','VoyageManagementForecast.cs','VoyageCards.cs','VoyageCrabPots.cs']:
 def convert(s):
  def cv(m):
   prefix,op,num=m.groups(); n=int(num);return prefix.replace('Hull','Tier')+op+str(n+1 if n>=3 else n)
  s=re.sub(r'((?:State\.)?Hull)(\s*(?:>=|<=|==|!=|>|<)\s*)([0-4])\b',cv,s)
  s=s.replace('Hull >= GameData.MinimumHull','Tier >= GameData.MinimumHull').replace('Hull < GameData.MinimumHull','Tier < GameData.MinimumHull')
  s=s.replace('State.Hull is 2 or 3','State.Tier is 2 or 3 or 4')
  return s
 edit(name,convert)
edit('GameState.cs',lambda s:s.replace('public HullDef HullDef =>','public int Tier => GameData.HullTier(Hull);\n        public HullDef HullDef =>'))
edit('GameStateCards.cs',lambda s:s.replace('public int CardTier => Hull >= 3 ? Hull + 1 : Hull;','public int CardTier => Tier;'))
edit('GameStateProgression.cs',lambda s:subs(s,[('CanRefitPrep => Tier == 2','CanRefitPrep => Tier == 3'),('        public const int PrepFisherCost', '''        public const int JigBoatCost = 6500;
        public bool CanRefitJig => Tier == 2 && Coins >= JigBoatCost;
        public bool RefitJig()
        {
            if (!CanRefitJig) return false;
            Coins -= JigBoatCost; Hull = 5; Fuel = FuelCapacity;
            EnsureCrewRoleOffers(); return true;
        }
        public const int PrepFisherCost''')]))
edit('CatchExpectation.cs',lambda s:s.replace('state.Hull<GameData.MinimumHull','state.Tier<GameData.MinimumHull').replace('hull<GameData.MinimumHull','GameData.HullTier(hull)<GameData.MinimumHull'))
edit('DeepLineRules.cs',lambda s:s.replace('state.Hull<GameData.MinimumHull','state.Tier<GameData.MinimumHull'))
edit('Data/Coasts.cs',lambda s:s.replace('hull >= OuterMinimumHull','GameData.HullTier(hull) >= GameData.HullTier(OuterMinimumHull)'))
edit('VoyageHarbour.cs',lambda s:s.replace('=> hull switch { 0 => Berth.Slipway, 1 => Berth.Pontoon, 2 or 3 => Berth.FishQuay, _ => Berth.OuterWharf }','=> GameData.HullTier(hull) switch { 0 => Berth.Slipway, 1 => Berth.Pontoon, 2 or 3 or 4 => Berth.FishQuay, _ => Berth.OuterWharf }').replace('int hull = State.Hull;','int hull = State.Tier;').replace('hull >= 4','hull >= 5').replace('hull >= 3','hull >= 4').replace('for (int h = 0; h < State.Hull; h++)','for (int h = 0; h < GameData.Hulls.Length; h++)').replace('                var def = GameData.Hulls[h];','                if (GameData.HullTier(h) >= State.Tier) continue;\n                var def = GameData.Hulls[h];'))
edit('VoyageInterfaceShop.cs',lambda s:subs(s,[('"module/second-net" =>','"refit/jig" => "v2-item-hull-jig",\n                "module/second-net" =>'),('string own = "v2-item-hull" + State.Hull;','string own = State.Hull == 5 ? "v2-item-hull-jig" : "v2-item-hull" + State.Hull;'),('if (State.Tier == 2) Product("refit/prep"','if (State.Tier == 3) Product("refit/prep"'),('"Tier 3 · 100 kg hold','"Tier 2 · 100 kg hold'),('            if (State.Tier == 3) Product("refit/prep"','            if (State.Tier == 2) Product("refit/jig", "Jig boat · Tier 3", "130 kg hold · five crew berths · three jig reels · squid lamps. Your crew and upgrades transfer.", "icon-skiff", $"Refit / {GameState.JigBoatCost:N0} coins", State.CanRefitJig, () => RefitJig());\n            if (State.Tier == 3) Product("refit/prep"')]))
edit('VoyageCompactFisher.cs',lambda s:s.replace('            if (IsPrepFisher) ConfigurePrepFisher(model);','            if (IsJigBoat) ConfigureJigBoat(model);\n            if (IsPrepFisher) ConfigurePrepFisher(model);').replace('if (!IsPrepFisher && native.x','if (!IsPrepFisher && !IsJigBoat && native.x').replace('                    // The low net basket','                    if (IsJigBoat && local.x > 2.795f && local.x < 4.305f && local.z > .58f && local.z < 1.82f) blocked = true;\n                    // The low net basket'))
edit('VoyageGame.cs',lambda s:s.replace('            UpdateHarbourDusk(frameDt);','            UpdateHarbourDusk(frameDt);\n            UpdateJigLamps();'))
edit('VoyageNet.cs',lambda s:s.replace('Vector3 NetBasketLocal => IsTier5','Vector3 NetBasketLocal => IsJigBoat ? new(5.9f,.14f,.9f) : IsTier5'))
out=Path('docs/screens/jig-boat-1');out.mkdir(parents=True,exist_ok=True)
(out/'comparison-changes.diff').write_text('\n'.join(p+'\n'+d for p,d in changes),encoding='utf-8')
shutil.copy2('../Catchline-sim/Logs/jig-native-measure.txt',out/'native-measure.txt')

using System.Collections.Generic;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public enum NetState { Stowed, Setting, Soaking, Ready, Hauling }
        public NetState Net { get; private set; }
        public int NetCatch => netFish.Count;
        public float NetRemaining => Mathf.Max(0f, netSoak - netTime);
        readonly List<(Species species, float kg)> netFish = new();
        float netSoak, netTime, netNextCatch;
        Transform netFloats, winchCrank, netDrum;
        LineRenderer[] netTowLines;
        float netTowStern, netTowFront, netTowHalfWidth;
        Person netWorker;
        int netClaim;
        public int NetBasketCount => UsesDeckGraph ? DeckGraph.OfKind(Deck.StationKind.Net).Sum(s => s.Out?.Count ?? 0) : OnDeck.FindAll(f => f.FromNetBasket).Count;
        public bool NetBasketBlocked => NetBasketCount > 0;
        Vector2Int NetAccess => IsTier5 && tier5RearNetAccess.HasValue ? tier5RearNetAccess.Value : IsNetFisher ? State.HullDef.NetAccess : new(3, 1);
        Vector3 NetBasketLocal => IsTier5 ? Grid.GetLocal(NetAccess)+new Vector3(.55f,.14f,0) : IsPrepFisher ? new(5.65f, .14f, 1.6f) : new(4.2f, .14f, 1.15f);

        void BuildNetKit()
        {
            if (State.Hull == 0) return;
            winchCrank = netDrum = null;
            var lib = ArtLibrary.Get();
            if (IsNetFisher)
            {
                winchCrank = netModelRoot == null ? null : ArtLibrary.Find(netModelRoot.gameObject, "NetCrank");
                netDrum = netModelRoot == null ? null : ArtLibrary.Find(netModelRoot.gameObject, "NetDrum");
                var basket = new GameObject("Net catch basket").transform;
                basket.SetParent(Boat, false);
                basket.localPosition = new Vector3(NetBasketLocal.x, .015f, NetBasketLocal.z);
                Visuals.Box("Basket floor", basket, Vector3.zero, new Vector3(.36f, .025f, .48f), Palette.DeckWoodDark);
                for (int side = -1; side <= 1; side += 2)
                {
                    Visuals.Box("Basket rim", basket, new Vector3(side * .18f, .08f, 0), new Vector3(.025f, .16f, .48f), Palette.DeckWood);
                    Visuals.Box("Basket rim", basket, new Vector3(0, .08f, side * .24f), new Vector3(.36f, .16f, .025f), Palette.DeckWood);
                }
            }
            else
            {
                var winch = ArtLibrary.Spawn(lib?.M("HandWinch"), Boat, new Vector3(4f, 0f, 1f), Quaternion.Euler(0f, 90f, 0f));
                if (winch != null) winchCrank = ArtLibrary.Find(winch, "Crank");
                else Visuals.Box("HandWinch", Boat, new Vector3(4f, .25f, 1f), new Vector3(.6f, .5f, .6f), Palette.Steel);
                ArtLibrary.Spawn(lib?.M("GillNetCoil"), Boat, new Vector3(3f, 0f, 2.32f), Quaternion.identity);
            }
            netFloats = new GameObject("Gill net in water").transform;
            netTowLines = null;
            netFloats.SetParent(world, false);
            for (int i = 0; i < 2; i++)
            {
                var position = IsNetFisher ? Grid.GetLocal(NetAccess) + new Vector3(.8f + i * .9f, -.30f, -.9f) : new Vector3(4.5f + i * 2f, -.30f, -.9f);
                var floats = ArtLibrary.Spawn(lib?.M("GillNetFloatLine"), netFloats, position, Quaternion.identity);
                ArtLibrary.Spawn(lib?.M("GillNetSection"), netFloats, position, Quaternion.identity);
                if (floats == null)
                    for (int f = 0; f < 4; f++) Visuals.Prim(PrimitiveType.Sphere, "Net float", netFloats, position + Vector3.right * (f * .5f - .75f), Vector3.one * .15f, Palette.Accent);
            }
            if (IsNetFisher) PositionNetBehindStern();
            netFloats.gameObject.SetActive(false);
        }

        static Bounds NetMeshBounds(Transform source, Transform frame)
        {
            Bounds result = new(); bool first = true;
            foreach (var mf in source.GetComponentsInChildren<MeshFilter>())
            {
                if (mf.sharedMesh == null) continue;
                var b = mf.sharedMesh.bounds; var m = frame.worldToLocalMatrix * mf.transform.localToWorldMatrix;
                for (int i = 0; i < 8; i++)
                {
                    var p = m.MultiplyPoint3x4(b.center + Vector3.Scale(b.extents,
                        new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                    if (first) { result = new Bounds(p, Vector3.zero); first = false; } else result.Encapsulate(p);
                }
            }
            return result;
        }
        void PositionNetBehindStern()
        {
            // Bow is -X. Centre the floating gear behind +X, not beside the rail.
            var hull = NetMeshBounds(netModelRoot != null ? netModelRoot : Boat, Boat);
            var gear = NetMeshBounds(netFloats, world);
            // The delivered panels are large enough to cover the whole boat.
            // Keep this small stationary net readable behind the compact fisher.
            float scale = Mathf.Min(1f, 2.2f / Mathf.Max(.01f, gear.size.x), 1.35f / Mathf.Max(.01f, gear.size.z));
            foreach (Transform child in netFloats)
            {
                child.localPosition = gear.center + (child.localPosition - gear.center) * scale;
                child.localScale *= scale;
            }
            gear = NetMeshBounds(netFloats, world);
            netTowStern = hull.max.x;
            var shift = new Vector3(netTowStern + .65f - gear.min.x, 0, State.HullDef.Center.z - gear.center.z);
            foreach (Transform child in netFloats) child.localPosition += shift;
            gear = NetMeshBounds(netFloats, world);
            netTowFront = gear.min.x; netTowHalfWidth = gear.extents.z * .7f;
            netTowLines = new LineRenderer[2];
            for (int i = 0; i < 2; i++)
            {
                var line = new GameObject("Stern net rope " + i).AddComponent<LineRenderer>();
                line.transform.SetParent(netFloats, false); line.useWorldSpace = true;
                line.positionCount = 2; line.startWidth = line.endWidth = .018f;
                line.sharedMaterial = Visuals.Mat(Palette.Hex("BBA47A"));
                netTowLines[i] = line;
            }
            UpdateNetTowLines();
        }
        void UpdateNetTowLines()
        {
            if (netTowLines == null) return;
            for (int i = 0; i < 2; i++)
            {
                float side = i == 0 ? -1 : 1;
                netTowLines[i].SetPosition(0, Boat.TransformPoint(new Vector3(netTowStern, .02f, State.HullDef.Center.z + side * .3f)));
                netTowLines[i].SetPosition(1, netFloats.TransformPoint(new Vector3(netTowFront, WaterY + .06f, State.HullDef.Center.z + side * netTowHalfWidth)));
            }
        }

        public bool CanWorkNet => CurrentMode == Mode.Fishing && AtFishingGround && State.Hull > 0 && Captain.Idle && Captain.Carrying == null && Manning == null
            && (Net == NetState.Ready || !NetBasketBlocked && !HoldFull);

        public bool SetNet() => CanWorkNet && Net == NetState.Stowed && StartCompactNet(Captain, false);
        public bool HaulNet() => CanWorkNet && Net == NetState.Ready && StartCompactNet(Captain, true);

        void TickNet(float dt)
        {
            if (State.Hull == 0) return;
            bool settingGame = NetGameActive && netGameRig == 0 && NetGameSetting;
            TickNetHaulGame(dt);
            if (settingGame && Net == NetState.Soaking) return;
            float winchDrive = NetGameActive ? NetGameHeld && NetGameTension < NetHaulRedTension ? 1f : 0f : 1f;
            if (netFloats != null && netFloats.gameObject.activeSelf)
            {
                netFloats.localPosition = new Vector3(0f, Mathf.Sin(SimTime * 1.8f) * .025f, 0f);
                UpdateNetTowLines();
            }
            if (Net == NetState.Hauling && winchCrank != null) winchCrank.Rotate(Vector3.right, dt * winchDrive * 300f, Space.Self);
            if (IsNetFisher && Net == NetState.Hauling && netDrum != null) netDrum.Rotate(Vector3.right, dt * winchDrive * 100f, Space.Self);
            if (Net != NetState.Soaking) return;
            netTime = Mathf.Min(netTime + dt, netSoak);
            if (netTime >= netSoak)
            {
                RollCompactCatch(); Net = NetState.Ready;
                Toast($"Net ready: {NetCatchKg:0.0} kg. Haul it yourself or enable Nets for a fisher.");
            }
        }

        readonly Dictionary<CrewMember, int> netAssignments = new();
        bool NetOperator(CrewMember c) => c != null && (UsesDeckGraph || IsTier5
            ? c.Role == CrewRole.Fisherman && c.Allows(FisherTask.Nets)
            : c.Role == CrewRole.Deckhand);
        bool RigBasketBlocked(int rig) => UsesDeckGraph ? GearStation(Deck.StationKind.Net, rig)?.Out?.Full == true : OnDeck.Any(f=>f.FromNetBasket && f.Tile==(rig==1?SecondNetAccess:NetAccess));
        public int AssignedNet(Person person)
        {
            foreach (var crew in new List<CrewMember>(netAssignments.Keys))
                if (!State.Crew.Contains(crew) || !NetOperator(crew)
                    || netAssignments[crew] == 1 && !SecondNetActive) netAssignments.Remove(crew);
            if (person?.Contract == null || !NetOperator(person.Contract)) return -1;
            if (netAssignments.TryGetValue(person.Contract, out int rig)) return rig;
            for (rig = 0; rig < (SecondNetActive ? 2 : 1); rig++)
                if (!netAssignments.ContainsValue(rig)) { netAssignments[person.Contract] = rig; return rig; }
            return -1;
        }
        DeckFish AssignedBasket(Person person)
        {
            if(person == netUnloader && NetUnloadRig >= 0)
                return OnDeck.Find(f=>f.FromNetBasket && f.Tile==(NetUnloadRig==1?SecondNetAccess:NetAccess));
            if (person.IsCaptain || IsTier5 && person.Contract?.Role == CrewRole.Deckhand)
                return OnDeck.Find(f=>f.FromNetBasket && f.ClaimedBy==null);
            int rig=AssignedNet(person); if(rig<0)return null;
            return OnDeck.Find(f=>f.FromNetBasket && f.ClaimedBy==null && f.Tile==(rig==1?SecondNetAccess:NetAccess));
        }
        public bool TryNetWork(Person person)
        {
            if (!IsNetFisher || person == null || person.IsCaptain || !NetOperator(person.Contract)) return false;
            int rig=AssignedNet(person);
            if (rig == 0) return Net == NetState.Ready ? StartCompactNet(person,true)
                : Net == NetState.Stowed && StartCompactNet(person,false);
            return rig == 1 && (SecondNet == NetState.Ready ? StartSecondNet(person,true)
                : SecondNet == NetState.Stowed && StartSecondNet(person,false));
        }

        bool StartCompactNet(Person person, bool haul)
        {
            if (CurrentMode != Mode.Fishing || !AtFishingGround || !person.Idle || person.Carrying != null || netWorker != null)
                return false;
            if (Net != (haul ? NetState.Ready : NetState.Stowed)) return false;
            if (!haul && AvailableNetStock(0) <= 0) return false;
            if (RigBasketBlocked(0) || (!haul && HoldFull)) return false;
            netWorker = person;
            int claim = ++netClaim;
            Net = haul ? NetState.Hauling : NetState.Setting;
            bool Owns() => netClaim == claim && netWorker == person;
            void Cancel()
            {
                if (!Owns()) return;
                netWorker = null;
                netClaim++;
                Net = haul ? NetState.Ready : NetState.Stowed;
            }
            void Complete()
            {
                if (!Owns()) return;
                // One roll per full worker recovery, never one roll per stage.
                if (haul && !IsTier5 && !person.IsCaptain && State.Rng.NextDouble() >= .8) { Tear(); return; }
                netWorker = null;
                netClaim++;
                if (haul) { if (DeepNetSelected) State.SpendDeepNetUse(); FinishHaul(); if (!UsesDeckGraph && (!IsTier5 || person.IsCaptain)) BeginNetUnload(person); return; }
                Net = NetState.Soaking;
                netTime = 0f;
                netSoak = DeepNetSelected ? GameData.DeepNetSoakSeconds : GameData.ShallowNetSoakSeconds;
                netFish.Clear();
                if (netFloats != null) netFloats.gameObject.SetActive(true);
                Toast($"{(DeepNetSelected ? "Deep" : "Shallow")} net set. {netSoak:0}s soak while the crew works.");
            }
            void Tear()
            {
                if (!Owns()) return;
                bool deep = DeepNetSelected;
                if (deep) State.SpendDeepNetUse();
                else State.NetInventory = Mathf.Max(0, State.NetInventory - 1);
                ResetPrimaryNet();
                Toast(deep ? $"Deep haul lost — one use spent. {State.NetLoadoutLabel}." : $"Net torn — catch lost. {State.NetInventory} shallow nets left; replacements {GameData.NetReplacementCost} coins.");
            }
            bool walking = person.WalkTo(Grid, NetAccess, () =>
            {
                if (!Owns()) return;
                FaceNet(person);
                if (person.IsCaptain) BeginNetGame(person, !haul, Complete, Cancel, Tear);
                else person.Do(haul ? "Hauling net" : "Setting net", haul ? GameData.NetHaulTime : GameData.NetSetTime, Complete, Cancel);
            }, Cancel);
            if (!walking) Cancel();
            return walking;
        }

        void RollCompactCatch()
        {
            netFish.Clear();
            netFish.AddRange(CatchExpectation.RollNet(State.Hull,ActiveSpot,DeepNetSelected,NetWeightRange(ActiveSpot,DeepNetSelected).y,State.Rng,State.FishTable(ActiveSpot)));
            foreach(var f in netFish)State.OnCatch(ActiveSpot,f.kg,f.species,true);
        }

        static bool SmallSchool(Species species) => species == Species.Herring || species == Species.Mackerel || species == Species.Whiting || species == Species.Pollock;

        void FinishHaul()
        {
            int count = netFish.Count;
            foreach (var (species, kg) in netFish)
            {
                if (UsesDeckGraph && GearStation(Deck.StationKind.Net, 0) is { } station)
                {
                    LandOnDeck(station, species, kg);
                    RecordLanding(FlowTelemetry.Kind.Net, species, kg); Stats.Landed++;
                    continue;
                }
                var fish = new DeckFish { Species = species, Kg = kg, Tile = NetAccess, CaughtAt = SimTime, FromNetBasket = true };
                fish.Root = DeckFish.BuildModel(species, kg, Boat);
                int i = IsNetFisher ? NetBasketCount : OnDeck.Count;
                fish.RestPos = IsNetFisher ? NetBasketLocal + new Vector3((i % 2 - .5f) * .1f, (i / 2) * .012f, (i % 3 - 1) * .08f)
                    : DeckGrid.ToLocal(NetAccess) + new Vector3((i % 4 - 1.5f) * .12f, .07f, (i / 4) * .08f);
                fish.SpawnFrom = IsNetFisher ? Grid.GetLocal(NetAccess) + new Vector3(.3f, .5f, 0f) : new Vector3(4.4f, .5f, .2f);
                fish.Root.localPosition = fish.SpawnFrom;
                OnDeck.Add(fish);
                RecordLanding(FlowTelemetry.Kind.Net, species, kg);
                Stats.Landed++;
            }
            ResetPrimaryNet();
            Toast($"Hauled {count} fish. Bringing the catch into storage.");
        }

        void ResetPrimaryNet()
        {
            netClaim++;
            if (!NetGameActive || netGameRig == 0) ResetNetHaulGame();
            netWorker = null;
            Net = NetState.Stowed;
            netFish.Clear();
            netTime = 0f;
            primaryNetCycleMistakes = 0;
            if (netFloats != null) netFloats.gameObject.SetActive(false);
        }
    }
}

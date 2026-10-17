using System.Collections.Generic;
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
        public int NetBasketCount => OnDeck.FindAll(f => f.FromNetBasket).Count;
        public bool NetBasketBlocked => NetBasketCount > 0;
        Vector2Int NetAccess => IsNetFisher ? State.HullDef.NetAccess : new(3, 1);
        Vector3 NetBasketLocal => IsPrepFisher ? new(5.65f, .14f, 1.6f) : new(4.2f, .14f, 1.15f);

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

        public bool CanWorkNet => CurrentMode == Mode.Fishing && State.Hull > 0 && Captain.Idle && Captain.Carrying == null && Manning == null
            && (Net == NetState.Ready || !NetBasketBlocked && !HoldFull);

        public bool SetNet() => CanWorkNet && Net == NetState.Stowed && StartCompactNet(Captain, false);
        public bool HaulNet() => CanWorkNet && Net == NetState.Ready && StartCompactNet(Captain, true);

        void TickNet(float dt)
        {
            if (State.Hull == 0) return;
            bool settingGame = NetGameActive && NetGameSetting;
            TickNetHaulGame(dt);
            if (settingGame && Net == NetState.Soaking) return;
            float winchDrive = NetGameActive ? NetGameHeld && NetGameTension < NetHaulRedTension ? 1f : 0f : 1f;
            if (netFloats != null && netFloats.gameObject.activeSelf)
            {
                netFloats.localPosition = new Vector3(0f, Mathf.Sin(SimTime * 1.8f) * .025f, 0f);
                UpdateNetTowLines();
            }
            if (Net == NetState.Hauling && winchCrank != null) winchCrank.Rotate(Vector3.right, dt * WorkMult * winchDrive * 300f, Space.Self);
            if (IsNetFisher && Net == NetState.Hauling && netDrum != null) netDrum.Rotate(Vector3.right, dt * WorkMult * winchDrive * 100f, Space.Self);
            if (Net != NetState.Soaking) return;
            netTime = Mathf.Min(netTime + dt, netSoak);
            if (netTime >= netSoak)
            {
                RollCompactCatch(); Net = NetState.Ready;
                Toast($"Net ready: {NetCatchKg:0.0} kg. Haul it yourself or assign a deckhand.");
            }
        }

        // Only the deckhand scheduler's Nets preference calls this; soak never owns a worker.
        public bool TryNetWork(Person person)
        {
            if (!IsNetFisher || person == null || person.IsCaptain || person.Contract?.Role != CrewRole.Deckhand)
                return false;
            if (Net == NetState.Stowed) return StartCompactNet(person, false);
            return Net == NetState.Ready && StartCompactNet(person, true);
        }

        bool StartCompactNet(Person person, bool haul)
        {
            if (CurrentMode != Mode.Fishing || !person.Idle || person.Carrying != null || netWorker != null)
                return false;
            if (Net != (haul ? NetState.Ready : NetState.Stowed)) return false;
            if (!haul && State.ActiveNetStock <= 0) return false;
            if (NetBasketBlocked || (!haul && HoldFull)) return false;
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
                if (haul && !person.IsCaptain && State.Rng.NextDouble() >= .8) { Tear(); return; }
                netWorker = null;
                netClaim++;
                if (haul) { if (DeepNetSelected) State.SpendDeepNetUse(); FinishHaul(); BeginNetUnload(person); return; }
                Net = NetState.Soaking;
                netTime = 0f;
                netSoak = DeepNetSelected ? 30f : 20f;
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
                ResetNet();
                Toast(deep ? $"Deep haul lost — one use spent. {State.NetLoadoutLabel}." : $"Net torn — catch lost. {State.NetInventory} shallow nets left; replacements {GameData.NetReplacementCost} coins.");
            }
            bool walking = person.WalkTo(Grid, NetAccess, () =>
            {
                if (!Owns()) return;
                FaceNet(person);
                if (person.IsCaptain) BeginNetGame(person, !haul, Complete, Cancel, Tear);
                else person.Do(haul ? "Hauling net" : "Setting net", haul ? 5f : 2f, Complete, Cancel);
            }, Cancel);
            if (!walking) Cancel();
            return walking;
        }

        void RollCompactCatch()
        {
            netFish.Clear();
            bool large = DeepNetSelected;
            float target = NetWeightRange(ActiveSpot, large).y;
            float mass = 0;
            var table = GameData.Spots[ActiveSpot].Table;
            // Every added specimen has positive mass. The loop ends on remaining kg,
            // never a fish-count limit; a fish cannot cross the net's hard weight limit.
            while (true)
            {
                float remaining = target - mass;
                float total = 0;
                foreach (var entry in table)
                {
                    var d = GameData.Get(entry.species);
                    if (!large && !SmallSchool(entry.species)) continue;
                    float min = Mathf.Lerp(d.MinKg, d.MaxKg, large ? .65f : .05f);
                    if (min > remaining) continue;
                    total += entry.weight * (large ? .08f + 6f * d.Heaviness * d.Heaviness : 1);
                }
                if (total <= 0)
                {
                    if (large) { large = false; continue; }
                    break; // Residual smaller than any local school specimen stays empty.
                }
                float roll = (float)State.Rng.NextDouble() * total;
                Species species = table[0].species;
                foreach (var entry in table)
                {
                    var d = GameData.Get(entry.species);
                    if (!large && !SmallSchool(entry.species)) continue;
                    float min = Mathf.Lerp(d.MinKg, d.MaxKg, large ? .65f : .05f);
                    if (min > remaining) continue;
                    species = entry.species;
                    roll -= entry.weight * (large ? .08f + 6f * d.Heaviness * d.Heaviness : 1);
                    if (roll <= 0) break;
                }
                var fish = GameData.Get(species);
                float low = Mathf.Lerp(fish.MinKg, fish.MaxKg, large ? .65f : .05f);
                float high = Mathf.Min(remaining, Mathf.Lerp(fish.MinKg, fish.MaxKg, large ? 1f : .25f));
                float kg = Mathf.Lerp(low, high, (float)State.Rng.NextDouble());
                if (kg <= 0 || mass + kg > target + .00001f) break;
                netFish.Add((species, kg)); mass += kg; State.OnCatch(ActiveSpot, kg);
            }
        }

        static bool SmallSchool(Species species) => species == Species.Herring || species == Species.Mackerel || species == Species.Whiting || species == Species.Pollock;

        void FinishHaul()
        {
            int count = netFish.Count;
            foreach (var (species, kg) in netFish)
            {
                var fish = new DeckFish { Species = species, Kg = kg, Tile = NetAccess, CaughtAt = SimTime, FromNetBasket = true };
                fish.Root = DeckFish.BuildModel(species, kg, Boat);
                int i = IsNetFisher ? NetBasketCount : OnDeck.Count;
                fish.RestPos = IsNetFisher ? NetBasketLocal + new Vector3((i % 2 - .5f) * .1f, (i / 2) * .012f, (i % 3 - 1) * .08f)
                    : DeckGrid.ToLocal(NetAccess) + new Vector3((i % 4 - 1.5f) * .12f, .07f, (i / 4) * .08f);
                fish.SpawnFrom = IsNetFisher ? Grid.GetLocal(NetAccess) + new Vector3(.3f, .5f, 0f) : new Vector3(4.4f, .5f, .2f);
                fish.Root.localPosition = fish.SpawnFrom;
                OnDeck.Add(fish);
                Stats.Landed++;
            }
            ResetNet();
            Toast($"Hauled {count} fish. Bringing the catch into storage.");
        }

        void ResetNet()
        {
            ClearNetUnload();
            netClaim++;
            ResetNetHaulGame();
            netWorker = null;
            Net = NetState.Stowed;
            netFish.Clear();
            netTime = 0f;
            netCycleMistakes = 0;
            if (netFloats != null) netFloats.gameObject.SetActive(false);
        }
    }
}

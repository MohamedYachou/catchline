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
        Transform netFloats, winchCrank;
        Vector2Int NetAccess => new(3, 1);

        void BuildNetKit()
        {
            if (State.Hull == 0) return;
            var lib = ArtLibrary.Get();
            var winch = ArtLibrary.Spawn(lib?.M("HandWinch"), Boat, new Vector3(4f, 0f, 1f), Quaternion.Euler(0f, 90f, 0f));
            if (winch != null) winchCrank = ArtLibrary.Find(winch, "Crank");
            else Visuals.Box("HandWinch", Boat, new Vector3(4f, .25f, 1f), new Vector3(.6f, .5f, .6f), Palette.Steel);
            ArtLibrary.Spawn(lib?.M("GillNetCoil"), Boat, new Vector3(3f, 0f, 2.32f), Quaternion.identity);
            netFloats = new GameObject("Gill net in water").transform;
            netFloats.SetParent(world, false);
            for (int i = 0; i < 2; i++)
            {
                var position = new Vector3(4.5f + i * 2f, -.30f, -.9f);
                var floats = ArtLibrary.Spawn(lib?.M("GillNetFloatLine"), netFloats, position, Quaternion.identity);
                ArtLibrary.Spawn(lib?.M("GillNetSection"), netFloats, position, Quaternion.identity);
                if (floats == null)
                    for (int f = 0; f < 4; f++) Visuals.Prim(PrimitiveType.Sphere, "Net float", netFloats, position + Vector3.right * (f * .5f - .75f), Vector3.one * .15f, Palette.Accent);
            }
            netFloats.gameObject.SetActive(false);
        }

        public bool CanWorkNet => CurrentMode == Mode.Fishing && State.Hull > 0 && Captain.Idle && Captain.Carrying == null && Manning == null && Cooler.Count < State.CoolerCapacity;

        public bool SetNet()
        {
            if (!CanWorkNet || Net != NetState.Stowed) return false;
            Net = NetState.Setting;
            bool walking = Captain.WalkTo(Grid, NetAccess, () => Captain.Do("Setting net", 2f, () =>
            {
                Net = NetState.Soaking;
                netTime = 0f;
                netSoak = Mathf.Lerp(GameData.NetSoakMin, GameData.NetSoakMax, (float)State.Rng.NextDouble());
                netNextCatch = 4f;
                netFloats.gameObject.SetActive(true);
                Toast("Net set. Fish with the rods while it soaks.");
            }, ResetNet), ResetNet);
            if (!walking) ResetNet();
            return walking;
        }

        public bool HaulNet()
        {
            if (!CanWorkNet || Net != NetState.Ready) return false;
            Net = NetState.Hauling;
            bool walking = Captain.WalkTo(Grid, NetAccess, () => Captain.Do("Hauling net", GameData.NetHaulTime, FinishHaul, () => Net = NetState.Ready), () => Net = NetState.Ready);
            if (!walking) Net = NetState.Ready;
            return walking;
        }

        void TickNet(float dt)
        {
            if (State.Hull == 0) return;
            if (netFloats != null && netFloats.gameObject.activeSelf)
                netFloats.localPosition = new Vector3(0f, Mathf.Sin(SimTime * 1.8f) * .025f, 0f);
            if (Net == NetState.Hauling && winchCrank != null) winchCrank.Rotate(Vector3.right, dt * WorkMult * 300f, Space.Self);
            if (Net != NetState.Soaking) return;
            netTime = Mathf.Min(netTime + dt, netSoak);
            while (netTime >= netNextCatch)
            {
                // Most catches are schooling fish; bycatch reflects the selected sea.
                Species species = State.Rng.NextDouble() < .7 ? State.Rng.NextDouble() < .3 ? Species.Herring : Species.Mackerel : State.RollFish(ActiveSpot, .5f).Item1;
                var def = GameData.Get(species);
                float kg = Mathf.Lerp(def.MinKg, def.MaxKg, .3f + (float)State.Rng.NextDouble() * .5f);
                netFish.Add((species, kg));
                State.OnCatch(ActiveSpot);
                netNextCatch += Mathf.Lerp(3f, 4.5f, (float)State.Rng.NextDouble()) / Mathf.Max(.5f, State.Richness[ActiveSpot]);
            }
            if (netTime >= netSoak)
            {
                Net = NetState.Ready;
                Toast($"Net ready: {NetCatch} fish. Tap Haul net when your hands are free.");
            }
        }

        void FinishHaul()
        {
            int count = netFish.Count;
            foreach (var (species, kg) in netFish)
            {
                var fish = new DeckFish { Species = species, Kg = kg, Tile = NetAccess };
                fish.Root = DeckFish.BuildModel(species, kg, Boat);
                int i = OnDeck.Count;
                fish.RestPos = DeckGrid.ToLocal(NetAccess) + new Vector3((i % 4 - 1.5f) * .12f, .07f, (i / 4) * .08f);
                fish.SpawnFrom = new Vector3(4.4f, .5f, .2f);
                fish.Root.localPosition = fish.SpawnFrom;
                OnDeck.Add(fish);
                Stats.Landed++;
            }
            ResetNet();
            Toast($"Hauled {count} fish. Carry them to the hold before they flop away.");
        }

        void ResetNet()
        {
            Net = NetState.Stowed;
            netFish.Clear();
            netTime = 0f;
            if (netFloats != null) netFloats.gameObject.SetActive(false);
        }
    }
}

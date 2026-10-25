using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using Catchline.Prototype;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        Person netUnloader;
        readonly List<DeckFish> netUnloadBatch = new();
        public bool NetUnloadActive => netUnloader != null;
        public int NetUnloadRig { get; private set; } = -1;
        bool IsNetUnloading(Person person) => netUnloader == person;
        void BeginNetUnload(Person person)
        {
            if (netUnloader != null && netUnloader != person) return; // Existing batch keeps its owner.
            var basket = AssignedBasket(person);
            if (basket == null) return;
            NetUnloadRig = SecondNetActive && basket.Tile == SecondNetAccess ? 1 : 0;
            netUnloader = person;
            Toast($"Bringing {NetBasketCount} net fish into storage.");
        }
        void ClearNetUnload()
        {
            foreach (var fish in netUnloadBatch)
            {
                if (fish.Root == null || !OnDeck.Contains(fish)) continue;
                fish.Root.SetParent(Boat, false); fish.Root.localPosition = fish.RestPos;
                fish.ClaimedBy = null;
            }
            if (netUnloader != null) netUnloader.CarryingBatch = false;
            netUnloadBatch.Clear(); netUnloader = null; NetUnloadRig = -1;
        }

        void TickNetUnload(float dt)
        {
            if (dt <= 0 || CurrentMode != Mode.Fishing || netUnloader == null) return;
            var person = netUnloader;
            if (person.Root == null) { ClearNetUnload(); return; }
            if (!person.Idle) return;
            if (HoldFull) { ClearNetUnload(); return; }
            var basket = AssignedBasket(person);
            var ready = basket == null ? new List<DeckFish>() : OnDeck.Where(f => f.FromNetBasket
                && f.Tile == basket.Tile && f.ClaimedBy == null && f.Age >= .4f).ToList();
            if (ready.Count > 0)
            {
                if (person.Tile != ready[0].Tile)
                { person.WalkTo(Grid, ready[0].Tile, null); return; }
                foreach (var fish in ready) { fish.ClaimedBy = person; netUnloadBatch.Add(fish); }
                person.FacePoint(ready[0].RestPos);
                person.Do("Gathering net catch", GameData.NetGatherTime, () =>
                {
                    for (int i = 0; i < netUnloadBatch.Count; i++)
                    {
                        var f = netUnloadBatch[i]; f.Root.SetParent(person.Root, false);
                        f.Root.localPosition = new Vector3((i % 2 - .5f) * .13f, .55f + (i / 4) * .018f, .21f + (i % 4 / 2) * .10f);
                    }
                    person.CarryingBatch = true;
                    if (!person.WalkTo(Grid, InboundAccess, () => { if(IsPrepFisher)person.FacePoint(PrepSurfaceLocal);else FaceHold(person); person.Do("Stowing net catch", GameData.StowTime, () =>
                    {
                        var stored = new List<CaughtFish>();
                        foreach (var f in netUnloadBatch.ToArray())
                        {
                            if (HoldFull || !OnDeck.Contains(f)) continue;
                            var secured = new CaughtFish { Species = f.Species, Kg = f.Kg, StowedAt = f.CaughtAt };
                            if (!DeliverCatch(secured)) continue; stored.Add(secured);
                            OnDeck.Remove(f); Visuals.Kill(f.Root.gameObject);
                        }
                        lidPop = 1f;
                        RecordStoredNet(stored);
                        ClearNetUnload();
                    }, ClearNetUnload); }, ClearNetUnload)) ClearNetUnload();
                }, ClearNetUnload);
                return;
            }
            // A just-landed batch needs the brief drop animation before pickup.
            if (basket == null) ClearNetUnload();
        }
    }
}

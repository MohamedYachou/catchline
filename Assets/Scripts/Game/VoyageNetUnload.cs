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
        bool IsNetUnloading(Person person) => netUnloader == person;
        void BeginNetUnload(Person person)
        {
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
            netUnloadBatch.Clear(); netUnloader = null;
        }

        void TickNetUnload(float dt)
        {
            if (dt <= 0 || CurrentMode != Mode.Fishing || netUnloader == null) return;
            var person = netUnloader;
            if (person.Root == null) { ClearNetUnload(); return; }
            if (!person.Idle) return;
            if (HoldFull) { ClearNetUnload(); return; }
            var ready = OnDeck.Where(f => f.FromNetBasket && f.ClaimedBy == null && f.Age >= .4f)
                .ToList();
            if (ready.Count > 0)
            {
                foreach (var fish in ready) { fish.ClaimedBy = person; netUnloadBatch.Add(fish); }
                person.FacePoint(ready[0].RestPos);
                person.Do("Gathering net catch", 1.2f, () =>
                {
                    for (int i = 0; i < netUnloadBatch.Count; i++)
                    {
                        var f = netUnloadBatch[i]; f.Root.SetParent(person.Root, false);
                        f.Root.localPosition = new Vector3((i % 2 - .5f) * .13f, .55f + (i / 4) * .018f, .21f + (i % 4 / 2) * .10f);
                    }
                    person.CarryingBatch = true;
                    if (!person.WalkTo(Grid, CoolerAccess, () => { FaceHold(person); person.Do("Stowing net catch", 1.8f, () =>
                    {
                        var stored = new List<CaughtFish>();
                        foreach (var f in netUnloadBatch.ToArray())
                        {
                            if (HoldFull || !OnDeck.Contains(f)) continue;
                            var secured = new CaughtFish { Species = f.Species, Kg = f.Kg, StowedAt = f.CaughtAt };
                            if (!TryStore(secured)) continue; stored.Add(secured);
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
            if (!OnDeck.Any(f => f.FromNetBasket)) ClearNetUnload();
        }
    }
}

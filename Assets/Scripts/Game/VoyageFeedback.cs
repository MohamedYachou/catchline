using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // First value comes from the real voyage: cast, catch, carry, sell, improve the boat.
    public partial class VoyageGame
    {
        Species lastCatchSpecies;
        float lastCatchKg, catchUntil, stowedAt = -100f;
        bool catchNew, catchRecord;

        public bool FirstVoyage => State.Voyage == 1 && State.Hull == 0 && State.LogCount.All(n => n == 0);
        public bool LearningFishing => State.Hull == 0 && State.LogCount.Sum() + Stats.Landed < 3;
        public float StrikeWindow => LearningFishing ? Mathf.Max(1.5f, State.BiteWindow) : State.BiteWindow;

        void ResetFeedback() { catchUntil = 0f; stowedAt = -100f; }

        void ShowCatch(Species species, float kg)
        {
            lastCatchSpecies = species;
            lastCatchKg = kg;
            // The just-landed fish is already in OnDeck. Compare against earlier catches this trip too.
            var earlier = OnDeck.Where(f => f.Species == species).Select(f => f.Kg)
                .Concat(Cooler.Where(f => f.Species == species).Select(f => f.Kg))
                .Concat(People.Where(p => p.Carrying?.Species == species).Select(p => p.Carrying.Kg));
            catchNew = State.LogCount[(int)species] == 0 && earlier.Count() == 1;
            catchRecord = !catchNew && kg > State.LogBest[(int)species] && earlier.All(k => k <= kg);
            catchUntil = SimTime + 4.5f;
        }

        static string FishPortrait(Species species) => "fish-" + species.ToString().ToLowerInvariant();

        public string VoyageHint()
        {
            if (Cooler.Count >= State.CoolerCapacity) return "Cooler full! Head home to sell your catch.";
            if (Captain.Carrying != null || Captain.Busy || Captain.Walking)
                return Captain.Carrying != null ? "Taking your fish to the cooler…" : "The captain is on it…";
            if (OnDeck.Any(CanCarry)) return "Tap Carry above the fish. The captain takes it to the cooler.";
            var rod = MinigameRod;
            if (rod != null) return rod.State switch
            {
                RodState.Bite => "Bite! Tap the water or press Space now!",
                RodState.Waiting => rod.Nibbling ? "Just a nibble. Wait until the bobber goes under." : "Watch the bobber. Wait for it to go under.",
                RodState.Reeling => "Hooked! The captain reels it in for you.",
                _ => "Casting… get ready to watch the bobber.",
            };
            if (FirstVoyage && Cooler.Count >= 3) return "Three fish safely aboard! Head home to sell, or keep filling the cooler.";
            if (!State.HasAnyBait && Rods.All(r => r.State == RodState.Unbaited)) return "Out of bait. Head home; Supplies sells more.";
            if (Rods.Any(r => CanCommandRod(r) && r.InWater)) return "Tap Watch above a rod to watch its bobber.";
            return Rods.Any(CanCommandRod) ? "Tap Fish above the rod. The captain baits and casts for you." : null;
        }

        void DrawVoyageGuide()
        {
            if (!ShowTips || MinigameRod != null) return;
            var hint = VoyageHint();
            if (hint == null) return;
            float width = Mathf.Min(520f, VW - 400f);
            var r = Panel(new Rect(Mathf.Max(362f, (VW - width) / 2f), 646f, width, 58f), Ui.ToastStyle);
            GUI.Label(new Rect(r.x + 12f, r.y + 6f, r.width - 24f, 46f), hint, Ui.WhiteCenterSmall);
        }

        void DrawCatchFeedback()
        {
            if (SimTime < catchUntil)
            {
                // Keep this out of the strike panel and away from the Carry bubble.
                var r = Panel(new Rect(VW - 266f, State.Hull > 0 ? 286f : 140f, 250f, 168f));
                Icon(new Rect(r.x + 14f, r.y + 42f, 86f, 78f), FishPortrait(lastCatchSpecies));
                GUI.Label(new Rect(r.x + 16f, r.y + 12f, r.width - 32f, 26f), catchNew ? "New species!" : catchRecord ? "New personal best!" : "Nice catch!", Ui.H2);
                GUI.Label(new Rect(r.x + 106f, r.y + 50f, 132f, 26f), GameData.Get(lastCatchSpecies).Name, Ui.Body);
                GUI.Label(new Rect(r.x + 106f, r.y + 78f, 132f, 26f), $"{lastCatchKg:0.00} kg", Ui.H2);
                int value = State.ValueOf(new CaughtFish { Species = lastCatchSpecies, Kg = lastCatchKg, StowedAt = SimTime }, SimTime);
                GUI.Label(new Rect(r.x + 16f, r.y + 124f, r.width - 32f, 28f), $"About {value} coins at today's price", Ui.Small);
            }
            float age = SimTime - stowedAt;
            if (age >= 0f && age < 1.6f)
            {
                var pos = ToGui(Cam.WorldToScreenPoint(Boat.TransformPoint(new Vector3(State.HullDef.Hold.x, 1f, State.HullDef.Hold.y))));
                GUI.Label(new Rect(pos.x - 90f, pos.y - 65f - age * 24f, 180f, 30f), "+1 safely stowed", Ui.MiniTitle);
            }
        }

        void DrawNextUpgrade()
        {
            if (State.Hull != 0) return;
            var id = !State.Has(UpgradeId.BigCooler) ? UpgradeId.BigCooler : UpgradeId.RodHolder;
            if (State.Has(id)) return;
            var upgrade = GameData.Upgrade(id);
            GUILayout.Space(12f);
            GUILayout.Label("Make the next trip better", Ui.H2);
            GUILayout.Label(id == UpgradeId.BigCooler ? "A bigger cooler carries six more fish and makes the skiff's 16-fish goal possible." : "A second rod lets you keep another line fishing while you work. Then hire a deckhand to handle bait and carrying.", Ui.Body);
            int shortfall = Mathf.Max(0, upgrade.Cost - State.Coins);
            GUILayout.Label(shortfall > 0 ? $"{upgrade.Name}: {upgrade.Cost} coins · {shortfall} more to go" : $"{upgrade.Name}: {upgrade.Cost} coins · you can afford it", Ui.Small);
            if (GUILayout.Button("Visit Chandlery", Ui.BtnAlt, GUILayout.Height(44f))) OpenShop(HudTab.Chandlery);
        }
    }
}

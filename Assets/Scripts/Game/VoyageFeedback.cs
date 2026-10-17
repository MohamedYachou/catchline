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

        void ResetFeedback() { catchUntil = 0f; stowedAt = -100f; ResetCatchReceipts(); }

        void ShowCatch(Species species, float kg)
        {
            toast = null;
            lastCatchSpecies = species;
            lastCatchKg = kg;
            // The just-landed fish is already in OnDeck. Compare against earlier catches this trip too.
            var earlier = OnDeck.Where(f => f.Species == species).Select(f => f.Kg)
                .Concat(Cooler.Where(f => f.Species == species).Select(f => f.Kg))
                .Concat(People.Where(p => p.Carrying?.Species == species).Select(p => p.Carrying.Kg));
            catchNew = State.LogCount[(int)species] == 0 && earlier.Count() == 1;
            catchRecord = !catchNew && kg > State.LogBest[(int)species] && earlier.All(k => k <= kg);
            catchUntil = SimTime + CatchDisplaySeconds;
        }

        static string FishPortrait(Species species) => "fish-" + species.ToString().ToLowerInvariant();

        public string VoyageHint()
        {
            if (HoldFull) return "Cooler full! Head home to sell.";
            if (Captain.Carrying != null || Captain.Busy || Captain.Walking)
                return Captain.Carrying != null ? "Taking your fish to the cooler…" : "The captain is on it…";
            if (OnDeck.Any(CanCarry)) return "Tap Carry. The captain takes it to the cooler.";
            var rod = MinigameRod;
            if (rod != null) return rod.State switch
            {
                RodState.Bite => "Bite! Tap the water or press Space now!",
                RodState.Waiting => rod.Nibbling ? "Just a nibble. Wait until the bobber goes under." : "Watch the bobber. Wait for it to go under.",
                RodState.Reeling => "Hooked! The captain reels it in for you.",
                _ => "Casting… get ready to watch the bobber.",
            };
            if (FirstVoyage && Cooler.Count >= 3) return "Three safely aboard! Head home to sell, or fill the cooler.";
            if (!State.HasPaidBait && Rods.All(r => r.State == RodState.Unbaited)) return "Free scraps: small fish, no cost. Tap Fish.";
            if (Rods.Any(r => CanCommandRod(r) && r.InWater)) return "Tap Watch to follow that bobber.";
            return Rods.Any(CanCommandRod) ? "Tap Fish. The captain baits and casts for you." : null;
        }

        void DrawVoyageGuide()
        {
            if (!ShowTips || MinigameRod != null || AwaitingCast) return;
            var hint = VoyageHint();
            if (hint == null) return;
            float width = Mathf.Min(520f, VW - 660f);
            if (width < 180f) return; // Action bubbles still guide unusually narrow windows.
            float height = VH < 600f ? 78f : 58f;
            var r = Panel(new Rect((VW - width) / 2f, VH - height - 20f, width, height), Ui.ToastStyle);
            GUI.Label(new Rect(r.x + 12f, r.y + 6f, r.width - 24f, height - 12f), hint, Ui.WhiteCenterSmall);
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

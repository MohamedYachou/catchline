using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public List<CaughtFish> CurrentHaul()
        {
            var haul = new List<CaughtFish>(Cooler);
            haul.AddRange(UnstowedHaul());
            return haul;
        }

        // A picked-up fish leaves OnDeck, so these two groups do not overlap.
        public List<CaughtFish> UnstowedHaul() => OnDeck
            .Concat(People.Where(p => p != null && p.Carrying != null).Select(p => p.Carrying))
            .Select(f => new CaughtFish { Species = f.Species, Kg = f.Kg, StowedAt = f.CaughtAt }).ToList();

        public int DepartureOverflow()
        {
            // Match HeadHome exactly: actors' carried fish first, then deck order.
            var fish = People.Where(p => p != null && p.Carrying != null).Select(p => p.Carrying)
                .Concat(OnDeck).ToList();
            double kg = Cooler.Sum(f => (double)f.Kg); int left = 0;
            foreach (var f in fish)
                if (kg < State.CoolerCapacity) kg += f.Kg; else left++;
            return left;
        }

        bool confirmHeadHome;

        // Player input only; automation and HeadHome's capacity/payout rules stay unchanged.
        void RequestHeadHome()
        {
            if (CurrentMode != Mode.Fishing) return;
            if (DepartureOverflow() == 0 && (!IsNetFisher || Net == NetState.Stowed)) { HeadHome(); return; }
            confirmHeadHome = true;
            paused = true; // Freeze catches, freshness and crew while the exact loss is displayed.
        }

        void CancelHeadHome()
        {
            confirmHeadHome = false;
            paused = false;
        }

        void ConfirmHeadHome()
        {
            confirmHeadHome = false;
            paused = false;
            HeadHome();
        }

        void DrawHeadHomeConfirmation()
        {
            Track(new Rect(0f, 0f, VW, VH));
            Dim(1f);
            var p = Panel(new Rect(VW / 2f - Mathf.Min(520f, VW - 32f) / 2f, VH / 2f - 170f, Mathf.Min(520f, VW - 32f), 340f));
            int overflow = DepartureOverflow();
            GUI.Label(new Rect(p.x + 20f, p.y + 16f, p.width - 40f, 40f), "Leave fish behind?", Ui.H2);
            GUI.Label(new Rect(p.x + 20f, p.y + 64f, p.width - 40f, 90f),
                (overflow > 0 ? $"{overflow} fish cannot fit in the hold and will go back to sea. " : "") +
                (IsNetFisher && Net != NetState.Stowed ? Net == NetState.Ready ? $"Your net still has {NetCatch} fish to haul. Leaving forfeits them. " : "Your net is still deployed; leaving ends this soak. " : "") +
                "The trip is paused while you choose.", Ui.Body);
            if (GUI.Button(new Rect(p.x + 20f, p.y + 174f, p.width - 40f, 60f), "Keep fishing · Esc", Ui.BtnAlt))
            { CancelHeadHome(); return; }
            if (GUI.Button(new Rect(p.x + 20f, p.y + 250f, p.width - 40f, 60f), overflow > 0 ? $"Head home · leave {overflow} fish" : "Head home · abandon net catch", Ui.Btn)) ConfirmHeadHome();
        }

        public string FreshnessStatus(List<CaughtFish> haul, float now)
        {
            if (haul.Count == 0) return "No catch yet";
            if (State.Has(UpgradeId.IceBox)) return "Iced · full value";
            float oldest = haul.Max(f => Mathf.Max(0f, now - f.StowedAt));
            float grace = GameData.FreshnessGraceSeconds - oldest;
            if (grace > 0f) return $"Value drops in {Mathf.CeilToInt(grace)}s";
            float freshness = haul.Min(f => State.Freshness(f, now));
            return freshness <= GameData.MinFreshness ? "Oldest: 60% value · minimum" :
                $"Oldest: {freshness * 100f:0}% · loses 7%/min";
        }

        void DrawCastChoice()
        {
            if (!AwaitingCast || Manning == null) return;
            var p = Panel(new Rect(VW / 2f - 200f, VH - 146f, 400f, 128f));
            GUI.Label(new Rect(p.x + 12f, p.y + 10f, p.width - 24f, 28f), "Deckhand takes care of your catch", Ui.Center);
            var cast = new Rect(p.x + 14f, p.y + 50f, 244f, 60f);
            var leave = new Rect(p.x + 268f, p.y + 50f, 118f, 60f);
            Track(cast); Track(leave);
            bool full = HoldFull;
            if (GUI.Button(cast, full ? "Cooler full" : "Throw again", full ? Ui.BtnOff : Ui.Btn) && !full) ThrowAgain();
            if (GUI.Button(leave, "Leave", Ui.BtnAlt)) LeaveFishing();
        }
    }
}

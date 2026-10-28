using System;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    // Design 14.5 (Mo 10-27): coming home on a restaurant day is a short scene, not a menu. The camera swings to Mira's
    // house on the quay, the prepped crates go up to her door one after another, the market's go to the stall, and a
    // banner tallies the day. A tap skips it; then the day carries on to the market card.
    public partial class VoyageGame
    {
        const float ArrivalSeconds = 6.5f;
        float arrivalAt = -1;
        Action arrivalDone;
        int arrivalPortions, arrivalMarket, arrivalContract;
        public bool ArrivalActive => arrivalAt >= 0;
        static readonly Vector3 MiraDoor = new(20f, HarbourQuayTop, 3.1f);

        void BeginArrival(Action done)
        {
            arrivalAt = SimTime; arrivalDone = done;
            arrivalPortions = RestaurantPrep.Rows.Sum(r => r.Portions);
            arrivalContract = ContractFish(State.UnsoldCatch).Count;
            arrivalMarket = RestaurantPrep.MarketFish;
            harbourLook = (new Vector3(19f, 0, 2.5f), 8.5f); // Mira's house, as the day-exterior capture frames it
            ArrivalCrates();
            audio?.Play(VoyageAudio.Cue.Moor, .5f);
        }

        // Kitchen crates first, to Mira's door; the market's follow to the stall (StartUnload's stack).
        void ArrivalCrates()
        {
            if (scenery == null) return;
            var lib = ArtLibrary.Get();
            var from = Boat.TransformPoint(State.HullDef.Center) + Vector3.up * .5f;
            int kitchen = Mathf.Clamp(Mathf.CeilToInt(arrivalPortions / 6f), arrivalPortions > 0 ? 1 : 0, 5);
            for (int i = 0; i < kitchen; i++)
            {
                var to = scenery.TransformPoint(MiraDoor + new Vector3((i % 3 - 1) * .62f, (i / 3) * .335f, 0));
                var crate = lib?.M("FishCrate") != null ? ArtLibrary.Spawn(lib.M("FishCrate"), scenery, Vector3.zero, Quaternion.identity).transform
                    : Visuals.Box("Crate", scenery, Vector3.zero, new Vector3(.6f, .32f, .4f), Palette.DeckWoodDark).transform;
                crate.position = from; crate.gameObject.SetActive(false);
                crates.Add((crate, from, to, SimTime + .8f + i * .5f));
            }
            var market = Shops.Find(s => s.tab == HudTab.Market).anchor;
            if (market == null || arrivalMarket == 0) return;
            var stack = market.localPosition; stack.y = HarbourQuayTop; stack += new Vector3(1.4f, 0, -1.1f);
            int sell = Mathf.Clamp(Mathf.CeilToInt(arrivalMarket / 4f), 1, 4);
            for (int i = 0; i < sell; i++)
            {
                var to = scenery.TransformPoint(stack + new Vector3((i % 2) * .62f, (i / 2) * .335f, 0));
                var crate = lib?.M("FishCrate") != null ? ArtLibrary.Spawn(lib.M("FishCrate"), scenery, Vector3.zero, Quaternion.identity).transform
                    : Visuals.Box("Crate", scenery, Vector3.zero, new Vector3(.6f, .32f, .4f), Palette.DeckWoodDark).transform;
                crate.position = from; crate.gameObject.SetActive(false);
                crates.Add((crate, from, to, SimTime + .8f + (kitchen + i) * .5f));
            }
        }

        void TickArrival()
        {
            if (!ArrivalActive || SimTime - arrivalAt < ArrivalSeconds) return;
            EndArrival();
        }

        public void EndArrival()
        {
            if (!ArrivalActive) return;
            arrivalAt = -1; harbourLook = null;
            var done = arrivalDone; arrivalDone = null;
            done?.Invoke();
        }

        void InterfaceArrival()
        {
            float t = SimTime - arrivalAt, w = Mathf.Min(compactInterface ? 560 : 720, iw - Edge * 2), h = compactInterface ? 96 : 118;
            var r = new Rect((iw - w) / 2, Edge + (compactInterface ? 8 : 16), w, h);
            var banner = coastalUi.Sliced("arrive/banner", r, "v3-arrival-banner");
            coastalUi.Pose("arrive/banner", 0, .85f + .15f * Ease.OutBack(Mathf.Clamp01(t / .45f)));
            coastalUi.Text("arrive/title", new Rect(w * .1f, 6, w * .8f, h * .46f), "Back in port", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, banner);
            string tally = $"{arrivalPortions} {Plural(arrivalPortions, "portion")} to the kitchen";
            if (arrivalMarket > 0) tally += $" · {arrivalMarket} fish to the market";
            if (arrivalContract > 0) tally += $" · {arrivalContract} for the hotel";
            int shown = Mathf.Clamp(Mathf.FloorToInt((t - .5f) * 40f), 0, tally.Length);
            coastalUi.Text("arrive/tally", new Rect(w * .08f, h * .46f, w * .84f, h * .42f), tally.Substring(0, shown), Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleCenter, banner);
            var bar = new Rect((iw - 240) / 2, ih - Edge - 30, 240, 8);
            coastalUi.ProgressBar("arrive/progress", bar, Mathf.Clamp01(t / ArrivalSeconds), Skin.Bar.Teal);
            coastalUi.Text("arrive/skip", new Rect(bar.x - 40, bar.y - 30, bar.width + 80, 26), "Tap to skip", Skin.Type.Caption, Skin.Cream, TextAnchor.MiddleCenter);
            coastalUi.HitArea("arrive/hit", new Rect(0, 0, iw, ih), EndArrival);
        }
    }
}

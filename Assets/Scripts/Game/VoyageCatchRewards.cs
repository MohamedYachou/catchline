using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public NetCatchReceipt LastNetReceipt { get; private set; }
        float netReceiptUntil;
        const float CatchDisplaySeconds = 6, NetReceiptSeconds = 11;
        static readonly Color RewardWhite = Palette.Hex("F4F1E8");
        static readonly Color RewardMuted = Palette.Hex("B3CAD2");

        void RecordStoredNet(IEnumerable<CaughtFish> stored)
        {
            var receipt = new NetCatchReceipt(stored, State, SimTime);
            if (receipt.Count == 0) return;
            LastNetReceipt = receipt;
            netReceiptUntil = SimTime + NetReceiptSeconds;
        }
        void ResetCatchReceipts() { LastNetReceipt = null; netReceiptUntil = 0; }
        void RewardSurface(string id, Rect r, Color accent, bool halo = false, float alpha = 1)
        {
            var rect = coastalUi.Box(id, r, "", Color.clear, blocks: false);
            // UGUI permits only one Graphic on each object. Keep the retained
            // element as its lifecycle/position owner and draw in a fill child.
            var surface = rect.Find("Reward surface") as RectTransform;
            if (surface == null)
            {
                surface = new GameObject("Reward surface", typeof(RectTransform), typeof(CanvasRenderer), typeof(CatchRewardGraphic)).GetComponent<RectTransform>();
                surface.gameObject.layer = 5;
                surface.SetParent(rect, false);
                surface.anchorMin = Vector2.zero; surface.anchorMax = Vector2.one;
                surface.offsetMin = surface.offsetMax = Vector2.zero;
            }
            var graphic = surface.GetComponent<CatchRewardGraphic>();
            graphic.Style(accent, halo, alpha);
        }
        void RewardText(string id, Rect r, string text, int size, Color color, TextAnchor anchor = TextAnchor.MiddleLeft)
            => coastalUi.Label(id, r, text, size, color, anchor, fitted: true);
        void InterfaceCatchRewards()
        {
            if (SimTime < catchUntil) InterfaceCatchSpecimen();
            if (LastNetReceipt == null) return;
            if (SimTime < netReceiptUntil) InterfaceNetReceipt();
            else
            {
                // Reopen the last receipt from the open-water gap, clear of the bottom action row.
                var review = new Rect(HudGapLeft, ih - Edge - HudButtonHeight - 12 - 52, compactInterface ? 220 : 250, 52);
                coastalUi.Secondary("catch/net/review", review, $"Last net · {LastNetReceipt.Count} fish", () => netReceiptUntil = SimTime + NetReceiptSeconds, "v2-icon-net"); Block(review);
            }
        }
        // Catch cards drop into the open water under the guidance toast, between the ground slab and the crew rail.
        Rect CatchCardRect(float height)
        {
            float left = HudGapLeft, right = HudGapRight, width = Mathf.Clamp(right - left, 280, 440);
            return new Rect(left + Mathf.Max(0, (right - left - width) / 2), CatchCardTop(), width, height);
        }
        // Below whichever pill is up top (a toast, else the guide hint), which grows when its text wraps.
        float CatchCardTop()
        {
            string top = toast != null && SimTime < toastUntil ? toast : ShowTips && MinigameRod == null && !AwaitingCast ? VoyageHint() : null;
            return Edge + (top != null ? CoastalCanvas.ToastHeight(top, HudGapRight - HudGapLeft) : 64) + 8;
        }
        void TierPill(string id, Rect r, CatchTier tier, Transform parent)
        {
            var pill = coastalUi.Sliced(id, r, "v2-pill-cream", parent, Color.Lerp(CatchPresentation.Accent(tier), Color.white, .55f));
            coastalUi.Text(id + "/label", new Rect(8, 0, r.width - 16, r.height), CatchPresentation.Label(tier), Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleCenter, pill);
        }
        void InterfaceCatchSpecimen()
        {
            var species = lastCatchSpecies; float kg = lastCatchKg;
            var tier = CatchPresentation.Tier(species, kg);
            float elapsed = CatchDisplaySeconds - (catchUntil - SimTime);
            if (catchNew && elapsed < 0) { InterfaceFirstCatchReveal(elapsed + FirstCatchRevealSeconds); return; }
            float enter = 1 - Mathf.Pow(1 - Mathf.Clamp01(elapsed / .28f), 3);
            float h = compactInterface ? 112 : 132;
            var r = CatchCardRect(h); r.y -= (1 - enter) * 12;
            string title = catchNew ? "New species!" : catchRecord ? "Personal best!" : "Nice catch!";
            var slab = coastalUi.Slab("catch", r, title, true); Block(r);
            float pw = compactInterface ? 40 : 46, ph = h - Skin.HeaderBand - 16;
            TierPill("catch/tier", new Rect(r.width - 150, 9, 136, 28), tier, slab);
            float art = ph * 1.5f;
            coastalUi.Card("catch/frame", new Rect(12, Skin.HeaderBand + 8, art, ph), Skin.Card.Ink, slab);
            coastalUi.Icon("catch/portrait", new Rect(18, Skin.HeaderBand + 10, art - 12, ph - 4), FishPortrait(species), slab, null, FishPortrait(species));
            float x = art + 26, tw = r.width - x - 14;
            coastalUi.Text("catch/name", new Rect(x, Skin.HeaderBand + 6, tw, ph * .52f), GameData.Get(species).Name, Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, slab);
            coastalUi.Text("catch/weight", new Rect(x, Skin.HeaderBand + 8 + ph * .52f, tw * .55f, ph * .44f),
                $"{kg:0.00} kg · {(CatchPresentation.IsBig(species, kg) ? "big" : "coastal")}", Skin.Type.Small, Skin.InkSoft, TextAnchor.UpperLeft, slab);
            int value = State.ValueOf(new CaughtFish { Species = species, Kg = kg, StowedAt = SimTime }, SimTime);
            coastalUi.PricePill("catch/value", new Rect(r.width - 14 - (compactInterface ? 100 : 116), Skin.HeaderBand + 8 + ph * .5f, compactInterface ? 100 : 116, pw - 6), value, true, slab);
        }
        public void RenderGeminiPreview(RenderTexture target) => coastalUi.RenderCapture(target);
        void InterfaceNetReceipt()
        {
            var receipt = LastNetReceipt;
            var groups = receipt.Items.GroupBy(f => (f.Species, f.Tier)).OrderByDescending(g => g.Key.Tier).ThenBy(g => g.Key.Species).ToList();
            float row = compactInterface ? 34 : 42, footer = compactInterface ? 34 : 40;
            float maxH = ih - Edge - HudButtonHeight - 24 - CatchCardTop();
            float height = Mathf.Min(maxH, Skin.HeaderBand + 10 + groups.Count * row + footer + 8);
            int shown = Mathf.Max(1, Mathf.Min(groups.Count, Mathf.FloorToInt((height - Skin.HeaderBand - 18 - footer) / row)));
            float elapsed = NetReceiptSeconds - (netReceiptUntil - SimTime);
            float enter = 1 - Mathf.Pow(1 - Mathf.Clamp01(elapsed / .28f), 3);
            var r = CatchCardRect(height); r.y -= (1 - enter) * 12;
            var slab = coastalUi.Slab("catch/net", r, "Net catch stowed", true); Block(r);
            float w = r.width;
            for (int i = 0; i < shown; i++)
            {
                var group = groups[i]; float y = Skin.HeaderBand + 8 + i * row;
                coastalUi.Icon($"catch/net/{i}/portrait", new Rect(14, y + 2, (row - 4) * 1.5f, row - 4), FishPortrait(group.Key.Species), slab, null, FishPortrait(group.Key.Species));
                string label = GameData.Get(group.Key.Species).Name + (group.Count() > 1 ? $" ×{group.Count()}" : "");
                float x = 22 + (row - 4) * 1.5f;
                coastalUi.Text($"catch/net/{i}/name", new Rect(x, y, w * .5f, row), label, Skin.Type.Body, Skin.Ink, TextAnchor.MiddleLeft, slab);
                coastalUi.Text($"catch/net/{i}/weight", new Rect(w * .5f + x - 20, y, w * .22f, row), $"{group.Sum(f => f.Kg):0.0} kg", Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleRight, slab);
                coastalUi.Text($"catch/net/{i}/value", new Rect(w - 86, y, 70, row), $"~{group.Sum(f => f.Value)}", Skin.Type.Heading, Skin.Teal, TextAnchor.MiddleRight, slab);
            }
            float fy = r.height - footer - 8;
            coastalUi.Sliced("catch/net/divider", new Rect(16, fy, w - 32, 2), "v2-rule", slab);
            coastalUi.Text("catch/net/total", new Rect(28, fy + 2, w * .6f, footer), $"{receipt.Count} fish · {receipt.Kg:0.00} kg", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, slab);
            coastalUi.Text("catch/net/value", new Rect(w * .5f, fy + 2, w * .5f - 28, footer), $"~{receipt.Value:N0} coins", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleRight, slab);
        }
    }
}

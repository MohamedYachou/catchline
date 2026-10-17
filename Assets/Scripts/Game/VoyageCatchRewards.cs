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
            => coastalUi.Label(id, r, text, size, color, anchor);
        void InterfaceCatchRewards()
        {
            if (SimTime < catchUntil) InterfaceCatchSpecimen();
            if (LastNetReceipt == null) return;
            if (SimTime < netReceiptUntil) InterfaceNetReceipt();
            else
            {
                var review = new Rect(16, ih - 62, 238, 44);
                IButton("catch/net/review", review, $"Last net · {LastNetReceipt.Count} fish", () => netReceiptUntil = SimTime + NetReceiptSeconds, false);
            }
        }
        void InterfaceCatchSpecimen()
        {
            var tier = CatchPresentation.Tier(lastCatchSpecies, lastCatchKg);
            var accent = CatchPresentation.Accent(tier);
            float elapsed = CatchDisplaySeconds - (catchUntil - SimTime);
            float enter = 1 - Mathf.Pow(1 - Mathf.Clamp01(elapsed / .28f), 3);
            float width = compactInterface ? 258 : 244, height = compactInterface ? 94 : 210;
            var r = new Rect(iw - width - 16, ih - height - 12 + (1 - enter) * 12, width, height);
            RewardSurface("catch", r, accent); Block(r);
            string title = catchNew ? "New species!" : catchRecord ? "Personal best!" : "Nice catch!";
            int value = State.ValueOf(new CaughtFish { Species = lastCatchSpecies, Kg = lastCatchKg, StowedAt = SimTime }, SimTime);
            if (compactInterface)
            {
                RewardSurface("catch/glow", new Rect(r.x + 1, r.y + 7, 102, 82), accent, true);
                coastalUi.Art("catch/portrait", new Rect(r.x + 5, r.y + 20, 93, 59), FishPortrait(lastCatchSpecies));
                RewardText("catch/tier", new Rect(r.x + 104, r.y + 4, 145, 19), CatchPresentation.Label(tier), 12, accent);
                RewardText("catch/name", new Rect(r.x + 104, r.y + 23, 145, 28), GameData.Get(lastCatchSpecies).Name, 19, RewardWhite);
                RewardText("catch/value", new Rect(r.x + 104, r.y + 51, 145, 20), $"{lastCatchKg:0.00} kg · ~{value} coins", 13, RewardMuted);
                RewardText("catch/achievement", new Rect(r.x + 104, r.y + 70, 145, 18), title, 12, accent);
            }
            else
            {
                RewardText("catch/achievement", new Rect(r.x + 16, r.y + 9, 212, 26), title, 18, RewardWhite);
                RewardSurface("catch/glow", new Rect(r.x + 10, r.y + 29, 224, 112), accent, true);
                coastalUi.Art("catch/portrait", new Rect(r.x + 18, r.y + 43, 208, 85), FishPortrait(lastCatchSpecies));
                RewardText("catch/name", new Rect(r.x + 16, r.y + 126, 212, 32), GameData.Get(lastCatchSpecies).Name, 23, RewardWhite);
                RewardText("catch/tier", new Rect(r.x + 16, r.y + 157, 212, 20), CatchPresentation.Label(tier), 13, accent);
                RewardText("catch/weight", new Rect(r.x + 16, r.y + 180, 98, 23), $"{lastCatchKg:0.00} kg", 17, RewardMuted);
                coastalUi.Art("catch/coin", new Rect(r.x + 124, r.y + 184, 16, 16), "icon-coin");
                RewardText("catch/value", new Rect(r.x + 145, r.y + 180, 83, 23), $"~{value}", 19, RewardWhite, TextAnchor.MiddleRight);
            }
        }
        void InterfaceNetReceipt()
        {
            var receipt = LastNetReceipt;
            var groups = receipt.Items.GroupBy(f => (f.Species, f.Tier)).OrderByDescending(g => g.Key.Tier).ThenBy(g => g.Key.Species).ToList();
            bool small = compactInterface;
            float row = small ? 30 : 40, header = small ? 42 : 54, footer = small ? 32 : 42;
            // A future five-species batch still clears the left instruments on phones.
            float available = ih - 26 - ReferenceRect(20, 416, 260, 72).yMax;
            if (small && groups.Count > 0) row = Mathf.Min(row, (available - header - footer) / groups.Count);
            float height = header + groups.Count * row + footer;
            float width = small ? 266 : 288;
            float elapsed = NetReceiptSeconds - (netReceiptUntil - SimTime);
            float enter = 1 - Mathf.Pow(1 - Mathf.Clamp01(elapsed / .28f), 3);
            var r = new Rect(16, ih - height - 14 + (1 - enter) * 12, width, height);
            RewardSurface("catch/net", r, Palette.Hex("78C8BB")); Block(r);
            coastalUi.Art("catch/net/icon", new Rect(r.x + 13, r.y + (small ? 9 : 14), 27, 27), "icon-net");
            RewardText("catch/net/title", new Rect(r.x + 49, r.y + 7, width - 65, small ? 27 : 29), "Net catch stowed", small ? 20 : 22, RewardWhite);
            if (!small) RewardText("catch/net/subtitle", new Rect(r.x + 49, r.y + 33, width - 65, 18), "Safely in your hold", 12, RewardMuted);
            for (int i = 0; i < groups.Count; i++)
            {
                var group = groups[i]; var tier = group.Key.Tier;
                float y = r.y + header + i * row;
                var accent = CatchPresentation.Accent(tier);
                RewardSurface($"catch/net/{i}/glow", new Rect(r.x + 8, y, 61, row), accent, true);
                coastalUi.Art($"catch/net/{i}/portrait", new Rect(r.x + 12, y + 3, 54, row - 6), FishPortrait(group.Key.Species));
                string label = GameData.Get(group.Key.Species).Name + (group.Count() > 1 ? $" ×{group.Count()}" : "");
                if (small)
                {
                    RewardText($"catch/net/{i}/name", new Rect(r.x + 76, y, width - 140, row), label, 15, RewardWhite);
                    RewardText($"catch/net/{i}/weight", new Rect(r.xMax - 62, y, 46, row), $"{group.Sum(f => f.Kg):0.00} kg", 12, RewardMuted, TextAnchor.MiddleRight);
                }
                else
                {
                    RewardText($"catch/net/{i}/name", new Rect(r.x + 76, y, width - 148, row * .6f), label, 17, RewardWhite);
                    RewardText($"catch/net/{i}/weight", new Rect(r.x + 76, y + row * .55f, width - 148, row * .45f), $"{group.Sum(f => f.Kg):0.00} kg", 12, RewardMuted);
                    RewardText($"catch/net/{i}/value", new Rect(r.xMax - 66, y, 50, row), $"~{group.Sum(f => f.Value)}", 18, accent, TextAnchor.MiddleRight);
                }
            }
            float fy = r.yMax - footer;
            coastalUi.Box("catch/net/divider", new Rect(r.x + 16, fy + 1, width - 32, 1), "", new Color(.7f, .85f, .87f, .16f), blocks: false);
            RewardText("catch/net/total", new Rect(r.x + 16, fy + 5, width - 103, footer - 9), $"{receipt.Count} fish · {receipt.Kg:0.00} kg", small ? 13 : 15, RewardMuted);
            coastalUi.Art("catch/net/coin", new Rect(r.xMax - 88, fy + (footer - 18) * .5f, 18, 18), "icon-coin");
            RewardText("catch/net/value", new Rect(r.xMax - 65, fy + 3, 49, footer - 6), $"~{receipt.Value}", small ? 18 : 21, RewardWhite, TextAnchor.MiddleRight);
        }
    }
}

using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Illustration landmarks, in normalized screen coordinates. These describe
        // the overview artwork; sailing still uses the real route contracts.
        public static readonly Vector2 ChartHarbour = new(.483f, .711f);
        public static Vector2 NauticalChartPoint(int spot) => spot switch {
            1 => new(.216f, .278f), 2 => new(.815f, .414f),
            3 => new(.159f, .583f), 4 => new(.607f, .08f), 5 => new(.375f, .115f), 6 => new(.72f, .56f), 7 => new(.66f, .24f), 8 => new(.06f, .40f), _ => new(.447f, .445f) };
        bool chartDetailsOpen, chartContractsOpen;
        public static Rect NauticalChartHit(int spot, float width, float height)
        {
            var p = NauticalChartPoint(spot); float w = 178;
            // Include icon and caption in one generous touch target.
            return new Rect(Mathf.Clamp(p.x * width - (spot == 0 ? 28 : 78), 8, width - w - 8), p.y * height - 28, w, 108);
        }
        void ChooseChartGround()
        {
            if (!State.Known(chartFocus) && !State.BuyChart(chartFocus)) return;
            SelectedSpot = chartFocus; SaveGame(); chartDetailsOpen = false;
            audio?.Play(VoyageAudio.Cue.Select, .4f);
        }
        void InterfaceNauticalChart()
        {
            chartFocus = Mathf.Clamp(chartFocus, 0, GameData.Spots.Length - 1);
            Block(new Rect(0, 0, iw, ih));
            coastalUi.ResourceArt("chart/illustrated/field", new Rect(0, 0, iw, ih), "Charts/gull-coast", true);
            var routeRect = coastalUi.Box("chart/routes", new Rect(0, 0, iw, ih), "", Color.clear, blocks: false);
            var routeGraphic = ChartGraphic<IllustratedRoutesGraphic>(routeRect);
            routeGraphic.raycastTarget = false; routeGraphic.SetVerticesDirty();
            for (int i = 0; i < GameData.Spots.Length; i++)
            {
                int spot = i; var p = NauticalChartPoint(i); float x = p.x * iw, y = p.y * ih;
                string id = "chart/nautical/pin/" + i;
                bool selected = SelectedSpot == i;
                DrawChartPin(id + "/symbol", new Rect(x - 22, y - 30, 44, 56), SpotGlyph(i), selected);
                float w = i == 0 ? 196 : 184, h = 58;
                // Harbour mouth and Deep channel carry their cards beside the pin: below it, the Deep channel card would
                // cover the Lighthouse rock pin on a phone.
                bool beside = i == 0 || i == 4;
                float cx = beside ? x + 18 : x - w * .48f;
                float cy = beside ? y - 10 : y + 31;
                var card = new Rect(Mathf.Clamp(cx, 8, iw - w - 8), cy, w, h);
                var face = coastalUi.Card(id + "/card", card, selected ? Skin.Card.Selected : Skin.Card.Soft);
                coastalUi.Text(id + "/name", new Rect(12, 4, w - 24, 28), GameData.Spots[i].Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, face);
                string state = !State.Known(i) ? $"Chart · {GameData.Spots[i].ChartCost} coins" : selected ? "Selected ground" : "Explore ground";
                coastalUi.Text(id + "/state", new Rect(12, 31, w - 24, 22), state, Skin.Type.Caption, State.Known(i) ? Skin.Teal : Skin.InkSoft, TextAnchor.MiddleLeft, face);
                var hit = new Rect(Mathf.Min(x - 25, card.x), y - 32, Mathf.Max(x + 25, card.xMax) - Mathf.Min(x - 25, card.x), card.yMax - y + 32);
                coastalUi.HitArea(id, hit, () => { chartFocus = spot; chartDetailsOpen = true; chartContractsOpen = false; MenuSound(); });
            }
            var harbour = new Vector2(ChartHarbour.x * iw, ChartHarbour.y * ih);
            DrawChartPin("chart/harbour/pin", new Rect(harbour.x - 22, harbour.y - 28, 44, 56), 5, false);
            ChartHeader();
            ShopTabs(true);
            if (chartDetailsOpen) DrawChartGroundDetail();
            if (chartContractsOpen) DrawChartContractsPanel();
        }
        // Spots 0-4 use glyphs 0-4; glyph 5 is home, so the Seal skerries (spot 5) gets the seal head (10) and the
        // Wreck bank (6, the open water right of the harbour mouth) the sunken steamer (11), Lighthouse rock (7) the
        // lighthouse (12) and the Whale shelf (8) a whale's tail (13).
        static int SpotGlyph(int spot) => spot == 5 ? 10 : spot == 6 ? 11 : spot == 7 ? 12 : spot == 8 ? 13 : spot;
        void DrawChartPin(string id, Rect r, int glyph, bool selected)
        {
            var host = coastalUi.Box(id, r, "", Color.clear, blocks: false);
            var graphic = ChartGraphic<ChartPinGraphic>(host);
            graphic.raycastTarget = false; graphic.Configure(glyph, selected, true);
        }
        // Floating header so the illustration stays visible: back + title left, coins and contracts right.
        void ChartHeader()
        {
            float h = compactInterface ? 52 : 64;
            var title = new Rect(Edge, Edge, compactInterface ? 220 : 260, h);
            var slab = coastalUi.Slab("chart/title", title);
            coastalUi.CardButton("shop/close", new Rect(8, (h - 44) / 2, 52, 44), null, () => { panelOpen = false; chartDetailsOpen = chartContractsOpen = false; }, "v2-icon-back", true, slab);
            coastalUi.Text("chart/title/name", new Rect(72, 0, title.width - 84, h), "CHART", Skin.Type.Display, Skin.Ink, TextAnchor.MiddleLeft, slab);
            float pill = compactInterface ? 170 : 220;
            coastalUi.PricePill("chart/coins", new Rect(iw - Edge - pill, Edge, pill, h), State.Coins);
            coastalUi.Secondary("chart/contracts", new Rect(iw - Edge - pill, Edge + h + 8, pill, compactInterface ? 44 : 52),
                $"Contracts {State.Active.Count}/{GameData.MaxActiveContracts}", () => { chartContractsOpen = true; chartDetailsOpen = false; MenuSound(); });
        }
        void DrawChartGroundDetail()
        {
            var ground = GameData.Spots[chartFocus]; bool known = State.Known(chartFocus);
            float w = compactInterface ? 340 : 380, h = compactInterface ? 236 : 280;
            var panel = new Rect(iw - Edge - w, ih - Edge - TabBarHeight - 16 - h, w, h);
            var slab = coastalUi.Slab("chart/focus/panel", panel, ground.Name, true);
            coastalUi.CardButton("chart/focus/close", new Rect(w - 100, 6, 88, 34), "Close", () => chartDetailsOpen = false, null, true, slab);
            float x = Skin.SlabPad + 4, tw = w - x * 2, y = Skin.HeaderBand + 10;
            coastalUi.Text("chart/focus/detail", new Rect(x, y, tw, 44), ground.Blurb, Skin.Type.Small, Skin.Ink, TextAnchor.UpperLeft, slab);
            coastalUi.Text("chart/focus/fish", new Rect(x, y + 46, tw, 40), string.Join(" · ", ground.Table.Select(e => GameData.Get(e.species).Name)), Skin.Type.Caption, Skin.InkSoft, TextAnchor.UpperLeft, slab);
            coastalUi.Text("chart/focus/stock", new Rect(x, y + 86, tw, 24), $"{ground.RowSeconds * State.HullDef.TravelMultiplier:0.#}s journey · stocks {State.Richness[chartFocus] * 100:0}%", Skin.Type.Small, Skin.Teal, TextAnchor.MiddleLeft, slab);
            string action = known ? SelectedSpot == chartFocus ? "Selected" : "Fish here" : $"Buy chart · {ground.ChartCost}";
            float bh = compactInterface ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight;
            coastalUi.Primary("chart/select", new Rect(x, h - bh - 14, tw, bh), action, ChooseChartGround, known ? null : "v2-icon-coin",
                known ? SelectedSpot != chartFocus : State.Coins >= ground.ChartCost, slab);
        }
        void DrawChartContractsPanel()
        {
            coastalUi.Scrim("chart/contracts/shade", () => chartContractsOpen = false, .7f);
            float w = Mathf.Min(680, iw - 32), rowH = compactInterface ? 64 : 76, gap = 8;
            int rows = State.Active.Count + State.Offers.Count;
            float h = Mathf.Min(ih - 64, Skin.HeaderBand + 56 + Mathf.Max(1, rows) * (rowH + gap) + Skin.SlabPad + 8);
            var panel = new Rect((iw - w) / 2, (ih - h) / 2, w, h);
            var slab = coastalUi.Slab("chart/contracts/panel", panel, $"Harbour contracts · {State.Active.Count}/{GameData.MaxActiveContracts}", true);
            coastalUi.CardButton("chart/contracts/close", new Rect(w - 100, 6, 88, 34), "Close", () => chartContractsOpen = false, null, true, slab);
            coastalUi.Text("chart/contracts/help", new Rect(Skin.SlabPad + 4, Skin.HeaderBand + 6, w - Skin.SlabPad * 2 - 8, 44),
                "Sell matching catches to make progress. Every fish is paid; completion earns a bonus.", Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleLeft, slab);
            float top = panel.y + Skin.HeaderBand + 56;
            var content = coastalUi.Scroll("catalog/contracts", new Rect(panel.x + Skin.SlabPad, top, w - Skin.SlabPad * 2, panel.yMax - top - Skin.SlabPad), rows * (rowH + gap) + 8);
            float cw = w - Skin.SlabPad * 2 - 12, y = 0;
            foreach (var c in State.Active)
            {
                var card = coastalUi.Card("active/" + c.Title, new Rect(0, y, cw, rowH), Skin.Card.Ink, content);
                coastalUi.Icon("active/" + c.Title + "/icon", new Rect(12, (rowH - 40) / 2, 40, 40), "icon-contract-scroll", card);
                coastalUi.Text("active/" + c.Title + "/title", new Rect(64, 4, cw - 76, rowH / 2 - 2), $"{c.Title} · {c.Delivered}/{c.Count}", Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, card);
                coastalUi.Text("active/" + c.Title + "/reward", new Rect(64, rowH / 2 + 2, cw - 76, rowH / 2 - 6), $"{c.Reward} bonus coins · {c.VoyagesLeft} voyages left", Skin.Type.Small, Skin.Teal, TextAnchor.UpperLeft, card);
                y += rowH + gap;
            }
            for (int i = 0; i < State.Offers.Count; i++)
            {
                var c = State.Offers[i];
                var card = coastalUi.Card("offer/" + i, new Rect(0, y, cw, rowH), Skin.Card.Soft, content);
                float bw = compactInterface ? 150 : 180;
                coastalUi.Text("offer/" + i + "/title", new Rect(14, 4, cw - bw - 36, rowH / 2 - 2), "Deliver " + c.Title, Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, card);
                coastalUi.Text("offer/" + i + "/reward", new Rect(14, rowH / 2 + 2, cw - bw - 36, rowH / 2 - 6), $"{c.Reward} bonus coins · {c.VoyagesLeft} voyages", Skin.Type.Small, Skin.Teal, TextAnchor.UpperLeft, card);
                coastalUi.Secondary("offer/" + i + "/take", new Rect(cw - bw - 12, (rowH - 48) / 2, bw, 48), "Take", () => { if (State.Offers.Contains(c) && State.TakeContract(c)) SaveGame(); },
                    null, State.Active.Count < GameData.MaxActiveContracts, card);
                y += rowH + gap;
            }
        }
    }
}

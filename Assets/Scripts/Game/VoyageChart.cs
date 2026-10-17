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
            3 => new(.159f, .583f), 4 => new(.607f, .08f), _ => new(.447f, .445f) };
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
        void ChartText(string id, Rect r, string text, float size = 18, bool bold = false, TextAnchor align = TextAnchor.MiddleLeft)
            => coastalUi.ReferenceLabel(id, r, text, size, bold, align, false);
        void InterfaceNauticalChart()
        {
            chartFocus = Mathf.Clamp(chartFocus, 0, GameData.Spots.Length - 1);
            coastalUi.ReferenceScale = 1;
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
                DrawChartPin(id + "/symbol", new Rect(x - 22, y - 30, 44, 56), i, selected);
                float w = i == 0 ? 188 : 178, h = 54;
                float cx = i == 0 ? x + 18 : x - w * .48f;
                float cy = i == 0 ? y - 10 : y + 31;
                var card = new Rect(Mathf.Clamp(cx, 8, iw - w - 8), cy, w, h);
                coastalUi.ReferencePanel(id + "/card", card, FishReferenceStyle.PanelKind.Row);
                ChartText(id + "/name", new Rect(card.x + 12, card.y + 2, w - 24, 28), GameData.Spots[i].Name, 19, true);
                string state = !State.Known(i) ? "Chart · " + GameData.Spots[i].ChartCost + " coins" : selected ? "Selected ground" : "Explore ground";
                ChartText(id + "/state", new Rect(card.x + 12, card.y + 29, w - 24, 21), state, 13);
                var hit = new Rect(Mathf.Min(x - 25, card.x), y - 32, Mathf.Max(x + 25, card.xMax) - Mathf.Min(x - 25, card.x), card.yMax - y + 32);
                coastalUi.ReferenceButton(id, hit, () => { chartFocus = spot; chartDetailsOpen = true; chartContractsOpen = false; });
            }
            var harbour = new Vector2(ChartHarbour.x * iw, ChartHarbour.y * ih);
            DrawChartPin("chart/harbour/pin", new Rect(harbour.x - 22, harbour.y - 28, 44, 56), 5, false);
            var home = new Rect(harbour.x - 90, Mathf.Min(harbour.y + 28, ih - 137), 180, 52);
            coastalUi.ReferencePanel("chart/harbour/card", home, FishReferenceStyle.PanelKind.Row);
            ChartText("chart/harbour/title", new Rect(home.x + 12, home.y + 2, 156, 28), "Gull Harbour", 20, true);
            ChartText("chart/harbour/subtitle", new Rect(home.x + 12, home.y + 29, 156, 20), "The home coast", 13);
            coastalUi.ReferenceButton("chart/harbour", new Rect(home.x, harbour.y - 28, home.width, home.yMax - harbour.y + 28), () => panelOpen = false);
            DrawChartStatus(); DrawChartNavigation();
            if (chartDetailsOpen) DrawChartGroundDetail();
            if (chartContractsOpen) DrawChartContractsPanel();
        }
        void DrawChartPin(string id, Rect r, int glyph, bool selected)
        {
            var host = coastalUi.Box(id, r, "", Color.clear, blocks: false);
            var graphic = ChartGraphic<ChartPinGraphic>(host);
            graphic.raycastTarget = false; graphic.Configure(glyph, selected, true);
        }
        void DrawChartStatus()
        {
            var status = new Rect(18, 18, 302, 58);
            coastalUi.ReferencePanel("chart/status", status, FishReferenceStyle.PanelKind.Row);
            coastalUi.ReferenceIcon("chart/status/sun", new Rect(30, 27, 37, 37), FishReferenceStyle.Icon.Sun);
            ChartText("chart/status/day", new Rect(77, 24, 80, 23), "DAY " + State.Voyage, 16, true);
            int seconds = Mathf.FloorToInt(SimTime);
            ChartText("chart/status/time", new Rect(77, 47, 80, 22), $"{seconds / 60:00}:{seconds % 60:00}", 18, true);
            coastalUi.Box("chart/status/divider", new Rect(166, 27, 1, 38), "", Palette.Hex("D8CDBA"), blocks: false);
            coastalUi.ReferenceIcon("chart/status/coin", new Rect(179, 28, 36, 36), FishReferenceStyle.Icon.Coin);
            ChartText("chart/status/coins", new Rect(225, 25, 82, 40), State.Coins.ToString("N0"), 25, true);
            var hold = new Rect(iw - 246, 18, 228, 58);
            coastalUi.ReferencePanel("chart/hold", hold, FishReferenceStyle.PanelKind.Row);
            coastalUi.ReferenceIcon("chart/hold/icon", new Rect(hold.x + 10, 26, 40, 39), FishReferenceStyle.Icon.Crate);
            ChartText("chart/hold/count", new Rect(hold.x + 61, 24, 155, 26), $"Hold  {HoldKg + State.UnsoldCatch.Sum(f => f.Kg):0.00} / {State.CoolerCapacity:0.#} kg", 17, true);
            coastalUi.ReferenceBar("chart/hold/fill", new Rect(hold.x + 61, 54, 146, 9), (HoldKg + State.UnsoldCatch.Sum(f => f.Kg)) / State.CoolerCapacity);
            var contracts = new Rect(iw - 194, 87, 176, 35);
            coastalUi.ReferencePanel("chart/contracts/card", contracts, FishReferenceStyle.PanelKind.Row);
            ChartText("chart/contracts/caption", contracts, $"Contracts  {State.Active.Count}/{GameData.MaxActiveContracts}", 15, true, TextAnchor.MiddleCenter);
            coastalUi.ReferenceButton("chart/contracts", contracts, () => { chartContractsOpen = true; chartDetailsOpen = false; });
        }
        void DrawChartNavigation()
        {
            float w = Mathf.Min(610, iw - 40), h = compactInterface ? 64 : 78;
            var nav = new Rect((iw - w) / 2, ih - h - 14, w, h);
            coastalUi.ReferencePanel("chart/nav", nav, FishReferenceStyle.PanelKind.Row);
            string[] names = { "Boat", "Crew", "Map", "Gear", "Port" };
            for (int i = 0; i < names.Length; i++)
            {
                int index = i; var item = new Rect(nav.x + i * w / 5 + 5, nav.y + 5, w / 5 - 10, h - 10);
                if (i == 2) coastalUi.ReferencePanel("chart/nav/selected", item, FishReferenceStyle.PanelKind.Row, Palette.Hex("AEE5EE"));
                var icon = coastalUi.Box("chart/nav/" + i + "/icon", new Rect(item.center.x - 17, item.y + 3, 34, 34), "", Color.clear, blocks: false);
                var graphic = ChartGraphic<ChartPinGraphic>(icon);
                graphic.raycastTarget = false; graphic.Configure(6 + i, false, false);
                ChartText("chart/nav/" + i + "/text", new Rect(item.x, item.yMax - 24, item.width, 24), names[i], 17, true, TextAnchor.MiddleCenter);
                coastalUi.ReferenceButton("chart/nav/" + names[i], item, () => {
                    chartDetailsOpen = chartContractsOpen = false;
                    if (index == 0) panelOpen = false;
                    else if (index == 1) OpenShop(HudTab.CrewOffice);
                    else if (index == 3) OpenShop(HudTab.Chandlery);
                    else if (index == 4) OpenShop(HudTab.Market);
                });
            }
        }
        void DrawChartGroundDetail()
        {
            var ground = GameData.Spots[chartFocus]; bool known = State.Known(chartFocus);
            var panel = new Rect(iw - 346, ih - (compactInterface ? 292 : 306), 328, 196);
            coastalUi.ReferencePanel("chart/focus/panel", panel, FishReferenceStyle.PanelKind.Row);
            ChartText("chart/focus/title", new Rect(panel.x + 14, panel.y + 6, 260, 30), ground.Name, 23, true);
            coastalUi.ReferenceButton("chart/focus/close", new Rect(panel.xMax - 44, panel.y + 4, 40, 40), () => chartDetailsOpen = false);
            ChartText("chart/focus/x", new Rect(panel.xMax - 40, panel.y + 4, 34, 34), "×", 23, true, TextAnchor.MiddleCenter);
            ChartText("chart/focus/detail", new Rect(panel.x + 14, panel.y + 41, 300, 42), ground.Blurb, 14);
            ChartText("chart/focus/fish", new Rect(panel.x + 14, panel.y + 85, 300, 38), string.Join(" · ", ground.Table.Select(e => GameData.Get(e.species).Name)), 12);
            ChartText("chart/focus/stock", new Rect(panel.x + 14, panel.y + 123, 300, 24), $"{ground.RowSeconds * State.HullDef.TravelMultiplier:0.#}s journey · stocks {State.Richness[chartFocus] * 100:0}%", 14);
            string action = known ? SelectedSpot == chartFocus ? "Selected ground" : "Fish here" : $"Buy chart · {ground.ChartCost} coins";
            coastalUi.Button("chart/select", new Rect(panel.x + 12, panel.y + 151, 304, 36), action, ChooseChartGround, "button-primary-normal", known || State.Coins >= ground.ChartCost, size: 16);
        }
        void DrawChartContractsPanel()
        {
            coastalUi.Box("chart/contracts/shade", new Rect(0, 0, iw, ih), "", new Color(.03f, .15f, .22f, .35f));
            var panel = new Rect((iw - 660) / 2, 82, 660, ih - 174);
            coastalUi.ReferencePanel("chart/contracts/panel", panel, FishReferenceStyle.PanelKind.Row);
            ChartText("chart/contracts/title", new Rect(panel.x + 18, panel.y + 10, 560, 32), "Harbour contracts", 25, true);
            coastalUi.Button("chart/contracts/close", new Rect(panel.xMax - 58, panel.y + 8, 44, 44), "×", () => chartContractsOpen = false, "button-secondary-normal");
            float top = panel.y + 55, height = panel.height - 70;
            catalog = coastalUi.Scroll("catalog/contracts", new Rect(panel.x + 16, top, panel.width - 32, height), 110 + State.Active.Count * 80 + State.Offers.Count * 88);
            catalogWidth = panel.width - 48; catalogY = 0;
            DrawNauticalContracts();
            ((RectTransform)catalog).sizeDelta = new Vector2(catalogWidth, Mathf.Max(height, catalogY));
        }
        void DrawNauticalContracts()
        {
            CatalogHeading("contracts/title", $"Harbour contracts · {State.Active.Count}/{GameData.MaxActiveContracts}", "Sell matching catches to make progress. Every fish is paid; completion earns a bonus.", 82);
            foreach (var c in State.Active)
            {
                coastalUi.Art("active/" + c.Title + "/icon", new Rect(8, catalogY + 8, 40, 40), "icon-contract-scroll", catalog);
                coastalUi.Label("active/" + c.Title, new Rect(64, catalogY, catalogWidth - 70, 70), $"{c.Title} · {c.Delivered}/{c.Count}\n{c.Reward} bonus coins · {c.VoyagesLeft} voyages left", 18, null, TextAnchor.MiddleLeft, catalog);
                catalogY += 78;
            }
            for (int i = 0; i < State.Offers.Count; i++)
            {
                var c = State.Offers[i];
                coastalUi.Label("offer/" + i, new Rect(4, catalogY, catalogWidth - 170, 78), $"Deliver {c.Title}\n{c.Reward} bonus coins · {c.VoyagesLeft} voyages", 18, null, TextAnchor.MiddleLeft, catalog);
                coastalUi.Button("offer/" + i + "/take", new Rect(catalogWidth - 158, catalogY + 12, 150, 48), "Take contract", () => { if (State.Offers.Contains(c) && State.TakeContract(c)) SaveGame(); }, "button-secondary-normal", State.Active.Count < GameData.MaxActiveContracts, catalog, 16);
                catalogY += 88;
            }
        }
    }
}

using System;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    public static class ChartChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string reason) { if (!ok) throw new Exception("Chart check failed: " + reason); }
        static void Field(VoyageGame g, string name, object value) => typeof(VoyageGame).GetField(name, Hidden).SetValue(g, value);
        static Text Text(VoyageGame g, string id) => g.GetComponentsInChildren<Text>().Single(t => t.name == id);
        static VoyageGame Fixture()
        {
            var g = new GameObject("Isolated illustrated coast").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            Field(g, "showTitle", false); Field(g, "paused", false); Field(g, "panelOpen", true);
            Field(g, "hudTab", VoyageGame.HudTab.HarbourMaster); Field(g, "toastUntil", 0f);
            typeof(VoyageGame).GetProperty("State").GetSetMethod(true).Invoke(g, new object[] { new GameState(11) });
            g.State.Charts.Clear(); g.SelectedSpot = 0; g.State.Coins = 0; return g;
        }
        static void Render(VoyageGame g, int w = 1920, int h = 1080) { g.PrepareInterface(w, h, 1); Canvas.ForceUpdateCanvases(); }
        static void Page(VoyageGame g, int page, int w = 1920, int h = 1080)
        {
            Render(g, w, h);
            if (g.GetComponentInChildren<IllustratedRoutesGraphic>().Page != page)
            {
                Check(g.InvokeInterface(page == 0 ? "chart/page/gull" : "chart/page/outer"), "coast switch works");
                Render(g, w, h);
            }
            Check(g.GetComponentInChildren<IllustratedRoutesGraphic>().Page == page, "route overlay follows coast page");
        }
        static void CoastRules()
        {
            Check(Coasts.Names.SequenceEqual(new[] { "Gull coast", "Outer coast" }), "two named coasts");
            Check(GameData.Spots.Length == 11 && Coasts.OuterFirstSpot == 5, "five Gull grounds and six Outer grounds");
            Check(GameData.HullTier(Coasts.OuterMinimumHull) == 4, "Outer coast opens at boat tier4");
            Check(GameData.Spots.Select(s => s.ChartCost).SequenceEqual(new[] { 0, 800, 2500, 4000, 8000, 9000, 14000, 18000, 26000, 32000, 36000 }), "current chart price ladder");
            for (int hull = 0; hull < GameData.Hulls.Length; hull++)
            {
                var state = new GameState(11) { Hull = hull, Coins = int.MaxValue };
                state.Charts.Clear();
                for (int spot = 0; spot < GameData.Spots.Length; spot++)
                {
                    bool open = spot < 5 || GameData.HullTier(hull) >= 4;
                    Check(VoyageGame.ChartPage(spot) == (spot < 5 ? 0 : 1), "ground belongs to its coast");
                    Check(Coasts.Open(spot, hull) == open, "tier gate uses boat tier rather than hull id");
                    int coins = state.Coins, price = GameData.Spots[spot].ChartCost;
                    bool bought = state.BuyChart(spot);
                    Check(bought == (price > 0 && open), "purchase respects free ground and tier gate");
                    Check(state.Known(spot) == (price == 0 || open) && state.Coins == coins - (bought ? price : 0), "purchase charges exact data price only when allowed");
                    coins = state.Coins;
                    Check(!state.BuyChart(spot) && state.Coins == coins, "repeat or blocked purchase never charges");
                }
            }
        }
        public static void Run()
        {
            ArtImport.BuildLibrary(); EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            CoastRules();
            var g = Fixture();
            try
            {
                for (int page = 0; page < 2; page++)
                {
                    Page(g, page);
                    for (int i = 0; i < GameData.Spots.Length; i++)
                    {
                        bool visible = VoyageGame.ChartPage(i) == page;
                        Check(g.GetComponentsInChildren<RectTransform>().Any(t => t.name == "chart/nautical/pin/" + i) == visible, "only current coast pins are active");
                        if (!visible) { Check(!g.InvokeInterface("chart/nautical/pin/" + i), "hidden coast has no live hit target"); continue; }
                        Check(g.InvokeInterface("chart/nautical/pin/" + i), "live landmark target"); Render(g);
                        Check(Text(g, "chart/focus/panel/title").text == GameData.Spots[i].Name.ToUpperInvariant(), "inspect real destination");
                        Check(g.SelectedSpot == 0, "inspection does not change sailing destination");
                        if (page == 1)
                        {
                            g.State.Coins = int.MaxValue; Render(g);
                            Check(!g.InvokeInterface("chart/select") && !g.State.Known(i) && g.State.Coins == int.MaxValue, "rowboat cannot buy Outer ground even with enough money");
                        }
                    }
                    Check(g.InvokeInterface("chart/focus/close"), "ground details close"); Render(g);
                }
                g.State.Hull = Coasts.OuterMinimumHull;
                for (int i = 1; i < GameData.Spots.Length; i++)
                {
                    Page(g, VoyageGame.ChartPage(i));
                    Check(g.InvokeInterface("chart/nautical/pin/" + i), "inspect ground for purchase");
                    int price = GameData.Spots[i].ChartCost, selected = g.SelectedSpot;
                    g.State.Coins = price - 1; Render(g);
                    Check(!g.InvokeInterface("chart/select") && !g.State.Known(i) && g.SelectedSpot == selected && g.State.Coins == price - 1, "short wallet cannot unlock or change selection");
                    g.State.Coins = price; Render(g);
                    Check(g.InvokeInterface("chart/select"), "buy ground through real action"); Render(g);
                    Check(g.State.Known(i) && g.SelectedSpot == i && g.State.Coins == 0, "purchase selects ground for exact data price");
                    g.InvokeInterface("chart/nautical/pin/" + i); Render(g);
                    Check(!g.InvokeInterface("chart/select") && g.State.Coins == 0, "selected ground is disabled and cannot charge twice");
                }
                Page(g, 0); g.InvokeInterface("chart/nautical/pin/0"); Render(g);
                Check(g.InvokeInterface("chart/select") && g.SelectedSpot == 0 && g.State.Coins == 0, "known unselected ground can be selected without coins");

                g.State.Active.Clear(); g.State.Offers.Clear();
                for (int i = 0; i < 3; i++) g.State.Offers.Add(new Contract { Species = (Species)i, Count = 3 + i, Reward = 15 + i, VoyagesLeft = 3 });
                g.InvokeInterface("chart/contracts"); Render(g); var contract = g.State.Offers[0];
                Check(g.InvokeInterface("offer/0/take"), "contracts reachable in map modal");
                Check(g.State.Active.Contains(contract) && !g.State.Offers.Contains(contract), "actual contract added once");
                g.InvokeInterface("offer/0/take"); Check(g.State.Active.Count == 1, "stale callback cannot duplicate");
                Render(g); g.InvokeInterface("offer/0/take"); Render(g);
                Check(!g.InvokeInterface("offer/0/take") && g.State.Active.Count == GameData.MaxActiveContracts, "contract cap preserved");
                Check(g.InvokeInterface("chart/contracts/close"), "contracts close"); Render(g);

                foreach (var size in new[] { new Vector2Int(1920, 1080), new Vector2Int(1440, 900), new Vector2Int(844, 390) })
                for (int page = 0; page < 2; page++)
                {
                    Page(g, page, size.x, size.y);
                    var plate = g.GetComponentsInChildren<Image>().Single(i => i.name == "chart/illustrated/field");
                    var expected = Resources.Load<Texture2D>(page == 1 ? "Charts/outer-coast" : "Charts/gull-coast") ?? Resources.Load<Texture2D>("Charts/gull-coast");
                    Check(expected != null && plate.sprite != null && plate.sprite.texture == expected, "current coast illustration resource is used");
                    var field = (RectTransform)plate.transform;
                    var root = g.GetComponentInChildren<CoastalCanvas>();
                    Check(Mathf.Abs(field.rect.width - root.Width) < 1 && Mathf.Abs(field.rect.height - root.Height) < 1, "edge-to-edge coast at " + size);
                    for (int i = 0; i < GameData.Spots.Length; i++)
                    {
                        if (VoyageGame.ChartPage(i) != page) continue;
                        var hit = g.GetComponentsInChildren<RectTransform>().Single(t => t.name == "chart/nautical/pin/" + i);
                        Check(hit.rect.width * size.y / root.Height >= 43.9f && hit.rect.height * size.y / root.Height >= 43.9f, "44pixel landmark target");
                        Vector2 p = hit.anchoredPosition;
                        Check(p.x >= 0 && p.x + hit.rect.width <= root.Width + 1 && -p.y >= 0 && -p.y + hit.rect.height <= root.Height + 1, "landmark target within screen");
                    }
                    Check(g.GetComponentsInChildren<IllustratedRoutesGraphic>().Length == 1, "one retained route overlay");
                    Check(g.GetComponentsInChildren<ChartPinGraphic>().Length == (page == 0 ? 6 : 7), "coast grounds plus harbour pin");
                    foreach (var text in g.GetComponentsInChildren<Text>().Where(t => t.name.StartsWith("chart/"))) Check(text.font != null, "real supplied live fonts");
                }
                g.State.Coins = 24850; Render(g);
                Check(Text(g, "chart/coins/value").text == 24850.ToString("N0"), "wallet uses current amount");
                foreach (var tab in new[] { VoyageGame.HudTab.CrewOffice, VoyageGame.HudTab.Chandlery, VoyageGame.HudTab.Supplies, VoyageGame.HudTab.Market })
                {
                    Check(g.InvokeInterface("shop/tab/" + tab), "shop destination works"); Render(g);
                    Check(g.GetComponentsInChildren<RectTransform>().All(t => t.name != "chart/illustrated/field"), "chart art and targets inactive in shop");
                    Check(Text(g, "shop/header/title").text == (tab == VoyageGame.HudTab.CrewOffice ? "CREW OFFICE" : tab.ToString().ToUpperInvariant()), "correct shop opened");
                    Check(g.InvokeInterface("shop/tab/HarbourMaster"), "chart reachable from shop"); Render(g);
                }
                Check(g.InvokeInterface("shop/close"), "back returns to harbour"); Render(g);
                Check(g.GetComponentsInChildren<RectTransform>().All(t => t.name != "chart/illustrated/field") && !g.InvokeInterface("chart/nautical/pin/0"), "closed chart art and hit targets inactive");
                g.SelectedSpot = GameData.Spots.Length - 1;
                Check(g.InvokeInterface("shop/tab/HarbourMaster"), "reopen chart from harbour"); Render(g);
                Check(g.GetComponentInChildren<IllustratedRoutesGraphic>().Page == 1, "reopened chart follows selected Outer ground");
            }
            finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }
            Debug.Log("[Catchline] CHART CHECKS PASSED: Gull5/Outer6, data prices/tier gates, focus/purchase/contracts, both coast resources/touch bounds, wallet and shop navigation");
        }
        public static void Capture()
        {
            Run(); var g = Fixture(); g.State.Coins = 200;
            System.IO.Directory.CreateDirectory(System.IO.Path.GetFullPath("Logs/chart017"));
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic);
            void Shot(string n, int w, int h) => shot.Invoke(null, new object[] { g, "../chart017/" + n, w, h, 1f });
            Shot("map-laptop", 2560, 1440); Shot("map-desktop", 1440, 900); Shot("map-phone", 844, 390);
            Page(g, 1); Shot("map-outer-desktop", 1440, 900); Shot("map-outer-phone", 844, 390); Page(g, 0);
            g.InvokeInterface("chart/nautical/pin/2"); Shot("map-sandbar", 1440, 900);
            g.InvokeInterface("chart/contracts"); Shot("map-contracts", 1440, 900);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] Snapshot written to Logs/chart017");
        }
    }
}

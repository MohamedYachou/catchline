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
        public static void Run()
        {
            ArtImport.BuildLibrary(); EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = Fixture(); Render(g);
            var plate = g.GetComponentsInChildren<Image>().Single(i => i.name == "chart/illustrated/field");
            Check(plate.sprite != null && plate.sprite.texture.width == 1672 && plate.sprite.texture.height == 941, "original-resolution illustrated resource is used without power-of-two resampling");
            Check(g.GetComponentsInChildren<RectTransform>().All(r => r.name != "shop/shell"), "map replaces shop shell across entire screen");
            for (int i = 0; i < GameData.Spots.Length; i++)
            {
                Check(g.InvokeInterface("chart/nautical/pin/" + i), "live landmark target"); Render(g);
                Check(Text(g, "chart/focus/title").text == GameData.Spots[i].Name, "inspect real destination");
                Check(g.SelectedSpot == 0, "inspection does not change sailing destination");
            }
            Check(g.InvokeInterface("chart/nautical/pin/2"), "inspect locked sandbar");
            int price = GameData.Spots[2].ChartCost; g.State.Coins = price - 1; Render(g);
            Check(!g.InvokeInterface("chart/select") && !g.State.Known(2) && g.SelectedSpot == 0, "no money cannot unlock");
            g.State.Coins = price; Render(g); Check(g.InvokeInterface("chart/select"), "real buy action"); Render(g);
            Check(g.State.Known(2) && g.SelectedSpot == 2 && g.State.Coins == 0, "one purchase selects correct ground");
            g.InvokeInterface("chart/nautical/pin/2"); Render(g); Check(g.InvokeInterface("chart/select") && g.State.Coins == 0, "owned chart never charges again");
            g.InvokeInterface("chart/nautical/pin/1"); Render(g); Check(g.InvokeInterface("chart/select") && g.SelectedSpot == 1, "known grounds need no coins");
            g.State.Active.Clear(); g.State.Offers.Clear();
            for (int i = 0; i < 3; i++) g.State.Offers.Add(new Contract { Species = (Species)i, Count = 3 + i, Reward = 15 + i, VoyagesLeft = 3 });
            g.InvokeInterface("chart/contracts"); Render(g); var contract = g.State.Offers[0];
            Check(g.InvokeInterface("offer/0/take"), "contracts reachable in map modal");
            Check(g.State.Active.Contains(contract) && !g.State.Offers.Contains(contract), "actual contract added once");
            g.InvokeInterface("offer/0/take"); Check(g.State.Active.Count == 1, "stale callback cannot duplicate");
            Render(g); g.InvokeInterface("offer/0/take"); Render(g);
            Check(!g.InvokeInterface("offer/0/take") && g.State.Active.Count == GameData.MaxActiveContracts, "contract cap preserved");
            g.InvokeInterface("chart/contracts/close");
            foreach (var size in new[] { new Vector2Int(1920, 1080), new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                Render(g, size.x, size.y);
                var field = (RectTransform)g.GetComponentsInChildren<Image>().Single(i => i.name == "chart/illustrated/field").transform;
                var root = g.GetComponentInChildren<CoastalCanvas>();
                Check(Mathf.Abs(field.rect.width - root.Width) < 1 && Mathf.Abs(field.rect.height - root.Height) < 1, "edge-to-edge map at " + size);
                for (int i = 0; i < 5; i++)
                {
                    var hit = g.GetComponentsInChildren<RectTransform>().Single(t => t.name == "chart/nautical/pin/" + i);
                    Check(hit.rect.width * size.y / root.Height >= 44 && hit.rect.height * size.y / root.Height >= 44, "44pixel landmark target");
                    Vector2 p = hit.anchoredPosition;
                    Check(p.x >= 0 && p.x + hit.rect.width <= root.Width + 1 && -p.y >= 0 && -p.y + hit.rect.height <= root.Height + 1, "landmark target within screen");
                }
                Check(g.GetComponentsInChildren<IllustratedRoutesGraphic>().Length == 1, "one retained route overlay");
                Check(g.GetComponentsInChildren<ChartPinGraphic>().Length == 11, "six pins and five working navigation icons");
                foreach (var text in g.GetComponentsInChildren<Text>().Where(t => t.name.StartsWith("chart/"))) Check(text.font != null, "real supplied live fonts");
            }
            Render(g); g.State.Coins = 24850; Render(g); Check(Text(g, "chart/status/coins").text == "24,850", "wallet uses current amount");
            Check(g.InvokeInterface("chart/nav/Crew"), "crew destination works"); Render(g);
            Check(g.GetComponentsInChildren<RectTransform>().Any(t => t.name == "shop/shell"), "real crew shop opened");
            Field(g, "hudTab", VoyageGame.HudTab.HarbourMaster); Render(g);
            Check(g.InvokeInterface("chart/nav/Gear"), "gear destination works");
            Field(g, "hudTab", VoyageGame.HudTab.HarbourMaster); Render(g);
            Check(g.InvokeInterface("chart/nav/Boat"), "boat destination returns to physical harbour"); Render(g);
            Check(g.GetComponentsInChildren<RectTransform>().All(t => t.name != "chart/illustrated/field"), "closed chart hit targets/art are inactive");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] CHART CHECKS PASSED: illustrated resource/fullscreen, real focus/unlock/contracts, live status, touch bounds and working navigation");
        }
        public static void Capture()
        {
            Run(); var g = Fixture(); g.State.Coins = 200;
            System.IO.Directory.CreateDirectory(System.IO.Path.GetFullPath("Logs/chart017"));
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic);
            void Shot(string n, int w, int h) => shot.Invoke(null, new object[] { g, "../chart017/" + n, w, h, 1f });
            Shot("map-laptop", 2560, 1440); Shot("map-desktop", 1440, 900); Shot("map-phone", 844, 390);
            g.InvokeInterface("chart/nautical/pin/2"); Shot("map-sandbar", 1440, 900);
            g.InvokeInterface("chart/contracts"); Shot("map-contracts", 1440, 900);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] Snapshot written to Logs/chart017");
        }
    }
}

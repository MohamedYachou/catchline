using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    // Run only in isolated Catchline-sim. Temporary saves never target the player path.
    public static class NetEconomyChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("Net economy check failed: " + why); }
        static void Field(VoyageGame game, string key, object value) => typeof(VoyageGame).GetField(key, Hidden).SetValue(game, value);
        static void Property(VoyageGame game, string key, object value) => typeof(VoyageGame).GetProperty(key).GetSetMethod(true).Invoke(game, new[] { value });
        public static void Run()
        {
            Check(GameData.NetReplacementCost == 30 && GameData.NetInventoryCapacity == 4, "approved provisional replacement price and capacity");
            var state = new GameState(51);
            Check(state.NetInventory == 3, "new game has one fitted net and two reserves");
            state.Coins = 29;
            Check(!state.BuyNet() && state.Coins == 29 && state.NetInventory == 3, "insufficient funds change neither resource");
            state.Coins = 30;
            Check(state.BuyNet() && state.Coins == 0 && state.NetInventory == 4, "exact funds buy one usable net once");
            state.Coins = 1000;
            Check(!state.BuyNet() && state.Coins == 1000 && state.NetInventory == 4, "full rack rejects purchase without spending");
            state.NetInventory = 0; state.Coins = 30;
            Check(state.BuyNet() && state.NetInventory == 1 && state.Coins == 0, "exhausted stock can recover with replacement");
            state.NetInventory = 0; state.Coins = 150;
            for (int i = 0; i < 4; i++) Check(state.BuyNet(), "purchase up to rack capacity");
            Check(state.NetInventory == 4 && state.Coins == 30 && !state.BuyNet() && state.Coins == 30, "repeated purchases charge exactly four times");
            state.NetInventory = -1; state.Coins = 30;
            Check(!state.BuyNet() && state.NetInventory == -1 && state.Coins == 30, "invalid runtime stock cannot become a paid negative inventory");
            state.NetInventory = 0; state.Coins = -1;
            Check(!state.BuyNet() && state.NetInventory == 0 && state.Coins == -1, "negative funds cannot purchase");
            state.Hull = 0; state.Coins = 30;
            Check(state.BuyNet() && state.Coins == 0 && state.NetInventory == 1, "domain follows other supplies without embedding harbour/hull mode");

            string path = Path.Combine(Path.GetTempPath(), "catchline-net-economy-" + Guid.NewGuid().ToString("N") + ".json");
            try
            {
                for (int inventory = 0; inventory <= GameData.NetInventoryCapacity; inventory++)
                {
                    state.Hull = 2; state.Coins = 123; state.NetInventory = inventory;
                    state.Save(path); var loaded = GameState.Load(path);
                    Check(loaded != null && loaded.NetInventory == inventory && loaded.Coins == 123 && loaded.Hull == 2, "each saved stock including exhausted zero round trips");
                }
                string json = File.ReadAllText(path);
                File.WriteAllText(path, Regex.Replace(json, "\"NetInventory\"\\s*:\\s*-?\\d+", "\"NetInventory\":999"));
                Check(GameState.Load(path)?.NetInventory == 4, "oversize saved stock clamps to capacity");
                File.WriteAllText(path, Regex.Replace(json, "\"NetInventory\"\\s*:\\s*-?\\d+", "\"NetInventory\":-2"));
                Check(GameState.Load(path)?.NetInventory == 0, "negative saved stock clamps to zero");
                // Existing Version1 saves predate net stock; this must not treat missing as exhausted.
                File.WriteAllText(path, "{\"Version\":1,\"Coins\":400,\"Bait\":15,\"Voyage\":3,\"FoodMinutes\":4,\"Owned\":[],\"Charts\":[],\"Board\":[],\"Offers\":[],\"Active\":[]}");
                var legacy = GameState.Load(path);
                Check(legacy != null && legacy.Hull == 0 && legacy.Coins == 400 && legacy.NetInventory == 3, "legacy save receives default stock without migrating hull or coins");
                legacy.NetInventory = 0; legacy.Save(path);
                Check(GameState.Load(path)?.NetInventory == 0, "legacy migration then exhausted save cannot replenish itself");
            }
            finally { if (File.Exists(path)) File.Delete(path); }

            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Isolated replacement-net supplies").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.AutoPlay = false; game.Build();
            Property(game, "State", new GameState(18) { Hull = 2, NetInventory = 3, Coins = 29 });
            typeof(VoyageGame).GetMethod("RebuildBoat", Hidden).Invoke(game, new object[] { true });
            Property(game, "CurrentMode", VoyageGame.Mode.Harbour);
            Field(game, "showTitle", false); Field(game, "paused", false); Field(game, "panelOpen", true);
            Field(game, "hudTab", VoyageGame.HudTab.Supplies); Field(game, "toastUntil", 0f);
            void Render() { game.PrepareInterface(1440, 900, 1); Canvas.ForceUpdateCanvases(); }
            Render();
            Check(!game.InvokeInterface("supplies/net/buy") && game.State.NetInventory == 3 && game.State.Coins == 29, "native supplies control disabled without money");
            game.State.Coins = 30; Render();
            Check(game.InvokeInterface("supplies/net/buy") && game.State.NetInventory == 4 && game.State.Coins == 0, "native supplies action buys exact replacement");
            game.State.Coins = 1000; Render();
            Check(!game.InvokeInterface("supplies/net/buy") && game.State.Coins == 1000, "native full-rack control disabled");
            var catalog = game.GetComponentsInChildren<RectTransform>().Single(t => t.name == "catalog/Supplies/content");
            var footer = game.GetComponentsInChildren<RectTransform>().Single(t => t.name == "supplies/preference");
            float footerBottom = -footer.anchoredPosition.y + footer.rect.height;
            Check(catalog.rect.height >= footerBottom, "exact product count still includes scrollable footer");
            Property(game, "CurrentMode", VoyageGame.Mode.Fishing); Render();
            Check(!game.InvokeInterface("supplies/net/buy"), "shop purchase not available through sea UI");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] NET ECONOMY CHECKS PASSED: price/default/cap, exact purchase, zero recovery, migration/save bounds and native harbour-only supplies");
        }
    }
}

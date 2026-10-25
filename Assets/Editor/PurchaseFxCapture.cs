using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    // Session-only production shop actions, with a deterministic presentation clock for capture.
    public static class PurchaseFxCapture
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static readonly string Out = Path.GetFullPath("../Catchline/docs/screens/purchase-fx");
        static int checks;
        static float captureAt;
        static object Field(VoyageGame g, string name) => typeof(VoyageGame).GetField(name, Hidden).GetValue(g);
        static void Set(VoyageGame g, string name, object value) => typeof(VoyageGame).GetField(name, Hidden).SetValue(g, value);
        static void Check(bool ok, string why)
        { checks++; if (!ok) throw new Exception("[Catchline] PURCHASE FX failed: " + why); }
        static Image Image(CoastalCanvas ui, string id) => ui.Root.Cast<Transform>().First(t => t.name == id).GetComponent<Image>();

        public static void Run()
        {
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name == "Catchline-sim", "assigned isolated scratch only");
            Directory.CreateDirectory(Out); ArtImport.BuildLibrary();
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            foreach (bool buy in new[] { true, false })
            {
                var g = Fixture();
                try
                {
                    Set(g, "hudTab", buy ? VoyageGame.HudTab.Supplies : VoyageGame.HudTab.Market);
                    if (!buy)
                        for (int i = 0; i < 9; i++) g.State.UnsoldCatch.Add(new CaughtFish { Species = Species.Mackerel, Kg = .6f + i * .05f });
                    At(g, size, 100);
                    int before = g.State.Coins;
                    Check(g.InvokeInterface(buy ? "shop/buy" : "market/sell"), "real transaction button invokes");
                    Check(buy ? g.State.Coins < before : g.State.Coins > before, "real transaction changes balance");
                    int after = g.State.Coins;
                    Check((bool)Field(g, "coinFxSpend") == buy, "real transaction starts correct flight");
                    var ui = g.GetComponentInChildren<CoastalCanvas>();
                    string id = buy ? "coinfx/burst" : "coinfx/glint";
                    At(g, size, .67f);
                    Check(!ui.TryFind(id, out _), "no contact effect before landing");
                    float previousWidth = 0, previousAlpha = 1;
                    foreach (float at in buy ? new[] { .76f, .93f, 1.1f } : new[] { 1.37f, 1.44f, 1.51f })
                    {
                        At(g, size, at);
                        Check(ui.TryFind(id, out var rect), "contact visible at " + at);
                        var image = Image(ui, id);
                        Check(image.sprite != null && image.sprite.name == (buy ? "fx-buy-burst" : "fx-coin-glint"), "accepted art imported");
                        Check(rect.width > previousWidth && image.color.a < previousAlpha, "contact grows and fades");
                        Check(!image.raycastTarget, "effect does not block actions");
                        Vector2 anchor;
                        if (buy)
                        {
                            Check(ui.TryFind((string)Field(g, "coinFxTarget"), out var target), "bought target remains visible");
                            anchor = target.center;
                            Check(ui.TryFind("coinfx/flash", out _), "original gold glow preserved");
                            Check(image.transform.GetSiblingIndex() > Image(ui, "coinfx/flash").transform.GetSiblingIndex(), "burst draws above glow");
                            Check(!ui.TryFind("coinfx/glint", out _), "purchase has no sale glint");
                        }
                        else
                        {
                            string walletId = ui.TryFind("shop/coins", out _) ? "shop/coins" : "port/coins";
                            Check(ui.TryFind(walletId, out var wallet), "wallet target visible");
                            Check(ui.TryFind(walletId + "/coin", out var coinIcon), "actual wallet coin icon visible");
                            anchor = coinIcon.center;
                            Check(ui.Root.Cast<Transform>().Count(t => t.name == id && t.gameObject.activeSelf) == 1, "one visible glint only");
                            Check(!ui.TryFind("coinfx/burst", out _), "sale has no purchase burst");
                        }
                        Check(Vector2.Distance(rect.center, anchor) < .2f, "contact centre matches destination: buy=" + buy + " at=" + at + " error=" + Vector2.Distance(rect.center, anchor));
                        previousWidth = rect.width; previousAlpha = image.color.a;
                        if (at == (buy ? .93f : 1.44f))
                        { captureAt = at; Shot(g, (buy ? "buy-" : "sell-") + size.x, size); }
                    }
                    if (!buy)
                    {
                        // Early consecutive contacts restart the same retained glint instead of stacking.
                        At(g, size, .72f); Check(ui.TryFind(id, out _), "first sale landing flashes");
                        At(g, size, .82f); Check(ui.TryFind(id, out _), "subsequent sale landing flashes");
                        Check(ui.Root.Cast<Transform>().Count(t => t.name == id && t.gameObject.activeSelf) == 1, "overlapping arrivals share one glint");
                    }
                    At(g, size, buy ? 1.18f : 1.58f);
                    Check(!ui.TryFind(id, out _), "contact hides after lifetime including final tail");
                    Check(g.State.Coins == after, "presentation leaves transaction balance unchanged");
                }
                finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }
            }
            File.WriteAllText(Path.Combine(Out, "checks.json"), "{\"passed\":true,\"assertions\":" + checks + "}");
            Debug.Log("[Catchline] PURCHASE FX CHECKS PASSED: " + checks);
            Debug.Log("[Catchline] Snapshot written to " + Out);
        }

        static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("Purchase capture - no save"); go.SetActive(false);
            var g = go.AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build(); go.SetActive(true);
            Set(g, "showTitle", false);
            g.State.Hull = 2; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", Hidden).Invoke(g, new object[] { false });
            for (int i = 0; i < 60; i++) g.Tick(.05f);
            g.State.Tutorial = (int)VoyageGame.TutStep.Done; g.State.Coins = 5000;
            Set(g, "panelOpen", true);
            return g;
        }

        static void At(VoyageGame g, Vector2Int size, float at)
        {
            g.Cam.aspect = size.x / (float)size.y;
            Set(g, "coinFxStart", Time.unscaledTime - at);
            g.PrepareInterface(size.x, size.y, 1); Canvas.ForceUpdateCanvases();
            Set(g, "coinFxStart", Time.unscaledTime - at);
            g.PrepareInterface(size.x, size.y, 1);
        }

        static void Shot(VoyageGame g, string file, Vector2Int size)
        {
            var rt = new RenderTexture(size.x, size.y, 24, RenderTextureFormat.ARGB32);
            var ui = new RenderTexture(size.x, size.y, 24, RenderTextureFormat.ARGB32);
            var composite = new Material(Shader.Find("Hidden/Catchline/Coastal UI Composite"));
            var texture = new Texture2D(size.x, size.y, TextureFormat.RGB24, false);
            var previous = RenderTexture.active; var target = g.Cam.targetTexture;
            try
            {
                g.Cam.targetTexture = rt; At(g, size, captureAt);
                RenderPipeline.SubmitRenderRequest(g.Cam, new RenderPipeline.StandardRequest { destination = rt });
                g.GetComponentInChildren<CoastalCanvas>().RenderCapture(ui);
                Graphics.Blit(ui, rt, composite);
                RenderTexture.active = rt; texture.ReadPixels(new Rect(0, 0, size.x, size.y), 0, 0); texture.Apply();
                File.WriteAllBytes(Path.Combine(Out, file + ".png"), texture.EncodeToPNG());
            }
            finally
            {
                RenderTexture.active = previous; g.Cam.targetTexture = target;
                UnityEngine.Object.DestroyImmediate(texture); UnityEngine.Object.DestroyImmediate(rt);
                UnityEngine.Object.DestroyImmediate(ui); UnityEngine.Object.DestroyImmediate(composite);
            }
        }
    }
}

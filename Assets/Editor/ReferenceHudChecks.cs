using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    // Run in a released scratch project only. SessionOnly fixtures never touch Mo's save.
    public static class ReferenceHudChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string reason) { if (!ok) throw new Exception("Reference HUD check failed: " + reason); }
        static void Set(VoyageGame game, string key, object value) => typeof(VoyageGame).GetField(key, Hidden).SetValue(game, value);
        static VoyageGame Fixture()
        {
            var game = new GameObject("Isolated fish reference HUD").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build(); Set(game, "showTitle", false);
            game.Showcase(0, 0); game.Tick(.01f); game.PrepareInterface(1672, 941, 1);
            return game;
        }
        static Text Text(VoyageGame game, string id) => game.GetComponentsInChildren<Text>().Single(t => t.name == id);
        static RectTransform Rect(VoyageGame game, string id) => game.GetComponentsInChildren<RectTransform>().Single(t => t.name == id);
        static void Inside(VoyageGame game, string child, string parent)
        {
            var c = Rect(game, child); var p = Rect(game, parent);
            var corners = new Vector3[4]; c.GetWorldCorners(corners);
            foreach (var corner in corners)
            {
                var q = p.InverseTransformPoint(corner);
                Check(q.x >= p.rect.xMin - 1 && q.x <= p.rect.xMax + 1 && q.y >= p.rect.yMin - 1 && q.y <= p.rect.yMax + 1,
                    child + " remains in its containing panel");
            }
        }
        public static void Run()
        {
            ArtImport.BuildLibrary();
            var game = Fixture();
            game.State.Coins = 2845; game.Tick(0); game.PrepareInterface(1672, 941, 1);
            Check(Text(game, "voyage/status/coins").text == "2,845", "wallet uses real state at reference value");
            game.State.Coins += 29; game.Tick(0);
            Check(Text(game, "voyage/status/coins").text == "2,874", "wallet updates after a state change");
            game.State.Coins = int.MaxValue; game.Tick(0);
            Check(Text(game, "voyage/status/coins").text.Length <= 7, "huge balance remains bounded");
            game.State.Active.Clear();
            game.State.Active.Add(new Contract { Species = Species.Herring, Count = 3, Delivered = 0, VoyagesLeft = 2, Reward = 10 });
            game.Cooler.Add(new CaughtFish { Species = Species.Herring, Kg = .2f, StowedAt = game.SimTime }); game.Tick(0);
            Check(Text(game, "voyage/goal/value").text.Contains("0/3"), "unsold fish cannot falsely complete delivered goal");
            game.State.Active[0].Delivered = 2; game.Tick(0);
            Check(Text(game, "voyage/goal/value").text.Contains("2/3"), "actual delivered progress updates");
            game.State.Active.Clear(); game.State.BestVoyageKg = 0; game.Tick(0);
            Check(Text(game, "voyage/goal/value").text == $"Goal: bring home a full {GameData.SkiffKgGoal:0} kg haul", "no-contract haul requirement preserved");
            game.State.BestVoyageKg = GameData.SkiffKgGoal; game.State.Coins = GameData.SkiffCost; game.Tick(0);
            Check(Text(game, "voyage/goal/value").text == "Goal: skiff refit ready", "existing ready state is exposed without executing refit");
            Check(game.State.Hull == 0, "HUD does not buy or mutate hull");
            foreach (var size in new[] { new Vector2Int(1672, 941), new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                game.PrepareInterface(size.x, size.y, 1); Canvas.ForceUpdateCanvases();
                Inside(game, "voyage/status/coins", "voyage/status");
                Inside(game, "voyage/goal/value", "voyage/goal");
                Inside(game, "voyage/crew/title", "voyage/crew");
                Inside(game, "voyage/crew/0", "voyage/crew");
                var labels = game.GetComponentsInChildren<Text>().Where(t => t.name.StartsWith("voyage/")).ToArray();
                Check(labels.Length > 0 && labels.All(t => t.font != null), "all live labels use a real imported font");
                Check(game.GetComponentsInChildren<Image>().Where(i => i.name == "voyage/status" || i.name == "voyage/goal").All(i => i.sprite != null), "live status and goal use supplied kit art");
            }
            game.PrepareInterface(844, 390, 1.15f);
            int largerType = Text(game, "voyage/goal/value").fontSize;
            Check(largerType > 0, "larger type uses live scalable goal");
            game.PrepareInterface(844, 390, 1);
            Check(Text(game, "voyage/goal/value").fontSize < largerType, "switching back restores normal live type size");
            Check(!game.GetComponentsInChildren<Text>().Any(t => t.name.StartsWith("reference/")), "retired reference HUD remains inactive");
            var canvas = game.GetComponentInChildren<CoastalCanvas>().GetComponent<Canvas>();
            // v2 Pressable expands the raycast child instead of stretching the artwork.
            var pauseHit = game.GetComponentsInChildren<RectTransform>().SingleOrDefault(t => t.name == "pause/hit") ?? Rect(game, "pause");
            Check(pauseHit.GetComponent<Image>().raycastTarget && pauseHit.rect.width * canvas.scaleFactor >= 43.9f && pauseHit.rect.height * canvas.scaleFactor >= 43.9f,
                "phone pause hit target remains44physical pixels without stretching icon");
            Check(game.InvokeInterface("pause"), "source hamburger invokes existing pause action");
            Check((bool)typeof(VoyageGame).GetField("paused", Hidden).GetValue(game), "pause control actually pauses game");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] REFERENCE HUD CHECKS PASSED (live state/assets/containment/retained pause; physical input and visual match separate)");
        }
        static void Shot(VoyageGame game, string filename, int width, int height, float type = 1)
        {
            game.PrepareInterface(width, height, type); game.Cam.aspect = width / (float)height;
            Canvas.ForceUpdateCanvases();
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            var ui = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            var oldTarget = game.Cam.targetTexture; var oldActive = RenderTexture.active;
            var composite = new Material(Shader.Find("Hidden/Catchline/Coastal UI Composite"));
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
            try
            {
                game.Cam.targetTexture = rt;
                var request = new RenderPipeline.StandardRequest { destination = rt };
                RenderPipeline.SubmitRenderRequest(game.Cam, request);
                game.GetComponentInChildren<CoastalCanvas>().RenderCapture(ui);
                Graphics.Blit(ui, rt, composite);
                RenderTexture.active = rt;
                texture.ReadPixels(new Rect(0, 0, width, height), 0, 0); texture.Apply();
                string folder = Path.GetFullPath("Logs/ui024"); Directory.CreateDirectory(folder);
                File.WriteAllBytes(Path.Combine(folder, filename + ".png"), texture.EncodeToPNG());
                // Capture the real production Canvas separately for overlay comparisons.
                RenderTexture.active = ui; texture.ReadPixels(new Rect(0, 0, width, height), 0, 0); texture.Apply();
                File.WriteAllBytes(Path.Combine(folder, filename + "-ui.png"), texture.EncodeToPNG());
            }
            finally
            {
                game.Cam.targetTexture = oldTarget; RenderTexture.active = oldActive;
                UnityEngine.Object.DestroyImmediate(rt); UnityEngine.Object.DestroyImmediate(ui);
                UnityEngine.Object.DestroyImmediate(composite); UnityEngine.Object.DestroyImmediate(texture);
            }
        }
        public static void Capture()
        {
            ArtImport.BuildLibrary();
            Run();
            var game = Fixture(); game.State.Coins = 2845;
            Shot(game, "reference-1672", 1672, 941);
            Shot(game, "desktop-1440", 1440, 900);
            Shot(game, "phone-844", 844, 390);
            Shot(game, "phone-large", 844, 390, 1.15f);
            game.CommandRod(game.Rods[0]);
            for (int i = 0; i < 600 && game.MinigameRod?.State != RodState.Bite; i++) game.Tick(.05f);
            Check(game.MinigameRod?.State == RodState.Bite, "native bite fixture reaches real fishing state");
            Shot(game, "bite-phone", 844, 390);
            game.StrikeTap();
            for (int i = 0; i < 300 && game.Stats.Landed == 0; i++) game.Tick(.05f);
            Shot(game, "catch-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] Snapshot written to Logs/ui024 (real Canvas+world and transparent UI pairs; Mo visual acceptance pending)");
        }
    }
}

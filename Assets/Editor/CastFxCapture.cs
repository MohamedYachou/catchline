using System;
using System.Collections;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.EditorTools
{
    // Scratch-only, session-only production casts and production Canvas composites; no player save.
    public static class CastFxCapture
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static readonly string Out = Path.GetFullPath("../Catchline/docs/screens/cast-fx");
        static int checks;
        static object Field(VoyageGame g, string name) => typeof(VoyageGame).GetField(name, Hidden).GetValue(g);
        static object Call(VoyageGame g, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Hidden).Invoke(g, args);
        static void Check(bool ok, string why)
        { checks++; if (!ok) throw new Exception("[Catchline] CAST FX failed: " + why); }
        static void Until(VoyageGame g, Func<bool> done, float seconds, string why)
        { for (float t = 0; t < seconds && !done(); t += .01f) g.Tick(.01f); Check(done(), why); }

        public static void Run()
        {
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name == "Catchline-sim", "isolated assigned scratch only");
            Directory.CreateDirectory(Out);
            ArtImport.BuildLibrary();
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                var g = Fixture();
                try
                {
                    var rod = g.Rods[0];
                    g.CommandRod(rod);
                    Until(g, () => rod.State == RodState.Flying && rod.Reading != null, 25, "captain casts through real path");
                    Until(g, () => rod.State == RodState.Waiting, 3, "captain lands");
                    var events = (IDictionary)Field(g, "castFx");
                    Check(events.Contains(rod), "captain landing records effect");
                    object landing = events[rod];
                    float born = (float)landing.GetType().GetField("Item1").GetValue(landing);
                    var point = (Vector3)landing.GetType().GetField("Item2").GetValue(landing);
                    Check(Vector3.Distance(point, rod.CastTarget) < .001f, "exact cast landing world point");
                    float previousWidth = 0, previousAlpha = 1;
                    foreach (float at in new[] { .1f, .3f, .6f })
                    {
                        g.Tick(Mathf.Max(0, born + at - g.SimTime));
                        Frame(g, size);
                        var ui = g.GetComponentInChildren<CoastalCanvas>();
                        string id = "castfx/" + rod.Index + "/ring";
                        Check(ui.TryFind(id, out var rect), "ring visible at " + at + " / " + size.x);
                        var view = g.Cam.WorldToViewportPoint(point);
                        Check(Vector2.Distance(rect.center, new Vector2(view.x * ui.Width, (1 - view.y) * ui.Height)) < .1f,
                            "ring anchored to projected water point at " + at);
                        var image = ui.Root.Cast<Transform>().First(t => t.name == id).GetComponent<UnityEngine.UI.Image>();
                        Check(rect.width > previousWidth && image.color.a < previousAlpha, "expands and fades at " + at);
                        Check(image.sprite != null && image.sprite.name == "fx-cast-ring", "accepted ring art imported");
                        Check(ui.TryFind("castfx/" + rod.Index + "/drops", out _) == (at < .32f), "short droplet pop lifetime");
                        previousWidth = rect.width; previousAlpha = image.color.a;
                        Shot(g, "cast-" + size.x + "-" + Mathf.RoundToInt(at * 10), size);
                    }
                    // Move the camera without moving the world point; the same event must project to its new location.
                    var canvas = g.GetComponentInChildren<CoastalCanvas>();
                    canvas.TryFind("castfx/" + rod.Index + "/ring", out var before);
                    g.Cam.transform.position += g.Cam.transform.right * .4f;
                    Frame(g, size);
                    Check(canvas.TryFind("castfx/" + rod.Index + "/ring", out var after) && Vector2.Distance(before.center, after.center) > 1,
                        "camera movement reprojects ring");
                    var moved = g.Cam.WorldToViewportPoint(point);
                    Check(Vector2.Distance(after.center, new Vector2(moved.x * canvas.Width, (1 - moved.y) * canvas.Height)) < .1f, "moved camera still anchored");
                    g.Tick(.12f); Frame(g, size);
                    Check(!canvas.TryFind("castfx/" + rod.Index + "/ring", out _), "ring hidden after .7 seconds");
                    Check(events[rod].Equals(landing), "Waiting does not retrigger landing");
                    // Exercise the deck/crew clock too, without entering a second captain close-up.
                    g.ReelInRodView();
                    Until(g, () => !g.RodViewActive, 8, "captain view exits");
                    rod.State = RodState.Ready;
                    rod.Cast(g, .5f);
                    Check(rod.Reading == null && rod.State == RodState.Flying, "deck cast path");
                    Until(g, () => rod.State == RodState.Waiting, 3, "deck cast lands");
                    Check(events.Contains(rod) && !events[rod].Equals(landing), "deck landing records fresh effect");
                    g.Tick(.1f); Frame(g, size);
                    Check(canvas.TryFind("castfx/" + rod.Index + "/ring", out _), "deck ring visible");
                    Shot(g, "deck-" + size.x, size);
                }
                finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }
            }
            File.WriteAllText(Path.Combine(Out, "checks.json"), "{\"passed\":true,\"assertions\":" + checks + "}");
            Debug.Log("[Catchline] CAST FX CHECKS PASSED: " + checks);
            Debug.Log("[Catchline] Snapshot written to " + Out);
        }

        static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("Cast splash capture - no save"); go.SetActive(false);
            var g = go.AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build(); go.SetActive(true);
            typeof(VoyageGame).GetField("showTitle", Hidden).SetValue(g, false);
            Call(g, "StartTestTier", 0); g.SetSail();
            Until(g, () => g.CurrentMode == VoyageGame.Mode.Fishing, 200, "arrive at ground");
            g.Tick(3);
            return g;
        }

        static void Frame(VoyageGame g, Vector2Int size)
        {
            g.Cam.aspect = size.x / (float)size.y;
            g.PrepareInterface(size.x, size.y, 1);
            Canvas.ForceUpdateCanvases();
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
                g.Cam.targetTexture = rt; Frame(g, size);
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

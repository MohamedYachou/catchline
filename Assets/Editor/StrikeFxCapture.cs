using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.Rendering;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    public static class StrikeFxCapture
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static readonly string Out = Path.GetFullPath("../Catchline/docs/screens/strike-fx");
        static int checks;
        static object Field(VoyageGame g, string name) => typeof(VoyageGame).GetField(name, Hidden).GetValue(g);
        static object Call(VoyageGame g, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Hidden).Invoke(g, args);
        static void Check(bool ok, string why)
        { checks++; if (!ok) throw new Exception("[Catchline] STRIKE FX failed: " + why); }
        static void UpdateInput() => InputSystem.Update();
        static void Until(VoyageGame g, Func<bool> done, float seconds, string why)
        { for (float t = 0; t < seconds && !done(); t += .01f) g.Tick(.01f); Check(done(), why); }
        static Image Image(CoastalCanvas ui, string id) => ui.Root.Cast<Transform>().First(t => t.name == id).GetComponent<Image>();

        public static void Run()
        {
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name == "Catchline-sim", "isolated assigned scratch only");
            Directory.CreateDirectory(Out);
            var updateMode = InputSystem.settings.updateMode;
            InputSystem.settings.updateMode = InputSettings.UpdateMode.ProcessEventsManually;
            // Same player-update opt-in used by Input System's edit-mode test fixtures.
            var manager = typeof(InputSystem).GetField("s_Manager", BindingFlags.Static | BindingFlags.NonPublic).GetValue(null);
            var editUpdates = manager.GetType().GetProperty("runPlayerUpdatesInEditMode");
            bool previousEditUpdates = (bool)editUpdates.GetValue(manager);
            editUpdates.SetValue(manager, true);
            var mouse = InputSystem.AddDevice<Mouse>();
            try
            {
                UpdateInput();
                _ = mouse.press.wasPressedThisFrame;
                InputState.Change(mouse, new MouseState().WithButton(MouseButton.Left), InputUpdateType.Manual);
                mouse.MakeCurrent();
                Check(mouse.press.wasPressedThisFrame, "manual input preflight press edge");
                UpdateInput(); InputState.Change(mouse, new MouseState(), InputUpdateType.Manual);
                Debug.Log("[Catchline] STRIKE FX INPUT PREFLIGHT PASSED");
                ArtImport.BuildLibrary();
                foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
                {
                    var g = Fixture();
                    try
                    {
                        var rod = g.Manning;
                        Until(g, () => rod.State == RodState.Waiting, 3, "cast lands"); Frame(g, size);
                        var ui = g.GetComponentInChildren<CoastalCanvas>();
                        Check(!ui.TryFind("strikefx/burst", out _), "no TAP cue while waiting");
                        Until(g, () => rod.State == RodState.Bite, 35, "real model reaches take");
                        g.Tick(.08f); Frame(g, size);
                        Check(ui.TryFind("strikefx/burst", out var burst), "bite draws burst");
                        Check(Image(ui, "strikefx/burst").sprite.name == "fx-tap-burst", "accepted burst imported");
                        var label = ui.Root.GetComponentsInChildren<Text>().First(t => t.name == "strikefx/label");
                        Check(label.text == "TAP!" && label.color == Skin.Ink && !label.raycastTarget, "display TAP label uses ink and is nonblocking");
                        var bobber = (Vector2)Call(g, "StrikeBobberPoint");
                        Check(ui.TryFind("strikefx/bobber-ring", out var ring) && Vector2.Distance(ring.center, bobber) < .2f, "ring follows water-plane bobber");
                        Check(burst.xMin > ring.xMax || burst.xMax < ring.xMin, "burst sits beside bobber ring; burst=" + burst + " ring=" + ring + " canvas=" + ui.Width + "x" + ui.Height);
                        Check(burst.xMin > 0 && burst.xMax < ui.Width && burst.yMin > 0 && burst.yMax < ui.Height, "burst stays inside view");
                        float pulse = Image(ui, "strikefx/burst").transform.localScale.x;
                        Check(pulse >= 1 && pulse <= 1.08f, "gentle pulse bound");
                        Shot(g, "bite-" + size.x, size);
                        g.Tick(.10f); Frame(g, size);
                        Check(Mathf.Abs(Image(ui, "strikefx/burst").transform.localScale.x - pulse) > .0001f, "pulse evolves over time");

                        // Inject a real press away from the bobber; the production StrikeTap hook records it.
                        var screen = new Vector2(Screen.width * .34f, Screen.height * .56f);
                        UpdateInput();
                        _ = mouse.press.wasPressedThisFrame; // Enable edge tracking before the first synthetic press.
                        InputState.Change(mouse, new MouseState { position = screen }.WithButton(MouseButton.Left), InputUpdateType.Manual);
                        mouse.MakeCurrent();
                        Check(UnityEngine.InputSystem.Pointer.current == mouse && mouse.press.wasPressedThisFrame,
                            "injected mouse is current pressed pointer; current=" + (UnityEngine.InputSystem.Pointer.current == mouse)
                            + " pressed=" + mouse.press.isPressed + " updated=" + mouse.wasUpdatedThisFrame + " edge=" + mouse.press.wasPressedThisFrame);
                        var expected = (Vector2)Call(g, "ToGui", screen);
                        var viewport = (Rect)typeof(VoyageGame).GetProperty("HudViewport", Hidden).GetValue(g);
                        float height = viewport.height < 600 ? 480 : 720;
                        var normal = expected / new Vector2(viewport.width / (viewport.height / height), height);
                        var before = rod.Reading;
                        int landed = g.Stats.Landed;
                        g.StrikeTap();
                        Check(rod.Reading == before && rod.ReadingResult == StrikeResult.Hooked, "real strike still hooks same fish");
                        Check(Mathf.Abs((float)Field(g, "strikeFxBorn") - g.SimTime) < .001f, "strike hook records simulated clock");
                        UpdateInput(); InputState.Change(mouse, new MouseState { position = screen }, InputUpdateType.Manual);
                        float previousWidth = 0, previousAlpha = 1, previousAt = 0;
                        foreach (float at in new[] { .05f, .2f, .4f })
                        {
                            g.Tick(at - previousAt); previousAt = at; Frame(g, size);
                            Check(!ui.TryFind("strikefx/burst", out _), "TAP cue hides after strike");
                            Check(ui.TryFind("strikefx/ripple", out var ripple), "ripple visible at " + at);
                            var image = Image(ui, "strikefx/ripple");
                            Check(image.sprite.name == "fx-tap-ripple" && !image.raycastTarget, "accepted ripple nonblocking");
                            Check(Mathf.Abs(ripple.width - ripple.height) < .01f, "ripple stays round");
                            Check(Vector2.Distance(ripple.center, normal * new Vector2(ui.Width, ui.Height)) < .2f, "ripple stays at actual tap point: actual=" + ripple.center + " expected=" + normal * new Vector2(ui.Width, ui.Height) + " stored=" + Field(g, "strikeFxPoint"));
                            Check(ripple.width > previousWidth && image.color.a < previousAlpha, "ripple grows and fades");
                            Check(!ui.TryFind("strikefx/bobber-ring", out _), "idle bobber ring hides on strike");
                            previousWidth = ripple.width; previousAlpha = image.color.a;
                            if (at == .2f) Shot(g, "ripple-" + size.x, size);
                        }
                        float born = (float)Field(g, "strikeFxBorn"); g.StrikeTap();
                        Check((float)Field(g, "strikeFxBorn") == born, "ignored repeat strike cannot retrigger ripple");
                        g.Tick(.08f); Frame(g, size);
                        Check(!ui.TryFind("strikefx/ripple", out _), "ripple expires after .45 seconds");
                        Check(g.Stats.Landed == landed, "presentation does not deliver fish early");
                    }
                    finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }

                    var early = Fixture();
                    try
                    {
                        Until(early, () => early.Manning.State == RodState.Waiting, 3, "early cast lands");
                        Frame(early, size); var bobber = (Vector2)Call(early, "StrikeBobberPoint");
                        var ui = early.GetComponentInChildren<CoastalCanvas>();
                        var rod = early.Manning; early.StrikeTap(); Frame(early, size);
                        Check(rod.ReadingResult == StrikeResult.TooEarly, "early strike model unchanged");
                        Check(ui.TryFind("strikefx/ripple", out var r) && Vector2.Distance(r.center, bobber) < .2f, "programmatic strike falls back to bobber");
                    }
                    finally { UnityEngine.Object.DestroyImmediate(early.gameObject); }
                }
            }
            finally
            {
                InputSystem.RemoveDevice(mouse);
                editUpdates.SetValue(manager, previousEditUpdates);
                InputSystem.settings.updateMode = updateMode;
            }
            File.WriteAllText(Path.Combine(Out, "checks.json"), "{\"passed\":true,\"assertions\":" + checks + "}");
            Debug.Log("[Catchline] STRIKE FX CHECKS PASSED: " + checks);
            Debug.Log("[Catchline] Snapshot written to " + Out);
        }

        static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("Strike capture - no save"); go.SetActive(false);
            var g = go.AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build(); go.SetActive(true);
            typeof(VoyageGame).GetField("showTitle", Hidden).SetValue(g, false);
            Check(g.StageFishViewCapture(), "deterministic production fish fixture");
            g.State.Tutorial = (int)VoyageGame.TutStep.Done;
            return g;
        }

        static void Frame(VoyageGame g, Vector2Int size)
        {
            g.Cam.aspect = size.x / (float)size.y;
            g.PrepareInterface(size.x, size.y, 1); Canvas.ForceUpdateCanvases();
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

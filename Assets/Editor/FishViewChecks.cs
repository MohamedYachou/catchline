using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class FishViewChecks
    {
        const BindingFlags Private = BindingFlags.NonPublic | BindingFlags.Instance;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("[Catchline] FISH VIEW failed: " + why); }
        static void Until(VoyageGame g, Func<bool> done, float seconds, string why)
        { for (float t = 0; t < seconds && !done(); t += .025f) g.Tick(.025f); Check(done(), why); }
        static object Call(VoyageGame g, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Private).Invoke(g, args);

        public static VoyageGame Fixture()
        {
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name == "Catchline-lead-sim", "assigned scratch only");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("FISH-VIEW-1 no save"); go.SetActive(false);
            var g = go.AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build(); go.SetActive(true);
            Call(g, "StartTestTier", 0); g.SetSail();
            Until(g, () => g.CurrentMode == VoyageGame.Mode.Fishing, 200, "arrive at fishing ground");
            g.Tick(3); g.CommandRod(g.Rods[0]);
            Until(g, () => g.Rods[0].Reading != null, 25, "captain baits and casts through real path");
            return g;
        }

        public static void Preview()
        {
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name == "Catchline-lead-sim", "assigned scratch only");
            ArtImport.BuildLibrary();
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                var g = Fixture();
                Check(g.StageFishViewCapture(), "capture cod fixture");
                Shot("start"); g.Tick(.6f); Shot("cast-mid"); g.Tick(.65f);
                var r = g.Manning;
                Until(g, () => r.Reading.Phase == FishPhase.Inspect, 12, "inspect"); Shot("waiting");
                Until(g, () => r.Reading.Phase == FishPhase.Fake && r.Reading.RodPull > .35f, 20, "fake"); Shot("fake");
                Until(g, () => r.Reading.Phase == FishPhase.Take, 20, "take"); g.Tick(.2f); Shot("take");
                g.StrikeTap(); g.Tick(r.ThrashSeconds + .85f); Shot("lifted");
                void Shot(string name)
                {
                    string folder = Path.GetFullPath("../Catchline/docs/screens/fish-view-1/preview"); Directory.CreateDirectory(folder);
                    g.Cam.aspect = size.x / (float)size.y;
                    g.PrepareInterface(size.x, size.y); Call(g, "Visual", 0f);
                    var render = (System.Collections.IEnumerator)Call(g, "CompositeFrame", folder, name + "-" + size.x, size);
                    while (render.MoveNext()) { }
                    Debug.Log("[Catchline] FISH VIEW preview " + name + "-" + size.x);
                }
            }
        }

        [MenuItem("Catchline/Fish View/Checks (scratch only)")]
        public static void Run()
        {
            FishRodImport.Prepare(); ArtImport.BuildLibrary(); Debug.Log("[Catchline] " + BiteModelChecks.Run());
            CheckImportedRod();
            CheckCaughtMouth();
            var shader = Resources.Load<Shader>("RodBend");
            Check(shader != null && !ShaderUtil.ShaderHasError(shader), "rod bend URP shader");
            foreach (int scenario in new[] { 0, 1, 2, 3, 4 })
            {
                var g = Fixture(); var rod = g.Rods[0]; int bait = g.State.Bait;
                int landed = g.Stats.Landed, spooked = g.Stats.Spooked, missed = g.Stats.Missed;
                var species = rod.HookedSpecies; float kg = rod.HookedKg;
                Check(g.RodViewActive && rod.State == RodState.Flying && rod.Reading != null, "captain model on cast");
                var cameraStart = g.Cam.transform.position;
                g.Tick(.6f);
                Check(Vector3.Distance(cameraStart, g.Cam.transform.position) > .1f, "camera moves during cast");
                Check(g.RodViewDeckOpacity == 0, "deck fades within .4s");
                g.Tick(.65f); g.PrepareInterface(1440, 900);
                var visible = g.GetComponentsInChildren<Transform>(false);
                Check(!visible.Any(t => t.name.StartsWith("strike/") || t.name == "strike"), "no old strike slab/sprites/bars");
                Check(visible.Any(t => t.name == "rodview/reel-in") && visible.Any(t => t.name == "rodview/pause"), "only rod controls present");
                if (scenario == 0)
                {
                    Until(g, () => rod.Reading?.Phase == FishPhase.Take && rod.Reading.PhaseTime >= .15f, 35, "patient take");
                    Check(rod.State == RodState.Bite, "Bite exactly equals model Take");
                    g.StrikeTap(); Check(rod.ReadingResult == StrikeResult.Hooked, "patient hooks");
                    g.Tick(rod.ThrashSeconds + .3f);
                    Check(g.Stats.Landed == landed && g.RodViewActive, "delivery deferred until lift and camera return");
                }
                else if (scenario == 1) { g.StrikeTap(); Check(rod.ReadingResult == StrikeResult.TooEarly, "early strike spooks"); }
                else if (scenario == 3) { g.ReelInRodView(); Check(rod.ReadingResult == StrikeResult.TooEarly, "reel in exits"); }
                else if (scenario == 4)
                {
                    Until(g, () => rod.Reading?.Phase == FishPhase.Take, 35, "take before abandoning");
                    g.ReelInRodView(); Check(rod.ReadingResult == StrikeResult.TooEarly, "reel in during take abandons without hooking");
                }
                Until(g, () => !g.RodViewActive, 45, "result returns to boat");
                Check(g.Cam.orthographic && g.Manning == null, "restores camera and releases captain");
                Check(g.State.Bait == bait, "does not spend second bait or automatically recast");
                if (scenario == 0)
                {
                    Check(g.Stats.Landed == landed + 1 && rod.HookedSpecies == species && rod.HookedKg == kg, "lands exact pre-rolled fish once");
                    g.Tick(.5f); Check(g.Stats.Landed == landed + 1, "no duplicate delivery");
                }
                else Check(g.Stats.Landed == landed && (scenario == 2 ? g.Stats.Missed == missed + 1 : g.Stats.Spooked == spooked + 1), "failed strike loses bait without fish");
                Debug.Log("[Catchline] FISH VIEW scenario " + scenario + " PASS");
            }
            // A rod cast without captain Manning follows the unchanged automatic crew path.
            var crewGame = Fixture(); var crewRod = crewGame.Rods[1];
            crewRod.SetUnlocked(true); crewRod.State = RodState.Ready; crewRod.Cast(crewGame, .5f);
            Check(crewRod.Reading == null, "crew/unmanned cast does not create captain model");
            Until(crewGame, () => crewRod.State == RodState.Bite, 90, "crew waiting clock still reaches Bite");
            Check(crewRod.Strike(crewGame) != null && crewRod.State == RodState.Reeling, "crew strike/reel path unchanged");
            Debug.Log("[Catchline] FISH VIEW CHECKS PASSED: patient/early/ignored/reel-in/reel-in-during-take, once-only deferred landing, bait, camera, crew path");
        }
        public static void VerifyAndBuild() { Run(); GameBuild.BuildBoth(); }
        public static void InspectCaughtModel()
        {
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name == "Catchline-lead-sim", "assigned scratch only");
            ArtImport.BuildLibrary();
            var model = DeckFish.BuildModel(Species.Cod, 5.7484f, null);
            ArtLibrary.AimAlong(model.gameObject, Vector3.forward, FishShadow.LengthFor(Species.Cod, 5.7484f));
            foreach (var t in model.GetComponentsInChildren<Transform>(true))
                Debug.Log($"[Catchline] caught model node {t.name} local={model.InverseTransformPoint(t.position):F4}");
            foreach (var r in model.GetComponentsInChildren<Renderer>(true))
                Debug.Log($"[Catchline] caught mesh {r.name} center={model.InverseTransformPoint(r.bounds.center):F4} size={r.bounds.size:F4}");
            UnityEngine.Object.DestroyImmediate(model.gameObject);
        }
        static void CheckCaughtMouth()
        {
            // The production Cod has no Nose and its tail points +Z after DeckFish fitting.
            // This fixture caught a visually plausible line that was attached to the tail.
            var fish = DeckFish.BuildModel(Species.Cod, 5.7484f, null);
            float length = FishShadow.LengthFor(Species.Cod, 5.7484f);
            ArtLibrary.AimAlong(fish.gameObject, Vector3.forward, length);
            var mouth = (Vector3)typeof(VoyageGame).GetMethod("FishViewMouth", BindingFlags.Static | BindingFlags.NonPublic)
                .Invoke(null, new object[] { fish, length });
            var tail = ArtLibrary.Find(fish.gameObject, "Tail");
            Check(tail != null && mouth.z < -.3f * length && fish.InverseTransformPoint(tail.position).z > 0,
                "real Cod mouth is at the head, opposite its tail pivot");
            Debug.Log($"[Catchline] caught Cod hook local={mouth:F4}, tail={fish.InverseTransformPoint(tail.position):F4}");
            UnityEngine.Object.DestroyImmediate(fish.gameObject);
        }
        static void CheckImportedRod()
        {
            var art = Resources.Load<RodViewArt>("RodViewArt");
            Check(art != null && art.Model != null && art.Atlas != null && art.Clips.Length == 7, "authored FP model/atlas/seven clips referenced");
            var model = UnityEngine.Object.Instantiate(art.Model);
            foreach (var animator in model.GetComponentsInChildren<Animator>()) animator.enabled = false;
            var renderer = model.GetComponentInChildren<SkinnedMeshRenderer>();
            Check(renderer != null && renderer.sharedMesh.triangles.Length / 3 < 6000, "authored skinned mesh budget");
            var tip = ArtLibrary.Find(model, "LineTip"); var mesh = new Mesh();
            foreach (var name in new[] { "Idle", "Cast", "Hold", "Twitch", "Strike", "Reel", "Lift" })
            {
                var clip = art.Clip(name); Check(clip != null, "imported clip " + name);
                clip.SampleAnimation(model, clip.length * .5f); renderer.BakeMesh(mesh);
                float nearest = mesh.vertices.Min(v => Vector3.Distance(renderer.transform.TransformPoint(v), tip.position));
                Debug.Log($"[Catchline] FP baked tip clearance {name}={nearest:F6}m");
                Check(nearest < .02f, "LineTip attaches to actual skinned blank in " + name);
            }
            UnityEngine.Object.DestroyImmediate(mesh); UnityEngine.Object.DestroyImmediate(model);
        }
    }
}

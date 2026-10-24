using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.EditorTools
{
    // Rendering foundation only. Runs in Catchline-lead-sim; never loads a player save.
    public static class FishShadowChecks
    {
        static readonly Species[] SpeciesRow = { Species.Herring, Species.Mackerel, Species.Cod, Species.ApexReefShark };
        static readonly float[] Masses = { .2f, .6f, 6, 14 };
        static readonly float[] Offsets = { -1.6f, -.85f, .05f, 1.25f };
        static void Check(bool condition, string why)
        { if (!condition) throw new Exception("[Catchline] FISH SHADOW failed: " + why); }
        static void ScratchOnly()
        {
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name == "Catchline-lead-sim", "use assigned scratch Catchline-lead-sim only");
        }

        public static void Run()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            var shader = Resources.Load<Shader>("FishShadow");
            Check(shader != null && !ShaderUtil.ShaderHasError(shader), "URP shader imports without errors");
            var parent = new GameObject("FishShadow isolated checks");
            try
            {
                float previous = 0;
                for (int i = 0; i < SpeciesRow.Length; i++)
                {
                    var fish = new GameObject("Test fish").AddComponent<FishShadow>();
                    fish.transform.SetParent(parent.transform, false);
                    fish.Initialize(SpeciesRow[i], Masses[i]);
                    var prefab = ArtLibrary.Get().FishFor(SpeciesRow[i]) ?? ArtLibrary.Get().M(SpeciesRow[i].ToString());
                    Check(fish.Model.GetComponentsInChildren<MeshFilter>().Select(m => m.sharedMesh)
                        .SequenceEqual(prefab.GetComponentsInChildren<MeshFilter>().Select(m => m.sharedMesh)), "same authored meshes: " + SpeciesRow[i]);
                    Check(fish.Length > previous, "clear specimen size order"); previous = fish.Length;
                    var b = LocalBounds(fish);
                    Check(Mathf.Abs(b.size.z - fish.Length) < .001f, "metre length fitted: " + SpeciesRow[i]);
                    Check(b.size.y < b.size.z && b.size.x < b.size.z, "upright long axis +Z: " + SpeciesRow[i]);
                    var nose = ArtLibrary.Find(fish.Model, "Nose"); var tail = ArtLibrary.Find(fish.Model, "TailEnd");
                    if (nose != null && tail != null)
                        Check(Vector3.Dot((nose.position - tail.position).normalized, Vector3.forward) > .99f, "nose +Z");
                    var d = GameData.Get(SpeciesRow[i]);
                    Check(FishShadow.LengthFor(SpeciesRow[i], d.MinKg) < FishShadow.LengthFor(SpeciesRow[i], d.MaxKg), "mass increases length");
                    Check(Mathf.Approximately(FishShadow.LengthFor(SpeciesRow[i], d.MaxKg * 5), FishShadow.LengthFor(SpeciesRow[i], d.MaxKg)), "outlier clamps to species size range");
                    fish.Depth = 0; float surface = fish.Model.transform.parent.position.y;
                    fish.Depth = 1; Check(fish.Model.transform.parent.position.y < surface - 1.2f, "depth submerges visual");
                    fish.Visibility = 0; Check(fish.GetComponentsInChildren<Renderer>().All(r => !r.enabled), "hidden renderers");
                    fish.Visibility = 1; Check(fish.GetComponentsInChildren<Renderer>().All(r => r.enabled), "show renderers");
                    fish.enabled = false; Check(fish.GetComponentsInChildren<Renderer>().All(r => !r.enabled), "disable hides");
                    fish.enabled = true;
                    fish.SwimTo(Vector3.forward, 1); fish.Advance(.25f);
                    Check(Vector3.Distance(fish.transform.position, Vector3.forward * .25f) < .0001f, "swim metres per second");
                    fish.Advance(10); Check(fish.transform.position == Vector3.forward && !fish.IsSwimming, "arrives without overshoot");
                    fish.Dart(Vector3.right); fish.Advance(.16f);
                    Check(fish.transform.position.x > .15f && fish.IsSwimming, "dart bursts");
                    fish.Advance(.5f); Check(!fish.IsSwimming, "dart ends");
                    fish.SwimTo(Vector3.zero, 2); fish.Advance(20);
                    Check(fish.transform.position == Vector3.zero, "swim after dart");
                    fish.Dart(Vector3.zero); Check(!fish.IsSwimming, "zero dart safe");
                    int count = fish.transform.childCount;
                    fish.Initialize(SpeciesRow[i], Masses[i]);
                    Check(fish.transform.childCount == count, "reinitialize disposes old visual");
                    Debug.Log($"[Catchline] FishShadow {SpeciesRow[i]} {Masses[i]}kg length={fish.Length:F4}m bounds={LocalBounds(fish).size:F4} model={prefab.name}");
                }
                bool rejected = false;
                try { FishShadow.LengthFor(Species.Herring, float.NaN); } catch (ArgumentOutOfRangeException) { rejected = true; }
                Check(rejected, "invalid mass rejected");
            }
            finally { UnityEngine.Object.DestroyImmediate(parent); }
            Debug.Log("[Catchline] FISH SHADOW API CHECKS PASSED");
        }

        static Bounds LocalBounds(FishShadow fish)
        {
            Bounds b = default; bool any = false;
            foreach (var mf in fish.Model.GetComponentsInChildren<MeshFilter>())
            {
                var m = fish.transform.worldToLocalMatrix * mf.transform.localToWorldMatrix;
                var mesh = mf.sharedMesh.bounds;
                for (int i = 0; i < 8; i++)
                {
                    var p = m.MultiplyPoint3x4(mesh.center + Vector3.Scale(mesh.extents,
                        new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                    if (!any) { b = new Bounds(p, Vector3.zero); any = true; } else b.Encapsulate(p);
                }
            }
            return b;
        }

        static VoyageGame PreviewGame()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("FISH-SILHOUETTE-1 save-isolated render preview");
            root.SetActive(false);
            var game = root.AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build(); root.SetActive(true);
            typeof(VoyageGame).GetMethod("StartTestTier", BindingFlags.NonPublic | BindingFlags.Instance).Invoke(game, new object[] { 0 });
            game.SetSail();
            for (int i = 0; i < 5000 && game.CurrentMode != VoyageGame.Mode.Fishing; i++) game.Tick(.05f);
            Check(game.CurrentMode == VoyageGame.Mode.Fishing && game.State.HullDef.Model == "Rowboat", "rowboat at sea");
            // Arrival switches mode before the sailing camera has finished easing.
            // Let the existing anchored camera settle; do not substitute a preview zoom.
            game.Tick(3f);
            Debug.Log($"[Catchline] FishShadow normal boat camera ortho={game.Cam.orthographicSize:F4}");
            return game;
        }

        [MenuItem("Catchline/Fish Shadow/Preview (scratch only)")]
        public static void Preview()
        {
            var game = PreviewGame(); Arrange(game);
            Selection.activeGameObject = game.gameObject;
            SceneView.lastActiveSceneView?.AlignViewToObject(game.Cam.transform);
        }

        static FishShadow[] Arrange(VoyageGame game)
        {
            Vector3 right = game.Cam.transform.right;
            Vector3 near = -Vector3.ProjectOnPlane(game.Cam.transform.forward, Vector3.up).normalized;
            Vector3 center = game.Boat.TransformPoint(game.State.HullDef.Center) + near * 2.5f;
            center.y = -.32f;
            var row = new FishShadow[SpeciesRow.Length];
            for (int i = 0; i < row.Length; i++)
            {
                var fish = new GameObject("Shadow " + SpeciesRow[i]).AddComponent<FishShadow>();
                fish.transform.SetParent(game.transform, false);
                fish.transform.position = center + right * Offsets[i];
                fish.transform.rotation = Quaternion.LookRotation(right * .85f - near * .5f, Vector3.up);
                fish.Initialize(SpeciesRow[i], Masses[i]);
                fish.Advance(.35f + i * .17f); row[i] = fish;
            }
            return row;
        }

        public static void Capture()
        {
            Run();
            var game = PreviewGame(); var row = Arrange(game);
            string folder = Path.GetFullPath("../Catchline/docs/screens/fish-silhouette-1");
            Directory.CreateDirectory(folder);
            var position = game.Cam.transform.position; var rotation = game.Cam.transform.rotation;
            float ortho = game.Cam.orthographicSize;
            for (int view = 0; view < 2; view++)
            {
                game.Cam.transform.SetPositionAndRotation(position, rotation);
                game.Cam.orthographic = true; game.Cam.orthographicSize = ortho;
                if (view == 1)
                {
                    var center = (row[0].transform.position + row[3].transform.position) * .5f;
                    Vector3 near = -Vector3.ProjectOnPlane(rotation * Vector3.forward, Vector3.up).normalized;
                    game.Cam.orthographicSize = 1.65f;
                    game.Cam.transform.position = center + near * 6 + Vector3.up * 3;
                    game.Cam.transform.LookAt(center + Vector3.down * .5f);
                }
                foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
                {
                    game.Cam.aspect = (float)size.x / size.y;
                    foreach (var f in row) f.Visibility = 0;
                    var baseline = Render(game.Cam, size.x, size.y);
                    float shallowDifference = 0;
                    foreach (float depth in new[] { .2f, .7f })
                    {
                        foreach (var f in row) { f.Depth = depth; f.Visibility = 1; }
                        var texture = Render(game.Cam, size.x, size.y);
                        float difference = Difference(baseline, texture);
                        Check(difference > .002f, "fish visible over real PTS water " + view + "/" + size + "/" + depth);
                        if (depth < .5f) shallowDifference = difference;
                        else Check(difference < shallowDifference, "deep silhouettes fainter");
                        string name = $"{(view == 0 ? "boat" : "close")}-depth-{depth:F1}-{size.x}.png";
                        File.WriteAllBytes(Path.Combine(folder, name), texture.EncodeToPNG());
                        Debug.Log($"[Catchline] FishShadow rendered {name}, mean pixel difference={difference:F5}");
                        UnityEngine.Object.DestroyImmediate(texture);
                    }
                    UnityEngine.Object.DestroyImmediate(baseline);
                }
            }
            Wave(game.Cam, row);
            Occlusion(game, row);
            Check(!ShaderUtil.ShaderHasError(Resources.Load<Shader>("FishShadow")), "rendered shader has no errors");
            Debug.Log("[Catchline] FISH SHADOW RENDER CHECKS PASSED; Snapshot written to " + folder);
        }

        static void Wave(Camera camera, FishShadow[] row)
        {
            foreach (var f in row) { f.Visibility = 1; f.Depth = .2f; }
            var before = Render(camera, 1440, 900);
            var positions = row.Select(f => f.transform.position).ToArray();
            foreach (var f in row) f.Advance(.6f);
            var after = Render(camera, 1440, 900);
            Check(row.Select((f, i) => f.transform.position == positions[i]).All(v => v), "idle wave does not translate roots");
            float difference = Difference(before, after);
            Check(difference > .005f, "GPU body/tail wave changes rendered fish, difference=" + difference);
            UnityEngine.Object.DestroyImmediate(before); UnityEngine.Object.DestroyImmediate(after);
            Debug.Log("[Catchline] FishShadow GPU body/tail wave PASS, difference=" + difference);
        }

        static void Occlusion(VoyageGame game, FishShadow[] row)
        {
            foreach (var f in row) f.Visibility = 0;
            var fish = row[3]; fish.Depth = .2f;
            var blocker = GameObject.CreatePrimitive(PrimitiveType.Cube);
            blocker.name = "Opaque occlusion fixture";
            blocker.transform.position = fish.transform.position;
            blocker.transform.localScale = new Vector3(3, .2f, 3);
            game.Cam.transform.position = fish.transform.position + Vector3.up * 10;
            game.Cam.transform.rotation = Quaternion.Euler(90, 0, 0);
            game.Cam.orthographicSize = 2; game.Cam.aspect = 1;
            var before = Render(game.Cam, 512, 512);
            fish.Visibility = 1;
            var after = Render(game.Cam, 512, 512);
            float diff = Difference(before, after);
            Check(diff < .00001f, "opaque geometry occludes late silhouette, difference=" + diff);
            UnityEngine.Object.DestroyImmediate(before); UnityEngine.Object.DestroyImmediate(after);
            UnityEngine.Object.DestroyImmediate(blocker);
            Debug.Log("[Catchline] FishShadow opaque depth occlusion PASS");
        }

        static float Difference(Texture2D a, Texture2D b)
        {
            var x = a.GetPixels32(); var y = b.GetPixels32(); double sum = 0;
            for (int i = 0; i < x.Length; i++) sum += Math.Abs(x[i].r - y[i].r) + Math.Abs(x[i].g - y[i].g) + Math.Abs(x[i].b - y[i].b);
            return (float)(sum / (x.Length * 3.0));
        }

        static Texture2D Render(Camera cam, int width, int height)
        {
            var rt = RenderTexture.GetTemporary(width, height, 24, RenderTextureFormat.ARGB32);
            var target = cam.targetTexture; var active = RenderTexture.active;
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
            try
            {
                cam.targetTexture = rt;
                RenderPipeline.SubmitRenderRequest(cam, new RenderPipeline.StandardRequest { destination = rt });
                RenderTexture.active = rt; texture.ReadPixels(new Rect(0, 0, width, height), 0, 0); texture.Apply();
                return texture;
            }
            finally { cam.targetTexture = target; RenderTexture.active = active; RenderTexture.ReleaseTemporary(rt); }
        }
    }
}

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
    // Lighthouse rock's life anchors get their pieces: puffin groups with one animated puffin per ledge, tide-race
    // standing waves on the water, the sweeping lamp beam in the additive glow material. Renders the dressed map.
    // Batch: -executeMethod Catchline.EditorTools.LighthouseLifeChecks.Run
    public static class LighthouseLifeChecks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("LIGHTHOUSELIFE: " + what); }

        public static void Run()
        {
            try
            {
                ArtImport.BuildLibrary();
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var lib = ArtLibrary.Get();
                foreach (var name in new[] { "Puffin", "PuffinGroup", "TideRace", "LighthouseGlow", "GullLighthouseRockSeaV2" }) Check(lib.M(name) != null, "model " + name);
                var clips = lib.M("Puffin").GetComponentInChildren<Animation>();
                Check(clips != null, "puffin Animation");
                var names = clips.Cast<AnimationState>().Select(s => s.name).ToArray();
                Check(names.Any(n => n.EndsWith("Idle")) && names.Any(n => n.EndsWith("Flap")), "Idle and Flap clips: " + string.Join(",", names));

                var g = new GameObject("Lighthouse life check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
                var env = ArtLibrary.Spawn(lib.M("GullLighthouseRockSeaV2"), null, new Vector3(600, -.12f, 0), Quaternion.identity); // clear of the harbour the game builds
                typeof(VoyageGame).GetMethod("DressSkerries", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { env, lib });

                Check(env.GetComponentsInChildren<PuffinLife>().Length == 3, "an animated puffin on each of the three ledges");
                var races = env.GetComponentsInChildren<TideRaceDrift>();
                Check(races.Length == 2 && races.All(r => Mathf.Abs(r.transform.position.y + .10f) < .001f), "two tide races on the water");
                var beam = env.GetComponentInChildren<BeamSweep>();
                Check(beam != null && beam.GetComponentsInChildren<Renderer>().All(r => r.sharedMaterial.shader.name == "Catchline/GlowAdditive"), "lamp beam in the glow material");
                Check(env.GetComponentInChildren<BuoyBob>() != null, "cardinal buoy");

                // The Whale shelf's anchors (MAP9) on a fixture until the map lands.
                var shelf = new GameObject("Shelf fixture"); shelf.transform.position = new Vector3(-600, -.12f, 0);
                var spoutAnchor = new GameObject("WhaleSpout_1").transform; spoutAnchor.SetParent(shelf.transform, false); spoutAnchor.localPosition = new Vector3(0, .3f, 0);
                typeof(VoyageGame).GetMethod("DressSkerries", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { shelf, lib });
                Check(shelf.GetComponentInChildren<WhaleSpout>() != null && shelf.GetComponentInChildren<WhaleTail>() != null, "whale spout and tail on the whale road");
                Check(Mathf.Abs(shelf.GetComponentInChildren<WhaleTail>().transform.position.y + .12f) < .001f, "whale tail at the water line");

                // A deck-angle view of the dressed map, and close views of each piece.
                var sun = new GameObject("Sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.intensity = 1.3f;
                sun.color = new Color(1, .96f, .88f); sun.transform.rotation = Quaternion.Euler(55, 195, 0);
                RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat; RenderSettings.ambientLight = new Color(.58f, .64f, .7f);
                var water = GameObject.CreatePrimitive(PrimitiveType.Plane); water.transform.position = new Vector3(600, -.12f, 0); water.transform.localScale = Vector3.one * 40;
                water.GetComponent<Renderer>().sharedMaterial = Prototype.Visuals.Mat(new Color(.18f, .5f, .6f));
                var cam = new GameObject("Cam").AddComponent<Camera>(); cam.orthographic = true; cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = new Color(.18f, .5f, .6f);
                var dir = new Vector3(.574f, -.819f, 1).normalized;
                void Shot(Vector3 at, float size, string file, Vector3? from = null)
                {
                    var d = (from ?? dir).normalized; cam.orthographicSize = size; cam.transform.position = at - d * 80; cam.transform.rotation = Quaternion.LookRotation(d);
                    cam.farClipPlane = 300;
                    var rt = new RenderTexture(1440, 900, 24); cam.targetTexture = rt; cam.Render();
                    RenderTexture.active = rt; var tex = new Texture2D(1440, 900, TextureFormat.RGB24, false);
                    tex.ReadPixels(new Rect(0, 0, 1440, 900), 0, 0); tex.Apply(); RenderTexture.active = null; cam.targetTexture = null;
                    Directory.CreateDirectory("C:/Users/momoy/Projects/Catchline/docs/screens/overnight"); File.WriteAllBytes("C:/Users/momoy/Projects/Catchline/docs/screens/overnight/" + file + ".png", tex.EncodeToPNG());
                }
                foreach (var t in env.GetComponentsInChildren<Transform>().Where(t => t.name.Contains("_") && char.IsDigit(t.name[^1]) && (t.name.StartsWith("Puffin") || t.name.StartsWith("Tide") || t.name.StartsWith("Light") || t.name.StartsWith("Cardinal"))))
                    {
                        // Is the anchor under the rock? Count rock triangles straight above it.
                        var top = env.GetComponentsInChildren<MeshFilter>().Where(m => m.sharedMesh != null && !m.transform.IsChildOf(t)).Select(m => m.GetComponent<Renderer>().bounds).Where(b => b.min.x < t.position.x && b.max.x > t.position.x && b.min.z < t.position.z && b.max.z > t.position.z && b.max.y > t.position.y + .3f).Count();
                        Debug.Log("LIGHTHOUSELIFE anchor " + t.name + " " + (t.position - env.transform.position).ToString("F2") + " meshes reaching above: " + top);
                    }
                Shot(env.transform.position + new Vector3(10, 0, 20), 60, "lighthouse-life-map");
                foreach (var t in env.GetComponentsInChildren<Transform>().Where(t => t.name is "PuffinLedge_2" or "TideRace_1" or "LighthouseLamp_1"))
                    Shot(t.position, t.name.StartsWith("Puffin") ? 8f : 7f, "lighthouse-life-" + t.name, t.name.StartsWith("Puffin") ? new Vector3(.574f, -.819f, 1) : null);
                UnityEngine.Object.DestroyImmediate(g.gameObject);
                Debug.Log("LIGHTHOUSELIFE PASS · puffin " + string.Join("/", names.Select(n => n.Split('|').Last())) + ", three ledges, two races, beam, buoy");
                EditorApplication.Exit(0);
            }
            catch (Exception e) { Debug.LogError(e); EditorApplication.Exit(1); }
        }
    }
}

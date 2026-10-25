using System;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The Wreck bank's life anchors get their pieces: a gannet over a herring boil with its splash, gulls on the wreck,
    // a bobbing cardinal buoy. The Gannet imports with legacy Glide and Dive clips.
    // Batch: -executeMethod Catchline.EditorTools.WreckLifeChecks.Run
    public static class WreckLifeChecks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("WRECKLIFE: " + what); }

        public static void Run()
        {
            try
            {
                ArtImport.BuildLibrary();
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var lib = ArtLibrary.Get();
                foreach (var name in new[] { "Gannet", "DiveSplash", "CardinalBuoy", "HerringBoil", "Seagull" }) Check(lib.M(name) != null, "model " + name);
                var clips = lib.M("Gannet").GetComponentInChildren<Animation>();
                Check(clips != null, "gannet Animation");
                var names = clips.Cast<AnimationState>().Select(s => s.name).ToArray();
                Check(names.Any(n => n.Contains("Glide")) && names.Any(n => n.Contains("Dive")), "Glide and Dive clips: " + string.Join(",", names));

                var g = new GameObject("Wreck life check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
                var env = new GameObject("GullWreckBank fixture"); env.transform.position = new Vector3(0, -.12f, 0);
                foreach (var (n, p) in new[] { ("GannetDive_1", new Vector3(4, .8f, 2)), ("WreckGulls_1", new Vector3(-3, 1.48f, 1)), ("CardinalBuoy_1", new Vector3(-6, -.32f, -2)) })
                { var a = new GameObject(n).transform; a.SetParent(env.transform, false); a.localPosition = p; }
                typeof(VoyageGame).GetMethod("DressSkerries", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { env, lib });

                var gannet = env.GetComponentInChildren<GannetDive>(true);
                Check(gannet != null && gannet.Splash != null, "gannet with its splash");
                Check(Mathf.Abs(gannet.Water.y + .12f) < .001f, "gannet dives to the water line");
                Check(env.transform.Find("GannetDive_1/HerringBoil")?.GetComponent<SurfPulse>() != null, "herring boil pulsing");
                Check(env.transform.Find("WreckGulls_1").GetComponentsInChildren<Gull>().Length == 3, "three gulls on the wreck");
                var buoy = env.GetComponentInChildren<BuoyBob>();
                Check(buoy != null && Mathf.Abs(buoy.transform.position.y + .12f) < .001f, "cardinal buoy at the water line");
                UnityEngine.Object.DestroyImmediate(g.gameObject);
                Debug.Log("WRECKLIFE PASS · gannet " + string.Join("/", names.Select(n => n.Split('|').Last())) + ", boil, splash, three gulls, buoy");
                EditorApplication.Exit(0);
            }
            catch (Exception e) { Debug.LogError(e); EditorApplication.Exit(1); }
        }
    }
}

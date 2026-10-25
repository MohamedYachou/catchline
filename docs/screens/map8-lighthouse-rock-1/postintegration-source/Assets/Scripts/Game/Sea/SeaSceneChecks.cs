#if UNITY_EDITOR
using System;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Sea;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class SeaSceneChecks
    {
        static void Check(bool value, string label)
        { if (!value) throw new Exception("Sea scene: " + label); }

        public static void Assets()
        {
            Check(Resources.Load<Shader>("SeaOverlay") != null, "overlay included in player resources");
            foreach (string map in SeaNav.Maps)
            {
                var nav = SeaNav.Load(map, GameData.Hulls[0]);
                Check(nav != null && !nav.Interim, map + " real navigation");
                var model = ArtLibrary.Get().M(nav.ModelId);
                Check(model != null, map + " authored model");
                Check(model.GetComponentsInChildren<Transform>(true).Any(t => t.name.StartsWith("Horizon")), map + " horizon silhouettes");
                var root = new GameObject("Sea environment check");
                var water = new Material(ArtLibrary.Get().WaterShader);
                try
                {
                    var surface = CoastalWater.Build(root.transform, water);
                    var env = root.AddComponent<SeaEnvironment>(); env.Build(nav, surface.transform, water);
                    var ocean = surface.transform.Find("Water to horizon").GetComponent<MeshFilter>().sharedMesh;
                    Check(ocean.bounds.size.x >= 4096 && ocean.vertexCount < 25000, map + " bounded-cost horizon water");
                    env.Follow(nav.Harbour); float harbourFog = RenderSettings.fogDensity;
                    env.Follow(nav.Snap(nav.Border[0]));
                    Check(RenderSettings.fogDensity > harbourFog, map + " fog increases near border");
                }
                finally { UnityEngine.Object.DestroyImmediate(root); UnityEngine.Object.DestroyImmediate(water); }
            }
            Debug.Log("[Catchline] SEA SCENE ASSET CHECKS PASSED: five real maps, horizon models, ocean extension, border fog; native visuals pending");
        }
    }
}
#endif

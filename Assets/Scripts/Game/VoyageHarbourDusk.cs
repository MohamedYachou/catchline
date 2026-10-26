using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // Day and night in the harbour (harbour plan to-do): a boat that comes home finds the harbour at dusk, with a low
    // warm sun, long shadows and the quay lamps lit; the next departure is morning again. Light only: play is unchanged.
    public partial class VoyageGame
    {
        static readonly Color DaySun = new(1f, .96f, .88f), DuskSun = new(1f, .66f, .42f);
        static readonly Color DayAmbient = new(.58f, .64f, .7f), DuskAmbient = new(.47f, .45f, .56f);
        static readonly Quaternion DaySunAngle = Quaternion.Euler(55f, 195f, 0f), DuskSunAngle = Quaternion.Euler(24f, 235f, 0f);
        bool harbourEvening;
        float duskBlend;
        Light sunLight;
        readonly List<Light> lampLights = new();
        Transform lampScenery;

        public bool HarbourEvening => harbourEvening;
        public void SetHarbourEvening(bool evening, bool instant = false) { harbourEvening = evening; if (instant) duskBlend = evening ? 1 : 0; }

        void UpdateHarbourDusk(float dt)
        {
            bool dusk = harbourEvening && CurrentMode == Mode.Harbour || State != null && State.NightVoyage && CurrentMode != Mode.Harbour;
            duskBlend = Mathf.MoveTowards(duskBlend, dusk ? 1 : 0, dt / (dusk ? 3f : 1.5f));
            if (sunLight == null) sunLight = transform.Find("Sun")?.GetComponent<Light>();
            float k = duskBlend * duskBlend * (3 - 2 * duskBlend);
            if (sunLight != null)
            {
                sunLight.color = Color.Lerp(DaySun, DuskSun, k);
                sunLight.intensity = Mathf.Lerp(1.3f, 1.05f, k);
                sunLight.transform.rotation = Quaternion.Slerp(DaySunAngle, DuskSunAngle, k);
            }
            RenderSettings.ambientLight = Color.Lerp(DayAmbient, DuskAmbient, k);
            if (scenery != lampScenery) LightLamps();
            foreach (var lamp in lampLights)
                if (lamp != null)
                {
                    lamp.intensity = 5f * k; lamp.enabled = k > .01f;
                    var bulb = lamp.transform.GetChild(0).gameObject;
                    bulb.SetActive(k > .3f);
                }
        }

        // A warm point light under the head of every quay lamp in the harbour scenery.
        void LightLamps()
        {
            foreach (var lamp in lampLights) if (lamp != null) Destroy(lamp.gameObject);
            lampLights.Clear(); lampScenery = scenery;
            var prefab = ArtLibrary.Get()?.LampPost;
            if (scenery == null || prefab == null) return;
            foreach (Transform child in scenery.GetComponentsInChildren<Transform>())
            {
                if (!child.name.StartsWith(prefab.name)) continue;
                var bounds = new Bounds(child.position, Vector3.zero);
                foreach (var part in child.GetComponentsInChildren<Renderer>()) bounds.Encapsulate(part.bounds);
                var light = new GameObject("Lamp light").AddComponent<Light>();
                light.transform.SetParent(child, false);
                light.transform.position = new Vector3(child.position.x, bounds.max.y - .25f, child.position.z);
                light.type = LightType.Point; light.range = 6f; light.color = new Color(1f, .78f, .45f);
                light.shadows = LightShadows.None; light.intensity = 0; light.enabled = false;
                // The lit lamp itself: a small unlit warm globe in the lantern head.
                var bulb = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                Prototype.Visuals.Kill(bulb.GetComponent<Collider>());
                bulb.name = "Lamp glow"; bulb.transform.SetParent(light.transform, false);
                bulb.transform.localScale = Vector3.one * .22f / Mathf.Max(.01f, child.lossyScale.x);
                var shader = Shader.Find("Universal Render Pipeline/Unlit");
                var r = bulb.GetComponent<Renderer>(); r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                if (shader != null) { r.sharedMaterial = new Material(shader); r.sharedMaterial.SetColor("_BaseColor", new Color(1f, .86f, .55f)); }
                bulb.SetActive(false);
                lampLights.Add(light);
            }
            if (Application.isBatchMode) Debug.Log("DUSK lamps " + lampLights.Count);
        }
    }
}

using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Visuals = Catchline.Prototype.Visuals;

namespace Catchline.Game
{
    // The captain's net work as a scene (docs/plans/MINIGAMES.md, section 1). The rules stay in VoyageNetGame: setting
    // is three taps while the marker crosses the green, hauling is tapping the roller round while keeping the tension out
    // of the red. This file only shows it: the marker swinging over the water and each panel flying out where it lands,
    // then the boat's own roller bringing the net in, and the bunt full of fish rising in the last third.
    public partial class VoyageGame
    {
        NetView netView;
        public bool NetViewActive => netView != null;
        Rect NetViewLeaveRect => new Rect(iw - Edge - 132, ih - Edge - 54, 132, 54);

        void UpdateNetView(float dt)
        {
            if (netView == null && NetGameActive && netGamePerson == Captain && !RodViewActive && !CageViewActive)
            { netView = new NetView(this, netGameRig, NetGameSetting); toastUntil = catchUntil = 0; }
            if (netView == null) return;
            if (!netView.Update(dt)) { netView.Dispose(); netView = null; Cam.orthographic = true; Cam.ResetProjectionMatrix(); }
        }

        void InterfaceNetView()
        {
            if (!NetGameActive || netView.Opacity < .5f) return;
            bool red = !NetGameSetting && NetGameTension >= NetHaulRedTension;
            string hint = NetGameSetting ? $"Tap as the float crosses the green · {Mathf.RoundToInt(NetGameProgress * 3)}/3 spread"
                : red ? "Too tight! Let it ease" : NetGameProgress > .66f ? "The bunt is up · keep it coming" : "Tap to turn the roller · keep it out of the red";
            var band = new Rect((iw - 560) / 2, Edge, 560, 52);
            coastalUi.Box("netview/hint", band, "chip-dark", new Color(1, 1, 1, .82f));
            coastalUi.Text("netview/hint/text", band, hint, Skin.Type.Body, red ? Skin.Brass : Skin.Cream, TextAnchor.MiddleCenter);

            // One slim gauge at the foot: the swing (setting) or the tension (hauling), with the net's progress under it.
            float w = Mathf.Min(460, iw - 2 * Edge - 300);
            var meter = new Rect((iw - w) / 2, ih - Edge - 44, w, 14);
            coastalUi.Box("netview/meter/back", new Rect(meter.x - 10, meter.y - 12, meter.width + 20, 52), "chip-dark", new Color(1, 1, 1, .7f));
            coastalUi.Bar("netview/meter", meter, NetGameSetting ? NetGamePhase : NetGameTension, red);
            float lo = NetGameSetting ? .35f : .65f, hi = NetGameSetting ? .65f : .84f;
            coastalUi.Box("netview/meter/sweet", new Rect(meter.x + meter.width * lo, meter.y, meter.width * (hi - lo), meter.height), "", new Color(.3f, .75f, .49f, .8f), blocks: false);
            if (!NetGameSetting) coastalUi.Box("netview/meter/red", new Rect(meter.x + meter.width * .85f, meter.y, meter.width * .15f, meter.height), "", new Color(.88f, .28f, .2f, .9f), blocks: false);
            float cursor = NetGameSetting ? NetGamePhase : NetGameTension;
            coastalUi.Box("netview/meter/cursor", new Rect(meter.x + meter.width * cursor - 2, meter.y - 3, 4, meter.height + 6), "", Skin.Cream, blocks: false);
            coastalUi.Bar("netview/progress", new Rect(meter.x, meter.yMax + 10, meter.width, 6), NetGameProgress);
            if (NetGameDamage > 0)
                coastalUi.Text("netview/risk", new Rect(meter.x, meter.y - 46, meter.width, 28), "Fraying · one more mistake loses this haul", Skin.Type.Small, Skin.Brass, TextAnchor.MiddleCenter);
            IButton("netview/leave", NetViewLeaveRect, "Leave net", CancelNetHaulGame, false); Block(NetViewLeaveRect);
        }

        sealed class NetView
        {
            const float SweepSeconds = .45f, ArcRadius = 6.5f, ArcSpread = 52f;
            public float Opacity => Ease(age / SweepSeconds) * (1 - Ease(returnAge / SweepSeconds));

            readonly VoyageGame g;
            readonly Transform root, marker, bunt, bundle;
            readonly LineRenderer arc, green;
            readonly RodViewAtmosphere sky;
            readonly List<(Transform t, Vector3 from, Vector3 to, float born)> flying = new();
            readonly List<(Transform t, float born)> heaps = new();
            readonly List<Transform> fish = new();
            readonly List<Renderer> hidden = new();
            readonly Vector3 access, outward, right, deckPosition, eye, centre;
            readonly Quaternion deckRotation, setRotation, haulRotation;
            readonly float deckFov;
            float age, returnAge = -1, lastProgress, haulBlend;
            int lastDamage;
            bool setting;

            public NetView(VoyageGame game, int rig, bool setting)
            {
                g = game; this.setting = setting; haulBlend = setting ? 0 : 1;
                deckPosition = g.Cam.transform.position; deckRotation = g.Cam.transform.rotation;
                deckFov = 2 * Mathf.Atan(g.Cam.orthographicSize / Mathf.Max(1, Vector3.Distance(deckPosition, g.Captain.Root.position))) * Mathf.Rad2Deg;
                access = g.Boat.TransformPoint(g.Grid.GetLocal(rig == 1 ? g.SecondNetAccess : g.NetAccess));
                var middle = g.Boat.TransformPoint(g.State.HullDef.Center);
                outward = access - middle; outward.y = 0;
                if (outward.sqrMagnitude < .01f) outward = -g.Boat.right;
                outward.Normalize();
                right = Vector3.Cross(Vector3.up, outward);
                eye = new Vector3(access.x, Rod.WaterY + 2f, access.z) - outward * .45f;
                // Setting looks out over the water to the marker's arc; hauling looks down at the roller and the rising net.
                setRotation = Quaternion.LookRotation(outward * Mathf.Cos(20 * Mathf.Deg2Rad) - Vector3.up * Mathf.Sin(20 * Mathf.Deg2Rad), Vector3.up);
                haulRotation = Quaternion.LookRotation(outward * Mathf.Cos(34 * Mathf.Deg2Rad) - Vector3.up * Mathf.Sin(34 * Mathf.Deg2Rad), Vector3.up);
                centre = new Vector3(access.x, Rod.WaterY + .02f, access.z) + outward * ArcRadius;
                lastProgress = g.NetGameProgress; lastDamage = g.NetGameDamage;

                root = new GameObject("Captain net view").transform; root.SetParent(g.transform, false);
                foreach (var r in g.Captain.Root.GetComponentsInChildren<Renderer>()) if (r.enabled) { r.enabled = false; hidden.Add(r); }

                // Setting: the swing arc on the water with its green window, and the float that rides it.
                arc = Line("Swing arc", .05f, Palette.Hex("F4EFE3"), 25);
                green = Line("Green window", .16f, Palette.Hex("4FBF7D"), 9);
                for (int i = 0; i < 25; i++) arc.SetPosition(i, ArcPoint(i / 24f));
                for (int i = 0; i < 9; i++) green.SetPosition(i, ArcPoint(Mathf.Lerp(.35f, .65f, i / 8f)) + Vector3.up * .01f);
                marker = new GameObject("Swing float").transform; marker.SetParent(root, false);
                Visuals.Prim(PrimitiveType.Sphere, "Float", marker, Vector3.zero, new Vector3(.32f, .26f, .32f), Palette.Accent);
                Visuals.Prim(PrimitiveType.Cylinder, "Flag pole", marker, new Vector3(0, .35f, 0), new Vector3(.03f, .3f, .03f), Palette.HullNavy);
                Visuals.Box("Flag", marker, new Vector3(.09f, .55f, 0), new Vector3(.18f, .12f, .01f), Palette.Hex("F2C14E"));
                bundle = new GameObject("Net bundle").transform; bundle.SetParent(root, false);
                bundle.position = eye + setRotation * new Vector3(-.38f, -.7f, .9f);
                for (int i = 0; i < 4; i++)
                    Visuals.Prim(PrimitiveType.Sphere, "Folds", bundle, new Vector3((i - 1.5f) * .09f, (i % 2) * .05f, 0), new Vector3(.2f, .12f, .16f), Palette.Hex("5E8C83"));

                // Hauling uses the boat's own roller and net; the view adds the bunt of fish coming up in the last third.
                bunt = new GameObject("Net bunt").transform; bunt.SetParent(root, false);
                for (int ring = 0; ring < 4; ring++)
                {
                    var hoop = new GameObject("Bunt mesh").AddComponent<LineRenderer>(); hoop.transform.SetParent(bunt, false);
                    hoop.useWorldSpace = false; hoop.loop = true; hoop.positionCount = 16; hoop.widthMultiplier = .022f;
                    hoop.sharedMaterial = Visuals.Mat(Palette.Hex("2F5D57")); hoop.shadowCastingMode = ShadowCastingMode.Off;
                    for (int n = 0; n < 16; n++)
                    {
                        float a = n * Mathf.PI * 2 / 16;
                        hoop.SetPosition(n, ring < 2 ? new Vector3(Mathf.Cos(a) * .55f, (ring - .5f) * .3f, Mathf.Sin(a) * .4f) : Quaternion.Euler(0, ring * 45, 0) * new Vector3(Mathf.Cos(a) * .55f, Mathf.Sin(a) * .35f, 0));
                    }
                }
                int count = Mathf.Clamp(Mathf.RoundToInt(g.NetCatchKg / 1.6f), 3, 9);
                var kinds = new[] { Species.Herring, Species.Mackerel, Species.Pollock, Species.Whiting };
                for (int i = 0; i < count; i++)
                {
                    var f = DeckFish.BuildModel(kinds[i % kinds.Length], .6f, bunt);
                    ArtLibrary.AimAlong(f.gameObject, Vector3.right, .32f);
                    f.localPosition = new Vector3((i % 3 - 1) * .26f, (i / 3) * .1f - .1f, ((i * 7) % 3 - 1) * .14f);
                    fish.Add(f);
                }
                sky = new RodViewAtmosphere(root, g.transform, outward);
                Show();
                g.audio?.Play(VoyageAudio.Cue.Moor, .35f);
            }

            LineRenderer Line(string name, float width, Color colour, int points)
            {
                var line = new GameObject(name).AddComponent<LineRenderer>(); line.transform.SetParent(root, false);
                line.useWorldSpace = true; line.positionCount = points; line.widthMultiplier = width;
                line.sharedMaterial = Visuals.Mat(colour); line.shadowCastingMode = ShadowCastingMode.Off;
                return line;
            }

            Vector3 ArcPoint(float t) => new Vector3(access.x, Rod.WaterY + .03f, access.z) + Quaternion.AngleAxis(Mathf.Lerp(-ArcSpread, ArcSpread, t), Vector3.up) * outward * ArcRadius;

            void Show()
            {
                arc.gameObject.SetActive(setting); green.gameObject.SetActive(setting); marker.gameObject.SetActive(setting); bundle.gameObject.SetActive(setting);
                bunt.gameObject.SetActive(!setting);
            }

            static float Ease(float t) { t = Mathf.Clamp01(t); return t * t * (3 - 2 * t); }

            // False once the view has returned to the deck.
            public bool Update(float dt)
            {
                age += dt;
                if (returnAge < 0 && (!g.NetGameActive || g.netGamePerson != g.Captain)) returnAge = 0;
                if (g.NetGameActive && g.NetGameSetting != setting) { setting = g.NetGameSetting; lastProgress = g.NetGameProgress; Show(); }
                haulBlend = Mathf.MoveTowards(haulBlend, setting ? 0 : 1, dt * 2.2f);
                float sweep = Ease(age / SweepSeconds), back = returnAge >= 0 ? Ease((returnAge += dt) / SweepSeconds) : 0;
                float blend = sweep * (1 - back);
                var view = Quaternion.Slerp(setRotation, haulRotation, Ease(haulBlend));
                g.Cam.transform.SetPositionAndRotation(Vector3.Lerp(deckPosition, eye, blend), Quaternion.Slerp(deckRotation, view, blend));
                g.Cam.orthographic = blend < .00001f;
                g.Cam.fieldOfView = Mathf.Lerp(deckFov, 54, blend); g.Cam.ResetProjectionMatrix();
                root.gameObject.SetActive(back < .98f);
                if (returnAge >= SweepSeconds) return false;
                if (blend > .001f) sky.Update(g.Cam, g.Cam.transform.position, Rod.WaterY, false, g.SimTime);
                if (!g.NetGameActive) return true;

                float progress = g.NetGameProgress, tension = g.NetGameTension;
                bool mistake = g.NetGameDamage > lastDamage; lastDamage = g.NetGameDamage;
                if (setting)
                {
                    var at = ArcPoint(g.NetGamePhase);
                    marker.position = at + Vector3.up * (Mathf.Sin(age * 3.1f) * .04f);
                    marker.rotation = Quaternion.LookRotation(outward) * Quaternion.Euler(Mathf.Sin(age * 2.3f) * 6, 0, Mathf.Sin(age * 1.7f) * 8);
                    bool inGreen = g.NetGamePhase >= .35f && g.NetGamePhase <= .65f;
                    green.widthMultiplier = inGreen ? .22f : .16f;
                    // A clean cast throws a panel to where the float is; a bad one lands in a heap.
                    if (progress > lastProgress + .01f) { flying.Add((Panel(), bundle.position, at, age)); g.audio?.Play(VoyageAudio.Cue.Cast, .45f); }
                    else if (mistake) { heaps.Add((Heap(at), age)); g.audio?.Play(VoyageAudio.Cue.Splash, .5f); }
                }
                else
                {
                    bool red = tension >= NetHaulRedTension;
                    if (progress > lastProgress + .005f) g.audio?.Play(VoyageAudio.Cue.Creak, Mathf.Lerp(.25f, .6f, tension));
                    if (mistake) { g.audio?.Play(VoyageAudio.Cue.Reel, .7f); g.audio?.Play(VoyageAudio.Cue.Splash, .4f); }
                    // The bunt rises alongside with the last third, straining when the tension is in the red.
                    float rise = Mathf.InverseLerp(.5f, .85f, progress);
                    var water = new Vector3(access.x, Rod.WaterY, access.z) + outward * Mathf.Lerp(3.6f, 2.3f, progress) - right * 1.1f; // beside the roller, clear of it
                    bunt.gameObject.SetActive(progress > .45f);
                    bunt.position = water + Vector3.down * Mathf.Lerp(.5f, -.35f, rise) + right * Mathf.Sin(age * 1.3f) * .05f;
                    bunt.rotation = Quaternion.LookRotation(outward);
                    bunt.localScale = Vector3.one * Mathf.Lerp(.85f, 1.05f, rise) * (red ? 1 + Mathf.Sin(age * 40) * .03f : 1);
                    for (int i = 0; i < fish.Count; i++)
                        fish[i].localRotation = Quaternion.Euler(0, i * 50 + Mathf.Sin(age * (9 + i) + i) * 30 * (.4f + rise), Mathf.Sin(age * (13 + i)) * 20 * rise);
                }
                lastProgress = progress;

                for (int i = flying.Count - 1; i >= 0; i--)
                {
                    var f = flying[i]; float t = (age - f.born) / .6f;
                    f.t.position = Vector3.Lerp(f.from, f.to, Ease(t)) + Vector3.up * Mathf.Sin(Mathf.Clamp01(t) * Mathf.PI) * 1.4f;
                    f.t.localScale = Vector3.one * Mathf.Lerp(.25f, 1, Ease(t));
                    if (t >= 1) { f.t.position = f.to; flying.RemoveAt(i); g.audio?.Play(VoyageAudio.Cue.Splash, .3f); }
                }
                for (int i = heaps.Count - 1; i >= 0; i--)
                {
                    float t = (age - heaps[i].born) / 2.5f;
                    heaps[i].t.position += Vector3.down * dt * .12f;
                    if (t >= 1) { Visuals.Kill(heaps[i].t.gameObject); heaps.RemoveAt(i); }
                }
                return true;
            }

            // An opened panel: a cork line across the top and the mesh hanging under it, lying on the water.
            Transform Panel()
            {
                var panel = new GameObject("Net panel").transform; panel.SetParent(root, false);
                panel.position = bundle.position; panel.rotation = Quaternion.LookRotation(outward);
                var mesh = panel.gameObject.AddComponent<LineRenderer>(); mesh.useWorldSpace = false;
                mesh.widthMultiplier = .025f; mesh.sharedMaterial = Visuals.Mat(Palette.Hex("7FA89E")); mesh.shadowCastingMode = ShadowCastingMode.Off;
                var points = new List<Vector3>();
                for (int n = 0; n <= 8; n++) { float x = -1.2f + n * .3f; points.Add(new Vector3(x, 0, n % 2 == 0 ? .5f : -.5f)); }
                for (int n = 8; n >= 0; n--) { float x = -1.2f + n * .3f; points.Add(new Vector3(x, 0, n % 2 == 0 ? -.5f : .5f)); }
                mesh.positionCount = points.Count; mesh.SetPositions(points.ToArray());
                var corks = new GameObject("Cork line").transform; corks.SetParent(panel, false);
                for (int n = 0; n < 7; n++)
                    Visuals.Prim(PrimitiveType.Sphere, "Cork", corks, new Vector3(-1.2f + n * .4f, .03f, .5f), new Vector3(.13f, .08f, .13f), Palette.Accent);
                return panel;
            }

            Transform Heap(Vector3 at)
            {
                var heap = new GameObject("Net heap").transform; heap.SetParent(root, false); heap.position = at;
                for (int i = 0; i < 5; i++)
                    Visuals.Prim(PrimitiveType.Sphere, "Tangle", heap, new Vector3((i % 3 - 1) * .18f, .02f + (i / 3) * .08f, ((i * 2) % 3 - 1) * .12f), new Vector3(.3f, .14f, .26f), Palette.Hex("5E8C83"));
                Visuals.Prim(PrimitiveType.Sphere, "Cork", heap, new Vector3(.1f, .14f, 0), new Vector3(.13f, .08f, .13f), Palette.Accent);
                return heap;
            }

            public void Dispose()
            {
                foreach (var r in hidden) if (r != null) r.enabled = true;
                hidden.Clear();
                sky?.Dispose();
                if (root != null) Visuals.Kill(root.gameObject);
            }
        }
    }
}

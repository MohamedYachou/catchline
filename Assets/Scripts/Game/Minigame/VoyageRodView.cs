using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Visuals = Catchline.Prototype.Visuals;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        RodView rodView;
        int rodViewCasts;
        public bool RodViewActive => rodView != null;

        internal static Vector3 FishViewMouth(Transform model, float length)
        {
            var nose = ArtLibrary.Find(model.gameObject, "Nose");
            if (nose != null) return model.InverseTransformPoint(nose.position);
            // Older library fish have no Nose locator and may face -Z after fitting.
            // Use their actual tail pivot to select the head end of the mesh bounds.
            var tail = ArtLibrary.Find(model.gameObject, "Tail");
            Bounds bounds = default; bool any = false;
            foreach (var mesh in model.GetComponentsInChildren<MeshFilter>())
            {
                if (mesh.sharedMesh == null) continue;
                var b = mesh.sharedMesh.bounds;
                var matrix = model.worldToLocalMatrix * mesh.transform.localToWorldMatrix;
                for (int i = 0; i < 8; i++)
                {
                    var p = matrix.MultiplyPoint3x4(b.center + Vector3.Scale(b.extents,
                        new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                    if (!any) { bounds = new Bounds(p, Vector3.zero); any = true; } else bounds.Encapsulate(p);
                }
            }
            if (!any) return Vector3.forward * length * .45f;
            float head = tail != null && model.InverseTransformPoint(tail.position).z > bounds.center.z ? -1 : 1;
            return bounds.center + Vector3.forward * (head * bounds.extents.z * .96f);
        }
        public float RodViewDeckOpacity => rodView?.DeckOpacity ?? 1;
        public void BeginRodView(Rod rod)
        {
            rodView?.Dispose();
            rodView = new RodView(this, rod, ++rodViewCasts <= 2 && ShowTips);
            // Transient deck messages must not become a result banner on the water.
            toastUntil = catchUntil = 0;
        }
        public void EndCaptainFishing(Rod rod)
        {
            if (Manning == rod) { Manning = null; AwaitingCast = false; }
        }
        public void ReelInRodView()
        {
            if (rodView == null || rodView.Rod.ReadingResult.HasValue) return;
            // Reeling in voluntarily still spends the bait already cast.
            rodView.Rod.ReelInView(this);
        }
        void UpdateRodView(float dt)
        {
            if (rodView == null) return;
            if (rodView.Rod.Reading == null || CurrentMode != Mode.Fishing || Manning != rodView.Rod)
            {
                Cam.orthographic = true; Cam.ResetProjectionMatrix();
                rodView.Dispose(); rodView = null; return;
            }
            rodView.Update(dt);
        }
        void OnDestroy() { rodView?.Dispose(); rodView = null; }
        void InterfaceRodView()
        {
            // Normal retained deck elements fade over the first .4 seconds of the cast.
            if (RodViewDeckOpacity > .001f)
            {
                InterfaceFishing();
                foreach (Transform t in coastalUi.Root)
                {
                    if (t.name.StartsWith("rodview/")) continue;
                    var cg = t.GetComponent<CanvasGroup>();
                    if (cg == null) cg = t.gameObject.AddComponent<CanvasGroup>();
                    cg.alpha = RodViewDeckOpacity; cg.interactable = cg.blocksRaycasts = false;
                }
                hudRects.Clear();
            }
            var p = new Rect(iw - Edge - 52, Edge, 52, 52);
            coastalUi.IconButton("rodview/pause", p, "v2-icon-menu", null, () => paused = true, null, "icon-menu"); Block(p);
            IButton("rodview/reel-in", new Rect(iw - Edge - 132, ih - Edge - 54, 132, 54), "Reel in", ReelInRodView, false,
                !rodView.Rod.ReadingResult.HasValue && rodView.Rod.State != RodState.Flying);
            if (rodView.ShowTip && !rodView.Rod.ReadingResult.HasValue && rodView.Rod.State is RodState.Waiting or RodState.Bite)
                coastalUi.Text("rodview/tip", new Rect(Edge + 100, ih - Edge - 48, iw - 2 * Edge - 350, 40),
                    "Wait until the bobber stays under, then strike.", Skin.Type.Small, Skin.Cream, TextAnchor.MiddleCenter);
        }

        // Presentation reads the model; rules and catch ownership remain in Rod/VoyageGame.
        sealed class RodView
        {
            public readonly Rod Rod;
            public readonly bool ShowTip;
            public float DeckOpacity => Mathf.Max(1 - Mathf.SmoothStep(0, 1, Rod.CastAge / .4f),
                Rod.ReadingResult.HasValue ? Ease((Rod.ResultAge - Rod.ReturnAt) / Rod.ReturnSeconds) : 0);
            readonly VoyageGame g;
            readonly Transform root, rig, pole, bobber, landed;
            readonly Vector3 landedMouth;
            readonly FishShadow fish;
            readonly LineRenderer line;
            readonly Vector3 outward, right, castStart, deckPosition;
            readonly Quaternion deckRotation;
            readonly List<Material> ownedMaterials = new();
            readonly List<(Transform t, float born, bool bubble)> effects = new();
            readonly MaterialPropertyBlock bend = new();
            readonly Renderer[] rodRenderers;
            readonly List<(Renderer renderer, bool hidden)> deckRodRenderers = new();
            readonly Transform bendBone, reelBone;
            readonly RodViewAnimation authored;
            readonly float deckFov;
            float previousDip, effectClock;
            bool castSplashed;
            const int Points = 25;
            readonly Vector3[] points = new Vector3[Points];

            public RodView(VoyageGame game, Rod rod, bool tip)
            {
                g = game; Rod = rod; ShowTip = tip;
                deckPosition = g.Cam.transform.position; deckRotation = g.Cam.transform.rotation;
                deckFov = 2 * Mathf.Atan(g.Cam.orthographicSize / Mathf.Max(1, Vector3.Distance(deckPosition, g.Captain.Root.position))) * Mathf.Rad2Deg;
                foreach (var renderer in rod.Root.GetComponentsInChildren<Renderer>(true))
                    deckRodRenderers.Add((renderer, renderer.forceRenderingOff));
                outward = g.Boat.TransformDirection(rod.Outward); outward.y = 0; outward.Normalize();
                right = Vector3.Cross(Vector3.up, outward);
                castStart = g.Boat.TransformPoint(rod.TipLocal);
                root = new GameObject("Captain rod view").transform; root.SetParent(g.transform, false);
                rig = new GameObject("Hands and rod").transform; rig.SetParent(root, false);
                var lib = ArtLibrary.Get();
                var fpArt = Resources.Load<RodViewArt>("RodViewArt");
                var fp = fpArt != null ? fpArt.Model : null;
                pole = ArtLibrary.Spawn(fp != null ? fp : lib?.FishingRod, rig, Vector3.zero, Quaternion.identity)?.transform;
                if (pole == null) throw new System.InvalidOperationException("Rod view requires ArtLibrary FishingRod");
                if (fp == null)
                {
                    ArtLibrary.AimAlong(pole.gameObject, Vector3.forward, 2.1f);
                    // Temporary geometric mitten poses, replaced automatically by the authored FP model.
                    Hand(new Vector3(.01f, -.055f, .22f), new Vector3(.11f, .10f, .16f));
                    Hand(new Vector3(-.14f, -.13f, .37f), new Vector3(.10f, .095f, .15f));
                    Visuals.Box("Captain navy cuff", rig, new Vector3(.015f, -.08f, .07f), new Vector3(.14f, .13f, .22f), Palette.HullNavy);
                    Visuals.Box("Reeling navy cuff", rig, new Vector3(-.18f, -.19f, .22f), new Vector3(.12f, .12f, .23f), Palette.HullNavy);
                }
                else authored = new RodViewAnimation(fpArt, pole.gameObject);
                bendBone = ArtLibrary.Find(pole.gameObject, "RodTip");
                reelBone = ArtLibrary.Find(pole.gameObject, "ReelHandle");
                rodRenderers = pole.GetComponentsInChildren<Renderer>();
                var shader = Resources.Load<Shader>("RodBend");
                foreach (var r in rodRenderers)
                {
                    if (r is SkinnedMeshRenderer skinned) skinned.updateWhenOffscreen = true;
                    var source = r.sharedMaterials; var mats = new Material[source.Length];
                    for (int i = 0; i < mats.Length; i++)
                    {
                        var m = new Material(shader) { name = "Rod view bend (owned)" };
                        m.SetColor("_BaseColor", source[i] != null && source[i].HasProperty("_BaseColor") ? source[i].GetColor("_BaseColor") : Palette.Steel);
                        if (source[i] != null && source[i].HasProperty("_BaseMap")) m.SetTexture("_BaseMap", source[i].GetTexture("_BaseMap"));
                        if (fpArt != null) { m.SetColor("_BaseColor", Color.white); m.SetTexture("_BaseMap", fpArt.Atlas); }
                        ownedMaterials.Add(m); mats[i] = m;
                    }
                    r.sharedMaterials = mats;
                }
                bobber = new GameObject("Bobber reading").transform; bobber.SetParent(root, false);
                if (lib?.Bobber != null) ArtLibrary.Spawn(lib.Bobber, bobber, Vector3.zero, Quaternion.identity, 2f);
                else Visuals.Prim(PrimitiveType.Sphere, "Float", bobber, Vector3.zero, Vector3.one * .12f, Palette.Oilskin);
                line = new GameObject("Sagging fishing line").AddComponent<LineRenderer>();
                line.transform.SetParent(root, false); line.positionCount = Points; line.useWorldSpace = true;
                line.widthMultiplier = .007f; line.sharedMaterial = Visuals.Mat(Palette.Hex("DFE7D9"));
                line.shadowCastingMode = ShadowCastingMode.Off; line.numCornerVertices = 3;
                fish = new GameObject("Reading fish").AddComponent<FishShadow>(); fish.transform.SetParent(root, false);
                fish.AutomaticAdvance = false;
                fish.Initialize(rod.HookedSpecies, rod.HookedKg);
                landed = DeckFish.BuildModel(rod.HookedSpecies, rod.HookedKg, root);
                ArtLibrary.AimAlong(landed.gameObject, Vector3.forward, FishShadow.LengthFor(rod.HookedSpecies, rod.HookedKg));
                landedMouth = FishViewMouth(landed, fish.Length);
                landed.gameObject.SetActive(false);
            }

            void Hand(Vector3 position, Vector3 size)
            {
                Visuals.Prim(PrimitiveType.Capsule, "Ivory glove", rig, position, size, Palette.Rail);
                Visuals.Prim(PrimitiveType.Sphere, "Glove thumb", rig, position + new Vector3(-.055f, .025f, .015f), size * .5f, Palette.Rail);
            }
            static float Ease(float t) { t = Mathf.Clamp01(t); return t * t * (3 - 2 * t); }
            Vector3 Plane(Vector2 p) => right * p.x + outward * p.y;

            public void Update(float dt)
            {
                effectClock += dt;
                var m = Rod.Reading;
                float cast = Ease(Rod.CastAge / Rod.ViewCastSeconds);
                float back = Rod.ReadingResult.HasValue ? Ease((Rod.ResultAge - Rod.ReturnAt) / Rod.ReturnSeconds) : 0;
                float blend = cast * (1 - back);
                var captain = g.Captain.Root.position;
                var shoulder = captain - outward * .5f + right * .3f + Vector3.up * 1.25f;
                var viewPosition = captain - outward * .2f + right * .12f + Vector3.up * 1.45f;
                // A quadratic sweep passes the shoulder and follows the cast toward the water.
                var castPosition = (1 - cast) * (1 - cast) * deckPosition + 2 * (1 - cast) * cast * shoulder + cast * cast * viewPosition;
                var aim = Rod.CastTarget - outward * 2f + Vector3.up * .05f;
                var viewRotation = Quaternion.LookRotation(aim - viewPosition, Vector3.up);
                var castRotation = Quaternion.Slerp(deckRotation, viewRotation, cast);
                var boatPosition = g.Cam.transform.position; var boatRotation = g.Cam.transform.rotation;
                g.Cam.transform.SetPositionAndRotation(Vector3.Lerp(castPosition, boatPosition, back), Quaternion.Slerp(castRotation, boatRotation, back));
                g.Cam.orthographic = blend < .00001f;
                // A long lens matches the deck's framing, then opens during the sweep.
                // Standard projection keeps URP/PTS depth and refraction correct throughout.
                g.Cam.fieldOfView = Mathf.Lerp(deckFov, 53, blend); g.Cam.ResetProjectionMatrix();
                foreach (var item in deckRodRenderers)
                    if (item.renderer != null) item.renderer.forceRenderingOff = item.hidden || cast > .2f && back < .9f;
                float sway = Mathf.Sin(g.SimTime * 1.35f);
                var holdPosition = authored != null ? new Vector3(.34f, -.065f, 1.187f) : new Vector3(.38f, -.34f, .62f);
                holdPosition.y += -(1 - cast) * .65f + sway * .009f;
                // Keep the caught fish and hands in the cast's world space during the return.
                // Parenting their apparent pose to the retreating, narrowing camera makes them
                // grow across the screen instead of receding toward the captain.
                rig.position = Vector3.Lerp(castPosition + castRotation * holdPosition,
                    captain + Vector3.up * .7f, back);
                float pull = m.RodPull;
                float strike = Rod.ReadingResult.HasValue ? Mathf.Sin(Mathf.Clamp01(Rod.ResultAge / .32f) * Mathf.PI) : 0;
                rig.rotation = castRotation * (authored != null
                    ? Quaternion.Euler(-11.5f + sway * .6f, 0, sway * .5f)
                    : Quaternion.Euler(-18 - strike * 16 - Mathf.Sin(cast * Mathf.PI) * 30 + sway * .6f, -2, -8 + sway * .5f));
                rig.gameObject.SetActive(cast > .22f && back < .98f);
                authored?.Sample(Rod, dt);
                bend.SetMatrix("_WorldToRod", rig.worldToLocalMatrix); bend.SetMatrix("_RodToWorld", rig.localToWorldMatrix);
                bend.SetFloat("_Bend", authored == null ? pull * .38f : 0); foreach (var r in rodRenderers) r.SetPropertyBlock(bend);
                if (authored == null && bendBone != null) bendBone.localRotation = Quaternion.Euler(pull * 28, 0, 0);
                if (authored == null && reelBone != null && Rod.ReadingResult == StrikeResult.Hooked) reelBone.Rotate(Vector3.forward, dt * 800, Space.Self);
                var bob = Rod.CastTarget + Plane(m.Drift) + Vector3.up * (.06f - m.Dip * .30f + sway * .012f);
                if (Rod.State == RodState.Flying)
                {
                    float flight = Mathf.Clamp01(Rod.CastAge / Rod.ViewCastSeconds);
                    bob = Vector3.Lerp(castStart, Rod.CastTarget, flight) + Vector3.up * Mathf.Sin(flight * Mathf.PI) * 1.3f;
                    fish.Visibility = 0;
                }
                else
                {
                    fish.Visibility = 1 - back; fish.Depth = m.FishDepth; fish.Advance(dt);
                    fish.transform.position = Rod.CastTarget + Plane(m.FishPos);
                    fish.transform.rotation = Quaternion.LookRotation(Plane(new Vector2(Mathf.Cos(m.FishHeading), Mathf.Sin(m.FishHeading))));
                }
                if (m.Dip > .055f && previousDip <= .055f)
                { Effect(bob, false); g.audio?.Play(m.Phase == FishPhase.Take ? VoyageAudio.Cue.Reel : VoyageAudio.Cue.Select, m.Phase == FishPhase.Take ? .45f : .12f); }
                if (m.Dart && dt > 0) Effect(fish.transform.position, true);
                if (Rod.State != RodState.Flying && !castSplashed)
                { castSplashed = true; Effect(Rod.CastTarget, false); g.audio?.Play(VoyageAudio.Cue.Splash, .35f); }
                previousDip = m.Dip;
                Vector3 lineEnd = bob;
                if (Rod.ReadingResult == StrikeResult.Hooked)
                {
                    float a = Rod.ResultAge;
                    fish.Visibility = 0; landed.gameObject.SetActive(true);
                    float lift = Ease((a - Rod.ThrashSeconds) / Rod.LiftSeconds);
                    Vector3 surface = Rod.CastTarget + right * Mathf.Sin(a * 12) * .18f + outward * Mathf.Cos(a * 9) * .1f;
                    surface.y = Rod.WaterY + .10f + Mathf.Abs(Mathf.Sin(a * 13)) * .13f;
                    var up = viewPosition + viewRotation * new Vector3(.02f, -.01f, 1.8f);
                    landed.position = Vector3.Lerp(surface, up, lift) + Vector3.up * Mathf.Sin(lift * Mathf.PI) * .7f;
                    landed.position = Vector3.Lerp(landed.position, captain + Vector3.up * .4f, back);
                    landed.rotation = Quaternion.LookRotation(right) * Quaternion.Euler(Mathf.Sin(a * 17) * (1 - lift) * 25, 0, lift * 72 + Mathf.Sin(a * 9) * 6);
                    lineEnd = landed.TransformPoint(landedMouth);
                    bobber.gameObject.SetActive(false);
                    if (a < Rod.ThrashSeconds && (int)(a * 8) != (int)((a - dt) * 8)) Effect(surface, false);
                }
                else
                {
                    bobber.gameObject.SetActive(true);
                    if (Rod.ReadingResult == StrikeResult.TooEarly) bob.y += Mathf.Sin(Mathf.Clamp01(Rod.ResultAge / .55f) * Mathf.PI) * .55f;
                    bobber.position = bob; bobber.rotation = Quaternion.Euler(sway * 7, 0, m.Dip * 25);
                }
                var tip = authored?.Tip != null ? authored.Tip.position : rig.TransformPoint(new Vector3(0, -.38f * pull * Mathf.Pow(2.1f / 2, 2), 2.1f));
                float slack = Rod.ReadingResult.HasValue && Rod.ReadingResult != StrikeResult.Hooked ? .6f : Mathf.Lerp(.24f, .025f, pull);
                for (int i = 0; i < Points; i++)
                { float t = i / (float)(Points - 1); points[i] = Vector3.Lerp(tip, lineEnd, t) + Vector3.down * (4 * t * (1 - t) * slack); }
                line.SetPositions(points);
                for (int i = effects.Count - 1; i >= 0; i--)
                {
                    var e = effects[i]; float age = effectClock - e.born;
                    if (age > .65f) { Visuals.Kill(e.t.gameObject); effects.RemoveAt(i); continue; }
                    float scale = e.bubble ? .7f + age : .2f + age * 1.8f;
                    e.t.localScale = Vector3.one * scale;
                    if (e.bubble) e.t.position += Vector3.up * dt * .3f;
                }
            }

            void Effect(Vector3 position, bool bubbles)
            {
                if (effects.Count > 20) return;
                var go = new GameObject(bubbles ? "Fish dart bubbles" : "Dip ripple"); go.transform.SetParent(root, false);
                go.transform.position = new Vector3(position.x, Rod.WaterY + .025f, position.z);
                if (bubbles)
                {
                    for (int i = 0; i < 5; i++) Visuals.Prim(PrimitiveType.Sphere, "Bubble", go.transform,
                        new Vector3((i - 2) * .055f, -.05f + i * .025f, Mathf.Sin(i * 2) * .05f), Vector3.one * (.028f + i * .004f), Palette.Hex("91DAD5"));
                }
                else
                {
                    var ring = go.AddComponent<LineRenderer>(); ring.useWorldSpace = false; ring.positionCount = 41;
                    ring.widthMultiplier = .012f; ring.sharedMaterial = Visuals.Mat(Palette.Hex("91DAD5"));
                    ring.shadowCastingMode = ShadowCastingMode.Off;
                    for (int n = 0; n <= 40; n++) { float a = n * Mathf.PI * 2 / 40; ring.SetPosition(n, new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a))); }
                }
                effects.Add((go.transform, effectClock, bubbles));
            }
            public void Dispose()
            {
                foreach (var item in deckRodRenderers) if (item.renderer != null) item.renderer.forceRenderingOff = item.hidden;
                foreach (var m in ownedMaterials) if (m != null) Visuals.Kill(m);
                if (root != null) Visuals.Kill(root.gameObject);
            }
        }
    }
}

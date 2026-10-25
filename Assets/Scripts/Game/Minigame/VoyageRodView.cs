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
        // The first two plays of a minigame show its tip line. The count lives in PlayerPrefs, not the save; test
        // (SessionOnly) builds count per session and never write the pref.
        bool TipDue(string pref, ref int sessionCount)
        {
            if (!ShowTips) return false;
            if (SessionOnly) return ++sessionCount <= 2;
            int shown = PlayerPrefs.GetInt(pref, 0);
            if (shown >= 2) return false;
            PlayerPrefs.SetInt(pref, shown + 1); PlayerPrefs.Save();
            return true;
        }
        public float RodViewDeckOpacity => rodView?.DeckOpacity ?? 1;
        public void BeginRodView(Rod rod)
        {
            rodView?.Dispose();
            rodView = new RodView(this, rod, TipDue("catchline.rodTipsShown", ref rodViewCasts));
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
        void OnDestroy() { rodView?.Dispose(); rodView = null; cageView?.Dispose(); cageView = null; netView?.Dispose(); netView = null; }
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
            readonly List<Mesh> ownedMeshes = new();
            readonly List<(Transform t, float born, bool bubble)> effects = new();
            readonly MaterialPropertyBlock bend = new();
            readonly Renderer[] rodRenderers;
            readonly List<(Renderer renderer, bool hidden)> deckRodRenderers = new();
            readonly Transform bendBone, reelBone;
            readonly RodViewAnimation authored;
            readonly RodViewAtmosphere atmosphere;
            readonly float deckFov;
            float previousDip, effectClock, pushIn, scatterAt;
            bool castSplashed, breached;
            float jumpAt = -1;
            readonly float heavy;
            readonly LineRenderer vWake;
            readonly List<FishShadow> shoal = new();
            readonly List<(Transform t, float born, Vector3 velocity)> drops = new();
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
                atmosphere = new RodViewAtmosphere(root, g.transform, outward);
                rig = new GameObject("Hands and rod").transform; rig.SetParent(root, false);
                var lib = ArtLibrary.Get();
                var fpArt = Resources.Load<RodViewArt>("RodViewArt");
                var fp = fpArt == null ? null : !fpArt.UseArms && fpArt.RodOnly != null ? fpArt.RodOnly : fpArt.Model;
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
                else
                {
                    authored = new RodViewAnimation(fpArt, pole.gameObject);
                    if (!fpArt.UseArms && fp != fpArt.RodOnly) // the authored rod-only model needs no stripping
                        foreach (var skin in pole.GetComponentsInChildren<SkinnedMeshRenderer>())
                            if (RodViewArt.WithoutArms(skin) is { } rodOnly) { skin.sharedMesh = rodOnly; ownedMeshes.Add(rodOnly); }
                }
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
                bobber = atmosphere.BuildBobber(root);
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
                heavy = Mathf.InverseLerp(.25f, 1.1f, fish.Length);
                // The V the line cuts in the water while the hooked fish runs.
                vWake = new GameObject("Running line V-wake").AddComponent<LineRenderer>();
                vWake.transform.SetParent(root, false); vWake.positionCount = 3; vWake.useWorldSpace = true;
                vWake.widthMultiplier = .03f; vWake.shadowCastingMode = ShadowCastingMode.Off;
                vWake.gameObject.SetActive(false);
                // Darters can come in as two or three shadows; the extras scatter when the real one takes.
                for (int i = 1; i < rod.Reading.Shoal; i++)
                {
                    var extra = new GameObject("Shoal shadow").AddComponent<FishShadow>(); extra.transform.SetParent(root, false);
                    extra.AutomaticAdvance = false; extra.Initialize(rod.HookedSpecies, rod.HookedKg * .8f);
                    shoal.Add(extra);
                }
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
                // Handheld breathing while waiting, a kick on the strike, and a slight push-in on the take and the fight.
                bool hooked = Rod.ReadingResult == StrikeResult.Hooked;
                float since = Rod.ResultAge, t0 = g.SimTime;
                float kick = hooked && since < .35f ? (1 - since / .35f) * 1.4f : 0;
                var handheld = Quaternion.Euler(Mathf.Sin(t0 * .8f) * .35f + Mathf.Sin(since * 83) * kick, Mathf.Sin(t0 * .55f) * .3f + Mathf.Cos(since * 71) * kick * .6f, 0);
                g.Cam.transform.rotation = Quaternion.Slerp(g.Cam.transform.rotation, g.Cam.transform.rotation * handheld, blend);
                float push = hooked ? (since < Rod.ThrashSeconds ? 3 + 2 * m.Thrash : 0) : m.Phase == FishPhase.Take ? 3 : 0;
                pushIn = Mathf.MoveTowards(pushIn, push, dt * 8);
                g.Cam.fieldOfView = Mathf.Lerp(deckFov, 53 - pushIn, blend); g.Cam.ResetProjectionMatrix();
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
                    // Bottom feeders show only close and late, as they come up off the bed.
                    float seen = m.Style == FishStyle.Bottom ? Mathf.InverseLerp(.75f, .35f, m.FishDepth) : 1;
                    fish.Visibility = (1 - back) * seen; fish.Depth = m.FishDepth; fish.Advance(dt);
                    fish.transform.position = Rod.CastTarget + Plane(m.FishPos);
                    fish.transform.rotation = Quaternion.LookRotation(Plane(new Vector2(Mathf.Cos(m.FishHeading), Mathf.Sin(m.FishHeading))));
                    // Shoal shadows circle the lead fish until it takes, then scatter and fade.
                    bool scatter = m.Phase is FishPhase.Take or FishPhase.Hooked or FishPhase.Spooked or FishPhase.Gone;
                    if (!scatter) scatterAt = effectClock;
                    for (int i = 0; i < shoal.Count; i++)
                    {
                        var offset = new Vector2(Mathf.Cos(effectClock * .9f + i * 2.4f), Mathf.Sin(effectClock * .9f + i * 2.4f)) * (.35f + i * .12f);
                        offset *= 1 + (effectClock - scatterAt) * 4;
                        shoal[i].Visibility = (1 - back) * Mathf.Clamp01(1 - (effectClock - scatterAt) * 2);
                        shoal[i].Depth = Mathf.Max(.35f, m.FishDepth); shoal[i].Advance(dt);
                        shoal[i].transform.position = Rod.CastTarget + Plane(m.FishPos + offset);
                        shoal[i].transform.rotation = Quaternion.LookRotation(Plane(new Vector2(-offset.y, offset.x).normalized));
                    }
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
                    float a = Rod.ResultAge, fight = Rod.ThrashSeconds;
                    fish.Visibility = 0; landed.gameObject.SetActive(true);
                    float lift = Ease((a - fight) / Rod.LiftSeconds);
                    // The fight: the fish runs where the model takes it, thrashing at the surface; jumpers clear the water.
                    var run = Rod.CastTarget + Plane(m.FishPos);
                    if (m.Jump && jumpAt < 0) { jumpAt = a; Effect(run, true); g.audio?.Play(VoyageAudio.Cue.Splash, .3f); }
                    float jump = jumpAt >= 0 ? Mathf.Clamp01((a - jumpAt) / .55f) : 1;
                    if (jumpAt >= 0 && jump >= 1) { jumpAt = -1; Effect(run, false); g.audio?.Play(VoyageAudio.Cue.Splash, .35f); }
                    float leap = jump < 1 ? Mathf.Sin(jump * Mathf.PI) * Mathf.Lerp(.9f, .5f, heavy) : 0;
                    var surface = run + right * Mathf.Sin(a * 12) * .12f * m.Thrash;
                    surface.y = Rod.WaterY + .06f + Mathf.Abs(Mathf.Sin(a * 13)) * .1f * m.Thrash + leap;
                    // The lift: the mouth rides the line up to the hang point in front of the camera.
                    var up = viewPosition + viewRotation * new Vector3(.02f, .05f, 1.8f);
                    var mouth = Vector3.Lerp(surface, up, lift) + Vector3.up * Mathf.Sin(lift * Mathf.PI) * .5f;
                    mouth = Vector3.Lerp(mouth, captain + Vector3.up * .9f, back);
                    // Hanging from the mouth: head up, a pendulum swing that settles, tail flaps that slow down. Heavy
                    // fish swing slow, small fish flick fast, flatfish flap like a plate, eels writhe long and slow.
                    float hang = Mathf.Max(0, a - fight - Rod.LiftSeconds * .35f);
                    float period = 2 * Mathf.PI * Mathf.Sqrt(Mathf.Max(.15f, fish.Length) / 9.8f) * Mathf.Lerp(1.4f, 2.4f, heavy);
                    float swing = 34 * Mathf.Exp(-hang * 1.3f) * Mathf.Cos(hang * 2 * Mathf.PI / period);
                    bool eel = m.Style == FishStyle.Eel, flat = m.Style == FishStyle.Bottom;
                    float flap = eel ? Mathf.Sin(hang * 7) * 32 * Mathf.Exp(-hang * .8f)
                        : Mathf.Sin(hang * Mathf.Lerp(26, 11, heavy)) * 22 * Mathf.Exp(-hang * Mathf.Lerp(1.1f, 2.2f, heavy));
                    var view = g.Cam.transform;
                    var nose = Quaternion.AngleAxis(swing, view.forward) * Vector3.up;
                    var flank = Vector3.ProjectOnPlane(view.position - mouth, nose).normalized;
                    var hanging = Quaternion.LookRotation(nose, Vector3.Cross(nose, flank))
                        * Quaternion.AngleAxis(flap * (flat ? 1.4f : 1), flat ? Vector3.forward : Vector3.up);
                    var thrashing = Quaternion.LookRotation(right) * Quaternion.Euler(Mathf.Sin(a * 17) * 25 * m.Thrash, 0,
                        Mathf.Sin(a * 9) * 6 + (jump < 1 ? Mathf.Lerp(-45, 45, jump) : 0));
                    landed.rotation = Quaternion.Slerp(thrashing, hanging, Ease(lift * 1.6f));
                    landed.position += mouth - landed.TransformPoint(landedMouth);
                    lineEnd = mouth;
                    bobber.gameObject.SetActive(false);
                    if (a < fight && leap <= 0 && (int)(a * 8) != (int)((a - dt) * 8)) Effect(surface, false);
                    // Breaking the surface: a splash and a spray, then drips off the tail while it hangs.
                    if (lift > .06f && !breached) { breached = true; Effect(surface, false); Effect(surface, true); g.audio?.Play(VoyageAudio.Cue.Splash, .45f); }
                    if (breached && back < .5f && (int)(a * 5) != (int)((a - dt) * 5))
                        Drip(landed.TransformPoint(new Vector3(landedMouth.x, landedMouth.y, -landedMouth.z)));
                    // The V-wake behind the running fish.
                    bool cutting = a < fight && leap <= 0;
                    vWake.gameObject.SetActive(cutting);
                    if (cutting)
                    {
                        var dir = Plane(new Vector2(Mathf.Cos(m.FishHeading), Mathf.Sin(m.FishHeading))); var side = Vector3.Cross(Vector3.up, dir);
                        var at = new Vector3(run.x, Rod.WaterY + .02f, run.z);
                        vWake.SetPosition(0, at - dir * .55f + side * .24f); vWake.SetPosition(1, at); vWake.SetPosition(2, at - dir * .55f - side * .24f);
                        atmosphere.StyleCue(vWake.transform, .5f + .3f * m.Thrash);
                    }
                }
                else
                {
                    bobber.gameObject.SetActive(true);
                    if (Rod.ReadingResult == StrikeResult.TooEarly) bob.y += Mathf.Sin(Mathf.Clamp01(Rod.ResultAge / .55f) * Mathf.PI) * .55f;
                    bobber.position = bob; bobber.rotation = Quaternion.Euler(sway * 7 + m.Tilt * 78, 0, m.Dip * 25);
                }
                atmosphere.Update(g.Cam, bob, Rod.WaterY,
                    Rod.State != RodState.Flying && !Rod.ReadingResult.HasValue && m.Dip < .65f, g.SimTime);
                var tip = authored?.Tip != null ? authored.Tip.position : rig.TransformPoint(new Vector3(0, -.38f * pull * Mathf.Pow(2.1f / 2, 2), 2.1f));
                float slack = Rod.ReadingResult.HasValue && Rod.ReadingResult != StrikeResult.Hooked ? .6f : Mathf.Lerp(.24f, .025f, pull);
                for (int i = 0; i < Points; i++)
                { float t = i / (float)(Points - 1); points[i] = Vector3.Lerp(tip, lineEnd, t) + Vector3.down * (4 * t * (1 - t) * slack); }
                line.SetPositions(points);
                for (int i = drops.Count - 1; i >= 0; i--)
                {
                    var d = drops[i]; d.velocity += Vector3.down * 9.8f * dt; d.t.position += d.velocity * dt; drops[i] = d;
                    if (d.t.position.y < Rod.WaterY || effectClock - d.born > 1.2f) { Visuals.Kill(d.t.gameObject); drops.RemoveAt(i); }
                }
                for (int i = effects.Count - 1; i >= 0; i--)
                {
                    var e = effects[i]; float age = effectClock - e.born;
                    if (age > .65f) { Visuals.Kill(e.t.gameObject); effects.RemoveAt(i); continue; }
                    float scale = e.bubble ? .7f + age : .2f + age * 1.8f;
                    e.t.localScale = Vector3.one * scale;
                    if (e.bubble) e.t.position += Vector3.up * dt * .3f;
                    atmosphere.StyleCue(e.t, (e.bubble ? .82f : .65f) * (1 - age / .65f));
                }
            }

            void Drip(Vector3 at)
            {
                if (drops.Count > 12) return;
                var d = Visuals.Prim(PrimitiveType.Sphere, "Drip", root, Vector3.zero, Vector3.one * .025f, Palette.Hex("CDEDE9")).transform; d.position = at;
                drops.Add((d, effectClock, new Vector3(Random.Range(-.15f, .15f), -.2f, Random.Range(-.15f, .15f))));
            }

            void Effect(Vector3 position, bool bubbles)
            {
                if (effects.Count > 20) return;
                var go = new GameObject(bubbles ? "Fish dart bubbles" : "Dip ripple"); go.transform.SetParent(root, false);
                go.transform.position = new Vector3(position.x, Rod.WaterY + .025f, position.z);
                if (bubbles)
                {
                    for (int i = 0; i < 5; i++) Visuals.Prim(PrimitiveType.Sphere, "Bubble", go.transform,
                        new Vector3((i - 2) * .09f, .015f + i * .045f, Mathf.Sin(i * 2) * .09f), Vector3.one * (.105f + i * .009f), Palette.Hex("91DAD5"));
                }
                else
                {
                    var ring = go.AddComponent<LineRenderer>(); ring.useWorldSpace = false; ring.positionCount = 41;
                    ring.widthMultiplier = .026f;
                    ring.shadowCastingMode = ShadowCastingMode.Off;
                    for (int n = 0; n <= 40; n++) { float a = n * Mathf.PI * 2 / 40; ring.SetPosition(n, new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a))); }
                }
                atmosphere.StyleCue(go.transform, bubbles ? .82f : .65f);
                effects.Add((go.transform, effectClock, bubbles));
            }
            public void Dispose()
            {
                atmosphere.Dispose();
                foreach (var item in deckRodRenderers) if (item.renderer != null) item.renderer.forceRenderingOff = item.hidden;
                foreach (var m in ownedMaterials) if (m != null) Visuals.Kill(m);
                foreach (var m in ownedMeshes) if (m != null) Visuals.Kill(m);
                if (root != null) Visuals.Kill(root.gameObject);
            }
        }
    }
}

using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;
using Visuals = Catchline.Prototype.Visuals;

namespace Catchline.Game
{
    public enum MendGrade { None, Clean, Ragged }

    // Net repair (docs/plans/MINIGAMES.md, section 5): one drag laces new twine over the hole along a zigzag.
    // Trace points are in metres on the net, x along the panel and y across it, the hole centred on the origin.
    public static class MendRules
    {
        public const float Tolerance = .06f;
        public static readonly Vector2[] Path = Zigzag();
        public static float Length { get; } = PathLength();

        static Vector2[] Zigzag()
        {
            var p = new Vector2[7];
            for (int i = 0; i < p.Length; i++) p[i] = new Vector2(-.18f + i * .06f, i % 2 == 0 ? -.11f : .11f);
            return p;
        }
        static float PathLength() { float l = 0; for (int i = 1; i < Path.Length; i++) l += Vector2.Distance(Path[i - 1], Path[i]); return l; }

        // Nearest point on the stretch of zigzag between arc lengths lo and hi: distance off it and arc length along it.
        // The legs lie closer together than the tolerance, so only the stretch the needle has reached may count.
        public static (float off, float along) Nearest(Vector2 q, float lo = 0, float hi = float.MaxValue)
        {
            float best = float.MaxValue, arc = 0, at = lo;
            for (int i = 1; i < Path.Length; i++)
            {
                Vector2 a = Path[i - 1], d = Path[i] - a; float len = d.magnitude;
                float t0 = Mathf.Clamp01((lo - arc) / len), t1 = Mathf.Clamp01((hi - arc) / len);
                if (t1 > t0 || (t0 == t1 && lo >= arc && lo <= arc + len))
                {
                    float t = Mathf.Clamp(Vector2.Dot(q - a, d) / (len * len), t0, t1);
                    float off = Vector2.Distance(q, a + d * t);
                    if (off < best) { best = off; at = arc + t * len; }
                }
                arc += len;
            }
            return (best, at);
        }

        // Progress only advances in order, a short step at a time: the needle cannot jump ahead to a later zig.
        public static (float progress, float worst) Follow(IReadOnlyList<Vector2> trace)
        {
            float progress = 0, worst = 0;
            if (trace == null) return (0, 0);
            foreach (var q in trace)
            {
                var (off, along) = Nearest(q, Mathf.Max(0, progress - .03f), progress + .08f);
                if (off > Tolerance * 2.5f) { if (progress > .02f) worst = Mathf.Max(worst, off); continue; } // wandered off
                progress = Mathf.Max(progress, along);
                if (progress > .02f) worst = Mathf.Max(worst, off);
            }
            return (progress, worst);
        }

        public static MendGrade Grade(IReadOnlyList<Vector2> trace)
        {
            var (progress, worst) = Follow(trace);
            if (progress < Length * .35f) return MendGrade.None; // a tap or a short scratch: carry on
            return progress >= Length * .9f && worst <= Tolerance ? MendGrade.Clean : MendGrade.Ragged;
        }
    }

    // The captain mends a torn net on the quay by the net loft: the camera comes down over the panel, a zigzag
    // crosses the hole and the netting needle follows the finger, laying twine behind it.
    public partial class VoyageGame
    {
        RepairView repairView;
        public bool RepairViewActive => repairView != null;
        public string MendResult { get; private set; }
        public MendGrade LastMend { get; private set; }
        Rect repairLeaveRect;
        readonly List<Vector2> mendStroke = new();
        bool mendDragging;

        public bool BeginMend()
        {
            if (repairView != null || CurrentMode != Mode.Harbour || scenery == null) return false;
            if (State.TornNets <= 0 || State.NetInventory >= GameData.NetInventoryCapacity) return false;
            panelOpen = false; MendResult = null; LastMend = MendGrade.None;
            repairView = new RepairView(this, scenery.TransformPoint(new Vector3(13.6f, HarbourQuayTop + .01f, 3.3f)));
            return true;
        }

        public MendGrade TraceMend(IReadOnlyList<Vector2> trace)
        {
            if (repairView == null || !repairView.Waiting) return MendGrade.None;
            var grade = MendRules.Grade(trace);
            if (grade == MendGrade.None) { repairView.Twine(0); return grade; }
            LastMend = grade;
            audio?.Play(VoyageAudio.Cue.Stitch, .20f);
            if (grade == MendGrade.Clean && State.MendNet())
            {
                MendResult = State.TornNets > 0 ? $"Mended · {State.TornNets} still torn" : "Mended · back on the rack";
                audio?.Play(VoyageAudio.Cue.Purchase, .5f);
                repairView.Mended();
                SaveGame();
            }
            else
            {
                MendResult = "The knots slipped · try again";
                audio?.Play(VoyageAudio.Cue.NetSlap, .4f);
                repairView.Twine(0);
            }
            return grade;
        }

        public void LeaveRepair() { repairView?.Close(); }

        void UpdateRepairView(float dt)
        {
            if (repairView == null) return;
            if (!repairView.Closing && CurrentMode != Mode.Harbour) LeaveRepair();
            if (!repairView.Update(dt))
            {
                repairView.Dispose(); repairView = null; Cam.orthographic = true; Cam.ResetProjectionMatrix();
                if (CurrentMode == Mode.Harbour) { hudTab = HudTab.Supplies; panelOpen = true; }
            }
        }

        void HandleRepairInput(Keyboard kb)
        {
            if (kb != null && kb.escapeKey.wasPressedThisFrame) { LeaveRepair(); return; }
            var pointer = Pointer.current;
            if (pointer == null || !Application.isFocused || repairView == null) return;
            var at = pointer.position.ReadValue();
            if (pointer.press.wasPressedThisFrame)
            {
                if (repairLeaveRect.Contains(ToGui(at))) return;
                mendStroke.Clear(); mendDragging = repairView.Waiting; MendResult = null;
            }
            if (mendDragging && pointer.press.isPressed && repairView.ToNet(at) is Vector2 p)
            {
                mendStroke.Add(p); repairView.Needle(p);
                repairView.Twine(MendRules.Follow(mendStroke).progress);
            }
            if (mendDragging && pointer.press.wasReleasedThisFrame) { mendDragging = false; TraceMend(mendStroke); }
        }

        void InterfaceRepairView()
        {
            string text = repairView.Waiting ? MendResult ?? "Drag the needle along the zigzag" : MendResult;
            if (text != null && repairView.Opacity > .5f && !repairView.Closing)
            {
                var band = new Rect((iw - 560) / 2, Edge, 560, 52);
                coastalUi.Box("repairview/hint", band, "chip-dark", new Color(1, 1, 1, .82f));
                coastalUi.Text("repairview/hint/text", band, text, Skin.Type.Body, LastMend == MendGrade.Clean && !repairView.Waiting ? Skin.Brass : Skin.Cream, TextAnchor.MiddleCenter);
            }
            repairLeaveRect = new Rect(iw - Edge - 132, ih - Edge - 54, 132, 54);
            if (!repairView.Closing) { IButton("repairview/leave", repairLeaveRect, repairView.Waiting ? "Leave" : "Done", LeaveRepair, false); Block(repairLeaveRect); }
        }

        sealed class RepairView
        {
            const float SweepSeconds = .45f;
            public bool Waiting => !mended && returnAge < 0;
            public bool Closing => returnAge >= 0;
            public float Opacity => Ease(age / SweepSeconds) * (1 - Ease(Mathf.Max(0, returnAge) / SweepSeconds));

            readonly VoyageGame g;
            readonly Transform root, needle, patch;
            readonly LineRenderer guide, twine;
            readonly List<Renderer> hidden = new();
            readonly Vector3 deckPosition, eye, top, along, across;
            readonly Quaternion deckRotation, view;
            readonly float deckFov;
            float age, returnAge = -1, mendedAge = -1;
            bool mended;

            public RepairView(VoyageGame game, Vector3 at)
            {
                g = game;
                deckPosition = g.Cam.transform.position; deckRotation = g.Cam.transform.rotation;
                deckFov = 2 * Mathf.Atan(g.Cam.orthographicSize / Mathf.Max(1, Vector3.Distance(deckPosition, at))) * Mathf.Rad2Deg;
                top = at; along = g.scenery.right; across = g.scenery.forward;
                // Looking north across the quay from the water side, 55 degrees down: the panel fills two thirds of the frame.
                eye = top - across * .78f + Vector3.up * 1.12f;
                view = Quaternion.LookRotation(top - eye, Vector3.up);

                root = new GameObject("Captain repair view").transform; root.SetParent(g.transform, false);
                foreach (var r in UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                {
                    var b = r.bounds; var flatOff = b.center - top; flatOff.y = 0;
                    // Props near the panel go (crab pots, bollards, a gull); the quay deck and buildings stay.
                    if (!r.enabled || b.size.y > 2.5f || b.size.x > 1.8f || b.size.z > 1.8f || b.max.y < top.y + .05f || flatOff.magnitude > 1.3f) continue;
                    r.enabled = false; hidden.Add(r);
                }
                var kit = ArtLibrary.Get()?.M("RepairKit");
                var flat = Quaternion.LookRotation(across, Vector3.up);
                if (Part(kit, "TornNet", top, flat) == null)
                    Visuals.Box("Torn net", root, top, new Vector3(1.2f, .01f, .8f), Palette.Hex("7C8B7E"));
                patch = Part(kit, "MendedPatch", top + Vector3.up * .002f, flat);
                if (patch != null) patch.gameObject.SetActive(false);
                needle = Part(kit, "NettingNeedle", top, flat * Quaternion.Euler(0, -35, 0));
                Part(kit, "TwineBall", top + along * .72f - across * .22f, flat);

                guide = Line("Zigzag", Palette.Hex("1F3B4D"), .006f); // dark ink: the quay boards are pale
                guide.positionCount = MendRules.Path.Length;
                for (int i = 0; i < MendRules.Path.Length; i++) guide.SetPosition(i, World(MendRules.Path[i]) + Vector3.up * .006f);
                twine = Line("New twine", Palette.Hex("A8742E"), .012f);
                Twine(0);
                Needle(MendRules.Path[0]);
            }

            LineRenderer Line(string name, Color color, float width)
            {
                var line = new GameObject(name).AddComponent<LineRenderer>(); line.transform.SetParent(root, false);
                line.useWorldSpace = true; line.widthMultiplier = width; line.numCornerVertices = 2;
                line.sharedMaterial = Visuals.Mat(color); line.shadowCastingMode = ShadowCastingMode.Off;
                return line;
            }

            Transform Part(GameObject kit, string name, Vector3 at, Quaternion rotation)
            {
                if (kit == null) return null;
                var go = ArtLibrary.Spawn(kit, root, Vector3.zero, kit.transform.localRotation);
                var part = ArtLibrary.Find(go, name);
                if (part == null) { Visuals.Kill(go); return null; }
                for (var t = part; t != go.transform && t.parent != null; t = t.parent)
                    foreach (Transform sibling in t.parent) sibling.gameObject.SetActive(sibling == t);
                go.name = name; go.transform.position = at; go.transform.rotation = rotation * kit.transform.localRotation;
                return go.transform;
            }

            Vector3 World(Vector2 p) => top + along * p.x + across * p.y;

            public Vector2? ToNet(Vector2 screen)
            {
                var ray = g.Cam.ScreenPointToRay(screen);
                if (!new Plane(Vector3.up, top).Raycast(ray, out float t)) return null;
                var d = ray.GetPoint(t) - top;
                return new Vector2(Vector3.Dot(d, along), Vector3.Dot(d, across));
            }

            public void Needle(Vector2 p) { if (needle != null) needle.position = World(p) + Vector3.up * .02f; }

            // Twine laid along the zigzag up to this arc length.
            public void Twine(float progress)
            {
                var points = new List<Vector3> { World(MendRules.Path[0]) };
                float arc = 0;
                for (int i = 1; i < MendRules.Path.Length && arc < progress; i++)
                {
                    float len = Vector2.Distance(MendRules.Path[i - 1], MendRules.Path[i]);
                    float t = Mathf.Clamp01((progress - arc) / len);
                    points.Add(World(Vector2.Lerp(MendRules.Path[i - 1], MendRules.Path[i], t)));
                    arc += len;
                }
                twine.positionCount = points.Count;
                for (int i = 0; i < points.Count; i++) twine.SetPosition(i, points[i] + Vector3.up * .01f);
                twine.gameObject.SetActive(points.Count > 1);
            }

            public void Mended()
            {
                mended = true; mendedAge = 0;
                guide.gameObject.SetActive(false); twine.gameObject.SetActive(false);
                if (patch != null) patch.gameObject.SetActive(true);
            }

            public void Close() { if (returnAge < 0) returnAge = 0; }

            static float Ease(float t) { t = Mathf.Clamp01(t); return t * t * (3 - 2 * t); }

            public bool Update(float dt)
            {
                age += dt;
                if (mendedAge >= 0 && (mendedAge += dt) > 1.6f) Close();
                float back = returnAge >= 0 ? Ease((returnAge += dt) / SweepSeconds) : 0;
                float blend = Ease(age / SweepSeconds) * (1 - back);
                g.Cam.transform.SetPositionAndRotation(Vector3.Lerp(deckPosition, eye, blend), Quaternion.Slerp(deckRotation, view, blend));
                g.Cam.orthographic = blend < .00001f;
                g.Cam.fieldOfView = Mathf.Lerp(deckFov, 50, blend); g.Cam.ResetProjectionMatrix();
                root.gameObject.SetActive(back < .98f);
                if (Waiting) guide.widthMultiplier = .006f * (1 + .25f * Mathf.Sin(age * 5));
                return returnAge < SweepSeconds;
            }

            public void Dispose()
            {
                foreach (var r in hidden) if (r != null) r.enabled = true;
                hidden.Clear();
                if (root != null) Visuals.Kill(root.gameObject);
            }
        }
    }
}

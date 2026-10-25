using System;
using System.Collections.Generic;
using Catchline.Game.Deck;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;
using Visuals = Catchline.Prototype.Visuals;

namespace Catchline.Game
{
    public enum GutGrade { None, Clean, Ragged }

    // One drag along the belly from vent to gills (docs/plans/MINIGAMES.md, section 3). Cut points are in cut space:
    // x is 0 at the vent and 1 at the gills, y the distance off the line in fish lengths. The reward is speed only.
    public static class GutRules
    {
        public const float Tolerance = .08f, CleanSeconds = .6f, RaggedSeconds = 3f;
        public static GutGrade Grade(IReadOnlyList<Vector2> cut)
        {
            if (cut == null || cut.Count < 2) return GutGrade.None;
            float start = cut[0].x, end = cut[cut.Count - 1].x, off = 0;
            foreach (var p in cut) off = Mathf.Max(off, Mathf.Abs(p.y));
            if (end - start < .3f) return GutGrade.None; // a tap or a short scratch: try again
            return start <= .2f && end >= .85f && off <= Tolerance ? GutGrade.Clean : GutGrade.Ragged;
        }
    }

    // The captain at the process table: the camera drops to the board, one fish at a time lies on it, and a drag along
    // the dotted belly line cuts it. Clean cuts finish at once and build a streak; ragged ones take the crew's time.
    public partial class VoyageGame
    {
        GutView gutView;
        public bool GutViewActive => gutView != null;
        public int GutStreak { get; private set; }
        public string GutResult { get; private set; }
        public GutGrade LastGut { get; private set; }
        public bool GutWaiting => gutView?.Waiting == true;
        Rect gutLeaveRect;
        readonly List<Vector2> gutStroke = new();
        bool gutDragging;

        // DeckScheduler.CaptainBench: the captain has walked to the table with a fish claimed.
        void BeginGut(Job job, Action done, Action cancel)
        {
            Captain.Do("Gutting", float.MaxValue, null, cancel);
            gutView ??= new GutView(this, job.At);
            gutView.Load(job.Fish[0], done, cancel);
            toastUntil = catchUntil = 0;
        }

        public bool CaptainGutAt(Station table) =>
            Scheduler != null && workers.TryGetValue(Captain, out var w) && Scheduler.CaptainTable(w, table);

        public GutGrade CutGut(IReadOnlyList<Vector2> cut)
        {
            if (gutView == null || !gutView.Waiting) return GutGrade.None;
            var grade = GutRules.Grade(cut);
            if (grade == GutGrade.None) return grade;
            LastGut = grade;
            GutStreak = grade == GutGrade.Clean ? GutStreak + 1 : 0;
            GutResult = grade == GutGrade.Ragged ? "Ragged cut · slower" : GutStreak > 1 ? $"Clean cut · {GutStreak} in a row" : "Clean cut";
            audio?.Play(VoyageAudio.Cue.Gut, .6f);
            var (done, cancel) = gutView.Cut(grade, cut);
            Captain.Do("Gutting", grade == GutGrade.Clean ? GutRules.CleanSeconds : GutRules.RaggedSeconds, () =>
            {
                done();
                // Straight on to the next fish waiting at this table; back to the deck when there is none.
                if (gutView != null && !CaptainGutAt(gutView.Table)) gutView.Close();
            }, cancel);
            return grade;
        }

        public void LeaveGut()
        {
            if (gutView == null) return;
            var v = gutView; v.Close();
            if (v.Waiting || v.Cutting) Captain.Stop(); // releases the claimed fish through the job's cancel
        }

        void UpdateGutView(float dt)
        {
            if (gutView == null) return;
            if (!gutView.Closing && CurrentMode != Mode.Fishing) LeaveGut();
            if (!gutView.Update(dt)) { gutView.Dispose(); gutView = null; Cam.orthographic = true; Cam.ResetProjectionMatrix(); }
        }

        void HandleGutInput(Keyboard kb)
        {
            if (kb != null && kb.escapeKey.wasPressedThisFrame) { LeaveGut(); return; }
            var pointer = Pointer.current;
            if (pointer == null || !Application.isFocused || gutView == null) return;
            var at = pointer.position.ReadValue();
            if (pointer.press.wasPressedThisFrame)
            {
                if (gutLeaveRect.Contains(ToGui(at))) return;
                gutStroke.Clear(); gutDragging = gutView.Waiting;
            }
            if (gutDragging && pointer.press.isPressed) { gutStroke.Add(gutView.ToCut(at)); gutView.Knife(at); }
            if (gutDragging && pointer.press.wasReleasedThisFrame)
            {
                gutDragging = false;
                CutGut(gutStroke);
            }
        }

        void InterfaceGutView()
        {
            string text = gutView.Waiting ? "Drag along the belly, vent to gills" : GutResult;
            if (text != null && gutView.Opacity > .5f && !gutView.Closing)
            {
                var band = new Rect((iw - 520) / 2, Edge, 520, 52);
                coastalUi.Box("gutview/hint", band, "chip-dark", new Color(1, 1, 1, .82f));
                coastalUi.Text("gutview/hint/text", band, text, Skin.Type.Body, !gutView.Waiting && LastGut == GutGrade.Clean ? Skin.Brass : Skin.Cream, TextAnchor.MiddleCenter);
            }
            if (GutStreak > 1 && !gutView.Closing)
            {
                var chip = new Rect(Edge, Edge, 150, 52);
                coastalUi.Box("gutview/streak", chip, "chip-dark", new Color(1, 1, 1, .82f));
                coastalUi.Text("gutview/streak/text", chip, $"Streak {GutStreak}", Skin.Type.Body, Skin.Brass, TextAnchor.MiddleCenter);
            }
            gutLeaveRect = new Rect(iw - Edge - 132, ih - Edge - 54, 132, 54);
            if (!gutView.Closing) { IButton("gutview/leave", gutLeaveRect, "Leave", LeaveGut, false); Block(gutLeaveRect); }
        }

        sealed class GutView
        {
            const float SweepSeconds = .45f, FishLength = .5f;
            public readonly Station Table;
            public bool Waiting => fish != null && cutAge < 0;
            public bool Cutting => fish != null && cutAge >= 0;
            public bool Closing => returnAge >= 0;
            public float Opacity => Ease(age / SweepSeconds) * (1 - Ease(Mathf.Max(0, returnAge) / SweepSeconds));

            readonly VoyageGame g;
            readonly Transform root, board, knife, open, ragged;
            readonly LineRenderer guide;
            readonly List<Renderer> hidden = new();
            readonly Vector3 deckPosition, eye, top, along, across;
            readonly Quaternion deckRotation, view, flat;
            readonly float deckFov;
            Transform fish, slitHolder;
            Action done, cancel;
            float age, returnAge = -1, cutAge = -1, cutFrom, cutTo;
            Vector3 vent, gills;

            public GutView(VoyageGame game, Station table)
            {
                g = game; Table = table;
                deckPosition = g.Cam.transform.position; deckRotation = g.Cam.transform.rotation;
                deckFov = 2 * Mathf.Atan(g.Cam.orthographicSize / Mathf.Max(1, Vector3.Distance(deckPosition, g.Captain.Root.position))) * Mathf.Rad2Deg;
                var at = g.Boat.TransformPoint(table.Position);
                // Stand where the captain stands, looking across the board: the fish lies left to right in front of them.
                var toward = at - g.Captain.Root.position; toward.y = 0;
                if (toward.sqrMagnitude < .01f) toward = g.Boat.right;
                toward.Normalize();
                along = Vector3.Cross(Vector3.up, toward); across = toward;
                top = new Vector3(at.x, g.Boat.position.y + TableTop(at), at.z);
                eye = top - toward * .26f + Vector3.up * .44f; // half a metre off, sixty degrees down: the board fills the frame
                view = Quaternion.LookRotation(top - eye, Vector3.up);

                root = new GameObject("Captain gut view").transform; root.SetParent(g.transform, false);
                foreach (var r in g.Captain.Root.GetComponentsInChildren<Renderer>()) if (r.enabled) { r.enabled = false; hidden.Add(r); }
                // Whatever stands on the worktop (the waiting fish, crates) would fill the lens half a metre away.
                foreach (var r in UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                {
                    var b = r.bounds; var flatOff = b.center - top; flatOff.y = 0;
                    if (!r.enabled || b.size.y > 1.4f || b.max.y < top.y + .03f || flatOff.magnitude > 1.1f) continue;
                    r.enabled = false; hidden.Add(r);
                }
                var lib = ArtLibrary.Get();
                var kit = lib?.M("GutKit");
                flat = Quaternion.LookRotation(across, Vector3.up); // kit +X runs along the board, left to right
                board = Part(kit, "GutBoard", top, flat);
                if (board == null)
                {
                    board = new GameObject("Gut board").transform; board.SetParent(root, false); board.position = top;
                    Visuals.Box("Board", board, new Vector3(0, -.02f, 0), new Vector3(.7f, .04f, .36f), Palette.Hex("C58B50"));
                    board.rotation = flat;
                }
                knife = Part(kit, "GutKnife", top, flat);
                open = Part(kit, "BellyOpen", top, flat);
                ragged = Part(kit, "BellyRagged", top, flat);
                Part(kit, "GutBucket", top + across * .05f - along * .55f - Vector3.up * .02f, flat);
                if (open != null) open.gameObject.SetActive(false);
                if (ragged != null) ragged.gameObject.SetActive(false);

                guide = new GameObject("Belly line").AddComponent<LineRenderer>(); guide.transform.SetParent(root, false);
                guide.useWorldSpace = true; guide.widthMultiplier = .008f; guide.positionCount = 2;
                guide.sharedMaterial = Visuals.Mat(Palette.Hex("F3F0DC")); guide.shadowCastingMode = ShadowCastingMode.Off;
                guide.textureMode = LineTextureMode.Tile;
            }

            Transform Part(GameObject kit, string name, Vector3 at, Quaternion rotation)
            {
                if (kit == null) return null;
                var go = ArtLibrary.Spawn(kit, root, Vector3.zero, kit.transform.localRotation);
                // Show only this item: hide everything off the path from the kit root down to it (the FBX nests them).
                var part = ArtLibrary.Find(go, name);
                if (part == null) { Visuals.Kill(go); return null; }
                for (var t = part; t != go.transform && t.parent != null; t = t.parent)
                    foreach (Transform sibling in t.parent) sibling.gameObject.SetActive(sibling == t);
                go.name = name; go.transform.position = at; go.transform.rotation = rotation * kit.transform.localRotation;
                return go.transform;
            }

            // Highest point of the table's own props near the station (the worktop); a waist-high bench otherwise.
            float TableTop(Vector3 at)
            {
                float best = -1;
                foreach (var r in g.Boat.GetComponentsInChildren<MeshRenderer>())
                {
                    var b = r.bounds;
                    if (b.size.y > 1.4f || !b.Contains(new Vector3(at.x, b.center.y, at.z))) continue;
                    best = Mathf.Max(best, b.max.y - g.Boat.position.y);
                }
                return best > .3f ? best + .01f : .95f;
            }

            public void Load(CaughtFish caught, Action done, Action cancel)
            {
                this.done = done; this.cancel = cancel; cutAge = -1;
                if (fish != null) Visuals.Kill(fish.gameObject);
                if (open != null) open.gameObject.SetActive(false);
                if (ragged != null) ragged.gameObject.SetActive(false);
                fish = DeckFish.BuildModel(caught.Species, caught.Kg, root);
                // BuildModel lays the fish on its side, nose -Z, belly +X. Measured unrotated from world bounds (skinned
                // meshes' localBounds are in bone space), then turned over so the head lies to screen right (+along) and the
                // belly faces the captain: local Z -> -along, X -> -across, Y -> down.
                fish.SetPositionAndRotation(top, Quaternion.identity);
                var bounds = new Bounds(top, Vector3.zero); bool any = false;
                foreach (var r in fish.GetComponentsInChildren<Renderer>())
                    if (any) bounds.Encapsulate(r.bounds); else { bounds = r.bounds; any = true; }
                var lo = bounds.min - top; var hi = bounds.max - top;
                float minA = -hi.z, maxA = -lo.z, near = -hi.x, low = -hi.y, high = -lo.y;
                fish.rotation = Quaternion.AngleAxis(180, across) * Quaternion.LookRotation(along, Vector3.up);
                if (any && maxA > minA)
                {
                    // Close-up scale: every fish fills the board the same way (extents scale about the pivot).
                    float k = FishLength / (maxA - minA);
                    fish.localScale *= k; minA *= k; maxA *= k; near *= k; low *= k; high *= k;
                }
                else { minA = -FishLength / 2; maxA = FishLength / 2; near = -.06f; low = 0; high = .05f; }
                fish.position = top + Vector3.up * -low;
                var line = top + across * (near + .03f) + Vector3.up * (high - low + .003f);
                float len = maxA - minA;
                // Vent a third of the way from the tail, gills a fifth from the head (head at +along, screen right).
                vent = line + along * (minA + len * .35f); gills = line + along * (maxA - len * .2f);
                guide.SetPosition(0, vent); guide.SetPosition(1, gills); guide.gameObject.SetActive(true);
                if (knife != null) knife.position = vent - across * .06f + Vector3.up * .01f;
            }

            // Screen position to cut space (see GutRules).
            public Vector2 ToCut(Vector2 screen)
            {
                Vector2 a = g.Cam.WorldToScreenPoint(vent), b = g.Cam.WorldToScreenPoint(gills);
                var d = b - a; float len = Mathf.Max(1, d.magnitude);
                var p = screen - a;
                return new Vector2(Vector2.Dot(p, d) / (len * len), (d.x * p.y - d.y * p.x) / (len * len) * (gills - vent).magnitude / FishLength);
            }

            public void Knife(Vector2 screen)
            {
                if (knife == null) return;
                var ray = g.Cam.ScreenPointToRay(screen);
                if (new Plane(Vector3.up, vent).Raycast(ray, out float t)) knife.position = ray.GetPoint(t) + Vector3.up * .01f;
            }

            public (Action done, Action cancel) Cut(GutGrade grade, IReadOnlyList<Vector2> cut)
            {
                cutAge = 0;
                cutFrom = Mathf.Clamp01(Mathf.Min(cut[0].x, cut[cut.Count - 1].x));
                cutTo = Mathf.Clamp01(Mathf.Max(cut[0].x, cut[cut.Count - 1].x));
                guide.gameObject.SetActive(false);
                var slit = grade == GutGrade.Clean ? open : ragged;
                if (slit != null)
                {
                    slit.gameObject.SetActive(true);
                    // Fit the modelled slit to the cut in a board-aligned holder (X along, Z across): the kit's own pivot,
                    // axes and scale vary, so it is measured in world space and stretched to the cut's length and a thin width.
                    if (slitHolder == null) { slitHolder = new GameObject("Slit").transform; slitHolder.SetParent(root, false); }
                    slitHolder.SetPositionAndRotation(vent, Quaternion.LookRotation(across, Vector3.up)); slitHolder.localScale = Vector3.one;
                    slit.SetParent(slitHolder, true);
                    slit.localScale = Vector3.one;
                    slit.rotation = flat * (ArtLibrary.Get()?.M("GutKit")?.transform.localRotation ?? Quaternion.identity);
                    var b = Bounds(slit, slitHolder);
                    float length = Mathf.Max(.02f, (cutTo - cutFrom) * (gills - vent).magnitude);
                    slitHolder.localScale = new Vector3(length / Mathf.Max(.001f, b.size.x), Mathf.Min(1, .01f / Mathf.Max(.001f, b.size.y)), .03f / Mathf.Max(.001f, b.size.z));
                    // Holder-space centre to the middle of the cut, its top just above the belly line.
                    var centre = slitHolder.TransformPoint(new Vector3(b.center.x, b.max.y, b.center.z));
                    slitHolder.position += Vector3.Lerp(vent, gills, (cutFrom + cutTo) / 2) + Vector3.up * .002f - centre;
                }
                return (done, cancel);
            }

            // Mesh bounds of everything under t, in space's local axes.
            static Bounds Bounds(Transform t, Transform space)
            {
                var b = new Bounds(); bool any = false;
                foreach (var f in t.GetComponentsInChildren<MeshFilter>())
                {
                    if (f.sharedMesh == null) continue;
                    var m = f.sharedMesh.bounds;
                    for (int i = 0; i < 8; i++)
                    {
                        var p = space.InverseTransformPoint(f.transform.TransformPoint(m.center + Vector3.Scale(m.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1))));
                        if (any) b.Encapsulate(p); else { b = new Bounds(p, Vector3.zero); any = true; }
                    }
                }
                return b;
            }

            public void Close() { if (returnAge < 0) returnAge = 0; }

            static float Ease(float t) { t = Mathf.Clamp01(t); return t * t * (3 - 2 * t); }

            // False once the view has returned to the deck.
            public bool Update(float dt)
            {
                age += dt;
                if (cutAge >= 0) cutAge += dt;
                float back = returnAge >= 0 ? Ease((returnAge += dt) / SweepSeconds) : 0;
                float blend = Ease(age / SweepSeconds) * (1 - back);
                g.Cam.transform.SetPositionAndRotation(Vector3.Lerp(deckPosition, eye, blend), Quaternion.Slerp(deckRotation, view, blend));
                g.Cam.orthographic = blend < .00001f;
                g.Cam.fieldOfView = Mathf.Lerp(deckFov, 55, blend); g.Cam.ResetProjectionMatrix();
                root.gameObject.SetActive(back < .98f);
                if (Waiting) guide.widthMultiplier = .008f * (1 + .25f * Mathf.Sin(age * 5));
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

using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;
using Visuals = Catchline.Prototype.Visuals;

namespace Catchline.Game
{
    // The captain's crab cage (docs/plans/MINIGAMES.md, section 2): the camera leans over the rail at the buoy, fast
    // taps haul the cage up through the water, a drag frees a snag, and the crabs come onto a sorting board one at a
    // time to be flicked up (keep) or down (back over the side). Rules live in CageModel; this file only presents it.
    public partial class VoyageGame
    {
        CageView cageView;
        int cageViewHauls;
        public bool CageViewActive => cageView != null;
        public CageModel Cage => cageView?.Model;
        public string CageResult { get; private set; }
        Rect cageLeaveRect;
        Vector2 cagePress; bool cagePressed;

        void BeginCageView(int buoy, Action<CageModel> sorted, Action cancel)
        {
            cageView?.Dispose();
            CageResult = null;
            cageView = new CageView(this, buoy, new CageModel(State.Rng,Abilities?.DoubleWeight == true), sorted, cancel, TipDue("catchline.cageTipsShown", ref cageViewHauls));
            toastUntil = catchUntil = 0;
        }

        public void TapCage() { if (cageView?.Model.Phase == CagePhase.Pull) { cageView.Model.Tap(Abilities?.WinchRate(null) ?? 1); if (cageView.Model.Tapped) audio?.Play(VoyageAudio.Cue.Winch, .3f); } }
        public void DragCage(int dir) { if (cageView != null && !cageView.Model.Drag(dir) && cageView.Model.Phase == CagePhase.Snag) audio?.Play(VoyageAudio.Cue.Moor, .4f); }
        public void FlickCage(bool keep) => cageView?.Flick(keep);
        public void LeaveCage() { if (cageView != null && !cageView.Finished) { var v = cageView; cageView = null; v.Dispose(); Cam.orthographic = true; Cam.ResetProjectionMatrix(); v.Cancel(); } }

        void UpdateCageView(float dt)
        {
            if (cageView == null) return;
            if (!cageView.Finished && (CurrentMode != Mode.Fishing || buoyWorkers[cageView.Buoy] != Captain)) { LeaveCage(); return; }
            if (!cageView.Update(dt)) { cageView.Dispose(); cageView = null; Cam.orthographic = true; Cam.ResetProjectionMatrix(); }
        }

        void HandleCageInput(Keyboard kb)
        {
            if (kb != null)
            {
                if (kb.escapeKey.wasPressedThisFrame) { LeaveCage(); return; }
                if (kb.spaceKey.wasPressedThisFrame) TapCage();
                if (kb.leftArrowKey.wasPressedThisFrame) DragCage(-1);
                if (kb.rightArrowKey.wasPressedThisFrame) DragCage(1);
                if (kb.upArrowKey.wasPressedThisFrame) FlickCage(true);
                if (kb.downArrowKey.wasPressedThisFrame) FlickCage(false);
            }
            var pointer = Pointer.current;
            if (pointer == null || !Application.isFocused) return;
            var at = pointer.position.ReadValue();
            if (pointer.press.wasPressedThisFrame)
            {
                if (cageLeaveRect.Contains(ToGui(at))) return;
                cagePress = at; cagePressed = true;
                TapCage(); // on press, so fast tapping feels instant
            }
            if (cagePressed && pointer.press.wasReleasedThisFrame)
            {
                cagePressed = false;
                var d = at - cagePress; float min = 28 * Mathf.Max(1, Screen.dpi / 160f);
                if (Mathf.Abs(d.x) > min && Mathf.Abs(d.x) > Mathf.Abs(d.y)) DragCage(d.x > 0 ? 1 : -1);
                else if (Mathf.Abs(d.y) > min && Mathf.Abs(d.y) > Mathf.Abs(d.x)) FlickCage(d.y > 0);
            }
        }

        void InterfaceCageView()
        {
            var m = cageView.Model;
            string hint = m.Phase switch
            {
                CagePhase.Pull => "Tap fast to haul the cage",
                CagePhase.Snag => m.SnagDirection < 0 ? "Snagged! Drag left to free it" : "Snagged! Drag right to free it",
                CagePhase.Sort => "Flick up to keep, down to throw back",
                _ => null,
            };
            if (cageView.Finished && CageResult != null)
            {
                var card = new Rect((iw - 460) / 2, ih * .16f, 460, 64);
                coastalUi.Box("cageview/result", card, "chip-dark", new Color(1, 1, 1, .92f));
                coastalUi.Text("cageview/result/text", card, CageResult, Skin.Type.Body, Skin.Cream, TextAnchor.MiddleCenter);
            }
            else if (hint != null && cageView.Opacity > .5f)
            {
                var band = new Rect((iw - 520) / 2, Edge, 520, 52);
                coastalUi.Box("cageview/hint", band, "chip-dark", new Color(1, 1, 1, .82f));
                coastalUi.Text("cageview/hint/text", band, hint, Skin.Type.Body, m.Phase == CagePhase.Snag ? Skin.Brass : Skin.Cream, TextAnchor.MiddleCenter);
            }
            if (!cageView.Finished && m.Phase is CagePhase.Pull or CagePhase.Snag)
            {
                // Depth meter: the rope marks between the sea bed and the rail.
                var track = new Rect(iw - Edge - 34, ih * .24f, 22, ih * .46f);
                coastalUi.Box("cageview/depth", track, "chip-dark", new Color(1, 1, 1, .6f));
                float f = Mathf.Clamp01(m.Lift);
                coastalUi.Box("cageview/depth/fill", new Rect(track.x + 4, track.yMax - 4 - (track.height - 8) * f, track.width - 8, (track.height - 8) * f), "panel-cream", Skin.Brass);
            }
            if (cageView.ShowTip && m.Phase == CagePhase.Sort && !cageView.Finished)
            {
                // On a dark chip like the hint band, so it reads over water and the board alike; clear of Leave.
                float w = Mathf.Min(iw - 2 * Edge - 150, 900);
                var tip = new Rect(Mathf.Max(Edge, (iw - w) / 2 - 60), ih - Edge - 52, w, 48);
                coastalUi.Box("cageview/tip/band", tip, "chip-dark", new Color(1, 1, 1, .82f));
                coastalUi.Text("cageview/tip", new Rect(tip.x + 12, tip.y, tip.width - 24, tip.height),
                    "Keep crabs past the red mark. Undersize crabs and females with orange eggs go back.", Skin.Type.Small, Skin.Cream, TextAnchor.MiddleCenter);
            }
            cageLeaveRect = new Rect(iw - Edge - 132, ih - Edge - 54, 132, 54);
            if (!cageView.Finished) { IButton("cageview/leave", cageLeaveRect, "Leave", LeaveCage, false); Block(cageLeaveRect); }
        }

        sealed class CageView
        {
            public readonly CageModel Model;
            public readonly int Buoy;
            public readonly bool ShowTip;
            public bool Finished { get; private set; }
            public float Opacity => Ease(age / SweepSeconds) * (1 - Ease(returnAge / SweepSeconds));
            const float SweepSeconds = .45f, ResultSeconds = 1.3f, Depth = 1.5f;

            readonly VoyageGame g;
            readonly Action<CageModel> sorted;
            readonly Action cancel;
            readonly Transform root, pot, hauler, board, gauge, arrow, lid, bridle, sheave;
            readonly Quaternion lidRest, sheaveRest;
            float sheaveTurn;
            readonly LineRenderer rope;
            readonly Vector3 anchor, outward, right, deckPosition, viewPosition, haulPoint, boardPoint;
            readonly Quaternion deckRotation, viewRotation;
            readonly float deckFov, legalLength;
            readonly List<Transform> inPot = new();
            readonly List<Renderer> hidden = new();
            readonly List<(Transform t, Vector3 from, Vector3 to, float born, bool keep)> flying = new();
            readonly List<(Transform t, float born)> ripples = new();
            Transform onBoard;
            float age, returnAge = -1, doneAge, lastLift;

            public CageView(VoyageGame game, int buoy, CageModel model, Action<CageModel> sorted, Action cancel, bool tip)
            {
                g = game; Buoy = buoy; Model = model; this.sorted = sorted; this.cancel = cancel; ShowTip = tip;
                deckPosition = g.Cam.transform.position; deckRotation = g.Cam.transform.rotation;
                deckFov = 2 * Mathf.Atan(g.Cam.orthographicSize / Mathf.Max(1, Vector3.Distance(deckPosition, g.Captain.Root.position))) * Mathf.Rad2Deg;
                anchor = g.Boat.TransformPoint(g.buoyAnchors[buoy]);
                var centre = g.Boat.TransformPoint(g.State.HullDef.Center);
                outward = anchor - centre; outward.y = 0;
                if (outward.sqrMagnitude < .01f) outward = g.Boat.forward;
                outward.Normalize();
                right = Vector3.Cross(Vector3.up, outward);
                // Leaning over the rail at the buoy: the eye just inboard of the anchor, looking out and down at the water.
                viewPosition = new Vector3(anchor.x, Rod.WaterY + 1.7f, anchor.z) - outward * .3f;
                // Thirty degrees down: open water to the top of the frame, the cage rising mid-frame, the rail below.
                viewRotation = Quaternion.LookRotation(outward * Mathf.Cos(30 * Mathf.Deg2Rad) - Vector3.up * Mathf.Sin(30 * Mathf.Deg2Rad), Vector3.up);
                var fwd = viewRotation * Vector3.forward;
                haulPoint = viewPosition + viewRotation * new Vector3(.55f, -.46f, 1f);
                boardPoint = viewPosition + viewRotation * new Vector3(.08f, -.33f, 1.22f);

                root = new GameObject("Captain cage view").transform; root.SetParent(g.transform, false);
                // The captain's own body and the deck buoy sit where the camera is; hide them for the view.
                foreach (var t in new[] { g.Captain.Root, g.buoyModels[buoy] })
                    if (t != null) foreach (var r in t.GetComponentsInChildren<Renderer>()) if (r.enabled) { r.enabled = false; hidden.Add(r); }
                var lib = ArtLibrary.Get();
                // The CageKit (CAGE-ART-1) when imported; the EmptyPot and primitive stand-ins otherwise.
                pot = ArtLibrary.Spawn(lib?.M("CrabCage") ?? lib?.M("EmptyPot"), root, Vector3.zero, Quaternion.LookRotation(outward))?.transform;
                lid = pot != null ? ArtLibrary.Find(pot.gameObject, "Lid") : null; bridle = pot != null ? ArtLibrary.Find(pot.gameObject, "Bridle") : null;
                if (lid != null) lidRest = lid.localRotation;
                if (pot == null)
                {
                    pot = new GameObject("Crab cage").transform; pot.SetParent(root, false);
                    Visuals.Box("Cage base", pot, new Vector3(0, .02f, 0), new Vector3(.6f, .04f, .45f), Palette.HullNavy);
                    for (int i = 0; i < 4; i++)
                        Visuals.Box("Cage hoop", pot, new Vector3(-.27f + i * .18f, .2f, 0), new Vector3(.03f, .36f, .45f), Palette.Hex("C9A46A"));
                }
                // The crabs ride inside the cage until their turn on the board.
                for (int i = 0; i < model.Crabs.Count; i++)
                {
                    var crab = Crab(model.Crabs[i], pot, lib);
                    crab.localPosition = new Vector3(-.16f + (i % 2) * .3f, .08f, -.08f + (i / 2) * .16f);
                    crab.localRotation = Quaternion.Euler(0, i * 70, 0);
                    inPot.Add(crab);
                }
                // The hauler's sheave turns about its local X, so local X lies along the rail (right) and the rope runs outward.
                hauler = ArtLibrary.Spawn(lib?.M("PotHauler"), root, Vector3.zero, Quaternion.identity)?.transform;
                if (hauler != null)
                {
                    hauler.rotation = Quaternion.LookRotation(outward);
                    sheave = ArtLibrary.Find(hauler.gameObject, "Sheave");
                    hauler.position = haulPoint - hauler.rotation * new Vector3(0, .247f, 0);
                    if (sheave != null) sheaveRest = sheave.localRotation;
                }
                else
                {
                    hauler = new GameObject("Pot hauler wheel").transform; hauler.SetParent(root, false);
                    hauler.position = haulPoint; hauler.rotation = Quaternion.LookRotation(right);
                    Visuals.Prim(PrimitiveType.Cylinder, "Hauler sheave", hauler, Vector3.zero, new Vector3(.3f, .03f, .3f), Palette.Steel).transform.localRotation = Quaternion.Euler(90, 0, 0);
                    Visuals.Box("Hauler spoke", hauler, Vector3.zero, new Vector3(.04f, .26f, .045f), Palette.Accent);
                }
                rope = new GameObject("Cage rope").AddComponent<LineRenderer>();
                rope.transform.SetParent(root, false); rope.positionCount = 2; rope.useWorldSpace = true;
                rope.widthMultiplier = .014f; rope.sharedMaterial = Visuals.Mat(Palette.Hex("D1AF76")); rope.shadowCastingMode = ShadowCastingMode.Off;

                board = new GameObject("Sorting board").transform; board.SetParent(root, false);
                board.position = boardPoint; board.rotation = Quaternion.LookRotation(Vector3.ProjectOnPlane(fwd, Vector3.up), Vector3.up);
                legalLength = FishShadow.LengthFor(Species.Crab, CageModel.LegalKg);
                gauge = new GameObject("Size gauge").transform; gauge.SetParent(board, false);
                // The board's gauge edge is its local -Z, toward the camera; zero at x -0.26.
                var kit = ArtLibrary.Spawn(lib?.M("SortingBoard"), board, Vector3.zero, Quaternion.identity);
                if (kit != null && ArtLibrary.Find(kit, "LegalMark") is { } mark)
                    mark.localPosition = new Vector3(-.26f + legalLength, mark.localPosition.y, mark.localPosition.z);
                else
                {
                    Visuals.Box("Board", board, Vector3.zero, new Vector3(.62f, .03f, .3f), Palette.DeckWoodDark);
                    gauge.localPosition = new Vector3(0, .02f, -.12f);
                    Visuals.Box("Gauge rule", gauge, Vector3.zero, new Vector3(.56f, .008f, .035f), Palette.Hex("F4EFE3"));
                    Visuals.Box("Legal mark", gauge, new Vector3(-.26f + legalLength, .006f, 0), new Vector3(.014f, .012f, .05f), Palette.Hex("C8442E"));
                }
                board.gameObject.SetActive(false);

                arrow = new GameObject("Snag arrow").transform; arrow.SetParent(root, false);
                for (int i = 0; i < 2; i++)
                {
                    var chevron = new GameObject("Chevron").transform; chevron.SetParent(arrow, false); chevron.localPosition = Vector3.right * i * .14f;
                    Visuals.Box("Arm", chevron, new Vector3(0, .045f, 0), new Vector3(.03f, .12f, .03f), Palette.Hex("F2C14E")).transform.localRotation = Quaternion.Euler(0, 0, 40);
                    Visuals.Box("Arm", chevron, new Vector3(0, -.045f, 0), new Vector3(.03f, .12f, .03f), Palette.Hex("F2C14E")).transform.localRotation = Quaternion.Euler(0, 0, -40);
                }
                arrow.gameObject.SetActive(false);
                g.audio?.Play(VoyageAudio.Cue.Moor, .4f);
            }

            static Transform Crab(CageModel.Crab c, Transform parent, ArtLibrary lib)
            {
                var berried = c.Berried ? lib?.M("CrabBerried") : null;
                var crab = berried != null ? ArtLibrary.Spawn(berried, parent, Vector3.zero, Quaternion.identity).transform : DeckFish.BuildModel(Species.Crab, c.Kg, parent);
                ArtLibrary.AimAlong(crab.gameObject, Vector3.right, FishShadow.LengthFor(Species.Crab, c.Kg));
                if (c.Berried && berried == null)
                    for (int i = 0; i < 5; i++)
                        Visuals.Prim(PrimitiveType.Sphere, "Egg mass", crab, new Vector3((i - 2) * .025f, -.01f, (i % 2) * .03f - .015f), Vector3.one * .045f, Palette.Hex("F08A24"));
                return crab;
            }

            static float Ease(float t) { t = Mathf.Clamp01(t); return t * t * (3 - 2 * t); }

            // A flick that comes before the crab has settled on the board is held for it, never dropped.
            public void Flick(bool keep)
            {
                if (Finished || Model.Current == null) return;
                if (onBoard == null || age - boardSince < .12f) { pendingFlick = keep; return; }
                pendingFlick = null;
                Model.Flick(keep);
                var from = onBoard.position;
                var to = keep ? viewPosition + Vector3.up * .5f - outward * .9f : new Vector3(anchor.x, Rod.WaterY, anchor.z) + outward * 3.2f + right * UnityEngine.Random.Range(-.6f, .6f);
                flying.Add((onBoard, from, to, age, keep));
                onBoard = null;
                g.audio?.Play(VoyageAudio.Cue.Click, .5f); g.audio?.Play(keep ? VoyageAudio.Cue.Stow : VoyageAudio.Cue.Cast, .35f);
            }
            float boardSince;
            bool? pendingFlick;

            // False once the view has returned to the deck.
            public bool Update(float dt)
            {
                age += dt;
                if (!Finished) Model.Tick(dt);
                float sweep = Ease(age / SweepSeconds), back = returnAge >= 0 ? Ease((returnAge += dt) / SweepSeconds) : 0;
                float blend = sweep * (1 - back);
                g.Cam.transform.SetPositionAndRotation(Vector3.Lerp(deckPosition, viewPosition, blend), Quaternion.Slerp(deckRotation, viewRotation, blend));
                g.Cam.orthographic = blend < .00001f;
                g.Cam.fieldOfView = Mathf.Lerp(deckFov, 52, blend); g.Cam.ResetProjectionMatrix();
                root.gameObject.SetActive(back < .98f);
                if (returnAge >= SweepSeconds) return false;

                // The cage rises from the sea bed; a snag shakes it sideways and shows which way to drag.
                float lift = Model.Phase == CagePhase.Sort || Model.Phase == CagePhase.Done ? 1 : Model.Lift;
                var water = new Vector3(anchor.x, Rod.WaterY, anchor.z) + outward * 2.5f;
                var shake = right * Model.Shudder * Mathf.Sin(age * 38) * .05f;
                var potAt = water + Vector3.down * (Depth * (1 - lift) + .1f) + shake;
                if (Model.Phase is CagePhase.Sort or CagePhase.Done)
                {
                    // Swung in over the rail beside the board.
                    float swing = Ease((age - sortSince) / .5f);
                    if (lid != null) lid.localRotation = lidRest * Quaternion.Euler(-90 * swing, 0, 0);
                    potAt = Vector3.Lerp(water + Vector3.up * .1f, boardPoint + viewRotation * new Vector3(-.95f, -.02f, .55f), swing);
                }
                pot.position = potAt;
                pot.rotation = Quaternion.LookRotation(outward) * Quaternion.Euler(Model.Shudder * Mathf.Sin(age * 31) * 6, 0, Model.Shudder * Mathf.Sin(age * 27) * 8);
                rope.SetPosition(0, haulPoint); rope.SetPosition(1, bridle != null ? bridle.position : pot.position + Vector3.up * .4f);
                rope.enabled = sortSince < 0 || age - sortSince < .5f; // unclipped once the cage is aboard
                if (sheave != null) sheave.localRotation = sheaveRest * Quaternion.Euler(sheaveTurn += (lift - lastLift) * 1400, 0, 0);
                else hauler.Rotate(Vector3.forward, (lift - lastLift) * 1400, Space.Self);
                if (lift >= .92f && lastLift < .92f) Ripple(water);
                lastLift = lift;
                arrow.gameObject.SetActive(Model.Phase == CagePhase.Snag);
                if (Model.Phase == CagePhase.Snag)
                {
                    arrow.position = Vector3.Lerp(water, pot.position, .5f) + right * Model.SnagDirection * (.3f + Mathf.Repeat(age * 1.2f, 1) * .2f);
                    arrow.rotation = Quaternion.LookRotation(g.Cam.transform.forward) * Quaternion.Euler(0, 0, Model.SnagDirection < 0 ? 180 : 0);
                }

                if (Model.Phase is CagePhase.Sort && sortSince < 0) sortSince = age;
                if (sortSince >= 0)
                {
                    board.gameObject.SetActive(true);
                    // Next crab out of the cage onto the board, its back against the gauge's zero.
                    if (onBoard == null && Model.Current is { } crab && age - sortSince > .5f)
                    {
                        onBoard = inPot[Model.Index]; onBoard.SetParent(board, true);
                        boardSince = age; g.audio?.Play(VoyageAudio.Cue.CrabClack, .45f);
                    }
                    if (onBoard != null)
                    {
                        float len = FishShadow.LengthFor(Species.Crab, Model.Crabs[Model.Index].Kg);
                        var target = board.TransformPoint(new Vector3(-.26f + len / 2, .05f, -.02f));
                        onBoard.position = Vector3.Lerp(onBoard.position, target, 1 - Mathf.Exp(-dt * 14));
                        onBoard.localRotation = Quaternion.Slerp(onBoard.localRotation, Quaternion.Euler(0, 0, Mathf.Sin(age * 9) * 3), 1 - Mathf.Exp(-dt * 10));
                        if (pendingFlick is { } held && age - boardSince >= .12f) Flick(held);
                    }
                }
                for (int i = flying.Count - 1; i >= 0; i--)
                {
                    var f = flying[i]; float t = (age - f.born) / .5f;
                    f.t.position = Vector3.Lerp(f.from, f.to, Ease(t)) + Vector3.up * Mathf.Sin(Mathf.Clamp01(t) * Mathf.PI) * (f.keep ? .25f : .5f);
                    f.t.Rotate(Vector3.right, dt * (f.keep ? 200 : 540), Space.Self);
                    if (t >= 1) { if (!f.keep) { Ripple(f.to); g.audio?.Play(VoyageAudio.Cue.Splash, .3f); } Visuals.Kill(f.t.gameObject); flying.RemoveAt(i); }
                }
                for (int i = ripples.Count - 1; i >= 0; i--)
                {
                    float t = (age - ripples[i].born) / .8f;
                    ripples[i].t.localScale = Vector3.one * Mathf.Lerp(.12f, .7f, t);
                    if (t >= 1) { Visuals.Kill(ripples[i].t.gameObject); ripples.RemoveAt(i); }
                }

                if (!Finished && Model.Phase == CagePhase.Done && flying.Count == 0)
                {
                    Finished = true; doneAge = age;
                    sorted?.Invoke(Model);
                    g.audio?.Play(VoyageAudio.Cue.Land, .5f);
                }
                if (Finished && returnAge < 0 && age - doneAge >= ResultSeconds) returnAge = 0;
                return true;
            }
            float sortSince = -1;

            void Ripple(Vector3 at)
            {
                var go = new GameObject("Cage ripple"); go.transform.SetParent(root, false);
                go.transform.position = new Vector3(at.x, Rod.WaterY + .03f, at.z);
                var ring = go.AddComponent<LineRenderer>(); ring.useWorldSpace = false; ring.positionCount = 33;
                ring.widthMultiplier = .025f; ring.sharedMaterial = Visuals.Mat(Palette.Hex("CDEDE9")); ring.shadowCastingMode = ShadowCastingMode.Off;
                for (int n = 0; n <= 32; n++) { float a = n * Mathf.PI * 2 / 32; ring.SetPosition(n, new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a))); }
                ripples.Add((go.transform, age));
            }

            public void Cancel() => cancel?.Invoke();
            public void Dispose()
            {
                foreach (var r in hidden) if (r != null) r.enabled = true;
                hidden.Clear();
                if (root != null) Visuals.Kill(root.gameObject);
            }
        }
    }
}

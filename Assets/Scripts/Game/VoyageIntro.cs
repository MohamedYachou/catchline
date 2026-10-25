using UnityEngine;
using Visuals = Catchline.Prototype.Visuals;

namespace Catchline.Game
{
    // The new-game intro: a dawn fly-in from the open sea, past the lighthouse and through the harbour mouth, settling
    // on the captain's boat in the normal harbour camera. Logo first, then three short captions. A tap skips to the
    // last second. It plays once, for a new game (and for the rowboat tier in the test build). Mo was away when it was
    // made, so its words and path are Claude's call, logged in comms.md for review.
    public partial class VoyageGame
    {
        public const float IntroSeconds = 11f;
        float introAge = -1;
        Quaternion introDeckRotation;
        Transform introRoot;
        RodViewAtmosphere introSky;
        public bool IntroActive => introAge >= 0;

        static readonly (float t, Vector3 at, Vector3 look)[] IntroPath =
        {
            (0f, new Vector3(-6.5f, 3.2f, -40f), new Vector3(5f, 2.5f, -12f)),
            (4f, new Vector3(-6.5f, 4.5f, -22f), new Vector3(-3f, .5f, -4f)),
            (8f, new Vector3(-13f, 6.5f, -9f), new Vector3(-21f, -.4f, -.6f)),
        };
        static readonly (float from, float to, string text)[] IntroCaptions =
        {
            (4.4f, 7.2f, "Gull Harbour, first light."),
            (7.5f, 10.4f, "One small boat. A whole sea of fish."),
        };

        public void BeginIntro()
        {
            EndIntro();
            introAge = 0; introDeckRotation = Cam.transform.rotation;
            introRoot = new GameObject("Intro sky").transform; introRoot.SetParent(transform, false);
            introSky = new RodViewAtmosphere(introRoot, transform, Vector3.forward);
            audio?.Play(VoyageAudio.Cue.Gull, .35f); audio?.Play(VoyageAudio.Cue.Bell, .25f);
        }

        public void SkipIntro() { if (IntroActive && introAge < IntroSeconds - 1.2f) introAge = IntroSeconds - 1.2f; }

        void EndIntro()
        {
            introAge = -1;
            introSky?.Dispose(); introSky = null;
            if (introRoot != null) Visuals.Kill(introRoot.gameObject);
            introRoot = null;
        }

        // Called after the normal camera has placed itself: the intro overrides it and hands back over the last 2.5 s.
        void ApplyIntroCamera(float dt)
        {
            if (!IntroActive) return;
            if (CurrentMode != Mode.Harbour || MenuOpen && !showTitle) { FinishIntro(); return; }
            if (showTitle) return; // waits behind the title until Start is pressed
            introAge += dt;
            if (introAge >= IntroSeconds) { FinishIntro(); return; }
            // The normal harbour pose as a long lens, so the hand-over to the orthographic camera is seamless.
            var deckFocus = camCenter;
            float distance = SeaCameraDistance();
            var deckAt = deckFocus - introDeckRotation * Vector3.forward * distance;
            float deckFov = 2 * Mathf.Atan(Cam.orthographicSize / distance) * Mathf.Rad2Deg;
            Vector3 at, look; float fov;
            float settle = Mathf.SmoothStep(0, 1, (introAge - (IntroSeconds - 2.5f)) / 2.5f);
            int seg = 0; while (seg < IntroPath.Length - 2 && introAge > IntroPath[seg + 1].t) seg++;
            var a = IntroPath[seg]; var b = IntroPath[seg + 1];
            float u = Mathf.SmoothStep(0, 1, Mathf.InverseLerp(a.t, b.t, introAge));
            at = Vector3.Lerp(a.at, b.at, u); look = Vector3.Lerp(a.look, b.look, u);
            fov = 50;
            var pathRotation = Quaternion.LookRotation(look - at, Vector3.up);
            at = Vector3.Lerp(at, deckAt, settle);
            var rotation = Quaternion.Slerp(pathRotation, introDeckRotation, settle);
            fov = Mathf.Lerp(fov, deckFov, settle * settle);
            Cam.transform.SetPositionAndRotation(at, rotation);
            Cam.orthographic = false; Cam.fieldOfView = fov; Cam.ResetProjectionMatrix();
            if (seaSurface != null) seaSurface.position = new Vector3(at.x + Cam.transform.forward.x * 25, seaSurface.position.y, at.z + Cam.transform.forward.z * 25);
            introSky?.Update(Cam, at, Rod.WaterY, false, SimTime);
        }

        void FinishIntro()
        {
            EndIntro();
            Cam.transform.rotation = introDeckRotation;
            Cam.orthographic = true; Cam.ResetProjectionMatrix();
            Cam.transform.position = camCenter - Cam.transform.forward * SeaCameraDistance();
            if (seaSurface != null) seaSurface.localPosition = new Vector3(0, seaSurface.localPosition.y, 0);
        }

        void InterfaceIntro()
        {
            float t = introAge;
            float logo = Mathf.Clamp01((t - .8f) / 1.2f) * (1 - Mathf.Clamp01((t - 3.6f) / .8f));
            if (logo > .01f)
            {
                float w = Mathf.Min(560, iw - 64), h = w * .33f;
                var r = new Rect((iw - w) / 2, ih * .3f - h / 2, w, h);
                coastalUi.Art("intro/logo", r, "logo-catchline");
                Fade("intro/logo", logo);
            }
            foreach (var c in IntroCaptions)
            {
                float k = Mathf.Clamp01((t - c.from) / .6f) * (1 - Mathf.Clamp01((t - c.to + .6f) / .6f));
                if (k <= .01f) continue;
                var band = new Rect(Edge, ih * .2f, iw - 2 * Edge, 56); // upper third: the boats sit low in the frame
                coastalUi.Text("intro/caption/" + c.from, band, c.text, Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleCenter, null, true);
                Fade("intro/caption/" + c.from, k);
            }
            var skip = new Rect(iw - Edge - 112, Edge, 112, 48);
            if (t < IntroSeconds - 1.4f) { IButton("intro/skip", skip, "Skip", SkipIntro, false); Block(skip); }
        }

        void Fade(string id, float alpha)
        {
            var t = coastalUi.Root.Find(id);
            if (t == null) return;
            var cg = t.GetComponent<CanvasGroup>();
            if (cg == null) cg = t.gameObject.AddComponent<CanvasGroup>();
            cg.alpha = alpha; cg.blocksRaycasts = false;
        }
    }
}

using System.Collections.Generic;
using Catchline.Game.Sea;
using UnityEngine;
using Visuals = Catchline.Prototype.Visuals;

namespace Catchline.Game
{
    // Landmarks along the sea lane and the rare moments on the way (docs/plans/HARBOUR-PLAN.md, travel ideas 2 and 5).
    // Channel markers frame the lane where it leaves the map edge, a bell buoy rides at its middle, and a wreck or a
    // seal rock sits well clear of it. About one leg in two meets a moment: dolphins running alongside, gulls diving on a
    // shoal, a floating crate worth picking up, or a fog bank. A model that is not imported yet is simply left out.
    public partial class VoyageGame
    {
        enum SeaMomentKind { None, Dolphins, Gulls, Crate, Fog }
        IReadOnlyList<Vector2> momentRoute;
        Transform momentRoot;
        SeaMomentKind moment;
        Vector2 momentAt, bellAt;
        bool bellRung;
        float momentAge = -1, momentFog, baseFogDensity;
        Color baseFogColor; bool baseFog, fogTouched;
        readonly List<Transform> momentActors = new();
        public string SeaMomentName => moment == SeaMomentKind.None ? null : moment.ToString();

        void TickSeaMoments(float dt)
        {
            if (Leg is not (TripLeg.SeaOut or TripLeg.SeaHome) || Sailor == null || Navigation == null || scenery == null)
            { if (moment != SeaMomentKind.None) EndMoment(); RestoreMomentFog(); return; }
            if (!ReferenceEquals(Sailor.Route, momentRoute) && Sailor.Route != null && Sailor.Route.Count > 1 && Leg is TripLeg.SeaOut or TripLeg.SeaHome)
                BeginSeaLeg(Sailor.Route);
            // The bell buoy rings once as the boat passes it.
            if (!bellRung && momentRoot != null && Vector2.Distance(Sailor.Position, bellAt) < 14f) { bellRung = true; audio?.Play(VoyageAudio.Cue.Bell, .4f); }
            if (moment == SeaMomentKind.None || momentRoot == null) { RestoreMomentFog(); return; }
            float near = Vector2.Distance(Sailor.Position, momentAt);
            if (momentAge < 0 && near < 18f) { momentAge = 0; if (moment == SeaMomentKind.Gulls) audio?.Play(VoyageAudio.Cue.Gull, .45f); if (moment == SeaMomentKind.Dolphins) audio?.Play(VoyageAudio.Cue.Splash, .35f); }
            if (momentAge < 0) return;
            momentAge += dt;
            var water = new Vector3(momentAt.x, Rod.WaterY, momentAt.y);
            switch (moment)
            {
                case SeaMomentKind.Dolphins:
                {
                    // They run alongside the bow for a while, each leaping on its own beat.
                    var forward = new Vector3(Mathf.Cos(Sailor.Heading), 0, Mathf.Sin(Sailor.Heading));
                    var side = new Vector3(-forward.z, 0, forward.x);
                    var boat = new Vector3(Sailor.Position.x, Rod.WaterY, Sailor.Position.y);
                    for (int i = 0; i < momentActors.Count; i++)
                    {
                        float beat = Mathf.Repeat(momentAge * .62f + i * .37f, 1f);
                        float arc = Mathf.Sin(beat * Mathf.PI);
                        var at = boat + side * (2.6f + i * 1.1f) * (i % 2 == 0 ? 1 : -1) + forward * (1.5f + i * .9f + beat * 1.6f);
                        momentActors[i].position = at + Vector3.up * (arc * .9f - .35f);
                        momentActors[i].rotation = Quaternion.LookRotation(forward) * Quaternion.Euler(Mathf.Lerp(-35, 35, beat), 0, 0);
                        momentActors[i].gameObject.SetActive(momentAge < 8f && beat > .08f && beat < .92f);
                    }
                    if (momentAge >= 8f) EndMoment();
                    break;
                }
                case SeaMomentKind.Gulls:
                    for (int i = 0; i < momentActors.Count; i++)
                    {
                        float cycle = Mathf.Repeat(momentAge * .5f + i * .27f, 1f);
                        var spot = water + new Vector3(Mathf.Sin(i * 2.1f) * 2.2f, 0, Mathf.Cos(i * 1.7f) * 2.2f);
                        momentActors[i].position = spot + Vector3.up * Mathf.Lerp(7f, -.2f, cycle * cycle);
                        momentActors[i].gameObject.SetActive(cycle < .97f);
                    }
                    if (near > 40f || momentAge > 30f) EndMoment();
                    break;
                case SeaMomentKind.Crate:
                {
                    var crate = momentActors[0];
                    crate.position = water + Vector3.up * (Mathf.Sin(momentAge * 1.6f) * .05f + .08f);
                    crate.rotation = Quaternion.Euler(Mathf.Sin(momentAge * 1.2f) * 6, momentAge * 9, Mathf.Cos(momentAge) * 5);
                    if (near < State.HullDef.NavigationRadius + 2.2f)
                    {
                        int coins = 12 + State.Rng.Next(29);
                        State.Coins += coins; Toast($"Picked up a floating crate: +{coins} coins.");
                        audio?.Play(VoyageAudio.Cue.Purchase, .5f);
                        EndMoment();
                    }
                    else if (near > 40f && momentAge > 4f) EndMoment();
                    break;
                }
                case SeaMomentKind.Fog:
                    // The bank thickens as the boat sails into it and thins behind.
                    momentFog = Mathf.Clamp01(1 - (near - 6f) / 22f);
                    if (!fogTouched) { fogTouched = true; baseFog = RenderSettings.fog; baseFogDensity = RenderSettings.fogDensity; baseFogColor = RenderSettings.fogColor; Toast("Fog bank ahead, skipper."); audio?.Play(VoyageAudio.Cue.Horn, .5f); }
                    RenderSettings.fog = true; RenderSettings.fogMode = FogMode.ExponentialSquared;
                    RenderSettings.fogColor = Color.Lerp(baseFogColor, Palette.Hex("D9E4E2"), momentFog);
                    RenderSettings.fogDensity = Mathf.Lerp(baseFog ? baseFogDensity : 0, .045f, momentFog);
                    if (momentAge > 6f && near > 30f) EndMoment();
                    break;
            }
        }

        void BeginSeaLeg(IReadOnlyList<Vector2> route)
        {
            momentRoute = route; EndMoment();
            if (momentRoot != null) Visuals.Kill(momentRoot.gameObject);
            momentRoot = new GameObject("Sea lane landmarks and moments").transform; momentRoot.SetParent(scenery, false);
            var lib = ArtLibrary.Get();
            float length = SeaNav.Length(route);
            Vector2 At(float u, out Vector2 dir)
            {
                float want = u * length, run = 0;
                for (int i = 1; i < route.Count; i++)
                {
                    float seg = Vector2.Distance(route[i - 1], route[i]);
                    if (run + seg >= want && seg > 0) { dir = (route[i] - route[i - 1]) / seg; return Vector2.Lerp(route[i - 1], route[i], (want - run) / seg); }
                    run += seg;
                }
                dir = (route[route.Count - 1] - route[route.Count - 2]).normalized; return route[route.Count - 1];
            }
            bool Open(Vector2 p) => Navigation.InsideBorder(p) && !Navigation.Blocked(p);
            void Mark(string model, Vector2 p, float yaw = 0)
            {
                var prefab = lib?.M(model);
                if (prefab != null && Open(p)) ArtLibrary.Spawn(prefab, momentRoot, new Vector3(p.x, Rod.WaterY, p.y), Quaternion.Euler(0, yaw, 0));
            }
            // The lane end at the map edge: home-side for both legs.
            bool outbound = Leg == TripLeg.SeaOut;
            float edgeU = outbound ? Mathf.Min(.12f, 10f / Mathf.Max(1, length)) : 1 - Mathf.Min(.12f, 10f / Mathf.Max(1, length));
            var gate = At(edgeU, out var gateDir); var gateSide = new Vector2(-gateDir.y, gateDir.x);
            float half = SeaLanes.Clearances[0] * .5f + 1f;
            Mark("ChannelMarkerRed", gate + gateSide * half); Mark("ChannelMarkerGreen", gate - gateSide * half);
            var middle = At(.5f, out var midDir); var midSide = new Vector2(-midDir.y, midDir.x);
            bellAt = middle + midSide * (half + 2f); bellRung = false;
            Mark("BellBuoy", bellAt);
            int seed = ActiveSpot * 31 + (outbound ? 0 : 7);
            var far = At(.3f + (seed % 5) * .08f, out var farDir); var farSide = new Vector2(-farDir.y, farDir.x) * (seed % 2 == 0 ? 1 : -1);
            Mark(seed % 3 == 0 ? "SealRocks" : "Wreck", far + farSide * 13f, seed * 47 % 360);

            // At most one moment a leg, about one leg in two.
            var roll = State.Rng.NextDouble();
            moment = roll < .17 ? SeaMomentKind.Dolphins : roll < .32 ? SeaMomentKind.Gulls : roll < .44 ? SeaMomentKind.Crate : roll < .52 ? SeaMomentKind.Fog : SeaMomentKind.None;
            momentAt = At(.45f + (float)State.Rng.NextDouble() * .2f, out var dir);
            var side = new Vector2(-dir.y, dir.x) * (State.Rng.Next(2) == 0 ? 1 : -1);
            string actor = moment switch { SeaMomentKind.Dolphins => "Dolphin", SeaMomentKind.Gulls => "SeagullDive", SeaMomentKind.Crate => "FloatingCrate", _ => null };
            int count = moment switch { SeaMomentKind.Dolphins => 3, SeaMomentKind.Gulls => 4, SeaMomentKind.Crate => 1, _ => 0 };
            if (moment == SeaMomentKind.Gulls) momentAt += side * 4.5f;
            var prefabActor = actor != null ? lib?.M(actor) : null;
            if (actor != null && prefabActor == null) { moment = SeaMomentKind.None; return; }
            for (int i = 0; i < count; i++)
            {
                var go = ArtLibrary.Spawn(prefabActor, momentRoot, new Vector3(momentAt.x, Rod.WaterY, momentAt.y), Quaternion.identity);
                if (go != null) momentActors.Add(go.transform);
            }
        }

        void EndMoment()
        {
            foreach (var t in momentActors) if (t != null) Visuals.Kill(t.gameObject);
            momentActors.Clear(); moment = SeaMomentKind.None; momentAge = -1;
            RestoreMomentFog();
        }

        void RestoreMomentFog()
        {
            if (!fogTouched) return;
            fogTouched = false; momentFog = 0;
            RenderSettings.fog = baseFog; RenderSettings.fogDensity = baseFogDensity; RenderSettings.fogColor = baseFogColor;
        }
    }
}

using System.Collections.Generic;
using Catchline.Game.Sea;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.Game
{
    // One small dynamic mesh for route dashes, destination/ground rings and the four-second foam trail.
    public sealed class SeaSailingEffects : MonoBehaviour
    {
        struct Stamp { public Vector2 P, Forward; public float Time; }
        readonly List<Stamp> wake = new();
        readonly List<Vector3> points = new();
        readonly List<Color> colors = new();
        readonly List<int> triangles = new();
        Mesh mesh;
        Material material;
        AudioSource scrape;
        AudioClip scrapeClip;
        float clock, lastStamp = -1;
        bool shallow;
        public int WakeSamples => wake.Count;
        public void Build()
        {
            mesh = new Mesh { name = "Sea routes and foam" }; mesh.MarkDynamic();
            gameObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            material = new Material(Resources.Load<Shader>("SeaOverlay"));
            var renderer = gameObject.AddComponent<MeshRenderer>(); renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
            // A short, quiet filtered noise brush: hull grazing sand, never an impact beep.
            scrapeClip = AudioClip.Create("Soft hull scrape", 6600, 1, 22050, false);
            var samples = new float[6600]; uint seed = 31231; float smooth = 0;
            for (int i = 0; i < samples.Length; i++)
            {
                seed = seed * 1664525 + 1013904223;
                smooth = Mathf.Lerp(smooth, (seed >> 8) / 8388608f - 1, .08f);
                samples[i] = smooth * Mathf.Sin(Mathf.PI * i / samples.Length) * .3f;
            }
            scrapeClip.SetData(samples, 0); scrape = gameObject.AddComponent<AudioSource>();
            scrape.clip = scrapeClip; scrape.volume = .24f; scrape.playOnAwake = false;
        }
        public bool Draw(BoatSailor sailor, bool showRoute, float dt, bool drawGroundRings = true)
        {
            clock += Mathf.Max(0, dt);
            var forward = new Vector2(Mathf.Cos(sailor.Heading), Mathf.Sin(sailor.Heading));
            if (sailor.Speed > .3f && clock - lastStamp >= .07f)
            {
                wake.Add(new Stamp { P = sailor.Position - forward * 1.5f, Forward = forward, Time = clock }); lastStamp = clock;
            }
            wake.RemoveAll(s => clock - s.Time >= 4);
            points.Clear(); colors.Clear(); triangles.Clear();
            for (int i = 1; i < wake.Count; i++)
            {
                var a = wake[i - 1]; var b = wake[i];
                if (Vector2.Distance(a.P, b.P) > 4) continue;
                float age = (clock - a.Time) / 4;
                float width = .18f + age * .4f;
                var n = new Vector2(-a.Forward.y, a.Forward.x);
                var m = new Vector2(-b.Forward.y, b.Forward.x);
                var c = new Color(.84f, .95f, .91f, .28f * (1 - age) * (1 - age));
                var clear = new Color(c.r, c.g, c.b, 0);
                // Feather both edges; a four-second wake should dissolve into the sea.
                Quad(a.P + n * width, a.P, b.P, b.P + m * width, clear, c, c, clear);
                Quad(a.P, a.P - n * width, b.P - m * width, b.P, c, clear, clear, c);
            }
            if (drawGroundRings)
                foreach (var ground in sailor.Nav.Grounds)
                    Ring(ground.Centre, ground.Radius, .07f, new Color(.92f, .85f, .63f, .48f));
            if (showRoute && !sailor.Arrived && sailor.Route != null)
            {
                var a = sailor.Position; float spacing = 0;
                for (int i = sailor.NextWaypoint; i < sailor.Route.Count; i++)
                {
                    var b = sailor.Route[i]; var d = b - a; float length = d.magnitude; var n = new Vector2(-d.y, d.x).normalized * .075f;
                    for (float t = spacing; t < length; t += 1.4f)
                    {
                        var start = a + d.normalized * t; var end = a + d.normalized * Mathf.Min(length, t + .65f);
                        Quad(start + n, start - n, end - n, end + n, new Color(1, .92f, .72f, .92f));
                    }
                    spacing = Mathf.Repeat(spacing - length, 1.4f); a = b;
                }
                Ring(sailor.Route[sailor.Route.Count - 1], 1.1f, .13f, new Color(1, .75f, .32f, .95f));
            }
            bool nowShallow = sailor.Nav.InShallows(sailor.Position);
            if (nowShallow) Ring(sailor.Position, sailor.Nav.Radius + .5f, .15f, new Color(.69f, .94f, .85f, .5f));
            bool entered = nowShallow && !shallow;
            if (entered && Application.isPlaying) scrape.Play();
            shallow = nowShallow;
            mesh.Clear(); mesh.SetVertices(points); mesh.SetColors(colors); mesh.SetTriangles(triangles, 0); mesh.RecalculateBounds();
            return entered;
        }
        void Ring(Vector2 center, float radius, float width, Color c)
        {
            const int count = 96;
            for (int i = 0; i < count; i++)
            {
                float a = i * Mathf.PI * 2 / count, b = (i + 1) * Mathf.PI * 2 / count;
                var x = new Vector2(Mathf.Cos(a), Mathf.Sin(a)); var y = new Vector2(Mathf.Cos(b), Mathf.Sin(b));
                Quad(center + x * radius, center + x * (radius - width), center + y * (radius - width), center + y * radius, c);
            }
        }
        void Quad(Vector2 a, Vector2 b, Vector2 c, Vector2 d, Color color)
            => Quad(a, b, c, d, color, color, color, color);
        void Quad(Vector2 a, Vector2 b, Vector2 c, Vector2 d, Color ca, Color cb, Color cc, Color cd)
        {
            int start = points.Count;
            foreach (var p in new[] { a, b, c, d }) points.Add(new Vector3(p.x, -.24f, p.y));
            colors.Add(ca); colors.Add(cb); colors.Add(cc); colors.Add(cd);
            triangles.Add(start); triangles.Add(start + 1); triangles.Add(start + 2);
            triangles.Add(start); triangles.Add(start + 2); triangles.Add(start + 3);
        }
        void OnDestroy()
        {
            if (mesh != null) Prototype.Visuals.Kill(mesh);
            if (material != null) Prototype.Visuals.Kill(material);
            if (scrapeClip != null) Prototype.Visuals.Kill(scrapeClip);
        }
    }
}

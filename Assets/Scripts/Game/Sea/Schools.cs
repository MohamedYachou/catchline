using System;
using System.Collections.Generic;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game.Sea
{
    // MAP-PLAN 7.2: one moving school (hotspot) per ground. Radius 6-8 m, drifts 0.2-0.4 m/s inside the zone, jumps to a
    // new spot every 3-5 minutes or when the ground thins below 0.5. Pure data; the scene cues read from it.
    public sealed class School
    {
        public Vector2 Position, Velocity;
        public float Radius, NextJumpIn, SinceJump;
        public int Jumps;
    }

    public sealed class Schools
    {
        public const float MaxBonus = 1.3f, JumpBelow = .5f, MinJumpGap = 30f;
        public readonly SeaNav Nav;
        public readonly School[] ByGround;
        readonly System.Random rng;

        public Schools(SeaNav nav, int seed)
        {
            Nav = nav; rng = new System.Random(seed);
            ByGround = new School[nav.Grounds.Count];
            for (int i = 0; i < ByGround.Length; i++)
            {
                ByGround[i] = new School { Radius = 6f + (float)rng.NextDouble() * 2f };
                Relocate(i, false);
            }
        }

        float Roll(float a, float b) => a + (float)rng.NextDouble() * (b - a);

        // Keeps the whole school inside the zone.
        float Reach(int ground) => Mathf.Max(0f, Nav.Grounds[ground].Radius - ByGround[ground].Radius);

        void Relocate(int ground, bool count)
        {
            var school = ByGround[ground]; var zone = Nav.Grounds[ground];
            float reach = Reach(ground);
            Vector2 old = school.Position;
            for (int attempt = 0; attempt < 8; attempt++)
            {
                float angle = Roll(0f, Mathf.PI * 2f), distance = Mathf.Sqrt(Roll(0f, 1f)) * reach;
                school.Position = zone.Centre + new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)) * distance;
                if (!count || (school.Position - old).magnitude >= school.Radius * 1.5f) break;
            }
            float heading = Roll(0f, Mathf.PI * 2f);
            school.Velocity = new Vector2(Mathf.Cos(heading), Mathf.Sin(heading)) * Roll(.2f, .4f);
            school.NextJumpIn = Roll(180f, 300f); school.SinceJump = 0;
            if (count) school.Jumps++;
        }

        // groundScore(i) = the ground's richness score (0.3-1.0).
        public void Tick(float dt, Func<int, float> groundScore)
        {
            for (int i = 0; i < ByGround.Length; i++)
            {
                var s = ByGround[i]; var zone = Nav.Grounds[i];
                s.SinceJump += dt; s.NextJumpIn -= dt;
                bool thin = groundScore != null && groundScore(i) < JumpBelow && s.SinceJump >= MinJumpGap;
                if (s.NextJumpIn <= 0 || thin) { Relocate(i, true); continue; }
                s.Position += s.Velocity * dt;
                var offset = s.Position - zone.Centre; float reach = Reach(i);
                if (offset.magnitude > reach)
                {
                    var normal = offset.normalized;
                    s.Position = zone.Centre + normal * reach;
                    s.Velocity = Vector2.Reflect(s.Velocity, normal);
                    // Turn inward with a little scatter, keeping the drift speed.
                    float speed = Mathf.Clamp(s.Velocity.magnitude, .2f, .4f);
                    float turn = Roll(-.5f, .5f);
                    var inward = (-normal * Mathf.Cos(turn) + new Vector2(-normal.y, normal.x) * Mathf.Sin(turn)).normalized;
                    s.Velocity = inward * speed;
                }
            }
        }

        // Bite-rate multiplier for a boat at `boat`: 1.3 inside the school, falling linearly to 1.0 at the zone edge,
        // measured along the line from the school through the boat. Outside the zone there is no school effect.
        public float Bonus(int ground, Vector2 boat)
        {
            if (ground < 0 || ground >= ByGround.Length) return 1f;
            var s = ByGround[ground]; var zone = Nav.Grounds[ground];
            if (!zone.Contains(boat)) return 1f;
            var delta = boat - s.Position; float d = delta.magnitude;
            if (d <= s.Radius) return MaxBonus;
            var u = delta / d; var from = s.Position - zone.Centre;
            float b = Vector2.Dot(from, u), c = from.sqrMagnitude - zone.Radius * zone.Radius;
            float edge = -b + Mathf.Sqrt(Mathf.Max(0f, b * b - c));
            if (edge <= s.Radius + .001f) return 1f;
            return 1f + (MaxBonus - 1f) * Mathf.Clamp01(1f - (d - s.Radius) / (edge - s.Radius));
        }
    }

    // Scene cues, all derived from the ground richness bands: gulls over the school (3-6 rich, 1-2 thinning, none poor),
    // the ground ring tinted warm / neutral / grey, and occasional surface boils with a jumping fish at the school.
    public sealed class GroundCues
    {
        sealed class Cue
        {
            public Transform Root, Ring, Boil, Leaper;
            public MeshRenderer RingRenderer;
            public readonly List<Transform> Gulls = new();
            public int Active;
            public RichnessBand Band;
            public float Boiling = -1, NextBoil;
        }

        readonly Cue[] cues;
        readonly Schools schools;
        readonly Transform root;
        readonly float waterY;
        float clock;
        public const int MaxGulls = 6;

        public GroundCues(Transform parent, Schools schools, float waterY)
        {
            this.schools = schools; this.waterY = waterY;
            root = new GameObject("Ground cues").transform; root.SetParent(parent, false);
            cues = new Cue[schools.ByGround.Length];
            for (int i = 0; i < cues.Length; i++) cues[i] = BuildCue(i);
        }

        Cue BuildCue(int ground)
        {
            var zone = schools.Nav.Grounds[ground];
            var cue = new Cue { Root = new GameObject("Ground " + zone.Id).transform, NextBoil = 2f + ground };
            cue.Root.SetParent(root, false);
            cue.Ring = BuildRing(cue.Root, zone.Centre, zone.Radius, .45f);
            cue.RingRenderer = cue.Ring.GetComponent<MeshRenderer>();
            for (int g = 0; g < MaxGulls; g++)
            {
                var gull = new GameObject("Gull").transform; gull.SetParent(cue.Root, false);
                var model = ArtLibrary.Get()?.M("PropsV2_GullSwoop");
                if (model != null) ArtLibrary.Spawn(model, gull, Vector3.zero, Quaternion.identity, .7f);
                else
                {
                    Visuals.Box("Wing L", gull, new Vector3(-.28f, 0, 0), new Vector3(.55f, .03f, .14f), Color.white).transform.localRotation = Quaternion.Euler(0, 0, 12);
                    Visuals.Box("Wing R", gull, new Vector3(.28f, 0, 0), new Vector3(.55f, .03f, .14f), Color.white).transform.localRotation = Quaternion.Euler(0, 0, -12);
                    Visuals.Box("Body", gull, Vector3.zero, new Vector3(.14f, .09f, .32f), new Color(.93f, .93f, .9f));
                }
                gull.gameObject.SetActive(false); cue.Gulls.Add(gull);
            }
            cue.Boil = BuildRing(cue.Root, Vector2.zero, .5f, .025f);
            cue.Boil.name = "Surface ripple";
            cue.Boil.GetComponent<MeshRenderer>().sharedMaterial = Visuals.Mat(new Color(.35f, .65f, .64f));
            cue.Boil.gameObject.SetActive(false);
            cue.Leaper = Visuals.Prim(PrimitiveType.Capsule, "Jumping fish", cue.Root, Vector3.zero, new Vector3(.12f, .22f, .12f), new Color(.72f, .8f, .84f)).transform;
            cue.Leaper.gameObject.SetActive(false);
            return cue;
        }

        static Transform BuildRing(Transform parent, Vector2 centre, float radius, float width)
        {
            const int segments = 72;
            var go = new GameObject("Ground ring"); go.transform.SetParent(parent, false);
            var vertices = new Vector3[segments * 2]; var triangles = new int[segments * 6];
            for (int i = 0; i < segments; i++)
            {
                float a = i * Mathf.PI * 2 / segments;
                var dir = new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a));
                vertices[i * 2] = new Vector3(centre.x, 0, centre.y) + dir * (radius - width);
                vertices[i * 2 + 1] = new Vector3(centre.x, 0, centre.y) + dir * radius;
                int n = (i + 1) % segments, t = i * 6;
                triangles[t] = i * 2; triangles[t + 1] = n * 2; triangles[t + 2] = i * 2 + 1;
                triangles[t + 3] = i * 2 + 1; triangles[t + 4] = n * 2; triangles[t + 5] = n * 2 + 1;
            }
            var mesh = new Mesh { name = "Ground ring", vertices = vertices, triangles = triangles };
            mesh.RecalculateNormals(); mesh.RecalculateBounds();
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; renderer.receiveShadows = false;
            return go.transform;
        }

        // Data the cues are driven by, readable without a renderer.
        public int GullsShown(int ground) => ground >= 0 && ground < cues.Length ? cues[ground].Active : 0;
        public RichnessBand RingBand(int ground) => cues[ground].Band;
        public Color RingColour(int ground) => cues[ground].RingRenderer.sharedMaterial != null ? cues[ground].RingRenderer.sharedMaterial.color : Color.clear;

        public void Update(float dt, Func<int, float> groundScore)
        {
            clock += dt;
            for (int i = 0; i < cues.Length; i++)
            {
                var cue = cues[i]; var school = schools.ByGround[i]; float score = groundScore(i);
                var band = Grounds.BandOf(score);
                var tint = Grounds.RingTint(score);
                if (cue.RingRenderer.sharedMaterial == null || cue.Band != band || cue.RingRenderer.sharedMaterial.color != tint)
                    cue.RingRenderer.sharedMaterial = Visuals.Mat(tint);
                cue.Band = band;
                cue.Ring.localPosition = new Vector3(0, waterY + .06f, 0);
                cue.Active = Grounds.GullCount(score, i + school.Jumps);
                for (int g = 0; g < cue.Gulls.Count; g++)
                {
                    var gull = cue.Gulls[g]; bool on = g < cue.Active;
                    if (gull.gameObject.activeSelf != on) gull.gameObject.SetActive(on);
                    if (!on) continue;
                    float phase = clock * (.5f + .05f * g) + g * 1.9f, radius = 3f + g * .7f;
                    var centre = new Vector3(school.Position.x, waterY + 3f + (g % 3) * .6f + Mathf.Sin(clock * 2f + g) * .2f, school.Position.y);
                    var p = centre + new Vector3(Mathf.Cos(phase), 0, Mathf.Sin(phase)) * radius;
                    gull.position = p;
                    gull.rotation = Quaternion.Euler(0, -phase * Mathf.Rad2Deg, Mathf.Sin(clock * 9f + g) * 8f);
                }
                // Occasional boil with a jumping fish while the school is not poor.
                if (band != RichnessBand.Poor)
                {
                    cue.NextBoil -= dt;
                    if (cue.NextBoil <= 0 && cue.Boiling < 0)
                    {
                        cue.Boiling = 0; cue.NextBoil = (band == RichnessBand.Rich ? 3f : 8f) + (i * 1.7f % 3f);
                        var a = (clock * 7.3f + i) % (Mathf.PI * 2f);
                        cue.Boil.position = new Vector3(school.Position.x, waterY + .07f, school.Position.y) + new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a)) * school.Radius * .5f;
                    }
                }
                if (cue.Boiling >= 0)
                {
                    cue.Boiling += dt; float t = cue.Boiling / 1.2f;
                    bool alive = t < 1f && band != RichnessBand.Poor;
                    cue.Boil.gameObject.SetActive(alive);
                    cue.Leaper.gameObject.SetActive(alive && t < .5f);
                    if (alive)
                    {
                        float size = Mathf.Lerp(.4f, 2.2f, t);
                        cue.Boil.localScale = new Vector3(size, .01f, size);
                        cue.Leaper.position = cue.Boil.position + Vector3.up * (Mathf.Sin(t * 2f * Mathf.PI) * .6f);
                        cue.Leaper.rotation = Quaternion.Euler(0, 0, 90f - t * 4f * 90f);
                    }
                    else cue.Boiling = -1;
                }
            }
        }

        public void Destroy() { if (root != null) Visuals.Kill(root.gameObject); }
    }
}

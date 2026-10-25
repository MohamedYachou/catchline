using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    // World dressing from Codex's kits: quay clutter, gulls, deck props and the landmarks of each sea.
    // Every model is optional: a missing one is simply skipped, so art can land in any order.
    public partial class VoyageGame
    {
        const float WaterY = -0.32f;

        static readonly string[] ShopFronts = { "ShopFront_FishMarket", "ShopFront_HarbourMaster", "ShopFront_CrewOffice", "ShopFront_Chandlery", "ShopFront_Supplies" };

        public static float ModelHeight(GameObject prefab)
        {
            float top = 0f;
            foreach (var mf in prefab.GetComponentsInChildren<MeshFilter>())
            {
                if (mf.sharedMesh == null) continue;
                var b = mf.sharedMesh.bounds;
                var m = mf.transform.localToWorldMatrix;
                top = Mathf.Max(top, m.MultiplyPoint3x4(b.center + new Vector3(0f, b.extents.y, 0f)).y - prefab.transform.position.y);
            }
            return top;
        }

        static GameObject Put(Transform root, GameObject prefab, Vector3 p, float yaw = 0f, float scale = 1f)
            => prefab == null ? null : ArtLibrary.Spawn(prefab, root, p, Quaternion.Euler(0f, yaw, 0f), scale);

        void DressHarbour(Transform root, ArtLibrary lib, float quayTop, System.Func<float, float, float> R)
        {
            if (lib == null) return;
            float q = quayTop;

            // Behind the shops: the town on the hill and the shipyard (task 07, when it lands).
            var hill = lib.M("HillBackdrop");
            if (hill != null)
                // Two extra tiles each side so the intro's wide shots never see the backdrop end; they fade into the haze.
            {
                for (float x = -118f; x <= 122f; x += 40f) Put(root, hill, new Vector3(x, q, 13.5f), 180f);
                // Past the quay (x -42..30) the hill sits on a plain stone shore instead of floating over the water.
                foreach (var (from, to) in new[] { (-138f, -42f), (30f, 142f) })
                    Visuals.Box("ShoreBank", root, new Vector3((from + to) / 2, (q - 1f) / 2, 11f), new Vector3(to - from, q + 1f, 5f), Palette.Hex("8E8A80"));
            }
            // Along the quay.
            Put(root, lib.M("CrateStack"), new Vector3(7.0f, q, 4.5f), 180f);
            Put(root, lib.M("Lifebuoy"), new Vector3(-4.3f, q, 4.4f), 180f);
            Put(root, lib.M("LifebuoyStand"), new Vector3(10.7f, q, 3.0f), 180f);
            Put(root, lib.M("Bench"), new Vector3(3.4f, q, 4.65f), 180f);
            Put(root, lib.M("CrabPotStack"), new Vector3(11.4f, q, 4.2f), 200f);
            Put(root, lib.M("NetRack"), new Vector3(12.6f, q, 4.9f), 180f);
            Put(root, lib.M("Barrel"), new Vector3(11.1f, q, 4.8f), 10f);
            Put(root, lib.M("NPC_Sitting"), new Vector3(3.4f, q + .2235f, 4.5f), 180f);

            // Gulls on bollards, a lamp, roofs and crates.
            var gull = lib.M("Seagull");
            if (gull != null)
            {
                var perches = new[]
                {
                    (new Vector3(-4.5f, q + 0.47f, 2.6f), 200f), (new Vector3(7.5f, q + 0.47f, 2.6f), 150f),
                    (new Vector3(3.4f, q + 2.8f, 4.0f), 220f), (new Vector3(14f, q + 0.47f, 2.6f), 170f),
                    (new Vector3(19f, 1.0f, -12f), 190f), (new Vector3(7.0f, q + 0.68f, 4.5f), 230f),
                };
                foreach (var (p, yaw) in perches) Put(root, gull, p, yaw)?.AddComponent<Gull>();
            }
        }

        void DressDeck(ArtLibrary lib)
        {
            if (lib == null) return;
            // Bow is -X; port (rods) is -Z. Keep the walking tiles clear: props hug the rails and corners.
            Put(Boat, lib.M("RopeCoil"), new Vector3(-0.38f, 0.01f, 0.45f), 30f, 0.8f);
            Put(Boat, lib.M("SmallAnchor"), new Vector3(-0.42f, 0.02f, 0.95f), 90f, 0.6f);
            Put(Boat, lib.M("TackleBox"), new Vector3(2.32f, 0f, 1.32f), 90f, 0.8f);
            Put(Boat, lib.M("Lantern"), new Vector3(2.4f, 0f, 0.55f), 0f, 0.8f);
        }

        // The fishing camera looks at (1, 0, -0.7) with ortho size 3.2 at 16:9, so it sees about 11 x 6.4 screen units.
        // Sea landmarks are placed in screen units (sx right, sy up, measured on the water) so they actually show up
        // around the boat. The boat itself covers about |sx| < 2.6, |sy| < 1.6.
        static readonly Vector3 SeaCenter = new(1f, 0f, -0.7f);
        public const float ScreenYaw = 35f; // a model's +X lines up with screen-right at this yaw

        public static Vector3 AtScreen(float sx, float sy, float y = WaterY)
        {
            // Inverse of the camera's ground projection (right = (cos35, 0, -sin35), up = (sin35 cos45, ., cos35 cos45) / cos45 on the ground).
            const float c = 0.81915f, s = 0.57358f, k = 0.70711f;
            // Solve [c, -s; s*k, c*k] [dx, dz] = [sx, sy]
            float det = c * c * k + s * s * k;
            float dx = (c * k * sx + s * sy) / det;
            float dz = (-s * k * sx + c * sy) / det;
            return new Vector3(SeaCenter.x + dx, y, SeaCenter.z + dz);
        }

        void BuildSea(int kind, Transform root, ArtLibrary lib, System.Func<float, float, float> R, System.Action<Vector3, float> rock)
        {
            BuildSeaDressing(kind, root, lib, R, rock);
            ReserveFishingWater(root);
        }

        void BuildSeaDressing(int kind, Transform root, ArtLibrary lib, System.Func<float, float, float> R, System.Action<Vector3, float> rock)
        {
            string[] environments = { "GullHarbourMouth", "GullKelpBank", "GullSandbar", "GullRockyPoint", "GullDeepChannel", "GullSkerries", "GullWreckBank" };
            if (kind >= 0 && kind < environments.Length && lib?.M(environments[kind]) != null)
            {
                var environment = Put(root, lib.M(environments[kind]), new Vector3(0, WaterY, 0));
                OrientFishingCoast(environment, root);
                if (kind >= 5) DressSkerries(environment, lib); // life anchors: skerries and wreck bank
                if (kind == 2)
                {
                    // Let actual water depth make sand wet. A per-quad colour
                    // boundary otherwise creates a square staircase at the shore.
                    var drySand = Visuals.Mat(Palette.Hex("D9C393"));
                    var seabedSand = Visuals.Mat(Palette.Hex("BEA77D"));
                    foreach (var renderer in environment.GetComponentsInChildren<Renderer>())
                    {
                        if (!renderer.name.Contains("Terrain_Connected")) continue;
                        var materials = renderer.sharedMaterials;
                        for (int i = 0; i < materials.Length; i++)
                            if (materials[i] == seabedSand) materials[i] = drySand;
                        renderer.sharedMaterials = materials;
                    }
                }
                return;
            }
            GameObject M(string n) => lib?.M(n);
            GameObject At(string n, float sx, float sy, float yaw = ScreenYaw, float scale = 1f, float y = WaterY)
                => Put(root, M(n), AtScreen(sx, sy, y), yaw, scale);
            void Rocks(params (float sx, float sy, float s)[] list)
            {
                foreach (var (sx, sy, s) in list) rock(AtScreen(sx, sy), s);
            }
            void Floating(GameObject go, float amp = 0.04f) { if (go != null) go.AddComponent<Floater>().Amp = amp; }

            switch (kind)
            {
                case 0: // Harbour mouth: the breakwater behind, the lighthouse at its end, marker buoys.
                    if (M("GullHarbourMouth") != null)
                    {
                        Put(root, M("GullHarbourMouth"), new Vector3(0f, WaterY, 0f));
                        break;
                    }
                    for (float sx = -8f; sx <= 2.5f; sx += 1.15f) Rocks((sx, R(3.2f, 3.7f), R(.65f, .95f)));
                    Rocks((3.4f, 3.6f, .9f), (6.6f, 3.4f, .9f));
                    if (lib?.Lighthouse != null)
                    {
                        Put(root, lib.Lighthouse, AtScreen(6.8f, 2.6f, .15f), ScreenYaw);
                        rock(AtScreen(6.8f, 2.6f, -.44f), .95f);
                    }
                    Floating(At("MarkerBuoy_Red", -4.6f, -1.15f) ?? At("ChannelBuoy", -4.6f, -1.15f, ScreenYaw, 0.6f));
                    Floating(At("MarkerBuoy_Green", 4.9f, -1.2f));
                    break;

                case 1: // Kelp bank: floating kelp all round, a couple of big mats, one rock.
                    for (int i = 0; i < 26; i++)
                    {
                        float sx = R(-6.5f, 6.5f), sy = R(-3.3f, 3.2f);
                        if (Mathf.Abs(sx) < 3f && Mathf.Abs(sy) < 1.9f) continue;
                        if (lib?.Kelp != null) Put(root, lib.Kelp, AtScreen(sx, sy, WaterY + 0.01f), R(0f, 360f), R(1.2f, 2.4f));
                    }
                    foreach (var (sx, sy) in new[] { (-5.2f, 2.3f), (5.0f, -2.5f), (-4.8f, -2.6f), (5.4f, 2.1f) })
                        At("KelpForest", sx, sy, R(0f, 360f), 1f, WaterY + 0.012f);
                    Rocks((4.6f, 2.8f, 1.3f));
                    break;

                case 2: // Sandbar: pale banks breaking the surface, a bird rock.
                    var bank = M("SandBank_Large") ?? M("SandBank");
                    foreach (var (sx, sy, s) in new[] { (-5.8f, 2.7f, 1.0f), (1.2f, 3.3f, 0.8f), (6.0f, 2.2f, 1.0f), (-6.0f, -2.9f, 0.8f), (5.0f, -3.1f, 0.9f) })
                    {
                        if (bank != null) Put(root, bank, AtScreen(sx, sy, WaterY + 0.015f), ScreenYaw + R(-20f, 20f), s);
                        else Visuals.Prim(PrimitiveType.Sphere, "SandBank", root, AtScreen(sx, sy, -0.33f), new Vector3(4f * s, 0.12f, 2f * s), Palette.Hex("E3CF9C"));
                    }
                    if (At("BirdIsland", -3.6f, 2.8f) == null) Rocks((-3.6f, 2.8f, 0.8f));
                    Rocks((3.2f, 3.0f, 0.6f), (-6.2f, 0.4f, 0.7f));
                    break;

                case 3: // Rocky point: a cliff wall behind, rock clusters, the arch.
                    var cliff = M("CliffSegment8m");
                    for (float sx = -8f; sx <= 8f; sx += 8f)
                    {
                        if (cliff != null) Put(root, cliff, AtScreen(sx, 3.1f), ScreenYaw);
                        else Visuals.Box("Cliff", root, AtScreen(sx, 3.1f, 0.8f), new Vector3(8f, 2.4f, 2.4f), Palette.Hex("7C7A6E"))
                            .transform.localRotation = Quaternion.Euler(0f, ScreenYaw, 0f);
                    }
                    foreach (var (sx, sy, s) in new[] { (-5.6f, 2.0f, 0.8f), (5.6f, -2.7f, 0.7f), (-5.2f, -3.0f, 0.7f), (6.0f, 1.7f, 0.9f) })
                        if (At("SeaRockCluster", sx, sy, R(0f, 360f), s) == null) Rocks((sx, sy, s * 1.4f));
                    if (At("RockArch", 3.6f, 2.6f) == null) Rocks((3.6f, 2.6f, 1.6f));
                    Rocks((-2.5f, 3.2f, 0.9f), (1.0f, 3.3f, 0.8f));
                    break;

                default: // Deep channel: open water, a channel buoy, a ship crossing far off, a wreck.
                    var buoy = At("ChannelBuoy", -4.6f, -2.2f, ScreenYaw, 0.7f);
                    if (buoy == null)
                    {
                        Visuals.Prim(PrimitiveType.Cylinder, "ChannelBuoy", root, AtScreen(-4.4f, -2f, 0.1f), new Vector3(0.45f, 0.45f, 0.45f), Palette.Bad);
                        Visuals.Prim(PrimitiveType.Sphere, "BuoyTop", root, AtScreen(-4.4f, -2f, 0.65f), Vector3.one * 0.3f, Palette.Oilskin);
                    }
                    else Floating(buoy, 0.06f);
                    var ship = At("DistantShip", 3.8f, 2.9f, ScreenYaw + 90f, 0.45f);
                    if (ship == null) Visuals.Box("FarShip", root, AtScreen(3.8f, 2.9f, 0.2f), new Vector3(6f, 1.2f, 1.4f), Palette.Hex("5A6670"))
                        .transform.localRotation = Quaternion.Euler(0f, ScreenYaw, 0f);
                    else Floating(ship, 0.02f);
                    At("WreckMast", -5.3f, 2.4f, 20f);
                    var tail = At("WhaleTail", 5.0f, -2.6f, ScreenYaw - 30f);
                    if (tail != null) tail.AddComponent<WhaleTail>();
                    break;
            }
        }

        void SetWaterBiome(int kind)
        {
            if (seaMat.HasProperty("_AbsorptionColor")) { PtsWater.SetBiome(seaMat, kind); return; }
            if (!seaMat.HasProperty("_ShallowColor")) return;
            string[] shallow = { "21B9C3", "31AA9E", "62D2CB", "2AAABB", "208B9E" };
            seaMat.SetColor("_ShallowColor", Palette.Hex(kind < 0 ? "54C7BE" : shallow[Mathf.Clamp(kind, 0, 4)]));
            seaMat.SetFloat("_DepthRange", kind == 2 ? 2.7f : kind == 4 ? 5f : 3.5f);
            seaMat.SetFloat("_WaveAmplitude", kind == 4 ? .032f : .018f);
            seaMat.SetFloat("_NormalStrength", kind == 4 ? .48f : .35f);
        }

        // Editor screenshots: puts the boat at a sea (kind >= 0), the harbour (-1) or keeps the scene for a deck close-up (-2).
        public void Showcase(int kind, float zoom)
        {
            if (kind >= -1)
            {
                if (scenery != null) Visuals.Kill(scenery.gameObject);
                if (oldScenery != null) Visuals.Kill(oldScenery.gameObject);
                oldScenery = null;
                scenery = BuildScenery(kind);
                CurrentMode = kind < 0 ? Mode.Harbour : Mode.Fishing;
                seaMat.color = kind < 0 ? Palette.Sea : GameData.Spots[kind].Water;
                SetWaterBiome(kind);
            }
            else CurrentMode = Mode.Fishing;
            ZoomOffset = zoom;
            snapCamera = true;
            Visual(0f);
        }

        // Which primitive stand-ins a sea can drop because a model replaces them.
        bool HasModel(string name) => ArtLibrary.Get()?.M(name) != null;
    }
}

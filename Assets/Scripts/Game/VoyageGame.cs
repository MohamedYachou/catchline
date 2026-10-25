using System.Collections.Generic;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Catchline.Game
{
    // Build 1: tier 1-2 rowboat. Harbour -> row out -> fish with the rod -> row home -> sell.
    // Runtime stage uses the authored art library; the HUD lives in VoyageHud.cs.
    public partial class VoyageGame : MonoBehaviour
    {
        public enum Mode { Harbour, SailingOut, Fishing, SailingHome }

        public class VoyageStats { public int Landed, Spooked, Missed, Lost; }

        public GameState State { get; private set; }
        public Mode CurrentMode { get; private set; } = Mode.Harbour;
        public int SelectedSpot;
        public int ActiveSpot { get; private set; }
        public Camera Cam { get; private set; }
        public Transform Boat { get; private set; }
        public DeckGrid Grid { get; private set; }
        public readonly List<Rod> Rods = new();
        public Person Captain { get; private set; }
        public Person Hand { get; private set; }
        public readonly List<Person> ExtraPeople = new();
        IEnumerable<Person> People => new[] { Captain, Hand }.Where(p => p != null).Concat(ExtraPeople);
        public readonly List<DeckFish> OnDeck = new();
        public readonly List<CaughtFish> Cooler = new();
        public VoyageStats Stats = new();
        public float SimTime;
        public bool AutoPlay;
        // Preview builds and checks can play from scratch without touching the captain's save.
        [HideInInspector] public bool SessionOnly;
        public int Seed = 7;
        public readonly List<string> Log = new();

        Vector2Int CoolerTile => State.HullDef.Hold;
        Vector2Int CoolerAccess => State.HullDef.HoldAccess;
        Vector2Int SeatTile => State.HullDef.Seat;
        Vector2Int HandRest => State.HullDef.Rest;
        Vector2Int RestFor(Person p)
        {
            int index = p == Hand ? 0 : ExtraPeople.IndexOf(p) + (Hand != null ? 1 : 0);
            var rests = State.HullDef.CrewRest;
            if (rests != null)
            {
                if (index < 0 || index >= rests.Length)
                    throw new System.InvalidOperationException($"No crew rest {index} on {State.HullDef.Name}");
                return rests[index];
            }
            // Legacy rowboat fixtures have no card berths.
            return p == Hand ? HandRest : ExtraPeople.IndexOf(p) == 0 ? new Vector2Int(2, 1) : new Vector2Int(0, 1);
        }

        Transform world, scenery, oldScenery, coolerLid;
        TextMesh coolerLabel;
        Material seaMat;
        VoyageAudio audio;
        Color seaFrom, seaTo;
        GameObject oarPort, oarStarboard, coolerModel, iceBoxModel;
        Quaternion oarPortBase = Quaternion.identity, oarStarboardBase = Quaternion.identity;
        bool modelOars;
        Transform propeller;
        int boatVisualSignature;
        int BoatVisualSignature => (State.Has(UpgradeId.BigCooler) ? 1 : 0) | (State.RodTier == 1 ? 2 : 0) | (State.RodTier >= 2 ? 4 : 0) | (State.Has(UpgradeId.RodHolder) ? 8 : 0) | (IsPrepFisher && State.Has(UpgradeId.IceBox) ? 16 : 0) | (SecondNetActive ? 32 : 0) | (IsTier5 && State.Has(UpgradeId.ThirdDeepLine) ? 64 : 0);
        float bowSign = 1f; // +1: bow toward +X (primitive hull), -1: toward -X (model)

        // Harbour buildings you tap to open a shop.
        public readonly List<(Transform anchor, HudTab tab)> Shops = new();
        readonly List<Transform> waves = new();
        readonly List<(Transform t, float age)> splashes = new();
        float modeTimer, modeDuration, voyageStart, lidPop;
        bool built, fullWarned;
        public static readonly Color ShadowColor = new(0.03f, 0.22f, 0.27f);
        readonly List<(Transform t, float speed, float radius, float phase)> school = new();
        string toast;
        float toastUntil;

        void Awake() => Build();

        void Update()
        {
            if (!built) return;
            Tick(paused || captureFreeze ? 0f : Time.deltaTime); // the harbour keeps bobbing behind the title screen
            HandleInput();
        }

        // ---- build ------------------------------------------------------------------------

        public void Build()
        {
            if (built) return;
            built = true;
            var loaded = AutoPlay || SessionOnly ? null : GameState.Load();
            hadSave = loaded != null;
            showTitle = !AutoPlay;
            State = loaded ?? new GameState(Seed);
            BuildGrid();
            BuildWorld();
            if (Application.isPlaying && !AutoPlay)
            {
                audio = gameObject.AddComponent<VoyageAudio>();
                audio.Initialize(SessionOnly);
            }
            BuildBoat();
            Captain = new Person("Captain", true, IsNetFisher ? Vector3.zero : new Vector3(0f, 0f, -0.05f)) { Grid = Grid };
            Captain.Build(Boat, SeatTile, Palette.HullNavy, Palette.Rail);
            scenery = BuildScenery(-1);
            SetWaterBiome(-1);
            SyncCrew();
            SyncUpgrades();
            EnterHarbour(false);
        }

        void BuildWorld()
        {
            var camGo = new GameObject("Camera") { tag = "MainCamera" };
            camGo.transform.SetParent(transform, false);
            Cam = camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            var waterCamera = camGo.AddComponent<UnityEngine.Rendering.Universal.UniversalAdditionalCameraData>();
            waterCamera.requiresDepthTexture = true;
            waterCamera.requiresColorTexture = true;
            Cam.orthographic = true;
            Cam.orthographicSize = 3.2f;
            Cam.clearFlags = CameraClearFlags.SolidColor;
            Cam.backgroundColor = Palette.Sea;
            Cam.nearClipPlane = 0.1f;
            Cam.farClipPlane = 120f;
            // Same angle as the art previews (45 down, 35 yaw): every hull is placed bow toward -X, which reads as 8 o'clock on screen.
            camGo.transform.rotation = Quaternion.Euler(45f, 35f, 0f);
            camGo.transform.position = new Vector3(1.1f, 0f, -1.3f) - camGo.transform.forward * 40f;

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.transform.SetParent(transform, false);
            sun.type = LightType.Directional;
            sun.intensity = 1.3f;
            sun.color = new Color(1f, 0.96f, 0.88f);
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(55f, 195f, 0f);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.58f, 0.64f, 0.7f);

            world = new GameObject("World").transform;
            world.SetParent(transform, false);
            var waterArt = ArtLibrary.Get();
            seaMat = waterArt?.WaterShader != null ? new Material(waterArt.WaterShader) : new Material(Visuals.Mat(Palette.Sea));
            if (waterArt?.WaterTex("water-tile") != null) seaMat.SetTexture("_WaterTile", waterArt.WaterTex("water-tile"));
            seaMat.color = Palette.Sea;
            seaMat.SetTexture("_Ripples", waterArt?.WaterRipples);
            seaMat.SetTexture("_Crossing", waterArt?.WaterCrossing);
            PtsWater.Configure(seaMat, waterArt?.PtsWaterNormals, waterArt?.PtsWaterDither);
            var cameraData = Cam.GetUniversalAdditionalCameraData();
            cameraData.requiresColorTexture = cameraData.requiresDepthTexture = true;
            cameraData.renderPostProcessing = true;
            cameraData.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            var sea = CoastalWater.Build(world, seaMat);
            seaSurface = sea.transform;
            sea.GetComponent<Renderer>().sharedMaterial = seaMat;
            seaFrom = seaTo = Palette.Sea;

            var rng = new System.Random(3);
            for (int i = 0; i < (waterArt?.WaterShader != null ? 0 : 34); i++)
            {
                var w = Visuals.Box("Wave", world, Vector3.zero, new Vector3(0.5f + (float)rng.NextDouble() * 0.6f, 0.01f, 0.05f), new Color(0.85f, 0.95f, 0.97f));
                w.transform.position = new Vector3(-14f + (float)rng.NextDouble() * 30f, -0.315f, -9f + (float)rng.NextDouble() * 14f);
                waves.Add(w.transform);
            }
            for (int i = 0; i < 6; i++)
            {
                float len = 0.25f + (float)rng.NextDouble() * 0.25f;
                var f = Visuals.Prim(PrimitiveType.Sphere, "SchoolFish", world, Vector3.zero, new Vector3(len * 0.35f, 0.01f, len), ShadowColor);
                school.Add((f.transform, (rng.Next(2) == 0 ? -1f : 1f) * (0.15f + (float)rng.NextDouble() * 0.2f), 2.4f + (float)rng.NextDouble() * 2.5f, (float)rng.NextDouble() * 6.28f));
            }
        }

        void BuildBoat()
        {
            var hull = State.HullDef;
            boatVisualSignature = BoatVisualSignature;
            Boat = new GameObject(hull.Name).transform;
            Boat.SetParent(world, false);

            var lib = ArtLibrary.Get();
            if (State.Hull > 0)
            {
                var prefab = lib?.M(hull.Model);
                if (prefab != null)
                {
                    var skiff = ArtLibrary.Spawn(prefab, Boat, hull.Center, Quaternion.Euler(0f, -90f, 0f));
                    if (IsNetFisher) FitCompactFisher(skiff, prefab);
                    coolerLid = ArtLibrary.Find(skiff, "HoldLid");
                    propeller = ArtLibrary.Find(skiff, "Propeller");
                }
                else BuildPrimitiveSkiff();
                bowSign = -1f;
            }
            else if (lib != null && lib.Rowboat != null)
            {
                // Model: deck centred on its origin, bow +Z. Turned so the port gunwale (rods) faces the camera;
                // the bow then points to -X, so the boat rows toward -X.
                var rb = ArtLibrary.Spawn(lib.Rowboat, Boat, new Vector3(1f, 0f, 0.5f), Quaternion.Euler(0f, -90f, 0f));
                bowSign = -1f;
                oarPort = ArtLibrary.Find(rb, "Oar_Port")?.gameObject;
                oarStarboard = ArtLibrary.Find(rb, "Oar_Starboard")?.gameObject;
                modelOars = oarPort != null && oarStarboard != null;
                if (modelOars)
                {
                    oarPortBase = oarPort.transform.localRotation;
                    oarStarboardBase = oarStarboard.transform.localRotation;
                }
            }
            else BuildPrimitiveHull();

            var floor = new GameObject("DeckFloor");
            floor.transform.SetParent(Boat, false);
            var fc = floor.AddComponent<BoxCollider>();
            fc.center = hull.Center + Vector3.down * .02f;
            fc.size = new Vector3((hull.Width - 1) * hull.CellSize + hull.CellSize, 0.06f, (hull.Height - 1) * hull.CellSize + hull.CellSize);
            floor.AddComponent<Tappable>().Deck = true;

            // Cooler on the starboard middle tile.
            var cooler = new GameObject("Cooler");
            cooler.transform.SetParent(Boat, false);
            cooler.transform.localPosition = Grid.GetLocal(CoolerTile);
            if (State.Hull > 0)
            {
                // The skiff FBX already contains FishHold and its hinged lid.
            }
            else if (lib != null && lib.Cooler != null && lib.IceBox != null)
            {
                var plain = State.Has(UpgradeId.BigCooler) ? lib.M("BigCooler") ?? lib.Cooler : lib.Cooler;
                var iced = State.Has(UpgradeId.BigCooler) ? lib.M("BigIceBox") ?? lib.IceBox : lib.IceBox;
                coolerModel = ArtLibrary.Spawn(plain, cooler.transform, Vector3.zero, Quaternion.Euler(0f, 180f, 0f));
                iceBoxModel = ArtLibrary.Spawn(iced, cooler.transform, Vector3.zero, Quaternion.Euler(0f, 180f, 0f));
                if (lib.BaitBucket != null) ArtLibrary.Spawn(lib.BaitBucket, Boat, new Vector3(0.25f, 0f, 1.25f), Quaternion.identity);
                DressDeck(lib);
            }
            else
            {
                Visuals.Box("Body", cooler.transform, new Vector3(0f, 0.22f, 0f), new Vector3(0.8f, 0.42f, 0.55f), Palette.Rail);
                Visuals.Box("Handle", cooler.transform, new Vector3(0f, 0.3f, -0.29f), new Vector3(0.3f, 0.05f, 0.04f), Palette.Rubber);
                coolerLid = new GameObject("LidHinge").transform;
                coolerLid.SetParent(cooler.transform, false);
                coolerLid.localPosition = new Vector3(0f, 0.43f, 0.28f);
                Visuals.Box("Lid", coolerLid, new Vector3(0f, 0.04f, -0.28f), new Vector3(0.84f, 0.08f, 0.59f), Palette.Accent);
            }
            var cc = cooler.AddComponent<BoxCollider>();
            cc.center = new Vector3(0f, 0.3f, 0f);
            cc.size = new Vector3(0.9f, 0.6f, 0.7f);
            cooler.AddComponent<Tappable>().Cooler = true;
            coolerLabel = Visuals.Label("Count", cooler.transform, new Vector3(0f, 0.75f, 0f), 0.045f);
            coolerLabel.gameObject.SetActive(false); // storage is shown by the HUD, leaving the boat clear
            coolerLabel.color = Palette.Rail;

            for (int i = 0; i < hull.RodTiles.Length; i++)
            {
                if (SecondNetActive && (IsTier5 ? i >= 2 : i < 2)) continue;
                var rod = new Rod(i, hull.RodTiles[i]);
                Rods.Add(rod);
                var rodModel = State.RodTier >= 2 ? lib?.M("FishingRod_Carbon") : State.RodTier == 1 ? lib?.M("FishingRod_Fibreglass") : null;
                rod.Build(Boat, world, hull.RodBases[i], rodModel, IsNetFisher && hull.RodBases[i].z > hull.Center.z ? Vector3.forward : Vector3.back);
                if (!IsNetFisher && i > 0 && (State.Hull > 0 || State.Has(UpgradeId.RodHolder) || State.Crew.Any(c => c.Role == CrewRole.Fisherman)))
                    ArtLibrary.Spawn(lib?.M("RodHolderClamp"), Boat, hull.RodBases[i], Quaternion.identity);
            }
            BuildNetKit();
            BuildSecondNetWater();
            if (IsTier5 || ConfigurePotLine()) BuildTier5Buoys();
        }

        void BuildGrid()
        {
            var hull = State.HullDef;
            Grid = new DeckGrid(hull.Width, hull.Height, hull.CellSize);
            foreach (var tile in hull.Blocked) Grid.Block(new RectInt(tile.x, tile.y, 1, 1));
        }

        void BuildPrimitiveSkiff()
        {
            var h = State.HullDef;
            Visuals.Box("Hull", Boat, h.Center + Vector3.down * .3f, new Vector3(6.5f, .6f, 3.5f), Palette.HullNavy);
            Visuals.Box("Deck", Boat, h.Center + Vector3.down * .025f, new Vector3(5f, .05f, 3f), Palette.DeckWood);
            Visuals.Box("Console", Boat, new Vector3(4f, .32f, 2f), new Vector3(.65f, .64f, .72f), Palette.Rail);
            Visuals.Box("Motor", Boat, new Vector3(5.25f, .15f, 1f), new Vector3(.45f, .55f, .45f), Palette.HullNavy);
            coolerLid = Visuals.Box("HoldLid", Boat, new Vector3(1f, .04f, 1f), new Vector3(1f, .08f, .8f), Palette.Steel).transform;
        }

        void RebuildBoat(bool preserveBait = true)
        {
            DestroySecondNetWater();
            ClearPrepWork();
            var baited = Rods.Select(r => (ready: preserveBait && r.State == RodState.Ready, squid: r.Squid, scraps: r.Scraps, chum: r.Chum)).ToArray();
            Captain?.Stop();
            Hand?.Stop();
            foreach (var p in ExtraPeople) p.Stop();
            foreach (var rod in Rods) rod.Destroy();
            Rods.Clear();
            if (Boat != null) { Boat.gameObject.SetActive(false); Visuals.Kill(Boat.gameObject); }
            Hand = null;
            ExtraPeople.Clear();
            ResetNet();
            if (netFloats != null) Visuals.Kill(netFloats.gameObject);
            netFloats = winchCrank = null;
            Manning = null;
            AwaitingCast = false;
            coolerLid = propeller = null;
            netModelRoot = null;
            rawBuckets = rawIceCoolers = null;
            PrepWorkerTiles = System.Array.Empty<Vector2Int>();
            coolerModel = iceBoxModel = oarPort = oarStarboard = null;
            modelOars = false;
            BuildGrid();
            BuildBoat();
            for (int i = 0; i < baited.Length && i < Rods.Count; i++)
                if (baited[i].ready) { Rods[i].State = RodState.Ready; Rods[i].Squid = baited[i].squid; Rods[i].Scraps = baited[i].scraps; Rods[i].Chum = baited[i].chum; }
            Captain = new Person("Captain", true, IsNetFisher ? Vector3.zero : new Vector3(0f, 0f, -.05f)) { Grid = Grid };
            Captain.Build(Boat, SeatTile, Palette.HullNavy, Palette.Rail);
            SyncCrew();
            SyncUpgrades();
        }

        public bool RefitSkiff()
        {
            if (CurrentMode != Mode.Harbour || !State.RefitSkiff()) return false;
            RebuildBoat();
            BeginRefitFx(); audio?.Play(VoyageAudio.Cue.RefitFanfare, .35f);
            State.EnsureCards();
            Toast("Skiff refitted! A welcome chest waits in the Crew office: open it to meet Mira, your navigator.");
            SaveGame();
            return true;
        }

        public bool RefitCompact()
        {
            if (CurrentMode != Mode.Harbour || !State.RefitCompact()) return false;
            RebuildBoat(); BeginRefitFx(); audio?.Play(VoyageAudio.Cue.RefitFanfare, .35f);
            Toast("Compact fisher ready · 100 kg hold, three rods and stern net. First tank included.");
            SaveGame(); return true;
        }

        public bool RefitPrep()
        {
            if (CurrentMode != Mode.Harbour || !State.RefitPrep()) return false;
            RebuildBoat(); BeginRefitFx(); audio?.Play(VoyageAudio.Cue.RefitFanfare, .35f);
            Toast("Prep fisher ready · 160 kg hold, four crew berths and a two-person table.");
            SaveGame(); return true;
        }

        float refitUntil;

        void BuildPrimitiveHull()
        {
            // Hull with a pointed bow (cube turned 45 degrees) and a flat transom.
            Visuals.Box("Hull", Boat, new Vector3(0.9f, -0.33f, 0.5f), new Vector3(3.0f, 0.6f, 2.3f), Palette.HullNavy);
            Visuals.Box("Stripe", Boat, new Vector3(0.9f, -0.12f, 0.5f), new Vector3(3.04f, 0.07f, 2.34f), Palette.Accent);
            float bow = 2.3f / Mathf.Sqrt(2f);
            var bowGo = Visuals.Box("Bow", Boat, new Vector3(2.4f, -0.33f, 0.5f), new Vector3(bow, 0.6f, bow), Palette.HullNavy);
            bowGo.transform.localRotation = Quaternion.Euler(0f, 45f, 0f);
            var bowStripe = Visuals.Box("BowStripe", Boat, new Vector3(2.4f, -0.12f, 0.5f), new Vector3(bow + 0.03f, 0.07f, bow + 0.03f), Palette.Accent);
            bowStripe.transform.localRotation = Quaternion.Euler(0f, 45f, 0f);
            var bowDeck = Visuals.Box("BowDeck", Boat, new Vector3(2.4f, -0.02f, 0.5f), new Vector3(bow - 0.25f, 0.06f, bow - 0.25f), Palette.DeckWoodDark);
            bowDeck.transform.localRotation = Quaternion.Euler(0f, 45f, 0f);

            for (int i = 0; i < 4; i++)
                Visuals.Box("Plank", Boat, new Vector3(1f, -0.02f, -0.375f + i * 0.5f), new Vector3(3.0f, 0.06f, 0.47f), i % 2 == 0 ? Palette.DeckWood : Palette.DeckWoodDark);

            Visuals.Box("GunwalePort", Boat, new Vector3(0.95f, 0.08f, -0.6f), new Vector3(3.1f, 0.14f, 0.1f), Palette.Rail);
            Visuals.Box("GunwaleStarboard", Boat, new Vector3(0.95f, 0.08f, 1.6f), new Vector3(3.1f, 0.14f, 0.1f), Palette.Rail);
            Visuals.Box("Transom", Boat, new Vector3(-0.6f, 0.08f, 0.5f), new Vector3(0.1f, 0.14f, 2.3f), Palette.Rail);

            oarPort = new GameObject("OarPort");
            oarPort.transform.SetParent(Boat, false);
            oarPort.transform.localPosition = new Vector3(1f, 0.15f, -0.62f);
            Visuals.Box("Shaft", oarPort.transform, new Vector3(0f, 0f, -0.8f), new Vector3(0.06f, 0.06f, 1.9f), Palette.DeckWoodDark);
            Visuals.Box("Blade", oarPort.transform, new Vector3(0f, 0f, -1.8f), new Vector3(0.2f, 0.03f, 0.45f), Palette.Accent);
            oarStarboard = new GameObject("OarStarboard");
            oarStarboard.transform.SetParent(Boat, false);
            oarStarboard.transform.localPosition = new Vector3(1f, 0.15f, 1.62f);
            Visuals.Box("Shaft", oarStarboard.transform, new Vector3(0f, 0f, 0.8f), new Vector3(0.06f, 0.06f, 1.9f), Palette.DeckWoodDark);
            Visuals.Box("Blade", oarStarboard.transform, new Vector3(0f, 0f, 1.8f), new Vector3(0.2f, 0.03f, 0.45f), Palette.Accent);

        }

        // -1 = Gull Harbour quay with the shops, otherwise the fishing spot index.
        Transform BuildScenery(int kind)
        {
            var root = new GameObject(kind < 0 ? "Scenery Harbour" : $"Scenery {GameData.Spots[kind].Name}").transform;
            root.SetParent(world, false);
            var rng = new System.Random(100 + kind);
            float R(float a, float b) => a + (float)rng.NextDouble() * (b - a);
            var lib = ArtLibrary.Get();
            if (kind >= 0 && Navigation != null)
            {
                BuildNavigableSea(root, lib);
                return root;
            }
            var rockColor = Palette.Hex("6F7270");

            void Rock(Vector3 p, float s)
            {
                var rot = Quaternion.Euler(0f, R(0f, 360f), 0f);
                var models = lib != null ? new[] { lib.RockA, lib.RockB, lib.RockC } : null;
                var prefab = models?[rng.Next(3)];
                if (prefab != null) ArtLibrary.Spawn(prefab, root, new Vector3(p.x, -0.45f, p.z), rot, s * 0.9f);
                else
                {
                    var g = Visuals.Box("Rock", root, p, new Vector3(s, s * 0.7f, s * 0.9f), rockColor);
                    g.transform.localRotation = Quaternion.Euler(R(-15f, 15f), R(0f, 90f), R(-10f, 10f));
                }
            }

            if (kind < 0) { harbourSignature = State.Hull; BuildHarbour(root, lib, R); }
            else BuildSea(kind, root, lib, R, Rock);
            return root;
        }

        // ---- flow -----------------------------------------------------------------------

        public void SyncCrew()
        {
            State.SyncCardCrew();
            for (int i = 1; i < Rods.Count; i++)
                Rods[i].SetUnlocked(State.Hull > 0 || State.Has(UpgradeId.RodHolder) || State.Crew.Any(c => c.Role == CrewRole.Fisherman));
            if (Hand != null && Hand.Contract != State.Deckhand)
            {
                Visuals.Kill(Hand.Root.gameObject);
                Hand = null;
            }
            if (State.Deckhand != null && Hand == null)
            {
                var c = State.Deckhand;
                Hand = new Person(c.Name, false, IsNetFisher ? Vector3.zero : new Vector3(0.12f, 0f, 0.08f)) { Contract = c, Grid = Grid };
                Hand.Build(Boat, HandRest, c.Suit, c.Grade == Grade.Veteran ? Palette.HullNavy : Palette.Accent);
            }
            for (int i = ExtraPeople.Count - 1; i >= 0; i--)
                if (!State.ExtraCrew.Contains(ExtraPeople[i].Contract))
                {
                    var p = ExtraPeople[i];
                    p.Stop();
                    foreach (var rod in Rods) if (rod.Fisher == p) rod.Fisher = null;
                    Visuals.Kill(p.Root.gameObject);
                    ExtraPeople.RemoveAt(i);
                }
            foreach (var c in State.ExtraCrew)
                if (!ExtraPeople.Any(p => p.Contract == c))
                {
                    var p = new Person(c.Name, false, IsNetFisher ? Vector3.zero : new Vector3(.12f, 0f, .08f)) { Contract = c, Grid = Grid };
                    ExtraPeople.Add(p);
                    p.Build(Boat, RestFor(p), c.Suit, c.Grade == Grade.Veteran ? Palette.HullNavy : Palette.Accent);
                }
            ConfigureCardPeople();
        }

        public void SyncUpgrades()
        {
            if (CurrentMode == Mode.Harbour && boatVisualSignature != BoatVisualSignature) { RebuildBoat(); return; }
            for (int i = 1; i < Rods.Count; i++) Rods[i].SetUnlocked(State.Hull > 0 || State.Has(UpgradeId.RodHolder) || State.Crew.Any(c => c.Role == CrewRole.Fisherman));
            bool ice = State.Has(UpgradeId.IceBox);
            if (IsPrepFisher) SyncPrepStorage();
            if (coolerModel != null)
            {
                coolerModel.SetActive(!ice);
                iceBoxModel.SetActive(ice);
                coolerLid = ArtLibrary.Find(ice ? iceBoxModel : coolerModel, "HingedLid");
            }
            else if (State.Hull == 0 && coolerLid != null) coolerLid.GetComponentInChildren<Renderer>().sharedMaterial = Visuals.Mat(ice ? Palette.Hex("4FB3C4") : Palette.Accent);
        }

        void SetRowing(bool on)
        {
            if (State.Hull > 0) return;
            if (modelOars)
            {
                oarPort.transform.localRotation = oarPortBase;
                oarStarboard.transform.localRotation = oarStarboardBase;
            }
            else
            {
                oarPort.SetActive(on);
                oarStarboard.SetActive(on);
            }
        }

        // Saves after selling and after every harbour purchase. The bot never touches the save file.
        public void SaveGame()
        {
            if (!AutoPlay && !SessionOnly && Application.isPlaying) State.Save();
        }

        public void NewGame()
        {
            Navigation = null; Sailor = null; ActiveGroundId = null;
            travelOffset = Vector3.zero; travelYaw = travelWake = 0;
            ResetTrip(); ClearUnload(); dockBow = Vector2.zero;
            if (!SessionOnly) GameState.DeleteSave();
            ClearPrepWork();
            ClearProcessingPipeline();
            ResetManagement();
            OnDeck.Clear();
            Cooler.Clear();
            State = new GameState(System.Environment.TickCount);
            SelectedSpot = 0;
            RebuildBoat(false);
            departureReady = false;
            Stats = new VoyageStats();
            refitUntil = 0f;
            ResetFeedback();
            if (oldScenery != null) Visuals.Kill(oldScenery.gameObject);
            oldScenery = null;
            if (scenery != null) Visuals.Kill(scenery.gameObject);
            scenery = BuildScenery(-1);
            EnterHarbour(false);
            hudTab = HudTab.Market;
            Toast("New game started.");
        }

        void EnterHarbour(bool arrived)
        {
            ClearPrepWork();
            State.Chum = 0;
            CurrentMode = Mode.Harbour;
            harbourEvening = arrived; // home from a trip: the harbour at dusk
            if (arrived)
            {
                State.UnsoldCatch.Clear();
                foreach (var fish in Cooler)
                    State.UnsoldCatch.Add(new CaughtFish { Species = fish.Species, Kg = fish.Kg, ValueBonus = fish.ValueBonus,
                        StowedAt = -Mathf.Max(0f, SimTime - fish.StowedAt)});
                State.BestVoyageKg = Mathf.Max(State.BestVoyageKg, State.UnsoldCatch.Sum(f => f.Kg));
                State.UnsoldMinutes = (SimTime - voyageStart) / 60f;
                Cooler.Clear();
                if (State.UnsoldCatch.Count == 0) { State.TripDeployment.Clear(); State.EndVoyage(new SaleReport()); }
                Toast(State.UnsoldCatch.Count > 0 ? "Haul safely ashore! Tap Sell haul to collect your coins." : "Back in Gull Harbour.");
                hudTab = HudTab.Market;
                panelOpen = true;
            }
            SyncCrew();
            Manning = null;
            AwaitingCast = false;
            Captain.Rowing = false;
            Captain.Place(SeatTile);
            Captain.Face(Vector3.forward);
            Hand?.Place(HandRest);
            foreach (var p in ExtraPeople) p.Place(RestFor(p));
            foreach (var r in Rods) r.ResetForTrip();
            SetRowing(false);
            if (!State.Known(SelectedSpot)) SelectedSpot = 0;
            SaveGame();
            botHarbourAt = SimTime + 0.5f;
        }

        public bool SellHaul()
        {
            if (CurrentMode != Mode.Harbour || State.UnsoldCatch.Count == 0) return false;
            float kg = State.UnsoldCatch.Sum(f => f.Kg);
            var sale = State.Sell(State.UnsoldCatch, 0f);
            sale.Minutes = State.UnsoldMinutes;
            State.UnsoldCatch.Clear(); // Consume once, including across save/reload.
            ClearUnload();
            sale.Tokens = State.AwardHaulTokens(kg);
            if (sale.Tokens > 0) sale.Lines.Add($"Crew tokens  +{sale.Tokens}");
            if (State.GrantDailyCrate(System.DateTime.Now)) { sale.Crates++; sale.Lines.Add("First sale today: a crate"); }
            State.EndVoyage(sale);
            int earned = sale.Coins + sale.ContractCoins;
            audio?.Play(VoyageAudio.Cue.Sale);
            Toast($"Haul sold! +{earned} coins" + (sale.Tokens > 0 ? $" · +{sale.Tokens} tokens" : "") + (sale.Crates > 0 ? $" · {sale.Crates} crate{(sale.Crates > 1 ? "s" : "")}" : ""));
            Log.Add($"Voyage {State.Voyage - 1}: {sale.Caught} fish, +{earned} coins, {sale.Minutes:0.0} min");
            SyncCrew();
            SyncUpgrades();
            SaveGame();
            return true;
        }

        public string SailBlocker()
        {
            if (CurrentMode != Mode.Harbour) return "Not in the harbour";
            if (State.UnsoldCatch.Count > 0) return "Sell your haul first";
            if (State.Coins < State.DepartureWages) return $"Crew wages need {State.DepartureWages} coins";
            if (State.Hull > 0 && State.FuelFraction <= .1f) return "Buy fuel at Supplies";
            return null;
        }

        public void SetSail()
        {
            if (SailBlocker() != null || !State.PayDepartureWages()) return;
            Abilities = new CrewAbilityEngine(State);
            harbourEvening = false; // a new day
            SyncUpgrades();
            ActiveSpot = SelectedSpot;
            departureReady = false;
            voyageStart = SimTime;
            ResetManagement();
            Stats = new VoyageStats();
            ResetFeedback();
            fullWarned = false;
            BeginTransition(Mode.SailingOut, ActiveSpot);
        }

        public void HeadHome()
        {
            if (CurrentMode != Mode.Fishing) return;
            flowReturning = true;
            ManagementOpen = false;
            ClearPrepWork();
            ClearProcessingPipeline(true);
            ClearNetUnload();
            netOrdersOpen = false;
            PrepOrdersOpen = false;
            toastUntil = 0; // a deck instruction (keep/throw, sort) must not ride home over the header (polish sweep PS-09)
            // Grab what's on deck if there's room; the rest goes back in the sea.
            foreach (var p in People)
            {
                if (p == null) continue;
                p.Stop();
                if (p.Carrying != null)
                {
                    TryStore(new CaughtFish { Species = p.Carrying.Species, Kg = p.Carrying.Kg, StowedAt = p.Carrying.CaughtAt });
                    Visuals.Kill(p.Carrying.Root.gameObject);
                    p.Carrying = null;
                }
            }
            ResetDeepLines(false);
            ResetNet();
            ResetSecondNet();
            foreach (var f in OnDeck)
            {
                TryStore(new CaughtFish { Species = f.Species, Kg = f.Kg, StowedAt = f.CaughtAt });
                Visuals.Kill(f.Root.gameObject);
            }
            OnDeck.Clear();
            if (Navigation == null) FlushDeckGraph();
            Manning = null;
            AwaitingCast = false;
            foreach (var r in Rods) r.ResetForTrip();
            BeginTransition(Mode.SailingHome, -1);
            flowReturning = false;
        }

        void BeginTransition(Mode mode, int sceneryKind)
        {
            // The three-leg trip (VoyageTrip.cs): harbour lane, chart, sea lane. Maps without a chart keep the old row.
            if (mode == Mode.SailingOut && BeginTrip()) return;
            if (Navigation != null)
            {
                BeginSeaRoute(mode);
                return;
            }
            CurrentMode = mode;
            modeTimer = 0f;
            modeDuration = sceneryKind < 0 ? GameData.Spots[ActiveSpot].RowSeconds : GameData.Spots[sceneryKind].RowSeconds;
            modeDuration *= State.HullDef.TravelMultiplier;
            if (oldScenery != null) Visuals.Kill(oldScenery.gameObject);
            oldScenery = scenery;
            scenery = BuildScenery(sceneryKind);
            scenery.localPosition = new Vector3(.573576f, 0, .819152f) * 30f;
            seaFrom = seaMat.color;
            seaTo = sceneryKind < 0 ? Palette.Sea : GameData.Spots[sceneryKind].Water;
            Captain.Stop();
            Captain.Place(SeatTile);
            Captain.Face(new Vector3(-bowSign, 0f, 0f)); // rowers face the stern
            Captain.Rowing = State.Hull == 0;
            Hand?.Stop();
            Hand?.Place(HandRest);
            foreach (var p in ExtraPeople) { p.Stop(); p.Place(RestFor(p)); }
            SetRowing(true);
            audio?.Play(VoyageAudio.Cue.Moor, .55f);
            UpdateTravel();
        }

        void FinishTransition()
        {
            if (oldScenery != null) Visuals.Kill(oldScenery.gameObject);
            oldScenery = null;
            scenery.localPosition = Vector3.zero;
            travelOffset = Vector3.zero;
            travelYaw = travelWake = 0f;
            seaMat.color = seaTo;
            SetWaterBiome(CurrentMode == Mode.SailingHome ? -1 : ActiveSpot);
            Captain.Rowing = false;
            SetRowing(false);
            if (CurrentMode == Mode.SailingOut)
            {
                CurrentMode = Mode.Fishing;
                SetupDeckGraph();
                Toast($"Arrived at {GameData.Spots[ActiveSpot].Name}.");
            }
            else { EnterHarbour(true); audio?.Play(VoyageAudio.Cue.Moor, .7f); }
        }

        // ---- simulation -------------------------------------------------------------------

        int CrewCount => State.CrewCount + 1;

        public void Tick(float dt)
        {
            if (!built) return;
            float total = dt;
            while (dt > 0f)
            {
                float step = Mathf.Min(dt, 0.05f);
                dt -= step;
                Step(step);
            }
            Visual(total);
        }

        void Step(float dt)
        {
            TickAbilities(dt);
            TickChart(dt);
            TickSeaMoments(dt);
            TickManagement(dt);
            TickGrounds(dt);
            SimTime += dt;
            var camRot = Cam.transform.rotation;
            switch (CurrentMode)
            {
                case Mode.Harbour:
                    SyncHarbourScenery();
                    if (AutoPlay && SimTime >= botHarbourAt) BotHarbour();
                    break;

                case Mode.SailingOut:
                case Mode.SailingHome:
                    BurnFuel(dt);
                    if (Leg is TripLeg.HarbourOut or TripLeg.ChartOut or TripLeg.ChartHome or TripLeg.HarbourIn) TickTrip(dt);
                    else if (Navigation != null) TickSeaTravel(dt);
                    else
                    {
                        modeTimer += dt * AbilityTravel * (State.Hull > 0 ? 1f : WorkSpeed.Rate(Captain));
                        UpdateTravel();
                    }
                    float stroke = Mathf.Sin(SimTime * 3.2f);
                    if (oarPort != null) oarPort.transform.localRotation = oarPortBase * Quaternion.Euler(stroke * 8f, stroke * 25f, 0f);
                    if (oarStarboard != null) oarStarboard.transform.localRotation = oarStarboardBase * Quaternion.Euler(-stroke * 8f, -stroke * 25f, 0f);
                    if (propeller != null) propeller.Rotate(IsNetFisher ? Vector3.up : Vector3.forward, 1000f * dt, Space.Self);
                    if (Navigation == null && Leg == TripLeg.None && CurrentMode != Mode.Harbour && modeTimer >= modeDuration) FinishTransition();
                    break;

                case Mode.Fishing:
                    BurnFuel(dt);
                    if (CurrentMode != Mode.Fishing) break;
                    if (!AtFishingGround) { TickDeckGraph(); TickDeckFish(dt); break; }
                    foreach (var r in Rods)
                        if (r.Unlocked) r.Tick(this, dt, Attending(r) || FisherAt(r));
                    ManRod();
                    PreemptNetFallback();
                    TickDeckGraph(); // migrated hulls: the scheduler hauls and sorts; legacy hand AI only baits and idles
                    if (Hand != null && (Hand.Idle || Hand.Loitering)) HandThink(Hand);
                    foreach (var employee in ExtraPeople)
                        if (employee.Contract.Role == CrewRole.Fisherman) FisherThink(employee);
                        else if (employee.Idle || employee.Loitering) HandThink(employee);
                    TickTier5(dt);
                    TickNet(dt);
                    TickSecondNet(dt);
                    TickNetUnload(dt);
                    if (AutoPlay) BotFish();
                    TickDeckFish(dt);
                    if (!fullWarned && HoldFull)
                    {
                        fullWarned = true;
                        Toast("The cooler is full. Head home to sell.");
                    }
                    break;
            }
            Captain.Pose = Manning?.State switch { RodState.Flying => "Cast", RodState.Waiting or RodState.Bite => "Wait", RodState.Reeling => "Reel", _ => "Idle" };
            Captain.Tick(dt, camRot);
            Hand?.Tick(dt, camRot);
            foreach (var p in ExtraPeople) p.Tick(dt, camRot);
        }

        void BurnFuel(float dt)
        {
            if (State.Hull == 0) return;
            State.Fuel = Mathf.Max(0, State.Fuel - dt * (Abilities?.Fuel ?? 1) / 60f);
            if (CurrentMode == Mode.Fishing && State.FuelFraction <= .1f)
            {
                confirmHeadHome = false;
                HeadHome();
                Toast("Fuel reserve reached · returning to Gull Harbour.");
            }
        }

        void TickDeckFish(float dt)
        {
            for (int i = OnDeck.Count - 1; i >= 0; i--)
            {
                var f = OnDeck[i];
                f.Age += dt;
                if (f.FromNetBasket && f.Root.parent != Boat) continue;
                if (f.FromNetBasket && f.Age >= .4f)
                {
                    f.Root.localPosition = f.RestPos;
                    f.Root.localRotation = Quaternion.identity;
                    continue;
                }
                if (f.Age < 0.4f)
                {
                    // Tossed from the rod tip onto the deck.
                    float a = f.Age / 0.4f;
                    f.Root.localPosition = Vector3.Lerp(f.SpawnFrom, f.RestPos, a) + Vector3.up * Mathf.Sin(a * Mathf.PI) * 0.5f;
                    f.Root.localRotation = Quaternion.Euler(a * 360f, 0f, 0f);
                    continue;
                }
                if (f.Tail != null) f.Tail.localRotation = Quaternion.Euler(0f, Mathf.Sin(f.Age * 14f) * 35f, 0f);
                float flop = Mathf.Max(0f, Mathf.Sin(f.Age * 7f + i)) * 0.1f;
                f.Root.localPosition = f.RestPos + Vector3.up * flop;
                f.Root.localRotation = Quaternion.Euler(0f, f.Age * 40f % 360f, Mathf.Sin(f.Age * 9f) * 25f);
                if (f.DeepLineRig < 0 && f.ClaimedBy == null && f.Age > GameData.DeckFishLifetime)
                {
                    Visuals.Kill(f.Root.gameObject);
                    OnDeck.RemoveAt(i);
                    Stats.Lost++;
                    Flow.Lose(f.Kg);
                    if (!f.CaughtByCrew) Toast("A fish flopped back overboard.");
                }
            }
        }

        Vector3 camCenter = new(1.0f, 0f, -0.7f);
        public float ZoomOffset;
        bool snapCamera = true;

        void Visual(float frameDt)
        {
            bool inTransit = CurrentMode is Mode.SailingOut or Mode.SailingHome;
            if (CurrentMode == Mode.Harbour && Leg == TripLeg.None) PlaceAtBerth();
            TickUnload();
            audio?.Mix(MenuOpen || captureFreeze || !Application.isFocused, CurrentMode == Mode.Harbour, inTransit && State.Hull == 0 && travelWake > .1f, ActiveSpot == 5, AtFishingGround ? ActiveSpot : -1, harbourEvening);
            PtsWater.HullPose(world.TransformPoint(travelOffset + State.HullDef.Center), travelYaw, State.Hull > 0,
                SimTime, out float heave, out Quaternion tilt);
            Boat.localRotation = Quaternion.Euler(0, travelYaw, 0) * tilt * SeaBankRotation(frameDt);
            // Rotate about the hull centre, rather than the corner of the deck grid.
            var pivotCorrection = State.HullDef.Center - Boat.localRotation * State.HullDef.Center;
            Boat.localPosition = travelOffset + pivotCorrection + Vector3.up * heave
                + (IsPrepFisher && Navigation == null && CurrentMode == Mode.Fishing ? Vector3.back * .65f : Vector3.zero);
            if (seaMat.HasProperty("_Clock"))
            {
                seaMat.SetFloat("_Clock", PtsWater.Clock(SimTime));
                seaMat.SetVector("_BoatCenter", Boat.TransformPoint(State.HullDef.Center));
                seaMat.SetVector("_BoatShape", new Vector4(IsPrepFisher ? 3.85f : State.Hull > 0 ? 3.25f : 2.1f, IsPrepFisher ? 2f : State.Hull > 0 ? 1.75f : 1.2f,
                    inTransit ? travelWake : 0f, travelYaw * Mathf.Deg2Rad));
            }
            // Camera: wide on the harbour (shifted left of the shop panel), close on the water.
            bool harbour = CurrentMode == Mode.Harbour;
            float harbourBlend = harbour ? 1f : CurrentMode == Mode.SailingOut ? 1f - Segment(TravelProgress, .18f, .65f)
                : CurrentMode == Mode.SailingHome ? Segment(TravelProgress, .55f, 1f) : 0f;
            if (Navigation != null || Leg != TripLeg.None) harbourBlend = 0;
            var framing = HarbourFraming();
            var center = Vector3.Lerp(Boat.TransformPoint(State.HullDef.Center) + new Vector3(.35f, 0f, -.30f), framing.focus, harbourBlend);
            center = SeaCameraTarget(center, frameDt);
            if (Navigation != null)
            {
                center.x = Mathf.Clamp(center.x, Navigation.CameraBounds.xMin, Navigation.CameraBounds.xMax);
                center.z = Mathf.Clamp(center.z, Navigation.CameraBounds.yMin, Navigation.CameraBounds.yMax);
                if (seaSurface != null) seaSurface.position = new Vector3(center.x, seaSurface.position.y, center.z);
            }
            else if (seaSurface != null && HarbourLaneActive) seaSurface.position = new Vector3(center.x, seaSurface.position.y, center.z);
            else if (seaSurface != null) seaSurface.localPosition = new Vector3(0, seaSurface.localPosition.y, 0);
            if (harbour && panelOpen) center += Cam.transform.right * 3.7f;
            float k = snapCamera ? 1f : 1f - Mathf.Exp(-frameDt * 3f);
            snapCamera = false;
            camCenter = Vector3.Lerp(camCenter, center, k);
            Cam.orthographicSize = Mathf.Lerp(Cam.orthographicSize, SeaCameraSize(HarbourLaneActive ? framing.size : Mathf.Lerp(IsTier5 ? 6.15f : IsPrepFisher ? 5.35f : State.Hull > 0 ? 4.8f : 3.2f, framing.size, harbourBlend)) + ZoomOffset + TripCameraLift, k);
            Cam.transform.position = camCenter - Cam.transform.forward * SeaCameraDistance();
            ApplyIntroCamera(frameDt);
            UpdateNavigableSeaVisual(frameDt);
            UpdateRodView(frameDt);
            UpdateCageView(frameDt);
            UpdateGutView(frameDt);
            UpdateRepairView(frameDt);
            UpdateHarbourTraffic(frameDt);
            UpdateHarbourDusk(frameDt);
            UpdateNetView(frameDt);
            RefreshInterface();

            float waveSpeed = CurrentMode is Mode.SailingOut or Mode.SailingHome ? 3.5f : 0.25f;
            foreach (var w in waves)
            {
                var p = w.position;
                p.x -= waveSpeed * frameDt * bowSign;
                if (p.x > 15f) p.x -= 30f;
                if (p.x < -15f) p.x += 30f;
                w.position = p;
            }
            for (int i = splashes.Count - 1; i >= 0; i--)
            {
                var (t, age) = splashes[i];
                age += frameDt;
                float s = 0.2f + age * 1.6f;
                t.localScale = new Vector3(s, 0.005f, s);
                if (age > 0.45f)
                {
                    Visuals.Kill(t.gameObject);
                    splashes.RemoveAt(i);
                }
                else splashes[i] = (t, age);
            }
            // Fish swimming around the boat; they keep their distance while sailing.
            bool sailing = CurrentMode is Mode.SailingOut or Mode.SailingHome;
            for (int i = 0; i < school.Count; i++)
            {
                var (t, speed, radius, phase) = school[i];
                t.gameObject.SetActive(!sailing && CurrentMode != Mode.Harbour);
                float ang = phase + SimTime * speed;
                var c = new Vector3(1f, 0f, 0.5f);
                var pos = c + new Vector3(Mathf.Cos(ang) * radius * 1.4f, 0f, Mathf.Sin(ang) * radius);
                var next = c + new Vector3(Mathf.Cos(ang + 0.05f * Mathf.Sign(speed)) * radius * 1.4f, 0f, Mathf.Sin(ang + 0.05f * Mathf.Sign(speed)) * radius);
                t.position = new Vector3(pos.x, WaterY - .60f, pos.z);
                t.rotation = Quaternion.LookRotation(next - pos);
            }

            lidPop = Mathf.Max(0f, lidPop - frameDt * 3f);
            if (coolerLid != null) coolerLid.localRotation = IsNetFisher ? compactLidRest * Quaternion.Euler(lidPop * 90f, 0f, 0f) : Quaternion.Euler(-lidPop * 70f, 0f, 0f);
            coolerLabel.text = $"{HoldKg:0.00}/{State.CoolerCapacity:0.#} kg";
            coolerLabel.color = HoldFull ? Palette.Oilskin : Palette.Rail;
            coolerLabel.transform.rotation = Cam.transform.rotation;
        }

        public void Splash(Vector3 pos, float size, bool sound = true)
        {
            if (sound) audio?.Play(VoyageAudio.Cue.Splash, .38f);
            if (seaMat.HasProperty("_Impact")) seaMat.SetVector("_Impact", new Vector4(pos.x, pos.z, SimTime, Mathf.Clamp01(size * 2f)));
            var s = Visuals.Prim(PrimitiveType.Cylinder, "Splash", world, pos + Vector3.up * 0.01f, new Vector3(size, 0.005f, size), new Color(0.92f, 0.97f, 1f));
            splashes.Add((s.transform, 0f));
        }

        public void Toast(string msg)
        {
            if (string.IsNullOrEmpty(msg)) return;
            toast = msg;
            toastUntil = SimTime + 3.2f;
        }

        // ---- deck actions (one tap each) -------------------------------------------------------
        //
        // Tap a rod's bubble: the captain walks there, baits if needed and casts by himself.
        // While he mans that rod the strike minigame is on screen; one tap strikes.
        // The fish lands next to him. Solo you tap its bubble to carry it to the cooler;
        // with a deckhand they fetch it and the rod's bubble comes back for the next cast.

        public Rod Manning { get; private set; }
        public bool AwaitingCast { get; private set; }
        public bool HasDeckhand => State.Crew.Any(c => c.Role == CrewRole.Deckhand);

        public bool ThrowAgain()
        {
            if (!AwaitingCast || Manning == null || CurrentMode != Mode.Fishing || HoldFull) return false;
            AwaitingCast = false;
            return true;
        }

        public void LeaveFishing()
        {
            // Only leave the between-casts panel; an active cast must resolve first.
            if (!AwaitingCast) return;
            AwaitingCast = false;
            Manning = null;
        }

        public bool Attending(Rod r) => !Captain.Walking && Captain.Tile == r.Tile;

        // The rod whose strike minigame is on screen, if any.
        public Rod MinigameRod => Manning != null && Attending(Manning) && Manning.State is RodState.Flying or RodState.Waiting or RodState.Bite or RodState.Reeling ? Manning : null;

        public bool CanCommandRod(Rod r) =>
            CurrentMode == Mode.Fishing && AtFishingGround && r.Unlocked && Manning != r
            && r.Fisher == null
            && (r.State is RodState.Waiting or RodState.Bite || !HoldFull && (r.State == RodState.Ready || r.State == RodState.Unbaited && (State.HasAnyBait || r.BaitingBy != null)));

        public bool CanCarry(DeckFish f) => CurrentMode == Mode.Fishing && f.ClaimedBy == null && f.Age > 0.4f
            && (!IsNetFisher || Captain.Idle && (Manning == null || Manning.State is not (RodState.Reeling or RodState.Flying)));

        public void CommandRod(Rod r)
        {
            if (!CanCommandRod(r)) return;
            if (Captain.Carrying != null) { Toast("Stow your fish first."); return; }
            Manning = r;
            AwaitingCast = false;
            if (!Attending(r)) Captain.WalkTo(Grid, r.Tile, () => Captain.Face(r.Outward));
        }

        public void CommandCarry(DeckFish f)
        {
            if (!CanCarry(f)) return;
            if (Captain.Carrying != null) { Toast("Your hands are full."); return; }
            Manning = null;
            AwaitingCast = false;
            if (f.FromNetBasket) BeginNetUnload(Captain);
            else Fetch(Captain, f);
        }

        // One tap during the minigame strikes. Too early on a nibble or too late both cost the bait.
        public void StrikeTap()
        {
            var r = MinigameRod;
            if (r != null && !r.ReadingResult.HasValue && r.State is RodState.Waiting or RodState.Bite)
            {
                Captain.PlayOnce("Strike");
                if (r.State == RodState.Bite) audio?.Play(VoyageAudio.Cue.Reel, .6f);
                string message = r.Strike(this);
                if (message != null) Toast(message);
            }
        }

        // The captain runs the rod he was sent to: bait, then cast.
        void ManRod()
        {
            var r = Manning;
            if (r == null || !Captain.Idle || Captain.Carrying != null || !Attending(r)) return;
            if (RodViewActive) return;
            Captain.Face(r.Outward);
            if (AwaitingCast) return;
            switch (r.State)
            {
                case RodState.Unbaited:
                    if (HoldFull || r.BaitingBy != null) return; // the deckhand is on it
                    Bait(Captain, r);
                    break;
                case RodState.Ready:
                    if (HoldFull) return;
                    Captain.Face(r.Outward);
                    Captain.Do("Casting", GameData.CastTime, () => { if (HoldFull) return; r.Cast(this, 0.35f + (float)State.Rng.NextDouble() * 0.4f); audio?.Play(VoyageAudio.Cue.Cast); });
                    break;
            }
        }

        public void LandFish(Rod rod, Species s, float kg)
        {
            int count = Abilities?.RodLanded(AbilityOwner(rod.Fisher), s) ?? 1;
            for (int i = 1; i < count; i++) EmitRodFish(rod, s, kg);
            EmitRodFish(rod, s, kg);
        }
        void EmitRodFish(Rod rod, Species s, float kg)
        {
            AbilityCatch(ActiveSpot, kg, s, false);
            Stats.Landed++;
            if (UsesDeckGraph && GearStation(Deck.StationKind.Rod, rod.Index) is { } rodStation)
            {
                LandOnDeck(rodStation, s, kg);
                RecordLanding(FlowTelemetry.Kind.Rod, s, kg);
                if (rod == Manning) { Manning = null; Captain.PlayOnce("Cheer"); }
                if (rod.Fisher == null) { ShowCatch(s, kg); audio?.Play(VoyageAudio.Cue.Land, .6f); }
                return;
            }
            var f = new DeckFish { Species = s, Kg = kg, Tile = rod.Tile, CaughtAt = SimTime, CaughtByCrew = rod.Fisher != null };
            f.Root = DeckFish.BuildModel(s, kg, Boat);
            int n = OnDeck.Count(o => o.Tile == rod.Tile);
            f.RestPos = Grid.GetLocal(rod.Tile) + (IsNetFisher ? new Vector3(-.12f + n * .08f, .07f, .08f) : new Vector3(-0.22f + n * 0.18f, 0.07f, 0.3f));
            f.SpawnFrom = rod.TipLocal;
            foreach (var t in f.Root.GetComponentsInChildren<Transform>())
                if (t.name.EndsWith("Tail")) f.Tail = t;
            f.Root.localPosition = f.SpawnFrom;
            OnDeck.Add(f);
            RecordLanding(FlowTelemetry.Kind.Rod, s, kg);
            if (rod == Manning)
            {
                if (HasDeckhand) AwaitingCast = true;
                else Manning = null;
                Captain.PlayOnce("Cheer");
            }
            if (rod.Fisher == null) { ShowCatch(s, kg); audio?.Play(VoyageAudio.Cue.Land, .6f); }
        }

        void Fetch(Person p, DeckFish f)
        {
            f.ClaimedBy = p;
            void Release() { if (f.ClaimedBy == p) f.ClaimedBy = null; }
            if (!p.WalkTo(Grid, f.Tile, () =>
            {
                p.FacePoint(f.RestPos);
                p.Do("Picking up", GameData.PickupTime, () => PickUp(p, f), Release);
            }, Release)) Release();
        }

        void PickUp(Person p, DeckFish f)
        {
            if (!OnDeck.Contains(f)) return;
            OnDeck.Remove(f);
            f.Root.SetParent(p.Root, false);
            p.Carrying = f;
            if (p == Captain) Stow(p);
        }

        void Stow(Person p)
        {
            // Actors may overlap for playability. Fish claims/capacity remain atomic;
            // one actor's stow animation never locks out another delivery.
            p.WalkTo(Grid, InboundAccess, () =>
            {
                if (IsPrepFisher) p.FacePoint(PrepSurfaceLocal); else FaceHold(p);
                p.Do("Stowing", GameData.StowTime, () => TryStow(p));
            });
        }

        bool TryStow(Person p)
        {
            if (p.Carrying == null) return false;
            if (HoldFull)
            {
                if (p == Captain) Toast("The cooler is full! Head home to sell.");
                return false;
            }
            var secured = new CaughtFish { Species = p.Carrying.Species, Kg = p.Carrying.Kg, StowedAt = p.Carrying.CaughtAt };
            if (!DeliverCatch(secured)) return false;
            if (p.Carrying.FromNetBasket) RecordStoredNet(new[] { secured });
            bool captainCatch = !p.Carrying.CaughtByCrew;
            Visuals.Kill(p.Carrying.Root.gameObject);
            p.Carrying = null;
            lidPop = 1f;
            if (captainCatch) { stowedAt = SimTime; audio?.Play(VoyageAudio.Cue.Stow, .55f); }
            return true;
        }

        void Bait(Person p, Rod rod)
        {
            if (!CanBaitRod(rod)) return;
            p.Face(rod.Outward);
            rod.BaitingBy = p;
            p.Do("Baiting", GameData.BaitTime, () =>
            {
                rod.BaitingBy = null;
                if (rod.State == RodState.Unbaited && State.TakeBait(BaitOwner(rod), out bool squid, out bool chum, out bool scraps))
                {
                    rod.Scraps = scraps;
                    rod.Squid = squid;
                    rod.Chum = chum;
                    rod.State = RodState.Ready;
                }
            }, () => rod.BaitingBy = null);
        }

        // Deck work is owned by the shared scheduler on every hull.
        void HandThink(Person h) { IdlePatrol(h); }

        bool FisherAt(Rod rod) => rod.Fisher != null && !rod.Fisher.Walking && rod.Fisher.Tile == rod.Tile;

        void FisherThink(Person fisher)
        {
            if (FisherSpecialThink(fisher)) return;
            var rod = Rods.FirstOrDefault(r => r.Fisher == fisher);
            if (rod == null)
            {
                rod = Rods.LastOrDefault(r => r.Unlocked && r != Manning && r.Fisher == null);
                if (rod == null) return;
                rod.Fisher = fisher;
            }
            fisher.Pose = rod.State switch { RodState.Flying => "Cast", RodState.Waiting or RodState.Bite => "Wait", RodState.Reeling => "Reel", _ => "Idle" };
            if (!fisher.Idle) return;
            if (!FisherAt(rod)) { fisher.WalkTo(Grid, rod.Tile, () => fisher.Face(rod.Outward)); return; }
            // Special Tier5 jobs are dispatched before claiming a rod, using saved policy.
            fisher.Face(rod.Outward);
            if (rod.State == RodState.Unbaited && !HoldFull && rod.BaitingBy == null && CanBaitRod(rod)) Bait(fisher, rod);
            else if (rod.State == RodState.Ready && !HoldFull)
                fisher.Do("Casting", GameData.CastTime, () => { if (!HoldFull) rod.Cast(this, .55f); });
            else if (rod.State == RodState.Bite && !rod.FisherAttempted)
            {
                rod.FisherAttempted = true;
                if (IsTier5 || State.Rng.NextDouble() < CardStrikeChance(fisher.Contract))
                {
                    fisher.PlayOnce("Strike");
                    rod.Strike(this);
                }
            }
        }

        // ---- events from the rods (the bot listens here too) --------------------------------

        Rod botStrikeRod;
        float botStrikeAt, botHarbourAt;

        public void OnNibble(Rod r)
        {
            if (AutoPlay && r == MinigameRod && State.Rng.NextDouble() < 0.05) StrikeTap();
        }

        public void OnBite(Rod r)
        {
            if (r == MinigameRod && r.Fisher == null) audio?.Play(VoyageAudio.Cue.Bite, .7f);
            if (!AutoPlay || r != MinigameRod) return;
            botStrikeRod = r;
            botStrikeAt = SimTime + (State.Rng.NextDouble() < 0.12 ? 1.0f : 0.25f + (float)State.Rng.NextDouble() * 0.5f);
        }

        // ---- autoplay (headless balance checks): only uses the same taps a player has --------

        void BotFish()
        {
            if (HoldFull) { HeadHome(); return; }
            if (State.Hull > 0 && Captain.Idle && Captain.Carrying == null && MinigameRod == null && Manning == null)
            {
                if (Net == NetState.Ready) { HaulNet(); return; }
                if (Net == NetState.Stowed && HoldKg + OnDeck.Sum(f => f.Kg) < State.CoolerCapacity) { SetNet(); return; }
            }
            if (botStrikeRod != null && SimTime >= botStrikeAt)
            {
                if (botStrikeRod == MinigameRod) StrikeTap();
                botStrikeRod = null;
            }
            if (AwaitingCast) ThrowAgain();
            var c = Captain;
            if (!c.Idle || c.Carrying != null || MinigameRod != null) return;

            bool handBusy = Hand != null && (Hand.Carrying != null || !Hand.Idle && Hand.BusyLabel == "Picking up");
            bool full = HoldFull;
            bool noBait = !State.HasAnyBait && Rods.All(r => !r.Unlocked || r.State == RodState.Unbaited);
            if (full || State.Hull == 0 && noBait && OnDeck.Count == 0 && !handBusy && Rods.All(r => r.State is not RodState.Reeling))
            {
                HeadHome();
                return;
            }
            var f = OnDeck.FirstOrDefault(CanCarry);
            if (f != null) { CommandCarry(f); return; }
            if (Manning != null || Hand == null && OnDeck.Any(x => x.ClaimedBy == null)) return;
            var rod = Rods.Where(CanCommandRod).OrderByDescending(r => r.State == RodState.Ready).FirstOrDefault();
            if (rod != null) CommandRod(rod);
        }

        void BotHarbour()
        {
            botHarbourAt = float.MaxValue;
            SellHaul();
            while (State.Active.Count < GameData.MaxActiveContracts && State.Offers.Count > 0) State.TakeContract(State.Offers[0]);
            // Buy in a fixed order, saving up for the next item (negative numbers are sea charts).
            foreach (int step in new[] { (int)UpgradeId.RodHolder, -2, (int)UpgradeId.IceBox, -3, (int)UpgradeId.BigCooler, (int)UpgradeId.LunchTin, -4 })
            {
                if (step < 0)
                {
                    int spot = -step;
                    if (State.Known(spot)) continue;
                    if (State.Coins < GameData.Spots[spot].ChartCost + 30) break;
                    State.BuyChart(spot);
                    continue;
                }
                var id = (UpgradeId)step;
                if (State.Has(id)) continue;
                if (State.Coins < State.UpgradeCost(id) + 30) break;
                State.TryBuy(id);
            }
            if (State.Coins > 150 && State.Squid < 5) State.BuySquid();
            if (State.CanRefit && State.Coins >= GameData.SkiffCost + 100) RefitSkiff();
            SyncUpgrades();
            State.EnsureCards();
            foreach (var c in State.Roster.Where(c => c.Def.Role != CardRole.Navigator))
                if (State.Coins > State.DepartureWages + c.Wage() + 100) State.DeployCard(c.Id,true);
            SyncCrew();
            while (State.Bait < (State.Hull > 0 ? 60 : State.Has(UpgradeId.RodHolder) ? 40 : 25) && State.BuyBait()) { }
            if (State.Hull > 0) State.BuyFuel();

            float best = -1f;
            for (int i = 0; i < GameData.Spots.Length; i++)
            {
                if (!State.Known(i)) continue;
                var s = GameData.Spots[i];
                float total = 0f, value = 0f;
                foreach (var e in s.Table)
                {
                    total += e.weight;
                    value += e.weight * GameData.Get(e.species).AvgValue;
                }
                float score = value / total * State.Richness[i] / (1f + s.RowSeconds / 30f);
                if (score > best) { best = score; SelectedSpot = i; }
            }
            if (State.Hull > 0)
                while (State.FuelFraction <= .1f && State.BuyFuel()) { }
            SetSail();
        }
    }
}

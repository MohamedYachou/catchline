using System.Collections.Generic;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    // Build 1: tier 1-2 rowboat. Harbour -> row out -> fish with the rod -> row home -> sell.
    // Everything is built from primitives at startup; the HUD lives in VoyageHud.cs.
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
        public readonly List<DeckFish> OnDeck = new();
        public readonly List<CaughtFish> Cooler = new();
        public VoyageStats Stats = new();
        public float SimTime;
        public bool AutoPlay;
        public int Seed = 7;
        public readonly List<string> Log = new();

        static readonly Vector2Int CoolerTile = new(1, 1), CoolerAccess = new(1, 0), SeatTile = new(1, 0), HandRest = new(0, 1);

        Transform world, scenery, oldScenery, coolerLid;
        TextMesh coolerLabel;
        Material seaMat;
        Color seaFrom, seaTo;
        GameObject oarPort, oarStarboard;
        readonly List<Transform> waves = new();
        readonly List<(Transform t, float age)> splashes = new();
        float modeTimer, modeDuration, voyageStart, lidPop;
        bool built, hungryWarned, fullWarned;
        Rod charging;
        string toast;
        float toastUntil;

        void Awake() => Build();

        void Update()
        {
            if (!built) return;
            Tick(Time.deltaTime);
            HandleInput();
        }

        // ---- build ------------------------------------------------------------------------

        public void Build()
        {
            if (built) return;
            built = true;
            State = new GameState(Seed);
            Grid = new DeckGrid(3, 2);
            Grid.Block(new RectInt(CoolerTile.x, CoolerTile.y, 1, 1));
            BuildWorld();
            BuildBoat();
            Captain = new Person("Captain", true, new Vector3(0f, 0f, -0.05f));
            Captain.Build(Boat, SeatTile, Palette.HullNavy, Palette.Rail);
            scenery = BuildScenery(-1);
            SyncCrew();
            SyncUpgrades();
            EnterHarbour(false);
        }

        void BuildWorld()
        {
            var camGo = new GameObject("Camera") { tag = "MainCamera" };
            Cam = camGo.AddComponent<Camera>();
            Cam.orthographic = true;
            Cam.orthographicSize = 3.2f;
            Cam.clearFlags = CameraClearFlags.SolidColor;
            Cam.backgroundColor = Palette.Sea;
            Cam.nearClipPlane = 0.1f;
            Cam.farClipPlane = 120f;
            camGo.transform.rotation = Quaternion.Euler(50f, 24f, 0f);
            camGo.transform.position = new Vector3(1.1f, 0f, -1.3f) - camGo.transform.forward * 40f;

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.3f;
            sun.color = new Color(1f, 0.96f, 0.88f);
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(55f, -35f, 0f);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.58f, 0.64f, 0.7f);

            world = new GameObject("World").transform;
            var sea = Visuals.Box("Sea", world, new Vector3(0f, -0.4f, 0f), new Vector3(200f, 0.16f, 200f), Palette.Sea);
            seaMat = new Material(Visuals.Mat(Palette.Sea));
            sea.GetComponent<Renderer>().sharedMaterial = seaMat;
            seaFrom = seaTo = Palette.Sea;

            var rng = new System.Random(3);
            for (int i = 0; i < 34; i++)
            {
                var w = Visuals.Box("Wave", world, Vector3.zero, new Vector3(0.5f + (float)rng.NextDouble() * 0.6f, 0.01f, 0.05f), new Color(0.85f, 0.95f, 0.97f));
                w.transform.position = new Vector3(-14f + (float)rng.NextDouble() * 30f, -0.315f, -9f + (float)rng.NextDouble() * 14f);
                waves.Add(w.transform);
            }
        }

        void BuildBoat()
        {
            Boat = new GameObject("Rowboat").transform;
            Boat.SetParent(world, false);

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

            var floor = new GameObject("DeckFloor");
            floor.transform.SetParent(Boat, false);
            var fc = floor.AddComponent<BoxCollider>();
            fc.center = new Vector3(1f, -0.02f, 0.5f);
            fc.size = new Vector3(3f, 0.06f, 2f);
            floor.AddComponent<Tappable>().Deck = true;

            // Cooler on the starboard middle tile.
            var cooler = new GameObject("Cooler");
            cooler.transform.SetParent(Boat, false);
            cooler.transform.localPosition = DeckGrid.ToLocal(CoolerTile);
            Visuals.Box("Body", cooler.transform, new Vector3(0f, 0.22f, 0f), new Vector3(0.8f, 0.42f, 0.55f), Palette.Rail);
            Visuals.Box("Handle", cooler.transform, new Vector3(0f, 0.3f, -0.29f), new Vector3(0.3f, 0.05f, 0.04f), Palette.Rubber);
            coolerLid = new GameObject("LidHinge").transform;
            coolerLid.SetParent(cooler.transform, false);
            coolerLid.localPosition = new Vector3(0f, 0.43f, 0.28f);
            Visuals.Box("Lid", coolerLid, new Vector3(0f, 0.04f, -0.28f), new Vector3(0.84f, 0.08f, 0.59f), Palette.Accent);
            var cc = cooler.AddComponent<BoxCollider>();
            cc.center = new Vector3(0f, 0.3f, 0f);
            cc.size = new Vector3(0.9f, 0.6f, 0.7f);
            cooler.AddComponent<Tappable>().Cooler = true;
            coolerLabel = Visuals.Label("Count", cooler.transform, new Vector3(0f, 0.75f, 0f), 0.045f);
            coolerLabel.color = Palette.Rail;

            Rods.Add(new Rod(0, new Vector2Int(0, 0)));
            Rods.Add(new Rod(1, new Vector2Int(2, 0)));
            foreach (var r in Rods) r.Build(Boat, world);
        }

        // -1 = harbour quay, otherwise the fishing spot index.
        Transform BuildScenery(int kind)
        {
            var root = new GameObject(kind < 0 ? "Scenery Harbour" : $"Scenery {GameData.Spots[kind].Name}").transform;
            root.SetParent(world, false);
            var rng = new System.Random(100 + kind);
            float R(float a, float b) => a + (float)rng.NextDouble() * (b - a);
            var stone = Palette.Hex("8E8A80");
            var rock = Palette.Hex("6F7270");

            void Rock(Vector3 p, float s)
            {
                var g = Visuals.Box("Rock", root, p, new Vector3(s, s * 0.7f, s * 0.9f), rock);
                g.transform.localRotation = Quaternion.Euler(R(-15f, 15f), R(0f, 90f), R(-10f, 10f));
            }

            if (kind < 0)
            {
                Visuals.Box("Quay", root, new Vector3(1f, -0.1f, 4.4f), new Vector3(40f, 0.9f, 4.4f), stone);
                Visuals.Box("QuayEdge", root, new Vector3(1f, 0.37f, 2.3f), new Vector3(40f, 0.06f, 0.25f), Palette.Hex("A7A398"));
                foreach (float x in new[] { -4f, 0.2f, 4.5f, 9f })
                    Visuals.Prim(PrimitiveType.Cylinder, "Bollard", root, new Vector3(x, 0.55f, 2.7f), new Vector3(0.25f, 0.2f, 0.25f), Palette.Rubber);
                Color[] walls = { Palette.Hex("E9D8B4"), Palette.Hex("C9DDE0"), Palette.Hex("E7B9A0"), Palette.Hex("D9E3C5"), Palette.Rail };
                for (int i = 0; i < 7; i++)
                {
                    float x = -7f + i * 2.6f;
                    float h = R(1.6f, 2.6f);
                    var wall = walls[i % walls.Length];
                    Visuals.Box("House", root, new Vector3(x, 0.35f + h / 2f, 6.6f), new Vector3(2.3f, h, 2.2f), wall);
                    var roof = Visuals.Box("Roof", root, new Vector3(x, 0.35f + h, 6.6f), new Vector3(2.4f, 1.1f, 1.1f), i % 2 == 0 ? Palette.Accent : Palette.HullNavy);
                    roof.transform.localRotation = Quaternion.Euler(45f, 0f, 0f);
                    Visuals.Box("Door", root, new Vector3(x, 0.75f, 5.48f), new Vector3(0.4f, 0.8f, 0.05f), Palette.HullNavy);
                }
                for (int i = 0; i < 3; i++)
                {
                    float x = -3f + i * 5f;
                    Visuals.Prim(PrimitiveType.Cylinder, "Lamp", root, new Vector3(x, 1.1f, 3.4f), new Vector3(0.07f, 0.75f, 0.07f), Palette.Rubber);
                    Visuals.Box("LampHead", root, new Vector3(x, 1.9f, 3.4f), new Vector3(0.22f, 0.18f, 0.22f), Palette.Oilskin);
                }
                // A neighbour's boat moored further along.
                Visuals.Box("OtherBoat", root, new Vector3(7.2f, -0.25f, 1.1f), new Vector3(3.6f, 0.55f, 1.6f), Palette.Hex("B8473A"));
                Visuals.Box("OtherDeck", root, new Vector3(7.2f, 0.04f, 1.1f), new Vector3(3.4f, 0.05f, 1.4f), Palette.DeckWood);
                Visuals.Box("Crates", root, new Vector3(3.2f, 0.55f, 3.2f), new Vector3(0.5f, 0.4f, 0.4f), Palette.HullNavy);
                Visuals.Box("Crates2", root, new Vector3(3.7f, 0.55f, 3.4f), new Vector3(0.5f, 0.4f, 0.4f), Palette.Rail);
            }
            else if (kind == 0)
            {
                for (int i = 0; i < 16; i++) Rock(new Vector3(-9f + i * 0.9f, R(-0.2f, 0.1f), 6.5f + R(-0.3f, 0.3f)), R(0.8f, 1.3f));
                Visuals.Prim(PrimitiveType.Cylinder, "Lighthouse", root, new Vector3(6f, 1.6f, 6.6f), new Vector3(1f, 1.8f, 1f), Palette.Rail);
                Visuals.Prim(PrimitiveType.Cylinder, "Band", root, new Vector3(6f, 2.0f, 6.6f), new Vector3(1.04f, 0.3f, 1.04f), Palette.Bad);
                Visuals.Prim(PrimitiveType.Cylinder, "Top", root, new Vector3(6f, 3.6f, 6.6f), new Vector3(0.8f, 0.25f, 0.8f), Palette.Oilskin);
                Visuals.Prim(PrimitiveType.Sphere, "Buoy", root, new Vector3(-3f, -0.25f, -3.5f), Vector3.one * 0.35f, Palette.Accent);
            }
            else if (kind == 1)
            {
                var kelp = Palette.Hex("3F6B38");
                for (int i = 0; i < 22; i++)
                {
                    var p = new Vector3(R(-10f, 13f), -0.305f, R(-8f, 7f));
                    if (p.x > -1.5f && p.x < 4f && p.z > -1.2f && p.z < 2.2f) continue;
                    var k = Visuals.Prim(PrimitiveType.Cylinder, "Kelp", root, p, new Vector3(R(0.8f, 2.2f), 0.004f, R(0.5f, 1.4f)), i % 3 == 0 ? kelp * 1.2f : kelp);
                    k.transform.localRotation = Quaternion.Euler(0f, R(0f, 180f), 0f);
                }
                Rock(new Vector3(8f, -0.1f, 4f), 1.2f);
            }
            else
            {
                for (int i = 0; i < 9; i++) Rock(new Vector3(R(-10f, 12f), R(-0.2f, 0.3f), R(4f, 7f)), R(1f, 2.4f));
                for (int i = 0; i < 4; i++) Rock(new Vector3(R(-9f, 10f), -0.2f, R(-8f, -5f)), R(0.6f, 1.2f));
                Visuals.Box("Cliff", root, new Vector3(1f, 1.2f, 9.5f), new Vector3(40f, 3.4f, 3f), Palette.Hex("7C7A6E"));
                Visuals.Box("CliffTop", root, new Vector3(1f, 2.95f, 9.5f), new Vector3(40f, 0.15f, 3f), Palette.Hex("6C8F4A"));
            }
            return root;
        }

        // ---- flow -----------------------------------------------------------------------

        void SyncCrew()
        {
            if (State.Deckhand == null && Hand != null)
            {
                Visuals.Kill(Hand.Root.gameObject);
                Hand = null;
            }
            if (State.Deckhand != null && Hand == null)
            {
                var c = State.Deckhand;
                Hand = new Person(c.Name, false, new Vector3(0.12f, 0f, 0.08f)) { Speed = GameData.Speed(c.Grade), Contract = c };
                Hand.Build(Boat, HandRest, c.Suit, c.Grade == Grade.Veteran ? Palette.HullNavy : Palette.Accent);
            }
        }

        public void SyncUpgrades()
        {
            Rods[1].SetUnlocked(State.Has(UpgradeId.RodHolder));
            var lid = coolerLid.GetComponentInChildren<Renderer>();
            lid.sharedMaterial = Visuals.Mat(State.Has(UpgradeId.IceBox) ? Palette.Hex("4FB3C4") : Palette.Accent);
        }

        void EnterHarbour(bool arrived)
        {
            CurrentMode = Mode.Harbour;
            if (arrived)
            {
                var sale = State.Sell(Cooler, SimTime);
                sale.Minutes = (SimTime - voyageStart) / 60f;
                int spot = ActiveSpot;
                State.EndVoyage(sale);
                int earned = sale.Coins + sale.ContractCoins;
                Log.Add($"Voyage {State.Voyage - 1,2} {GameData.Spots[spot].Name,-13} {sale.Minutes:0.0} min  fish {sale.Caught,2}  " +
                        $"+{earned,3} ({earned / Mathf.Max(0.1f, sale.Minutes):0}/min)  coins {State.Coins,4}  bait {State.Bait,2}  " +
                        $"spooked {Stats.Spooked} missed {Stats.Missed} lost {Stats.Lost}  hand {(Hand != null ? GameData.GradeName(Hand.Contract.Grade) : "-")}  " +
                        $"upgrades [{string.Join(",", State.Owned)}]");
                Cooler.Clear();
                hudTab = HudTab.Catch;
            }
            SyncCrew();
            Captain.Rowing = false;
            Captain.Place(SeatTile);
            Captain.Face(Vector3.forward);
            Hand?.Place(HandRest);
            foreach (var r in Rods) r.ResetForTrip();
            oarPort.SetActive(false);
            oarStarboard.SetActive(false);
            botHarbourAt = SimTime + 0.5f;
        }

        public string SailBlocker()
        {
            if (CurrentMode != Mode.Harbour) return "Not in the harbour";
            if (State.Bait <= 0 && Rods.All(r => r.State != RodState.Ready)) return "Buy bait first";
            return null;
        }

        public void SetSail()
        {
            if (SailBlocker() != null) return;
            ActiveSpot = SelectedSpot;
            voyageStart = SimTime;
            Stats = new VoyageStats();
            hungryWarned = State.FoodMinutes <= 0f;
            fullWarned = false;
            BeginTransition(Mode.SailingOut, ActiveSpot);
            if (State.FoodMinutes <= 0f) Toast("No food on board: the crew works at 70% speed.");
        }

        public void HeadHome()
        {
            if (CurrentMode != Mode.Fishing) return;
            // Grab what's on deck if there's room; the rest goes back in the sea.
            foreach (var p in new[] { Captain, Hand })
            {
                if (p == null) continue;
                p.Stop();
                if (p.Carrying != null)
                {
                    if (Cooler.Count < State.CoolerCapacity) Cooler.Add(new CaughtFish { Species = p.Carrying.Species, Kg = p.Carrying.Kg, StowedAt = SimTime });
                    Visuals.Kill(p.Carrying.Root.gameObject);
                    p.Carrying = null;
                }
            }
            foreach (var f in OnDeck)
            {
                if (Cooler.Count < State.CoolerCapacity) Cooler.Add(new CaughtFish { Species = f.Species, Kg = f.Kg, StowedAt = SimTime });
                Visuals.Kill(f.Root.gameObject);
            }
            OnDeck.Clear();
            charging = null;
            foreach (var r in Rods) r.ResetForTrip();
            BeginTransition(Mode.SailingHome, -1);
        }

        void BeginTransition(Mode mode, int sceneryKind)
        {
            CurrentMode = mode;
            modeTimer = 0f;
            modeDuration = sceneryKind < 0 ? GameData.Spots[ActiveSpot].RowSeconds : GameData.Spots[sceneryKind].RowSeconds;
            if (oldScenery != null) Visuals.Kill(oldScenery.gameObject);
            oldScenery = scenery;
            scenery = BuildScenery(sceneryKind);
            scenery.localPosition = new Vector3(30f, 0f, 0f);
            seaFrom = seaMat.color;
            seaTo = sceneryKind < 0 ? Palette.Sea : GameData.Spots[sceneryKind].Water;
            Captain.Stop();
            Captain.Place(SeatTile);
            Captain.Face(Vector3.right);
            Captain.Rowing = true;
            Hand?.Stop();
            Hand?.Place(HandRest);
            oarPort.SetActive(true);
            oarStarboard.SetActive(true);
        }

        void FinishTransition()
        {
            if (oldScenery != null) Visuals.Kill(oldScenery.gameObject);
            oldScenery = null;
            scenery.localPosition = Vector3.zero;
            seaMat.color = seaTo;
            Captain.Rowing = false;
            oarPort.SetActive(false);
            oarStarboard.SetActive(false);
            if (CurrentMode == Mode.SailingOut)
            {
                CurrentMode = Mode.Fishing;
                Toast($"Arrived at {GameData.Spots[ActiveSpot].Name}. Tap the rod to walk to it.");
                Captain.WalkTo(Grid, Rods[0].Tile, () => Captain.Face(Vector3.back));
            }
            else EnterHarbour(true);
        }

        // ---- simulation -------------------------------------------------------------------

        public float WorkMult => State.FoodMinutes > 0f ? 1f : GameData.HungrySpeed;
        int CrewCount => Hand != null ? 2 : 1;

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
            SimTime += dt;
            var camRot = Cam.transform.rotation;
            switch (CurrentMode)
            {
                case Mode.Harbour:
                    if (AutoPlay && SimTime >= botHarbourAt) BotHarbour();
                    break;

                case Mode.SailingOut:
                case Mode.SailingHome:
                    Eat(dt);
                    modeTimer += dt * WorkMult;
                    float p = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(modeTimer / modeDuration));
                    if (oldScenery != null) oldScenery.localPosition = new Vector3(-30f * p, 0f, 0f);
                    scenery.localPosition = new Vector3(30f * (1f - p), 0f, 0f);
                    seaMat.color = Color.Lerp(seaFrom, seaTo, p);
                    float stroke = Mathf.Sin(SimTime * 3.2f);
                    oarPort.transform.localRotation = Quaternion.Euler(stroke * 8f, stroke * 25f, 0f);
                    oarStarboard.transform.localRotation = Quaternion.Euler(-stroke * 8f, -stroke * 25f, 0f);
                    if (modeTimer >= modeDuration) FinishTransition();
                    break;

                case Mode.Fishing:
                    Eat(dt);
                    float mult = WorkMult;
                    foreach (var r in Rods)
                        if (r.Unlocked) r.Tick(this, dt, mult, Attending(r));
                    if (charging != null && (charging.State != RodState.Charging || Captain.Tile != charging.Tile || Captain.Walking))
                    {
                        charging.CancelCharge();
                        charging = null;
                    }
                    if (Hand != null && Hand.Idle) HandThink(Hand);
                    if (AutoPlay) BotFish();
                    TickDeckFish(dt);
                    if (!fullWarned && Cooler.Count >= State.CoolerCapacity)
                    {
                        fullWarned = true;
                        Toast("The cooler is full. Head home to sell.");
                    }
                    break;
            }
            Captain.Tick(dt, WorkMult, camRot);
            Hand?.Tick(dt, WorkMult, camRot);
        }

        void Eat(float dt)
        {
            if (State.FoodMinutes <= 0f) return;
            State.FoodMinutes = Mathf.Max(0f, State.FoodMinutes - dt / 60f * CrewCount);
            if (State.FoodMinutes <= 0f && !hungryWarned)
            {
                hungryWarned = true;
                Toast("Out of food: the crew works at 70% speed.");
            }
        }

        void TickDeckFish(float dt)
        {
            for (int i = OnDeck.Count - 1; i >= 0; i--)
            {
                var f = OnDeck[i];
                f.Age += dt;
                float flop = Mathf.Max(0f, Mathf.Sin(f.Age * 7f + i)) * 0.1f;
                f.Root.localPosition = f.RestPos + Vector3.up * flop;
                f.Root.localRotation = Quaternion.Euler(0f, f.Age * 40f % 360f, Mathf.Sin(f.Age * 9f) * 25f);
                if (f.ClaimedBy == null && f.Age > GameData.DeckFishLifetime)
                {
                    Visuals.Kill(f.Root.gameObject);
                    OnDeck.RemoveAt(i);
                    Stats.Lost++;
                    Toast("A fish flopped back overboard.");
                }
            }
        }

        void Visual(float frameDt)
        {
            Boat.localRotation = Quaternion.Euler(Mathf.Sin(SimTime * 0.6f) * 1.2f, 0f, Mathf.Sin(SimTime * 0.9f) * 1.6f);
            Boat.localPosition = new Vector3(0f, Mathf.Sin(SimTime * 1.1f) * 0.03f, 0f);
            float waveSpeed = CurrentMode is Mode.SailingOut or Mode.SailingHome ? 3.5f : 0.25f;
            foreach (var w in waves)
            {
                var p = w.position;
                p.x -= waveSpeed * frameDt;
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
            lidPop = Mathf.Max(0f, lidPop - frameDt * 3f);
            coolerLid.localRotation = Quaternion.Euler(-lidPop * 70f, 0f, 0f);
            coolerLabel.text = $"{Cooler.Count}/{State.CoolerCapacity}";
            coolerLabel.color = Cooler.Count >= State.CoolerCapacity ? Palette.Oilskin : Palette.Rail;
            coolerLabel.transform.rotation = Cam.transform.rotation;
        }

        public void Splash(Vector3 pos, float size)
        {
            var s = Visuals.Prim(PrimitiveType.Cylinder, "Splash", world, pos + Vector3.up * 0.01f, new Vector3(size, 0.005f, size), new Color(0.92f, 0.97f, 1f));
            splashes.Add((s.transform, 0f));
        }

        public void Toast(string msg)
        {
            if (string.IsNullOrEmpty(msg)) return;
            toast = msg;
            toastUntil = SimTime + 3.2f;
        }

        // ---- deck actions -----------------------------------------------------------------

        bool Attending(Rod r) => !Captain.Walking && Captain.Tile == r.Tile;
        Rod RodAt(Vector2Int tile) => Rods.FirstOrDefault(r => r.Unlocked && r.Tile == tile);

        public void LandFish(Rod rod, Species s, float kg)
        {
            State.OnCatch(ActiveSpot);
            Stats.Landed++;
            var f = new DeckFish { Species = s, Kg = kg, Tile = rod.Tile };
            f.Root = DeckFish_Build(f);
            int n = OnDeck.Count(o => o.Tile == rod.Tile);
            f.RestPos = DeckGrid.ToLocal(rod.Tile) + new Vector3(-0.2f + n * 0.18f, 0.07f, 0.28f);
            f.Root.localPosition = f.RestPos;
            OnDeck.Add(f);
        }

        Transform DeckFish_Build(DeckFish f)
        {
            var holder = Catchline.Game.DeckFish.BuildModel(f.Species, f.Kg, Boat);
            var bc = holder.gameObject.AddComponent<BoxCollider>();
            bc.size = new Vector3(0.55f, 0.35f, 0.55f);
            holder.gameObject.AddComponent<Tappable>().Fish = f;
            return holder;
        }

        public void TapRod(Rod r)
        {
            if (CurrentMode != Mode.Fishing || !r.Unlocked) return;
            Captain.WalkTo(Grid, r.Tile, () => Captain.Face(Vector3.back));
        }

        public void TapFish(DeckFish f)
        {
            if (CurrentMode != Mode.Fishing) return;
            if (Captain.Carrying != null) { Toast("Your hands are full. Stow this fish in the cooler first."); return; }
            if (f.ClaimedBy != null && f.ClaimedBy != Captain) { Toast($"{f.ClaimedBy.Name} is already on it."); return; }
            Fetch(Captain, f);
        }

        void Fetch(Person p, DeckFish f)
        {
            f.ClaimedBy = p;
            void Release() { if (f.ClaimedBy == p) f.ClaimedBy = null; }
            p.WalkTo(Grid, f.Tile, () => p.Do("Picking up", GameData.PickupTime, () => PickUp(p, f), Release), Release);
        }

        void PickUp(Person p, DeckFish f)
        {
            if (!OnDeck.Contains(f)) return;
            OnDeck.Remove(f);
            f.Root.GetComponent<Collider>().enabled = false;
            f.Root.SetParent(p.Root, false);
            p.Carrying = f;
        }

        public void TapCooler()
        {
            if (CurrentMode != Mode.Fishing) return;
            if (Captain.Carrying == null) { Toast("Carry a fish here to put it in the cooler."); return; }
            Stow(Captain);
        }

        void Stow(Person p)
        {
            p.WalkTo(Grid, CoolerAccess, () =>
            {
                p.Face(Vector3.forward);
                p.Do("Stowing", GameData.StowTime, () => TryStow(p));
            });
        }

        bool TryStow(Person p)
        {
            if (p.Carrying == null) return false;
            if (Cooler.Count >= State.CoolerCapacity)
            {
                if (p == Captain) Toast("The cooler is full! Head home to sell.");
                return false;
            }
            Cooler.Add(new CaughtFish { Species = p.Carrying.Species, Kg = p.Carrying.Kg, StowedAt = SimTime });
            Visuals.Kill(p.Carrying.Root.gameObject);
            p.Carrying = null;
            lidPop = 1f;
            return true;
        }

        public void TapDeck(Vector3 worldPoint)
        {
            if (CurrentMode != Mode.Fishing) return;
            var tile = DeckGrid.ToTile(Boat.InverseTransformPoint(worldPoint));
            tile.x = Mathf.Clamp(tile.x, 0, Grid.Width - 1);
            tile.y = Mathf.Clamp(tile.y, 0, Grid.Height - 1);
            if (Grid.IsBlocked(tile)) return;
            Captain.WalkTo(Grid, tile, null);
        }

        void Bait(Person p, Rod rod)
        {
            if (State.Bait <= 0)
            {
                if (p == Captain) Toast("Out of bait. Head home and buy more.");
                return;
            }
            rod.BaitingBy = p;
            p.Do("Baiting", GameData.BaitTime, () =>
            {
                rod.BaitingBy = null;
                if (rod.State == RodState.Unbaited && State.Bait > 0)
                {
                    State.Bait--;
                    rod.State = RodState.Ready;
                }
            }, () => rod.BaitingBy = null);
        }

        // Deckhand: carry fish to the cooler first, then bait empty hooks, then rest.
        void HandThink(Person h)
        {
            if (h.Carrying != null)
            {
                if (Cooler.Count < State.CoolerCapacity) Stow(h);
                else if (h.Tile != HandRest) h.WalkTo(Grid, HandRest, null);
                else h.Do("Waiting", 1f, null);
                return;
            }
            var f = OnDeck.FirstOrDefault(x => x.ClaimedBy == null);
            if (f != null)
            {
                Fetch(h, f);
                return;
            }
            var rod = Rods.FirstOrDefault(r => r.Unlocked && r.State == RodState.Unbaited && r.BaitingBy == null);
            if (rod != null && State.Bait > 0)
            {
                rod.BaitingBy = h;
                h.WalkTo(Grid, rod.Tile, () => Bait(h, rod), () => rod.BaitingBy = null);
                return;
            }
            if (h.Tile != HandRest) h.WalkTo(Grid, HandRest, null);
            else h.Do("Resting", 0.5f, null);
        }

        // ---- the action button ----------------------------------------------------------------

        public enum ActionKind { None, Strike, Cast, Bait, Stow, PickUp, GoToRod }

        public struct ActionInfo
        {
            public ActionKind Kind;
            public string Label;
            public bool Hot;
            public Rod Rod;
            public DeckFish Fish;
        }

        public ActionInfo Context()
        {
            var a = new ActionInfo { Kind = ActionKind.None, Label = "" };
            if (CurrentMode != Mode.Fishing) return a;
            if (Captain.Carrying != null) return new ActionInfo { Kind = ActionKind.Stow, Label = "Put in cooler" };
            if (Captain.Busy) return new ActionInfo { Label = Captain.BusyLabel + "..." };

            var here = Captain.Walking ? null : RodAt(Captain.Tile);
            if (here != null)
            {
                switch (here.State)
                {
                    case RodState.Waiting: return new ActionInfo { Kind = ActionKind.Strike, Label = "Strike!", Rod = here };
                    case RodState.Bite: return new ActionInfo { Kind = ActionKind.Strike, Label = "STRIKE!", Hot = true, Rod = here };
                    case RodState.Ready: return new ActionInfo { Kind = ActionKind.Cast, Label = "Hold to cast", Rod = here };
                    case RodState.Charging: return new ActionInfo { Kind = ActionKind.Cast, Label = "Release to cast", Rod = here };
                    case RodState.Flying: return new ActionInfo { Label = "Casting..." };
                    case RodState.Reeling: return new ActionInfo { Label = "Reeling in..." };
                    case RodState.Unbaited:
                        if (here.BaitingBy != null) return new ActionInfo { Label = $"{here.BaitingBy.Name} is baiting" };
                        if (State.Bait > 0) return new ActionInfo { Kind = ActionKind.Bait, Label = "Bait hook", Rod = here };
                        break;
                }
            }
            var fish = OnDeck.FirstOrDefault(x => x.ClaimedBy == null || x.ClaimedBy == Captain);
            if (fish != null) return new ActionInfo { Kind = ActionKind.PickUp, Label = "Pick up fish", Fish = fish };
            var target = Rods.Where(r => r.Unlocked && r != here)
                .OrderByDescending(r => r.State switch { RodState.Bite => 3, RodState.Ready => 2, RodState.Unbaited => 1, _ => 0 })
                .FirstOrDefault();
            if (here == null && target == null) target = Rods[0];
            if (target != null && (here == null || target.State is RodState.Ready or RodState.Bite or RodState.Unbaited))
                return new ActionInfo { Kind = ActionKind.GoToRod, Label = $"Go to rod {target.Index + 1}", Rod = target };
            if (State.Bait <= 0 && here != null && here.State == RodState.Unbaited) return new ActionInfo { Label = "Out of bait" };
            return a;
        }

        public void ActionPress()
        {
            var a = Context();
            switch (a.Kind)
            {
                case ActionKind.Strike: Toast(a.Rod.Strike(this)); break;
                case ActionKind.Cast:
                    a.Rod.BeginCharge();
                    charging = a.Rod;
                    break;
                case ActionKind.Bait: Bait(Captain, a.Rod); break;
                case ActionKind.Stow: Stow(Captain); break;
                case ActionKind.PickUp: TapFish(a.Fish); break;
                case ActionKind.GoToRod: TapRod(a.Rod); break;
            }
        }

        public void ActionRelease()
        {
            if (charging == null) return;
            if (charging.State == RodState.Charging) charging.Cast(this, charging.Power);
            charging = null;
        }

        public bool IsCharging => charging != null && charging.State == RodState.Charging;
        public float ChargePower => charging != null ? charging.Power : 0f;

        // ---- events from the rods (the bot listens here too) --------------------------------

        Rod botStrikeRod;
        float botStrikeAt, botHarbourAt;

        public void OnNibble(Rod r)
        {
            if (AutoPlay && Attending(r) && State.Rng.NextDouble() < 0.05) Toast(r.Strike(this));
        }

        public void OnBite(Rod r)
        {
            if (!AutoPlay || !Attending(r)) return;
            botStrikeRod = r;
            botStrikeAt = SimTime + (State.Rng.NextDouble() < 0.12 ? 1.0f : 0.25f + (float)State.Rng.NextDouble() * 0.5f);
        }

        // ---- autoplay (headless balance checks) -----------------------------------------------

        void BotFish()
        {
            if (botStrikeRod != null && SimTime >= botStrikeAt)
            {
                Toast(botStrikeRod.Strike(this));
                botStrikeRod = null;
            }
            var c = Captain;
            if (!c.Idle) return;

            bool handBusy = Hand != null && (Hand.Carrying != null || !Hand.Idle && Hand.BusyLabel == "Picking up");
            bool full = Cooler.Count >= State.CoolerCapacity;
            bool noBait = State.Bait <= 0 && Rods.All(r => !r.Unlocked || r.State == RodState.Unbaited);
            if (full && c.Carrying == null || noBait && c.Carrying == null && OnDeck.Count == 0 && !handBusy && Rods.All(r => r.State is not RodState.Reeling))
            {
                HeadHome();
                return;
            }
            if (c.Carrying != null)
            {
                if (full) HeadHome();
                else Stow(c);
                return;
            }
            if (Hand == null)
            {
                var f = OnDeck.FirstOrDefault(x => x.ClaimedBy == null);
                if (f != null) { Fetch(c, f); return; }
            }
            var here = RodAt(c.Tile);
            if (here != null)
            {
                if (here.State == RodState.Ready) { here.Cast(this, 0.5f + (float)State.Rng.NextDouble() * 0.4f); return; }
                if (here.State == RodState.Unbaited && Hand == null && State.Bait > 0 && here.BaitingBy == null) { Bait(c, here); return; }
            }
            var ready = Rods.FirstOrDefault(r => r.Unlocked && r != here && r.State == RodState.Ready);
            var unbaited = Hand == null ? Rods.FirstOrDefault(r => r.Unlocked && r != here && r.State == RodState.Unbaited && State.Bait > 0) : null;
            var next = ready ?? unbaited;
            if (next != null && (here == null || here.State is not (RodState.Bite or RodState.Reeling or RodState.Flying)))
            {
                TapRod(next);
                return;
            }
            if (here == null)
            {
                var waiting = Rods.Where(r => r.Unlocked && r.State == RodState.Waiting).OrderBy(r => r.WaitRemaining).FirstOrDefault();
                if (waiting != null) TapRod(waiting);
            }
        }

        void BotHarbour()
        {
            botHarbourAt = float.MaxValue;
            while (State.Active.Count < GameData.MaxActiveContracts && State.Offers.Count > 0) State.TakeContract(State.Offers[0]);
            foreach (var id in new[] { UpgradeId.RodHolder, UpgradeId.IceBox, UpgradeId.BigCooler, UpgradeId.LunchTin })
            {
                if (State.Has(id)) continue;
                if (State.Coins < GameData.Upgrade(id).Cost + 30) break;
                State.TryBuy(id);
            }
            SyncUpgrades();
            if (State.Deckhand == null && State.Has(UpgradeId.RodHolder))
            {
                var pick = State.Board.Where(b => State.Coins >= b.Fee + 30).OrderByDescending(b => b.Grade).FirstOrDefault();
                if (pick != null) State.Hire(pick);
                SyncCrew();
            }
            while (State.Bait < (State.Has(UpgradeId.RodHolder) ? 40 : 25) && State.BuyBait()) { }
            State.FillFood();

            float best = -1f;
            for (int i = 0; i < GameData.Spots.Length; i++)
            {
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
            SetSail();
        }
    }
}

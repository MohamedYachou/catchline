using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Catchline.Prototype
{
    // Blocky deck prototype: a 10x5 day-boat deck, five Crab Coast stations, a captain
    // and two deckhands. Everything is built from primitives at startup, so the scene
    // only needs this one component.
    //
    // Controls: tap a person to select them, tap a station to assign them to it,
    // tap the bare deck to make them a free deckhand (carries and fills gaps).
    public class DeckPrototype : MonoBehaviour
    {
        public const int TotalPots = 10;
        public const int CrabPrice = 6;
        public const int HireCost = 150;
        public const int MaxCrew = 5;

        public DeckGrid Grid { get; private set; }
        public Transform Boat { get; private set; }
        public Camera Cam { get; private set; }
        public readonly List<Station> Stations = new();
        public readonly List<Worker> Workers = new();

        public int PotsInWater = TotalPots;
        public int PotsBeingHauled;
        public int Money = 100;
        public int CrabsDelivered;
        public float SimTime;
        public float Speed = 1f;

        readonly System.Random rng = new(42);
        readonly Queue<float> deliveryTimes = new();
        readonly List<GameObject> buoys = new();
        Station hauler, sorter, bander, tank, rack;
        Transform tankWater;
        Worker selected;
        string toast;
        float toastUntil;
        bool built;

        static readonly Vector2Int[] RestTiles = { new(4, 3), new(3, 3), new(7, 3), new(7, 1), new(2, 2) };
        static readonly string[] HireNames = { "Ana", "Bram", "Kofi" };
        static readonly Color[] HireSuits = { new(0.25f, 0.6f, 0.35f), new(0.55f, 0.3f, 0.6f), new(0.3f, 0.45f, 0.8f) };

        void Awake() => Build();

        void Update()
        {
            if (!built) return;
            Tick(Time.deltaTime * Speed);
            HandleInput();
        }

        // ---- world ----------------------------------------------------------------

        public void Build()
        {
            if (built) return;
            built = true;
            Grid = new DeckGrid(10, 5);
            BuildWorld();
            BuildStations();
            BuildCrew();
        }

        void BuildWorld()
        {
            var sea = new Color(0.13f, 0.56f, 0.72f);
            var deckCenter = new Vector3(4.5f, 0f, 2f);

            var camGo = new GameObject("Camera") { tag = "MainCamera" };
            Cam = camGo.AddComponent<Camera>();
            Cam.orthographic = true;
            Cam.orthographicSize = 4.4f;
            Cam.clearFlags = CameraClearFlags.SolidColor;
            Cam.backgroundColor = sea;
            Cam.nearClipPlane = 0.1f;
            Cam.farClipPlane = 100f;
            camGo.transform.rotation = Quaternion.Euler(48f, 28f, 0f);
            camGo.transform.position = deckCenter + new Vector3(0.6f, 0f, 0.4f) - camGo.transform.forward * 30f;

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.25f;
            sun.color = new Color(1f, 0.96f, 0.88f);
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(55f, -35f, 0f);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.55f, 0.62f, 0.7f);

            var world = new GameObject("World").transform;
            Visuals.Box("Sea", world, new Vector3(5f, -0.6f, 2f), new Vector3(120f, 0.1f, 120f), sea);
            for (int i = 0; i < TotalPots; i++)
            {
                var b = Visuals.Prim(PrimitiveType.Sphere, "Buoy", world,
                    new Vector3(0.6f + i * 0.9f, -0.5f, -2.0f - (i % 2) * 0.7f), Vector3.one * 0.24f, new Color(1f, 0.45f, 0.15f));
                buoys.Add(b);
            }

            Boat = new GameObject("Boat").transform;
            var navy = new Color(0.12f, 0.24f, 0.48f);
            var woodA = new Color(0.74f, 0.56f, 0.36f);
            var woodB = new Color(0.69f, 0.51f, 0.32f);
            var rail = new Color(0.93f, 0.93f, 0.9f);

            // Hull, stripe and a pointed bow made from a cube turned 45 degrees.
            Visuals.Box("Hull", Boat, new Vector3(4.5f, -0.42f, 2f), new Vector3(10.6f, 0.75f, 5.6f), navy);
            Visuals.Box("Stripe", Boat, new Vector3(4.5f, -0.24f, 2f), new Vector3(10.64f, 0.08f, 5.64f), new Color(0.88f, 0.36f, 0.2f));
            float bowSize = 5.6f / Mathf.Sqrt(2f);
            var bow = Visuals.Box("Bow", Boat, new Vector3(9.8f, -0.42f, 2f), new Vector3(bowSize, 0.75f, bowSize), navy);
            bow.transform.localRotation = Quaternion.Euler(0f, 45f, 0f);
            var bowDeck = Visuals.Box("BowDeck", Boat, new Vector3(9.8f, -0.05f, 2f), new Vector3(bowSize - 0.3f, 0.1f, bowSize - 0.3f), woodB);
            bowDeck.transform.localRotation = Quaternion.Euler(0f, 45f, 0f);

            for (int x = 0; x < Grid.Width; x++)
                for (int y = 0; y < Grid.Height; y++)
                    Visuals.Box($"Tile {x},{y}", Boat, new Vector3(x, -0.05f, y), new Vector3(0.98f, 0.1f, 0.98f), (x + y) % 2 == 0 ? woodA : woodB);

            var floor = new GameObject("DeckFloor");
            floor.transform.SetParent(Boat, false);
            var fc = floor.AddComponent<BoxCollider>();
            fc.center = new Vector3(4.5f, -0.05f, 2f);
            fc.size = new Vector3(10f, 0.1f, 5f);
            floor.AddComponent<Clickable>().Deck = true;

            // Rails, with a gap at the pot hauler on the port side.
            Visuals.Box("RailPortAft", Boat, new Vector3(0f, 0.15f, -0.46f), new Vector3(1f, 0.3f, 0.08f), rail);
            Visuals.Box("RailPortFwd", Boat, new Vector3(5.65f, 0.15f, -0.46f), new Vector3(8.3f, 0.3f, 0.08f), rail);
            Visuals.Box("RailStarboard", Boat, new Vector3(4.65f, 0.15f, 4.46f), new Vector3(10.3f, 0.3f, 0.08f), rail);
            Visuals.Box("RailStern", Boat, new Vector3(-0.46f, 0.15f, 2f), new Vector3(0.08f, 0.3f, 5f), rail);

            // Wheelhouse at the bow, 2x3 tiles.
            var house = new RectInt(8, 1, 2, 3);
            Grid.Block(house);
            Visuals.Box("Wheelhouse", Boat, new Vector3(8.5f, 0.8f, 2f), new Vector3(1.9f, 1.6f, 2.9f), new Color(0.95f, 0.95f, 0.93f));
            Visuals.Box("Roof", Boat, new Vector3(8.5f, 1.66f, 2f), new Vector3(2.1f, 0.12f, 3.1f), new Color(0.9f, 0.35f, 0.22f));
            Visuals.Box("Windows", Boat, new Vector3(7.54f, 1.1f, 2f), new Vector3(0.04f, 0.35f, 2.4f), new Color(0.2f, 0.3f, 0.4f));
            Visuals.Prim(PrimitiveType.Cylinder, "Mast", Boat, new Vector3(8.8f, 2.4f, 2f), new Vector3(0.08f, 0.7f, 0.08f), rail);
        }

        Station AddStation(string name, StationKind kind, RectInt footprint, Vector2Int access, float workTime, float height, Color color)
        {
            var s = new Station(name, kind, footprint, access, workTime, height);
            Grid.Block(footprint);
            s.BuildVisual(Boat, color);
            Stations.Add(s);
            return s;
        }

        void BuildStations()
        {
            hauler = AddStation("Pot hauler", StationKind.Hauler, new RectInt(1, 0, 1, 1), new Vector2Int(1, 1), 3.5f, 0.45f, new Color(0.95f, 0.55f, 0.15f));
            hauler.AddOutput(ItemType.FullPot, 4, new Vector3(0f, 0f, 0.05f));
            Visuals.Box("Davit", hauler.Root, new Vector3(0f, 0.9f, -0.35f), new Vector3(0.12f, 0.9f, 0.12f), new Color(0.95f, 0.55f, 0.15f));

            sorter = AddStation("Sorting table", StationKind.SortTable, new RectInt(3, 2, 2, 1), new Vector2Int(3, 1), 2.5f, 0.55f, new Color(0.62f, 0.66f, 0.7f));
            sorter.AddInput(ItemType.FullPot, 4, new Vector3(-0.5f, 0f, 0f));
            sorter.AddOutput(ItemType.Crab, 8, new Vector3(0.45f, 0f, -0.15f));
            sorter.AddOutput(ItemType.EmptyPot, 4, new Vector3(0.45f, 0f, 0.28f));

            bander = AddStation("Banding bench", StationKind.BandingBench, new RectInt(6, 2, 1, 1), new Vector2Int(6, 1), 1.2f, 0.5f, new Color(0.35f, 0.62f, 0.4f));
            bander.AddInput(ItemType.Crab, 8, new Vector3(-0.2f, 0f, 0.1f));
            bander.AddOutput(ItemType.BandedCrab, 6, new Vector3(0.22f, 0f, 0.1f));

            tank = AddStation("Live tank", StationKind.LiveTank, new RectInt(5, 4, 2, 1), new Vector2Int(6, 3), 0f, 0.7f, new Color(0.22f, 0.45f, 0.75f));
            tank.AddInput(ItemType.BandedCrab, 30, null);
            tankWater = Visuals.Box("Water", tank.Root, new Vector3(0f, 0.7f, 0f), new Vector3(1.7f, 0.02f, 0.7f), new Color(0.35f, 0.75f, 0.9f)).transform;

            rack = AddStation("Pot rack", StationKind.PotRack, new RectInt(1, 4, 2, 1), new Vector2Int(1, 3), 1.5f, 0.2f, new Color(0.5f, 0.38f, 0.25f));
            rack.AddInput(ItemType.EmptyPot, 6, new Vector3(0f, 0f, 0f));

            hauler.Routes[ItemType.FullPot] = sorter;
            sorter.Routes[ItemType.Crab] = bander;
            sorter.Routes[ItemType.EmptyPot] = rack;
            bander.Routes[ItemType.BandedCrab] = tank;
        }

        void BuildCrew()
        {
            var captain = AddWorker("Captain", true, new Color(0.15f, 0.2f, 0.4f), Color.white);
            captain.WorkSpeed = 1.3f;
            AddWorker("Sam", false, new Color(0.98f, 0.8f, 0.2f), new Color(0.95f, 0.45f, 0.15f)).Assigned = hauler;
            AddWorker("Jo", false, new Color(0.95f, 0.5f, 0.15f), new Color(0.2f, 0.4f, 0.75f)).Assigned = sorter;
            Select(captain);
        }

        Worker AddWorker(string name, bool captain, Color suit, Color hat)
        {
            int index = Workers.Count;
            var w = new Worker(name, captain, index);
            w.BuildVisual(Boat, RestTiles[index % RestTiles.Length], suit, hat);
            Workers.Add(w);
            return w;
        }

        // ---- simulation -----------------------------------------------------------

        public void Tick(float dt)
        {
            if (!built) return;
            // Fixed small steps keep 4x speed stable.
            while (dt > 0f)
            {
                float step = Mathf.Min(dt, 0.05f);
                dt -= step;
                SimTime += step;
                foreach (var w in Workers) w.Tick(this, step);
                var face = Cam.transform.rotation;
                foreach (var s in Stations) s.Tick(this, step, face);
            }

            Boat.localRotation = Quaternion.Euler(Mathf.Sin(SimTime * 0.53f) * 0.5f, 0f, Mathf.Sin(SimTime * 0.8f) * 0.8f);
            for (int i = 0; i < buoys.Count; i++)
            {
                buoys[i].SetActive(i < PotsInWater);
                var p = buoys[i].transform.localPosition;
                buoys[i].transform.localPosition = new Vector3(p.x, -0.5f + Mathf.Sin(SimTime * 1.7f + i) * 0.04f, p.z);
            }
            var t = tank.Inputs[ItemType.BandedCrab];
            float level = Mathf.Max(0.02f, 0.6f * t.Fill);
            tankWater.localScale = new Vector3(1.7f, level, 0.7f);
            tankWater.localPosition = new Vector3(0f, 0.1f + level / 2f, 0f);
            while (deliveryTimes.Count > 0 && deliveryTimes.Peek() < SimTime - 60f) deliveryTimes.Dequeue();
        }

        public int RollKeepers()
        {
            // Shore crab: plenty undersized, so 0-3 keepers per pot, 1.5 on average.
            int r = rng.Next(100);
            return r < 15 ? 0 : r < 50 ? 1 : r < 85 ? 2 : 3;
        }

        public void OnDelivered(Station dest, ItemType item)
        {
            if (dest != tank) return;
            CrabsDelivered++;
            deliveryTimes.Enqueue(SimTime);
        }

        public float CrabsPerMinute => deliveryTimes.Count * 60f / Mathf.Clamp(SimTime, 1f, 60f);

        // Picks the next job for an idle worker.
        public void AssignJob(Worker w)
        {
            if (w.Assigned != null)
            {
                var s = w.Assigned;
                if (s.HasWork && s.Operator == null && s.CanStartWork(this))
                {
                    w.StartWork(this, s);
                    return;
                }
                var c = BestCarry(s);
                if (c.from != null)
                {
                    w.StartCarry(this, c.from, c.to, c.type);
                    return;
                }
                if (w.Tile != s.Access) w.StartIdle(this, s.Access);
                else w.Wait(0.3f);
                return;
            }

            // Free deckhand: carry the fullest pile, or run a station nobody is assigned to.
            var carry = BestCarry(null);
            Station bestWork = null;
            float workScore = -1f;
            foreach (var s in Stations)
            {
                if (!s.HasWork || s.Operator != null || !s.CanStartWork(this) || HasAssignee(s)) continue;
                float score = s.WorkScore(this);
                if (score > workScore)
                {
                    workScore = score;
                    bestWork = s;
                }
            }

            if (carry.from != null && (bestWork == null || carry.score - 0.15f >= 0.5f && carry.score >= workScore)) w.StartCarry(this, carry.from, carry.to, carry.type);
            else if (bestWork != null) w.StartWork(this, bestWork);
            else
            {
                var rest = RestTiles[Workers.IndexOf(w) % RestTiles.Length];
                if (w.Tile != rest) w.StartIdle(this, rest);
                else w.Wait(0.4f);
            }
        }

        bool HasAssignee(Station s)
        {
            foreach (var o in Workers)
                if (o.Assigned == s) return true;
            return false;
        }

        (Station from, Station to, ItemType type, float score) BestCarry(Station onlyFrom)
        {
            (Station, Station, ItemType, float) best = (null, null, default, -1f);
            foreach (var s in Stations)
            {
                if (onlyFrom != null && s != onlyFrom) continue;
                foreach (var route in s.Routes)
                {
                    var src = s.Outputs[route.Key];
                    var dst = route.Value.Inputs[route.Key];
                    if (src.Available <= 0 || dst.Space <= 0) continue;
                    float score = src.Fill + 0.15f;
                    if (score > best.Item4) best = (s, route.Value, route.Key, score);
                }
            }
            return best;
        }

        // ---- player actions ---------------------------------------------------------

        void Select(Worker w)
        {
            if (selected != null) selected.SetSelected(false);
            selected = w;
            if (selected != null) selected.SetSelected(true);
        }

        void Assign(Worker w, Station s)
        {
            if (s != null && !s.HasWork)
            {
                Toast("The tank has no job of its own: free deckhands carry crabs into it.");
                return;
            }
            w.Assigned = s;
            Toast(s == null ? $"{w.Name} is now a free deckhand." : $"{w.Name} now runs the {s.Name.ToLower()}.");
        }

        void SellCatch()
        {
            var t = tank.Inputs[ItemType.BandedCrab];
            if (t.Count == 0)
            {
                Toast("The tank is empty.");
                return;
            }
            int earned = t.Count * CrabPrice;
            Money += earned;
            Toast($"Sold {t.Count} crabs for €{earned}.");
            t.Clear();
        }

        void Hire()
        {
            if (Workers.Count >= MaxCrew) { Toast("The deck is full."); return; }
            if (Money < HireCost) { Toast($"Hiring costs €{HireCost}."); return; }
            Money -= HireCost;
            int i = Workers.Count - 3;
            var w = AddWorker(HireNames[i], false, HireSuits[i], new Color(0.9f, 0.2f, 0.25f));
            Select(w);
            Toast($"{w.Name} joined as a free deckhand. Tap a station to give them a job.");
        }

        // Test hook: staffs the banding bench and pot rack without paying.
        public void StaffFully()
        {
            AddWorker(HireNames[0], false, HireSuits[0], new Color(0.9f, 0.2f, 0.25f)).Assigned = bander;
            AddWorker(HireNames[1], false, HireSuits[1], new Color(0.9f, 0.2f, 0.25f)).Assigned = rack;
        }

        void Toast(string message)
        {
            toast = message;
            toastUntil = Time.realtimeSinceStartup + 3.5f;
        }

        // ---- input -------------------------------------------------------------------

        readonly List<Rect> hudRects = new();
        float GuiScale => Screen.height / 720f;

        void HandleInput()
        {
            var mouse = Mouse.current;
            if (mouse != null)
            {
                float scroll = mouse.scroll.ReadValue().y;
                if (Mathf.Abs(scroll) > 0.01f) Cam.orthographicSize = Mathf.Clamp(Cam.orthographicSize - Mathf.Sign(scroll) * 0.4f, 2.5f, 8f);
            }

            var pointer = Pointer.current;
            if (pointer == null || !pointer.press.wasReleasedThisFrame) return;
            var screen = pointer.position.ReadValue();
            var gui = new Vector2(screen.x / GuiScale, (Screen.height - screen.y) / GuiScale);
            foreach (var r in hudRects)
                if (r.Contains(gui)) return;

            if (!Physics.Raycast(Cam.ScreenPointToRay(screen), out var hit, 200f)) return;
            var c = hit.collider.GetComponent<Clickable>();
            if (c == null) return;
            if (c.Worker != null) Select(c.Worker);
            else if (c.Station != null && selected != null) Assign(selected, c.Station);
            else if (c.Deck && selected != null) Assign(selected, null);
        }

        // ---- HUD (IMGUI, prototype only) ------------------------------------------

        GUIStyle box, big, small, button;

        void OnGUI()
        {
            if (!built) return;
            if (box == null)
            {
                box = new GUIStyle(GUI.skin.box) { alignment = TextAnchor.UpperLeft, padding = new RectOffset(12, 12, 10, 10) };
                big = new GUIStyle(GUI.skin.label) { fontSize = 22, fontStyle = FontStyle.Bold };
                small = new GUIStyle(GUI.skin.label) { fontSize = 15, wordWrap = true };
                button = new GUIStyle(GUI.skin.button) { fontSize = 15 };
            }
            GUI.matrix = Matrix4x4.Scale(new Vector3(GuiScale, GuiScale, 1f));
            hudRects.Clear();

            var stats = new Rect(12, 12, 300, 238);
            hudRects.Add(stats);
            GUI.Box(stats, GUIContent.none, box);
            GUILayout.BeginArea(new Rect(stats.x + 12, stats.y + 8, stats.width - 24, stats.height - 16));
            GUILayout.Label($"€{Money}", big);
            var t = tank.Inputs[ItemType.BandedCrab];
            GUILayout.Label($"Live tank {t.Count}/{t.Capacity}   Pots in water {PotsInWater}/{TotalPots}", small);
            GUILayout.Label($"Crabs per minute {CrabsPerMinute:0.0}   Total {CrabsDelivered}", small);
            GUILayout.BeginHorizontal();
            foreach (var sp in new[] { 1f, 2f, 4f })
                if (GUILayout.Toggle(Mathf.Approximately(Speed, sp), $"{sp}x", button)) Speed = sp;
            GUILayout.EndHorizontal();
            if (GUILayout.Button($"Sell catch (€{CrabPrice} per crab)", button)) SellCatch();
            if (GUILayout.Button($"Hire deckhand (€{HireCost})", button)) Hire();
            GUILayout.EndArea();

            float vw = Screen.width / GuiScale;
            var crew = new Rect(vw - 312, 12, 300, 30 + Workers.Count * 40);
            hudRects.Add(crew);
            GUI.Box(crew, GUIContent.none, box);
            GUILayout.BeginArea(new Rect(crew.x + 12, crew.y + 8, crew.width - 24, crew.height - 16));
            foreach (var w in Workers)
            {
                string job = w.Assigned != null ? w.Assigned.Name : "free deckhand";
                if (GUILayout.Button($"{(w == selected ? "> " : "")}{w.Name}: {job}\n{w.StateText}", small)) Select(w);
            }
            GUILayout.EndArea();

            var help = new Rect(12, 720 - 74, 620, 62);
            hudRects.Add(help);
            GUI.Box(help, GUIContent.none, box);
            GUI.Label(new Rect(help.x + 12, help.y + 6, help.width - 24, help.height - 12),
                "Tap a person to select them, then tap a station to give them that job. Tap the bare deck to make them a free deckhand. Scroll to zoom.", small);

            if (toast != null && Time.realtimeSinceStartup < toastUntil)
            {
                var r = new Rect(vw / 2 - 260, 14, 520, 40);
                GUI.Box(r, GUIContent.none, box);
                GUI.Label(new Rect(r.x + 12, r.y + 9, r.width - 24, 26), toast, small);
            }
        }

        // ---- diagnostics -------------------------------------------------------------

        public string Report()
        {
            var sb = new StringBuilder();
            sb.AppendLine($"t={SimTime:0}s  crabs delivered={CrabsDelivered}  per-min(last 60s)={CrabsPerMinute:0.0}  pots in water={PotsInWater}  money=€{Money}");
            foreach (var s in Stations) sb.AppendLine("  " + s.Report(SimTime));
            foreach (var w in Workers) sb.AppendLine($"  {w.Name}: {(w.Assigned != null ? w.Assigned.Name : "free")} - {w.StateText}");
            return sb.ToString();
        }
    }
}

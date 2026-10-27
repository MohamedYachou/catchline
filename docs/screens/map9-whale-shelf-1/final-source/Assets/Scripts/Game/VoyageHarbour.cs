using System.Collections.Generic;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    // Gull Harbour grows with the boat (docs/plans/HARBOUR-PLAN.md). Each hull has its berth, the hulls you owned
    // before stay moored, other fishermen fill the spare slots and the quay gains buildings tier by tier.
    // Harbour frame: x along the shore, water at z < 2.3, quay top y 0.35. Every model is optional.
    public partial class VoyageGame
    {
        public enum Berth { Slipway, Pontoon, FishQuay, OuterWharf }
        public static Berth BerthFor(int hull) => hull switch { 0 => Berth.Slipway, 1 => Berth.Pontoon, 2 or 3 => Berth.FishQuay, _ => Berth.OuterWharf };

        const float HarbourQuayTop = .35f, QuayFace = 2.3f;
        public static readonly Vector2 HarbourBasin = new(-2.5f, -7.5f), HarbourMouth = new(-6.5f, -13.5f), HarbourOutside = new(-6.5f, -25f);

        // Slot 0 is the captain's. Bow-in berths (slipway, pontoon) point the bow at the land.
        static Vector2[] BerthSlots(Berth berth, float beam) => berth switch
        {
            Berth.Slipway => new[] { new Vector2(-27.35f, -1.8f), new Vector2(-22.65f, -1.8f) },
            Berth.Pontoon => new[] { new Vector2(-10.25f, -6.5f), new Vector2(-15.75f, -1.6f) },
            Berth.FishQuay => new[] { new Vector2(1.5f, QuayFace - .25f - beam / 2), new Vector2(12.5f, QuayFace - .25f - beam / 2) },
            _ => new[] { new Vector2(12.4f, -10.6f + .9f + .55f + beam / 2), new Vector2(24.2f, -10.6f + .9f + .55f + beam / 2) },
        };
        static bool BowIn(Berth berth) => berth is Berth.Slipway or Berth.Pontoon;
        // Away from the dock, toward open basin water.
        static Vector2 BerthAway(Berth berth) => berth switch { Berth.FishQuay => Vector2.down, Berth.OuterWharf => Vector2.up, _ => Vector2.down };

        static readonly string[][] OtherFishermen =
        {
            new[] { "Rowboat_VariantGreen", "Rowboat_VariantRed" },
            new[] { "Skiff_VariantBlue" },
            new[] { "CompactFisherV1_VariantRed", "PrepFisherV1_VariantGreen" },
            new[] { "Tier5DeepLines103_VariantBlue" },
        };

        // Where the captain's boat lies in the harbour, and which way its bow points (set when it docks).
        public Vector2 HarbourSlot => BerthSlots(BerthFor(State.Hull), State.HullDef.Height * State.HullDef.CellSize)[0];
        Vector2 dockBow;
        Vector2 DockBow => dockBow != Vector2.zero ? dockBow : BowIn(BerthFor(State.Hull)) ? Vector2.up : Vector2.left;
        int harbourSignature = -1;

        // Yaw that points the hull's bow along dir (x, z); the models' bow is local -X.
        float YawFor(Vector2 dir) => Mathf.Atan2(-dir.y * bowSign, dir.x * bowSign) * Mathf.Rad2Deg;
        void PlaceAtBerth()
        {
            var c = State.HullDef.Center;
            travelOffset = new Vector3(HarbourSlot.x - c.x, 0, HarbourSlot.y - c.z);
            travelYaw = YawFor(DockBow); travelWake = 0;
        }

        // Camera focus and size that keep the berth and the buildings serving it in frame.
        (Vector3 focus, float size) HarbourFraming() => BerthFor(State.Hull) switch
        {
            Berth.Slipway => (new Vector3(-21.5f, 0, 2.5f), 6.2f),
            Berth.Pontoon => (new Vector3(-14f, 0, 0.5f), 7.2f),
            Berth.FishQuay => (new Vector3(0f, 0, 2.6f), IsPrepFisher ? 7.4f : 7f),
            _ => (new Vector3(9f, 0, -1.5f), 9f),
        };

        void BuildHarbour(Transform root, ArtLibrary lib, System.Func<float, float, float> R)
        {
            Shops.Clear();
            float q = HarbourQuayTop;
            int hull = State.Hull;
            var stone = Palette.Hex("8E8A80");
            GameObject M(string n) => lib?.M(n);
            GameObject Place(GameObject prefab, Vector3 p, float yaw = 0f, float scale = 1f)
                => prefab == null ? null : ArtLibrary.Spawn(prefab, root, p, Quaternion.Euler(0f, yaw, 0f), scale);

            // Ground: the quay and the town behind it, the beach at the west end.
            for (float x = -18f; x <= 26f; x += 4f)
            {
                var piece = x == 2f && lib?.QuayLadder != null ? lib.QuayLadder : lib?.Quay;
                if (piece != null) Place(piece, new Vector3(x, q, 3.3f));
            }
            if (lib?.Quay == null) Visuals.Box("QuayEdge", root, new Vector3(4f, q - .45f, 3.3f), new Vector3(48f, .9f, 2f), stone);
            Visuals.Box("QuayBack", root, new Vector3(-6f, q - .47f, 8.5f), new Vector3(72f, .9f, 8.5f), stone);
            // The beach stops at the slipway (x -29..-21) so the ramp and the rowboats on it never sink into sand.
            Visuals.Box("Beach", root, new Vector3(-35.5f, -.32f, 1.6f), new Vector3(13f, .7f, 6.6f), Palette.Hex("D9C393"));
            Visuals.Box("BeachBank", root, new Vector3(-31f, q - .45f, 4.6f), new Vector3(22f, .9f, 1.2f), Palette.Hex("C7B07E"));

            foreach (float x in new[] { -4.5f, -.6f, 3.4f, 7.5f, 14f, 18f })
                if (lib?.Bollard != null) Place(lib.Bollard, new Vector3(x, q, 2.6f));
            foreach (float x in new[] { -15.2f, -3.8f, 3.4f, 10.6f, 20f })
                if (lib?.LampPost != null) Place(lib.LampPost, new Vector3(x, q, 4.0f));

            // Slipway (beach, rowboats), sunk .4 m so it runs down from the sand and the rowboats float clear of it.
            if (Place(M("Slipway"), new Vector3(-25f, q - .4f, 2.4f)) == null)
            {
                var ramp = Visuals.Box("Slipway", root, new Vector3(-25f, -.25f, -.5f), new Vector3(8f, .2f, 7f), Palette.Hex("A9A49A"));
                ramp.transform.localRotation = Quaternion.Euler(-9f, 0, 0);
            }

            // East breakwater with the lighthouse at its head, west headland with the green beacon.
            void Wall(Vector3 p, float yaw)
            {
                if (Place(M("BreakwaterWall"), p, yaw) != null) return;
                Visuals.Box("BreakwaterCap", root, p + new Vector3(0, -.2f, 0), yaw == 0f ? new Vector3(4.1f, .9f, 1.8f) : new Vector3(1.8f, .9f, 4.1f), Palette.Hex("B5AFA3"));
                for (int i = 0; i < 3; i++)
                {
                    var rock = new[] { "BreakwaterRockA", "BreakwaterRockB", "BreakwaterRockC" }[i];
                    var side = Quaternion.Euler(0, yaw, 0) * new Vector3(-1.4f + i * 1.4f, 0, i % 2 == 0 ? -1.3f : 1.3f);
                    Place(M(rock), new Vector3(p.x + side.x, -.35f, p.z + side.z), R(0f, 360f), R(.9f, 1.3f));
                }
            }
            for (float z = 0f; z >= -8f; z -= 4f) Wall(new Vector3(28f, .6f, z), 90f);
            for (float x = 26f; x >= 10f; x -= 4f) Wall(new Vector3(x, .6f, -12f), 0f);
            if (Place(M("BreakwaterEnd"), new Vector3(6.5f, .6f, -12f)) == null) Wall(new Vector3(7f, .6f, -12f), 0f);
            if (lib?.Lighthouse != null) Place(lib.Lighthouse, new Vector3(5.6f, .6f, -12.3f), 200f);
            var headland = new[] { "BreakwaterRockA", "BreakwaterRockB", "BreakwaterRockC" };
            for (int i = 0; i <= 12; i++)
            {
                float t = i / 12f;
                var p = (1 - t) * (1 - t) * new Vector2(-40f, 1f) + 2 * t * (1 - t) * new Vector2(-34f, -16f) + t * t * new Vector2(-19f, -14f);
                Place(M(headland[i % 3]), new Vector3(p.x, -.35f, p.y), R(0f, 360f), R(1.3f, 1.9f));
            }
            if (Place(M("MouthBeacon"), new Vector3(-18.6f, .1f, -14f)) == null)
                Visuals.Prim(PrimitiveType.Cylinder, "MouthBeacon", root, new Vector3(-18.6f, .9f, -14f), new Vector3(.45f, .9f, .45f), Palette.Hex("3E9B5B"));

            // Outer wharf on the breakwater's inner face, built for the buoy fisher.
            if (hull >= 4)
                for (float x = 12f; x <= 24f; x += 4f)
                    if (Place(M("OuterWharf"), new Vector3(x, .6f, -10.6f)) == null)
                        Visuals.Box("OuterWharf", root, new Vector3(x, .35f, -10.6f), new Vector3(4.05f, .5f, 1.8f), Palette.Hex("C2BCB0"));

            // Pontoon with the fuel dock, from the skiff on.
            if (hull >= 1)
            {
                if (Place(M("PontoonGangway"), new Vector3(-13f, q, 2.4f)) == null)
                {
                    var g = Visuals.Box("Gangway", root, new Vector3(-13f, .15f, 1.2f), new Vector3(1.2f, .12f, 2.6f), Palette.DeckWoodDark);
                    g.transform.localRotation = Quaternion.Euler(-8f, 0, 0);
                }
                foreach (float z in new[] { -1.5f, -5.5f })
                    if (Place(M("PontoonSegment"), new Vector3(-13f, 0f, z)) == null)
                        Visuals.Box("Pontoon", root, new Vector3(-13f, -.1f, z), new Vector3(2f, .22f, 4f), Palette.Hex("B98F5E"));
                if (Place(M("FuelDock"), new Vector3(-13f, 0f, -8.6f)) == null)
                {
                    Visuals.Box("FuelFloat", root, new Vector3(-13f, -.1f, -8.6f), new Vector3(2f, .22f, 2f), Palette.Hex("B98F5E"));
                    Visuals.Box("FuelPump", root, new Vector3(-13f, .45f, -8.9f), new Vector3(.45f, .9f, .35f), Palette.Accent);
                }
            }

            // Buildings: what you start with, then what each tier adds. The tab each one hosts gets a bubble.
            void Host(HudTab tab, Vector3 p, float height)
            {
                var anchor = new GameObject($"{tab} bubble").transform;
                anchor.SetParent(root, false);
                anchor.localPosition = p + Vector3.up * (height + .6f);
                Shops.Add((anchor, tab));
            }
            void Sign(string text, Vector3 p, float y)
            {
                var board = Visuals.Box("Sign", root, new Vector3(p.x, q + y, p.z), new Vector3(Mathf.Max(1.3f, text.Length * .17f), .42f, .06f), Palette.HullNavy);
                var label = Visuals.Label("SignText", board.transform.parent, new Vector3(p.x, q + y - .13f, p.z - .05f), .032f);
                label.text = text; label.color = Palette.Cream; label.fontStyle = FontStyle.Bold;
                label.transform.localRotation = Quaternion.identity;
            }
            float Building(string model, Vector3 p, Vector3 fallback, Color wall)
            {
                var made = Place(M(model), p, 180f);
                if (made != null) return ModelHeight(made);
                Visuals.Box(model, root, p + Vector3.up * fallback.y / 2, fallback, wall);
                var roof = Visuals.Box(model + "Roof", root, p + Vector3.up * fallback.y, new Vector3(fallback.x + .1f, .5f, fallback.z + .2f), Palette.HullNavy);
                return fallback.y + .5f;
            }
            float House(bool a, string front, Vector3 p)
            {
                var house = a ? lib?.HouseA : lib?.HouseB;
                float height = 3.8f;
                if (house != null) Place(house, p, 180f, .95f);
                else Visuals.Box("House", root, p + Vector3.up * 1.3f, new Vector3(3f, 2.6f, 2.4f), Palette.Hex("E9D8B4"));
                var made = Place(M(front), new Vector3(p.x, q, 4.95f));
                return made != null ? Mathf.Max(height, ModelHeight(made) + .35f) : height;
            }

            var stall = new Vector3(-21.5f, q, 5.0f);
            var stallMade = Place(M("MarketStall") ?? M("MarketStallAwning"), stall, 180f);
            float stallH = stallMade != null ? ModelHeight(stallMade) : 2.2f;
            if (stallMade == null) Visuals.Box("MarketStall", root, stall + Vector3.up * 1f, new Vector3(2.4f, 2f, 1.4f), Palette.Hex("E9D8B4"));
            Place(M("FishCrate"), stall + new Vector3(1.5f, 0, -.8f), 12f);
            Place(M("FishCrate"), stall + new Vector3(1.7f, .335f, -.75f), -8f);
            Place(M("NPC_Fishmonger"), stall + new Vector3(.2f, 0, -.9f), 180f);

            var hut = new Vector3(-17.5f, q, 6.0f);
            float hutH = Building("HarbourMasterHut", hut, new Vector3(2.5f, 2.4f, 2f), Palette.Hex("C9DDE0"));
            Place(M("NPC_HarbourMaster"), hut + new Vector3(-1.6f, 0, -1.7f), 160f);
            var board = new Vector3(-15.6f, q, 4.6f);
            float boardH = Building("NoticeBoard", board, new Vector3(2f, 1.9f, .25f), Palette.DeckWoodDark);
            var shed = new Vector3(-29f, q, 6.0f);
            float shedH = Building("SuppliesShed", shed, new Vector3(3f, 2.4f, 2.5f), Palette.Hex("D9E3C5"));
            Sign("SUPPLIES", shed + new Vector3(0, 0, -1.4f), shedH + .1f);

            if (hull >= 1)
            {
                var yard = new Vector3(-34f, q, 6.5f);
                Building(M("BoatyardShed") != null ? "BoatyardShed" : "Shed_Shipyard", yard, new Vector3(5f, 3.2f, 4f), Palette.Hex("B98F5E"));
                if (Place(M("BoatCradle"), new Vector3(-34f, .05f, 2.5f)) == null)
                    for (int i = -1; i <= 1; i++) Visuals.Box("CradleBlock", root, new Vector3(-34f + i * 2f, .2f, 2.5f), new Vector3(.4f, .4f, 2f), Palette.DeckWoodDark);
            }
            float crewH = 0, chandleryH = 0, hallH = 0, officeH = 0;
            var crew = new Vector3(-10.4f, q, 6.6f); var chandlery = new Vector3(-6.8f, q, 6.6f);
            var hall = new Vector3(-2.6f, q, 6.6f); var office = new Vector3(1.0f, q, 6.6f);
            if (hull >= 1) { crewH = House(true, "ShopFront_CrewOffice", crew); Sign("CREW OFFICE", new Vector3(crew.x, q, 5.05f), 1.55f); }
            if (hull >= 1) { chandleryH = House(false, "ShopFront_Chandlery", chandlery); Sign("CHANDLERY", new Vector3(chandlery.x, q, 5.05f), 1.55f); }
            if (hull >= 2)
            {
                Building("NetLoft", new Vector3(9.0f, q, 6.6f), new Vector3(3f, 4.2f, 2.6f), Palette.Hex("B98F5E"));
                var crane = Place(M("QuayCrane"), new Vector3(16.5f, q, 4.2f), 180f);
                if (crane != null) { var jib = ArtLibrary.Find(crane, "Jib"); if (jib != null) jib.localRotation *= Quaternion.Euler(0, 25f, 0); }
                else
                {
                    Visuals.Box("CraneMast", root, new Vector3(16.5f, q + 2.4f, 4.2f), new Vector3(.35f, 4.8f, .35f), Palette.Accent);
                    Visuals.Box("CraneJib", root, new Vector3(15.4f, q + 4.7f, 3.6f), new Vector3(2.6f, .25f, .25f), Palette.Accent);
                }
            }
            if (hull >= 3)
            {
                hallH = House(true, "ShopFront_FishMarket", hall); Sign("FISH MARKET", new Vector3(hall.x, q, 5.05f), 1.55f);
                officeH = House(false, "ShopFront_HarbourMaster", office); Sign("HARBOUR MASTER", new Vector3(office.x, q, 5.05f), 1.55f);
                Building("IceHouse", new Vector3(5.0f, q, 6.4f), new Vector3(3.2f, 2.8f, 2.8f), Palette.Hex("DCE7EA"));
            }

            Host(HudTab.Market, hull >= 3 ? hall : stall, hull >= 3 ? hallH : stallH);
            Host(HudTab.HarbourMaster, hull >= 3 ? office : hut, hull >= 3 ? officeH : hutH);
            Host(HudTab.CrewOffice, hull >= 1 ? crew : board, hull >= 1 ? crewH : boardH);
            Host(HudTab.Chandlery, hull >= 1 ? chandlery : shed + Vector3.right * 1.2f, hull >= 1 ? chandleryH : shedH);
            Host(HudTab.Supplies, shed + Vector3.left * 1.2f, shedH);

            MoorBoats(root, lib);
            DressHarbour(root, lib, q, R);
        }

        // The captain's earlier hulls at their own berths, other fishermen in the spare slots.
        void MoorBoats(Transform root, ArtLibrary lib)
        {
            var used = new Dictionary<Berth, int>();
            int Next(Berth b) { used.TryGetValue(b, out int n); used[b] = n + 1; return n; }
            Next(BerthFor(State.Hull)); // slot 0: the captain's boat
            void Moor(GameObject prefab, HullDef def, Berth berth, int slot)
            {
                float beam = def.Height * def.CellSize;
                var slots = BerthSlots(berth, beam);
                if (prefab == null || slot >= slots.Length) return;
                var s = slots[slot];
                var go = ArtLibrary.Spawn(prefab, root, Vector3.zero, Quaternion.identity);
                Bounds Measure()
                {
                    var b = new Bounds(go.transform.position, Vector3.zero); bool any = false;
                    foreach (var r in go.GetComponentsInChildren<Renderer>()) { if (!any) b = r.bounds; else b.Encapsulate(r.bounds); any = true; }
                    return b;
                }
                // The hull kit points bows down -X; the older harbour variants lie along Z. Turn the long axis
                // across the berth for bow-in slots and along the dock for alongside ones, then centre on the slot.
                // Keep the importer's own rotation (the net fishers are Z-up sources) under the yaw.
                var import = prefab.transform.localRotation;
                go.transform.localRotation = import;
                var native = Measure();
                bool alongZ = native.size.z > native.size.x;
                go.transform.localRotation = Quaternion.Euler(0, BowIn(berth) == alongZ ? 0f : 90f, 0) * import;
                var bounds = Measure();
                var centre = root.InverseTransformPoint(bounds.center);
                go.transform.localPosition = new Vector3(s.x - centre.x, 0, s.y - centre.z);
                go.AddComponent<Floater>();
            }
            for (int h = 0; h < State.Hull; h++)
            {
                var def = GameData.Hulls[h];
                Moor(lib?.M(def.Model), def, BerthFor(h), Next(BerthFor(h)));
            }
            foreach (Berth berth in System.Enum.GetValues(typeof(Berth)))
            {
                var names = OtherFishermen[(int)berth];
                var def = GameData.Hulls[berth switch { Berth.Slipway => 0, Berth.Pontoon => 1, Berth.FishQuay => 2, _ => 4 }];
                for (int i = 0; i < names.Length; i++)
                {
                    int slot = Next(berth);
                    var prefab = lib?.M(names[i]) ?? (berth is Berth.Slipway or Berth.Pontoon ? null : lib?.M(def.Model));
                    Moor(prefab, def, berth, slot);
                }
            }
        }

        int HarbourSignatureNow => State.Hull;
        void SyncHarbourScenery()
        {
            if (CurrentMode != Mode.Harbour || harbourSignature == HarbourSignatureNow) return;
            harbourSignature = HarbourSignatureNow;
            dockBow = Vector2.zero;
            if (scenery != null) Visuals.Kill(scenery.gameObject);
            scenery = BuildScenery(-1);
        }
    }
}

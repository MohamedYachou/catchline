using System.Collections.Generic;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool IsNetFisher => State != null && State.Hull >= 2;
        Transform netModelRoot;
        Quaternion compactLidRest;
        public int CompactWalkableTiles { get; private set; }

        void FitCompactFisher(GameObject model, GameObject prefab)
        {
            // Keep the importer's source-Z-up conversion exactly once.
            model.transform.localRotation = Quaternion.Euler(0, -90, 0) * prefab.transform.localRotation;
            model.transform.localScale = prefab.transform.localScale;
            netModelRoot = model.transform;
            foreach (var t in model.GetComponentsInChildren<Transform>())
                if (t.name.StartsWith("RodVisual_")) t.gameObject.SetActive(false);
            compactLidRest = ArtLibrary.Find(model, "HoldLid")?.localRotation ?? Quaternion.identity;
            if (IsPrepFisher) ConfigurePrepFisher(model);
            if (IsTier5) ConfigureTier5(model);
            BuildSecondNetModuleVisual(model);
            FitCompactDeck(model);
        }

        // Rasterize the delivered mesh at the artist's three body-clearance heights.
        // This deliberately includes the hatch even while its lid is animated open:
        // crew route around the real opening, never across it.
        void FitCompactDeck(GameObject model)
        {
            var segments = new List<(Vector2 a, Vector2 b)>();
            foreach (var mf in model.GetComponentsInChildren<MeshFilter>())
            {
                var mesh = mf.sharedMesh;
                if (mesh == null || !mf.gameObject.activeInHierarchy) continue;
                var matrix = Boat.worldToLocalMatrix * mf.transform.localToWorldMatrix;
                var vertices = mesh.vertices;
                for (int i = 0; i < vertices.Length; i++) vertices[i] = matrix.MultiplyPoint3x4(vertices[i]);
                var tris = mesh.triangles;
                foreach (float height in new[] { .20f, .55f, .95f })
                    for (int i = 0; i < tris.Length; i += 3)
                    {
                        var points = new List<Vector2>(3);
                        for (int edge = 0; edge < 3; edge++)
                        {
                            var a = vertices[tris[i + edge]];
                            var b = vertices[tris[i + (edge + 1) % 3]];
                            if ((a.y < height) == (b.y < height) || Mathf.Abs(a.y - b.y) < .00001f) continue;
                            var p = Vector3.Lerp(a, b, (height - a.y) / (b.y - a.y));
                            points.Add(new Vector2(p.x, p.z));
                        }
                        if (points.Count >= 2) segments.Add((points[0], points[1]));
                    }
            }
            CompactWalkableTiles = 0;
            for (int y = 0; y < Grid.Height; y++)
                for (int x = 0; x < Grid.Width; x++)
                {
                    var tile = new Vector2Int(x, y);
                    var local = Grid.GetLocal(tile);
                    var point = new Vector2(local.x, local.z);
                    bool blocked = segments.Any(s => SegmentDistance(point, s.a, s.b) < .28f);
                    // Hold opening below the first body-height slice.
                    var native = new Vector2(State.HullDef.Center.z - local.z, State.HullDef.Center.x - local.x);
                    if (!IsPrepFisher && native.x > -.97f - .28f && native.x < -.33f + .28f && native.y > -1.13f - .28f && native.y < -.37f + .28f) blocked = true;
                    // The low net basket sits below the body slices too.
                    var basket = NetBasketLocal;
                    var nearBasket = new Vector2(Mathf.Clamp(local.x, basket.x - .18f, basket.x + .18f), Mathf.Clamp(local.z, basket.z - .24f, basket.z + .24f));
                    if (Vector2.Distance(point, nearBasket) < .28f) blocked = true;
                    if(IsTier5 && SecondNetActive)
                    {
                        var sideBasket=SecondNetBasketLocal;
                        var nearSide=new Vector2(Mathf.Clamp(local.x,sideBasket.x-.18f,sideBasket.x+.18f),Mathf.Clamp(local.z,sideBasket.z-.24f,sideBasket.z+.24f));
                        if(Vector2.Distance(point,nearSide)<.28f)blocked=true;
                    }
                    if (blocked) Grid.Block(new RectInt(x, y, 1, 1));
                    else CompactWalkableTiles++;
                }
        }

        static float SegmentDistance(Vector2 p, Vector2 a, Vector2 b)
        {
            var d = b - a;
            return Vector2.Distance(p, a + d * Mathf.Clamp01(Vector2.Dot(p - a, d) / Mathf.Max(.000001f, d.sqrMagnitude)));
        }

        public bool SetDeckhandWork(CrewMember crew, DeckhandWork preference)
        {
            if (!IsNetFisher || crew == null || crew.Role != CrewRole.Deckhand || !State.Crew.Contains(crew)) return false;
            if (preference == DeckhandWork.Prep && (!IsPrepFisher || crew.WorkPreference != DeckhandWork.Prep
                && State.Crew.Count(c => c.WorkPreference == DeckhandWork.Prep && c.Role == CrewRole.Deckhand) >= 2)) return false;
            crew.WorkPreference = preference; forecastSignature=flowCrewSignature=null;
            // Complete any fish already in hand. Release a walking/timed job safely;
            // Person cancellation also releases fish, bait and winch claims.
            var person = People.FirstOrDefault(p => p.Contract == crew);
            person?.Stop();
            if (preference != DeckhandWork.Nets) netAssignments.Remove(crew);
            if (person != null && preference != DeckhandWork.Prep) prepStations.Remove(person);
            SaveGame();
            return true;
        }

        public bool CanCaptainNet => CurrentMode == Mode.Fishing && AtFishingGround && Captain.Idle && Captain.Carrying == null
            && (Manning == null || Manning.State is not (RodState.Reeling or RodState.Flying))
            && !NetUnloadActive && (Net == NetState.Ready || Net == NetState.Stowed && (NetBasketBlocked || State.ActiveNetStock > 0) && !HoldFull);

        public bool CaptainNetAction()
        {
            if (!CanCaptainNet || Net is not (NetState.Stowed or NetState.Ready)) return false;
            // A baited/waiting rod stays in its holder; returning to Watch can resume it.
            var oldRod = Manning;
            bool oldCastChoice = AwaitingCast;
            Manning = null;
            AwaitingCast = false;
            if (Net == NetState.Stowed && NetBasketBlocked) { BeginNetUnload(Captain); return true; }
            bool started = Net == NetState.Ready ? HaulNet() : SetNet();
            if (!started) { Manning = oldRod; AwaitingCast = oldCastChoice; }
            return started;
        }

        public bool TrialCompactFisher()
        {
            if (!SessionOnly || CurrentMode != Mode.Harbour || State.Hull == 2) return false;
            State.Hull = 2;
            // A layout-trial downgrade releases the extra temporary trial berth.
            while (State.CrewCount > State.HullDef.CrewCap && State.ExtraCrew.Count > 0)
                State.ExtraCrew.RemoveAt(State.ExtraCrew.Count - 1);
            State.Fuel = State.FuelCapacity;
            State.FoodMinutes = State.FoodCapacity;
            State.Coins = Mathf.Max(State.Coins, 200); // Explicit isolated trial budget, not progression economy.
            State.EnsureCrewRoleOffers();
            RebuildBoat();
            Toast("Compact fisher trial. Hire any three crew at the Crew Office; choose Fish or Nets for each deckhand.");
            return true;
        }

        // Explicit opt-in launch fixture. Never reads or writes the player's save.
        public bool StartNetBoatTrial()
        {
            if (!SessionOnly) return false;
            NewGame();
            TrialCompactFisher();
            State.Coins = 1000;
            foreach (var role in new[] { CrewRole.Deckhand, CrewRole.Fisherman, CrewRole.Fisherman })
            {
                State.EnsureCrewRoleOffers();
                State.Hire(State.Board.First(c => c.Role == role));
            }
            State.Coins = 200;
            State.Bait = 60;
            State.FoodMinutes = State.FoodCapacity;
            SyncCrew();
            showTitle = paused = showSettings = panelOpen = captureFreeze = netOrdersOpen = false;
            ActiveSpot = SelectedSpot = 0;
            voyageStart = SimTime;
            Showcase(0, 0);
            toastUntil = 0;
            return true;
        }

        public bool StartCrewMixTrial()
        {
            if (!SessionOnly) return false;
            NewGame();
            if (!TrialCompactFisher()) return false;
            State.Coins = 1000;
            State.Bait = 60;
            State.DeepNetUses.Clear();
            State.DeepNetUses.AddRange(new[] { 3, 3 });
            State.SelectedNet = NetKind.Deep;
            State.EnsureCrewRoleOffers();
            SyncCrew();
            showTitle = paused = showSettings = captureFreeze = netOrdersOpen = false;
            ActiveSpot = SelectedSpot = 0;
            departureReady = false;
            toastUntil = 0f;
            OpenShop(HudTab.CrewOffice);
            Toast("Hire any three crew. Contracts expire, but both roles remain available.");
            RefreshInterface();
            return true;
        }
    }
}

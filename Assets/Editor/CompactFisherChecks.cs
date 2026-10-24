using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class CompactFisherChecks
    {
        const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool pass, string why) { if (!pass) throw new Exception("Compact fisher check failed: " + why); }
        static object Call(VoyageGame game, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Private).Invoke(game, args);
        static void Field(VoyageGame game, string name, object value) => typeof(VoyageGame).GetField(name, Private).SetValue(game, value);
        static void Property(VoyageGame game, string name, object value) => typeof(VoyageGame).GetProperty(name).GetSetMethod(true).Invoke(game, new[] { value });
        static VoyageGame Fixture()
        {
            var game = new GameObject("Isolated compact fisher").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build(); Field(game, "showTitle", false);
            Check(game.TrialCompactFisher(), "trial accessible from harbour");
            return game;
        }
        static void Crew(VoyageGame game, params CrewRole[] roles)
        {
            game.State.Deckhand = null; game.State.ExtraCrew.Clear(); game.SyncCrew();
            game.State.Coins = 1000;
            foreach (var role in roles)
            {
                game.State.EnsureCrewRoleOffers();
                Check(game.State.Hire(game.State.Board.First(c => c.Role == role)), "hire " + role);
            }
            game.SyncCrew();
        }
        static void Fishing(VoyageGame game)
        {
            Property(game, "CurrentMode", VoyageGame.Mode.Fishing);
            Property(game, "ActiveSpot", 0);
            Field(game, "panelOpen", false);
            game.State.Bait = 200; game.State.FoodMinutes = 24;
        }
        static void Work(Person p)
        { for (int i = 0; i < 1000 && !p.Idle; i++) p.Tick(.05f, Quaternion.identity); }

        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = Fixture();
            var hull = game.State.HullDef;
            Check(GameData.Hulls[0].Model == "Rowboat" && GameData.Hulls[1].Model == "Skiff", "old saved hull IDs preserved");
            Check(JsonUtility.FromJson<CrewMember>("{\"Role\":0}").WorkPreference == DeckhandWork.Fish, "old crew saves default to Fish duty");
            Check(game.Grid.CellSize == .1f && game.Rods.Count == 3 && hull.CrewCap == 3, "physical grid/three rods/three hired berths");
            var model = game.Boat.GetComponentsInChildren<Transform>().First(t => t.name == "CompactFisherV1");
            var mesh = model.GetComponentsInChildren<MeshFilter>().First(m => m.name == "Hull");
            var points = mesh.sharedMesh.vertices.Select(v => game.Boat.InverseTransformPoint(mesh.transform.TransformPoint(v))).ToArray();
            var size = new Vector3(points.Max(v => v.x) - points.Min(v => v.x), points.Max(v => v.y) - points.Min(v => v.y), points.Max(v => v.z) - points.Min(v => v.z));
            Debug.Log($"[Catchline] Compact native hull metres {size}; walkable {game.CompactWalkableTiles}");
            Check(Mathf.Abs(size.x - 5.4f) < .1f && Mathf.Abs(size.z - 2.8f) < .1f && size.y < 1.5f, "real model upright at approved physical size");
            for (int i = 0; i < 3; i++)
            {
                var socket = model.GetComponentsInChildren<Transform>().First(t => t.name == "RodSocket_" + (i + 1));
                var socketPos = game.Boat.InverseTransformPoint(socket.position);
                Check(Vector3.Distance(socketPos, hull.RodBases[i]) < .06f, "actual rod socket " + i + " " + socketPos);
            }
            var jobs = new[] { hull.Seat, hull.HoldAccess, hull.NetAccess }.Concat(hull.CrewRest).Concat(hull.RodTiles).ToArray();
            Directory.CreateDirectory(Path.GetFullPath("Logs/net010"));
            File.WriteAllLines("Logs/net010/deck-grid.txt", Enumerable.Range(0, game.Grid.Height).Reverse().Select(y => string.Concat(Enumerable.Range(0, game.Grid.Width).Select(x => jobs.Contains(new Vector2Int(x, y)) ? 'J' : game.Grid.IsBlocked(new Vector2Int(x, y)) ? '#' : '.'))));
            foreach (var a in jobs)
            {
                Check(!game.Grid.IsBlocked(a), "job tile walkable: " + a);
                foreach (var b in jobs) Check(game.Grid.FindPath(a, b) != null, "actual deck connects " + a + " to " + b);
            }
            Check(game.Boat.GetComponentsInChildren<Transform>().Count(t => t.name.StartsWith("RodVisual_")) == 0, "display-only duplicate rods hidden");
            var lid = model.GetComponentsInChildren<Transform>().First(t => t.name == "HoldLid");
            var lidMesh = lid.GetComponent<MeshFilter>();
            var lidRest = lid.localRotation;
            float closedY = lidMesh.sharedMesh.vertices.Average(v => lidMesh.transform.TransformPoint(v).y);
            lid.localRotation = lidRest * Quaternion.Euler(90, 0, 0);
            Check(lidMesh.sharedMesh.vertices.Average(v => lidMesh.transform.TransformPoint(v).y) > closedY + .2f, "native hinged lid opens upward");
            lid.localRotation = lidRest;
            var propeller = model.GetComponentsInChildren<Transform>().First(t => t.name == "Propeller");
            Check(Mathf.Abs(Vector3.Dot(propeller.TransformDirection(Vector3.up), game.Boat.right)) > .99f, "source-Y propeller shaft matches native stern axis");
            Crew(game, CrewRole.Deckhand, CrewRole.Fisherman, CrewRole.Fisherman);
            Fishing(game);
            game.CommandRod(game.Rods[0]);
            int activeHandSteps = 0, maxDeck = 0;
            for (int i = 0; i < 2400; i++)
            {
                if (game.MinigameRod?.State == RodState.Bite) game.StrikeTap();
                if (game.AwaitingCast) game.ThrowAgain();
                game.Tick(.05f);
                if (game.Hand.Walking || game.Hand.Busy && game.Hand.BusyLabel != "Resting") activeHandSteps++;
                maxDeck = Mathf.Max(maxDeck, game.OnDeck.Count);
                foreach (var p in new[] { game.Captain, game.Hand }.Concat(game.ExtraPeople))
                    Check(!game.Grid.IsBlocked(p.Tile), "crew stays on clear deck: " + p.Name + " at " + p.Tile);
            }
            Check(game.Rods.Count(r => r.Fisher != null) == 2, "two hired fishers run distinct rods");
            Check(game.Stats.Landed > 8 && game.Cooler.Count > 4, "four real actors fish and carry");
            Debug.Log($"[Catchline] Compact 120s crew trace landed={game.Stats.Landed} held={game.Cooler.Count} deck={game.OnDeck.Count} peakDeck={maxDeck} lost={game.Stats.Lost} handActive={activeHandSteps / 24f:0}%");
            // Save through an explicit scratch filename, never the player's persistent path.
            var hand = game.State.Deckhand;
            Check(game.SetDeckhandWork(hand, DeckhandWork.Nets), "net work preference accepted");
            string save = Path.GetFullPath("Logs/net010/preference-save.json");
            Directory.CreateDirectory(Path.GetDirectoryName(save)); game.State.Save(save);
            var loaded = GameState.Load(save);
            Check(loaded.Hull == 2 && loaded.Deckhand.WorkPreference == DeckhandWork.Nets, "new hull and duty round-trip save");
            // Isolate the work-allocation checks from any rod/reel left in the timed trace.
            foreach (var p in new[] { game.Captain, game.Hand }.Concat(game.ExtraPeople)) p.Stop();
            Property(game, "Manning", null);
            game.Cooler.Clear();
            game.Hand.Stop();
            if (game.Hand.Carrying != null) Call(game, "TryStow", game.Hand);
            Call(game, "ResetNet");
            Call(game, "HandThink", game.Hand);
            Work(game.Hand);
            Check(game.Net == VoyageGame.NetState.Soaking, "net-priority hand sets autonomously");
            Call(game, "TickNet", GameData.ShallowNetSoakSeconds);
            // Isolate this success-path allocation check from the separate20% tear regression.
            // Seed0's first roll(.726...) is inside the safe band for a completed cycle.
            var safeRoll = new System.Random(0).NextDouble();
            Check(safeRoll >= .2 && safeRoll < .8, "known deterministic safe worker seed");
            game.State.Rng = new System.Random(0);
            Call(game, "HandThink", game.Hand); Work(game.Hand);
            Check(game.NetBasketCount > 0, "net-priority hand hauls the weight-budget catch into basket on safe cycle");
            var basket = game.OnDeck.Where(f => f.FromNetBasket).ToArray();
            Call(game, "TickDeckFish", 120f);
            Check(basket.All(f => game.OnDeck.Contains(f)), "basket cannot flop away");
            foreach (var f in basket) Check(game.CanCarry(f), "captain can collect while hired hand is available");
            Call(game, "RequestHeadHome");
            Check(!(bool)typeof(VoyageGame).GetField("confirmHeadHome", Private).GetValue(game), "stowed net and fitting catch can return directly");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            game = Fixture(); Fishing(game);
            Property(game, "Manning", game.Rods[0]);
            for (int i = 0; i < game.State.CoolerCapacity; i++) game.Cooler.Add(new CaughtFish { Kg = 1f });
            Check(!game.CaptainNetAction() && game.Manning == game.Rods[0], "failed full-hold action preserves captain rod");
            game.Cooler.Clear(); Property(game, "Manning", null);
            Check(game.SetNet(), "set for departure protection"); Work(game.Captain); NetHaulChecks.FinishCaptainSet(game);
            Call(game, "RequestHeadHome");
            Check((bool)typeof(VoyageGame).GetField("confirmHeadHome", Private).GetValue(game), "deployed net prompts before abandoning");
            Call(game, "CancelHeadHome");
            Check(game.Net == VoyageGame.NetState.Soaking && game.CurrentMode == VoyageGame.Mode.Fishing, "cancel preserves deployed net");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            foreach (var role in new[] { CrewRole.Fisherman, CrewRole.Deckhand })
            {
                game = Fixture(); Crew(game, role, role, role); Fishing(game);
                for (int i = 0; i < 200; i++) game.Tick(.05f);
                Check(game.State.CrewCount == 3 && game.ExtraPeople.Count + (game.Hand != null ? 1 : 0) == 3, "three-" + role + " composition");
                if (role == CrewRole.Fisherman) Check(game.Rods.All(r => r.Fisher != null), "three fishers use all rods; captain can do logistics");
                game.HeadHome();
                Check(game.CurrentMode == VoyageGame.Mode.SailingHome, "compact boat begins return with full crew");
                for (int i = 0; i < 400 && game.CurrentMode != VoyageGame.Mode.Harbour; i++) game.Tick(.05f);
                Check(game.CurrentMode == VoyageGame.Mode.Harbour, "compact boat docks successfully");
                Check(game.SailBlocker() == null, "compact boat ready to launch with included fuel");
                game.SetSail();
                for (int i = 0; i < 400 && game.CurrentMode != VoyageGame.Mode.Fishing; i++) game.Tick(.05f);
                Check(game.CurrentMode == VoyageGame.Mode.Fishing, "compact boat reaches fishing ground again");
                UnityEngine.Object.DestroyImmediate(game.gameObject);
            }
            Debug.Log("[Catchline] COMPACT FISHER CHECKS PASSED");
        }

        public static void ValidateCaptureAndBuildPreview()
        {
            Capture();
            ReferenceHudChecks.Capture();
            FirstVoyageChecks.BuildPreview();
        }

        public static void Capture()
        {
            Run(); NetChoiceChecks.Run();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = Fixture(); Crew(game, CrewRole.Deckhand, CrewRole.Fisherman, CrewRole.Fisherman);
            game.Showcase(0, 0); Fishing(game); game.Tick(.1f);
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic);
            string folder = Path.GetFullPath("Logs/net010");
            void Shot(string name, int width, int height) => shot.Invoke(null, new object[] { game, "../net010/" + Path.GetFileNameWithoutExtension(name), width, height, 1f });
            Shot("compact-desktop.png", 1440, 900); Shot("compact-phone.png", 844, 390);
            Check(game.InvokeInterface("net/orders"), "native crew orders button bound");
            Shot("duties-desktop.png", 1440, 900); Shot("duties-phone.png", 844, 390);
            Check(game.InvokeInterface("net/orders/0/nets"), "native Nets choice bound");
            Check(game.State.Deckhand.WorkPreference == DeckhandWork.Nets, "native choice changes real scheduler");
            Check(game.InvokeInterface("net/orders/close"), "close duties");
            game.SetDeckhandWork(game.State.Deckhand, DeckhandWork.Fish);
            game.Captain.Stop();
            Field(game, "toastUntil", 0f);
            game.PrepareInterface(1440, 900);
            Check(game.InvokeInterface("net"), "captain net action bound"); Work(game.Captain); NetHaulChecks.FinishCaptainSet(game);
            Check(game.Net == VoyageGame.NetState.Soaking, "native set starts real soak");
            Shot("net-soaking-desktop.png", 1440, 900);
            Call(game, "TickNet", GameData.ShallowNetSoakSeconds);
            Shot("net-ready-phone.png", 844, 390);
            Check(game.InvokeInterface("net"), "captain haul action bound"); NetHaulChecks.FinishCaptainHaul(game);
            Call(game, "TickDeckFish", 1f);
            Shot("net-basket-desktop.png", 1440, 900); Shot("net-basket-phone.png", 844, 390);
            int secured = game.Cooler.Count;
            var fish = game.OnDeck.First(f => f.FromNetBasket);
            game.CommandCarry(fish); Work(game.Captain);
            Check(game.Cooler.Count == secured + 1 && !game.OnDeck.Contains(fish), "captain carries basket catch into hold");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] Snapshot written to " + folder);
        }
    }
}

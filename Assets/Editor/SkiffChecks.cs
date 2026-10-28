using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Scratch-project regression check; never uses the player's actual save.
    public static class SkiffChecks
    {
        static void Check(bool ok, string message)
        {
            if (!ok) throw new Exception("[Catchline] Skiff check failed: " + message);
        }

        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Skiff regression").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.AutoPlay = true;
            game.Build();
            var state = game.State;
            state.Coins = GameData.SkiffCost;
            Check(!game.RefitSkiff() && state.Coins == GameData.SkiffCost, "goal blocks refit without spending");
            state.BestVoyageFish = 16; state.BestVoyageKg = GameData.SkiffKgGoal;
            state.Coins = GameData.SkiffCost - 1;
            Check(!game.RefitSkiff() && state.Hull == 0, "fee blocks refit");
            state.Coins = GameData.SkiffCost;
            game.Rods[0].State = RodState.Ready;
            game.Rods[0].Squid = true;
            state.Owned.Add(UpgradeId.BigCooler);
            state.EquipTool(GameState.CaptainToolOwner, 0, state.AddTool(ToolKind.Rod, CardRarity.Gold).Uid);
            game.SyncUpgrades();
            Check(game.Rods[0].State == RodState.Ready && game.Rods[0].Squid, "visual upgrades preserve baited rods");
            Check(ArtLibrary.Find(game.Boat.gameObject, "BigCooler") != null && ArtLibrary.Find(game.Rods[0].Root.gameObject, "FishingRod_Carbon") != null, "purchased cooler and rod variants visible");
            Check(game.RefitSkiff() && state.Coins == 0 && state.Hull == 1, "refit spends once");
            Check(game.Rods[0].State == RodState.Ready && game.Rods[0].Squid, "refit preserves baited rods");
            Check(!game.RefitSkiff() && state.Coins == 0, "second refit rejected");
            Check(game.Grid.Width == state.HullDef.Width && game.Grid.Height == state.HullDef.Height, "skiff dimensions match hull data");
            Check(state.Has(UpgradeId.BigCooler) && state.CoolerCapacity == state.HullDef.Capacity * 1.5f, "skiff hold applies purchased cooler to hull capacity");
            Check(game.Rods.Count == 3 && game.Rods.TrueForAll(r => r.Unlocked), "three working rods");
            foreach (var rod in game.Rods)
                Check(game.Grid.FindPath(state.HullDef.Seat, rod.Tile) != null, "console-to-rod route");
            Check(game.Grid.FindPath(state.HullDef.Rest, state.HullDef.HoldAccess) != null, "deckhand-to-hold route");
            Check(game.Grid.IsBlocked(new Vector2Int(4, 2)) && game.Grid.IsBlocked(new Vector2Int(1, 1)), "console and hold blocked");
            var model = ArtLibrary.Get()?.M("Skiff");
            Check(model != null && ArtLibrary.Find(game.Boat.gameObject, "HoldLid") != null, "skiff asset and lid integrated");
            var library = ArtLibrary.Get();
            // Crew are the Quaternius human puppets animated by the Universal Animation Library (the captain
            // borrows Mira's puppet). The library ships far more than the old eleven blob clips.
            Check(library.CrewClips.Length >= 11, "crew animation library imported");
            var rig = ArtLibrary.Find(game.Captain.Root.gameObject, "mira") ?? ArtLibrary.Find(game.Captain.Root.gameObject, "CrewRig");
            var leg = ArtLibrary.Find(rig.gameObject, "thigh_l") ?? ArtLibrary.Find(rig.gameObject, "LeftUpLeg");
            var walk = library.CrewClips.Single(c => c.name.Split('|').Last() == "Walk_Loop");
            walk.SampleAnimation(rig.gameObject, .1f);
            var before = leg.localRotation;
            walk.SampleAnimation(rig.gameObject, .6f);
            Check(Quaternion.Angle(before, leg.localRotation) > 5f, "walk animation moves skinned rig in Unity");
            game.Tick(.2f);
            PrototypeTools.Render(game.Cam, Path.GetFullPath("Logs/skiff-harbour.png"), 1440, 900);

            string save = Path.GetFullPath("Logs/skiff-check-" + Guid.NewGuid().ToString("N") + ".json");
            Directory.CreateDirectory(Path.GetDirectoryName(save));
            try
            {
                state.Save(save);
                var loaded = GameState.Load(save);
                Check(loaded != null && loaded.Hull == 1 && loaded.Fuel == state.Fuel && loaded.BestVoyageFish == 16, "skiff save round trip");
                File.WriteAllText(save, "{\"Version\":1,\"Coins\":400,\"Bait\":15,\"Voyage\":3,\"FoodMinutes\":4,\"Owned\":[],\"Charts\":[],\"Board\":[],\"Offers\":[],\"Active\":[]}");
                loaded = GameState.Load(save);
                // SaveV2 accepts only CurrentVersion; pre-card saves are deliberately discarded.
                Check(loaded == null, "version1 rowboat save is rejected by the current save contract");
            }
            finally { if (File.Exists(save)) File.Delete(save); }

            game.SelectedSpot = 4;
            state.Fuel = 0;
            Check(game.SailBlocker() == "Buy fuel at Supplies", "empty tank blocks departure");
            state.Coins = GameData.FuelPackCost;
            Check(state.BuyFuel() && state.Coins == 0, "fuel purchase");
            float fuel = state.Fuel;
            float departure = game.SimTime;
            game.SetSail();
            Check(state.Fuel == fuel, "fuel burns with elapsed voyage time");
            // Prevent the autoplay bot from interfering during this targeted voyage.
            game.AutoPlay = false;
            Check(game.Leg == VoyageGame.TripLeg.HarbourOut, "skiff starts in the harbour lane");
            for (int n = 0; n < 4800 && !(game.CurrentMode == VoyageGame.Mode.Fishing && game.Leg == VoyageGame.TripLeg.None); n++) game.Tick(.05f);
            Check(game.CurrentMode == VoyageGame.Mode.Fishing && game.AtFishingGround, "skiff completes harbour, chart and sea travel");
            game.Tick(2f);
            PrototypeTools.Render(game.Cam, Path.GetFullPath("Logs/skiff-sea-desktop.png"), 1440, 900);
            PrototypeTools.Render(game.Cam, Path.GetFullPath("Logs/skiff-sea-phone.png"), 844, 390);
            Check(!game.RefitSkiff(), "refit rejected at sea");
            game.HeadHome();
            Check(Mathf.Abs(state.Fuel - (fuel - (game.SimTime - departure) / 60f)) < .002f && state.Fuel > 0,
                "elapsed voyage time consumes fuel with reserve remaining");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] SKIFF CHECKS PASSED: refit, models, routes, save migration, fuel and travel");
        }

        public static void Automation()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Automation regression").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.AutoPlay = true;
            game.Build();
            var s = game.State;
            s.Coins = 10000; s.BestVoyageFish = 16; s.BestVoyageKg = GameData.SkiffKgGoal;
            Check(game.RefitSkiff(), "automation refit");
            s.Board.Clear();
            var deckhand = new CrewMember { Name = "Test hand", Role = CrewRole.Deckhand, Grade = Grade.Hand, VoyagesLeft = 2 };
            var fisher = new CrewMember { Name = "Test fisherman", Role = CrewRole.Fisherman, Grade = Grade.Veteran, VoyagesLeft = 5 };
            var secondHand = new CrewMember { Name = "Test second hand", Role = CrewRole.Deckhand, Grade = Grade.Experienced, VoyagesLeft = 3 };
            s.Board.AddRange(new[] { deckhand, fisher, secondHand });
            // The skiff has two berths (deck berths, 48671cf1): a deckhand and a fisherman; the second hand finds it full.
            Check(s.Hire(deckhand) && s.Hire(fisher), "two role-aware hires");
            Check(!s.Hire(secondHand) && s.CrewCount == 2, "crew cap enforced");
            game.SyncCrew();
            Check(game.ExtraPeople.Count == 1 && game.Hand != null, "all hired crew built");
            // No save round trip here: hires off the board are legacy fixtures and session-only; the crew a save keeps are
            // cards (Deployment), covered by the card checks.
            s.FoodMinutes = 48f; s.Bait = 200;
            game.SelectedSpot = 4;
            game.SetSail();
            game.AutoPlay = false;
            // Sail out until the captain can work the net: travel time follows the day's route (Day v2), not a fixed 11 s.
            for (int i = 0; i < 400 && !game.CanWorkNet; i++) game.Tick(.25f);
            Check(game.SetNet(), $"captain can set net (mode {game.CurrentMode}, net {game.Net}, can work {game.CanWorkNet})");
            NetHaulChecks.FinishCaptainSet(game);
            Check(game.Net == VoyageGame.NetState.Soaking, "set action reaches soaking");
            PrototypeTools.Render(game.Cam, Path.GetFullPath("Logs/skiff-net-soaking.png"), 1440, 900);
            game.Tick(90f);
            Check(game.Net == VoyageGame.NetState.Ready && game.NetCatch > 0, "net soaks and catches");
            Check(game.Stats.Landed > 0 && game.Rods.Any(r => r.Fisher != null), "fisherman lands fish without captain taps");
            int landed = game.Stats.Landed, net = game.NetCatch;
            Check(game.HaulNet(), "one tap starts haul");
            NetHaulChecks.FinishCaptainHaul(game);
            Check(game.Net == VoyageGame.NetState.Stowed && game.Stats.Landed >= landed + net, "haul deposits net fish on deck");
            Check(game.OnDeck.Count > 0, "haul creates carrying backlog");
            Check(game.ExtraPeople.Where(p => p.Contract.Role == CrewRole.Fisherman).All(p => p.Carrying == null), "fishermen leave carrying to deckhands");
            game.Tick(2f);
            PrototypeTools.Render(game.Cam, Path.GetFullPath("Logs/skiff-net-desktop.png"), 1440, 900);
            PrototypeTools.Render(game.Cam, Path.GetFullPath("Logs/skiff-net-phone.png"), 844, 390);
            game.HeadHome();
            Check(game.Net == VoyageGame.NetState.Stowed && game.NetCatch == 0, "return clears net state");
            var sale = new SaleReport();
            s.EndVoyage(sale); s.EndVoyage(sale);
            Check(!s.Crew.Contains(deckhand) && s.Crew.Contains(fisher) && fisher.VoyagesLeft == 3, "contracts expire by voyage including extra crew");
            Debug.Log("[Catchline] SKIFF CHECKS PASSED: role hiring, cap, save, fisherman, net, backlog and contracts");
        }
    }
}

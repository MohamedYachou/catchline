using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.EditorTools
{
    // Camera renders of the lead's new views for review in the scratch editor (no UI: IMGUI and the overlay canvas are
    // not in a camera render). Batch: -executeMethod Catchline.EditorTools.LeadShots.Run ; CATCHLINE_SHOTS filters
    // the sets (harbour, intro, cage, trip). Images go to docs/screens/overnight/ in the main checkout.
    public static class LeadShots
    {
        const string Out = @"C:\Users\momoy\Projects\Catchline\docs\screens\overnight\";
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;

        public static void Run()
        {
            Directory.CreateDirectory(Out);
            ArtImport.BuildLibrary();
            var only = Environment.GetEnvironmentVariable("CATCHLINE_SHOTS");
            bool Want(string set) => string.IsNullOrEmpty(only) || only.Contains(set);
            if (Want("harbour")) Harbour();
            if (Want("intro")) Intro();
            if (Want("cage")) Cage();
            if (Want("trip")) Trip();
            if (Want("net")) Net();
            if (Want("gut")) Gut();
            if (Want("traffic")) Traffic();
            if (Want("town")) Town();
            if (Want("repair")) Repair();
            if (Want("dusk")) Dusk();
            if (Want("pots")) Pots();
            if (Want("chart")) Chart();
            if (Want("harbourui")) HarbourUi();
            if (Want("deckui")) DeckUi();
            if (Want("rod")) Rod();
            if (Want("crewui")) CrewUi();
            if (Want("abilitypop")) AbilityPop();
            Debug.Log("LEADSHOTS DONE " + Out);
        }

        // Crew office v2 at a fixed clock: garage, card panel, chests and their reveal, tools, renown and a rank-up.
        static void CrewUi()
        {
            var g = Game("Crew UI shot"); Rebuild(g, 4);
            var s = g.State;
            CardRoster.GrantUpToTier(s.Roster, s.Deployment, s.CardTier); s.EnsureCards();
            // Olaf and Tove have not joined: their offers show on the recruit page, Olaf's on his last (guaranteed) chest.
            s.Roster.RemoveAll(c => c.Id == "olaf" || c.Id == "tove"); s.Deployment.RemoveAll(id => id == "olaf" || id == "tove"); s.CrewChestsBought["olaf"] = 9; s.CrewChestsBought["dirk"] = 4;
            s.Tokens = 640; s.Coins = 25000; s.FocusCard = "noor";
            var noor = CardRoster.Find(s.Roster, "noor"); noor.Rarity = CardRarity.Blue; noor.Level = 12; noor.Blueprints = 1;
            var pim = CardRoster.Find(s.Roster, "pim"); if (pim != null) { pim.Level = 5; pim.Blueprints = 1; }
            var mira = CardRoster.Find(s.Roster, "mira"); if (mira != null) { mira.Rarity = CardRarity.Mythic; mira.Stars = 2; mira.Level = 30; }
            foreach (ToolKind k in new[] { ToolKind.Rod, ToolKind.Rod, ToolKind.Gloves, ToolKind.Gaff, ToolKind.Compass, ToolKind.Boots })
                s.AddTool(k, k == ToolKind.Gaff ? CardRarity.Purple : CardRarity.White);
            s.AddTool(ToolKind.Reel, CardRarity.Gold);
            s.GrantChest(ChestKind.Crate); s.GrantChest(ChestKind.Crate); s.GrantChest(ChestKind.CaptainsChest);
            var T = typeof(VoyageGame);
            void Set(string f, object v) => T.GetField(f, H).SetValue(g, v);
            void Clock(float t) => Set("cardUiClock", t);
            Set("panelOpen", true); Set("hudTab", VoyageGame.HudTab.CrewOffice); Clock(10);
            ShotUi(g, "crew-garage"); ShotUi(g, "crew-garage-phone", 844, 390);
            Set("cardPanelId", "noor"); ShotUi(g, "crew-card-noor"); ShotUi(g, "crew-card-noor-phone", 844, 390);
            Set("cardPanelId", "mira"); ShotUi(g, "crew-card-mira");
            Set("cardPanelId", null); Set("crewTab", 1); ShotUi(g, "crew-chests"); ShotUi(g, "crew-chests-phone", 844, 390);
            Clock(100); T.GetMethod("StartReveal", H, null, new[] { typeof(ChestKind) }, null).Invoke(g, new object[] { ChestKind.CaptainsChest });
            foreach (float t in new[] { .3f, .9f, 1.35f, 1.7f, 3.0f }) { Clock(100 + t); ShotUi(g, $"crew-reveal-{t:0.00}"); }
            Clock(103); var flip = T.GetMethod("FlipReveal", H); flip.Invoke(g, new object[] { 0, 0f }); flip.Invoke(g, new object[] { 1, 0f });
            Clock(103.17f); ShotUi(g, "crew-reveal-flipping");
            for (int i = 2; i < 8; i++) try { flip.Invoke(g, new object[] { i, 0f }); } catch { }
            Clock(104); ShotUi(g, "crew-reveal-open"); ShotUi(g, "crew-reveal-open-phone", 844, 390);
            T.GetMethod("CollectReveal", H).Invoke(g, null);
            Set("crewTab", 2); Clock(105); ShotUi(g, "crew-recruit"); ShotUi(g, "crew-recruit-phone", 844, 390);
            Clock(120); T.GetMethod("BuyCrewChestWithFx", H).Invoke(g, new object[] { "olaf" });
            foreach (float t in new[] { 1.0f, 1.7f }) { Clock(120 + t); ShotUi(g, $"crew-crewchest-{t:0.0}"); }
            Clock(123); for (int i = 0; i < 8; i++) try { flip.Invoke(g, new object[] { i, 0f }); } catch { }
            Clock(124); ShotUi(g, "crew-crewchest-open"); ShotUi(g, "crew-crewchest-open-phone", 844, 390);
            T.GetMethod("CollectReveal", H).Invoke(g, null); Clock(125); ShotUi(g, "crew-crewchest-joined");
            Set("cardPanelId", null);
            Set("crewTab", 3); Clock(110); ShotUi(g, "crew-tools"); ShotUi(g, "crew-tools-phone", 844, 390);
            Set("crewTab", 4); ShotUi(g, "crew-renown"); ShotUi(g, "crew-renown-phone", 844, 390);
            Set("crewTab", 0); noor.Level = noor.LevelCap; noor.Blueprints = 2; Clock(200);
            T.GetMethod("RankUpWithFx", H).Invoke(g, new object[] { "noor" });
            foreach (float t in new[] { .6f, 1.2f, 2.0f }) { Clock(200 + t); ShotUi(g, $"crew-rankup-{t:0.0}"); }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            WelcomeChest();
        }

        // Tutorial: the first boat, no crew yet, the welcome chest waiting with Mira.
        static void WelcomeChest()
        {
            var g = Game("Welcome chest shot"); Rebuild(g, 1);
            var s = g.State; s.Roster.Clear(); s.Deployment.Clear(); s.EnsureCards();
            var T = typeof(VoyageGame);
            void Set(string f, object v) => T.GetField(f, H).SetValue(g, v);
            void Clock(float t) => Set("cardUiClock", t);
            Set("panelOpen", true); Set("hudTab", VoyageGame.HudTab.CrewOffice); Set("crewTab", 1); Clock(10);
            ShotUi(g, "crew-welcome"); ShotUi(g, "crew-welcome-phone", 844, 390);
            Set("crewTab", 0); ShotUi(g, "crew-garage-empty");
            Set("crewTab", 1); Clock(20); T.GetMethod("StartReveal", H, null, new[] { typeof(ChestKind) }, null).Invoke(g, new object[] { ChestKind.Welcome });
            Clock(21.6f); ShotUi(g, "crew-welcome-reveal");
            var flip = T.GetMethod("FlipReveal", H); for (int i = 0; i < 4; i++) try { flip.Invoke(g, new object[] { i, 0f }); } catch { }
            Clock(23); ShotUi(g, "crew-welcome-open"); ShotUi(g, "crew-welcome-open-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        // Ability names floating over the crew at sea: every deployed card raised to Purple, its auto ability just fired.
        static void AbilityPop()
        {
            var g = Game("Ability pop shot"); g.StartTier5Trial();
            foreach (var c in g.State.Roster) if (c.Rarity < CardRarity.Purple) { c.Rarity = CardRarity.Purple; c.Level = 20; }
            for (int i = 0; i < 300; i++) g.Tick(.1f);
            var engine = g.Abilities;
            var fired = (System.Collections.Generic.Dictionary<string, float>)engine.GetType().GetField("fired", H).GetValue(engine);
            float i2 = 0;
            foreach (var id in g.State.Deployment) { fired[id + ".auto"] = engine.Time - .25f - i2; i2 += .3f; }
            ShotUi(g, "ability-pop"); ShotUi(g, "ability-pop-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static VoyageGame Game(string name)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject(name).AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            typeof(VoyageGame).GetField("showTitle", H).SetValue(g, false);
            return g;
        }

        static void Shot(VoyageGame g, string file, int width = 1440, int height = 900)
        {
            var rt = RenderTexture.GetTemporary(width, height, 24, RenderTextureFormat.ARGB32);
            var target = g.Cam.targetTexture; var active = RenderTexture.active;
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
            try
            {
                g.Cam.targetTexture = rt; g.Cam.aspect = width / (float)height;
                RenderPipeline.SubmitRenderRequest(g.Cam, new RenderPipeline.StandardRequest { destination = rt });
                RenderTexture.active = rt; texture.ReadPixels(new Rect(0, 0, width, height), 0, 0); texture.Apply();
                File.WriteAllBytes(Out + file + ".png", texture.EncodeToPNG());
            }
            finally { g.Cam.targetTexture = target; RenderTexture.active = active; RenderTexture.ReleaseTemporary(rt); UnityEngine.Object.DestroyImmediate(texture); }
        }

        // Scene plus the production HUD canvas, composited the way InterfaceChecks does it.
        static void ShotUi(VoyageGame g, string file, int width = 1440, int height = 900)
        {
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            var ui = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            var composite = new Material(Shader.Find("Hidden/Catchline/Coastal UI Composite"));
            var texture = new Texture2D(width, height, TextureFormat.RGB24, false);
            var previous = RenderTexture.active;
            try
            {
                g.Cam.targetTexture = rt; g.Cam.aspect = width / (float)height;
                g.PrepareInterface(width, height, 0);
                Canvas.ForceUpdateCanvases();
                RenderPipeline.SubmitRenderRequest(g.Cam, new RenderPipeline.StandardRequest { destination = rt });
                g.GetComponentInChildren<CoastalCanvas>().RenderCapture(ui);
                Graphics.Blit(ui, rt, composite);
                RenderTexture.active = rt; texture.ReadPixels(new Rect(0, 0, width, height), 0, 0); texture.Apply();
                File.WriteAllBytes(Out + file + ".png", texture.EncodeToPNG());
            }
            finally
            {
                RenderTexture.active = previous; g.Cam.targetTexture = null;
                UnityEngine.Object.DestroyImmediate(texture); UnityEngine.Object.DestroyImmediate(rt);
                UnityEngine.Object.DestroyImmediate(ui); UnityEngine.Object.DestroyImmediate(composite);
            }
        }

        static void Rebuild(VoyageGame g, int hull)
        {
            g.State.Hull = hull; g.State.Coins = 10000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", H).Invoke(g, new object[] { false });
            for (int i = 0; i < 60; i++) g.Tick(.05f);
        }

        static void Harbour()
        {
            for (int hull = 0; hull <= 4; hull++)
            {
                var g = Game("Harbour shot"); Rebuild(g, hull);
                Shot(g, $"harbour-h{hull}");
                Shot(g, $"harbour-h{hull}-phone", 844, 390);
                UnityEngine.Object.DestroyImmediate(g.gameObject);
            }
        }

        // The harbour master's chart with every pin; the last one (the Wreck bank) opened in detail.
        static void Chart()
        {
            var g = Game("Chart shot"); Rebuild(g, 4);
            typeof(VoyageGame).GetField("hudTab", H).SetValue(g, VoyageGame.HudTab.HarbourMaster);
            typeof(VoyageGame).GetField("panelOpen", H).SetValue(g, true);
            ShotUi(g, "chart-all"); ShotUi(g, "chart-all-phone", 844, 390);
            typeof(VoyageGame).GetField("chartFocus", H).SetValue(g, GameData.Spots.Length - 1);
            typeof(VoyageGame).GetField("chartDetailsOpen", H).SetValue(g, true);
            ShotUi(g, "chart-last-detail-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        // The harbour with its HUD at phone size, panel closed and each shop tab open.
        static void HarbourUi()
        {
            var g = Game("Harbour HUD shot"); Rebuild(g, 2);
            var panel = typeof(VoyageGame).GetField("panelOpen", H); var tab = typeof(VoyageGame).GetField("hudTab", H);
            panel.SetValue(g, false); ShotUi(g, "hud-harbour-phone", 844, 390);
            foreach (VoyageGame.HudTab t in Enum.GetValues(typeof(VoyageGame.HudTab)))
            { panel.SetValue(g, true); tab.SetValue(g, t); ShotUi(g, "hud-" + t.ToString().ToLowerInvariant() + "-phone", 844, 390); }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        // Fishing on deck with the HUD: the prep fisher and the tier-5 boat a minute into their trials.
        static void DeckUi()
        {
            var g = Game("Deck HUD shot"); g.StartPrepBoatTrial();
            for (int i = 0; i < 600; i++) g.Tick(.1f);
            ShotUi(g, "hud-deck-prep-phone", 844, 390); ShotUi(g, "hud-deck-prep");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            g = Game("Deck HUD shot"); g.StartTier5Trial();
            for (int i = 0; i < 600; i++) g.Tick(.1f);
            ShotUi(g, "hud-deck-tier5-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        // The captain's rod view with its HUD on a phone: waiting for a bite, the take, the fish lifted.
        static void Rod()
        {
            var g = FishViewChecks.Fixture();
            g.StageFishViewCapture(); g.Tick(1.25f);
            var r = g.Manning;
            void Wait(Func<bool> done) { for (float t = 0; t < 25 && !done(); t += .025f) g.Tick(.025f); }
            Wait(() => r.Reading.Phase == FishPhase.Inspect); ShotUi(g, "rod-0-waiting-phone", 844, 390); ShotUi(g, "rod-0-waiting");
            Wait(() => r.Reading.Phase == FishPhase.Take); g.Tick(.2f); ShotUi(g, "rod-1-take-phone", 844, 390);
            g.StrikeTap(); g.Tick(r.ThrashSeconds + .85f); ShotUi(g, "rod-2-lifted-phone", 844, 390); ShotUi(g, "rod-2-lifted");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        // Townsfolk on the quay: the harbour view, then a close look at each walker.
        static void Town()
        {
            var g = Game("Town shot"); Rebuild(g, 1);
            var walkers = UnityEngine.Object.FindObjectsByType<TownWalker>(FindObjectsSortMode.None);
            Debug.Log("TOWN walkers " + walkers.Length + ": " + string.Join(", ", walkers.Select(w => w.name + " @" + w.transform.position)));
            for (int i = 0; i < 70; i++) foreach (var w in walkers) w.Tick(.05f);
            Shot(g, "town-h1");
            var cam = g.Cam.transform; var size = g.Cam.orthographicSize; var home = cam.position;
            for (int n = 0; n < walkers.Length; n++)
            {
                g.Cam.orthographicSize = 2.2f;
                cam.position = walkers[n].transform.position + Vector3.up * .8f - cam.forward * 40f;
                Shot(g, "town-close-" + n);
            }
            g.Cam.orthographicSize = size; cam.position = home;
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Traffic()
        {
            var g = Game("Traffic shot"); Rebuild(g, 2);
            g.ShowHarbourTraffic(.42f); Shot(g, "traffic-h2-basin");
            g.BeginIntro();
            for (float t = 0; t < 3f; t += .05f) g.Tick(.05f);
            g.ShowHarbourTraffic(.3f); Shot(g, "traffic-intro-mouth");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Intro()
        {
            var g = Game("Intro shot");
            for (int i = 0; i < 40; i++) g.Tick(.05f);
            g.BeginIntro();
            float t = 0;
            foreach (float at in new[] { .5f, 3f, 5.5f, 8f, 10f })
            {
                while (t < at) { g.Tick(.05f); t += .05f; }
                ShotUi(g, $"intro-{at:0.0}s");
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Cage()
        {
            var g = Game("Cage shot");
            g.StartTier5Trial();
            var timers = (float[])typeof(VoyageGame).GetField("buoyTimers", H).GetValue(g);
            timers[0] = timers[1] = g.BuoySoakSeconds;
            g.TryBuoyWork(g.Captain);
            for (int i = 0; i < 400 && !g.CageViewActive; i++) g.Tick(.05f);
            for (int i = 0; i < 12; i++) g.Tick(.05f);
            ShotUi(g, "cage-0-start"); ShotUi(g, "cage-0-start-phone", 844, 390);
            var cage = g.Cage;
            for (int i = 0; i < 6; i++) { g.TapCage(); g.Tick(.05f); g.Tick(.05f); }
            ShotUi(g, "cage-1-hauling");
            for (int i = 0; i < 200 && cage.Phase == CagePhase.Pull; i++) { g.TapCage(); g.Tick(.08f); }
            if (cage.Phase == CagePhase.Snag) { g.Tick(.3f); ShotUi(g, "cage-2-snag"); g.DragCage(cage.SnagDirection); }
            for (int i = 0; i < 200 && cage.Phase == CagePhase.Pull; i++) { g.TapCage(); g.Tick(.08f); }
            for (int i = 0; i < 20; i++) g.Tick(.05f);
            ShotUi(g, "cage-3-board"); ShotUi(g, "cage-3-board-phone", 844, 390);
            if (cage.Current is { } crab) { g.FlickCage(!crab.Keeper); g.Tick(.05f); g.Tick(.15f); ShotUi(g, "cage-4-flick"); }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Net()
        {
            var g = NetViewChecks.Fixture();
            g.SetNet();
            for (int i = 0; i < 600 && !g.NetViewActive; i++) g.Tick(.05f);
            for (int i = 0; i < 14; i++) g.Tick(.05f);
            ShotUi(g, "net-0-setting"); ShotUi(g, "net-0-setting-phone", 844, 390);
            int shots = 0;
            for (int i = 0; i < 800 && g.NetGameActive; i++)
            {
                if (g.NetGamePhase >= .43f && g.NetGamePhase <= .55f && g.TapNetGame() && shots++ == 1) { g.Tick(.025f); g.Tick(.3f); ShotUi(g, "net-1-cast"); }
                g.Tick(.025f);
            }
            typeof(VoyageGame).GetMethod("TickNet", H).Invoke(g, new object[] { GameData.ShallowNetSoakSeconds + 1f });
            g.HaulNet();
            for (int i = 0; i < 600 && !g.NetViewActive; i++) g.Tick(.05f);
            for (int i = 0; i < 14; i++) g.Tick(.05f);
            bool mid = false, bunt = false;
            for (int i = 0; i < 1200 && g.NetGameActive; i++)
            {
                if (g.NetGameTension < .64f) g.TapNetGame();
                g.Tick(.025f);
                if (!mid && g.NetGameProgress > .3f) { mid = true; ShotUi(g, "net-2-haul"); }
                if (!bunt && g.NetGameProgress > .85f) { bunt = true; ShotUi(g, "net-3-bunt"); ShotUi(g, "net-3-bunt-phone", 844, 390); }
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Gut()
        {
            var (g, table) = GutViewChecks.Fixture(2);
            g.CaptainGutAt(table);
            for (int i = 0; i < 400 && !g.GutWaiting; i++) g.Tick(.05f);
            for (int i = 0; i < 14; i++) g.Tick(.05f);
            ShotUi(g, "gut-0-board"); ShotUi(g, "gut-0-board-phone", 844, 390);
            g.CutGut(GutViewChecks.CleanCut); g.Tick(.2f);
            ShotUi(g, "gut-1-clean"); ShotUi(g, "gut-1-clean-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Pots()
        {
            foreach (int hull in new[] { 1, 2 })
            {
                var g = CrabPotChecks.Fixture(hull);
                while (g.BuyCrabPot()) { }
                g.Showcase(0, 0); for (int i = 0; i < 20; i++) g.Tick(.05f);
                var timers = (float[])typeof(VoyageGame).GetField("buoyTimers", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic).GetValue(g);
                timers[0] = g.BuoySoakSeconds; g.Tick(.05f);
                ShotUi(g, $"pots-h{hull}-deck"); ShotUi(g, $"pots-h{hull}-deck-phone", 844, 390);
                g.TryBuoyWork(g.Captain);
                for (int i = 0; i < 400 && !g.CageViewActive; i++) g.Tick(.05f);
                for (int i = 0; i < 20; i++) g.Tick(.05f);
                ShotUi(g, $"pots-h{hull}-haul-phone", 844, 390);
                UnityEngine.Object.DestroyImmediate(g.gameObject);
            }
        }

        static void Dusk()
        {
            var g = Game("Dusk shot"); Rebuild(g, 2);
            g.SetHarbourEvening(true, true); g.Tick(.05f);
            Shot(g, "dusk-h2"); Shot(g, "dusk-h2-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Repair()
        {
            var g = RepairChecks.Fixture();
            g.BeginMend(); for (int i = 0; i < 14; i++) g.Tick(.05f);
            ShotUi(g, "repair-0-torn"); ShotUi(g, "repair-0-torn-phone", 844, 390);
            g.TraceMend(RepairChecks.Trace(.09f)); g.Tick(.1f);
            ShotUi(g, "repair-1-ragged-phone", 844, 390);
            g.TraceMend(RepairChecks.Trace()); g.Tick(.3f);
            ShotUi(g, "repair-2-mended"); ShotUi(g, "repair-2-mended-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Trip()
        {
            var g = Game("Trip shot"); Rebuild(g, 2);
            for (int i = 0; i < 5; i++) if (!g.State.Known(0)) g.State.BuyChart(0);
            g.SelectedSpot = 0; g.SetSail();
            float t = 0;
            foreach (float at in new[] { 3f, 9f, 16f, 22f })
            {
                while (t < at) { g.Tick(.05f); t += .05f; }
                ShotUi(g, $"trip-{at:00}s-{g.Leg}");
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
    }
}

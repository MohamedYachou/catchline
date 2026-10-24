using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    public static class CrewPolishChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static object Call(VoyageGame g, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Hidden).Invoke(g, args);
        static void Check(bool ok, string why) { if (!ok) throw new Exception("Crew polish check failed: " + why); }
        static void Until(VoyageGame g, Func<bool> done, string why, float seconds = 30)
        {
            for (float t = 0; t < seconds && !done(); t += .05f) g.Tick(.05f);
            Check(done(), why);
        }
        static VoyageGame Fixture(int hull)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Save-isolated crew polish").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.State.Hull = hull; g.State.Fuel = g.State.FuelCapacity; g.State.Coins = 1000; g.State.FoodMinutes = g.State.FoodCapacity;
            g.State.EnsureCrewRoleOffers();
            Check(g.State.Hire(g.State.Board.First(c => c.Role == CrewRole.Deckhand)), "hand hired");
            Call(g, "RebuildBoat", false);
            typeof(VoyageGame).GetField("showTitle", Hidden).SetValue(g, false);
            g.Showcase(0, 0);
            foreach (var rod in g.Rods) rod.State = RodState.Ready;
            return g;
        }
        static DeckFish Fish(VoyageGame g)
        {
            var f = new DeckFish { Species = Species.Herring, Kg = .3f, Tile = g.Rods[0].Tile, Age = 1, CaughtAt = g.SimTime };
            f.RestPos = g.Grid.GetLocal(f.Tile) + new Vector3(.1f, .07f, .15f);
            f.Root = DeckFish.BuildModel(f.Species, f.Kg, g.Boat); f.Root.localPosition = f.RestPos;
            g.OnDeck.Add(f); return f;
        }
        static void Facing(Person p, Vector3 target, string why)
        {
            target.y = 0;
            Check(Vector3.Dot(p.Root.localRotation * Vector3.forward, target.normalized) > .97f, why);
        }
        static void Shot(VoyageGame g, string name, int w = 1440, int h = 900) => typeof(ReferenceHudChecks)
            .GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic).Invoke(null, new object[] { g, "../crew016/" + name, w, h, 1f });
        public static void Run()
        {
            for (int hull = 0; hull < 3; hull++)
            {
                var g = Fixture(hull); var hand = g.Hand;
                Check(hand.Root.Find("Progress") == null && g.Captain.Root.Find("Progress") == null, "no overhead progress geometry");
                g.State.Rng = new System.Random(123);
                var start = hand.Root.localPosition; bool walking = false, looking = false;
                float greatestTravel = 0;
                for (int i = 0; i < 600; i++)
                {
                    g.Tick(.05f);
                    Check(!g.Grid.IsBlocked(hand.Tile), "patrol remains on walkable deck hull " + hull);
                    Check(!hand.Busy, "idle routine never creates a fake timed work job");
                    greatestTravel = Mathf.Max(greatestTravel, Vector3.Distance(start, hand.Root.localPosition));
                    walking |= hand.Loitering && hand.Walking;
                    looking |= hand.Loitering && !hand.Walking;
                    if (hand.Loitering && !hand.Walking)
                        Check(Mathf.Abs(hand.Root.localPosition.y - start.y) < .0001f, "lookout has no root jitter");
                }
                Check(walking && looking && greatestTravel >= .6f && hand.PatrolLeg >= 2, "walk, dwell, then continue on hull " + hull);
                Check(g.State.Rng.Next() == new System.Random(123).Next(), "cosmetic patrol does not consume catch RNG");
                var frozen = hand.Root.localPosition; var rotation = hand.Root.localRotation;
                g.Tick(0);
                Check(hand.Root.localPosition == frozen && Quaternion.Angle(rotation, hand.Root.localRotation) < .001f, "pause freezes patrol");
                Until(g, () => hand.Loitering && hand.Walking, "reach an active patrol walk");
                var fish = Fish(g); g.Tick(.05f);
                Check(fish.ClaimedBy == hand && !hand.Loitering, "new catch interrupts patrol on next simulation step");
                Until(g, () => hand.BusyLabel == "Picking up" && hand.Busy, "actual pickup pose");
                hand.Tick(.5f, Quaternion.identity);
                Facing(hand, fish.RestPos - hand.Root.localPosition, "pickup faces fish");
                Until(g, () => hand.Busy && hand.BusyLabel == "Stowing", "actual stow pose");
                hand.Tick(.5f, Quaternion.identity);
                Facing(hand, g.Grid.GetLocal(g.State.HullDef.Hold) - hand.Root.localPosition, "delivery faces hold");
                Until(g, () => g.Cooler.Count == 1, "patrol interruption delivers fish exactly once");
                Until(g, () => hand.Loitering && hand.Walking, "resumes patrol after delivery");
                var rod = g.Rods[0]; rod.State = RodState.Unbaited; g.Tick(.05f);
                Check(rod.BaitingBy == hand && !hand.Loitering, "baiting interrupts stroll");
                Until(g, () => hand.Busy && hand.BusyLabel == "Baiting", "bait action starts");
                hand.Tick(.5f, Quaternion.identity); Facing(hand, rod.Outward, "bait faces actual rod side");
                float deckY = hand.Root.localPosition.y; hand.Tick(.05f, Quaternion.identity);
                Check(Mathf.Abs(hand.Root.localPosition.y - deckY) < .0001f, "rigged work has no second root bob");
                Debug.Log("[Catchline] CREW016 hull " + hull + ": patrol legs=" + hand.PatrolLeg + ", travel=" + greatestTravel + "; walk/look/resume, interrupt pickup/bait, facing, pause, no RNG passed");
                UnityEngine.Object.DestroyImmediate(g.gameObject);
            }
            var net = Fixture(2); var worker = net.Hand;
            net.State.Rng = new System.Random(0);
            net.Tick(.05f); Check(worker.Loitering, "net fixture initially strolls");
            worker.Contract.WorkPreference = DeckhandWork.Nets; net.Tick(.05f);
            Check(net.Net == VoyageGame.NetState.Setting && !worker.Loitering, "net duty interrupts active patrol immediately");
            Until(net, () => worker.Busy && worker.BusyLabel == "Setting net", "net worker reaches winch");
            worker.Tick(.5f, Quaternion.identity); Facing(worker, Vector3.right, "net worker faces stern equipment");
            Until(net, () => net.Net == VoyageGame.NetState.Soaking, "worker sets net");
            net.Tick(.05f); Check(worker.Loitering, "soaking frees worker to patrol");
            worker.Contract.WorkPreference = DeckhandWork.Fish;
            net.Captain.Stop(); net.Captain.Place(net.Rods[1].Tile); net.CommandRod(net.Rods[1]);
            net.Tick(.5f); Facing(net.Captain, net.Rods[1].Outward, "already-at-rod captain faces rod rather than old heading");
            net.PrepareInterface(1672, 941, 1);
            foreach (string role in new[] { "captain", "deckhand", "fisherman" })
            {
                var texture = Resources.Load<Texture2D>("FishReference/portrait-" + role);
                Check(texture != null && texture.width == 57 && texture.height == 60, "actual reference portrait imported " + role);
            }
            var images = net.GetComponentsInChildren<Image>();
            Check(images.Single(i => i.name == "reference/crew/0/portrait").sprite.name == "reference/portrait-captain", "captain uses reference pixels");
            Check(images.Single(i => i.name == "reference/crew/1/portrait").sprite.name == "reference/portrait-deckhand", "deckhand uses reference pixels");
            UnityEngine.Object.DestroyImmediate(net.gameObject);
            Debug.Log("[Catchline] CREW POLISH CHECKS PASSED");
        }
        public static void Capture()
        {
            Directory.CreateDirectory(Path.GetFullPath("Logs/crew016"));
            var g = Fixture(2); g.State.Coins = 1000; g.State.EnsureCrewRoleOffers();
            g.State.Hire(g.State.Board.First(c => c.Role == CrewRole.Fisherman)); g.SyncCrew();
            for (int i = 0; i < 500 && !(g.Hand.Loitering && !g.Hand.Walking); i++) g.Tick(.05f);
            Shot(g, "lookout-desktop"); Shot(g, "lookout-reference", 1672, 941); Shot(g, "lookout-phone", 844, 390);
            for (int i = 0; i < 500 && !(g.Hand.Loitering && g.Hand.Walking); i++) g.Tick(.05f);
            Shot(g, "strolling-desktop");
            Fish(g);
            Until(g, () => g.Hand.Busy && g.Hand.BusyLabel == "Stowing", "stow capture");
            g.Tick(.5f); Shot(g, "stowing-desktop"); Shot(g, "stowing-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] Snapshot written to Logs/crew016");
        }
        public static void ValidateAndBuildPreview()
        {
            FirstVoyageChecks.Regression(); NetHaulChecks.Run(); NetEconomyChecks.Run(); Run(); Capture(); BuildPreview();
        }
        public static void ReviewAndBuildPreview()
        {
            Capture(); BuildPreview();
        }
        public static void BuildPreview()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Catchline crew polish preview").AddComponent<VoyageGame>(); g.SessionOnly = true;
            const string scene = "Assets/Scenes/Crew016Preview.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
            string output = Path.GetFullPath("Builds/Crew016/Catchline.exe");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None });
            Check(report.summary.result == BuildResult.Succeeded, "separate crew preview built");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + output);
        }
    }
}

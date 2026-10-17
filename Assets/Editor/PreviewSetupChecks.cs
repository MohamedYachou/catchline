using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class PreviewSetupChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string reason) { if (!ok) throw new Exception("Preview setup check failed: " + reason); }
        static T Field<T>(VoyageGame game, string name) => (T)typeof(VoyageGame).GetField(name, Hidden).GetValue(game);
        static void Set(VoyageGame game, string name, object value) => typeof(VoyageGame).GetField(name, Hidden).SetValue(game, value);
        static void Route(VoyageGame game, bool home, int spot)
        {
            float duration = GameData.Spots[spot].RowSeconds * game.State.HullDef.TravelMultiplier;
            var incoming = Field<Transform>(game, "scenery");
            var outgoing = Field<Transform>(game, "oldScenery");
            game.Tick(duration * .4f);
            var startIn = incoming.localPosition; var startOut = outgoing.localPosition;
            game.Tick(duration * .02f);
            var bow = game.Boat.TransformDirection(Vector3.left); bow.y = 0;
            var direction = VoyageGame.RouteDirection(spot) * (home ? -1 : 1);
            Check(Vector3.Dot(bow.normalized, direction) > .99f, "physical bow faces voyage direction");
            Check(Vector3.Dot((incoming.localPosition - startIn).normalized, bow.normalized) < -.99f, "incoming scenery passes sternward " + spot + " home=" + home);
            Check(Vector3.Dot((outgoing.localPosition - startOut).normalized, bow.normalized) < -.99f, "outgoing scenery passes sternward " + spot + " home=" + home);
            game.Tick(duration);
        }
        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Native laptop trial fixture").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build();
            Check(game.StartNetBoatTrial(), "isolated setup runs");
            Check(game.IsNetFisher && game.State.Coins == 200 && game.CurrentMode == VoyageGame.Mode.Fishing && !game.MenuOpen, "direct playable200coin net boat");
            Check(game.State.CrewCount == 3 && game.State.Crew.Count(c => c.Role == CrewRole.Fisherman) == 2 && game.Hand != null, "two fishers and one hand pre-hired");
            Check(game.State.Bait == 60 && game.State.FoodMinutes == game.State.FoodCapacity, "ready supplies");
            Check(game.SetNet(), "net immediately usable"); game.Captain.Stop();
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            {
                game.Showcase(-1, 0); game.State.Charts.Add(spot); game.State.Fuel = 100;
                game.SelectedSpot = spot; game.SetSail(); Route(game, false, spot);
                Check(game.CurrentMode == VoyageGame.Mode.Fishing, "outbound arrives");
                game.HeadHome(); Route(game, true, spot);
                Check(game.CurrentMode == VoyageGame.Mode.Harbour, "return arrives");
            }
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] PREVIEW SETUP CHECKS PASSED: direct200coin net boat,3crew,supplies,forward cruise both directions across5maps");
        }
        public static void ValidateAndBuildPreview()
        {
            Run();
            FirstVoyageChecks.BuildPreview();
        }
    }
}

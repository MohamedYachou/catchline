using System;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace Catchline.EditorTools
{
    public static class FisherFeedbackChecks
    {
        static void Check(bool ok,string message)
        {
            if(!ok)throw new Exception("[Catchline] First voyage check failed: fisherman feedback "+message);
        }
        static T Read<T>(VoyageGame game,string name)=>(T)typeof(VoyageGame).GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).GetValue(game);
        public static void Run()
        {
            Check(Mathf.Approximately(GameData.StrikeChance(Grade.Hand),.8f),"basic fisherman strikes 80 percent");
            Check(GameData.StrikeChance(Grade.Experienced)>.8f && GameData.StrikeChance(Grade.Veteran)>GameData.StrikeChance(Grade.Experienced),"higher grades retain advantage");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var game=new GameObject("Quiet fisherman check").AddComponent<VoyageGame>();
            game.SessionOnly=true;game.Build();game.State.Coins=1000;
            game.State.Hire(game.State.Board.First(c=>c.Role==CrewRole.Fisherman));game.SyncCrew();game.SyncUpgrades();
            game.State.FoodMinutes=20;game.SetSail();
            for(int i=0;i<1000 && game.CurrentMode!=VoyageGame.Mode.Fishing;i++)game.Tick(.05f);
            game.Tick(2f);
            var captain=game.Rods[0];var crew=game.Rods[1];
            Check(crew.Fisher!=null,"fisherman owns separate rod");
            game.LandFish(captain,Species.Herring,.25f);
            float until=Read<float>(game,"catchUntil");
            game.Toast("Captain feedback stays");
            game.LandFish(crew,Species.Mackerel,.3f);
            Check(Read<float>(game,"catchUntil")==until && Read<float>(game,"lastCatchKg")==.25f,"crew catch never replaces captain catch card");
            Check(Read<string>(game,"toast")=="Captain feedback stays","crew catch never clears captain toast");
            Check(game.OnDeck.Last().CaughtByCrew && game.CurrentHaul().Count>=2,"crew fish still land and count in haul");
            crew.State=RodState.Bite;crew.FisherAttempted=true;
            int missed=game.Stats.Missed;
            game.Tick(2f);
            Check(game.Stats.Missed>missed,"forced missed crew bite simulated");
            Check(Read<string>(game,"toast")=="Captain feedback stays","missed crew bite never overwrites captain toast");
            game.LandFish(captain,Species.Pollock,1.1f);
            Check(Read<float>(game,"lastCatchKg")==1.1f,"captain catches still show rewards");
            Debug.Log("[Catchline] FISHER FEEDBACK CHECKS PASSED: 80 percent baseline; crew catch/miss silent; captain feedback preserved; haul counts");
        }
    }
}

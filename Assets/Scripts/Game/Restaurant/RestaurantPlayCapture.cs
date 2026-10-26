using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Catchline.Game.Restaurant
{
    // Dedicated scratch scene only. Binds the lead's existing HUD; it draws no interface and never opens a save.
    public sealed class RestaurantPlayCapture : MonoBehaviour
    {
        RestaurantWorld world; RestaurantSim sim; VoyageGame game; bool proof;
        string output; int shot; readonly float[] moments={60,240,540};
        IEnumerator Start()
        {
            proof=Environment.GetCommandLineArgs().Contains("-restaurant-proof");
            output="C:/Users/momoy/Projects/Catchline/docs/screens/restaurant-play-1/"+Screen.width+"x"+Screen.height;
            Directory.CreateDirectory(output);Application.runInBackground=true;Time.timeScale=1;
            yield return null;yield return null;
            game=FindFirstObjectByType<VoyageGame>();
            if(game==null||!game.SessionOnly)throw new InvalidOperationException("Restaurant proof requires SessionOnly");
            game.SendMessage("EndIntro",SendMessageOptions.DontRequireReceiver);
            typeof(VoyageGame).GetField("showTitle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance)?.SetValue(game,false);
            var layout=new RestaurantLayout(RestaurantLayout.StartingKit());
            var forecast=new RestaurantForecast(91,1,DayOfWeek.Friday,Weather.Fair,new[]{(Species.Pollock,60f),(Species.Cod,30f),(Species.Mackerel,10f)},layout);forecast.Lock();
            sim=new RestaurantSim(91,layout,forecast,new[]{new PortionStock{Species=Species.Pollock,Form=PreparedForm.Fillet,Count=9},new PortionStock{Species=Species.Herring,Form=PreparedForm.Stock,Count=6}},
                new[]{RestaurantStaff.FromCard(new CardState("mira"),Job.Reception,layout.Door),RestaurantStaff.Captain(layout.Door)}){Breakdowns=true};
            world=game.gameObject.AddComponent<RestaurantWorld>();world.DriveSimulation=false;world.Begin(sim);
            game.RestaurantPreview=VoyageGame.RestaurantScreen.Service;game.RestaurantService.QuestionTitle=null;
            game.RestaurantService.Crew.Clear();game.RestaurantService.Stock.Clear();
            for(int i=0;i<10;i++)game.RestaurantService.Arrivals[i]=sim.Groups.Count(g=>g.Arrival>=i*60&&g.Arrival<(i+1)*60)/5f;
            while(!sim.Finished){
                float speed=proof?4:game.RestaurantService.Paused?0:game.RestaurantService.Speed;
                sim.Tick(Time.unscaledDeltaTime*speed);world.Refresh(Time.unscaledDeltaTime*speed);Bind();
                if(proof&&shot<moments.Length&&sim.Seconds>=moments[shot]){
                    yield return Screenshot(new[]{"1830","2000","2230"}[shot]);shot++;
                }
                yield return null;
            }
            Bind();File.WriteAllText(output+"/night-result.json",JsonUtility.ToJson(sim.Result,true));
            var r=sim.Result;var close=game.RestaurantClosing;
            close.Served=r.Served;close.Left=r.Left;close.Dishes=r.DishCoins-r.StapleCosts;close.Drinks=r.DrinkCoins;close.Tips=r.Tips;close.CatPortions=r.Cats;close.CatValue=0;
            close.Stars=Mathf.RoundToInt(r.Stars);close.PopularityFrom=1;close.PopularityTo=Mathf.Max(0,Mathf.RoundToInt(1+r.PopularityGain));close.PopularityBefore=.1f;close.Popularity=close.PopularityTo/10f;
            close.Reviews.Clear();close.CrewOfTheNight="Captain";close.CrewPortrait="captain";close.MiraLine="We did it together.";
            game.RestaurantPreview=VoyageGame.RestaurantScreen.Closing;
            yield return null;yield return Screenshot("2300-result");
            Debug.Log("[Catchline] RESTAURANT NATIVE FULL NIGHT PASS "+Screen.width+"x"+Screen.height+" served="+r.Served+" net="+r.NetCoins);
            if(proof){yield return new WaitForSecondsRealtime(1);Application.Quit();}
        }
        void Bind()
        {
            var snap=world.Snapshot;var v=game.RestaurantService;
            v.Hour=snap.Hour;v.Coins=snap.CoinsTonight;v.Popularity=Mathf.RoundToInt(snap.Popularity);v.Alert=snap.BrokenAppliances.Count==0?null:"Appliance needs repair";
            v.QuestionTitle=snap.Question?.Title;v.QuestionBody="The planned fish has sold out.";v.QuestionBodyShort=v.QuestionBody;v.QuestionYes="Offer soup";v.QuestionNo="Just drinks";
            v.Crew.Clear();foreach(var s in snap.Staff)v.Crew.Add(new VoyageGame.RestaurantStaff{Portrait=s.PortraitKey,Job=s.Task,Icon=s.Job==Job.Reception?"v2-icon-bell":"v2-icon-crew",Fallback="icon-crew",Busy=s.Busy});
            v.Stock.Clear();foreach(var s in snap.Stock.GroupBy(x=>x.Dish))v.Stock.Add(new VoyageGame.RestaurantStock{Name=s.Key.ToString(),Art=s.Key==Dish.Soup?"v2-dish-fish-soup":"v2-dish-fillets",Fallback="icon-food",Count=s.Sum(x=>x.Portions),Max=15,Alert=s.Sum(x=>x.Portions)==0});
        }
        IEnumerator Screenshot(string name)
        {
            yield return new WaitForEndOfFrame();var texture=ScreenCapture.CaptureScreenshotAsTexture();
            if(texture==null||texture.width!=Screen.width||texture.height!=Screen.height)throw new InvalidOperationException("No native framebuffer");
            File.WriteAllBytes(output+"/"+name+".png",texture.EncodeToPNG());Destroy(texture);
            var rows=new List<string>{"hour="+sim.Hour,"seconds="+sim.Seconds,"staff="+sim.Staff.Count,"coins="+sim.Result.NetCoins};
            rows.AddRange(sim.Staff.Select(s=>s.Id+" "+s.Action+" position="+s.Position+" walked="+s.Metres));
            rows.AddRange(sim.Layout.Active.Select(i=>i.Uid+" "+i.Id+" screen="+world.WorldToScreen(i.Uid)));
            File.WriteAllLines(output+"/"+name+".txt",rows);
        }
    }
}

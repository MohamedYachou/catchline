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
            if(Environment.GetCommandLineArgs().Contains("-restaurant-feel-proof")){yield return Feel();yield break;}
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
        // Fixed presentation steps and a real framebuffer, in a SessionOnly scratch player. No player save is opened.
        sealed class Strip {public string Name;public int Group,Frame;public float Start;public int Count;}
        IEnumerator Feel()
        {
            output="C:/Users/momoy/Projects/Catchline/docs/screens/restaurant-feel-1/"+Screen.width+"x"+Screen.height;
            Directory.CreateDirectory(output);Application.runInBackground=true;QualitySettings.vSyncCount=0;Application.targetFrameRate=120;Time.timeScale=1;
            yield return null;yield return null;game=FindFirstObjectByType<VoyageGame>();
            if(game==null||!game.SessionOnly)throw new InvalidOperationException("Restaurant feel proof requires SessionOnly");
            game.SendMessage("EndIntro",SendMessageOptions.DontRequireReceiver);
            typeof(VoyageGame).GetField("showTitle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance)?.SetValue(game,false);
            var layout=new RestaurantLayout(RestaurantLayout.StartingKit());
            var forecast=new RestaurantForecast(91,1,DayOfWeek.Friday,Weather.Fair,new[]{(Species.Pollock,60f),(Species.Cod,30f),(Species.Mackerel,10f)},layout);forecast.Lock();
            sim=new RestaurantSim(91,layout,forecast,new[]{new PortionStock{Species=Species.Pollock,Form=PreparedForm.Fillet,Count=9},new PortionStock{Species=Species.Herring,Form=PreparedForm.Stock,Count=6}},
                new[]{RestaurantStaff.FromCard(new CardState("mira"),Job.Reception,layout.Door),RestaurantStaff.Captain(layout.Door),RestaurantStaff.FromCard(new CardState("dirk"),Job.Cook,layout.PassKitchen),RestaurantStaff.FromCard(new CardState("ana"),Job.Waiter,layout.Door),RestaurantStaff.FromCard(new CardState("ines"),Job.Barista,layout.Door)}){Breakdowns=false};
            world=game.gameObject.AddComponent<RestaurantWorld>();world.DriveSimulation=false;world.Begin(sim);
            game.RestaurantPreview=VoyageGame.RestaurantScreen.Service;game.RestaurantService.QuestionTitle=null;
            var strips=new List<Strip>();var previous=sim.Groups.ToDictionary(g=>g.Id,g=>g.Phase);var summary=new List<string>{"Seed91; unmodified starter layout/stock, Mira+captain+Dirk+Ana+Ines; no breakdowns; SessionOnly; actual native HUD.","Five .02s presentation steps per captured .1s; enabled World uses the external driver, like RestaurantDay."};
            bool seated=false,left=false,served=false;float elapsed=0;
            while(elapsed<610){
                for(int step=0;step<5;step++){sim.Tick(.02f);world.Refresh(.02f);elapsed+=.02f;}
                Bind();
                if(!seated){var host=sim.Staff.FirstOrDefault(s=>s.Action=="Seat group"&&s.Task.Current!=null&&s.Task.Legs.Count==0);
                    if(host!=null){var g=sim.Groups.FirstOrDefault(g=>g.Phase==GroupPhase.Seating&&g.Count>=2);if(g!=null){strips.Add(new Strip{Name="seating",Group=g.Id,Start=elapsed,Count=80});seated=true;}}}
                if(!left){var g=sim.Groups.FirstOrDefault(g=>g.Phase==GroupPhase.Gone&&g.TableUid!=0&&previous[g.Id]!=GroupPhase.Gone&&g.Count>=2);
                    if(g!=null){strips.Add(new Strip{Name="leaving",Group=g.Id,Start=elapsed,Count=80});left=true;}}
                if(!served){var waiter=sim.Staff.First(s=>s.Id=="ana");if(waiter.Action=="Serve fish"&&waiter.Task.Current!=null&&waiter.Task.Legs.Count==0){
                    var g=sim.Groups.First(x=>x.Tickets.Any(t=>t.Phase==TicketPhase.Serving));strips.Add(new Strip{Name="serving",Group=g.Id,Start=elapsed,Count=60});served=true;}}
                foreach(var strip in strips.Where(x=>x.Frame<x.Count)){
                    string folder=output+"/"+strip.Name;Directory.CreateDirectory(folder);
                    yield return new WaitForEndOfFrame();var texture=ScreenCapture.CaptureScreenshotAsTexture();
                    if(texture==null||texture.width!=Screen.width||texture.height!=Screen.height)throw new InvalidOperationException("No native framebuffer");
                    string name=folder+"/"+strip.Frame.ToString("D3");File.WriteAllBytes(name+".png",texture.EncodeToPNG());Destroy(texture);
                    var rows=new List<string>{FormattableString.Invariant($"elapsed={elapsed:F3} strip={elapsed-strip.Start:F3} sim={sim.Seconds:F2} group={strip.Group}")};
                    rows.AddRange(sim.Groups.Where(g=>g.Phase!=GroupPhase.NotArrived).Select(g=>"group="+g.Id+" phase="+g.Phase+" guests="+string.Join(",",g.Guests.Select(o=>o.Id))+" table="+g.TableUid+" delivered="+g.Tickets.Count(t=>t.Phase==TicketPhase.Delivered)));
                    rows.AddRange(sim.Groups.SelectMany(g=>g.Tickets.Select(t=>"ticket="+t.Order.Id+" group="+g.Id+" dish="+t.Dish+" phase="+t.Phase)));
                    rows.AddRange(sim.Staff.Select(s=>"staff="+s.Id+" task="+s.Action+" remainingLegs="+(s.Task?.Legs.Count??-1)));
                    foreach(Transform t in world.RoomRoot)if(t.name.StartsWith("Guest ")||t.name.StartsWith("Staff ")){
                        var p=t.position;var f=t.forward;var vp=world.ServiceCamera.WorldToScreenPoint(p);rows.Add(FormattableString.Invariant($"actor={t.name} active={t.gameObject.activeSelf} xyz={p.x:F4},{p.y:F4},{p.z:F4} forward={f.x:F4},{f.z:F4} screen={vp.x:F2},{Screen.height-vp.y:F2} children={string.Join(",",t.Cast<Transform>().Select(x=>x.name))}"));
                        if(t.name.StartsWith("Staff ")){var rig=t.GetChild(0);var rs=rig.GetComponentsInChildren<Renderer>();var b=rs.Length>0?rs[0].bounds:new Bounds();foreach(var r in rs)b.Encapsulate(r.bounds);rows.Add(FormattableString.Invariant($"rig={t.name} scale={rig.localScale} bounds={b.size} renderers={rs.Length}"));}}
                    File.WriteAllLines(name+".txt",rows);strip.Frame++;
                }
                foreach(var g in sim.Groups)previous[g.Id]=g.Phase;
                if(seated&&left&&served&&strips.All(x=>x.Frame==x.Count))break;
                yield return null;
            }
            foreach(var strip in strips)summary.Add(strip.Name+" group="+strip.Group+" frames="+strip.Frame+" interval=.1s start="+strip.Start);
            bool pass=seated&&left&&served&&strips.All(x=>x.Frame==x.Count);File.WriteAllLines(output+"/capture.txt",summary);
            Debug.Log("[Catchline] RESTAURANT FEEL NATIVE "+(pass?"PASS":"FAIL")+" "+Screen.width+"x"+Screen.height+" strips="+strips.Count);
            Application.Quit(pass?0:1);
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

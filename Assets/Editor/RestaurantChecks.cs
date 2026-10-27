using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text;
using Catchline.Game;
using Catchline.Game.Restaurant;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

namespace Catchline.EditorTools
{
    public sealed class RestaurantGuestImport : AssetPostprocessor
    {
        public override int GetPostprocessOrder()=>100;
        void OnPreprocessModel(){if(assetPath.StartsWith("Assets/Art/Models/Restaurant/Guests/")){var mi=(ModelImporter)assetImporter;mi.importAnimation=true;mi.animationType=ModelImporterAnimationType.Legacy;}}
    }
    public static class RestaurantChecks
    {
        const string Out="C:/Users/momoy/Projects/Catchline/docs/screens/restaurant-play-1";
        static int assertions;
        static readonly List<string> checks=new List<string>();
        static void Check(bool ok,string why){assertions++;checks.Add((ok?"PASS ":"FAIL ")+why);if(!ok)throw new Exception("Restaurant: "+why);}
        static void Reason(LayoutResult r,LayoutReason expected,string why)=>Check(r.Reason==expected && r.Message==RestaurantLayout.Sentence(expected),why+" => "+r.Reason+" / "+r.Message);
        static RestaurantLayout Kit(){return new RestaurantLayout(RestaurantLayout.StartingKit());}
        static RestaurantForecast Forecast(RestaurantLayout l,int seed=42,int popularity=1) => new RestaurantForecast(seed,popularity,DayOfWeek.Friday,Weather.Fair,
            new[]{(Species.Pollock,60f),(Species.Cod,30f),(Species.Mackerel,10f)},l);
        static List<RestaurantStaff> Team(RestaurantLayout l,int cooks,int waiters,bool bars=false,bool engineer=false)
        {
            var list=new List<RestaurantStaff>{new RestaurantStaff{Id="mira",Job=Job.Reception,NativeJob=Job.Reception,Rarity=CardRarity.Gold,Tile=l.Door}};
            for(int i=0;i<cooks;i++)list.Add(new RestaurantStaff{Id="cook"+i,Job=Job.Cook,NativeJob=Job.Cook,Tile=l.PassKitchen});
            for(int i=0;i<waiters;i++)list.Add(new RestaurantStaff{Id="waiter"+i,Job=Job.Waiter,NativeJob=Job.Waiter,Tile=l.Door});
            if(bars)list.Add(new RestaurantStaff{Id="barista",Job=Job.Barista,NativeJob=Job.Barista,Tile=l.Door});
            if(engineer)list.Add(new RestaurantStaff{Id="engineer",Job=Job.Handyman,NativeJob=Job.Handyman,Tile=l.PassKitchen});
            return list;
        }
        static List<PortionStock> Stock(int fillets,int soup) => new List<PortionStock>{new PortionStock{Species=Species.Pollock,Form=PreparedForm.Fillet,Count=fillets},new PortionStock{Species=Species.Herring,Form=PreparedForm.Stock,Count=soup}};
        static RestaurantLayout Large(int stage=3)
        {
            var s=new RestaurantState{Stage=stage,Coins=100000,Popularity=10};var l=new RestaurantLayout(s);
            Action<ItemId,int,int,bool> add=(id,x,y,r)=>{var result=l.Buy(id,x,y,r);if(!result.Ok)throw new Exception("Fixture "+id+" "+x+","+y+" "+result.Message);};
            add(ItemId.Stove,0,4,false);add(ItemId.Stove,0,3,false);add(ItemId.SoupKettle,0,2,false);add(ItemId.PrepCounter,2,4,false);
            add(ItemId.Fridge,0,0,false);add(ItemId.Fridge,2,0,false);add(ItemId.Fridge,2,1,false);add(ItemId.Fridge,2,3,false);
            int k=l.Stage.KitchenWidth;
            add(ItemId.CoffeeMachine,k+1,4,false);add(ItemId.DrinksFridge,k+2,4,false);add(ItemId.Reception,l.Stage.Width-2,0,false);
            for(int x=k+2;x<l.Stage.Width-1;x+=3){add(ItemId.Table4,x,2,false);add(ItemId.Table2,x+1,4,false);}
            if(stage>=2)add(ItemId.TerraceTable,l.Stage.Width,3,false);
            return l;
        }
        static void LayoutChecks()
        {
            var l=Kit();Reason(l.Validate(),LayoutReason.Ok,"starting kit valid");
            foreach(LayoutReason r in Enum.GetValues(typeof(LayoutReason)))Check(!string.IsNullOrWhiteSpace(RestaurantLayout.Sentence(r)),"sentence for "+r);
            Reason(l.CheckPlacement(ItemId.Stove,5,1),LayoutReason.KitchenOnly,"kitchen zone");
            Reason(l.CheckPlacement(ItemId.Plant,1,2),LayoutReason.GuestsOnly,"guest zone");
            Reason(l.CheckPlacement(ItemId.Plant,8,1),LayoutReason.Outside,"room bounds");
            Reason(l.CheckPlacement(ItemId.Sink,0,0),LayoutReason.StageLocked,"stage lock");
            Reason(l.CheckPlacement(ItemId.Plant,7,0),LayoutReason.DoorBlocked,"door cannot be occupied");
            Reason(l.CheckPlacement(ItemId.Plant,5,2),LayoutReason.Occupied,"overlap");
            Reason(l.CheckPlacement(ItemId.Lamp,6,2),LayoutReason.WallOnly,"wall fixture interior rejected");
            Reason(l.CheckPlacement(ItemId.Stove,2,2),LayoutReason.PassBlocked,"pass access");
            Reason(l.CheckPlacement(ItemId.Plant,3,4),LayoutReason.PassBlocked,"pass boundary");
            Reason(l.Buy(ItemId.Plant,5,0),LayoutReason.NotEnoughCoins,"insufficient money atomic");Check(l.State.Coins==0&&l.State.Items.Count==8,"no charge or ghost after failed buy");
            var stove=l.Active.First(i=>i.Id==ItemId.Stove);int sx=stove.X,sy=stove.Y;
            Reason(l.Move(stove.Uid,5,1),LayoutReason.KitchenOnly,"failed move");Check(stove.X==sx&&stove.Y==sy,"failed move preserves coordinates");
            Reason(l.Store(999),LayoutReason.MissingItem,"missing item");
            l.State.Coins=10000;Reason(l.Buy(ItemId.Table4,4,3),LayoutReason.Ok,"2x1 table");var table=l.Active.Last();int coins=l.State.Coins;
            Reason(l.Rotate(table.Uid),LayoutReason.Occupied,"rotation checks full footprint");
            Reason(l.Store(table.Uid),LayoutReason.Ok,"store");Check(table.Stored,"stored removed from floor");
            Reason(l.Move(table.Uid,4,3),LayoutReason.Ok,"retrieve stored item");Reason(l.Sell(table.Uid),LayoutReason.Ok,"sell back");
            Check(l.State.Coins==coins+(int)(RestaurantData.Get(ItemId.Table4).Price*RestaurantTuning.SellBack),"half-price sale exact");
            Reason(l.Buy(ItemId.Lamp,6,4),LayoutReason.Ok,"wall lamp shares floor footprint safely");
            Reason(l.Expand(3),LayoutReason.InvalidStage,"expansion sequential");Reason(l.Expand(2),LayoutReason.Popularity,"expansion popularity gate");
            l.State.Popularity=10;l.State.Coins=0;Reason(l.Expand(2),LayoutReason.NotEnoughCoins,"expansion coin gate");l.State.Coins=100000;
            int[] ids=l.State.Items.Select(i=>i.Uid).OrderBy(x=>x).ToArray();
            Reason(l.Expand(2),LayoutReason.Ok,"expand bistro");Reason(l.CheckPlacement(ItemId.TerraceTable,7,1),LayoutReason.TerraceOnly,"terrace zone");
            Reason(l.Expand(3),LayoutReason.Ok,"expand restaurant");Reason(l.Expand(4),LayoutReason.Ok,"expand seafood house");
            Check(l.State.Items.Select(i=>i.Uid).OrderBy(x=>x).SequenceEqual(ids),"all item IDs retained by three expansions");
            var loaded=RestaurantState.FromJson(l.State.ToJson());Check(loaded.Name=="Mira's"&&loaded.Items.Count==l.State.Items.Count&&loaded.Stage==4&&loaded.Coins==l.State.Coins,"JsonUtility round trip");
            Check(new RestaurantLayout(loaded).Validate().Ok,"restored layout still reachable");
            var blocked=Kit();blocked.State.Items.Add(new RestaurantItem{Uid=99,Id=ItemId.PrepCounter,X=2,Y=0});Reason(blocked.Validate(),LayoutReason.DoorBlocked,"blocking crossing aisle fails");
            var seat=Kit();seat.State.Items.Add(new RestaurantItem{Uid=99,Id=ItemId.Plant,X=6,Y=4});seat.State.Items.Add(new RestaurantItem{Uid=100,Id=ItemId.Plant,X=7,Y=3});Reason(seat.Validate(),LayoutReason.SeatBlocked,"every seat access checked");
            var kitchen=Kit();kitchen.State.Items.Add(new RestaurantItem{Uid=99,Id=ItemId.PrepCounter,X=1,Y=4});Reason(kitchen.Validate(),LayoutReason.KitchenBlocked,"every kitchen access checked");
            var rec=Kit();var reception=rec.Active.First(i=>i.Id==ItemId.Reception);reception.X=6;reception.Y=3;
            foreach(var p in new[]{new Vector2Int(5,3),new Vector2Int(7,3),new Vector2Int(6,2),new Vector2Int(6,4)})rec.State.Items.Add(new RestaurantItem{Uid=100+rec.State.Items.Count,Id=ItemId.Plant,X=p.x,Y=p.y});
            Reason(rec.Validate(),LayoutReason.ReceptionBlocked,"reception access checked");
            Check(Kit().Path(new Vector2Int(7,0),new Vector2Int(2,2)).Count==9,"BFS shortest route around pass");
        }
        static void PortionChecks()
        {
            Check(RestaurantPortions.Yield(Species.Mackerel,.8f,PreparedForm.Whole)==1,"0.8 kg whole boundary");
            Check(RestaurantPortions.Yield(Species.Mackerel,.81f,PreparedForm.Whole)==0,"large fish cannot grill whole");
            Check(RestaurantPortions.HerringPortions(5)==2,"two herring per portion, odd fish retained");
            Check(RestaurantPortions.Yield(Species.Cod,4.5f,PreparedForm.Fillet)==11,"4.5 kg cod gives eleven fillets");
            Check(RestaurantPortions.Yield(Species.Cod,4.5f,PreparedForm.Fillet,true)==12,"captain cut adds one");
            Check(RestaurantPortions.Yield(Species.Cod,1,PreparedForm.Stock)==4,"stock four bowls/kg");
            Check(RestaurantPortions.Yield(Species.Cod,3.99f,PreparedForm.Platter)==0&&RestaurantPortions.Yield(Species.Cod,4,PreparedForm.Platter)==1,"platter threshold");
            Check(RestaurantPortions.Yield(Species.Crab,1.2f,PreparedForm.Crab)==1,"one crab one portion");
            Check(RestaurantPortions.Yield(Species.GiantSquid,.9f,PreparedForm.Squid)==3,"squid 0.3 kg per portion");
            var l=Kit();var f=Forecast(l);f.Lock();
            var fish=Enumerable.Range(0,20).Select(i=>new RestaurantCatch{Species=Species.Pollock,Kg=1.2f}).ToArray();
            var tight=RestaurantPortions.Suggest(fish,f,l,PrepMargin.Tight);var extra=RestaurantPortions.Suggest(fish,f,l,PrepMargin.TwentyPercent);
            Check(tight.Portions<=15&&extra.Portions<=15,"fridge cap applies all forms including offcuts");
            Check(extra.Market.Count+extra.Stock.Where(s=>s.Form==PreparedForm.Fillet).Sum(s=>s.Count)/3<=20,"whole fish allocated once");
            Check(extra.Unavailable.ContainsKey(PreparedForm.Whole)&&extra.Unavailable[PreparedForm.Whole].Contains("grill"),"unavailable form reason");
            Check(extra.MarketCoins==(int)Math.Round(extra.Market.Sum(x=>GameData.Get(x.Species).PricePerKg*x.Kg*.5f)),"whole market value at half current prices");
            var catStock=Stock(3,4);Check(RestaurantPortions.FeedCats(catStock)==7&&RestaurantPortions.FeedCats(catStock)==0,"cats transfer exactly once");
        }
        static void ForecastChecks()
        {
            var l=Kit();
            for(int seed=0;seed<1000;seed++){
                var f=Forecast(l,seed,3);Check(f.GuestRange.Contains(f.Guests.Count),"seed "+seed+" departure range");
                int max=(int)Math.Floor(f.BaseCount*.2f);Check(!f.MiraChange(max+1),"seed "+seed+" growth capped");
                Check(f.MiraChange(max)&&f.MiraChange(-1)&&!f.MiraChange(0),"seed "+seed+" at most two calls");
                Check(f.Guests.Count<=f.BaseCount+max,"seed "+seed+" total growth");
                foreach(var group in f.Guests.GroupBy(g=>(g.Species,g.Dish)))Check(f.DishRanges[group.Key].Contains(group.Count()),"seed "+seed+" dish range");
                foreach(var g in f.Guests)Check(l.CanCook(g.Dish),"seed "+seed+" kitchen filter");
                int booked=f.Guests.Count;f.Lock();Check(f.WalkIns<=Math.Floor(booked*.1f)&&f.GuestRange.Contains(f.Guests.Count),"seed "+seed+" locked walk-ins/range");
                var truth=f.Guests.Select(g=>g.Id).ToArray();f.Lock();Check(!f.MiraChange(1)&&f.Guests.Select(g=>g.Id).SequenceEqual(truth),"seed "+seed+" idempotent immutable lock");
            }
            var a=Forecast(l);var b=Forecast(l);a.Lock();b.Lock();Check(a.Guests.Select(g=>(g.Id,g.Group,g.Species,g.Dish,g.Drink,g.Coffee)).SequenceEqual(b.Guests.Select(g=>(g.Id,g.Group,g.Species,g.Dish,g.Drink,g.Coffee))),"seeded entire guest list");
            RestaurantForecast special=null;GuestOrder request=null;
            for(int seed=0;seed<100&&request==null;seed++){special=Forecast(l,seed,8);request=special.Guests.FirstOrDefault(g=>g.Special);}
            Check(request!=null&&special.SpecialRequest(request.Id,true)&&special.Guests.Single(g=>g.Id==request.Id).Accepted,"accept special");
            Check(special.SpecialRequest(request.Id,false)&&!special.Guests.Single(g=>g.Id==request.Id).Accepted,"decline special");special.Lock();Check(!special.SpecialRequest(request.Id,true),"special locks on departure");
        }
        static void EdgeChecks()
        {
            var l=Large(2);
            foreach(var i in l.Active.Where(i=>i.Id==ItemId.Stove||i.Id==ItemId.SoupKettle).ToArray())Check(l.Store(i.Uid).Ok,"store baseline stove/kettle for mixed appliance check");
            Check(l.Buy(ItemId.Oven,0,4).Ok&&l.Buy(ItemId.Steamer,0,3).Ok,"oven and crab-only kitchen fixture");
            for(int seed=0;seed<100;seed++){
                var f=new RestaurantForecast(seed,2,DayOfWeek.Friday,Weather.Fair,new[]{(Species.Cod,1f),(Species.Crab,1f)},l);f.Lock();
                Check(f.Guests.All(g=>l.CanCook(g.Dish)),"mixed platter-only and crab forecast remains cookable "+seed);
            }
            int specials=0;
            for(int seed=0;seed<20;seed++){
                var k=Large();var f=new RestaurantForecast(seed,1,DayOfWeek.Friday,Weather.Fair,new[]{(Species.Cod,1f)},k);
                foreach(var g in f.Guests.Where(g=>g.Special))f.SpecialRequest(g.Id,true);f.Lock();
                var regular=Stock(40,20);var special=Stock(40,20);regular[0].Species=Species.Cod;special[0].Species=Species.Cod;special[0].Special=true;
                var a=new RestaurantSim(seed,k,f,regular,Team(k,2,3)){Breakdowns=false}.RunToClose();
                var b=new RestaurantSim(seed,k,f,special,Team(k,2,3)){Breakdowns=false}.RunToClose();
                Check(a.SpecialServed==0,"accepted special request cannot turn ordinary fish into a special "+seed);
                specials+=b.SpecialServed;
            }
            Check(specials>0,"actual special-catch provenance earns a special delivery");
        }
        static RestaurantSim Sim(RestaurantLayout l,int seed,int pop,int cooks,int waiters,int fillets,int soup)
        {
            var f=Forecast(l,seed,pop);f.Lock();return new RestaurantSim(seed,l,f,Stock(fillets,soup),Team(l,cooks,waiters)){Breakdowns=false};
        }
        static void SimChecks()
        {
            var l=Kit();var a=Sim(l,11,1,1,1,9,6);var b=Sim(Kit(),11,1,1,1,9,6);
            Debug.Log("[Catchline] SimChecks first seeded night");var ar=a.RunToClose();Debug.Log("[Catchline] SimChecks first night closed");while(!b.Finished&&b.Seconds<650)b.Tick(.5f);
            Check(b.Finished,"baseline bounded close");
            Check(JsonUtility.ToJson(ar)==JsonUtility.ToJson(b.Result),"determinism across 1s and .5s calls");
            Check(a.Groups.All(g=>g.Phase==GroupPhase.Gone)&&ar.Guests==ar.Served+ar.Left,"stage1 Mira + two crew all guests gone");
            Check(ar.Cats>=0&&a.Stock.Count==0,"leftovers transferred at closing");
            Check(a.Staff.Any(s=>s.Metres>0),"staff really walk");
            Check(RestaurantStaff.FromCard(new CardState("mira"),Job.Reception,l.Door).NativeJob==Job.Reception,"Mira card remains the host at native speed");
            var native=new RestaurantStaff{Job=Job.Cook,NativeJob=Job.Cook};float own=native.Rate;native.Job=Job.Waiter;
            Check(Math.Abs(native.Rate/own-.7f)<.0001f&&Math.Abs(native.WalkSpeed/(GameData.WalkSpeed*own)-.7f)<.0001f,"off-role work AND walk 70 percent");
            native.Rarity=CardRarity.Gold;native.Level=10;Check(native.Rate>.7f,"rarity and level use shared speed math");
            // Same five specialists, only job assignment differs; aggregate ten seeds, so no cherry-picked night.
            Debug.Log("[Catchline] SimChecks specialist capacity");int four=0,two=0;
            for(int seed=0;seed<10;seed++){Debug.Log("[Catchline] specialist seed "+seed);
                var ll=Large();var ff=Forecast(ll,seed,8);ff.Lock();
                var crew=Team(ll,2,3);var badCrew=Team(ll,2,3);
                badCrew[4].Job=Job.Cook;badCrew[5].Job=Job.Cook;
                four+=new RestaurantSim(seed,ll,ff,Stock(36,24),badCrew){Breakdowns=false}.RunToClose().Served;
                two+=new RestaurantSim(seed,ll,ff,Stock(36,24),crew){Breakdowns=false}.RunToClose().Served;
            }
            Check(four<=two,"4 cooks/1 waiter cannot improve service over 2 cooks/3 waiters across 10 seeds: "+four+" <= "+two);
            Debug.Log("[Catchline] SimChecks soup and commands");var soupSim=Sim(Kit(),7,1,1,1,0,15);var soup=soupSim.RunToClose();Check(soup.Substitutions>0&&soup.DishCoins>0,"sold-out defaults to cooked soup and pays");
            var all=new RestaurantForecast(1,2,DayOfWeek.Friday,Weather.Fair,new[]{(Species.Cod,1f)},Kit());all.Lock();
            var plenty=new RestaurantSim(1,Kit(),all,Stock(0,15),Team(Kit(),1,1)){Breakdowns=false};plenty.CloseDoor();var cr=plenty.RunToClose();
            Check(cr.Cats==15&&cr.Served==0&&cr.Left==cr.Guests,"closed door leaves all stock to cats");
            var manager=Sim(Kit(),3,1,1,1,9,6);int stove=manager.Layout.Active.First(i=>i.Id==ItemId.Stove).Uid;
            Check(manager.Break(stove)&&manager.CaptainHoldFix(stove,5)&&manager.Broken.Contains(stove),"captain partial hold");
            Check(manager.CaptainHoldFix(stove,5)&&!manager.Broken.Contains(stove),"captain completed repair");
            Check(manager.Pin(manager.Layout.Active.First(i=>i.Id==ItemId.Table2).Uid)&&!manager.Pin(stove),"pin tables only");
            Check(!manager.SetJob("cook0",Job.Waiter)&&manager.SetJob("cook0",Job.Cook)&&!manager.SetJob("missing",Job.Cook),"fixed card roles reject reassignment");
            var repair=Sim(Kit(),4,1,1,1,9,6);repair.Staff.Add(new RestaurantStaff{Id="fixer",NativeJob=Job.Handyman,Job=Job.Handyman,Tile=repair.Layout.PassKitchen});repair.Break(stove);
            for(int i=0;i<120&&repair.Broken.Count>0;i++)repair.Tick(.25f);
            Check(repair.Broken.Count==0&&repair.Staff.Last().Metres>0,"handyman walks and repairs");
        }
        static RestaurantSim Fresh(int seed=91)
        {
            var l=Kit();var f=Forecast(l,seed);f.Lock();
            return new RestaurantSim(seed,l,f,Stock(9,6),new[]{RestaurantStaff.FromCard(new CardState("mira"),Job.Reception,l.Door),RestaurantStaff.Captain(l.Door)}){Breakdowns=false};
        }
        static void PlayChecks()
        {
            var a=Fresh();var b=Fresh();var actions=new HashSet<string>();
            Check(a.Staff.Count==2&&a.Staff.Count(s=>s.Id=="captain")==1,"fresh save has one captain and Mira only");
            Check(a.Groups.All(g=>g.Arrival<480)&&a.Groups.Count>=12&&a.Groups.Count<=26,"roughly four groups per game hour before 22:00");
            while(!a.Finished&&a.Seconds<650){a.Tick(.25f);actions.Add(a.Staff.Single(s=>s.Id=="captain").Action);}
            b.RunToClose();Check(JsonUtility.ToJson(a.Result)==JsonUtility.ToJson(b.Result),"helper determinism across quarter and one second frames");
            Check(actions.Any(x=>x.StartsWith("Cook"))&&actions.Contains("Serve fish")&&actions.Contains("Clear table"),"one captain actually cooks serves and clears");
            Check(a.Result.Served>0&&a.Seconds==600&&a.Hour==23&&a.DoorClosed,"600 second night closes at 23 with actual meals");
            Check(a.Result.Stars>=1&&a.Result.Stars<=5,"stars remain in one to five scale");
            foreach(string id in new[]{"ines","mats"})Check(RestaurantStaff.FromCard(new CardState(id),Job.Cook,Kit().Door).Job==Job.Barista,id+" fixed coffee role");
            var repair=Fresh();int stove=repair.Layout.Active.First(i=>i.Id==ItemId.Stove).Uid;bool broke=false;
            while(!repair.Finished&&repair.Seconds<650){repair.Tick(.25f);if(!broke&&repair.Staff.Last().Action.StartsWith("Cook")){repair.Break(stove);broke=true;}}
            Check(broke&&!repair.Broken.Contains(stove)&&repair.Result.Served>0,"helper interrupts its own blocked cook to repair and resume service");
            var bad=Fresh();bad.CloseDoor();bad.RunToClose();Check(bad.Result.PopularityGain<0,"lost guests reduce popularity");
            // Controlled till fixtures isolate cold price/stars from seeded queue timing.
            RestaurantSim Payment(bool cold){var sim=Fresh();var g=sim.Groups[0];sim.Groups.Clear();sim.Groups.Add(g);g.Arrival=0;g.TableUid=sim.Layout.Active.First(i=>i.Id==ItemId.Table2).Uid;g.Phase=GroupPhase.Payment;
                g.Tickets.Clear();foreach(var o in g.Guests)g.Tickets.Add(new ServiceTicket{Order=o,Dish=Dish.PanFish,Species=Species.Pollock,Phase=TicketPhase.Delivered,Cold=cold});return sim;}
            var hot=Payment(false);var cold=Payment(true);hot.RunToClose();cold.RunToClose();
            Check(cold.Result.DishCoins<hot.Result.DishCoins&&cold.Result.Stars<hot.Result.Stars,"cold plates reduce pay and stars");
            var till=Payment(false);int uid=till.Layout.Active.First(i=>i.Id==ItemId.Reception).Uid;till.Break(uid);till.RunToClose();Check(!till.Broken.Contains(uid)&&till.Result.DishCoins>0,"captain repairs broken till so Mira can collect payment");
        }
        public static void Run()
        {
            Directory.CreateDirectory(Out);assertions=0;checks.Clear();
            try {LayoutChecks();Debug.Log("[Catchline] Restaurant layout passed");PortionChecks();Debug.Log("[Catchline] Restaurant portions passed");ForecastChecks();Debug.Log("[Catchline] Restaurant 1000 forecasts passed");SimChecks();Debug.Log("[Catchline] Simulation baseline passed");EdgeChecks();Debug.Log("[Catchline] Edge baseline passed");PlayChecks();Debug.Log("[Catchline] Restaurant service passed");Reports();}
            finally{File.WriteAllLines(Out+"/checks.txt",checks);}
            File.WriteAllText(Out+"/checks.json","{\"passed\":true,\"assertions\":"+assertions+"}");
            Debug.Log("[Catchline] RESTAURANT CHECKS PASSED: "+assertions);Debug.Log("[Catchline] Snapshot written to "+Out+"/checks.json");
        }
        public static void Regression()
        {
            Run();JigBoatChecks.Regression();GullCoastLifeChecks.Run();
            File.WriteAllText(Out+"/regression-passed.txt","Restaurant + JigBoat full regression (crew abilities, M2, bites, cages, tutorial, map nav, harbour trips) + Gull coast life passed.\n");
            Debug.Log("[Catchline] RESTAURANT FULL REGRESSION PASSED. Snapshot written to "+Out+"/regression-passed.txt");
        }
        public static void PrepareWorldAssets()
        {
            const string root="Assets/Art/Models/Restaurant/";
            foreach(string p in Directory.GetFiles(root,"*.png",SearchOption.AllDirectories)){
                var ti=(TextureImporter)AssetImporter.GetAtPath(p);ti.sRGBTexture=!p.Contains("Surface");ti.mipmapEnabled=true;ti.maxTextureSize=2048;ti.SaveAndReimport();
            }
            var shader=Shader.Find("Catchline/RestaurantAtlas");Check(shader!=null,"restaurant atlas shader imports");
            string matPath=root+"RestaurantAtlas.mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(matPath);
            if(mat==null){mat=new Material(shader);AssetDatabase.CreateAsset(mat,matPath);}mat.shader=shader;
            mat.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(root+"textures/Restaurant_BaseColor.png"));
            mat.SetTexture("_SurfaceMap",AssetDatabase.LoadAssetAtPath<Texture2D>(root+"textures/Restaurant_Surface.png"));
            EditorUtility.SetDirty(mat);
            foreach(string disk in Directory.GetFiles(root,"*.fbx",SearchOption.AllDirectories)){
                string p=disk.Replace('\\','/');var mi=(ModelImporter)AssetImporter.GetAtPath(p);
                if(p.Contains("/Guests/")){mi.importAnimation=true;mi.animationType=ModelImporterAnimationType.Legacy;mi.SaveAndReimport();continue;}
                foreach(var source in AssetDatabase.LoadAllAssetsAtPath(p).OfType<Material>())mi.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),source.name),mat);mi.SaveAndReimport();
            }
            AssetDatabase.SaveAssets();ArtImport.BuildLibrary();
            Debug.Log("[Catchline] Snapshot written to "+matPath);
        }
        public static void PlayBuild()
        {
            if(!Application.dataPath.Replace('\\','/').Contains("Catchline-sim/"))throw new Exception("Scratch only");
            Run();PrepareWorldAssets();Time.timeScale=1;
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var game=new GameObject("Restaurant SessionOnly native HUD").AddComponent<VoyageGame>();game.SessionOnly=true;
            new GameObject("Restaurant acceptance runner").AddComponent<RestaurantPlayCapture>();
            const string fixture="Assets/RestaurantPlayAcceptance.unity";EditorSceneManager.SaveScene(scene,fixture);
            var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{fixture},locationPathName="Builds/RestaurantPlay/Catchline.exe",target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
            Check(result.summary.result==UnityEditor.Build.Reporting.BuildResult.Succeeded,"restaurant native build");
            File.WriteAllText(Out+"/build.txt",result.summary.result+" bytes="+result.summary.totalSize+" errors="+result.summary.totalErrors);
            Debug.Log("[Catchline] Snapshot written to Builds/RestaurantPlay/Catchline.exe");
        }
        public static void FeelBuild()
        {
            var path=Application.dataPath.Replace('\\','/');if(!path.Contains("Catchline-lead-sim/")&&!path.Contains("Catchline-sim/"))throw new Exception("Scratch only");
            const string folder="C:/Users/momoy/Projects/Catchline/docs/screens/restaurant-feel-1";Directory.CreateDirectory(folder);ArtImport.BuildLibrary();Time.timeScale=1;
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var game=new GameObject("Restaurant feel SessionOnly native HUD").AddComponent<VoyageGame>();game.SessionOnly=true;
            new GameObject("Restaurant feel acceptance runner").AddComponent<RestaurantPlayCapture>();
            const string fixture="Assets/RestaurantFeelAcceptance.unity";EditorSceneManager.SaveScene(scene,fixture);
            var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{fixture},locationPathName="Builds/RestaurantFeel/Catchline.exe",target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
            Check(result.summary.result==UnityEditor.Build.Reporting.BuildResult.Succeeded,"restaurant feel native build");
            File.WriteAllText(folder+"/build.txt",result.summary.result+" bytes="+result.summary.totalSize+" errors="+result.summary.totalErrors);
            Debug.Log("[Catchline] RESTAURANT FEEL BUILD PASS Builds/RestaurantFeel/Catchline.exe");
        }
        // Same small room, stock, forecast and seed for each crew. This is evidence for the lead, not tuning.
        public static void FeelBalance()
        {
            const string folder="C:/Users/momoy/Projects/Catchline/docs/screens/restaurant-feel-1";Directory.CreateDirectory(folder);
            var text=new StringBuilder("# Restaurant feel: balance, no tuning\n\n20 seeds (0–19), fixed .25s ticks, Friday/fair/popularity1. Starting kit, 9 pollock fillets + 6 herring stock; no extra fixtures/upgrades. Breakdowns disabled, events enabled. Crew use default CardState rarity/level and fixed native jobs; captain is the helper. Missing drinks fridge is part of the current starter room, so drinks cannot be fabricated.\n\nGave-up = guests in tables with Why=gave-up. Left at door = Gone with no assigned table. Served/guests and stars are the sim's own final totals (stars guest weighted). Idle% = fraction of 600 seconds with no accepted task, sampled before every tick; walking/preparing/waiting on a task counts busy. Dash = member absent.\n\n| Crew | Seed | Served / guests | Gave-up | Left at door | Cold dishes | Mean stars | Net coins | Mira idle% | Captain idle% | Cook idle% | Waiter idle% | Barista idle% |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n");
            string[] names={"Mira + captain","+ cook (Dirk)","+ cook + waiter (Ana)","+ cook + waiter + barista (Ines)"};
            for(int crew=0;crew<4;crew++){
                int served=0,guests=0,gaveup=0,door=0,cold=0,coins=0;float stars=0;var idleSum=new float[5];
                for(int seed=0;seed<20;seed++){
                    var l=Kit();var f=Forecast(l,seed);f.Lock();var staff=new List<RestaurantStaff>{RestaurantStaff.FromCard(new CardState("mira"),Job.Reception,l.Door),RestaurantStaff.Captain(l.Door)};
                    if(crew>=1)staff.Add(RestaurantStaff.FromCard(new CardState("dirk"),Job.Cook,l.PassKitchen));
                    if(crew>=2)staff.Add(RestaurantStaff.FromCard(new CardState("ana"),Job.Waiter,l.Door));
                    if(crew>=3)staff.Add(RestaurantStaff.FromCard(new CardState("ines"),Job.Barista,l.Door));
                    var sim=new RestaurantSim(seed,l,f,Stock(9,6),staff){Breakdowns=false};var idle=new float[5];
                    while(!sim.Finished&&sim.Seconds<650){for(int i=0;i<staff.Count;i++)if(!staff[i].Busy)idle[i]+=.25f;sim.Tick(.25f);}
                    Check(sim.Finished&&sim.Result.Guests==sim.Result.Served+sim.Result.Left,"feel balance bounded/conserved crew="+crew+" seed="+seed);
                    var r=sim.Result;int give=sim.Groups.Where(g=>g.Why=="gave-up").Sum(g=>g.Count),atDoor=sim.Groups.Where(g=>g.Phase==GroupPhase.Gone&&g.TableUid==0).Sum(g=>g.Count);
                    text.Append(FormattableString.Invariant($"| {names[crew]} | {seed} | {r.Served} / {r.Guests} | {give} | {atDoor} | {r.ColdDishes} | {r.Stars:F3} | {r.NetCoins} |"));
                    for(int i=0;i<5;i++){float percent=idle[i]*100/sim.Seconds;idleSum[i]+=percent;text.Append(i<staff.Count?FormattableString.Invariant($" {percent:F2} |"):" — |");}text.Append('\n');
                    served+=r.Served;guests+=r.Guests;gaveup+=give;door+=atDoor;cold+=r.ColdDishes;coins+=r.NetCoins;stars+=r.Stars*r.Guests;
                }
                text.Append(FormattableString.Invariant($"| **{names[crew]} aggregate** | **20 seeds** | **{served} / {guests}** | {gaveup} | {door} | {cold} | {stars/Math.Max(1,guests):F3} | {coins} |"));
                for(int i=0;i<5;i++)text.Append(i<crew+2?FormattableString.Invariant($" {idleSum[i]/20:F2} |"):" — |");text.Append('\n');
            }
            text.Append("\nAggregate counts/coins are totals; aggregate idle% is the mean across seeds. No balance constants or sim rules changed.\n");
            File.WriteAllText(folder+"/balance.md",text.ToString());Debug.Log("[Catchline] RESTAURANT FEEL BALANCE PASS: 80 nights; "+folder+"/balance.md");
        }
        [Serializable] sealed class ReportsFile {public List<NightResult> Nights=new List<NightResult>();}
        public static void Reports()
        {
            var text=new StringBuilder("# Restaurant core: headless service reports\n\nProvisional tuning; no production wiring. Fixed 0.25 s ticks; random breakdowns disabled in pacing comparisons (separate repair checks). Each scenario uses its declared seed.\n\n");
            text.Append("| Scenario | Seed | Guests | Served | Left | Dishes | Drinks | Tips | Staple cost | Net | Stars | Cats | Seconds | Metres |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|\n");
            var output=new ReportsFile();
            for(int scenario=0;scenario<6;scenario++){
                int seed=scenario>=4?102:100+scenario;
                int stage=scenario<4?scenario+1:3;var l=stage==1?Kit():Large(stage);
                int pop=stage==1?1:stage==2?3:stage==3?5:8;
                var f=Forecast(l,seed,pop);f.Lock();
                int cap=l.FridgeCapacity;int portions=scenario==4?6:scenario==5?cap:Math.Min(cap,(int)Math.Ceiling(f.Guests.Count*1.1f));
                int soup=portions/3;var stock=Stock(portions-soup,soup);
                var team=stage==1?Team(l,1,1):stage==2?Team(l,1,2,true):stage==3?Team(l,2,3,true):Team(l,3,3,true,true);
                // New game: exactly Mira and one captain, with no invisible second cook.
                if(stage==1)team=new List<RestaurantStaff>{team[0],RestaurantStaff.Captain(l.Door)};
                string name=scenario==4?"Under-prepped (stage3)":scenario==5?"Over-prepped (stage3)":"Stage "+stage+" / "+(stage==1?"Skiff":stage==2?"Compact fisher":stage==3?"Prep fisher":"Buoy fisher");
                var sim=new RestaurantSim(seed,l,f,stock,team){Breakdowns=false};var r=sim.RunToClose();output.Nights.Add(r);
                string metres=string.Join("; ",r.Walking.Select(w=>w.Id+" "+w.Metres.ToString("F1")));
                text.Append($"| {name} | {seed} | {r.Guests} | {r.Served} | {r.Left} | {r.DishCoins} | {r.DrinkCoins} | {r.Tips} | {r.StapleCosts} | {r.NetCoins} | {r.Stars:F2} | {r.Cats} | {r.Seconds:F2} | {metres} |\n");
                Check(r.Guests==r.Served+r.Left,"report "+name+" guest conservation");
                Check(portions==r.Served+r.Cats,"report "+name+" prepared portions either served or reach cats");
            }
            text.Append("\nPLAY-1 rules: 600 seconds, 18-22 arrivals and 23 closing; stage1 Mira + one captain helper. Fixed card roles; cold after 30s, payment at till, repairable breakdowns and 1-5 stars. Plates/sink/trash are simplified to clearing, not finite supply lines. Other report stages use specialists at their native jobs. No player-save/UI integration claimed.\n\n");
            text.Append("Integration API: standalone RestaurantState + RestaurantLayout; forecast takes ground weighted (Species, weight) pairs, exposes copied guests and ranges, supports MiraChange/SpecialRequest/Lock. RestaurantPortions.Suggest produces fridge stock and untouched market fish. RestaurantSim.Tick accepts elapsed seconds, fixed steps internally; SetJob, Pin, Seat, CloseDoor, ChooseSubstitute, Break, CaptainHoldFix are manager commands. Busy staff finish their accepted task before taking the new role. RunToClose is the headless runner. Result includes gross/net split and each staff distance.\n\n");
            text.Append("Layout expansion inserts kitchen columns at the pass and shifts guest-side items together, preserving every UID and relative guest positions. Existing items are never sold or lost. Terrace width is3 at stages2-4. Access tiles are the nearest reachable cardinal neighbours of footprints; table access represents all chairs (no separate chair occupancy in v1). Wall fixtures share floor tiles; the vertical pass has a front aisle crossing. Layout must remain fixed during service.\n\n");
            text.Append("Tuning defaults live only in RestaurantTuning. Plan-defined values: 600s night, 8 soup/batch, 15 portions/fridge, fixed jobs, half-price market, dish3x raw, growth20%, walk-ins10%, portion yields. Unspecified timings, prices, forecast slack, stock offcut mass20%, base guests/popularity, stars/tips and failure probability are provisional and require lead/pacing review. No finite plates/sink/trash, events, critic, ability twins, live save integration or UI.\n\n");
            text.Append("[View evidence](view/README.md), [check details](checks.txt), [machine reports](nights.json). Existing regression status is in regression-passed.txt only after that suite completes.\n");
            File.WriteAllText(Out+"/README.md",text.ToString());File.WriteAllText(Out+"/nights.json",JsonUtility.ToJson(output,true));
        }
    }
}

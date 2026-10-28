using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game.Restaurant
{
    public enum GroupPhase { NotArrived, Queue, Seating, Order, Drinks, Kitchen, Eating, Coffee, Clearing, Gone, Payment }
    public enum TicketPhase { Choice, Waiting, Cooking, Ready, Serving, Delivered, Abandoned }
    public sealed class ServiceTicket
    {
        public GuestOrder Order; public Dish Dish; public Species Species; public TicketPhase Phase;
        public float ChoiceAt, ReadyAt, DeliveredAt; public bool Substitute, CaptainCut, SpecialServed, Cold; public float CookQuality;
    }
    public sealed class ServiceGroup
    {
        public int Id, TableUid; public List<GuestOrder> Guests=new List<GuestOrder>();
        public List<ServiceTicket> Tickets=new List<ServiceTicket>();
        public GroupPhase Phase; public float Arrival, SeatedAt, LastPatienceBoost, EatUntil, ServedAt;
        public bool Reserved, DrinksDelivered, CoffeeDelivered, Paid; public int Stars;
        // What the table will say about the night (closing reviews): gave-up, missing, cold, swap, slow, special, captain, great.
        public string Why;
        // Tonight's light events (design section 6): a birthday table tips double when happy; a regular who gets a good
        // night spreads the word (popularity).
        public bool Birthday, Regular;
        // Service v2 upsell: the round the table waves for (offered once), open until UpsellUntil; UpsellSold pops "+coins".
        public bool UpsellOffered; public Dish Upsell; public float UpsellUntil=-1, UpsellSoldAt=-1; public int UpsellCoins;
        public bool GullStole; // a gull got to the plate before anyone shooed it
        public int Count=>Guests.Count;
    }
    // The work a staff member tries, in their priority order (S9 crew priorities); the first that finds work wins.
    public enum Work { Seat, Till, TakeOrder, Cook, Serve, Clear, Drinks, Repair }
    public sealed class RestaurantStaff
    {
        public string Id; public Job NativeJob, Job; public CardRarity Rarity; public int Level=1, Stars;
        public Work[] Order;
        // Each job's own work first (the order the night ran before priorities existed), then two ways to help out.
        public static Work[] DefaultOrder(Job job)=>job switch{
            Job.Reception=>new[]{Work.Till,Work.TakeOrder,Work.Seat},
            Job.Cook=>new[]{Work.Cook,Work.Serve,Work.Clear},
            Job.Waiter=>new[]{Work.Serve,Work.Clear,Work.Drinks},
            Job.Barista=>new[]{Work.Drinks,Work.Serve,Work.Clear},
            Job.Handyman=>new[]{Work.Repair,Work.Clear,Work.Serve},
            _=>null};
        public static string Label(Work w)=>w switch{Work.Seat=>"Seat guests",Work.Till=>"Till",Work.TakeOrder=>"Take orders",Work.Cook=>"Cook orders",
            Work.Serve=>"Serve",Work.Clear=>"Clear tables",Work.Drinks=>"Drinks",_=>"Repairs"};
        public Vector2Int Tile; public Vector2 Position, PrevPosition; public float Metres;
        // Where to draw this frame: the fixed clock moves Position in 250 ms steps, so drawing it raw stutters.
        public Vector2 DrawPosition(float alpha)=>Vector2.Lerp(PrevPosition,Position,alpha);
        internal StaffTask Task;
        public bool Busy=>Task!=null;
        public float BusyProgress=>Task==null?0:Task.Progress;
        public Vector2Int Target=>Task?.Current?.Target ?? Tile;
        public bool Walking=>Task?.Path!=null&&Task.Path.Count>0;
        public string Action=>Task?.Label ?? "Idle";
        public float Mult=>CardProgression.WorkMult(Rarity,Level,Stars);
        public float Boost=1;
        public float Rate=>WorkSpeed.Rate(Job==NativeJob?100:RestaurantTuning.OffRole*100,Mult)*Boost;
        public float WalkSpeed=>WorkSpeed.Walk(Job==NativeJob?100:RestaurantTuning.OffRole*100,Mult)*Boost*RestaurantTuning.WalkBoost;
        public static RestaurantStaff Captain(Vector2Int start)=>new RestaurantStaff{Id="captain",Job=Job.Helper,NativeJob=Job.Helper,Tile=start,Position=start,Boost=RestaurantTuning.CaptainBoost};
        public static RestaurantStaff FromCard(CardState card,Job job,Vector2Int start) {
            var fixedJob=card.Id=="mira"?Job.Reception:card.Id=="ines"||card.Id=="mats"?Job.Barista:RestaurantData.NativeJob(card.Def.Role);
            return new RestaurantStaff {Id=card.Id,NativeJob=fixedJob,Job=fixedJob,Rarity=card.Rarity,Level=card.Level,Stars=card.Stars,Tile=start,Position=start};
        }
    }
    internal sealed class StaffLeg { public Vector2Int Target; public float Seconds; public int Appliance; public Action Done; }
    internal sealed class StaffTask
    {
        public string Label; public Queue<StaffLeg> Legs=new Queue<StaffLeg>();public StaffLeg Current;
        public Queue<Vector2Int> Path; public float Remaining, Segment;
        public Action Complete, Cancel;
        public float Total, Elapsed;
        public float Progress=>Total<=0?0:Mathf.Clamp01(Elapsed/Total);
    }
    [Serializable] public sealed class NightResult
    {
        public int Guests, Served, Left, DishCoins, DrinkCoins, Tips, StapleCosts, Cats, Substitutions, SpecialServed, ColdDishes, HappyRegulars, WalkIns, Combos, Staples, Upsells, GullsShooed, GullSteals; // Staples: bread and fries plates served (pantry, not tonight's fish)
        public float PopularityGain;
        public float Stars, Seconds;
        public List<StaffDistance> Walking=new List<StaffDistance>();
        public int Coins=>DishCoins+DrinkCoins+Tips;
        public int NetCoins=>Coins-StapleCosts;
        public string LayoutTip;
    }
    [Serializable] public sealed class StaffDistance {public string Id;public float Metres;}

    // Fixed 250 ms clock; caller frame size never changes event ordering. This is headless and does not
    // read Time, Unity random, scene objects, GameState, files, or the player's save.
    public sealed class RestaurantSim
    {
        public readonly RestaurantLayout Layout;
        public readonly List<RestaurantStaff> Staff;
        public readonly List<ServiceGroup> Groups=new List<ServiceGroup>();
        public readonly List<PortionStock> Stock;
        public readonly NightResult Result=new NightResult();
        public readonly HashSet<int> Broken=new HashSet<int>();
        readonly HashSet<int> stations=new HashSet<int>();
        readonly Dictionary<(Vector2Int,Vector2Int),List<Vector2Int>> routes=new();
        readonly Dictionary<(int,Vector2Int),Vector2Int?> access=new();
        readonly Dictionary<int,float> captainRepairs=new Dictionary<int,float>();
        readonly Dictionary<string,StaffTask> suspended=new Dictionary<string,StaffTask>();
        readonly System.Random random; readonly Weather weather;
        double accumulator;int ticks, soupReady, waste, pin;
        public float Seconds=>ticks*RestaurantTuning.TickSeconds;
        // Fraction of the next fixed step already elapsed; presentation interpolates staff between PrevPosition and Position.
        public float Alpha=>Mathf.Clamp01((float)(accumulator/RestaurantTuning.TickSeconds));
        // A seated table's patience left (0..1). Only the wait for food counts: guests who are eating, having coffee or
        // paying never walk out. The rules and every meter read this one number.
        public float Patience(ServiceGroup g)
        {
            if(g.Phase<GroupPhase.Order||g.Phase>GroupPhase.Kitchen)return 1;
            return Mathf.Clamp01(1-(Seconds-g.SeatedAt)/(RestaurantTuning.TablePatience+g.LastPatienceBoost+Layout.Ambience*RestaurantTuning.AmbiencePatience));
        }
        public float Hour=>18+Math.Min(1,Seconds/RestaurantTuning.NightSeconds)*5;
        public bool DoorClosed {get;private set;}
        public bool Finished {get;private set;}
        public bool Breakdowns=true;
        // Mira's supplier deal (design 14.3): coins added to every fish plate tonight.
        public int PriceBonus;
        // Birthday tables and regulars; rolled on the first tick (after the caller's initializer) from their own random,
        // so the rest of the night plays out exactly as it would without them.
        public bool Events=true; bool eventsRolled; readonly int eventSeed;
        // Service v2: walk-ins all night (WalkInPace scales their rate; 0 turns them off), and the captain as the player's
        // hands: with CaptainHandsOn he does only what the player taps, in order (up to three taps ahead).
        public float WalkInPace=1; public bool CaptainHandsOn, CaptainAuto; // CaptainAuto: no taps queued, he helps where it hurts (bots, captures)
        // Gulls (GullPace scales how often; 0, the default, keeps them away): the table one stands on, and the last one to leave.
        public float GullPace; public int GullTable, GullLeftTable; public float GullLandedAt=-1, GullLeftAt=-1; public bool GullLeftFed; float nextGull=-1;
        readonly System.Random walkRandom, upsellRandom, gullRandom; float nextWalkIn=-1; int walkInIds=1000000;
        readonly List<int> captainOrders=new List<int>();
        public IReadOnlyList<int> CaptainOrders=>captainOrders;
        // The last trip that served two or more tables at once: plates and the tip it paid (the UI pops it).
        public int LastCombo, LastComboTip; public float LastComboAt=-1;
        sealed class Cooking{public int Uid;public ServiceTicket Ticket;public ServiceGroup Group;public PortionStock Taken;public float ReadyAt;}
        readonly List<Cooking> cooking=new List<Cooking>();
        public int PortionsTaken, SoupBowls; // bookkeeping for the checks: portions out of the fridge, bowls served from a batch
        void RollEvents()
        {
            eventsRolled=true;if(!Events)return;
            var r=new System.Random(eventSeed*31+17);
            var pairs=Groups.Where(g=>g.Count>=2).ToList();
            if(pairs.Count>0&&r.NextDouble()<RestaurantTuning.BirthdayChance)pairs[r.Next(pairs.Count)].Birthday=true;
            var small=Groups.Where(g=>g.Count<=2&&!g.Birthday).ToList();
            if(small.Count>0&&r.NextDouble()<RestaurantTuning.RegularChance)small[r.Next(small.Count)].Regular=true;
        }
        public RestaurantSim(int seed,RestaurantLayout layout,RestaurantForecast forecast,IEnumerable<PortionStock> stock,IEnumerable<RestaurantStaff> staff)
        {
            if(!forecast.Locked)throw new ArgumentException("Lock Mira's plan before service");
            if(!layout.Validate().Ok)throw new ArgumentException(layout.Validate().Message);
            Layout=layout;weather=forecast.Weather;random=new System.Random(seed);eventSeed=seed;walkRandom=new System.Random(seed*13+7);upsellRandom=new System.Random(seed*7+3);gullRandom=new System.Random(seed*5+11);Stock=stock.Select(s=>s.Copy()).ToList();Staff=staff.ToList();
            if(Stock.Any(s=>s.Count<0)||Stock.Sum(s=>s.Count)>layout.FridgeCapacity)throw new ArgumentException("Tonight's stock must fit the fridges");
            if(Staff.Select(s=>s.Id).Distinct().Count()!=Staff.Count)throw new ArgumentException("Staff IDs must be unique");
            foreach(var s in Staff){if(!layout.Walkable(s.Tile))s.Tile=layout.Door;s.Position=s.PrevPosition=s.Tile;s.Metres=0;s.Task=null;}
            foreach(var g in forecast.Guests.GroupBy(g=>g.Group)){
                // Stratified slots avoid bursts; inverse CDF peaks in the early evening (19:00).
                float u=(Groups.Count+(float)random.NextDouble())/Math.Max(1,forecast.Guests.Select(x=>x.Group).Distinct().Count());
                float arrival=(u<.25f?Mathf.Sqrt(u*.25f):1-Mathf.Sqrt((1-u)*.75f))*RestaurantTuning.DoorCloseSeconds;
                Groups.Add(new ServiceGroup{Id=g.Key,Guests=g.ToList(),Arrival=arrival,Phase=GroupPhase.NotArrived});
            }
            Groups.Sort((a,b)=>a.Arrival!=b.Arrival?a.Arrival.CompareTo(b.Arrival):a.Id.CompareTo(b.Id));Result.Guests=Groups.Sum(g=>g.Count);
        }
        public void Tick(float elapsed)
        {
            if(float.IsNaN(elapsed)||float.IsInfinity(elapsed)||elapsed<0)throw new ArgumentOutOfRangeException(nameof(elapsed));
            accumulator+=elapsed;
            if(!eventsRolled)RollEvents();
            while(!Finished&&accumulator+1e-8>=RestaurantTuning.TickSeconds){accumulator-=RestaurantTuning.TickSeconds;Step();}
        }
        public bool SetJob(string staffId,Job job)
        {
            var s=Staff.FirstOrDefault(x=>x.Id==staffId);if(s==null||!Enum.IsDefined(typeof(Job),job)||Finished)return false;
            // Finish an already accepted delivery safely, then take the new role's next ticket.
            if(job!=s.NativeJob)return false;s.Job=job;return true;
        }
        public bool Pin(int tableUid){if(!Layout.Active.Any(i=>i.Uid==tableUid&&RestaurantData.Get(i.Id).Seats>0))return false;pin=pin==tableUid?0:tableUid;return true;}
        // The player taps a table, a station, the till or the drinks: the captain does that next. Three taps queue up;
        // a fourth replaces the last. False when the tap is not on something he can work.
        public bool Command(int uid)
        {
            if(Finished||!Layout.Active.Any(i=>i.Uid==uid))return false;
            if(captainOrders.Count>0&&captainOrders[captainOrders.Count-1]==uid)return true;
            if(captainOrders.Count>=3)captainOrders.RemoveAt(captainOrders.Count-1);
            captainOrders.Add(uid);return true;
        }
        // The player taps a table that is waving for another round: sold on the spot, one per guest. False when nothing is open there.
        public bool TakeUpsell(int tableUid)
        {
            var g=Groups.FirstOrDefault(x=>x.TableUid==tableUid&&x.Phase==GroupPhase.Eating&&Seconds<x.UpsellUntil);
            if(g==null||Finished)return false;
            g.UpsellCoins=RestaurantTuning.StaplePrice(g.Upsell)*g.Count;Result.DrinkCoins+=g.UpsellCoins;Result.Upsells++;
            g.UpsellUntil=-1;g.UpsellSoldAt=Seconds;return true;
        }
        // The player taps the table a gull stands on: it flies off empty-beaked.
        public bool ShooGull(int tableUid)
        {
            if(GullTable==0||GullTable!=tableUid||Finished)return false;
            Result.GullsShooed++;GullAway(false);return true;
        }
        void GullAway(bool fed)
        {
            GullLeftTable=GullTable;GullLeftAt=Seconds;GullLeftFed=fed;GullTable=0;
            nextGull=Seconds+RestaurantTuning.GullEvery/GullPace*(.6f+.8f*(float)gullRandom.NextDouble());
        }
        void Gulls()
        {
            if(GullPace<=0)return;
            if(nextGull<0)nextGull=Seconds+RestaurantTuning.GullEvery/GullPace*(.6f+.8f*(float)gullRandom.NextDouble());
            if(GullTable!=0){
                var at=Groups.FirstOrDefault(x=>x.TableUid==GullTable&&x.Phase==GroupPhase.Eating);
                if(at==null)GullAway(false); // the table finished first
                else if(Seconds-GullLandedAt>=RestaurantTuning.GullSeconds){at.GullStole=true;Result.GullSteals++;GullAway(true);}
                return;
            }
            if(Seconds<nextGull)return;
            var eating=Groups.Where(x=>x.Phase==GroupPhase.Eating&&x.TableUid!=0&&!x.GullStole&&x.EatUntil-Seconds>RestaurantTuning.GullSeconds).ToList();
            if(eating.Count==0){nextGull=Seconds+2;return;}
            GullTable=eating[gullRandom.Next(eating.Count)].TableUid;GullLandedAt=Seconds;
        }
        void OfferUpsell(ServiceGroup g)
        {
            g.UpsellOffered=true;
            if(upsellRandom.NextDouble()>=RestaurantTuning.UpsellChance)return;
            var menu=new List<Dish>();
            if(Layout.Active.Any(i=>i.Id==ItemId.DrinksFridge)){menu.Add(Dish.Beer);menu.Add(Dish.Lemonade);}
            if(Layout.Active.Any(i=>i.Id==ItemId.CoffeeMachine)){menu.Add(Dish.Coffee);menu.Add(Dish.Tea);}
            if(menu.Count==0)menu.Add(Dish.Bread);
            g.Upsell=menu[upsellRandom.Next(menu.Count)];g.UpsellUntil=Seconds+RestaurantTuning.UpsellSeconds;
        }
        public void CloseDoor(){DoorClosed=true;}
        public bool Seat(int groupId,int tableUid)
        {
            var g=Groups.FirstOrDefault(x=>x.Id==groupId&&x.Phase==GroupPhase.Queue&&!x.Reserved);
            var t=Layout.Active.FirstOrDefault(i=>i.Uid==tableUid);
            if(g==null||t==null||!TableFree(t,g.Count))return false;
            var mira=Staff.FirstOrDefault(s=>s.Job==Job.Reception&&!s.Busy);
            return mira!=null&&StartSeat(mira,g,t);
        }
        public bool ChooseSubstitute(int guestId,Dish? dish,Species species=Species.Herring)
        {
            var t=Groups.SelectMany(g=>g.Tickets).FirstOrDefault(t=>t.Order.Id==guestId&&t.Phase==TicketPhase.Choice);
            if(t==null)return false;
            if(dish==null){t.Substitute=true;t.Phase=TicketPhase.Delivered;t.Dish=Dish.Coffee;Result.Substitutions++;return true;}
            if(!Layout.CanCook(dish.Value)||RestaurantData.Get(dish.Value).Staple||!Available(species,dish.Value))return false;
            t.Dish=dish.Value;t.Species=species;t.Substitute=true;t.Phase=TicketPhase.Waiting;Result.Substitutions++;return true;
        }
        public bool Break(int uid)
        {
            if(!Layout.Active.Any(i=>i.Uid==uid)||Finished)return false;return Broken.Add(uid);
        }
        // The player taps a broken station: the captain walks there next and repairs it himself (no remote fixing).
        int captainRepair;
        public bool SendToFix(int uid){if(!Broken.Contains(uid)||Finished)return false;captainRepair=uid;return true;}
        public bool CaptainHoldFix(int uid,float heldSeconds)
        {
            if(!Broken.Contains(uid)||heldSeconds<=0||float.IsNaN(heldSeconds)||float.IsInfinity(heldSeconds))return false;
            captainRepairs.TryGetValue(uid,out float old);captainRepairs[uid]=old+heldSeconds;
            if(captainRepairs[uid]>=WorkSpeed.Duration(RestaurantTuning.RepairSeconds)){Broken.Remove(uid);captainRepairs.Remove(uid);}return true;
        }
        bool TableFree(RestaurantItem t,int count)=>RestaurantData.Get(t.Id).Seats>=count&&!Broken.Contains(t.Uid)&&
            !(t.Id==ItemId.TerraceTable&&weather==Weather.Rain)&&!Groups.Any(g=>g.TableUid==t.Uid&&g.Phase!=GroupPhase.Gone&&g.Phase!=GroupPhase.NotArrived&&g.Phase!=GroupPhase.Queue);
        // Layout is fixed for a service; edits belong between nights. Cache both successful and blocked searches.
        List<Vector2Int> Path(Vector2Int from,Vector2Int to){var key=(from,to);if(!routes.TryGetValue(key,out var path)){path=Layout.Path(from,to);routes[key]=path;}return path;}
        Vector2Int? At(RestaurantItem i,Vector2Int from){var key=(i.Uid,from);if(!access.TryGetValue(key,out var tile)){tile=Layout.Access(i,from);access[key]=tile;}return tile;}
        RestaurantItem Station(ItemId id)=>Layout.Active.FirstOrDefault(i=>i.Id==id&&!Broken.Contains(i.Uid)&&!stations.Contains(i.Uid));
        RestaurantItem Table(ServiceGroup g)=>Layout.Active.First(i=>i.Uid==g.TableUid);
        IEnumerable<ServiceGroup> Priority()=>Groups.OrderBy(g=>g.TableUid==pin?0:1).ThenBy(g=>g.Arrival).ThenBy(g=>g.Id);
        StaffLeg Leg(Vector2Int target,float seconds=0,int appliance=0,Action done=null)=>new StaffLeg{Target=target,Seconds=seconds,Appliance=appliance,Done=done};
        bool Start(RestaurantStaff s,string label,IEnumerable<StaffLeg> legs,Action complete)
        {
            var list=legs.ToList();Vector2Int p=s.Tile;float total=0;
            foreach(var leg in list){var path=Path(p,leg.Target);if(path==null)return false;total+=path.Count/s.WalkSpeed+leg.Seconds/s.Rate;p=leg.Target;}
            s.Task=new StaffTask{Label=label,Legs=new Queue<StaffLeg>(list),Complete=complete,
                Total=total};return true;
        }
        bool StartSeat(RestaurantStaff s,ServiceGroup g,RestaurantItem table)
        {
            var reception=Layout.Active.FirstOrDefault(i=>i.Id==ItemId.Reception&&!Broken.Contains(i.Uid));
            if(reception==null)return false;var a=At(reception,s.Tile);var b=At(table,Layout.Door);if(!a.HasValue||!b.HasValue)return false;
            if(!Start(s,"Seat group",new[]{Leg(a.Value),Leg(Layout.Door,RestaurantTuning.SeatSeconds),Leg(b.Value)},()=>{
                if(g.Phase==GroupPhase.Seating){g.Phase=GroupPhase.Order;g.SeatedAt=Seconds;g.Reserved=false;}}))return false;
            g.TableUid=table.Uid;g.Phase=GroupPhase.Seating;g.Reserved=true;return true;
        }
        void Advance(RestaurantStaff s)
        {
            var task=s.Task;float budget=RestaurantTuning.TickSeconds;
            int iterations=0;
            while(task!=null&&budget>.000001f){
                if(++iterations>100)throw new InvalidOperationException("Non-progressing restaurant task "+s.Id+" "+task.Label+" budget="+budget+" remaining="+task.Remaining);
                if(task.Current==null){if(task.Legs.Count==0){s.Task=null;task.Complete?.Invoke();return;}task.Current=task.Legs.Dequeue();
                    var path=Path(s.Tile,task.Current.Target);if(path==null)throw new InvalidOperationException("Layout changed during service");
                    task.Path=new Queue<Vector2Int>(path);task.Remaining=task.Current.Seconds;task.Segment=0;}
                if(task.Path.Count>0){float distance=Math.Min(1-task.Segment,budget*s.WalkSpeed);float used=distance/s.WalkSpeed;
                    task.Elapsed+=used;task.Segment+=distance;s.Metres+=distance;s.Position=Vector2.Lerp(s.Tile,task.Path.Peek(),task.Segment);budget-=used;
                    if(task.Segment>=.99999f){s.Tile=task.Path.Dequeue();s.Position=s.Tile;task.Segment=0;}continue;}
                if(task.Current.Appliance!=0&&Broken.Contains(task.Current.Appliance))return;
                float work=Math.Min(task.Remaining,budget*s.Rate);task.Remaining-=work;task.Elapsed+=work/s.Rate;budget-=work/s.Rate;
                if(task.Remaining<=.00001f){task.Current.Done?.Invoke();task.Current=null;}else return;
            }
        }
        // Staples (fries, bread, drinks) come from the pantry, never from tonight's fish.
        bool Available(Species species,Dish dish)
        {
            if(RestaurantData.Get(dish).Staple)return true;
            if(dish==Dish.Soup&&soupReady>0)return true;var form=RestaurantData.Get(dish).Form;
            return Stock.Any(s=>s.Count>0&&s.Form==form&&(dish==Dish.Soup||s.Species==species));
        }
        PortionStock Take(Species species,Dish dish,int count=1,bool preferSpecial=false)
        {
            var form=RestaurantData.Get(dish).Form;
            if(RestaurantData.Get(dish).Staple)return new PortionStock{Species=species,Form=form,Count=count};
            var stock=Stock.Where(s=>s.Count>0&&s.Form==form&&(dish==Dish.Soup||s.Species==species)).OrderByDescending(s=>preferSpecial&&s.Special).FirstOrDefault();
            if(stock==null)return null;int take=Math.Min(count,stock.Count);stock.Count-=take;PortionsTaken+=take;
            return new PortionStock{Species=stock.Species,Form=form,Count=take,CaptainCut=stock.CaptainCut,Special=stock.Special};
        }
        void MakeTickets(ServiceGroup g)
        {
            bool platter=false;
            foreach(var guest in g.Guests){if(guest.Dish==Dish.Platter&&platter)continue;if(guest.Dish==Dish.Platter)platter=true;
                var t=new ServiceTicket{Order=guest,Dish=guest.Dish,Species=guest.Species,Phase=TicketPhase.Waiting};
                if(!Available(t.Species,t.Dish)){t.Phase=TicketPhase.Choice;t.ChoiceAt=Seconds;}g.Tickets.Add(t);}
            g.Phase=GroupPhase.Kitchen;
        }
        // Service v2: the cook takes the fish from the fridge and loads the station, then is free; the station cooks by
        // itself (CookSeconds) and the plate lands on the pass (Step). `only` and `at` narrow it to the player's tap.
        bool Cook(RestaurantStaff s,ServiceGroup only=null,ItemId? at=null)
        {
            foreach(var g in Priority().Where(g=>g.Phase==GroupPhase.Kitchen&&(only==null||g==only)))foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Waiting)){
                if(t.Dish==Dish.Soup&&soupReady>0){soupReady--;SoupBowls++;t.Phase=TicketPhase.Ready;t.ReadyAt=Seconds;continue;}
                var kind=RestaurantData.Get(t.Dish).Appliance;
                if(at.HasValue&&at.Value!=kind&&at.Value!=ItemId.Fridge&&at.Value!=ItemId.PrepCounter)continue;
                var appliance=Station(kind);var fridge=Station(ItemId.Fridge);
                if(appliance==null||fridge==null)continue;
                if(!Available(t.Species,t.Dish)){t.Phase=TicketPhase.Choice;t.ChoiceAt=Seconds;continue;}
                bool staple=RestaurantData.Get(t.Dish).Staple;
                var f=staple?null:At(fridge,s.Tile);var a=At(appliance,staple?s.Tile:f.HasValue?f.Value:s.Tile);if(!staple&&!f.HasValue||!a.HasValue)continue;
                // Reserve one appliance and the ingredients atomically with the task.
                int count=t.Dish==Dish.Soup?RestaurantTuning.KettleBatch:1;
                var taken=Take(t.Species,t.Dish,count,t.Order.Accepted);if(taken==null)continue;
                var legs=new List<StaffLeg>();if(!staple)legs.Add(Leg(f.Value));
                legs.Add(Leg(a.Value,RestaurantTuning.LoadSeconds,appliance.Uid,()=>cooking.Add(new Cooking{Uid=appliance.Uid,Ticket=t,Group=g,Taken=taken,ReadyAt=Seconds+RestaurantTuning.CookSeconds(t.Dish)})));
                float quality=s.Mult;
                bool started=Start(s,"Cook "+t.Dish,legs,()=>t.CookQuality=quality);
                if(!started){if(!staple){RestaurantPortions.Add(Stock,taken.Species,taken.Form,taken.Count,taken.CaptainCut,taken.Special);PortionsTaken-=taken.Count;}continue;}
                s.Task.Cancel=()=>{if(cooking.Any(c=>c.Ticket==t))return;waste+=staple?0:taken.Count;stations.Remove(appliance.Uid);t.Phase=TicketPhase.Abandoned;};
                stations.Add(appliance.Uid);t.Phase=TicketPhase.Cooking;return true;
            }return false;
        }
        // Stations finish on their own; a broken one holds its dish until it is repaired.
        void TickCooking()
        {
            foreach(var c in cooking.ToArray()){
                if(Broken.Contains(c.Uid)){c.ReadyAt+=RestaurantTuning.TickSeconds;continue;}
                if(Seconds<c.ReadyAt)continue;
                cooking.Remove(c);stations.Remove(c.Uid);var t=c.Ticket;
                if(t.Dish==Dish.Soup)soupReady+=c.Taken.Count-1;
                if(c.Group.Phase==GroupPhase.Kitchen&&t.Phase==TicketPhase.Cooking){t.Phase=TicketPhase.Ready;t.ReadyAt=Seconds;t.CaptainCut=c.Taken.CaptainCut;t.SpecialServed=c.Taken.Special&&t.Order.Special&&t.Order.Accepted;if(t.CookQuality<=0)t.CookQuality=1;}
                else {if(!RestaurantData.Get(t.Dish).Staple)waste++;t.Phase=TicketPhase.Abandoned;}
            }
        }
        // Cooking dishes for the room to draw on their stations: (station uid, dish, 0..1 done).
        public IEnumerable<(int uid,Dish dish,float done)> OnStations=>cooking.Select(c=>(c.Uid,c.Ticket.Dish,Mathf.Clamp01(1-(c.ReadyAt-Seconds)/RestaurantTuning.CookSeconds(c.Ticket.Dish))));
        bool Wait(RestaurantStaff s,bool host=false,bool serve=true,bool clear=true,ServiceGroup only=null)
        {
            foreach(var g in Priority().Where(g=>only==null||g==only)){
                if(g.Reserved)continue;var table=g.TableUid==0?null:Table(g);if(table==null||Broken.Contains(table.Uid))continue;
                var a=At(table,s.Tile);if(!a.HasValue)continue;
                if(g.Phase==GroupPhase.Order){
                    if(!host)continue;
                    g.Reserved=Start(s,"Take order",new[]{Leg(a.Value,RestaurantTuning.OrderSeconds)},()=>{g.Reserved=false;if(g.Phase!=GroupPhase.Order)return;
                        if(!g.DrinksDelivered&&g.Guests.Any(x=>x.Drink))g.Phase=GroupPhase.Drinks;else MakeTickets(g);});if(g.Reserved)return true;
                }
                if(host)continue;
                if(g.Phase==GroupPhase.Kitchen&&serve){var ticket=g.Tickets.FirstOrDefault(t=>t.Phase==TicketPhase.Ready);if(ticket==null)continue;
                    if(Start(s,"Serve fish",new[]{Leg(Layout.PassGuests),Leg(a.Value,RestaurantTuning.ServeSeconds)},()=>{
                        if(g.Phase==GroupPhase.Kitchen){ticket.Phase=TicketPhase.Delivered;ticket.DeliveredAt=Seconds;ticket.Cold=Seconds-ticket.ReadyAt>RestaurantTuning.ColdSeconds;if(ticket.Cold)Result.ColdDishes++;}else {if(!RestaurantData.Get(ticket.Dish).Staple)waste++;ticket.Phase=TicketPhase.Abandoned;}
                    })){ticket.Phase=TicketPhase.Serving;return true;}
                }
                if(g.Phase==GroupPhase.Clearing&&clear){
                    g.Reserved=Start(s,"Clear table",new[]{Leg(a.Value,RestaurantTuning.ClearSeconds),Leg(Layout.PassGuests)},()=>{g.Reserved=false;g.Phase=GroupPhase.Gone;});if(g.Reserved)return true;
                }
            }return false;
        }
        bool Drinks(RestaurantStaff s,bool dedicated,ServiceGroup only=null)
        {
            foreach(var g in Priority().Where(g=>(only==null||g==only)&&!g.Reserved&&(g.Phase==GroupPhase.Drinks||g.Phase==GroupPhase.Coffee||(dedicated&&g.Phase==GroupPhase.Queue&&!g.DrinksDelivered&&g.Guests.Any(x=>x.Drink))))){
                bool coffee=g.Phase==GroupPhase.Coffee, queued=g.Phase==GroupPhase.Queue;
                var orders=g.Guests.Where(x=>coffee?x.Coffee:x.Drink).ToList();var legs=new List<StaffLeg>();var at=s.Tile;bool ready=true;
                foreach(var drink in orders){Dish d=coffee?Dish.Coffee:drink.DrinkDish;var machine=Station(RestaurantData.Get(d).Appliance);if(machine==null){ready=false;break;}
                    var m=At(machine,at);if(!m.HasValue){ready=false;break;}legs.Add(Leg(m.Value,coffee?RestaurantTuning.CoffeeSeconds:RestaurantTuning.DrinkSeconds,machine.Uid));at=m.Value;}
                if(!ready)continue;Vector2Int? table=queued?Layout.Door:At(Table(g),at);if(!table.HasValue)continue;legs.Add(Leg(table.Value,RestaurantTuning.ServeSeconds));
                g.Reserved=Start(s,coffee?"Serve coffee":"Serve drinks",legs,()=>{
                    g.Reserved=false;if(g.Phase!=(queued?GroupPhase.Queue:coffee?GroupPhase.Coffee:GroupPhase.Drinks))return;
                    foreach(var order in orders){Result.DrinkCoins+=RestaurantTuning.StaplePrice(coffee?Dish.Coffee:order.DrinkDish);Result.StapleCosts+=RestaurantTuning.StapleCost;}
                    if(coffee){g.CoffeeDelivered=true;g.Phase=GroupPhase.Payment;}
                    else {g.DrinksDelivered=true;g.LastPatienceBoost=RestaurantTuning.DrinkPatience;if(!queued)MakeTickets(g);}
                });if(g.Reserved)return true;
            }return false;
        }
        bool Repair(RestaurantStaff s)
        {
            foreach(int uid in Broken.OrderBy(x=>s.Job==Job.Helper&&x==captainRepair?0:1).ThenBy(x=>x)){
                if(stations.Contains(-uid))continue;var item=Layout.Active.First(i=>i.Uid==uid);var a=At(item,s.Tile);if(!a.HasValue)continue;
                if(Start(s,"Repair "+RestaurantData.Get(item.Id).Name,new[]{Leg(a.Value,RestaurantTuning.RepairSeconds)},()=>{Broken.Remove(uid);stations.Remove(-uid);captainRepairs.Remove(uid);})){
                    stations.Add(-uid);return true;}
            }return false;
        }
        bool Host(RestaurantStaff s)=>Till(s)||Wait(s,true)||Seat(s);
        bool Till(RestaurantStaff s,ServiceGroup only=null)
        {
            foreach(var g in Priority().Where(x=>x.Phase==GroupPhase.Payment&&!x.Reserved&&(only==null||x==only))){
                var till=Station(ItemId.Reception);if(till==null)break;var a=At(till,s.Tile);if(!a.HasValue)continue;
                g.Reserved=Start(s,"Take payment",new[]{Leg(a.Value,RestaurantTuning.PaymentSeconds,till.Uid)},()=>{g.Reserved=false;if(g.Phase!=GroupPhase.Payment)return;Pay(g,false);g.Phase=GroupPhase.Clearing;});
                if(g.Reserved)return true;
            }
            return false;
        }
        bool Seat(RestaurantStaff s)
        {
            foreach(var g in Priority().Where(x=>x.Phase==GroupPhase.Queue&&!x.Reserved)){
                var table=Layout.Active.Where(i=>RestaurantData.Get(i.Id).Seats>0&&TableFree(i,g.Count)).OrderBy(i=>RestaurantData.Get(i.Id).Seats).ThenBy(i=>i.Uid).FirstOrDefault();
                if(table!=null&&StartSeat(s,g,table))return true;
            }
            return false;
        }
        bool Do(RestaurantStaff s,Work w)=>w switch{
            Work.Seat=>Seat(s),Work.Till=>Till(s),Work.TakeOrder=>Wait(s,true),Work.Cook=>Cook(s),
            Work.Serve=>Wait(s,false,true,false),Work.Clear=>Wait(s,false,false,true),Work.Drinks=>Drinks(s,s.Job==Job.Barista),_=>Repair(s)};
        bool Help(RestaurantStaff s)
        {
            // Count actionable queues, breaking ties in favour of hot plates. Fall through when a station is busy.
            var queues=new[]{
                (count:Groups.Sum(g=>g.Tickets.Count(t=>t.Phase==TicketPhase.Ready))*2+Groups.Count(g=>g.Phase==GroupPhase.Clearing&&!g.Reserved),task:(Func<bool>)(()=>Wait(s))),
                (count:Broken.Count*3,task:(Func<bool>)(()=>Repair(s))),
                (count:Groups.Sum(g=>g.Tickets.Count(t=>t.Phase==TicketPhase.Waiting)),task:(Func<bool>)(()=>Cook(s))),
                (count:Groups.Count(g=>(g.Phase==GroupPhase.Drinks||g.Phase==GroupPhase.Coffee)&&!g.Reserved),task:(Func<bool>)(()=>Drinks(s,false))),
                (count:Groups.Count(g=>(g.Phase==GroupPhase.Queue||g.Phase==GroupPhase.Order||g.Phase==GroupPhase.Payment)&&!g.Reserved),task:(Func<bool>)(()=>Host(s)))
            };
            foreach(var q in queues.OrderByDescending(q=>q.count))if(q.count>0&&q.task())return true;
            return false;
        }
        // ---- service v2: the player's taps -------------------------------------------------------------------------
        // What the captain does for a tapped piece: a table gets whatever it needs next (seat the first group that fits,
        // take the order, cook it, serve its plates, drinks, the bill, clearing); a kitchen station cooks the oldest
        // ticket it can make; the till takes payment or seats; the bar makes drinks; a broken piece gets repaired.
        bool CaptainDo(RestaurantStaff s,int uid)
        {
            var item=Layout.Active.FirstOrDefault(i=>i.Uid==uid);if(item==null)return false;
            if(Broken.Contains(uid)){captainRepair=uid;return Repair(s);}
            var def=RestaurantData.Get(item.Id);
            if(def.Seats>0&&item.Id!=ItemId.BarCounter)return CaptainTable(s,item);
            if(item.Id==ItemId.Reception)return Till(s)||Seat(s);
            if(def.Area==Area.Bar)return Drinks(s,false);
            if(def.Area==Area.Kitchen)return Cook(s,null,item.Id);
            return false;
        }
        bool CaptainTable(RestaurantStaff s,RestaurantItem table)
        {
            var g=Groups.FirstOrDefault(x=>x.TableUid==table.Uid&&x.Phase!=GroupPhase.Gone&&x.Phase!=GroupPhase.NotArrived&&x.Phase!=GroupPhase.Queue);
            if(g==null){var q=Priority().FirstOrDefault(x=>x.Phase==GroupPhase.Queue&&!x.Reserved&&TableFree(table,x.Count));return q!=null&&StartSeat(s,q,table);}
            if(g.Reserved)return false;
            switch(g.Phase){
                case GroupPhase.Order:return Wait(s,true,false,false,g);
                case GroupPhase.Kitchen:return g.Tickets.Any(t=>t.Phase==TicketPhase.Ready)?CaptainServe(s,g):Cook(s,g);
                case GroupPhase.Drinks:case GroupPhase.Coffee:return Drinks(s,false,g);
                case GroupPhase.Payment:return Till(s,g);
                case GroupPhase.Clearing:return Wait(s,false,false,true,g);
            }
            return false;
        }
        // One trip from the pass: up to CarryPlates plates, this table's first, then the next queued taps' tables that
        // have plates waiting (those taps are used up). Two or more tables in one trip is a combo and tips per plate.
        bool CaptainServe(RestaurantStaff s,ServiceGroup first)
        {
            var load=new List<(ServiceGroup g,List<ServiceTicket> plates)>();int room=RestaurantTuning.CarryPlates;
            void Add(ServiceGroup g){if(room<=0||g.Reserved||g.Phase!=GroupPhase.Kitchen)return;var p=g.Tickets.Where(t=>t.Phase==TicketPhase.Ready).Take(room).ToList();if(p.Count==0)return;load.Add((g,p));room-=p.Count;}
            Add(first);
            foreach(int uid in captainOrders.ToArray()){
                if(room<=0)break;var other=Groups.FirstOrDefault(x=>x.TableUid==uid&&x.Phase==GroupPhase.Kitchen&&x!=first);
                if(other==null||load.Any(l=>l.g==other))continue;int before=load.Count;Add(other);if(load.Count>before)captainOrders.Remove(uid);
            }
            if(load.Count==0)return false;
            var legs=new List<StaffLeg>{Leg(Layout.PassGuests)};var at=Layout.PassGuests;
            foreach(var (g,plates) in load){
                var a=At(Table(g),at);if(!a.HasValue)return false;at=a.Value;
                legs.Add(Leg(a.Value,RestaurantTuning.ServeSeconds*plates.Count,0,()=>{
                    foreach(var ticket in plates){
                        if(g.Phase==GroupPhase.Kitchen&&ticket.Phase==TicketPhase.Serving){ticket.Phase=TicketPhase.Delivered;ticket.DeliveredAt=Seconds;ticket.Cold=Seconds-ticket.ReadyAt>RestaurantTuning.ColdSeconds;if(ticket.Cold)Result.ColdDishes++;}
                        else if(ticket.Phase==TicketPhase.Serving){if(!RestaurantData.Get(ticket.Dish).Staple)waste++;ticket.Phase=TicketPhase.Abandoned;}
                    }}));
            }
            int count=load.Sum(l=>l.plates.Count);bool combo=load.Count>=2;
            if(!Start(s,"Serve fish",legs,()=>{if(!combo)return;int tip=RestaurantTuning.ComboTip*count;Result.Tips+=tip;Result.Combos++;LastCombo=count;LastComboTip=tip;LastComboAt=Seconds;}))return false;
            foreach(var (_,plates) in load)foreach(var t in plates)t.Phase=TicketPhase.Serving;
            return true;
        }
        // Walk-ins: groups of one to three off the pier, all night, faster as the night's stars climb. They eat
        // tonight's fish while there is plenty left over for the bookings, otherwise the quick menu (fries, bread,
        // soup, drinks), so the kitchen always has something to cook.
        void WalkIns()
        {
            if(WalkInPace<=0||DoorClosed)return;
            float momentum=Groups.Count(g=>g.Paid)==0?.5f:(Groups.Where(g=>g.Paid).Average(g=>(float)g.Stars)-1)/4;
            float Next()=>Seconds+RestaurantTuning.WalkInEvery/WalkInPace/(.75f+.5f*momentum)*(.6f+(float)walkRandom.NextDouble()*.8f);
            if(nextWalkIn<0){nextWalkIn=Next();return;}
            if(Seconds<nextWalkIn)return;nextWalkIn=Next();
            if(Groups.Count(g=>g.Phase==GroupPhase.Queue)>=RestaurantTuning.WalkInQueue)return; // a full doorway: they stroll on
            int seats=Layout.Active.Where(i=>i.Id!=ItemId.BarCounter).Select(i=>RestaurantData.Get(i.Id).Seats).DefaultIfEmpty(0).Max();if(seats<=0)return;
            int n=Math.Min(seats,walkRandom.NextDouble()<.5?2:walkRandom.Next(1,4));
            var menu=new List<Dish>{Dish.Bread};if(Layout.CanCook(Dish.Fries))menu.Add(Dish.Fries);if(Layout.CanCook(Dish.Soup)&&(soupReady>0||Stock.Any(x=>x.Form==PreparedForm.Stock&&x.Count>0)))menu.Add(Dish.Soup);
            // Fish to spare: more portions on hand than the booked guests still to come could eat.
            int booked=Groups.Where(g=>g.Id<1000000&&(g.Phase==GroupPhase.NotArrived||g.Phase==GroupPhase.Queue||g.Phase==GroupPhase.Seating||g.Phase==GroupPhase.Order)).Sum(g=>g.Count);
            var spare=Stock.Where(x=>x.Count>0&&x.Form!=PreparedForm.Stock&&x.Form!=PreparedForm.Platter).ToList();
            var drinks=new List<Dish>();if(Layout.Has(ItemId.CoffeeMachine)){drinks.Add(Dish.Coffee);drinks.Add(Dish.Tea);}if(Layout.Has(ItemId.DrinksFridge)){drinks.Add(Dish.Lemonade);drinks.Add(Dish.Beer);}
            var g=new ServiceGroup{Id=walkInIds++,Arrival=Seconds,Phase=GroupPhase.Queue};
            for(int i=0;i<n;i++){
                Dish dish=menu[walkRandom.Next(menu.Count)];Species species=Species.Herring;
                if(spare.Sum(x=>x.Count)>booked+2&&walkRandom.NextDouble()<RestaurantTuning.WalkInFishChance){
                    var p=spare[walkRandom.Next(spare.Count)];species=p.Species;
                    var d=p.Form==PreparedForm.Whole?Dish.GrilledFish:p.Form==PreparedForm.Crab?Dish.Crab:p.Form==PreparedForm.Squid?Dish.Calamari:Layout.CanCook(Dish.PanFish)?Dish.PanFish:Dish.FishAndChips;
                    if(Layout.CanCook(d))dish=d;
                }
                g.Guests.Add(new GuestOrder{Id=walkInIds++,Group=g.Id,Species=species,Dish=dish,
                    Drink=drinks.Count>0&&walkRandom.NextDouble()<RestaurantTuning.DrinkChance,DrinkDish=drinks.Count==0?Dish.Coffee:drinks[walkRandom.Next(drinks.Count)]});
            }
            Groups.Add(g);Result.Guests+=n;Result.WalkIns+=n;
        }
        void Pay(ServiceGroup g,bool impatient)
        {
            if(g.Paid)return;g.Paid=true;
            int delivered=g.Tickets.Count(t=>t.Phase==TicketPhase.Delivered&&t.Dish!=Dish.Coffee);
            bool full=delivered==g.Tickets.Count && g.Tickets.Count>0;
            float waited=(g.ServedAt>0?g.ServedAt:Seconds)-g.SeatedAt;bool substituted=g.Tickets.Any(t=>t.Substitute);
            float quality=g.Tickets.Count==0?0:g.Tickets.Average(t=>t.CookQuality);
            g.Stars=impatient||!full?1:substituted||waited>RestaurantTuning.TablePatience*.85f?3:5;
            if(g.Tickets.Any(t=>t.Cold))g.Stars=Math.Max(1,g.Stars-1);
            if(g.GullStole)g.Stars=Math.Max(1,g.Stars-1);
            g.Why=impatient?"gave-up":!full?"missing":g.Tickets.Any(t=>t.Cold)?"cold":g.GullStole?"gull":substituted?"swap":waited>RestaurantTuning.TablePatience*.85f?"slow"
                :g.Tickets.Any(t=>t.SpecialServed)?"special":g.Tickets.Any(t=>t.CaptainCut)?"captain":"great";
            int dishCoins=0;
            foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Delivered)){
                if(t.Dish==Dish.Coffee){Result.StapleCosts+=RestaurantTuning.StapleCost;continue;}
                if(RestaurantData.Get(t.Dish).Staple){Result.Staples++;Result.StapleCosts+=RestaurantTuning.StapleCost;}
                float price=RestaurantData.PortionPrice(t.Species,t.Dish)+PriceBonus;
                if(t.Cold)price*=RestaurantTuning.ColdPrice;
                if(t.SpecialServed&&!t.Substitute){price*=RestaurantTuning.SpecialMultiplier;Result.SpecialServed++;}
                dishCoins+=(int)Math.Round(price);
            }
            Result.DishCoins+=dishCoins;
            if(!impatient)Result.Tips+=(int)Math.Round(dishCoins*RestaurantTuning.TipRate*((g.Stars-1)*.25f+Layout.Ambience*.02f+g.Tickets.Count(t=>t.CaptainCut)*.02f)*(g.Birthday&&g.Stars>=4?2:1));
            if(g.Regular&&g.Stars>=4)Result.HappyRegulars++;
            if(g.Stars>=4&&g.Birthday)g.Why="birthday";else if(g.Stars>=4&&g.Regular)g.Why="regular";
            int served=full?g.Count:Math.Min(g.Count,delivered);Result.Served+=served;Result.Left+=g.Count-served;
            Result.Stars+=g.Stars*g.Count;
            foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Ready)){if(!RestaurantData.Get(t.Dish).Staple)waste++;t.Phase=TicketPhase.Abandoned;}
            foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Waiting||t.Phase==TicketPhase.Choice))t.Phase=TicketPhase.Abandoned;
        }
        void Step()
        {
            ticks++;if(Seconds>=RestaurantTuning.DoorCloseSeconds)DoorClosed=true;
            foreach(var s in Staff)s.PrevPosition=s.Position;
            WalkIns();TickCooking();Gulls();
            foreach(var g in Groups){
                if(g.Phase==GroupPhase.NotArrived&&Seconds>=g.Arrival){if(DoorClosed){Result.Left+=g.Count;Result.Stars+=g.Count;g.Phase=GroupPhase.Gone;}else g.Phase=GroupPhase.Queue;}
                if(g.Phase==GroupPhase.Queue&&Seconds-g.Arrival>RestaurantTuning.DoorPatience+g.LastPatienceBoost+Layout.Ambience*RestaurantTuning.AmbiencePatience){
                    // A walk-in tired of the doorway strolls on and never counted as tonight's guest; a booking that leaves does.
                    if(g.Id>=1000000){Result.Guests-=g.Count;Result.WalkIns-=g.Count;}else {Result.Left+=g.Count;Result.Stars+=g.Count;}
                    g.Phase=GroupPhase.Gone;g.Reserved=false;}
                if(g.Phase>=GroupPhase.Order&&g.Phase<=GroupPhase.Kitchen&&Patience(g)<=0){Pay(g,true);g.Phase=GroupPhase.Clearing;g.Reserved=false;}
                // Nobody free to make coffee: they skip it and pay rather than sit on forever.
                if(g.Phase==GroupPhase.Coffee&&!g.Reserved&&Seconds-g.EatUntil>RestaurantTuning.CoffeeWait)g.Phase=GroupPhase.Payment;
                foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Choice&&Seconds-t.ChoiceAt>=RestaurantTuning.SubstituteDelay).ToArray()){
                    if(!ChooseSubstitute(t.Order.Id,Dish.Soup)){ChooseSubstitute(t.Order.Id,null);}
                }
                if(g.Phase==GroupPhase.Kitchen&&g.Tickets.All(t=>t.Phase==TicketPhase.Delivered)){g.Phase=GroupPhase.Eating;g.ServedAt=Seconds;g.EatUntil=Seconds+RestaurantTuning.EatSeconds;}
                if(g.Phase==GroupPhase.Eating&&!g.UpsellOffered&&Seconds>=g.ServedAt+RestaurantTuning.UpsellAfter)OfferUpsell(g);
                if(g.Phase==GroupPhase.Eating&&Seconds>=g.EatUntil){if(g.Guests.Any(x=>x.Coffee))g.Phase=GroupPhase.Coffee;else g.Phase=GroupPhase.Payment;}
            }
            if(Breakdowns&&Seconds<RestaurantTuning.NightSeconds){
                foreach(var item in Layout.Active.Where(i=>i.Id==ItemId.Stove||i.Id==ItemId.Oven||i.Id==ItemId.Fryer||i.Id==ItemId.Reception||i.Id==ItemId.CoffeeMachine))
                    if(!Broken.Contains(item.Uid)&&random.NextDouble()<RestaurantTuning.BreakdownPerSecond*RestaurantTuning.TickSeconds/(1+Staff.Count(s=>s.NativeJob==Job.Handyman))*(item.Id==ItemId.Stove&&Layout.HasUpgrade("ReliableStove")?.3f:1))Broken.Add(item.Uid);
            }
            foreach(var s in Staff){
                if(s.Job==Job.Helper&&s.Task?.Current!=null&&s.Task.Current.Appliance!=0&&Broken.Contains(s.Task.Current.Appliance)&&!suspended.ContainsKey(s.Id)){
                    suspended[s.Id]=s.Task;s.Task=null;
                }
                if(s.Job==Job.Helper&&suspended.ContainsKey(s.Id)&&!s.Busy){
                    if(Repair(s))continue;s.Task=suspended[s.Id];suspended.Remove(s.Id);
                    if(s.Task.Current!=null){s.Task.Path=new Queue<Vector2Int>(Path(s.Tile,s.Task.Current.Target));s.Task.Segment=0;}
                }
                if(s.Busy)Advance(s);if(s.Busy)continue;
                if(s.Job==Job.Helper&&captainRepair!=0){if(!Broken.Contains(captainRepair))captainRepair=0;else if(Repair(s))continue;}
                if(s.Job==Job.Helper&&CaptainHandsOn){bool did=false;while(captainOrders.Count>0&&!did){int uid=captainOrders[0];captainOrders.RemoveAt(0);did=CaptainDo(s,uid);}if(!did&&CaptainAuto)Help(s);continue;}
                if(s.Order!=null){foreach(var w in s.Order)if(Do(s,w))break;continue;}
                switch(s.Job){
                    case Job.Reception:
                        Host(s);break;
                    case Job.Cook:Cook(s);break;
                    case Job.Waiter:if(!Wait(s)&&!Staff.Any(x=>x.Job==Job.Barista))Drinks(s,false);break;
                    case Job.Barista:Drinks(s,true);break;
                    case Job.Handyman:Repair(s);break;
                    case Job.Helper:Help(s);break;
                }
            }
            // No waiter must not leave an empty, dirty room running forever. Guests have already paid/left.
            if(Seconds>=RestaurantTuning.NightSeconds){
                foreach(var g in Groups.Where(g=>g.Phase!=GroupPhase.Gone&&g.Phase!=GroupPhase.Clearing)){
                    if(g.Phase==GroupPhase.NotArrived||g.Phase==GroupPhase.Queue||g.Phase==GroupPhase.Seating){Result.Left+=g.Count;Result.Stars+=g.Count;}
                    else Pay(g,true);
                    g.Reserved=false;g.Phase=GroupPhase.Gone;
                }
                foreach(var g in Groups.Where(g=>g.Phase==GroupPhase.Clearing)){g.Phase=GroupPhase.Gone;g.Reserved=false;}
                if(Groups.All(g=>g.Phase==GroupPhase.Gone)){foreach(var s in Staff){s.Task?.Cancel?.Invoke();s.Task=null;}foreach(var task in suspended.Values)task.Cancel?.Invoke();suspended.Clear();Finish();}
            }
        }
        void Finish()
        {
            // Whatever was still on a station at closing goes to the cats with the rest.
            foreach(var c in cooking)if(!RestaurantData.Get(c.Ticket.Dish).Staple)waste+=c.Taken.Count;cooking.Clear();
            foreach(var t in Groups.SelectMany(g=>g.Tickets).Where(t=>t.Phase==TicketPhase.Serving||t.Phase==TicketPhase.Ready)){if(!RestaurantData.Get(t.Dish).Staple)waste++;t.Phase=TicketPhase.Abandoned;} // plates still in hand
            Finished=true;Result.Cats=RestaurantPortions.FeedCats(Stock)+soupReady+waste;soupReady=0;waste=0;
            Result.Seconds=Seconds;Result.Stars=Result.Guests==0?0:Result.Stars/Result.Guests;
            Result.PopularityGain=Result.Guests==0?0:(Result.Stars-3)*.5f+Result.SpecialServed*RestaurantTuning.PopularityPerSpecial+Result.HappyRegulars*RestaurantTuning.PopularityPerRegular;
            Result.Walking=Staff.Select(s=>new StaffDistance{Id=s.Id,Metres=s.Metres}).ToList();
            float waiters=Staff.Where(s=>s.Job==Job.Waiter).Sum(s=>s.Metres);
            Result.LayoutTip=waiters>0?"Our waiters walked "+Math.Round(waiters)+" m tonight. Tables nearer the pass would help.":"Try assigning a waiter tomorrow.";
        }
        public NightResult RunToClose(float limit=900)
        {
            while(!Finished&&Seconds<limit)Tick(1);
            if(!Finished)throw new InvalidOperationException("Service has not finished; repair blocked stations or reassign staff");return Result;
        }
    }
}

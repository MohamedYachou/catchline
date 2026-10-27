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
        public GroupPhase Phase; public float Arrival, SeatedAt, LastPatienceBoost, EatUntil;
        public bool Reserved, DrinksDelivered, CoffeeDelivered, Paid; public int Stars;
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
        public Vector2Int Tile; public Vector2 Position; public float Metres;
        internal StaffTask Task;
        public bool Busy=>Task!=null;
        public float BusyProgress=>Task==null?0:Task.Progress;
        public Vector2Int Target=>Task?.Current?.Target ?? Tile;
        public bool Walking=>Task?.Path!=null&&Task.Path.Count>0;
        public string Action=>Task?.Label ?? "Idle";
        public float Mult=>CardProgression.WorkMult(Rarity,Level,Stars);
        public float Rate=>WorkSpeed.Rate(Job==NativeJob?100:RestaurantTuning.OffRole*100,Mult);
        public float WalkSpeed=>WorkSpeed.Walk(Job==NativeJob?100:RestaurantTuning.OffRole*100,Mult);
        public static RestaurantStaff Captain(Vector2Int start)=>new RestaurantStaff{Id="captain",Job=Job.Helper,NativeJob=Job.Helper,Tile=start,Position=start};
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
        public int Guests, Served, Left, DishCoins, DrinkCoins, Tips, StapleCosts, Cats, Substitutions, SpecialServed, ColdDishes;
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
        public float Hour=>18+Math.Min(1,Seconds/RestaurantTuning.NightSeconds)*5;
        public bool DoorClosed {get;private set;}
        public bool Finished {get;private set;}
        public bool Breakdowns=true;
        public RestaurantSim(int seed,RestaurantLayout layout,RestaurantForecast forecast,IEnumerable<PortionStock> stock,IEnumerable<RestaurantStaff> staff)
        {
            if(!forecast.Locked)throw new ArgumentException("Lock Mira's plan before service");
            if(!layout.Validate().Ok)throw new ArgumentException(layout.Validate().Message);
            Layout=layout;weather=forecast.Weather;random=new System.Random(seed);Stock=stock.Select(s=>s.Copy()).ToList();Staff=staff.ToList();
            if(Stock.Any(s=>s.Count<0)||Stock.Sum(s=>s.Count)>layout.FridgeCapacity)throw new ArgumentException("Tonight's stock must fit the fridges");
            if(Staff.Select(s=>s.Id).Distinct().Count()!=Staff.Count)throw new ArgumentException("Staff IDs must be unique");
            foreach(var s in Staff){if(!layout.Walkable(s.Tile))s.Tile=layout.Door;s.Position=s.Tile;s.Metres=0;s.Task=null;}
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
            while(!Finished&&accumulator+1e-8>=RestaurantTuning.TickSeconds){accumulator-=RestaurantTuning.TickSeconds;Step();}
        }
        public bool SetJob(string staffId,Job job)
        {
            var s=Staff.FirstOrDefault(x=>x.Id==staffId);if(s==null||!Enum.IsDefined(typeof(Job),job)||Finished)return false;
            // Finish an already accepted delivery safely, then take the new role's next ticket.
            if(job!=s.NativeJob)return false;s.Job=job;return true;
        }
        public bool Pin(int tableUid){if(!Layout.Active.Any(i=>i.Uid==tableUid&&RestaurantData.Get(i.Id).Seats>0))return false;pin=pin==tableUid?0:tableUid;return true;}
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
        bool Available(Species species,Dish dish)
        {
            if(dish==Dish.Soup&&soupReady>0)return true;var form=RestaurantData.Get(dish).Form;
            return Stock.Any(s=>s.Count>0&&s.Form==form&&(dish==Dish.Soup||s.Species==species));
        }
        PortionStock Take(Species species,Dish dish,int count=1,bool preferSpecial=false)
        {
            var form=RestaurantData.Get(dish).Form;var stock=Stock.Where(s=>s.Count>0&&s.Form==form&&(dish==Dish.Soup||s.Species==species)).OrderByDescending(s=>preferSpecial&&s.Special).FirstOrDefault();
            if(stock==null)return null;int take=Math.Min(count,stock.Count);stock.Count-=take;
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
        bool Cook(RestaurantStaff s)
        {
            foreach(var g in Priority().Where(g=>g.Phase==GroupPhase.Kitchen))foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Waiting)){
                if(t.Dish==Dish.Soup&&soupReady>0){soupReady--;t.Phase=TicketPhase.Ready;t.ReadyAt=Seconds;continue;}
                var appliance=Station(RestaurantData.Get(t.Dish).Appliance);var fridge=Station(ItemId.Fridge);var prep=Station(ItemId.PrepCounter);
                if(appliance==null||fridge==null||prep==null)continue;
                if(!Available(t.Species,t.Dish)){t.Phase=TicketPhase.Choice;t.ChoiceAt=Seconds;continue;}
                var f=At(fridge,s.Tile);var a=At(appliance,Layout.PassKitchen);var p=At(prep,Layout.PassKitchen);if(!f.HasValue||!a.HasValue||!p.HasValue)continue;
                // Reserve one appliance and the ingredients atomically with the task.
                int count=t.Dish==Dish.Soup?RestaurantTuning.KettleBatch:1;
                var taken=Take(t.Species,t.Dish,count,t.Order.Accepted);if(taken==null)continue;
                bool started=Start(s,"Cook "+t.Dish,new[]{Leg(f.Value),Leg(a.Value,RestaurantTuning.CookSeconds(t.Dish),appliance.Uid),Leg(p.Value,RestaurantTuning.PlateSeconds,prep.Uid),Leg(Layout.PassKitchen)},()=>{
                    stations.Remove(appliance.Uid);if(t.Dish==Dish.Soup)soupReady+=taken.Count-1;
                    if(g.Phase==GroupPhase.Kitchen){t.Phase=TicketPhase.Ready;t.ReadyAt=Seconds;t.CaptainCut=taken.CaptainCut;t.SpecialServed=taken.Special&&t.Order.Special&&t.Order.Accepted;t.CookQuality=s.Mult;}
                    else {waste+=taken.Count==0?0:1;t.Phase=TicketPhase.Abandoned;}
                });
                if(!started){RestaurantPortions.Add(Stock,taken.Species,taken.Form,taken.Count,taken.CaptainCut,taken.Special);continue;}
                s.Task.Cancel=()=>{waste+=taken.Count;stations.Remove(appliance.Uid);t.Phase=TicketPhase.Abandoned;};
                stations.Add(appliance.Uid);t.Phase=TicketPhase.Cooking;return true;
            }return false;
        }
        bool Wait(RestaurantStaff s,bool host=false,bool serve=true,bool clear=true)
        {
            foreach(var g in Priority()){
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
                        if(g.Phase==GroupPhase.Kitchen){ticket.Phase=TicketPhase.Delivered;ticket.DeliveredAt=Seconds;ticket.Cold=Seconds-ticket.ReadyAt>RestaurantTuning.ColdSeconds;if(ticket.Cold)Result.ColdDishes++;}else {waste++;ticket.Phase=TicketPhase.Abandoned;}
                    })){ticket.Phase=TicketPhase.Serving;return true;}
                }
                if(g.Phase==GroupPhase.Clearing&&clear){
                    g.Reserved=Start(s,"Clear table",new[]{Leg(a.Value,RestaurantTuning.ClearSeconds),Leg(Layout.PassGuests)},()=>{g.Reserved=false;g.Phase=GroupPhase.Gone;});if(g.Reserved)return true;
                }
            }return false;
        }
        bool Drinks(RestaurantStaff s,bool dedicated)
        {
            foreach(var g in Priority().Where(g=>!g.Reserved&&(g.Phase==GroupPhase.Drinks||g.Phase==GroupPhase.Coffee||(dedicated&&g.Phase==GroupPhase.Queue&&!g.DrinksDelivered&&g.Guests.Any(x=>x.Drink))))){
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
            foreach(int uid in Broken.OrderBy(x=>x)){
                if(stations.Contains(-uid))continue;var item=Layout.Active.First(i=>i.Uid==uid);var a=At(item,s.Tile);if(!a.HasValue)continue;
                if(Start(s,"Repair "+RestaurantData.Get(item.Id).Name,new[]{Leg(a.Value,RestaurantTuning.RepairSeconds)},()=>{Broken.Remove(uid);stations.Remove(-uid);captainRepairs.Remove(uid);})){
                    stations.Add(-uid);return true;}
            }return false;
        }
        bool Host(RestaurantStaff s)=>Till(s)||Wait(s,true)||Seat(s);
        bool Till(RestaurantStaff s)
        {
            foreach(var g in Priority().Where(x=>x.Phase==GroupPhase.Payment&&!x.Reserved)){
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
        void Pay(ServiceGroup g,bool impatient)
        {
            if(g.Paid)return;g.Paid=true;
            int delivered=g.Tickets.Count(t=>t.Phase==TicketPhase.Delivered&&t.Dish!=Dish.Coffee);
            bool full=delivered==g.Tickets.Count && g.Tickets.Count>0;
            float waited=Seconds-g.SeatedAt;bool substituted=g.Tickets.Any(t=>t.Substitute);
            float quality=g.Tickets.Count==0?0:g.Tickets.Average(t=>t.CookQuality);
            g.Stars=impatient||!full?1:substituted||waited>RestaurantTuning.TablePatience*.85f?3:5;
            if(g.Tickets.Any(t=>t.Cold))g.Stars=Math.Max(1,g.Stars-1);
            int dishCoins=0;
            foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Delivered)){
                if(t.Dish==Dish.Coffee){Result.StapleCosts+=RestaurantTuning.StapleCost;continue;}
                float price=RestaurantData.PortionPrice(t.Species,t.Dish);
                if(t.Cold)price*=RestaurantTuning.ColdPrice;
                if(t.SpecialServed&&!t.Substitute){price*=RestaurantTuning.SpecialMultiplier;Result.SpecialServed++;}
                dishCoins+=(int)Math.Round(price);
            }
            Result.DishCoins+=dishCoins;
            if(!impatient)Result.Tips+=(int)Math.Round(dishCoins*RestaurantTuning.TipRate*((g.Stars-1)*.25f+Layout.Ambience*.02f+g.Tickets.Count(t=>t.CaptainCut)*.02f));
            int served=full?g.Count:Math.Min(g.Count,delivered);Result.Served+=served;Result.Left+=g.Count-served;
            Result.Stars+=g.Stars*g.Count;
            foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Ready)){waste++;t.Phase=TicketPhase.Abandoned;}
            foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Waiting||t.Phase==TicketPhase.Choice))t.Phase=TicketPhase.Abandoned;
        }
        void Step()
        {
            ticks++;if(Seconds>=RestaurantTuning.DoorCloseSeconds)DoorClosed=true;
            foreach(var g in Groups){
                if(g.Phase==GroupPhase.NotArrived&&Seconds>=g.Arrival){if(DoorClosed){Result.Left+=g.Count;Result.Stars+=g.Count;g.Phase=GroupPhase.Gone;}else g.Phase=GroupPhase.Queue;}
                if((g.Phase==GroupPhase.Queue||g.Phase==GroupPhase.Seating)&&Seconds-g.Arrival>RestaurantTuning.DoorPatience+g.LastPatienceBoost+Layout.Ambience*RestaurantTuning.AmbiencePatience){Result.Left+=g.Count;Result.Stars+=g.Count;g.Phase=GroupPhase.Gone;g.Reserved=false;}
                if(g.Phase>=GroupPhase.Order&&g.Phase<=GroupPhase.Coffee&&Seconds-g.SeatedAt>RestaurantTuning.TablePatience+g.LastPatienceBoost+Layout.Ambience*RestaurantTuning.AmbiencePatience){Pay(g,true);g.Phase=GroupPhase.Clearing;g.Reserved=false;}
                foreach(var t in g.Tickets.Where(t=>t.Phase==TicketPhase.Choice&&Seconds-t.ChoiceAt>=RestaurantTuning.SubstituteDelay).ToArray()){
                    if(!ChooseSubstitute(t.Order.Id,Dish.Soup)){ChooseSubstitute(t.Order.Id,null);}
                }
                if(g.Phase==GroupPhase.Kitchen&&g.Tickets.All(t=>t.Phase==TicketPhase.Delivered)){g.Phase=GroupPhase.Eating;g.EatUntil=Seconds+RestaurantTuning.EatSeconds;}
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
            Finished=true;Result.Cats=RestaurantPortions.FeedCats(Stock)+soupReady+waste;soupReady=0;waste=0;
            Result.Seconds=Seconds;Result.Stars=Result.Guests==0?0:Result.Stars/Result.Guests;
            Result.PopularityGain=Result.Guests==0?0:(Result.Stars-3)*.5f+Result.SpecialServed*RestaurantTuning.PopularityPerSpecial;
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

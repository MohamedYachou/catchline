using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game.Restaurant
{
    public enum LayoutReason { Ok, Outside, KitchenOnly, GuestsOnly, TerraceOnly, WallOnly, Occupied, StageLocked,
        DoorBlocked, ReceptionBlocked, SeatBlocked, KitchenBlocked, NotEnoughCoins, MissingItem, InvalidStage, Popularity, PassBlocked }
    public readonly struct LayoutResult
    {
        public readonly LayoutReason Reason;
        public bool Ok => Reason==LayoutReason.Ok;
        public string Message => RestaurantLayout.Sentence(Reason);
        public LayoutResult(LayoutReason reason) { Reason=reason; }
    }
    public sealed class RestaurantLayout
    {
        public readonly RestaurantState State;
        public RestaurantLayout(RestaurantState state) { State=state ?? throw new ArgumentNullException(nameof(state)); }
        public StageDef Stage => RestaurantData.Stage(State.Stage);
        public Vector2Int Door => new Vector2Int(Stage.Width-1,0);
        public Vector2Int PassKitchen => new Vector2Int(Stage.KitchenWidth-1,2);
        public Vector2Int PassGuests => new Vector2Int(Stage.KitchenWidth+1,2);
        public IEnumerable<RestaurantItem> Active => State.Items.Where(i=>!i.Stored);
        public int FridgeCapacity => (Active.Count(i=>i.Id==ItemId.Fridge)+(HasUpgrade("BigFridge")?1:0))*RestaurantTuning.FridgePortions;
        public bool HasUpgrade(string id) => State.Upgrades!=null&&State.Upgrades.Contains(id);
        public bool Has(ItemId id) => Active.Any(i=>i.Id==id);
        public bool CanCook(Dish d) => Has(RestaurantData.Get(d).Appliance);
        public int Ambience => Active.Count(i=>RestaurantData.Get(i.Id).Area==Area.Decor || RestaurantData.Get(i.Id).Area==Area.Wall)+(HasUpgrade("CosyLighting")?2:0);
        public static string Sentence(LayoutReason reason)
        {
            switch(reason) {
                case LayoutReason.Ok:return "Ready to place";
                case LayoutReason.Outside:return "Keep the item inside the room";
                case LayoutReason.KitchenOnly:return "Kitchen items go in the kitchen";
                case LayoutReason.GuestsOnly:return "Guest items go in the guest area";
                case LayoutReason.TerraceOnly:return "Terrace tables go on the terrace";
                case LayoutReason.WallOnly:return "Hang this on a wall";
                case LayoutReason.Occupied:return "This space is already taken";
                case LayoutReason.StageLocked:return "Expand the restaurant to unlock this item";
                case LayoutReason.DoorBlocked:return "Leave a way to the door";
                case LayoutReason.ReceptionBlocked:return "Leave a way to reception";
                case LayoutReason.SeatBlocked:return "Leave a way to every table";
                case LayoutReason.KitchenBlocked:return "Leave a way to each kitchen station";
                case LayoutReason.PassBlocked:return "Leave the pass and its access clear";
                case LayoutReason.NotEnoughCoins:return "You need more coins";
                case LayoutReason.MissingItem:return "That item is no longer here";
                case LayoutReason.InvalidStage:return "Expand one stage at a time";
                case LayoutReason.Popularity:return "Welcome more guests to unlock this expansion";
                default:throw new ArgumentOutOfRangeException(nameof(reason));
            }
        }
        public IEnumerable<Vector2Int> Cells(RestaurantItem i)
        {
            var d=RestaurantData.Get(i.Id); int w=i.Rotated?d.Height:d.Width,h=i.Rotated?d.Width:d.Height;
            for(int y=0;y<h;y++)for(int x=0;x<w;x++)yield return new Vector2Int(i.X+x,i.Y+y);
        }
        public bool Inside(Vector2Int p) => p.x>=0 && p.y>=0 && p.x<Stage.TotalWidth && p.y<Stage.Depth;
        bool Pass(Vector2Int p) => p.x==Stage.KitchenWidth && p.y>0;
        public bool Walkable(Vector2Int p) => Inside(p) && !Pass(p) && !Active.Any(i=>RestaurantData.Get(i.Id).Area!=Area.Wall && Cells(i).Contains(p));
        static readonly Vector2Int[] Directions={Vector2Int.right,Vector2Int.up,Vector2Int.left,Vector2Int.down};
        public List<Vector2Int> Path(Vector2Int from, Vector2Int to)
        {
            // Build occupancy once per search, rather than enumerating every footprint per neighbour.
            int width=Stage.TotalWidth, height=Stage.Depth, pass=Stage.KitchenWidth;
            var blocked=new bool[width,height];
            foreach(var item in Active)if(RestaurantData.Get(item.Id).Area!=Area.Wall)
                foreach(var tile in Cells(item))if(Inside(tile))blocked[tile.x,tile.y]=true;
            bool Free(Vector2Int p)=>p.x>=0&&p.y>=0&&p.x<width&&p.y<height&&!(p.x==pass&&p.y>0)&&!blocked[p.x,p.y];
            if(!Free(from)||!Free(to))return null;
            var parents=new Dictionary<Vector2Int,Vector2Int>();var q=new Queue<Vector2Int>();q.Enqueue(from);parents[from]=from;
            while(q.Count>0){var p=q.Dequeue();if(p==to){var path=new List<Vector2Int>();while(p!=from){path.Add(p);p=parents[p];}path.Reverse();return path;}
                foreach(var d in Directions){var n=p+d;if(!parents.ContainsKey(n)&&Free(n)){parents[n]=p;q.Enqueue(n);}}}
            return null;
        }
        public Vector2Int? Access(RestaurantItem i, Vector2Int from)
        {
            Vector2Int? best=null;int distance=int.MaxValue;
            foreach(var c in Cells(i))foreach(var d in Directions){var p=c+d;var path=Path(from,p);if(path!=null&&path.Count<distance){best=p;distance=path.Count;}}
            return best;
        }
        LayoutResult Geometry(RestaurantItem i)
        {
            var def=RestaurantData.Get(i.Id);
            if(def.Stage>State.Stage)return new LayoutResult(LayoutReason.StageLocked);
            foreach(var p in Cells(i)){
                if(!Inside(p))return new LayoutResult(LayoutReason.Outside);
                if(def.Area==Area.Wall){if(p.y!=Stage.Depth-1 && p.x!=0 && p.x!=Stage.TotalWidth-1)return new LayoutResult(LayoutReason.WallOnly);}
                else {
                    if(p==Door)return new LayoutResult(LayoutReason.DoorBlocked);
                    if(Pass(p)||p==PassKitchen||p==PassGuests)return new LayoutResult(LayoutReason.PassBlocked);
                    if(def.Area==Area.Kitchen && p.x>=Stage.KitchenWidth)return new LayoutResult(LayoutReason.KitchenOnly);
                    if(def.Area!=Area.Kitchen && p.x<=Stage.KitchenWidth)return new LayoutResult(LayoutReason.GuestsOnly);
                    if(i.Id==ItemId.TerraceTable && p.x<Stage.Width)return new LayoutResult(LayoutReason.TerraceOnly);
                }
                if(Active.Any(other=>other.Uid!=i.Uid && (RestaurantData.Get(other.Id).Area==Area.Wall)==(def.Area==Area.Wall) && Cells(other).Contains(p)))return new LayoutResult(LayoutReason.Occupied);
            }
            return new LayoutResult(LayoutReason.Ok);
        }
        public LayoutResult Validate()
        {
            foreach(var i in Active){var g=Geometry(i);if(!g.Ok)return g;}
            if(!Walkable(Door))return new LayoutResult(LayoutReason.DoorBlocked);
            if(Path(Door,PassGuests)==null || Path(PassKitchen,PassGuests)==null)return new LayoutResult(LayoutReason.DoorBlocked);
            foreach(var i in Active){var d=RestaurantData.Get(i.Id);
                if(d.Area==Area.Wall)continue;
                var from=d.Area==Area.Kitchen?PassKitchen:Door;
                if(Access(i,from)==null)return new LayoutResult(i.Id==ItemId.Reception?LayoutReason.ReceptionBlocked:d.Seats>0?LayoutReason.SeatBlocked:d.Area==Area.Kitchen?LayoutReason.KitchenBlocked:LayoutReason.SeatBlocked);
            }
            return new LayoutResult(LayoutReason.Ok);
        }
        public LayoutResult CheckPlacement(ItemId id,int x,int y,bool rotate=false,int uid=0)
        {
            var old=State.Items.FirstOrDefault(i=>i.Uid==uid);var candidate=new RestaurantItem{Uid=uid==0?-1:uid,Id=id,X=x,Y=y,Rotated=rotate};
            if(old!=null)State.Items.Remove(old);State.Items.Add(candidate);
            LayoutResult result;
            try { result=Validate(); } finally {State.Items.Remove(candidate);if(old!=null)State.Items.Add(old);}
            return result;
        }
        public LayoutResult Buy(ItemId id,int x,int y,bool rotate=false)
        {
            var r=CheckPlacement(id,x,y,rotate);if(!r.Ok)return r;
            var d=RestaurantData.Get(id);if(State.Coins<d.Price)return new LayoutResult(LayoutReason.NotEnoughCoins);
            State.Coins-=d.Price;State.Items.Add(new RestaurantItem{Uid=State.NextUid++,Id=id,X=x,Y=y,Rotated=rotate});return r;
        }
        public LayoutResult Move(int uid,int x,int y,bool rotate=false)
        {
            var i=State.Items.FirstOrDefault(a=>a.Uid==uid);if(i==null)return new LayoutResult(LayoutReason.MissingItem);
            var r=CheckPlacement(i.Id,x,y,rotate,uid);if(r.Ok){i.X=x;i.Y=y;i.Rotated=rotate;i.Stored=false;}return r;
        }
        public LayoutResult Rotate(int uid){var i=State.Items.FirstOrDefault(a=>a.Uid==uid);return i==null?new LayoutResult(LayoutReason.MissingItem):Move(uid,i.X,i.Y,!i.Rotated);}
        public LayoutResult Store(int uid)
        {
            var i=State.Items.FirstOrDefault(a=>a.Uid==uid);if(i==null)return new LayoutResult(LayoutReason.MissingItem);
            bool previous=i.Stored;i.Stored=true;var r=Validate();if(!r.Ok)i.Stored=previous;return r;
        }
        public LayoutResult Sell(int uid)
        {
            var i=State.Items.FirstOrDefault(a=>a.Uid==uid);if(i==null)return new LayoutResult(LayoutReason.MissingItem);
            var r=Store(uid);if(!r.Ok)return r;State.Items.Remove(i);State.Coins+=(int)(RestaurantData.Get(i.Id).Price*RestaurantTuning.SellBack);return r;
        }
        public LayoutResult Expand(int nextStage)
        {
            if(nextStage!=State.Stage+1 || nextStage>4)return new LayoutResult(LayoutReason.InvalidStage);
            var next=RestaurantData.Stage(nextStage);if(State.Popularity<next.Popularity)return new LayoutResult(LayoutReason.Popularity);
            if(State.Coins<next.Price)return new LayoutResult(LayoutReason.NotEnoughCoins);
            int oldStage=State.Stage,oldKitchen=Stage.KitchenWidth;var snapshots=State.Items.Select(i=>i.Copy()).ToList();
            // Insert added kitchen columns at the pass; shift guest-side items together to preserve their layout.
            foreach(var i in State.Items)if(!i.Stored && i.X>=oldKitchen)i.X+=next.KitchenWidth-oldKitchen;
            State.Stage=nextStage;var r=Validate();if(!r.Ok){State.Stage=oldStage;State.Items=snapshots;return r;}
            State.Coins-=next.Price;return r;
        }
        // Service v2 (Mo 10-28, "we must serve a lot more customers"): the cafe seats ten from the first night. New saves
        // and old ones both get the two extra tables, free, wherever they still fit and the room stays valid.
        public static RestaurantState WithServiceTables(RestaurantState s)
        {
            if(s.Stage>1)return s;
            foreach(var (id,x,y) in new[]{(ItemId.Table4,5,4),(ItemId.Table2,7,2)}){
                var l=new RestaurantLayout(s);
                if(l.Active.Count(i=>RestaurantData.Get(i.Id).Seats>0&&i.Id!=ItemId.BarCounter)>=4)break;
                if(!l.CheckPlacement(id,x,y).Ok)continue;
                s.Items.Add(new RestaurantItem{Uid=s.NextUid++,Id=id,X=x,Y=y});
                if(!new RestaurantLayout(s).Validate().Ok)s.Items.RemoveAt(s.Items.Count-1);
            }
            return s;
        }
        public static RestaurantState StartingKit()
        {
            var s=new RestaurantState();
            Action<ItemId,int,int> put=(id,x,y)=>s.Items.Add(new RestaurantItem{Uid=s.NextUid++,Id=id,X=x,Y=y});
            put(ItemId.Stove,0,4);put(ItemId.SoupKettle,0,3);put(ItemId.PrepCounter,2,4);put(ItemId.Fridge,0,1);
            put(ItemId.CoffeeMachine,4,4);put(ItemId.Reception,6,0);put(ItemId.Table2,5,2);put(ItemId.Table2,7,4);
            return s;
        }
    }
}

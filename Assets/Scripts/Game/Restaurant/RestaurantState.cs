using System;
using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game.Restaurant
{
    [Serializable] public sealed class RestaurantItem
    {
        public int Uid; public ItemId Id; public int X, Y; public bool Rotated, Stored;
        public RestaurantItem Copy() => (RestaurantItem)MemberwiseClone();
    }
    [Serializable] public sealed class RestaurantState
    {
        public const int CurrentVersion = 1;
        public int Version = CurrentVersion, Stage = 1, Popularity = 1, Day, Coins, NextUid = 1;
        public string Name = "Mira's";
        public List<RestaurantItem> Items = new List<RestaurantItem>();
        public List<PortionStock> Stock = new List<PortionStock>();
        public string ToJson() => JsonUtility.ToJson(this,true);
        public static RestaurantState FromJson(string json)
        {
            var s=JsonUtility.FromJson<RestaurantState>(json);
            if(s==null || s.Version!=CurrentVersion || s.Stage<1 || s.Stage>4 || s.Coins<0 || s.Items==null || s.Stock==null)
                throw new ArgumentException("Unsupported restaurant save");
            var ids=new HashSet<int>(); int max=0;
            foreach(var i in s.Items) { if(i==null || i.Uid<=0 || !ids.Add(i.Uid) || !Enum.IsDefined(typeof(ItemId),i.Id)) throw new ArgumentException("Invalid restaurant item"); max=Math.Max(max,i.Uid); }
            s.NextUid=Math.Max(s.NextUid,max+1);
            var valid=new RestaurantLayout(s).Validate();
            if(!valid.Ok) throw new ArgumentException(valid.Message);
            return s;
        }
    }
}

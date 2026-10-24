using System;
using System.Linq;
using System.Collections;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        CrewMember CounterOffer(CrewRole role) => State.Board.Where(c=>c.Role==role).OrderBy(c=>c.Fee).FirstOrDefault();
        bool ChangeCrewCounter(CrewRole role, bool add)
        {
            if(CurrentMode!=Mode.Harbour)return false;
            if(add) { var offer=CounterOffer(role); if(offer==null || !State.Hire(offer))return false; }
            else
            {
                var member=State.Crew.LastOrDefault(c=>c.Role==role);if(member==null)return false;
                if(State.Deckhand==member)State.Deckhand=null;else State.ExtraCrew.Remove(member);
                State.Coins+=member.Fee;
                State.Board.Add(member);
            }
            SyncCrew();SaveGame();return true;
        }
        void InterfaceCrewCounter(CrewRole role,string title)
        {
            var members=State.Crew.Where(c=>c.Role==role).ToArray();var offer=CounterOffer(role);
            string id="crew/count/"+role;float y=catalogY,w=catalogWidth;
            float height=122+members.Length*44;
            coastalUi.Box(id,new Rect(0,y,w,height),"card-white",null,catalog);
            coastalUi.Label(id+"/title",new Rect(18,y+8,w-210,38),title,24,null,TextAnchor.MiddleLeft,catalog);
            coastalUi.Button(id+"/minus",new Rect(w-190,y+12,48,48),"−",()=>ChangeCrewCounter(role,false),"button-secondary-normal",members.Length>0,catalog,24);
            coastalUi.Label(id+"/count",new Rect(w-140,y+12,78,48),$"{members.Length}/{State.HullDef.CrewCap}",23,null,TextAnchor.MiddleCenter,catalog);
            coastalUi.Button(id+"/plus",new Rect(w-60,y+12,48,48),"+",()=>ChangeCrewCounter(role,true),"button-primary-normal",offer!=null && State.CrewCount<State.HullDef.CrewCap && State.Coins>=offer.Fee,catalog,24);
            string detail=offer==null?"No contracts available":$"Add: {offer.Fee} coins · {offer.VoyagesLeft} voyages";
            detail+=members.Length>0?$"   /   Remove: +{members.Last().Fee} coins":"";
            coastalUi.Label(id+"/price",new Rect(18,y+65,w-36,44),detail,16,SeaInk,TextAnchor.MiddleLeft,catalog);
            for(int i=0;i<members.Length;i++)
            {
                var c=members[i];string label=role==CrewRole.Engineer ? $"{i+1}. {c.Name} / Maintenance + repairs" : role==CrewRole.Fisherman?$"{i+1}. {c.Name} · Bait":$"{i+1}. {c.Name} / {c.WorkPreference}";
                coastalUi.Button(id+"/settings/"+i,new Rect(16,y+112+i*44,w-32,40),label,()=>
                {
                    if(role==CrewRole.Fisherman)OpenCrewBait(c);
                    else if(role==CrewRole.Deckhand && IsNetFisher)SetDeckhandWork(c,c.WorkPreference==DeckhandWork.Fish?DeckhandWork.Nets:c.WorkPreference==DeckhandWork.Nets && IsPrepFisher?DeckhandWork.Prep:DeckhandWork.Fish);
                },"button-secondary-normal",role!=CrewRole.Engineer && (role==CrewRole.Fisherman || IsNetFisher),catalog,16);
            }
            catalogY+=height+16;
        }
    }
}


using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        CrewMember baitSettingsCrew;
        CrewMember BaitOwner(Rod rod) => rod.Fisher?.Contract;
        bool CanBaitRod(Rod rod) => State.CanTakeBait(BaitOwner(rod));
        public void OpenCrewBait(CrewMember crew)
        {
            if (crew == null || crew.Role != CrewRole.Fisherman || !State.Crew.Contains(crew)) return;
            baitSettingsCrew = crew; toastUntil = 0;
        }
        public void ToggleCrewBait(CrewMember crew, BaitPermission bait)
        {
            if (crew == null || crew.Role != CrewRole.Fisherman || !State.Crew.Contains(crew)) return;
            crew.AllowedBait = crew.BaitPolicy ^ (bait & BaitPermission.All); crew.HasBaitPolicy = true;
            forecastSignature=flowCrewSignature=null; SaveGame();
        }
        void InterfaceCrewBait()
        {
            if (baitSettingsCrew == null) return;
            if (!State.Crew.Contains(baitSettingsCrew)) { baitSettingsCrew = null; return; }
            var c = baitSettingsCrew;
            Block(new Rect(0,0,iw,ih));
            coastalUi.Box("crew/bait/shade", new Rect(0,0,iw,ih), "chip-dark", new Color(1,1,1,.8f));
            var p = new Rect((iw-550)/2,(ih-360)/2,550,360);
            coastalUi.Box("crew/bait/panel",p);
            coastalUi.Label("crew/bait/title",new Rect(p.x+20,p.y+12,430,36),"Bait · " + c.Name,25);
            IButton("crew/bait/close",new Rect(p.xMax-74,p.y+8,54,48),"X",()=>baitSettingsCrew=null,false);
            coastalUi.Label("crew/bait/help",new Rect(p.x+20,p.y+62,510,50),"Choose what this fisher may use.\nApplies to hooks baited by this fisher or a deckhand.",17,SeaInk);
            var choices = new[]{BaitPermission.Scraps,BaitPermission.Worms,BaitPermission.Squid,BaitPermission.Chum};
            for(int i=0;i<choices.Length;i++)
            {
                var b=choices[i]; bool on=(c.BaitPolicy & b)!=0;
                IButton("crew/bait/"+b,new Rect(p.x+20+i%2*262,p.y+126+i/2*64,248,54),b+": "+(on?"Allowed":"Off"),()=>ToggleCrewBait(c,b),on);
            }
            coastalUi.Label("crew/bait/status",new Rect(p.x+20,p.y+266,510,70),
                "Chum first, then your squid/worm preference.\nNo allowed bait in stock? This fisher waits.\nAlready baited hooks keep their bait.",16,SeaInk);
        }
    }
}

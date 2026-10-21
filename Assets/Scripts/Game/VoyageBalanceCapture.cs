using System.Collections;
using System.IO;
using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        IEnumerator CaptureBalance045(string directory)
        {
            Application.runInBackground=true;
            yield return null;
            Directory.CreateDirectory(directory);
            StartPrepBoatTrial();captureFreeze=true;toastUntil=0;

            var fisher=State.Crew.First(c=>c.Role==CrewRole.Fisherman);
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                var hands=People.Where(p=>p.Contract?.Role==CrewRole.Deckhand).ToArray();
                CancelCaptainPrep();ClearPrepWork();Showcase(0,0);Cooler.Clear();State.Chum=3;
                Screen.SetResolution(size.x,size.y,FullScreenMode.Windowed);
                for(int i=0;i<16;i++)yield return null;
                Cooler.Add(new CaughtFish{Species=Species.Pollock,Kg=1.4f,StowedAt=SimTime});
                Cooler.Add(new CaughtFish{Species=Species.Conger,Kg=7,StowedAt=SimTime});
                State.PrepOrders.ChumMaxKg=2;State.PrepOrders.PrepareHighestValue=true;
                State.PrepOrders.ChumTarget=10;
                PrepOrdersOpen=true;netOrdersOpen=false;toastUntil=0;yield return null;
                yield return CaptureFrame(directory,"prep-priority-"+size.x);
                PrepOrdersOpen=false;Showcase(-1,0);hudTab=HudTab.CrewOffice;panelOpen=true;toastUntil=0;yield return null;
                var crewScroll=coastalUi.Root.GetComponentsInChildren<UnityEngine.UI.ScrollRect>().FirstOrDefault(s=>s.gameObject.name=="catalog/CrewOffice");
                var fisherCard=coastalUi.Root.GetComponentsInChildren<RectTransform>().FirstOrDefault(t=>t.gameObject.name=="employee/"+fisher.Name);
                if(crewScroll!=null&&fisherCard!=null)crewScroll.content.anchoredPosition=new Vector2(0,-fisherCard.anchoredPosition.y);
                yield return null;
                yield return CaptureFrame(directory,"crew-bait-button-"+size.x);
                OpenCrewBait(fisher);fisher.HasBaitPolicy=true;fisher.AllowedBait=BaitPermission.Scraps|BaitPermission.Worms;
                yield return null;yield return CaptureFrame(directory,"fisher-bait-"+size.x);
                baitSettingsCrew=null;Showcase(0,0);Cooler.Clear();State.PrepOrders.ChumTarget=0;
                foreach(var h in hands){h.Stop();SetDeckhandWork(h.Contract,DeckhandWork.Prep);}
                for(int n=0;n<4;n++)Cooler.Add(new CaughtFish{Species=Species.Conger,Kg=7,StowedAt=SimTime});
                Cooler.Add(new CaughtFish{Species=Species.Cod,Kg=State.CoolerCapacity-28,Prepared=true,PreparedQuality=1});
                foreach(var h in hands)TryPrepWork(h);
                StartCaptainPrep();for(int n=0;n<3000&&Captain.Walking;n++)Captain.Tick(.02f,1,Cam.transform.rotation);
                foreach(var h in hands)for(int n=0;n<3000&&h.Walking;n++)h.Tick(.02f,1,Cam.transform.rotation);
                TickCaptainPrep(.6f);toastUntil=0;yield return null;
                yield return CaptureFrame(directory,"captain-full-hold-"+size.x);
                CancelCaptainPrep();ClearPrepWork();Cooler.Clear();Showcase(-1,0);
                State.Hull=2;State.Coins=9500;State.BestVoyageKg=100;RebuildBoat();
                hudTab=HudTab.Chandlery;panelOpen=true;toastUntil=0;yield return null;
                // Move scroll to the real refit card near the end of the gear catalogue.
                var scroll=coastalUi.Root.GetComponentsInChildren<UnityEngine.UI.ScrollRect>().FirstOrDefault(s=>s.gameObject.name=="catalog/Chandlery");
                if(scroll!=null)scroll.verticalNormalizedPosition=0;
                yield return null;yield return CaptureFrame(directory,"prep-refit-"+size.x);
                State.Hull=3;RebuildBoat();
            }
            Debug.Log("[Catchline] BALANCE045 NATIVE CAPTURES COMPLETE");Application.Quit(0);
        }
    }
}

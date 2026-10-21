using System.Collections;
using System.IO;
using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool ConfigureTier5NetTeam()
        {
            if(!IsTier5 || CurrentMode!=Mode.Harbour)return false;
            State.SecondNetEnabled=true;
            var fishers=State.Crew.Where(c=>c.Role==CrewRole.Fisherman).ToArray();
            for(int i=0;i<fishers.Length;i++) { fishers[i].HasFisherTasks=true;fishers[i].AllowedTasks=i<2?FisherTask.Nets:FisherTask.Rods|FisherTask.Crabs; }
            var hands=State.Crew.Where(c=>c.Role==CrewRole.Deckhand).ToArray();
            for(int i=0;i<hands.Length;i++)hands[i].WorkPreference=i==0?DeckhandWork.Prep:DeckhandWork.Fish;
            RebuildBoat(false);return true;
        }
        IEnumerator CaptureTier5(string directory)
        {
            Application.runInBackground=true;
            Directory.CreateDirectory(directory);
            StartTier5Trial();captureFreeze=true;
            for(int n=0;n<2000;n++)Tick(.05f);
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,false);
                for(int f=0;f<20;f++)yield return null;
                toastUntil=0;Visual(.02f);
                yield return CaptureFrame(directory,"tier5-rods-"+size.x);
                tier5OperationsOpen=true;Visual(.02f);yield return null;
                yield return CaptureFrame(directory,"tier5-condition-"+size.x);
                tier5OperationsOpen=false;PrepOrdersOpen=true;Visual(.02f);yield return null;
                yield return CaptureFrame(directory,"tier5-processing-"+size.x);
                PrepOrdersOpen=false;
            }
            HeadHome();for(int n=0;n<2000&&CurrentMode!=Mode.Harbour;n++)Tick(.05f);ResetNet();ConfigureTier5NetTeam();Showcase(0,0);captureFreeze=true;
            for(int n=0;n<1800;n++)Tick(.05f);
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,false);for(int f=0;f<20;f++)yield return null;
                toastUntil=0;Visual(.02f);yield return CaptureFrame(directory,"tier5-nets-"+size.x);
            }
            Showcase(-1,0);hudTab=HudTab.CrewOffice;panelOpen=true;toastUntil=0;
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,false);for(int f=0;f<20;f++)yield return null;
                Visual(.02f);yield return CaptureFrame(directory,"tier5-crew-"+size.x);
            }
            Debug.Log("[Catchline] TIER071 NATIVE CAPTURES COMPLETE");Application.Quit(0);
        }
    }
}

using System.Collections;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        IEnumerator CaptureGeminiUi(string directory)
        {
            Directory.CreateDirectory(directory);Application.runInBackground=true;
            captureFreeze=true;AutoPlay=false;showTitle=paused=panelOpen=PrepOrdersOpen=netOrdersOpen=false;
            bool fish050=System.Environment.GetCommandLineArgs().Contains("-fish050-only");
            var specimens=GameData.Fish.Select(f=>f.Species).Where(s=>!fish050||(int)s>=25).ToArray();
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,FullScreenMode.Windowed);
                for(int i=0;i<16;i++)yield return null;
                State.Coins=1000;Showcase(0,0);captureFreeze=true;toastUntil=0;Tick(.01f);yield return null;
                // The front-edge rod keeps new model review clear of the roof and crew.
                // This changes only the opt-in save-isolated FISH050 capture fixture.
                if(fish050){Captain.Stop();Captain.Place(State.HullDef.Seat);}
                catchUntil=0;yield return CaptureFrame(directory,"hud-"+size.x);
                foreach(var s in specimens)
                {
                    var d=GameData.Get(s);lastCatchSpecies=s;lastCatchKg=s==Species.Mackerel?d.MinKg:s==Species.GoldenPuffer?.6f:d.MaxKg;
                    catchNew=(int)s>=10;catchRecord=!catchNew;catchUntil=SimTime+CatchDisplaySeconds-.5f;toastUntil=0;
                    // One real world mesh per specimen lets the same capture check portrait and deck model.
                    foreach(var f in OnDeck.ToArray()){if(f.Root!=null)Destroy(f.Root.gameObject);}OnDeck.Clear();
                    LandFish(fish050?Rods[1]:Rods[0],s,lastCatchKg);
                    foreach(var fish in OnDeck){fish.Age=1;fish.Root.localPosition=fish.RestPos;}
                    catchUntil=SimTime+CatchDisplaySeconds-.5f;
                    yield return null;yield return CaptureFrame(directory,"catch-"+s+"-"+size.x);
                }
                State.Coins=int.MaxValue;lastCatchSpecies=Species.AbyssalGreatWhite;lastCatchKg=GameData.Get(lastCatchSpecies).MaxKg;
                catchUntil=SimTime+CatchDisplaySeconds-.5f;PrepareInterface(size.x,size.y,1.25f);yield return null;
                yield return CaptureFrame(directory,"large-type-long-name-"+size.x);PrepareInterface(0,0,0);
                catchUntil=0;PrepOrdersOpen=true;yield return null;yield return CaptureFrame(directory,"prep-orders-"+size.x);
                PrepOrdersOpen=false;netOrdersOpen=true;yield return null;yield return CaptureFrame(directory,"crew-duties-"+size.x);netOrdersOpen=false;
                HeadHome();for(int i=0;i<2000&&CurrentMode!=Mode.Harbour;i++)Tick(.1f);
                OpenShop(HudTab.Market);yield return null;yield return CaptureFrame(directory,"market-"+size.x);
                OpenShop(HudTab.Chandlery);yield return null;yield return CaptureFrame(directory,"gear-"+size.x);
                OpenShop(HudTab.HarbourMaster);yield return null;yield return CaptureFrame(directory,"chart-"+size.x);
            }
            Debug.Log("[Catchline] UI041 NATIVE CAPTURES COMPLETE");Application.Quit(0);
        }
    }
}

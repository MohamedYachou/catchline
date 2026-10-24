using System;
using System.Collections;
using System.IO;
using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        bool prepRarityCaptureStarted;
        void MaybeCapturePrepRarity()
        {
            if(!Application.isPlaying||!SessionOnly||prepRarityCaptureStarted)return;
            var args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"-capture-prep047");
            if(n<0||n+1>=args.Length)return;
            prepRarityCaptureStarted=true;StartCoroutine(CapturePrepRarity(args[n+1]));
        }
        IEnumerator CapturePrepRarity(string directory)
        {
            Application.runInBackground=true;Directory.CreateDirectory(directory);yield return null;
            StartPrepBoatTrial();captureFreeze=true;toastUntil=0;
            State.Chum=8;Cooler.Add(new CaughtFish{Species=Species.Cod,Kg=4,StowedAt=SimTime});
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,false);for(int n=0;n<16;n++)yield return null;
                PrepOrdersOpen=true;prepClassDropdown=0;toastUntil=0;yield return null;
                yield return CaptureFrame(directory,"prep-table-"+size.x);
                prepClassDropdown=1;yield return null;yield return CaptureFrame(directory,"chum-classes-"+size.x);
            }
            PrepOrdersOpen=false;prepClassDropdown=0;Cooler.Clear();Showcase(-1,0);
            State.SecondNetOwned=true;State.SecondNetEnabled=true;RebuildBoat();Showcase(0,0);captureFreeze=true;
            var hands=People.Where(p=>p.Contract?.Role==CrewRole.Deckhand).ToArray();
            foreach(var h in hands){h.Stop();SetDeckhandWork(h.Contract,DeckhandWork.Nets);AssignedNet(h);}
            Net=NetState.Soaking;netSoak=GameData.ShallowNetSoakSeconds;SecondNet=NetState.Ready;secondNetFish.Clear();
            for(int i=0;i<8;i++)secondNetFish.Add((Species.Mackerel,.8f));
            State.Rng=new System.Random(0);hands[1].Place(SecondNetAccess);TryNetWork(hands[1]);
            for(int n=0;n<3000&&!hands[1].Idle;n++)hands[1].Tick(.02f, Cam.transform.rotation);
            TickDeckFish(.5f);toastUntil=0;
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,false);for(int n=0;n<16;n++)yield return null;
                yield return CaptureFrame(directory,"net2-catch-at-net2-"+size.x);
            }
            for(int n=0;n<3000&&!hands[1].CarryingBatch;n++){TickNetUnload(.02f);hands[1].Tick(.02f, Cam.transform.rotation);}
            hands[1].Tick(.4f, Cam.transform.rotation);
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,false);for(int n=0;n<16;n++)yield return null;
                yield return CaptureFrame(directory,"net2-carry-batch-"+size.x);
            }
            for(int n=0;n<3000&&NetUnloadActive;n++){TickNetUnload(.02f);hands[1].Tick(.02f, Cam.transform.rotation);TickDeckFish(.02f);}
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,false);for(int n=0;n<16;n++)yield return null;
                yield return CaptureFrame(directory,"net2-stowed-clear-actions-"+size.x);
                netOrdersOpen=true;yield return null;yield return CaptureFrame(directory,"assigned-net-duties-"+size.x);netOrdersOpen=false;
            }
            Debug.Log("[Catchline] PREP047 NATIVE CAPTURES COMPLETE");Application.Quit(0);
        }
    }
}

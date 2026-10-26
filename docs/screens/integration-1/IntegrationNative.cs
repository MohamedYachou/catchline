using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
namespace Catchline.Game {
 public partial class VoyageGame {
  [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
  static void StartIntegrationCapture() {
   var args=Environment.GetCommandLineArgs(); int i=Array.IndexOf(args,"-capture-integration");
   if(i<0||i+1>=args.Length)return;
   var g=UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
   if(g==null||!g.SessionOnly){Application.Quit(7);return;}
   g.StartCoroutine(g.CaptureIntegration(Path.GetFullPath(args[i+1])));
  }
  IEnumerator CaptureIntegration(string directory) {
   yield return null;
   Application.runInBackground=true;Directory.CreateDirectory(directory);
   NewGame();EndIntro();State=new GameState(6501);State.Hull=4;State.Coins=10000;State.Fuel=State.FuelCapacity;
   State.Tutorial=(int)TutStep.Done;
   captureFreeze=true;showTitle=paused=panelOpen=false;Time.timeScale=0;
   RebuildBoat(false);Tick(.05f);
   // NewGame schedules the previous harbour for destruction at the frame boundary.
   yield return null;
   if(UnityEngine.Object.FindObjectsByType<HarbourDog>(FindObjectsSortMode.None).Length!=1||UnityEngine.Object.FindObjectsByType<HarbourCat>(FindObjectsSortMode.None).Length!=1){Fail("pets production hook");yield break;}
   var frames=new List<string>();
   yield return Frames("harbour-pets");
   chartFocus=9;chartDetailsOpen=chartContractsOpen=false;hudTab=HudTab.HarbourMaster;panelOpen=true;
   yield return Frames("chart");
   chartDetailsOpen=true;PrepareInterface(1440,900);
   if(!InvokeInterface("chart/select")||!State.Known(9)){Fail("chart9 purchase");yield break;}
   panelOpen=false;SetSail();
   if(!Until(()=>CurrentMode==Mode.Fishing&&Leg==TripLeg.None)){Fail("normal departure to Seal cliffs");yield break;}
   var rod=Rods.FirstOrDefault(CanCommandRod);
   if(rod==null){Fail("captain rod");yield break;}
   CommandRod(rod);
   if(!Until(()=>RodViewActive&&rod.State==RodState.Bite)){Fail("real cast to bite");yield break;}
   yield return Frames("bite");
   PrepareInterface(1440,900);StrikeTap();
   if(rod.ReadingResult!=StrikeResult.Hooked){Fail("strike hooks fish");yield break;}
   Tick(.12f);yield return Frames("strike");
   HeadHome();if(!Until(()=>CurrentMode==Mode.Harbour)){Fail("home");yield break;}
   File.WriteAllLines(Path.Combine(directory,"capture-complete.txt"),frames);
   Debug.Log("[Catchline] INTEGRATION NATIVE COMPLETE: one SessionOnly pets/chart9 purchase/departure/cast/bite/strike/home session; "+frames.Count+" frames");Application.Quit(0);
   bool Until(Func<bool> done){for(int n=0;n<20000&&!done();n++)Tick(.025f);return done();}
   void Fail(string why){Debug.LogError("[Catchline] INTEGRATION NATIVE FAILED: "+why);Application.Quit(8);}
   IEnumerator Frames(string stage) {
    toastUntil=catchUntil=0;
    foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)}) {
     Screen.SetResolution(size.x,size.y,false);for(int n=0;n<20;n++)yield return null;
     PrepareInterface(size.x,size.y);snapCamera=true;for(int n=0;n<80;n++)Visual(.025f);
     for(int n=0;n<8;n++)yield return null;
     yield return new WaitForEndOfFrame();var frame=ScreenCapture.CaptureScreenshotAsTexture();
     string name=stage+"-"+size.x+".png";File.WriteAllBytes(Path.Combine(directory,name),frame.EncodeToPNG());Destroy(frame);
     string record=name+" mode="+CurrentMode+" leg="+Leg+" ground="+ActiveGroundId+" simTime="+SimTime;
     frames.Add(record);Debug.Log("[Catchline] INTEGRATION FRAME "+record);
    }
   }
  }
 }
}

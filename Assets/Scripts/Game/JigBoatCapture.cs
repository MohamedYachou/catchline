using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
namespace Catchline.Game {
public partial class VoyageGame {
[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
static void StartJigCapture() {
 var args=Environment.GetCommandLineArgs();int at=Array.IndexOf(args,"-capture-jig");
 if(at<0||at+1>=args.Length||Application.isEditor||Application.isBatchMode)return;
 var g=UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
 if(g==null||!g.SessionOnly){Debug.LogError("Jig capture needs SessionOnly");Application.Quit(7);return;}
 g.StartCoroutine(g.CaptureJig(Path.GetFullPath(args[at+1])));
}
IEnumerator CaptureJig(string directory) {
 yield return null;Directory.CreateDirectory(directory);Application.runInBackground=true;
 NewGame();EndIntro();State=new GameState(7021){Hull=2,Coins=100000};State.Fuel=State.FuelCapacity;
 captureFreeze=true;showTitle=paused=panelOpen=false;
 var frames=new List<string>();float oldScale=Time.timeScale;
 try {
 Time.timeScale=0;RebuildBoat(false);Tick(.05f);hudTab=HudTab.Chandlery;panelOpen=true;shopSelection[HudTab.Chandlery]="refit/jig";
 yield return Frames("refit-card");
 PrepareInterface(1440,900);
 // Use the actual refit action, with its normal affordability checks and model rebuild.
 if(!RefitJig()||State.Hull!=5){Fail("Jig refit action");yield break;}
 panelOpen=false;refitUntil=0;State.GrantTrialCards();foreach(var c in State.Roster.ToArray())if(State.Deployment.Count<State.CardBerths)State.DeployCard(c.Id,true);RebuildBoat(false);Tick(.05f);
 yield return Frames("harbour");
 if(!State.BuyChart(4)){Fail("Deep channel chart");yield break;}SelectedSpot=4;SetSail();
 if(!Until(()=>CurrentMode==Mode.Fishing&&Leg==TripLeg.None)){Fail("Deep channel arrival");yield break;}
 yield return Frames("anchor-day");
 if(!Until(()=>Rods.Any(CanCommandRod))){Fail("captain rod");yield break;}var rod=Rods.First(CanCommandRod);CommandRod(rod);
 if(!Until(()=>rod.InWater)){Fail("bait/cast");yield break;}
 // Return from the proven cast to the deck through the normal view teardown.
 EndCaptainFishing(rod);for(int n=0;n<60;n++)Tick(.025f);
 if(!Until(()=>People.Any(p=>!p.IsCaptain&&(p.Busy||p.Walking&&!p.Loitering)))){Fail("real crew work");yield break;}
 yield return Frames("deck-working");
 State.NightVoyage=true;for(int n=0;n<160;n++)Tick(.025f);yield return Frames("anchor-night");
 HeadHome();if(!Until(()=>CurrentMode==Mode.Harbour)){Fail("home");yield break;}
 File.WriteAllLines(Path.Combine(directory,"capture-complete.txt"),frames);Debug.Log("[Catchline] JIG NATIVE COMPLETE "+frames.Count+" frames; refit/crew/Deep channel/cast/home");Application.Quit(0);
 }finally{Time.timeScale=oldScale;captureFreeze=false;}
 bool Until(Func<bool> done){for(int n=0;n<16000&&!done();n++)Tick(.025f);return done();}
 void Fail(string stage){Debug.LogError("JIG NATIVE FAIL "+stage);Application.Quit(8);}
 IEnumerator Frames(string stage){
 toastUntil=catchUntil=0;
 foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)}){
 Screen.SetResolution(size.x,size.y,false);for(int n=0;n<20;n++)yield return null;
 PrepareInterface(size.x,size.y);snapCamera=true;for(int n=0;n<80;n++)Visual(.025f);
 for(int n=0;n<8;n++)yield return null;
 yield return new WaitForEndOfFrame();var frame=ScreenCapture.CaptureScreenshotAsTexture();string name=stage+"-"+size.x+".png";
 File.WriteAllBytes(Path.Combine(directory,name),frame.EncodeToPNG());Destroy(frame);
 string row=name+" hull="+State.Hull+" tier="+State.Tier+" mode="+CurrentMode+" leg="+Leg+" lamps="+JigLampsLit+" bulb="+(jigBulb!=null)+" glow="+(jigGlow!=null&&jigGlow.gameObject.activeInHierarchy)+" crew="+State.Deployment.Count+" ground="+ActiveGroundId+" workers="+string.Join(";",People.Select(p=>p.Name+":"+p.State+"@"+p.Tile));frames.Add(row);Debug.Log("[Catchline] JIG FRAME "+row);
 }
 }
}
}
}

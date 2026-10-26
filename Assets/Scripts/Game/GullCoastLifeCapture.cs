using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
namespace Catchline.Game {
public partial class VoyageGame {
[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
static void StartGullCoastCapture(){
 var args=Environment.GetCommandLineArgs();int at=Array.IndexOf(args,"-capture-gull-coast");
 if(at<0||at+1>=args.Length||Application.isEditor||Application.isBatchMode)return;
 var g=UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
 if(g==null||!g.SessionOnly){Debug.LogError("Gull coast capture requires SessionOnly");Application.Quit(7);return;}
 g.StartCoroutine(g.CaptureGullCoast(Path.GetFullPath(args[at+1])));
}
IEnumerator CaptureGullCoast(string directory){
 yield return null;Directory.CreateDirectory(directory);Application.runInBackground=true;
 float oldScale=Time.timeScale;var frames=new List<string>();
 try{
 Time.timeScale=0;captureFreeze=true;
 for(int map=0;map<5;map++){
 NewGame();EndIntro();State=new GameState(8200+map){Hull=2,Coins=100000};State.Fuel=State.FuelCapacity;
 showTitle=paused=panelOpen=false;RebuildBoat(false);Tick(.05f);
 if(!State.Known(map)&&!State.BuyChart(map)){Fail("chart");yield break;}
 SelectedSpot=map;SetSail();if(!Until(()=>CurrentMode==Mode.Fishing&&Leg==TripLeg.None)){Fail("arrival");yield break;}
 for(int ground=0;ground<Navigation.Grounds.Count;ground++){
 if(ground>0){if(!RequestSailMode()||!SailTo(Navigation.Grounds[ground].Centre)){Fail("ground route");yield break;}
 if(!Until(()=>Sailor.Arrived)||!FishHere()){Fail("ground anchor");yield break;}}
 // Real Unity time drives the delivered Legacy clips and bounded bob. The
 // game's update stays frozen; manual Tick above alone advances navigation.
 Time.timeScale=1;yield return new WaitForSeconds(.45f);Time.timeScale=0;
 yield return Frames("ground-"+(ground+1),false);
 if(ground==0){
 var birds=scenery.GetComponentsInChildren<GullCoastBird>();var bobs=scenery.GetComponentsInChildren<GullCoastBob>();
 var poses=birds.Select(b=>b.GetComponentsInChildren<Transform>().Select(t=>t.localRotation).ToArray()).ToArray();
 var positions=bobs.Select(b=>b.transform.localPosition).ToArray();
 Time.timeScale=1;yield return new WaitForSeconds(4.25f);Time.timeScale=0;
 for(int b=0;b<birds.Length;b++)if(!birds[b].GetComponentsInChildren<Transform>().Select((t,i)=>Quaternion.Angle(t.localRotation,poses[b][i])>.1f).Any(x=>x)){Fail("bird motion");yield break;}
 for(int b=0;b<bobs.Length;b++)if(Vector3.Distance(positions[b],bobs[b].transform.localPosition)<.001f){Fail("bob motion");yield break;}
 Debug.Log("[Catchline] GULL LIVE MOTION PASS map="+map+" birds="+birds.Length+" bobs="+bobs.Length);
 yield return Frames("life-detail",true);
 }
 }
 HeadHome();if(!Until(()=>CurrentMode==Mode.Harbour)){Fail("home");yield break;}
 Debug.Log("[Catchline] GULL MAP COMPLETE "+map);
 }
 File.WriteAllLines(Path.Combine(directory,"capture-complete.txt"),frames);Debug.Log("[Catchline] GULL CAPTURE COMPLETE "+frames.Count+" frames");Application.Quit(0);
 }finally{Time.timeScale=oldScale;captureFreeze=false;}
 bool Until(Func<bool> done){for(int n=0;n<24000&&!done();n++)Tick(.025f);return done();}
 void Fail(string stage){Debug.LogError("GULL CAPTURE FAIL "+stage+" map="+ActiveSpot);Application.Quit(8);}
 IEnumerator Frames(string stage,bool detail){
 toastUntil=catchUntil=0;
 foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)}){
 Screen.SetResolution(size.x,size.y,false);for(int n=0;n<20;n++)yield return null;
 PrepareInterface(size.x,size.y);snapCamera=true;for(int n=0;n<80;n++)Visual(.025f);
 for(int n=0;n<8;n++){
 yield return null;
 if(detail){var root=ArtLibrary.Find(scenery.gameObject,"Gull coast life");
 var subject=root.GetComponentsInChildren<Renderer>().Where(r=>r.enabled&&r.gameObject.activeInHierarchy).Select(r=>r.bounds.center).ToArray();
 var centre=subject.Aggregate(Vector3.zero,(a,b)=>a+b)/subject.Length;
 // Explicitly supplementary camera composition; production deck camera,
 // terrain, life positions and HUD are not changed by this fixture.
 Cam.orthographicSize=ActiveSpot==4?16:3.5f;
 var depth=Cam.WorldToViewportPoint(centre).z;Cam.transform.position+=centre-Cam.ViewportToWorldPoint(new Vector3(.64f,.35f,depth));}
 }
 yield return new WaitForEndOfFrame();var frame=ScreenCapture.CaptureScreenshotAsTexture();string name="map"+(ActiveSpot+1)+"-"+stage+"-"+size.x+".png";
 File.WriteAllBytes(Path.Combine(directory,name),frame.EncodeToPNG());Destroy(frame);
 string row=name+" mode="+CurrentMode+" ground="+ActiveGroundId+" boat="+Sailor.Position+" supplementaryCamera="+detail;frames.Add(row);Debug.Log("[Catchline] GULL FRAME "+row);
 }
 }
}
}
}

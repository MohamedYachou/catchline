using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Catchline.Game;
namespace Catchline.EditorTools {
public static class GullCoastLifeChecks {
 static void Check(bool ok,string label) {if(!ok)throw new Exception("Gull coast life: "+label);}
 static void Scratch(){Check(Application.dataPath.Replace('\\','/').EndsWith("Catchline-sim/Assets",StringComparison.OrdinalIgnoreCase),"scratch only");}
 static object Call(object o,string name,params object[] args)=>o.GetType().GetMethod(name,System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic).Invoke(o,args);
 public static void Run(){
 Scratch();ArtImport.BuildLibrary();var rows=new List<string>();
 foreach(var (model,names) in new[]{("Cormorant",new[]{"Idle","DryWings","Dive"}),("Oystercatcher",new[]{"Walk","Probe"})}){
 var path="Assets/Art/Models/GullCoastLife/"+model+".fbx";
 var importer=(ModelImporter)AssetImporter.GetAtPath(path);Check(importer.animationType==ModelImporterAnimationType.Legacy&&importer.globalScale==1,model+" metre Legacy import");
 var clips=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview")).ToArray();
 foreach(string name in names)Check(clips.Any(c=>c.name.Contains(name)&&c.legacy&&c.length>0),model+" clip "+name);
 }
 EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
 var g=new GameObject("Gull coast check SessionOnly").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();
 try{for(int map=0;map<5;map++){
 g.State.Hull=5;g.State.Coins=100000;g.State.Fuel=g.State.FuelCapacity;Call(g,"RebuildBoat",false);g.Tick(.05f);Call(g,"SetupDeckGraph");
 if(!g.State.Known(map))Check(g.State.BuyChart(map),"chart "+map);
 g.SelectedSpot=map;g.SetSail();Until(()=>g.CurrentMode==VoyageGame.Mode.Fishing&&g.Leg==VoyageGame.TripLeg.None,"anchor");
 var life=UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None).FirstOrDefault(t=>t.name=="Gull coast life"&&t.gameObject.activeInHierarchy);Check(life!=null,"actual SeaV2 dispatch "+map);
 Check(life.GetComponentsInChildren<Collider>().Length==0,"noncolliding life "+map);Clearance(life,g.Navigation,rows);
 foreach(var r in life.GetComponentsInChildren<Renderer>())foreach(var mat in r.sharedMaterials)Check(mat!=null&&mat.shader.name=="Universal Render Pipeline/Lit","local URP binding "+r.name);
 if(map==2){var terrain=life.parent.gameObject;foreach(var r in life.GetComponentsInChildren<Renderer>())if(r.name.StartsWith("Forager_")&&r.enabled){float h=Surface(terrain,new Vector2(r.bounds.center.x,r.bounds.center.z));Check(Mathf.Abs(r.bounds.min.y-h)<.015f,"sand foot contact "+r.name);rows.Add("sand contact "+r.name+" error="+(r.bounds.min.y-h));}}
 if(map==4){var red=life.GetComponentsInChildren<Transform>().First(t=>t.name=="RedCan");var green=life.GetComponentsInChildren<Transform>().First(t=>t.name=="GreenCone");Check(red.parent==life&&green.parent==life&&Vector3.Distance(red.position,green.position)>22,"split marker pivots/full passage");Check(Mathf.Abs(red.position.y+.32f)<.001f,"marker waterline");}
 foreach(var bird in life.GetComponentsInChildren<GullCoastBird>()){
 Call(bird,"Start");var clips=bird.GetComponentInChildren<Animation>();
 Check(clips[bird.Cormorant?"Idle":"Probe"]!=null,"short animation names");
 if(bird.Cormorant)Check(clips["Dive"].wrapMode==WrapMode.Once,"Dive never loops");
 }
 var rod=g.Rods.FirstOrDefault(g.CanCommandRod);Check(rod!=null,"captain rod "+map);g.CommandRod(rod);Until(()=>rod.InWater,"cast");g.EndCaptainFishing(rod);
 g.HeadHome();Until(()=>g.CurrentMode==VoyageGame.Mode.Harbour,"home");rows.Add("map"+(map+1)+" actual sea dressing/out/anchor/cast/home PASS");
 void Until(Func<bool> done,string stage){for(int n=0;n<24000&&!done();n++)g.Tick(.025f);Check(done(),stage+" map"+map+" captain="+g.Captain.Tile+" walking="+g.Captain.Walking+" idle="+g.Captain.Idle+" rod="+(g.Manning==null?"none":g.Manning.State.ToString())+" bait="+g.State.Bait);}
 }}finally{UnityEngine.Object.DestroyImmediate(g.gameObject);}
 File.WriteAllLines("Logs/gull-coast-focused.txt",rows);Debug.Log("[Catchline] GULL COAST FOCUSED PASS. Snapshot written to Logs/gull-coast-focused.txt");
 }
 static void Clearance(Transform life,Catchline.Game.Sea.SeaNav actual,List<string> rows){
 var props=life.Cast<Transform>().Where(t=>t.GetComponentsInChildren<Renderer>().Any(r=>r.enabled&&r.gameObject.activeInHierarchy)).ToArray();
 foreach(var hull in GameData.Hulls){
 var nav=Catchline.Game.Sea.SeaNav.Load(actual.Map,hull);nav.SetHarbour(actual.Harbour);
 var ends=nav.Grounds.Select(g=>g.Centre).Prepend(nav.Harbour).ToArray();float min=float.PositiveInfinity;
 foreach(var prop in props){var renderers=prop.GetComponentsInChildren<Renderer>().Where(r=>r.enabled&&r.gameObject.activeInHierarchy).ToArray();var box=renderers[0].bounds;foreach(var r in renderers.Skip(1))box.Encapsulate(r.bounds);
 var p=new Vector2(box.center.x,box.center.z);float radius=new Vector2(box.extents.x,box.extents.z).magnitude;
 for(int a=0;a<ends.Length;a++)for(int b=0;b<ends.Length;b++)if(a!=b){var route=nav.Plan(ends[a],ends[b]);Check(route!=null,"life clearance route");for(int i=1;i<route.Count;i++){var d=route[i]-route[i-1];float u=Mathf.Clamp01(Vector2.Dot(p-route[i-1],d)/d.sqrMagnitude);min=Mathf.Min(min,Vector2.Distance(p,route[i-1]+u*d)-radius-hull.NavigationRadius);}}
 }
 rows.Add(actual.Map+"/"+hull.Model+" minimum prop-envelope/nav-radius clearance="+min.ToString("F3")+"m");File.WriteAllLines("Logs/gull-coast-clearance-progress.txt",rows);Check(min>0,"life outside all centre routes "+actual.Map+"/"+hull.Model+" "+min);
 }
 }
 public static void RegressionBuild(){
 Run();JigBoatChecks.Regression();
 Time.timeScale=1;var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);var g=new GameObject("Gull coast native SessionOnly").AddComponent<VoyageGame>();g.SessionOnly=true;
 const string fixture="Assets/GullCoastAcceptance.unity";EditorSceneManager.SaveScene(scene,fixture);Directory.CreateDirectory("Builds/GullCoastCapture");
 var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{fixture},locationPathName="Builds/GullCoastCapture/Catchline.exe",target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
 Check(result.summary.result==UnityEditor.Build.Reporting.BuildResult.Succeeded,"native build");File.WriteAllText("Logs/gull-coast-build-result.txt",result.summary.result+" bytes="+result.summary.totalSize+" errors="+result.summary.totalErrors);Debug.Log("[Catchline] Snapshot written to Builds/GullCoastCapture/Catchline.exe");
 }
 static float Surface(GameObject map, Vector2 p) {
 float height=-999;
 foreach(var mf in map.GetComponentsInChildren<MeshFilter>())if(mf.name.Contains("Terrain_long-sandbar")){
 var v=mf.sharedMesh.vertices;var tri=mf.sharedMesh.triangles;
 for(int i=0;i<tri.Length;i+=3){var a=mf.transform.TransformPoint(v[tri[i]]);var b=mf.transform.TransformPoint(v[tri[i+1]]);var c=mf.transform.TransformPoint(v[tri[i+2]]);float det=(b.z-c.z)*(a.x-c.x)+(c.x-b.x)*(a.z-c.z);if(Mathf.Abs(det)<.00001f)continue;float u=((b.z-c.z)*(p.x-c.x)+(c.x-b.x)*(p.y-c.z))/det;float w=((c.z-a.z)*(p.x-c.x)+(a.x-c.x)*(p.y-c.z))/det;if(u>=0&&w>=0&&u+w<=1)height=Mathf.Max(height,u*a.y+w*b.y+(1-u-w)*c.y);}}
 return height;
 }
 public static void FitSand(){
 Scratch();ArtImport.BuildLibrary();var lib=ArtLibrary.Get();var map=UnityEngine.Object.Instantiate(lib.M("GullSandbarSeaV2"));
 var group=ArtLibrary.Spawn(lib.M("OystercatcherGroup"),map.transform,new Vector3(-14,0,5),Quaternion.Euler(0,90,0));var rows=new List<string>();
 foreach(var r in group.GetComponentsInChildren<Renderer>())if(r.name.StartsWith("Forager_")){
 var b=r.bounds;var p=new Vector2(b.center.x,b.center.z);float y=Surface(map,p);rows.Add(r.name+" footXZ="+p+" terrainY="+y+" offsetY="+(y-b.min.y+.003f));}
 File.WriteAllLines("Logs/gull-sand-fit.txt",rows);UnityEngine.Object.DestroyImmediate(map);Debug.Log("[Catchline] Snapshot written to Logs/gull-sand-fit.txt");
 }
 public static void Measure(){
 Scratch();ArtImport.BuildLibrary();var rows=new List<string>();
 foreach(string name in new[]{"Cormorant","CormorantRock","Oystercatcher","OystercatcherGroup","ChannelMarkers","PotBuoyLine"}){
 var prefab=ArtLibrary.Get().M(name);Check(prefab!=null,name+" imported");var go=UnityEngine.Object.Instantiate(prefab);
 foreach(var r in go.GetComponentsInChildren<Renderer>())rows.Add(name+" BOUNDS "+r.name+" "+r.bounds.min.ToString("F4")+" "+r.bounds.max.ToString("F4")+" materials="+string.Join(",",r.sharedMaterials.Select(m=>m.name+":"+ColorUtility.ToHtmlStringRGB(m.color))));
 foreach(var a in go.GetComponentsInChildren<Animation>())foreach(AnimationState c in a)rows.Add(name+" CLIP "+c.name+" "+c.length+" legacy="+c.clip.legacy);
 UnityEngine.Object.DestroyImmediate(go);}
 foreach(string name in new[]{"GullHarbourMouth","GullKelpBank","GullSandbar","GullRockyPoint","GullDeepChannel"}){
 var go=UnityEngine.Object.Instantiate(ArtLibrary.Get().M(name+"SeaV2"));
 foreach(var r in go.GetComponentsInChildren<Renderer>())if(r.name.Contains("Terrain")||r.name.Contains("Kelp"))rows.Add(name+" TERRAIN "+r.name+" "+r.bounds.min.ToString("F2")+" "+r.bounds.max.ToString("F2"));
 if(name=="GullSandbar")foreach(var mf in go.GetComponentsInChildren<MeshFilter>())if(mf.name.Contains("Terrain_long-sandbar")){
 var mesh=mf.sharedMesh;var v=mesh.vertices;var tri=mesh.triangles;
 foreach(float x in new[]{-14f,-13f,-12f,12f,13f,14f}){float height=-999;
 var p=new Vector2(x,5);for(int i=0;i<tri.Length;i+=3){var a=mf.transform.TransformPoint(v[tri[i]]);var b=mf.transform.TransformPoint(v[tri[i+1]]);var c=mf.transform.TransformPoint(v[tri[i+2]]);float det=(b.z-c.z)*(a.x-c.x)+(c.x-b.x)*(a.z-c.z);if(Mathf.Abs(det)<.00001f)continue;float u=((b.z-c.z)*(p.x-c.x)+(c.x-b.x)*(p.y-c.z))/det;float w=((c.z-a.z)*(p.x-c.x)+(a.x-c.x)*(p.y-c.z))/det;if(u>=0&&w>=0&&u+w<=1)height=Mathf.Max(height,u*a.y+w*b.y+(1-u-w)*c.y);}
 rows.Add("SANDBAR surface x="+x+" z=5 height="+height);}}
 UnityEngine.Object.DestroyImmediate(go);}
 Directory.CreateDirectory("Logs");File.WriteAllLines("Logs/gull-coast-native-measure.txt",rows);Debug.Log("[Catchline] Snapshot written to Logs/gull-coast-native-measure.txt");
 }
}
}

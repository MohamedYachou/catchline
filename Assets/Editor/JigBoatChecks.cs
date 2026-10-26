using System; using System.IO; using System.Linq; using UnityEngine; using System.Collections.Generic; using System.Reflection; using UnityEditor.SceneManagement; using UnityEditor; using Catchline.Game; using Catchline.Prototype;
namespace Catchline.EditorTools { public static class JigBoatChecks {
public static void Measure() {
 ArtImport.BuildLibrary(); var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Art/Models/Boats/JigBoatV1/JigBoatV1.fbx");
 var go=UnityEngine.Object.Instantiate(prefab);go.transform.rotation=Quaternion.Euler(0,-90,0)*prefab.transform.localRotation;go.transform.localScale=prefab.transform.localScale;
 var rows=go.GetComponentsInChildren<Transform>().Select(t=>t.name+" "+t.position.ToString("F4")).ToList();
 foreach(var r in go.GetComponentsInChildren<Renderer>())rows.Add("BOUNDS "+r.name+" "+r.bounds.min.ToString("F4")+" "+r.bounds.max.ToString("F4"));
 File.WriteAllLines("Logs/jig-native-measure.txt",rows);UnityEngine.Object.DestroyImmediate(go); Debug.Log("[Catchline] Snapshot written to Logs/jig-native-measure.txt");
}

static void Check(bool ok,string label) {if(!ok)throw new Exception("JIG check: "+label);}
static object Call(object obj,string method,params object[] args)=>obj.GetType().GetMethod(method,BindingFlags.Instance|BindingFlags.NonPublic).Invoke(obj,args);
static void Scratch() { Check(Application.dataPath.Replace('\\','/').EndsWith("Catchline-sim/Assets",StringComparison.OrdinalIgnoreCase),"scratch only"); }
public static void Run() {
 Scratch(); ArtImport.BuildLibrary(); var rows=new List<string>();
 int[] tiers={0,1,2,4,5,3};
 Check(GameData.Hulls.Length==6,"six saved hulls");
 for(int id=0;id<6;id++) { var s=new GameState(91){Hull=id};Check(GameData.HullTier(id)==tiers[id]&&s.Tier==tiers[id]&&s.CardTier==tiers[id],"tier ID"+id); }
 var state=new GameState(92){Hull=2,Coins=6499};Check(!state.RefitJig()&&state.Hull==2,"unaffordable Jig atomic");
 state.Coins=6500;Check(!state.RefitPrep()&&state.RefitJig()&&state.Hull==5&&state.Coins==0&&state.Fuel==state.FuelCapacity,"Compact to Jig6500 no kg gate");
 state.Coins=9500;state.BestVoyageKg=99;Check(!state.RefitPrep(),"Prep haul gate");state.BestVoyageKg=100;state.Coins=9499;Check(!state.RefitPrep(),"Prep price gate");state.Coins=9500;Check(state.RefitPrep()&&state.Hull==3&&state.Coins==0,"Jig to Prep9500");
 state.Coins=18000;Check(state.RefitTier5()&&state.Hull==4&&state.Coins==0,"Prep to Buoy18000");
 foreach(int id in new[]{3,4}) { string path=Path.GetFullPath("Logs/jig-old-save-"+id+".json");var old=new GameState(93){Hull=id,Coins=731};old.Save(path);var loaded=GameState.Load(path);Check(loaded!=null&&loaded.Hull==id&&loaded.Coins==731&&loaded.Tier==tiers[id],"old save identity "+id); }
 Check(!Coasts.Open(5,5)&&Coasts.Open(5,3),"Jig below Outer gate, old Prep above");rows.Add("tier mapping, affordability, refit sequence, old Prep/Buoy save IDs, coast gates PASS");
 EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
 var g=new GameObject("Jig session check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.State.Hull=5;g.State.Coins=100000;g.State.Fuel=g.State.FuelCapacity;Call(g,"RebuildBoat",false);g.Tick(.05f);
 try {
 Call(g,"SetupDeckGraph");
 Check(g.IsJigBoat&&!g.IsPrepFisher&&g.UsesDeckGraph,"Jig model/net graph, no prep");
 var jigMeshes=AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Models/Boats/JigBoatV1/JigBoatV1.fbx").OfType<Mesh>().ToArray();Check(jigMeshes.Length>0&&jigMeshes.All(m=>m.isReadable),"native raster meshes readable in player");
 Check(g.State.HullDef.Capacity==130&&g.State.HullDef.CrewCap==5&&g.Rods.Count==3,"130kg/five berths/three rods");
 Check(!g.State.SecondNetActive,"single net");
 Check(typeof(VoyageGame).GetField("jigBulb",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(g)!=null,"bulb emissive material bound");Check(typeof(VoyageGame).GetField("jigGlow",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(g)!=null,"glow imported and instantiated");
 var hatch=g.Boat.GetComponentsInChildren<Transform>().FirstOrDefault(t=>t.name=="HoldHatchLid"&&t.GetComponent<MeshFilter>()==null);Check(hatch!=null&&hatch.GetComponentsInChildren<MeshFilter>().Any(m=>m.name=="Jig hatch panel"),"runtime hatch edge hinge");
 var nodes=g.DeckGraph.Stations.Select(s=>s.WorkTile).Concat(g.State.HullDef.CrewRest).Append(g.State.HullDef.Seat).Append(g.State.HullDef.HoldAccess).Append(g.State.HullDef.NetAccess).Distinct().ToArray();
 File.WriteAllLines("Logs/jig-grid.txt",Enumerable.Range(0,g.Grid.Height).Reverse().Select(y=>string.Concat(Enumerable.Range(0,g.Grid.Width).Select(x=>g.Grid.IsBlocked(new Vector2Int(x,y))?'#':'.'))));
 Debug.Log("JIG SOCKET STATUS "+string.Join(";",nodes.Select(t=>t+" blocked="+g.Grid.IsBlocked(t))));
 foreach(var t in nodes)Check(!g.Grid.IsBlocked(t),"socket blocked "+t);
 foreach(var a in nodes)foreach(var b in nodes)Check(g.Grid.FindPath(a,b)!=null,"socket path "+a+"->"+b);
 
 g.SetHarbourEvening(false,true);g.State.NightVoyage=false;Call(g,"UpdateJigLamps");Check(!g.JigLampsLit,"harbour day lamps off");g.State.NightVoyage=true;Call(g,"UpdateJigLamps");Check(g.JigLampsLit,"night lamps on");g.State.NightVoyage=false;
 Check(g.State.BuyChart(4),"Deep channel chart");g.SelectedSpot=4;var legs=new HashSet<VoyageGame.TripLeg>();
 void Until(Func<bool> done,string stage) {for(int n=0;n<16000&&!done();n++){g.Tick(.025f);legs.Add(g.Leg);}Check(done(),stage);}
 g.SetSail();Until(()=>g.CurrentMode==VoyageGame.Mode.Fishing&&g.Leg==VoyageGame.TripLeg.None,"Deep channel anchor");Call(g,"UpdateJigLamps");Check(g.AtFishingGround&&g.JigLampsLit,"anchored day lamps on");
 var rod=g.Rods.FirstOrDefault(g.CanCommandRod);Check(rod!=null,"captain rod available");g.CommandRod(rod);Until(()=>rod.InWater,"captain bait/cast");g.State.NightVoyage=true;for(int n=0;n<160;n++)g.Tick(.025f);Check((float)typeof(VoyageGame).GetField("duskBlend",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(g)>.99f&&g.JigLampsLit,"real sea night lighting and lamps");g.State.NightVoyage=false;g.HeadHome();Until(()=>g.CurrentMode==VoyageGame.Mode.Harbour,"Jig returns home");
 foreach(var leg in new[]{VoyageGame.TripLeg.HarbourOut,VoyageGame.TripLeg.ChartOut,VoyageGame.TripLeg.SeaOut,VoyageGame.TripLeg.SeaHome,VoyageGame.TripLeg.ChartHome,VoyageGame.TripLeg.HarbourIn})Check(legs.Contains(leg),"trip leg "+leg);
 rows.Add("native raster sockets all-pairs connected; three rods/one net/no prep; day/night/anchor lamps; Jig Deep channel bait/cast/home PASS");
 }finally{UnityEngine.Object.DestroyImmediate(g.gameObject);}
 File.WriteAllLines("Logs/jig-focused.txt",rows);Debug.Log("[Catchline] JIG FOCUSED PASS. Snapshot written to Logs/jig-focused.txt");
}
public static void Regression() {
 Scratch(); CrewCardsAbilityChecks.Regression();MapNavChecks.Run();string harbour=HarbourTripChecks.Run();
 var trip=typeof(HarbourTripChecks).GetMethod("Trip",BindingFlags.Static|BindingFlags.NonPublic);string jig=(string)trip.Invoke(null,new object[]{5,4});
 File.WriteAllText("Logs/jig-regression.txt",MapNavChecks.Report+"\n"+harbour+"\n"+jig);Debug.Log("[Catchline] JIG REGRESSION PASS. Snapshot written to Logs/jig-regression.txt");
}

public static void BuildNative() {
 Run();Time.timeScale=1;
 var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);var g=new GameObject("Jig native SessionOnly").AddComponent<VoyageGame>();g.SessionOnly=true;
 const string fixture="Assets/JigAcceptance.unity";EditorSceneManager.SaveScene(scene,fixture);Directory.CreateDirectory("Builds/JigCapture");
 var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{fixture},locationPathName="Builds/JigCapture/Catchline.exe",target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
 Check(result.summary.result==UnityEditor.Build.Reporting.BuildResult.Succeeded,"native build");File.WriteAllText("Logs/jig-build-result.txt",result.summary.result+" bytes="+result.summary.totalSize+" errors="+result.summary.totalErrors);Debug.Log("[Catchline] Snapshot written to Builds/JigCapture/Catchline.exe");
}
} }

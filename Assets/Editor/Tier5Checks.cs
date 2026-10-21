using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
namespace Catchline.EditorTools
{
    public static class Tier5Checks
    {
        const BindingFlags H=BindingFlags.Instance|BindingFlags.NonPublic;
        static void Check(bool ok,string why){if(!ok)throw new Exception("TIER071: "+why);}
        static object Call(VoyageGame g,string n,params object[] args)=>typeof(VoyageGame).GetMethod(n,H).Invoke(g,args);
        static void Work(Person p){for(int i=0;i<2500&&!p.Idle;i++)p.Tick(.025f,1,Quaternion.identity);}
        static void Deck(VoyageGame g,string variant)
        {
            var h=g.State.HullDef;
            var transform=g.Boat.GetComponentsInChildren<Transform>(true).Single(t=>t.name=="Hull");
            var mesh=transform.GetComponent<MeshFilter>().sharedMesh;
            var v=mesh.vertices.Select(p=>g.Boat.InverseTransformPoint(transform.TransformPoint(p))).ToArray();
            Check(mesh.isReadable,"runtime routing mesh readable");
            Check(Mathf.Abs(v.Max(p=>p.x)-v.Min(p=>p.x)-8.5f)<.01f&&Mathf.Abs(v.Max(p=>p.z)-v.Min(p=>p.z)-4.2f)<.01f,"upright8.5x4.2m exacthull");
            var jobs=new[]{h.Seat,h.HoldAccess,(Vector2Int)typeof(VoyageGame).GetProperty("NetAccess",H).GetValue(g),(Vector2Int)typeof(VoyageGame).GetProperty("SecondNetAccess",H).GetValue(g)}.Concat(h.CrewRest).Concat(h.RodTiles).Concat(g.PrepWorkerTiles).Concat(g.BuoyWorkerTiles).Distinct().ToArray();
            File.WriteAllLines("Logs/tier071/deck-"+variant+".txt",Enumerable.Range(0,g.Grid.Height).Reverse().Select(y=>string.Concat(Enumerable.Range(0,g.Grid.Width).Select(x=>jobs.Contains(new Vector2Int(x,y))?(g.Grid.IsBlocked(new Vector2Int(x,y))?'X':'J'):g.Grid.IsBlocked(new Vector2Int(x,y))?'#':'.'))));
            foreach(var a in jobs)
            {
                Debug.Log("[Catchline] TIER071 "+variant+" job "+a+" blocked="+g.Grid.IsBlocked(a));
                Check(!g.Grid.IsBlocked(a),"jobclear "+variant+" "+a);
                foreach(var b in jobs)Check(g.Grid.FindPath(a,b)!=null,"connected "+a+" -> "+b);
            }
            for(int i=0;i<4;i++)
            {
                var socket=g.Boat.GetComponentsInChildren<Transform>(true).Single(t=>t.name=="RodSocket_"+(i+1));
                var actual=g.Boat.InverseTransformPoint(socket.position);
                Debug.Log("[Catchline] TIER071 socket "+i+" "+actual);
                Check(Vector3.Distance(actual,h.RodBases[i])<.01f,"rod mount exact"+i);
            }
            Check(!g.Boat.GetComponentsInChildren<Transform>(true).Any(t=>t.name.StartsWith("T5 ")||t.name.Contains("Studio")),"no reviewstatues/studio exported");
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/tier071");ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("TIER071 isolated check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();
            Check(g.StartTier5Trial(),"startsaveisolatedtrial");
            Check(g.IsTier5&&g.State.CrewCount==6&&g.ExtraPeople.Count+(g.Hand!=null?1:0)==6,"sixactualworkerspluscaptain");
            Check(g.Rods.Count==4&&!g.SecondNetActive&&g.State.CoolerCapacity==240,"rodheavyconfiguration");
            Deck(g,"rods");
            g.PrepareInterface(844,390);Check(g.InvokeInterface("tier5/operations"),"actualoperationsbutton");
            g.PrepareInterface(844,390);Check(g.InvokeInterface("tier5/processing"),"actualprocessingordersbutton");
            g.PrepareInterface(844,390);bool oldOrder=g.State.PrepOrders.PrepareHighestValue;
            Check(g.InvokeInterface("prep/sort")&&g.State.PrepOrders.PrepareHighestValue!=oldOrder,"actualprocessingprioritytoggle");
            Check(g.InvokeInterface("prep/close"),"closeprocessing");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("tier5/operations"),"reopenoperations");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("tier5/crew/duties"),"actualcrewdutiesbutton");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("management/close"),"closeactualduties");

            for(int i=0;i<3600;i++)
            {
                g.Tick(.05f);
                foreach(var p in new[]{g.Captain,g.Hand}.Concat(g.ExtraPeople).Where(p=>p!=null))Check(!g.Grid.IsBlocked(p.Tile),"actualworkeroncleartile "+p.Name+" "+p.Tile);
            }
            Debug.Log($"[Catchline] TIER071180s rods landed={g.Stats.Landed} hold={g.HoldKg} buoyhauls={g.BuoyHauls} maintenance={g.MaintenanceJobs} prepared={g.Cooler.Count(f=>f.Prepared)}");
            Check(g.Stats.Landed>5&&g.Cooler.Count>0,"actualrod/netcatchandstorage");
            Check(g.BuoyHauls>0&&g.Flow.Sum(FlowTelemetry.Kind.Trap,180)>0,"actualbuoycatchlandedandrecorded; storage identity verified through isolated full pipeline");
            Check(g.MaintenanceJobs==0,"manual gear requires no maintenance worker");
            Check(g.Cooler.Any(f=>f.Prepared&&f.PreparedBonus==1.5f),"processorproduces150percentcatch");
            Check(g.State.PrepOrders.ChumTarget==10,"Tier5 uses existing station chum orders");
            var raw=new CaughtFish{Species=Species.Cod,Kg=4,StowedAt=g.SimTime};var processed=new CaughtFish{Species=Species.Cod,Kg=4,StowedAt=g.SimTime,Prepared=true,PreparedBonus=1.5f,PreparedQuality=1};
            Check(Mathf.Abs(g.State.ValueOf(processed,g.SimTime)-g.State.ValueOf(raw,g.SimTime)*1.5f)<=1,"150percentvaluewithrounding");
            g.State.Tier5Condition[0]=10;g.State.Tier5Broken[0]=true;
            Check(g.EquipmentEfficiency(0)==1&&!g.Tier5EquipmentFailure(0)&&!g.CaptainService(),"legacy manual wear has no effect");
            g.State.Save("Logs/tier071/save.json");var loaded=GameState.Load("Logs/tier071/save.json");
            Check(loaded.Hull==4&&loaded.CrewCount==6&&!loaded.Crew.Any(c=>c.Role==CrewRole.Engineer),"six active fisher/deckhand save roundtrip");
            var old=new GameState(9){Hull=3,Coins=GameState.Tier5Cost};Check(old.RefitTier5()&&old.Coins==0&&old.Hull==4&&old.SecondNetOwned,"realprogressionexactcharge");Check(!old.RefitTier5(),"notchargedtwice");
            g.HeadHome();for(int n=0;n<2000&&g.CurrentMode!=VoyageGame.Mode.Harbour;n++)g.Tick(.05f);Check(g.CurrentMode==VoyageGame.Mode.Harbour,"actualreturnbeforerefit");
            Call(g,"ResetNet");Check(g.ConfigureTier5NetTeam(),"netheavyteamrefit");
            Check(g.Rods.Count==2&&g.SecondNetActive&&g.State.Crew.Count(c=>c.Role==CrewRole.Fisherman)==3,"tworods/twonets/twofishers");
            Deck(g,"nets");g.Showcase(0,0);bool secondWorked=false,firstWorked=false;
            for(int i=0;i<3000;i++){g.Tick(.05f);firstWorked|=g.Net!=VoyageGame.NetState.Stowed;secondWorked|=g.SecondNet!=VoyageGame.NetState.Stowed;}
            Check(firstWorked&&secondWorked,"bothrealnetjobsoperate");
            g.HeadHome();for(int n=0;n<2000&&g.CurrentMode!=VoyageGame.Mode.Harbour;n++)g.Tick(.05f);
            Call(g,"ResetNet");Check(g.ToggleSecondNetModule()&&g.Rods.Count==4,"switchrestores4rods");
            g.PrepareInterface(844,390);Check(!g.State.Board.Any(c=>c.Role==CrewRole.Engineer),"engineers reserved for later tier");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Check(GameData.Hulls[0].Model=="Rowboat"&&GameData.Hulls[1].Model=="Skiff"&&GameData.Hulls[2].Model=="CompactFisherV1"&&GameData.Hulls[3].Model=="PrepFisherV1","oldhullIDsunchanged");
            Debug.Log("[Catchline] TIER071 CHECKS PASSED");Debug.Log("[Catchline] Snapshot written to Logs/tier071");
        }
        public static void ValidateAndBuild()
        {
            Run();SecondNetModuleChecks.Run();Balance045Checks.Run();PtsWaterChecks.Run();BuildPreview();
        }
        public static void FinalValidateAndBuild() { Run(); BuildPreview(); }
        public static void BuildPreview()
        {
            PtsWaterChecks.Run();
            foreach(bool test in new[]{true,false})
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
                var game=new GameObject(test?"Tier5 isolated preview":"Persistent Catchline").AddComponent<VoyageGame>();game.SessionOnly=test;
                string scene="Assets/Scenes/Tier071"+(test?"Test":"Real")+".unity";EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(),scene);
                string output=Path.GetFullPath("Builds/Tier071/"+(test?"Test":"Real")+"/Catchline.exe");
                var r=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{scene},locationPathName=output,target=BuildTarget.StandaloneWindows64});
                Check(r.summary.result==BuildResult.Succeeded,"standalonebuild"+r.summary.result);
                Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: "+output);
            }
            Debug.Log("[Catchline] Snapshot written to Logs/tier071");
        }
    }
}

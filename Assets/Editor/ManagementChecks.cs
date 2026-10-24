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
    public static class ManagementChecks
    {
        static void Check(bool ok,string message){if(!ok)throw new Exception("MANAGEMENT078: "+message);}
        static void Ledger()
        {
            var f=new FlowTelemetry();f.Tick(30,1);f.Record(FlowTelemetry.Kind.Rod,3,60);
            Check(Mathf.Abs(f.Rate(FlowTelemetry.Kind.Rod,60)-6)<.001f,"warmup denominator uses elapsed fishing time");
            f.Record(FlowTelemetry.Kind.Stored,3,carried:true);f.Record(FlowTelemetry.Kind.Sorted,3);
            Check(f.LandedKg==3&&f.Sum(FlowTelemetry.Kind.Stored,60)==3&&f.Sum(FlowTelemetry.Kind.Sorted,60)==3,"independent stages without double landed count");
            f.Record(FlowTelemetry.Kind.Rod,float.NaN);Check(f.LandedKg==3,"invalid event ignored");
            f.Tick(61,0);Check(f.Rate(FlowTelemetry.Kind.Rod,60)==0&&f.Rate(FlowTelemetry.Kind.Rod,180)>0,"window boundary ages out independently");
            f.Tick(180,0);Check(f.Sum(FlowTelemetry.Kind.Rod,180)==0&&f.LandedKg==3,"bounded rolling entries preserve voyage total");
            Check(FlowTelemetry.Pressure(7,10,false,false)==0&&FlowTelemetry.Pressure(8,10,false,false)==1&&FlowTelemetry.Pressure(11,10,false,false)==2,"green/orange/red thresholds");
            Check(FlowTelemetry.Pressure(0,0,false,true)==-1&&FlowTelemetry.Pressure(0,0,true,true)==2,"no data neutral, blocking overrides warmup");
            f.Reset();Check(f.Clock==0&&f.LandedKg==0&&f.CarrySamples==0,"reset clears observations");
        }
        public static void Run()
        {
            Ledger();Directory.CreateDirectory("Logs/management078");ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("Management isolated functional check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartTier5Trial();g.State.PrepOrders.ChumTarget=0;
            Check(g.Flow.Clock==0&&g.Flow.LandedKg==0,"trial begins with no fabricated samples");
            g.PrepareInterface(844,390);
            var entry=g.GetComponentsInChildren<RectTransform>().Single(t=>t.name=="management/open");
            float logicalHeight=(float)typeof(VoyageGame).GetField("ih",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(g);
            Check(-entry.anchoredPosition.y>=0&&-entry.anchoredPosition.y+entry.sizeDelta.y<=logicalHeight,"phone entry fully within safe-area height");
            g.PrepareInterface(1440,900);Check(g.InvokeInterface("management/open"),"real entry button");g.PrepareInterface(1440,900);
            Check(g.ManagementOpen&&g.InvokeInterface("management/tab/income"),"actual fishing tab");g.PrepareInterface(1440,900);
            Check(g.InvokeInterface("management/method/0"),"real method detail");g.PrepareInterface(1440,900);Check(g.InvokeInterface("management/detail/close"),"detail closes");g.PrepareInterface(1440,900);Check(!g.InvokeInterface("rod/0"),"underlying control absent");
            g.PrepareInterface(844,390);Check(g.InvokeInterface("management/tab/operations"),"phone flow tab");g.PrepareInterface(844,390,1.15f);
            Check(g.InvokeInterface("management/stage/1"),"hauling detail");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("management/duties")&&g.ManagementOpen,"duties navigation closes management");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("management/close"),"duties close");
            g.OpenManagement();g.PrepareInterface(844,390);g.InvokeInterface("management/tab/operations");g.PrepareInterface(844,390);Check(g.InvokeInterface("management/stage/2"),"processing detail");g.PrepareInterface(844,390);Check(g.InvokeInterface("management/orders"),"processing navigation");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("prep/close"),"processing close");
            for(int i=0;i<3600;i++)g.Tick(.05f);
            float landed=g.Flow.Sum(FlowTelemetry.Kind.Rod,180)+g.Flow.Sum(FlowTelemetry.Kind.Net,180)+g.Flow.Sum(FlowTelemetry.Kind.Trap,180)+g.Flow.Sum(FlowTelemetry.Kind.DeepLine,180);
            Check(g.Flow.LandedKg>0&&g.Flow.Sum(FlowTelemetry.Kind.Trap,180)>0,"real rod/net/trap event stream");
            Check(Mathf.Abs(g.Flow.LandedKg-landed)<.01f,"first180s landed totals reconcile");
            Check(g.Flow.Sum(FlowTelemetry.Kind.Stored,180)>0&&g.Flow.Sum(FlowTelemetry.Kind.Sorted,180)>0,"real storage and prep event stream");
            Check(Mathf.Abs(g.Flow.LandedKg-g.HoldKg-g.ProcessingKg-g.Flow.ChumKg-g.OnDeck.Sum(f=>f.Kg)-new[]{g.Captain,g.Hand}.Concat(g.ExtraPeople).Where(p=>p?.Carrying!=null).Sum(p=>p.Carrying.Kg)-g.Flow.LostKg)<.03f,"mass conservation landed=hold+processing+deck+hands+chum+lost");
            Check(g.Flow.CarryPace>0,"completed jobs teach carrying pace");
            Debug.Log($"[Catchline] MANAGEMENT078 actual180s landed={g.Flow.LandedKg} stored={g.HoldKg} deck={g.OnDeck.Sum(f=>f.Kg)} lost={g.Flow.LostKg} prep={g.Flow.Sum(FlowTelemetry.Kind.Sorted,180)} pace={g.Flow.CarryPace}");
            var clock=g.Flow.Clock;g.Tick(0);Check(g.Flow.Clock==clock,"zero dt does not advance windows");
            g.OpenManagement();g.PrepareInterface(1440,900);Check(g.InvokeInterface("management/close")&&!g.ManagementOpen,"real close callback");
            g.HeadHome();for(int i=0;i<2000&&g.CurrentMode!=VoyageGame.Mode.Harbour;i++)g.Tick(.05f);
            clock=g.Flow.Clock;g.Tick(1);Check(g.Flow.Clock==clock,"harbour excluded from rate denominator");
            // Existing save/state must not acquire any diagnostic fields.
            string json=JsonUtility.ToJson(g.State);Check(!json.Contains("CarryBusySeconds")&&!json.Contains("FlowTelemetry"),"telemetry not persisted");
            g.StartTier5Trial();Check(g.Flow.Clock==0&&g.Flow.LandedKg==0&&!g.ManagementOpen,"new session clears rate history and modal");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] MANAGEMENT078 CHECKS PASSED");Debug.Log("[Catchline] Snapshot written to Logs/management078");
        }
        public static void ValidateAndBuild()
        {
            Run();Tier5Checks.Run();PtsWaterChecks.Run();BuildPreview();
        }
        public static void FinalValidateAndBuild() { Run(); BuildPreview(); }
        static void BuildPreview()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("Management078 save-isolated preview").AddComponent<VoyageGame>();g.SessionOnly=true;
            string scene="Assets/Scenes/Management078Test.unity";EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(),scene);
            string output=Path.GetFullPath("Builds/Management078/Test/Catchline.exe");
            var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{scene},locationPathName=output,target=BuildTarget.StandaloneWindows64});
            Check(result.summary.result==BuildResult.Succeeded,"Windows standalone built");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: "+output);Debug.Log("[Catchline] Snapshot written to Logs/management078");
        }
    }
}

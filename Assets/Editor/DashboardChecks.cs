using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
namespace Catchline.EditorTools
{
    public static class DashboardChecks
    {
        static void Check(bool ok,string why){if(!ok)throw new Exception("DASH082: "+why);}
        static void Work(Person p){for(int n=0;n<5000&&!p.Idle;n++)p.Tick(.025f,1,Quaternion.identity);Check(p.Idle,"job can reach completion");}
        static void Pipeline()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("DASH082 pipeline check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartPrepBoatTrial();
            g.State.PrepOrders.ChumTarget=0;foreach(var p in new[]{g.Captain,g.Hand}.Concat(g.ExtraPeople).Where(p=>p!=null))p.Stop();
            var processor=new[]{g.Hand}.Concat(g.ExtraPeople).First(p=>p?.Contract?.Role==CrewRole.Deckhand&&p.Contract.WorkPreference==DeckhandWork.Prep);
            var carrier=new[]{g.Hand}.Concat(g.ExtraPeople).First(p=>p?.Contract?.Role==CrewRole.Deckhand&&p!=processor);
            var f=new CaughtFish{Species=Species.Cod,Kg=4,StowedAt=g.SimTime};
            Check(g.DeliverCatch(f)&&g.ProcessingInput.Contains(f)&&!g.Cooler.Contains(f),"raw catch reaches input, not hold");
            Check(!g.DeliverCatch(f),"duplicate arrival rejected");
            Check(g.TryPrepWork(processor),"processor claims input");processor.Stop();
            Check(g.ProcessingInput.Contains(f)&&!f.Prepared&&g.PrepWorkersActive==0,"cancel processing conserves raw input");
            Check(g.TryPrepWork(processor),"processing can restart");Work(processor);
            Check(f.Prepared&&g.ProcessingOutput.Contains(f)&&!g.ProcessingInput.Contains(f)&&g.HoldKg==0,"processed fish waits separately outside main hold");
            Check(g.TryCarryProcessed(carrier),"real outbound hauling job starts");carrier.Stop();
            Check(g.ProcessingOutput.Contains(f)&&g.HoldKg==0,"cancel hauling leaves output safe");
            Check(g.TryCarryProcessed(carrier),"outbound can restart");Work(carrier);
            Check(g.Cooler.Contains(f)&&!g.ProcessingOutput.Contains(f)&&g.HoldKg==4,"separate completed carry stores exact same prepared fish");
            Check(!g.TryStore(f),"duplicate hold insertion rejected");
            var raw=new CaughtFish{Species=Species.Cod,Kg=3,StowedAt=g.SimTime};g.DeliverCatch(raw);g.HeadHome();
            Check(g.ProcessingKg==0&&g.Cooler.Contains(raw)&&g.Cooler.Contains(f),"return salvages input and prepared cargo without inventing preparation");
            for(int n=0;n<2000&&g.CurrentMode!=VoyageGame.Mode.Harbour;n++)g.Tick(.05f);
            Check(g.State.UnsoldCatch.Any(c=>c.Prepared)&&g.State.UnsoldCatch.Any(c=>!c.Prepared),"raw and prepared statuses survive docking");
            g.NewGame();g.Showcase(0,0);var small=new CaughtFish{Species=Species.Mackerel,Kg=.5f};
            Check(!g.IsPrepFisher&&g.DeliverCatch(small)&&g.Cooler.Contains(small)&&g.ProcessingKg==0,"small boat bypasses processing");
            g.LandFish(g.Rods[0],Species.Herring,.2f);g.LandFish(g.Rods[0],Species.Mackerel,.3f);
            foreach(var fDeck in g.OnDeck)fDeck.Age=1;
            g.CommandCarry(g.OnDeck[0]);g.OpenManagement();g.PrepareInterface(1440,900);
            var statuses=(int[])typeof(VoyageGame).GetField("stageStatus",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(g);
            Check(statuses[1]!=2,"active manual carrying is not falsely blocked when small boat has no hired crew");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        static void ForecastAndControls()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("DASH082 forecast check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartTier5Trial();g.State.Chum=10;
            var rng=new System.Random(820);g.State.Rng=new System.Random(820);int coins=g.State.Coins;float richness=g.State.Richness[g.ActiveSpot];
            g.UpdateManagementForecast();
            Check(g.ForecastIncome>0&&g.Forecast.All(f=>f.ValuePerMinute>0),"all equipped methods forecast positive expected value");
            Check(g.State.Rng.Next()==rng.Next()&&g.State.Coins==coins&&g.State.Richness[g.ActiveSpot]==richness,"forecast has no live RNG/economy/stock effects");
            Check(Mathf.Abs(g.Forecast[0].SpeciesCounts.Values.Sum()-1)<.0001f,"rod species probabilities sum to one");
            Check(Mathf.Abs(g.Forecast[0].CycleValue-100*g.Forecast[0].ValuePerMinute/g.Forecast[0].FishPerMinute)<.001f,"per100 catch value weighted by actual actor catch rates");
            float expected=g.ForecastIncome;g.State.Owned.Add(UpgradeId.IceBox);g.UpdateManagementForecast();Check(Mathf.Abs(g.ForecastIncome-expected)<.0001f,"cooler and freshness do not change nominal forecast");
            Check(g.Forecast[1].CycleFish>0&&g.Forecast[1].CycleValue>0,"probability-based per-haul estimate");
            foreach(var size in new[]{new Vector2Int(1672,941),new Vector2Int(1440,900),new Vector2Int(844,390),new Vector2Int(1024,768)})
            {
                g.CloseManagement();g.PrepareInterface(size.x,size.y);Check(g.InvokeInterface("management/open"),"entry "+size);
                g.PrepareInterface(size.x,size.y);Check(g.InvokeInterface("management/tab/income"),"income tab "+size);
                g.PrepareInterface(size.x,size.y);Check(g.InvokeInterface("management/method/2"),"crab method detail "+size);
                g.PrepareInterface(size.x,size.y);Check(g.GetComponentsInChildren<UnityEngine.UI.Text>().Any(t=>t.name=="management/detail/title"&&t.text.StartsWith("Crab")),"method-specific closure "+size);
                Check(!g.InvokeInterface("rod/0"),"underlying fishing command absent");Check(g.InvokeInterface("management/detail/close"),"detail close");
                g.PrepareInterface(size.x,size.y);Check(g.InvokeInterface("management/tab/operations"),"operations tab");g.PrepareInterface(size.x,size.y);
                Check(g.InvokeInterface("management/stage/2"),"processing stage opens");g.PrepareInterface(size.x,size.y);Check(g.InvokeInterface("management/orders"),"processing orders work");g.PrepareInterface(size.x,size.y);Check(g.InvokeInterface("prep/close"),"processing panel closes");
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        static void ConfigureAssets()
        {
            AssetDatabase.Refresh();
            foreach(var name in new[]{"DASH1","DASH2"})
            {
                var path="Assets/Resources/ManagementReference/"+name+".png";var importer=(TextureImporter)AssetImporter.GetAtPath(path);
                importer.textureType=TextureImporterType.Default;importer.maxTextureSize=2048;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.mipmapEnabled=false;importer.npotScale=TextureImporterNPOTScale.None;importer.sRGBTexture=true;importer.SaveAndReimport();
                var texture=Resources.Load<Texture2D>("ManagementReference/"+name);Check(texture.width==1672&&texture.height==941,"original raster dimensions retained without NPOT resampling");
            }
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/dash082");ConfigureAssets();ArtImport.BuildLibrary();Pipeline();ForecastAndControls();ManagementChecks.Run();HandlingPaceChecks.Run();PrepRarityChecks.Run();Balance045Checks.Run();NetHaulChecks.Run();Tier5Checks.Run();PtsWaterChecks.Run();
            Debug.Log("[Catchline] DASH082 CHECKS PASSED");Debug.Log("[Catchline] Snapshot written to Logs/dash082");
        }
        public static void ValidateAndBuild(){Run();BuildPreview();}
        public static void FinalValidateAndBuild(){ConfigureAssets();ArtImport.BuildLibrary();Pipeline();ForecastAndControls();ManagementChecks.Run();Debug.Log("[Catchline] DASH082 CHECKS PASSED");BuildPreview();}
        public static void BuildPreview()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("DASH082 save-isolated preview").AddComponent<VoyageGame>();g.SessionOnly=true;
            string scene="Assets/Scenes/Dash082Test.unity";EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(),scene);
            string output=Path.GetFullPath("Builds/Dash082/Test/Catchline.exe");
            var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{scene},locationPathName=output,target=BuildTarget.StandaloneWindows64});
            Check(result.summary.result==BuildResult.Succeeded,"standalone built");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: "+output);Debug.Log("[Catchline] Snapshot written to Logs/dash082");
        }
    }
}

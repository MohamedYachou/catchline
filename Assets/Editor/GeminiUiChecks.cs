using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    public static class GeminiUiChecks
    {
        static void Check(bool ok,string message){if(!ok)throw new Exception("UI041: "+message);}
        public static void Run()
        {
            ArtImport.BuildLibrary();
            Check(GameData.Fish.Length==29 && (int)Species.Cod==6 && (int)Species.Turbot==9,"legacy IDs and nineteen appended species");
            for(int i=0;i<GameData.Fish.Length;i++)Check((int)GameData.Fish[i].Species==i,"stable definition index "+i);
            var fresh=new GameState(1941){Hull=3};var seen=new System.Collections.Generic.HashSet<Species>();
            for(int ground=1;ground<GameData.Spots.Length;ground++)for(int i=0;i<30000;i++)
            {
                var(s,kg)=fresh.RollFish(ground,1.4f,false,false,true);seen.Add(s);var d=GameData.Get(s);
                Check(kg>=d.MinKg && kg<=d.MaxKg,"specimen mass bounds");
                Check(GameData.Spots[ground].Table.Any(t=>t.species==s),"location membership");
            }
            foreach(var s in Enum.GetValues(typeof(Species)).Cast<Species>().Where(s=>(int)s>=10))Check(seen.Contains(s),"new species actually rolls "+s);
            var starter=new GameState(1942);
            for(int i=0;i<10000;i++){var(s,_)=starter.RollFish(4,1.4f,false,false,true);Check((int)s<10,"locked encounters do not leak to starter");}
            foreach(var tier in Enum.GetValues(typeof(CatchTier)).Cast<CatchTier>())Check(ArtLibrary.Get().UiTex(GeminiUiSkin.Card(tier))!=null,"six card assets "+tier);
            foreach(var s in Enum.GetValues(typeof(Species)).Cast<Species>())
            {
                Check(ArtLibrary.Get().UiTex("fish-"+s.ToString().ToLowerInvariant())!=null,"new portrait "+s);
                var holder=DeckFish.BuildModel(s,GameData.Get(s).MaxKg,null);
                Check(holder.GetComponentsInChildren<MeshFilter>().Sum(m=>m.sharedMesh.vertexCount)>200,"authored mesh content "+s);
                Check(ArtLibrary.Get().FishFor(s)!=null,"authored FBX registered "+s);
                foreach(var mf in holder.GetComponentsInChildren<MeshFilter>())foreach(var v in mf.sharedMesh.vertices)
                    Check(float.IsFinite(v.x)&&float.IsFinite(v.y)&&float.IsFinite(v.z),"finite model");
                UnityEngine.Object.DestroyImmediate(holder.gameObject);
            }
            var fish=Enum.GetValues(typeof(Species)).Cast<Species>().Where(s=>(int)s>=10).Select(s=>new CaughtFish{Species=s,Kg=GameData.Get(s).MaxKg}).ToList();
            var quote=fresh.QuoteSale(fish,0);int before=fresh.Coins;var sold=fresh.Sell(fish,0);
            Check(sold.Coins==quote.Coins && fresh.Coins-before==quote.Coins,"new species quote equals payout");
            string path=Path.Combine(Path.GetTempPath(),"catchline-ui041-"+Guid.NewGuid()+".json");
            try
            {
                File.WriteAllText(path,"{\"Version\":1,\"Coins\":123,\"Owned\":[],\"Charts\":[],\"Board\":[],\"Offers\":[],\"Active\":[],\"Market\":[0.8,1,1,1,1,1,1,1,1,1],\"LogCount\":[2,0,0,0,0,0,1,0,0,0],\"LogBest\":[0.25,0,0,0,0,0,3,0,0,0]}");
                var old=GameState.Load(path);Check(old!=null&&old.Coins==123&&old.LogCount[6]==1&&old.Market[24]==1,"ten-species save grows safely");
                old.UnsoldCatch.Add(new CaughtFish{Species=Species.AbyssalLeviathan,Kg=50,Prepared=true,PreparedQuality=.72f});old.Save(path);var round=GameState.Load(path);
                Check(round.UnsoldCatch.Single().Species==Species.AbyssalLeviathan&&round.UnsoldCatch.Single().PreparedQuality==.72f,"new fish and prepared quality save roundtrip");
            }
            finally{if(File.Exists(path))File.Delete(path);}
            ExportCards();
            HandlingPaceChecks.Run();
            Debug.Log("[Catchline] UI041 CHECKS PASSED");Debug.Log("[Catchline] Snapshot written to Logs/ui041");
        }
        public static void ExportCards()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("UI041 isolated card renders").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartPrepBoatTrial();
            Directory.CreateDirectory("Logs/ui041/cards");
            var specimens=new[]{Species.Mackerel,Species.Cod,Species.GoldenPuffer,Species.SpottedEagleRay,Species.ApexReefShark,Species.AbyssalLeviathan};
            foreach(var s in specimens)
            {
                float kg=s==Species.Mackerel?GameData.Get(s).MinKg:s==Species.GoldenPuffer?.6f:GameData.Get(s).MaxKg;
                g.PrepareGeminiCardPreview(688,288,s,kg);
                Canvas.ForceUpdateCanvases();
                foreach(var text in g.GetComponentsInChildren<Text>().Where(t=>t.name.StartsWith("preview/")))
                    Check(MaskUtilities.GetRectMaskForClippable(text)==text.transform.parent.GetComponent<RectMask2D>(),"actual UGUI clipping ancestor for "+text.name);
                var rt=new RenderTexture(688,288,24,RenderTextureFormat.ARGB32);rt.Create();
                g.RenderGeminiPreview(rt);var previous=RenderTexture.active;RenderTexture.active=rt;
                var tex=new Texture2D(688,288,TextureFormat.RGBA32,false);tex.ReadPixels(new Rect(0,0,688,288),0,0);tex.Apply();
                File.WriteAllBytes("Logs/ui041/cards/"+GeminiUiSkin.Card(CatchPresentation.Tier(s,kg)).Replace("EmptyCardTemplate","PopulatedPreview")+".png",tex.EncodeToPNG());
                RenderTexture.active=previous;UnityEngine.Object.DestroyImmediate(tex);rt.Release();UnityEngine.Object.DestroyImmediate(rt);
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] Snapshot written to Logs/ui041/cards");
        }
        public static void ValidateAndBuild(){Run();PrepFisherChecks.BuildPreview();}
    }
}

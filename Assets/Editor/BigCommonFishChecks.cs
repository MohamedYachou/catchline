using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class BigCommonFishChecks
    {
        static readonly Species[] Added = { Species.YellowfinTuna, Species.Barracuda, Species.MahiMahi, Species.Monkfish };
        static void Check(bool ok, string why) { if (!ok) throw new Exception("FISH050: " + why); }

        public static void ValidateAndBuild()
        {
            Directory.CreateDirectory("Logs/fish050");
            ArtImport.BuildLibrary();
            string[] legacy = { "Herring", "Mackerel", "Pollock", "SeaBass", "Conger", "Plaice", "Cod", "Whiting", "RedMullet", "Turbot", "GoldenPuffer", "SpottedEagleRay", "ApexReefShark", "GoldTipShark", "AbyssalGreatWhite", "AbyssalLeviathan", "BlueSpottedStingray", "FlyingFish", "Lionfish", "GiantDevilManta", "AtlanticSwordfish", "OceanSunfish", "ScallopedHammerhead", "PelagicThresherShark", "GiantSquid" };
            Check(GameData.Fish.Length >= 29, "original29species retained alongside additive species");
            for (int i = 0; i < legacy.Length; i++) Check(((Species)i).ToString() == legacy[i], "legacy ID " + i);
            for (int i = 0; i < Added.Length; i++) Check((int)Added[i] == 25+i, "append-only new ID");
            Check(GameData.Spots[0].Table.Select(e=>e.species).SequenceEqual(new[] {Species.Herring,Species.Mackerel,Species.Whiting}), "starter harbour pool retained");
            var orders = new PrepOrderSettings { HasClassFilters=true, ChumClassMask=2, PrepareClassMask=2 };
            foreach (var s in Added)
            {
                var d = GameData.Get(s);
                foreach (float kg in new[] { d.MinKg, (d.MinKg+d.MaxKg)*.5f, d.MaxKg })
                {
                    Check(CatchPresentation.Tier(s,kg)==CatchTier.BigCommon, "fixed green class " + s);
                    var fish = new CaughtFish { Species=s, Kg=kg };
                    Check(orders.Allows(fish,true)&&orders.Allows(fish,false), "BigCommon prep/chum eligibility " + s);
                    Check(!new PrepOrderSettings().Allows(fish,true), "safe default chum protects new fish");
                    var model=DeckFish.BuildModel(s,kg,null);
                    var meshes=model.GetComponentsInChildren<MeshFilter>();
                    Check(meshes.Length==2 && ArtLibrary.Find(model.gameObject,"Tail")!=null, "authored body and animated tail " + s);
                    Check(meshes.Sum(m=>m.sharedMesh.triangles.Length/3)>1000, "real geometry " + s);
                    var renderers=model.GetComponentsInChildren<Renderer>();
                    Bounds b=renderers[0].bounds;foreach(var r in renderers){b.Encapsulate(r.bounds);Check(r.sharedMaterials.All(m=>m!=null&&m.shader!=null),"material remap " + s);}
                    Check(b.size.z>b.size.y*1.8f && b.size.magnitude<2.5f,"lies on deck at metre scale " + s);
                    Check(Mathf.Abs(b.size.z-d.Length*Mathf.Lerp(.85f,1.25f,Mathf.InverseLerp(d.MinKg,d.MaxKg,kg))*1.3f)<.02f,"heading and length fit " + s);
                    UnityEngine.Object.DestroyImmediate(model.gameObject);
                }
                Check(ArtLibrary.Get().FishFor(s)==AssetDatabase.LoadAssetAtPath<GameObject>("Assets/gemini/Models/"+s+".fbx"),"registered actual FBX " + s);
                var tex=ArtLibrary.Get().UiTex("fish-"+s.ToString().ToLowerInvariant());
                Check(tex!=null&&tex.width==768&&tex.height==384,"matching portrait import " + s);
                var uv=GeminiUiSkin.SpriteRect(tex);Check(uv.x>0&&uv.y>0&&uv.xMax<tex.width&&uv.yMax<tex.height,"portrait alpha crop contained " + s);
            }
            Check(CatchPresentation.Tier(Species.Herring,GameData.Get(Species.Herring).MinKg)==CatchTier.Common && CatchPresentation.Tier(Species.Herring,GameData.Get(Species.Herring).MaxKg)==CatchTier.BigCommon,"old size variants retained");
            var seen=new HashSet<Species>();var report=new System.Text.StringBuilder("ground,rodCatches,newFish\n");
            for(int ground=0;ground<GameData.Spots.Length;ground++)
            {
                var unlocked=new GameState(5000+ground){Hull=2};var locked=new GameState(5010+ground){Hull=1};int additions=0;
                for(int i=0;i<20000;i++)
                {
                    var(s,kg)=unlocked.RollFish(ground,.65f);var(low,_)=locked.RollFish(ground,1.4f,false,false,true);
                    Check((int)low<25,"locked additions excluded");
                    Check(GameData.Spots[ground].Table.Any(e=>e.species==s),"local rod pool");
                    if((int)s>=25){seen.Add(s);additions++;Check(kg>=GameData.Get(s).MinKg&&kg<=GameData.Get(s).MaxKg,"new mass bounds");}
                }
                report.AppendLine($"{GameData.Spots[ground].Name},20000,{additions}");
            }
            Check(Added.All(seen.Contains),"all four roll on normal bait with Compact fisher");
            File.WriteAllText("Logs/fish050/rod-sample.csv",report.ToString());
            SaveAndSale();
            NetPools();
            FishContentChecks.Run();
            GeminiUiChecks.Run();
            Debug.Log("[Catchline] FISH050 CHECKS PASSED");
            // This covers prep class selection, both nets, batch storage, crew,
            // capacity and wait-cap regressions, then builds the current player.
            PrepRarityChecks.ValidateAndBuild();
            Debug.Log("[Catchline] Snapshot written to Logs/fish050");
        }

        static void SaveAndSale()
        {
            string path=Path.Combine(Path.GetTempPath(),"catchline-fish050-"+Guid.NewGuid()+".json");
            try
            {
                var old=new GameState(5050){Hull=2,Coins=321};old.Market[24]=.8f;old.LogCount[24]=3;old.LogBest[24]=50;
                old.UnsoldCatch.Add(new CaughtFish{Species=Species.GiantSquid,Kg=40});old.Save(path);
                // Reconstruct a genuine pre-expansion25-slot save using its existing JSON format.
                var json=JsonUtility.FromJson<LegacyArrays>(File.ReadAllText(path));
                json.Market=json.Market.Take(25).ToArray();json.LogCount=json.LogCount.Take(25).ToArray();json.LogBest=json.LogBest.Take(25).ToArray();
                File.WriteAllText(path,JsonUtility.ToJson(json));var loaded=GameState.Load(path);
                Check(loaded!=null&&loaded.Coins==321&&loaded.LogCount[24]==3&&loaded.LogBest[24]==50&&loaded.Market[24]==.8f,"25-species save preserves prior records");
                Check(loaded.UnsoldCatch.Single().Species==Species.GiantSquid,"old cargo identity retained");
                foreach(var s in Added)Check(loaded.Market[(int)s]==1&&loaded.LogCount[(int)s]==0&&loaded.LogBest[(int)s]==0,"new save slots initialized");
                loaded.UnsoldCatch.Clear();loaded.UnsoldCatch.AddRange(Added.Select(s=>new CaughtFish{Species=s,Kg=GameData.Get(s).MaxKg,Prepared=true,PreparedQuality=.72f}));
                loaded.PrepOrders.HasClassFilters=true;loaded.PrepOrders.ChumClassMask=2;loaded.PrepOrders.PrepareClassMask=2;loaded.Save(path);loaded=GameState.Load(path);
                Check(loaded.UnsoldCatch.Select(f=>f.Species).SequenceEqual(Added)&&loaded.UnsoldCatch.All(f=>f.Prepared&&f.PreparedQuality==.72f),"all new prepared catches save roundtrip");
                Check(loaded.PrepOrders.ChumClasses==2&&loaded.PrepOrders.PrepareClasses==2,"BigCommon selection roundtrip");
                var quote=loaded.QuoteSale(loaded.UnsoldCatch,0);int before=loaded.Coins;var sale=loaded.Sell(loaded.UnsoldCatch,0);
                Check(sale.FishSold==4&&sale.Coins==quote.Coins&&loaded.Coins==before+quote.Coins,"new fish sale equals quote");
                foreach(var s in Added)Check(loaded.LogCount[(int)s]==1&&loaded.LogBest[(int)s]==GameData.Get(s).MaxKg,"new fish records credited");
            }
            finally{if(File.Exists(path))File.Delete(path);}
        }
        [Serializable] sealed class LegacyArrays
        {
            public int Version=1,Coins,Hull;
            public int[] Owned,Charts;
            public CrewMember[] Board;
            public Contract[] Offers,Active;
            public CaughtFish[] UnsoldCatch;
            public float[] Market,LogBest;
            public int[] LogCount;
        }

        static void NetPools()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("FISH050 net pool fixture").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartPrepBoatTrial();
            const BindingFlags hidden=BindingFlags.Instance|BindingFlags.NonPublic;
            var roll=typeof(VoyageGame).GetMethod("RollCompactCatch",hidden);
            var field=typeof(VoyageGame).GetField("netFish",hidden);
            var spot=typeof(VoyageGame).GetProperty("ActiveSpot");
            var seen=new HashSet<Species>();
            for(int ground=1;ground<GameData.Spots.Length;ground++)
            {
                spot.GetSetMethod(true).Invoke(g,new object[]{ground});
                foreach(bool deep in new[]{false,true})
                {
                    g.State.SelectedNet=deep?NetKind.Deep:NetKind.Shallow;g.State.DeepNetUses.Clear();g.State.DeepNetUses.Add(3);
                    for(int i=0;i<200;i++)
                    {
                        roll.Invoke(g,null);var fish=(List<(Species species,float kg)>)field.GetValue(g);
                        Check(fish.Sum(f=>f.kg)<=g.State.NetCapacityKg+.001f,"net hard capacity");
                        foreach(var f in fish)
                        {
                            Check(GameData.Spots[ground].Table.Any(t=>t.species==f.species),"local net pool");
                            if((int)f.species>=25){Check(deep,"signature fish excluded from small-school shallow nets");seen.Add(f.species);}
                        }
                    }
                }
            }
            Check(Added.All(seen.Contains),"all four catchable through deep net");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
    }
}

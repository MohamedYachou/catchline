using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class PrepFisherChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("TIER033: " + why); }
        static void Field(VoyageGame g, string n, object v) => typeof(VoyageGame).GetField(n, H).SetValue(g, v);
        static void Call(VoyageGame g, string n, params object[] args) => typeof(VoyageGame).GetMethod(n, H).Invoke(g, args);
        static void Work(Person p) { for (int n = 0; n < 1600 && !p.Idle; n++) p.Tick(.05f, 1, Quaternion.identity); }
        static Transform Find(VoyageGame g, string name) => g.Boat.GetComponentsInChildren<Transform>(true).Single(t => t.name == name);
        static void Deck(VoyageGame g, string variant)
        {
            var h = g.State.HullDef;
            var mesh = Find(g, "Hull").GetComponent<MeshFilter>();
            Check(mesh.sharedMesh.isReadable, "player can read geometry for routing");
            var points = mesh.sharedMesh.vertices.Select(v => g.Boat.InverseTransformPoint(mesh.transform.TransformPoint(v))).ToArray();
            var size = new Vector3(points.Max(v=>v.x)-points.Min(v=>v.x),points.Max(v=>v.y)-points.Min(v=>v.y),points.Max(v=>v.z)-points.Min(v=>v.z));
            Debug.Log($"[Catchline] TIER033 {variant} hull={size}, walkable={g.CompactWalkableTiles}; prep={string.Join(";",g.PrepWorkerTiles)}");
            Check(Mathf.Abs(size.x - 6.8f)<.01f && Mathf.Abs(size.z - 3.5f)<.01f && size.y<1.2f,"approved dimensions upright at native metre scale");
            for (int i=0;i<3;i++)
            {
                var actual=g.Boat.InverseTransformPoint(Find(g,"RodSocket_"+(i+1)).position);
                Debug.Log($"[Catchline] TIER033 socket{i} {actual}");
                Check(Vector3.Distance(actual,h.RodBases[i])<.006f,"rod attached to exact socket"+i);
            }
            Check(!g.Boat.GetComponentsInChildren<Transform>(true).Any(t=>t.name.StartsWith("T3 ") || t.name.StartsWith("T4 prep hand")),"no comparison statues in game");
            var jobs=new[]{h.Seat,h.HoldAccess,h.NetAccess}.Concat(h.CrewRest).Concat(h.RodTiles).Concat(g.PrepWorkerTiles).Distinct().ToArray();
            File.WriteAllLines("Logs/tier033/deck-"+variant+".txt",Enumerable.Range(0,g.Grid.Height).Reverse().Select(y=>string.Concat(Enumerable.Range(0,g.Grid.Width).Select(x=>jobs.Contains(new Vector2Int(x,y)) ? (g.Grid.IsBlocked(new Vector2Int(x,y))?'X':'J') : g.Grid.IsBlocked(new Vector2Int(x,y))?'#':'.'))));
            foreach(var a in jobs)
            {
                Check(!g.Grid.IsBlocked(a),"job must be physically clear "+variant+" "+a);
                foreach(var b in jobs) Check(g.Grid.FindPath(a,b)!=null,"connected jobs "+a+" to "+b);
            }
            Check(Find(g,"RawBuckets").gameObject.activeSelf==!g.State.Has(UpgradeId.IceBox),"bucket variant follows upgrade");
            Check(Find(g,"RawIceCoolers").gameObject.activeSelf==g.State.Has(UpgradeId.IceBox),"cooler variant follows upgrade");
            Check(Find(g,"PreparedHold").gameObject.activeInHierarchy,"rear prepared boxes always present");
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/tier033");
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("TIER033 isolated check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();
            Check(g.StartPrepBoatTrial(),"isolated trial can start");
            Check(g.IsPrepFisher && g.IsNetFisher && g.State.CrewCount==4 && g.ExtraPeople.Count==3,"four real temporary workers plus captain");
            Check(g.Rods.Count==3 && g.State.CoolerCapacity==160,"production Prep capacity and rod count");
            Deck(g,"buckets");
            g.Showcase(-1,0);g.State.Owned.Add(UpgradeId.IceBox);g.SyncUpgrades();
            // Storage footprints differ; rebuild the physical grid on a port upgrade.
            Deck(g,"ice-coolers");
            g.State.Owned.Remove(UpgradeId.IceBox);Call(g,"RebuildBoat",true);
            g.Showcase(0,0);Field(g,"toastUntil",0f);
            for(int i=0;i<2400;i++)
            {
                g.Tick(.05f);
                foreach(var p in new[]{g.Captain,g.Hand}.Concat(g.ExtraPeople)) Check(!g.Grid.IsBlocked(p.Tile),"live worker remains on clear deck "+p.Name+" "+p.Tile);
            }
            Check(g.Rods.Count(r=>r.Fisher!=null)==2 && g.Stats.Landed>3 && g.Cooler.Count>0,"real fishermen and deckhands fish and deliver on the new deck");
            Debug.Log($"[Catchline] TIER033120s trace: landed={g.Stats.Landed}, stored={g.Cooler.Count}, kg={g.HoldKg}");
            foreach(var p in new[]{g.Captain,g.Hand}.Concat(g.ExtraPeople))p.Stop();
            // The timed trace may finish with a fish in hand. Finish that delivery
            // before testing a separate net allocation; Stop intentionally preserves cargo.
            foreach(var p in new[]{g.Captain,g.Hand}.Concat(g.ExtraPeople))
                if(p.Carrying!=null) Call(g,"TryStow",p);
            Call(g,"ResetNet");g.Cooler.Clear();
            Check(g.SetDeckhandWork(g.State.Deckhand,DeckhandWork.Nets),"tier4 net duty selectable");
            Call(g,"HandThink",g.Hand);Work(g.Hand);Check(g.Net==VoyageGame.NetState.Soaking,"hand reaches new stern and sets net");
            Call(g,"TickNet",GameData.ShallowNetSoakSeconds);g.State.Rng=new System.Random(0);Call(g,"HandThink",g.Hand);Work(g.Hand);
            Check(g.NetBasketCount>0,"hand can haul into relocated basket");
            Check(g.OnDeck.Where(f=>f.FromNetBasket).All(f=>f.RestPos.x>5.3f),"net catch stays behind prepared boxes");
            // Clear net work so normal return can run without a modal confirmation.
            g.HeadHome();for(int n=0;n<1200 && g.CurrentMode!=VoyageGame.Mode.Harbour;n++)g.Tick(.05f);
            Check(g.CurrentMode==VoyageGame.Mode.Harbour,"trial docks");
            g.State.Save("Logs/tier033/isolated-state.json");var loaded=GameState.Load("Logs/tier033/isolated-state.json");
            Check(loaded.Hull==3 && loaded.CrewCount==4 && loaded.HullDef.Model=="PrepFisherV1","additive hull/four crew save roundtrip");
            Check(GameData.Hulls[0].Model=="Rowboat" && GameData.Hulls[1].Model=="Skiff" && GameData.Hulls[2].Model=="CompactFisherV1","old saved hull IDs unchanged");
            g.State.Coins=3000;g.PrepareInterface(844,390);Field(g,"hudTab",VoyageGame.HudTab.Chandlery);Field(g,"panelOpen",true);Field(g,"toastUntil",0f);g.PrepareInterface(844,390);
            Check(g.InvokeInterface("trial/netboat/buy") && g.State.Hull==2 && g.State.CrewCount==3,"tier3 trial downgrade respects three-crew cap");
            g.PrepareInterface(844,390);Check(g.InvokeInterface("trial/prepboat/buy") && g.IsPrepFisher,"native shipyard card selects tier4");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            CompactFisherChecks.Run();
            Debug.Log("[Catchline] TIER033 CHECKS PASSED");
            Debug.Log("[Catchline] Snapshot written to Logs/tier033");
        }
        public static void ValidateAndBuild()
        {
            Run();
            BuildPreview();
        }
        public static void BuildPreview()
        {
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("Tier4 save-isolated preview").AddComponent<VoyageGame>();g.SessionOnly=true;
            const string path="Assets/Scenes/Tier033Preview.unity";EditorSceneManager.SaveScene(scene,path);
            var output=Path.GetFullPath("Builds/Tier033/Catchline.exe");
            var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{path},locationPathName=output,target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
            Check(report.summary.result==BuildResult.Succeeded,"standalone player build "+report.summary.result);
            Debug.Log("[Catchline] TIER033 PLAYABLE PREVIEW BUILT: "+output);
        }
    }
}

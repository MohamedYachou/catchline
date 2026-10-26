using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.EditorTools
{
    public static class PetsCapture
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static readonly string Out = Path.GetFullPath("../Catchline/docs/screens/harbour-pets-1");
        static int assertions;
        static void Check(bool ok, string why)
        { assertions++; if (!ok) throw new Exception("[Catchline] HARBOUR PETS: " + why); }
        static void Field(VoyageGame g,string name,object value) => typeof(VoyageGame).GetField(name,Hidden).SetValue(g,value);
        static object Call(VoyageGame g,string name,params object[] args) => typeof(VoyageGame).GetMethod(name,Hidden).Invoke(g,args);

        public static void Run()
        {
            assertions=0;
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name=="Catchline-sim","isolated scratch only");
            Directory.CreateDirectory(Out); ArtImport.BuildLibrary();
            Check(ArtLibrary.Get().M("Dog")!=null && ArtLibrary.Get().M("Cat")!=null,"generic library discovers both");
            var contact = new List<string>();
            foreach (string animal in new[]{"Dog","Cat"}) contact.Add(ImportAndContact(animal));
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var go=new GameObject("Harbour pets evidence - no save"); go.SetActive(false);
            var g=go.AddComponent<VoyageGame>(); g.SessionOnly=true; g.Build(); go.SetActive(true);
            try
            {
                Call(g,"EndIntro"); g.State.Hull=1; g.State.Tutorial=(int)VoyageGame.TutStep.Done;
                Field(g,"showTitle",false); Field(g,"paused",false); Field(g,"panelOpen",false);
                Call(g,"RebuildBoat",false); g.Tick(.05f);
                var dogs=UnityEngine.Object.FindObjectsByType<HarbourDog>(FindObjectsInactive.Exclude,FindObjectsSortMode.None);
                var cats=UnityEngine.Object.FindObjectsByType<HarbourCat>(FindObjectsInactive.Exclude,FindObjectsSortMode.None);
                Check(dogs.Length==1&&cats.Length==1,"one active dog/cat through production hook");
                var dog=dogs.Single(); var cat=cats.Single();
                Check(dog.enabled && cat.enabled,"all required Legacy clips found");
                Check(Mathf.Abs(dog.transform.position.y-.35f)<.001f,"dog on quay edge paving");
                Check(Mathf.Abs(cat.transform.position.y-1.035f)<.001f,"cat on crate lid");
                var support=cat.transform.parent;
                Check(support.GetComponentsInChildren<Transform>().Count(t=>t.name=="Crate lid plank")==3,"solid lid on open artist crate");
                Check(Mathf.Abs(support.position.y-.33f)<.001f,"crate on lower back paving");
                var catCentre=cat.transform.position+Vector3.up*.12f;
                foreach(var r in UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
                    if(r.enabled && r.GetComponentInParent<HarbourCat>()==null)
                        Check(!r.bounds.Contains(catCentre),"cat clear of scenery bounds: "+r.name);
                var dogActions=new HashSet<string>(); var catActions=new HashSet<string>();
                var fixedCat=cat.transform.position; var fixedCatRotation=cat.transform.rotation;
                float seenWest=float.MaxValue,seenEast=float.MinValue;
                float lastLookStart=-1,lookAge=0; int lookCount=0,stops=0; string beforeCat=cat.Action;
                for (int i=0;i<12000;i++)
                {
                    const float dt=.05f;
                    var pos=dog.transform.position; var yaw=dog.transform.rotation; string beforeDog=dog.Action;
                    dog.Tick(dt); cat.Tick(dt); dogActions.Add(dog.Action); catActions.Add(cat.Action);
                    var p=dog.transform.position; seenWest=Mathf.Min(seenWest,p.x);seenEast=Mathf.Max(seenEast,p.x);
                    Check(p.x>=HarbourDog.West-.001f&&p.x<=HarbourDog.East+.001f,"dog stays on eight-metre beat");
                    Check(Mathf.Abs(p.y-.35f)<.001f&&Mathf.Abs(p.z-HarbourDog.Lane)<.001f,"dog holds quay surface/lane");
                    Check(Vector3.Distance(pos,p)<=.75f*dt+.0001f,"dog walking pace");
                    Check(Quaternion.Angle(yaw,dog.transform.rotation)<=180*dt+.02f,"smooth bounded turn");
                    if(beforeDog=="Trot"&&dog.Action!="Trot")
                    { Check(dog.LastStopDuration>=3&&dog.LastStopDuration<=8,"random stop duration3..8");stops++; }
                    if(beforeDog!="Trot"&&dog.Action!="Trot") Check(Vector3.Distance(pos,p)<.0001f,"dog holds still while sniffing/sitting");
                    Check(Vector3.Distance(cat.transform.position,fixedCat)<.0001f&&Quaternion.Angle(cat.transform.rotation,fixedCatRotation)<.001f,"cat fixed on perch");
                    if(beforeCat!="Look"&&cat.Action=="Look")
                    {
                        float start=(i+1)*dt;
                        if(lastLookStart>=0) Check(start-lastLookStart>=19.94f&&start-lastLookStart<=40.06f,"Look start interval20..40");
                        lastLookStart=start;lookAge=0;lookCount++;
                    }
                    if(cat.Action=="Look") lookAge+=dt;
                    if(beforeCat=="Look"&&cat.Action!="Look") Check(Mathf.Abs(lookAge-3)<.061f,"Look lasts3s");
                    beforeCat=cat.Action;
                }
                Check(dogActions.SetEquals(new[]{"Trot","Sit","Sniff"})&&stops>=10,"dog visits all three actions repeatedly");
                Check(seenWest<HarbourDog.West+.1f&&seenEast>HarbourDog.East-.1f,"dog traverses full beat");
                Check(catActions.SetEquals(new[]{"Sleep","Look"})&&lookCount>=10,"cat sleeps and looks repeatedly");
                Check(HarbourDog.Lane-3.5f>.4f&&HarbourDog.Lane>2.6f,"pet lane separated from walkers/bollards/boats");
                Debug.Log("[Catchline] HARBOUR PETS BEHAVIOUR PASSED:600s,stops="+stops+",looks="+lookCount+",dog="+string.Join(",",dogActions));

                // Natural patrol position near the cat, same pose for both overview sizes.
                for(int i=0;i<4000&&(dog.transform.position.x< -13.8f||dog.transform.position.x> -13.4f||dog.Action!="Trot");i++) dog.Tick(.05f);
                Check(dog.transform.position.x>=-13.8f&&dog.transform.position.x<=-13.4f,"overview dog patrol position");
                var town=g.GetComponentsInChildren<TownWalker>().First();
                town.Tick(.01f); // same imported townsperson, staged only for the scale evidence
                town.transform.localPosition=new Vector3(-14.6f,.35f,3.05f);
                town.transform.localRotation=Quaternion.Euler(0,180,0);
                foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
                {
                    g.Cam.aspect=size.x/(float)size.y; Field(g,"snapCamera",true);
                    for(int n=0;n<80;n++) Call(g,"Visual",.025f);
                    foreach(var pet in new[]{dog.transform,cat.transform})
                    { var view=g.Cam.WorldToViewportPoint(pet.position); Check(view.z>0&&view.x>.1f&&view.x<.9f&&view.y>.13f&&view.y<.9f,"both pets inside overview camera"); }
                    Shot(g,"harbour-"+size.x,size,true);
                }
                Close(g,dog.transform.position,"dog-close",town);
                Close(g,cat.transform.position,"cat-close",town);
                File.WriteAllText(Path.Combine(Out,"checks.json"),JsonUtility.ToJson(new Receipt{
                    passed=true,assertions=assertions,behaviourSeconds=600,stops=stops,looks=lookCount,
                    importContact=contact.ToArray(),limits=new[]{"Editor URP/Canvas captures, not standalone or installed-player acceptance.","Townsperson staged beside pets for scale; animal model scale unchanged.","Runtime Legacy crossfades use imported actions; editor contact proof samples every imported animation frame."}
                },true));
            }
            finally{UnityEngine.Object.DestroyImmediate(go);}
            Debug.Log("[Catchline] HARBOUR PETS CHECKS PASSED:"+assertions);
            Debug.Log("[Catchline] Snapshot written to "+Out);
        }
        [Serializable] sealed class Receipt
        { public bool passed;public int assertions,behaviourSeconds,stops,looks;public string[] importContact,limits; }

        static string ImportAndContact(string animal)
        {
            string path="Assets/Art/Models/HarbourLife/"+animal+".fbx";
            var importer=(ModelImporter)AssetImporter.GetAtPath(path);
            Check(importer.importAnimation&&importer.animationType==ModelImporterAnimationType.Legacy,animal+" Legacy importer");
            var clips=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToArray();
            var expected=animal=="Dog"?new[]{"Trot","Sit","Sniff"}:new[]{"Sleep","Look"};
            Check(clips.Length==expected.Length&&expected.All(n=>clips.Any(c=>c.name.EndsWith(n))),animal+" exact clips");
            var rig=ArtLibrary.Spawn(ArtLibrary.Get().M(animal),null,Vector3.zero,Quaternion.identity);
            try
            {
                var animation=rig.GetComponentInChildren<Animation>(); Check(animation!=null,animal+" Animation component");animation.enabled=false;
                var skin=rig.GetComponentsInChildren<SkinnedMeshRenderer>().Single();
                var mesh=new Mesh(); float min=float.MaxValue,max=float.MinValue;int samples=0;
                try
                {
                    foreach(var clip in clips)
                    {
                        Check(clip.legacy,clip.name+" legacy");
                        for(int f=0;f<=Mathf.CeilToInt(clip.length*30);f++)
                        {
                            clip.SampleAnimation(rig,Mathf.Min(f/30f,clip.length));skin.BakeMesh(mesh);
                            float floor=mesh.vertices.Min(v=>skin.transform.TransformPoint(v).y);
                            min=Mathf.Min(min,floor);max=Mathf.Max(max,floor);samples++;
                            Check(Mathf.Abs(floor)<.025f,animal+" imported pose floor "+clip.name+"/"+f+":"+floor);
                            Check(rig.transform.position.sqrMagnitude<.00001f,animal+" no exported root motion");
                        }
                    }
                }
                finally{UnityEngine.Object.DestroyImmediate(mesh);}
                return animal+" "+samples+" imported frames floor="+min.ToString("F4")+".."+max.ToString("F4");
            }
            finally{UnityEngine.Object.DestroyImmediate(rig);}
        }
        static void Close(VoyageGame g,Vector3 pet,string file,TownWalker person)
        {
            person.transform.localPosition=new Vector3(pet.x+1.0f,.35f,3.05f);
            var focus=new Vector3(pet.x+.35f,.75f,pet.z);
            g.Cam.transform.position=focus-g.Cam.transform.forward*30;
            g.Cam.orthographicSize=1.7f;g.Cam.aspect=1.6f;
            Shot(g,file,new Vector2Int(1440,900),false);
        }
        static void Shot(VoyageGame g,string file,Vector2Int size,bool hud)
        {
            var rt=new RenderTexture(size.x,size.y,24,RenderTextureFormat.ARGB32);
            var ui=new RenderTexture(size.x,size.y,24,RenderTextureFormat.ARGB32);
            var composite=new Material(Shader.Find("Hidden/Catchline/Coastal UI Composite"));
            var texture=new Texture2D(size.x,size.y,TextureFormat.RGB24,false);
            var previous=RenderTexture.active;var target=g.Cam.targetTexture;
            try
            {
                g.Cam.targetTexture=rt;g.Cam.aspect=size.x/(float)size.y;
                if(hud){g.PrepareInterface(size.x,size.y,1);Canvas.ForceUpdateCanvases();g.PrepareInterface(size.x,size.y,1);}
                foreach(var pet in g.GetComponentsInChildren<SkinnedMeshRenderer>())
                    foreach(var material in pet.sharedMaterials) Check(material!=null&&material.shader!=null&&material.shader.name!="Hidden/InternalErrorShader","no pink skinned materials");
                RenderPipeline.SubmitRenderRequest(g.Cam,new RenderPipeline.StandardRequest{destination=rt});
                if(hud){g.GetComponentInChildren<CoastalCanvas>().RenderCapture(ui);Graphics.Blit(ui,rt,composite);}
                RenderTexture.active=rt;texture.ReadPixels(new Rect(0,0,size.x,size.y),0,0);texture.Apply();
                File.WriteAllBytes(Path.Combine(Out,file+".png"),texture.EncodeToPNG());
            }
            finally
            {
                RenderTexture.active=previous;g.Cam.targetTexture=target;
                UnityEngine.Object.DestroyImmediate(texture);UnityEngine.Object.DestroyImmediate(rt);
                UnityEngine.Object.DestroyImmediate(ui);UnityEngine.Object.DestroyImmediate(composite);
            }
        }
    }
}

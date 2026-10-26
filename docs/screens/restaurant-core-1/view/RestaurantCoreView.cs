using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
public static class RestaurantCoreView {
 const string Out="C:/Users/momoy/Projects/Catchline/docs/screens/restaurant-core-1/view";
 [Serializable] public class Row { public string file,projection; public int width,height,roomW,roomD,pitch,topBand,bottomBand; public float tileW,tileD,crewHeight,crewWorldHeight,orthoSize,distance,fov; public bool fits,tappable; public int kitchenVisible,kitchenSamples,kitchenFloorVisible; public string blockedBy; }
 [Serializable] public class Rows {public List<Row> captures=new List<Row>();}
 static Material Mat(string hex){var m=new Material(Shader.Find("Universal Render Pipeline/Lit"));ColorUtility.TryParseHtmlString(hex,out var c);m.color=c;return m;}
 static GameObject Box(string n,Vector3 p,Vector3 s, Material m){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=n;g.transform.position=p;g.transform.localScale=s;g.GetComponent<Renderer>().sharedMaterial=m;return g;}
 static Bounds BoundsOf(GameObject g){var rr=g.GetComponentsInChildren<Renderer>().Where(r=>r.gameObject.activeInHierarchy).ToArray();var b=rr[0].bounds;foreach(var r in rr)b.Encapsulate(r.bounds);return b;}
 static Vector3[] Corners(Bounds b){var list=new List<Vector3>();for(int x=0;x<2;x++)for(int y=0;y<2;y++)for(int z=0;z<2;z++)list.Add(b.min+Vector3.Scale(b.size,new Vector3(x,y,z)));return list.ToArray();}
 static GameObject Crew(float x,float z){var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Art/Models/Crew/CrewRig.fbx");if(!prefab)throw new Exception("Real crew missing");var g=UnityEngine.Object.Instantiate(prefab);g.name="Real CrewRig - native scale";g.transform.position=new Vector3(x,0,z);foreach(var t in g.GetComponentsInChildren<Transform>(true)){if(t.name.StartsWith("Outfit_"))t.gameObject.SetActive(t.name=="Outfit_Deckhand");if(t.name.StartsWith("Hat_"))t.gameObject.SetActive(t.name=="Hat_Beanie");}var clip=AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Models/Crew/CrewRig.fbx").OfType<AnimationClip>().FirstOrDefault(a=>a.name.ToLower().Contains("idle"));if(clip)clip.SampleAnimation(g,0);var a=g.GetComponent<Animation>();if(a)a.enabled=false;foreach(var r in g.GetComponentsInChildren<Renderer>()){var mm=r.sharedMaterials;for(int i=0;i<mm.Length;i++){Color c=mm[i]?mm[i].color:new Color(.8f,.65f,.4f);mm[i]=Mat("#D9A46A");mm[i].color=c;}r.sharedMaterials=mm;}var b=BoundsOf(g);g.transform.position-=new Vector3(0,b.min.y,0);b=BoundsOf(g);var blocker=g.AddComponent<BoxCollider>();blocker.center=g.transform.InverseTransformPoint(b.center);blocker.size=b.size;return g;}

 public static void Run(){Directory.CreateDirectory(Out);var rows=new Rows();foreach(int w in new[]{8,10,12,14,17}){
 EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);int k=w==8?3:w==10||w==12?4:5;
 var wood=Mat("#BA936B");var cream=Mat("#E8E0CC");var metal=Mat("#718A8A");var navy=Mat("#173F57");var warm=Mat("#C3AA88");var orange=Mat("#E36A35");
 for(int x=0;x<w;x++)for(int z=0;z<5;z++)Box("Tile "+x+","+z,new Vector3(x+.5f,-.045f,z+.5f),new Vector3(.98f,.09f,.98f),x<k?warm:x>=14?metal:wood);
 Box("Low back wall",new Vector3(w/2f,.5f,5.06f),new Vector3(w,1,.12f),cream);Box("Low west wall",new Vector3(-.06f,.5f,2.5f),new Vector3(.12f,1,5),cream);Box("Low east wall",new Vector3(w+.06f,.5f,2.5f),new Vector3(.12f,1,5),cream);
 for(int z=1;z<5;z++)Box("Pass front to back",new Vector3(k+.5f,.4f,z+.5f),new Vector3(.9f,.8f,.95f),navy);
 for(int z=1;z<5;z++)Box("Kitchen station",new Vector3(.5f,.45f,z+.5f),new Vector3(.9f,.9f,.9f),metal);
 Box("Door on quay",new Vector3((w==17?14:w)-.5f,.02f,.5f),new Vector3(.94f,.04f,.94f),orange);Box("Reception",new Vector3((w==17?14:w)-1.5f,.4f,.5f),new Vector3(.9f,.8f,.8f),navy);
 for(int x=k+2;x<w-1;x+=2)for(int z=2;z<5;z+=2)Box("Guest table",new Vector3(x+.5f,.38f,z+.5f),new Vector3(.8f,.76f,.8f),cream);
 var crew=Crew(1.5f,2.5f);Crew(w-2.5f,1.5f);var light=new GameObject("Key").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.3f;light.transform.rotation=Quaternion.Euler(48,-35,0);RenderSettings.ambientMode=UnityEngine.Rendering.AmbientMode.Flat;RenderSettings.ambientLight=new Color(.65f,.7f,.76f);
 var cam=new GameObject("52deg arranging camera").AddComponent<Camera>();cam.orthographic=true;cam.transform.rotation=Quaternion.Euler(52,0,0);cam.backgroundColor=new Color(.12f,.22f,.27f);cam.clearFlags=CameraClearFlags.SolidColor;cam.nearClipPlane=.05f;cam.farClipPlane=100;
 foreach(var res in new[]{new Vector2Int(844,390),new Vector2Int(1440,900)}){int rw=res.x,rh=res.y,top=rh==390?44:66,bot=rh==390?84:126,usable=rh-top-bot;float ppu=rh==390?56:96;
 cam.rect=new Rect(0,bot/(float)rh,1,usable/(float)rh);cam.aspect=rw/(float)usable;cam.orthographicSize=usable/(2*ppu);cam.transform.position=new Vector3(w==17?7:w/2f,.5f,2.5f)-cam.transform.forward*40;
 Func<Vector3,Vector2> screen=p=>{var q=cam.WorldToViewportPoint(p);return new Vector2(q.x*rw,q.y*usable);};var b=BoundsOf(crew);float ch=Vector2.Distance(screen(new Vector3(b.center.x,b.min.y,b.center.z)),screen(new Vector3(b.center.x,b.max.y,b.center.z)));
 string name=$"{w}x5-52-ortho-{rw}x{rh}";var rt=new RenderTexture(rw,rh,24);cam.targetTexture=rt;cam.Render();RenderTexture.active=rt;var tex=new Texture2D(rw,rh,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,rw,rh),0,0);tex.Apply();File.WriteAllBytes(Out+"/"+name+".png",tex.EncodeToPNG());cam.targetTexture=null;RenderTexture.active=null;UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(tex);
 rows.captures.Add(new Row{file=name+".png",projection="ortho",width=rw,height=rh,roomW=w,roomD=5,pitch=52,topBand=top,bottomBand=bot,tileW=ppu,tileD=ppu*Mathf.Sin(52*Mathf.Deg2Rad),crewHeight=ch,crewWorldHeight=b.size.y,orthoSize=cam.orthographicSize,fits=w*ppu<=rw,tappable=true});
 }}File.WriteAllText(Out+"/metrics.json",JsonUtility.ToJson(rows,true));Debug.Log("[Restaurant] VIEW COMPLETE10");}
}

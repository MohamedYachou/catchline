using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game.Restaurant
{
    public sealed class StaffSnapshot
    {
        public string Id, PortraitKey, Task; public Job Job; public float Busy;
    }
    public sealed class OrderSnapshot
    {
        public int TableId, GroupId; public Dish Dish; public float Patience; public GroupPhase Phase;
    }
    public sealed class StockSnapshot { public Dish Dish; public Species Species; public int Portions; }
    public sealed class QuestionSnapshot { public int GuestId; public string Title, Yes, No; }
    public sealed class RestaurantSnapshot
    {
        public float Hour, Popularity; public int CoinsTonight; public bool Finished;
        public readonly List<StaffSnapshot> Staff=new();
        public readonly List<OrderSnapshot> Orders=new();
        public readonly List<StockSnapshot> Stock=new();
        public readonly List<int> BrokenAppliances=new();
        public QuestionSnapshot Question;
    }

    // Presentation follows the pure service clock. No UI, save access or second simulation is hidden here.
    // Tick ownership is explicit: leave DriveSimulation=true, OR set false and let the day loop Tick its sim.
    public sealed class RestaurantWorld : MonoBehaviour
    {
        public static readonly Vector3 HarbourQuayOrigin=new(18f,.31f,9f);
        public bool DriveSimulation=true;
        public float Popularity=1;
        public RestaurantSim Sim {get;private set;}
        public RestaurantSnapshot Snapshot {get;}=new();
        public Camera ServiceCamera {get;private set;}
        public int Speed {get;private set;}=1;
        public Transform RoomRoot {get;private set;}
        const int Layer=28;
        readonly Dictionary<int,Transform> items=new();
        readonly Dictionary<string,Actor> actors=new();
        readonly Dictionary<int,Actor> guests=new();
        readonly List<Camera> previousCameras=new();
        readonly Dictionary<string,AnimationClip> clips=new();
        readonly List<Material> guestMaterials=new();
        int width,height;
        float animationTime;
        sealed class Actor
        {
            public Transform Root,Rig,Prop; public Vector3 Last; public float Phase;
        }
        static readonly Dictionary<ItemId,string> Models=new(){
            [ItemId.Stove]="Stove",[ItemId.SoupKettle]="SoupKettle",[ItemId.PrepCounter]="PrepCounter",
            [ItemId.Fridge]="FridgeV2",[ItemId.CoffeeMachine]="CoffeeBar",[ItemId.DrinksFridge]="FridgeV2",
            [ItemId.Table2]="TableFor2",[ItemId.Table4]="TableFor4",[ItemId.Booth6]="Booth",
            [ItemId.TerraceTable]="TerraceTable",[ItemId.Reception]="ReceptionDesk",[ItemId.Sink]="SinkDishRack",
            [ItemId.Fryer]="Fryer",[ItemId.Oven]="Oven",[ItemId.Grill]="Stove",[ItemId.Steamer]="SoupKettle",
            [ItemId.BarCounter]="PassCounter",[ItemId.Plant]="PlantPot1",[ItemId.Lamp]="LampPost",
            [ItemId.Trophy]="PlantPot2",[ItemId.Net]="PlantPot2",[ItemId.Chart]="PlantPot2",[ItemId.Jukebox]="CoffeeBar"
        };
        GameObject Model(string name)=>ArtLibrary.Get()?.M("Restaurant_"+name);
        Transform Spawn(string name,Vector3 p,Quaternion rotation,Transform parent=null)
        {
            var prefab=Model(name);
            if(prefab==null)throw new InvalidOperationException("Restaurant asset missing: "+name+". Rebuild ArtLibrary after importing the Restaurant folder.");
            return ArtLibrary.Spawn(prefab,parent??RoomRoot,p,rotation).transform;
        }
        public Vector3 TileToWorld(Vector2 tile,float y=.04f)=>RoomRoot.TransformPoint(new Vector3(tile.x-3.5f,y,2-tile.y));
        public void Begin(RestaurantSim sim)
        {
            if(sim==null)throw new ArgumentNullException(nameof(sim));
            End();Sim=sim;Speed=1;animationTime=0;
            RoomRoot=new GameObject("Restaurant night (quay)").transform;
            RoomRoot.position=HarbourQuayOrigin;
            try {
                Spawn("RoomShell",Vector3.zero,Quaternion.identity);
                foreach(var item in sim.Layout.Active){
                    if(!Models.TryGetValue(item.Id,out var model))continue;
                    float x=item.X+(item.Rotated?1:RestaurantData.Get(item.Id).Width)*.5f-.5f;
                    var pos=new Vector3(x-3.5f,.04f,2-item.Y);
                    var t=Spawn(model,pos,Quaternion.Euler(0,item.Rotated?90:0,0));items.Add(item.Uid,t);
                    if(RestaurantData.Get(item.Id).Seats>0){Spawn("TableLantern",pos+Vector3.up*.57f,Quaternion.identity);}
                }
                Spawn("PassCounter",new Vector3(-.5f,.04f,0),Quaternion.Euler(0,90,0));
                Spawn("TrashCan",new Vector3(-2.7f,.04f,2.05f),Quaternion.identity);
                Spawn("PlantPot1",new Vector3(3.65f,.04f,-.5f),Quaternion.identity);
                foreach(var clip in ArtLibrary.Get().CrewClips??Array.Empty<AnimationClip>())if(clip!=null){var n=clip.name.Split('|').Last();clips[n]=clip;}
                foreach(var staff in sim.Staff)actors[staff.Id]=MakeActor(staff.Id,false);
                ServiceCamera=new GameObject("Restaurant camera").AddComponent<Camera>();
                ServiceCamera.transform.SetParent(RoomRoot,false);
                ServiceCamera.clearFlags=CameraClearFlags.SolidColor;ServiceCamera.backgroundColor=new Color(.09f,.3f,.56f); // the mockup's evening sea
                ServiceCamera.nearClipPlane=.1f;ServiceCamera.farClipPlane=70;ServiceCamera.cullingMask=1<<Layer;ServiceCamera.depth=30;
                // V3's camera study: 38 degree pitch, -2 degree yaw from the quay, 58mm equivalent.
                ServiceCamera.transform.localPosition=new Vector3(-.598f,13.359f,17.088f);
                ServiceCamera.transform.localRotation=Quaternion.Euler(38,178,0);
                ServiceCamera.orthographic=false;ServiceCamera.fieldOfView=21.9542f;
                foreach(var c in Camera.allCameras)if(c!=ServiceCamera&&c.enabled){previousCameras.Add(c);c.enabled=false;}
                AddLight(new Vector3(-3,7,3),new Color(.68f,.78f,1),.6f,true);
                foreach(float x in new[]{-3.6f,.15f,3.6f})AddLight(new Vector3(x,2.5f,-1.9f),new Color(1,.68f,.3f),2.5f,false);
                // The player build drops the material's atlas reference; bind the painted atlas from Resources.
                var atlas=Resources.Load<Texture2D>("RestaurantAtlas/Restaurant_BaseColor");var surface=Resources.Load<Texture2D>("RestaurantAtlas/Restaurant_Surface");
                foreach(var r in RoomRoot.GetComponentsInChildren<Renderer>(true))foreach(var m in r.sharedMaterials)
                    if(m!=null&&m.shader.name=="Catchline/RestaurantAtlas"&&m.GetTexture("_BaseMap")==null){m.SetTexture("_BaseMap",atlas);m.SetTexture("_SurfaceMap",surface);}
                SetLayer(RoomRoot.gameObject);FrameCamera();Refresh(0);
            }catch{End();throw;}
        }
        void AddLight(Vector3 position,Color color,float intensity,bool sun)
        {
            var go=new GameObject(sun?"Blue dusk":"Warm practical");go.transform.SetParent(RoomRoot,false);go.transform.localPosition=position;
            var l=go.AddComponent<Light>();l.type=sun?LightType.Directional:LightType.Point;l.color=color;l.intensity=intensity;l.range=6;l.cullingMask=1<<Layer;
            if(sun)go.transform.localRotation=Quaternion.Euler(42,-25,0);
        }
        static void SetLayer(GameObject go){foreach(var t in go.GetComponentsInChildren<Transform>(true))t.gameObject.layer=Layer;}
        Actor MakeActor(string id,bool guest)
        {
            var holder=new GameObject((guest?"Guest ":"Staff ")+id).transform;holder.SetParent(RoomRoot,false);
            var lib=ArtLibrary.Get();string[] civilians={"Ada","Ben","Cora","Dan","Edda","Finn"};
            var prefab=lib?.M(guest?"Restaurant_Guest_"+civilians[guests.Count%civilians.Length]:"CrewRig");
            if(prefab==null)throw new InvalidOperationException("Boat CrewRig is missing from ArtLibrary");
            var rig=ArtLibrary.Spawn(prefab,holder,Vector3.zero,Quaternion.identity).transform;
            foreach(var a in rig.GetComponentsInChildren<Animation>())a.enabled=false;
            foreach(var a in rig.GetComponentsInChildren<Animator>())a.enabled=false;
            string outfit=id=="captain"?"Outfit_Captain":"Outfit_Deckhand";
            foreach(var t in rig.GetComponentsInChildren<Transform>(true)){
                if(t.name.StartsWith("Outfit_"))t.gameObject.SetActive(t.name==outfit);
                if(t.name.StartsWith("Hat_"))t.gameObject.SetActive(!guest&&t.name==(id=="captain"||id=="mira"?"Hat_CaptainCap":"Hat_Beanie"));
            }
            if(guest&&prefab.name=="CrewRig"){
                // Clearly temporary civilian colours on the accepted boat skeleton, without modifying shared materials.
                int index=guests.Count;Color[] colors={new(.68f,.27f,.24f),new(.22f,.51f,.49f),new(.73f,.48f,.24f),new(.32f,.42f,.62f)};
                foreach(var r in rig.GetComponentsInChildren<Renderer>()){
                    var mats=r.sharedMaterials;
                    for(int n=0;n<mats.Length;n++)if(mats[n]!=null&&(mats[n].name.Contains("Oilskin")||mats[n].name.Contains("Hull")||mats[n].name.Contains("Safety"))){var m=new Material(mats[n]);m.color=colors[index%colors.Length];guestMaterials.Add(m);mats[n]=m;}
                    r.sharedMaterials=mats;
                }
            }
            var prop=Spawn("GrilledFishPlate",new Vector3(0,.65f,.27f),Quaternion.identity,holder);prop.gameObject.SetActive(false);
            SetLayer(holder.gameObject);
            return new Actor{Root=holder,Rig=rig,Prop=prop,Last=holder.position,Phase=actors.Count*.27f+guests.Count*.17f};
        }
        void FrameCamera()
        {
            width=Screen.width;height=Screen.height;if(ServiceCamera==null)return;
            bool phone=width/(float)Math.Max(1,height)>1.9f;
            float top=phone?46f/390:78f/900,bottom=phone?72f/390:140f/900;
            // Full screen like the mockup (the sea runs under the HUD); a lens shift keeps the room between the bars.
            ServiceCamera.rect=new Rect(0,0,1,1);ServiceCamera.usePhysicalProperties=true;
            ServiceCamera.gateFit=Camera.GateFitMode.Vertical;ServiceCamera.lensShift=new Vector2(0,(top-bottom)*.5f);
            // Preserve vertical framing when HUD reduces the viewport; widen for the full 8x5 shell.
            float aspect=width*(1-top-bottom)/Math.Max(1,height); // overridden below by actual viewport aspect
            aspect=width/(height*(1-top-bottom));
            // Like the mockup: the 8 m room plus its quay edge (about 10.4 m) fills the width between the bars.
            float distance=ServiceCamera.transform.localPosition.magnitude;
            float inner=2*Mathf.Atan(5.2f/distance/aspect)*Mathf.Rad2Deg;
            ServiceCamera.fieldOfView=2*Mathf.Atan(Mathf.Tan(inner*.5f*Mathf.Deg2Rad)/(1-top-bottom))*Mathf.Rad2Deg;
        }
        public void SetSpeed(int speed){if(speed<0||speed>2)throw new ArgumentOutOfRangeException(nameof(speed));Speed=speed;}
        public bool Answer(bool yes)
        {
            var q=Snapshot.Question;if(q==null||Sim==null)return false;
            bool ok=Sim.ChooseSubstitute(q.GuestId,yes?Dish.Soup:(Dish?)null);Refresh(0);return ok;
        }
        // Unity screen coordinates (origin bottom left); convert Y for top-left IMGUI if needed.
        public Vector2 WorldToScreen(int itemId)
        {
            if(ServiceCamera==null||!items.TryGetValue(itemId,out var t))return new Vector2(-10000,-10000);
            var p=ServiceCamera.WorldToScreenPoint(t.position+Vector3.up*.9f);return p.z>0?new Vector2(p.x,p.y):new Vector2(-10000,-10000);
        }
        void Update()
        {
            if(Sim==null)return;
            if(DriveSimulation)Sim.Tick(Time.unscaledDeltaTime*Speed);
            Refresh(Time.unscaledDeltaTime*Speed);
        }
        public void Refresh(float dt)
        {
            if(Sim==null)return;if(width!=Screen.width||height!=Screen.height)FrameCamera();animationTime+=dt;
            foreach(var s in Sim.Staff){
                var a=actors[s.Id];var goal=TileToWorld(s.Position);a.Root.position=goal;
                Vector3 dir=goal-a.Last;if(dir.sqrMagnitude>.000001f)a.Root.rotation=Quaternion.Slerp(a.Root.rotation,Quaternion.LookRotation(dir),1-Mathf.Exp(-dt*12));
                bool carry=s.Action.StartsWith("Serve")||s.Action=="Clear table";
                a.Prop.gameObject.SetActive(carry);Animate(a,s.Walking?carry?"Carry":"Walk":s.Busy?"Bait":"Idle");a.Last=goal;
            }
            foreach(var g in Sim.Groups)for(int i=0;i<g.Guests.Count;i++){
                var order=g.Guests[i];bool active=g.Phase!=GroupPhase.NotArrived&&g.Phase!=GroupPhase.Gone;
                if(!guests.TryGetValue(order.Id,out var a)){if(!active)continue;a=MakeActor(order.Id.ToString(),true);guests[order.Id]=a;}
                a.Root.gameObject.SetActive(active);if(!active)continue;
                bool seated=g.TableUid!=0&&g.Phase!=GroupPhase.Seating&&g.Phase!=GroupPhase.Queue;
                Vector3 p=TileToWorld(new Vector2(Sim.Layout.Door.x,Sim.Layout.Door.y))+new Vector3((i%2)*.5f,0,.9f+(g.Id%4)*.45f);
                if(seated&&items.TryGetValue(g.TableUid,out var table))p=table.position+new Vector3(i%2==0?-.42f:.42f,0,(i/2)*.45f);
                if(a.Last==Vector3.zero||a.Root.position==RoomRoot.position)a.Root.position=p;
                a.Root.position=Vector3.MoveTowards(a.Root.position,p,Mathf.Max(.01f,dt)*GameData.WalkSpeed);
                a.Root.localRotation=Quaternion.Euler(0,seated?(i%2==0?90:270):180,0);
                // Existing boat work loop is a placeholder for eating; knees are folded on the same skeleton.
                Animate(a,seated?g.Phase==GroupPhase.Eating?"Eat":"Sit":"Walk");
                
                a.Last=a.Root.position;
            }
            Snapshot.Hour=Sim.Hour;Snapshot.CoinsTonight=Sim.Result.NetCoins;Snapshot.Popularity=Mathf.Max(0,Popularity+Sim.Result.PopularityGain);Snapshot.Finished=Sim.Finished;
            Snapshot.Staff.Clear();foreach(var s in Sim.Staff)Snapshot.Staff.Add(new StaffSnapshot{Id=s.Id,PortraitKey=s.Id,Job=s.Job,Task=s.Action,Busy=s.BusyProgress});
            Snapshot.Orders.Clear();foreach(var g in Sim.Groups.Where(g=>g.TableUid!=0&&g.Phase!=GroupPhase.Gone))foreach(var t in g.Tickets)Snapshot.Orders.Add(new OrderSnapshot{TableId=g.TableUid,GroupId=g.Id,Dish=t.Dish,Phase=g.Phase,Patience=Mathf.Clamp01(1-(Sim.Seconds-g.SeatedAt)/(RestaurantTuning.TablePatience+g.LastPatienceBoost))});
            Snapshot.Stock.Clear();foreach(var stock in Sim.Stock)foreach(var dish in RestaurantData.Dishes.Where(d=>!d.Staple&&d.Form==stock.Form&&Sim.Layout.CanCook(d.Id)))Snapshot.Stock.Add(new StockSnapshot{Dish=dish.Id,Species=stock.Species,Portions=stock.Count});
            Snapshot.BrokenAppliances.Clear();Snapshot.BrokenAppliances.AddRange(Sim.Broken.OrderBy(x=>x));
            var choice=Sim.Groups.SelectMany(g=>g.Tickets).FirstOrDefault(t=>t.Phase==TicketPhase.Choice);
            Snapshot.Question=choice==null?null:new QuestionSnapshot{GuestId=choice.Order.Id,Title="Offer fish soup instead?",Yes="Offer soup",No="Just drinks"};
        }
        void Animate(Actor actor,string pose)
        {
            AnimationClip clip=null;
            var anim=actor.Rig.GetComponentInChildren<Animation>();
            if(anim!=null)foreach(AnimationState state in anim)if(state.name.Split('|').Last()==pose){clip=state.clip;break;}
            if(clip==null&&!clips.TryGetValue(pose,out clip)&&!clips.TryGetValue("Idle",out clip))return;
            clip.SampleAnimation(actor.Rig.gameObject,Mathf.Repeat(animationTime+actor.Phase,Mathf.Max(.01f,clip.length)));
        }
        public void End()
        {
            foreach(var c in previousCameras)if(c!=null)c.enabled=true;previousCameras.Clear();
            if(RoomRoot!=null){if(Application.isPlaying)Destroy(RoomRoot.gameObject);else DestroyImmediate(RoomRoot.gameObject);}
            foreach(var m in guestMaterials)if(m!=null){if(Application.isPlaying)Destroy(m);else DestroyImmediate(m);}guestMaterials.Clear();
            items.Clear();actors.Clear();guests.Clear();clips.Clear();RoomRoot=null;ServiceCamera=null;Sim=null;
            Snapshot.Staff.Clear();Snapshot.Orders.Clear();Snapshot.Stock.Clear();Snapshot.BrokenAppliances.Clear();Snapshot.Question=null;
        }
        void OnDestroy()=>End();
    }
}

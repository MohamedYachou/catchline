using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using URP = UnityEngine.Rendering.Universal;

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
        // The room being drawn: the night's layout, or the player's own while arranging (no sim, no people).
        public RestaurantLayout Layout {get;private set;}
        public RestaurantSnapshot Snapshot {get;}=new();
        public Camera ServiceCamera {get;private set;}
        // Night cards the house has kept (gadget/dish ids) and tonight's night card: they show in the room.
        public readonly HashSet<string> Cards=new();public string NightCard;
        public int Speed {get;private set;}=1;
        public Transform RoomRoot {get;private set;}
        const int Layer=28;
        readonly Dictionary<int,Transform> items=new();
        readonly Dictionary<string,Actor> actors=new();
        readonly Dictionary<int,Actor> guests=new();
        readonly Dictionary<int,GuestWalk> guestWalks=new();
        readonly List<Camera> previousCameras=new();
        readonly Dictionary<string,AnimationClip> clips=new();
        readonly List<Material> guestMaterials=new();
        int width,height;
        float animationTime;
        VolumeProfile postProfile;
        ReflectionProbe reflectionProbe;
        bool ambientSaved;
        AmbientMode savedAmbientMode;DefaultReflectionMode savedReflectionMode;
        Color savedAmbientSky,savedAmbientEquator,savedAmbientGround,savedAmbientLight;
        float savedAmbientIntensity,savedReflectionIntensity;
        sealed class Actor
        {
            public Transform Root,Rig,Prop,Dish; public Vector3 Last,Velocity; public float Phase; public string DishName,PropName;
            public bool Placed,Arrived,Leaving,Departed; public float Fade=1; public Material[] FadeMaterials; public int RouteKey,Waypoint; public List<Vector3> Route;
            public Actor Ahead; public StaffTask CarryTask; public ServiceTicket CarryTicket;
        }
        sealed class GuestWalk
        {
            public readonly List<Vector3> Trail=new(); public bool Following;
            public readonly Dictionary<int,List<Vector3>> Routes=new();
        }
        Vector2 WorldTile(Vector3 p){var local=RoomRoot.InverseTransformPoint(p);return new Vector2(3.5f-local.x,2-local.z);}
        Vector2Int NearestFloor(Vector3 p)
        {
            var tile=WorldTile(p);Vector2Int best=Layout.Door;float distance=float.MaxValue;
            for(int y=0;y<Layout.Stage.Depth;y++)for(int x=Layout.Stage.KitchenWidth+1;x<Layout.Stage.TotalWidth;x++){
                var at=new Vector2Int(x,y);if(!Layout.Walkable(at))continue;float d=((Vector2)at-tile).sqrMagnitude;
                if(d<distance){distance=d;best=at;}}
            return best;
        }
        // A route belongs to the group's presentation, never to the service clock. Only the last step enters a chair.
        List<Vector3> GuestRoute(Vector3 from,Vector3 to,Transform table=null)
        {
            var start=NearestFloor(from);var end=NearestFloor(to);
            if(table!=null){
                var centre=TableBounds(table).center;var side=to-centre;side.y=0;float best=float.MaxValue;
                for(int y=0;y<Layout.Stage.Depth;y++)for(int x=Layout.Stage.KitchenWidth+1;x<Layout.Stage.TotalWidth;x++){
                    var tile=new Vector2Int(x,y);if(!Layout.Walkable(tile))continue;var p=TileToWorld(tile);var radial=p-centre;radial.y=0;
                    if(Vector3.Dot(radial,side)<=0||Layout.Path(start,tile)==null)continue;
                    float distance=(p-to).sqrMagnitude;if(distance<best){best=distance;end=tile;}}
            }
            var path=Layout.Path(start,end);var route=new List<Vector3>();
            if(path==null)return route;route.Add(TileToWorld(start));foreach(var tile in path)route.Add(TileToWorld(tile));route.Add(to);return route;
        }
        bool WalkGuest(Actor a,List<Vector3> route,float dt)
        {
            float budget=Mathf.Max(0,dt)*GameData.WalkSpeed;var from=a.Root.position;
            while(a.Waypoint<route.Count){
                var goal=route[a.Waypoint];float gap=Vector3.Distance(a.Root.position,goal);
                if(gap<=.001f){a.Waypoint++;continue;}if(budget<=0)break;
                float step=Mathf.Min(gap,budget);var next=Vector3.MoveTowards(a.Root.position,goal,step);
                // The door is a single file: a follower waits for the person ahead to clear the shared waypoint.
                if(a.Ahead!=null&&!a.Ahead.Departed&&(next-a.Ahead.Root.position).sqrMagnitude<.48f*.48f&&(next-a.Ahead.Root.position).sqrMagnitude<(a.Root.position-a.Ahead.Root.position).sqrMagnitude)break;
                a.Root.position=next;budget-=step;
                if(step<gap)break;
            }
            var dir=a.Root.position-from;dir.y=0;bool moving=dir.sqrMagnitude>.0000001f;
            if(moving)a.Root.rotation=Quaternion.LookRotation(dir);return moving;
        }
        void Leave(Actor a,float dt)
        {
            if(!a.Leaving){
                a.Leaving=true;a.Route=GuestRoute(a.Root.position,TileToWorld(Layout.Door));a.Waypoint=0;
                a.Route.Add(TileToWorld(Layout.Door)+RoomRoot.forward*1.7f);
                PlaceDish(a,null,null,0);
            }
            bool moving=WalkGuest(a,a.Route,dt);Animate(a,moving?"Walk":"Idle");
            // At the outer threshold, dissolve only this visitor's instances; the shared guest palette stays intact.
            if(a.Waypoint>=a.Route.Count-1){
                if(a.FadeMaterials==null){var mats=new List<Material>();foreach(var r in a.Rig.GetComponentsInChildren<Renderer>()){
                    var copies=r.sharedMaterials.Select(m=>m==null?null:new Material(m)).ToArray();
                    foreach(var m in copies)if(m!=null){m.SetFloat("_Surface",1);m.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);m.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);m.SetFloat("_ZWrite",0);
                        m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");m.renderQueue=(int)RenderQueue.Transparent;guestMaterials.Add(m);mats.Add(m);}r.sharedMaterials=copies;}a.FadeMaterials=mats.ToArray();}
                a.Fade=Mathf.Max(0,a.Fade-dt*2);foreach(var m in a.FadeMaterials){foreach(string property in new[]{"_BaseColor","_Color"})if(m.HasProperty(property)){var c=m.GetColor(property);c.a=a.Fade;m.SetColor(property,c);}}
            }
            if(a.Fade<=0&&a.Waypoint==a.Route.Count){a.Departed=true;a.Root.gameObject.SetActive(false);}
        }
        // Sample the host's actual footsteps, so a trailing file takes the same corners instead of cutting a table.
        void Escort(ServiceGroup g,GuestWalk walk)
        {
            var host=Sim.Staff.FirstOrDefault(s=>s.Action=="Seat group"&&s.Task.Current!=null&&s.Task.Legs.Count==0);
            if(host==null||!actors.TryGetValue(host.Id,out var actor))return;
            var table=Layout.Active.First(i=>i.Uid==g.TableUid);var access=Layout.Access(table,Layout.Door);
            if(!access.HasValue||host.Target!=access.Value)return;
            if(!walk.Following){walk.Following=true;walk.Trail.Add(TileToWorld(Layout.Door));}
            var p=actor.Root.position;if(Vector3.Distance(walk.Trail[walk.Trail.Count-1],p)>.08f)walk.Trail.Add(p);
        }
        static List<Vector3> Trailing(List<Vector3> trail,float behind)
        {
            var route=new List<Vector3>(trail);while(route.Count>1&&behind>0){int last=route.Count-1;float length=Vector3.Distance(route[last],route[last-1]);
                if(length<=behind){behind-=length;route.RemoveAt(last);}else{route[last]=Vector3.MoveTowards(route[last],route[last-1],behind);break;}}
            return route;
        }
        static readonly Dictionary<ItemId,string> Models=new(){
            [ItemId.Stove]="Stove",[ItemId.SoupKettle]="SoupKettle",[ItemId.PrepCounter]="PrepCounter",
            [ItemId.Fridge]="FridgeV2",[ItemId.CoffeeMachine]="CoffeeBar",
            [ItemId.Table2]="TableFor2",[ItemId.Table4]="TableFor4",[ItemId.Booth6]="Booth",
            [ItemId.TerraceTable]="TerraceTable",[ItemId.Reception]="ReceptionDesk",[ItemId.Sink]="SinkDishRack",
            [ItemId.Fryer]="Fryer",[ItemId.Oven]="Oven",[ItemId.Grill]="Grill",[ItemId.Steamer]="Steamer",
            [ItemId.BarCounter]="PassCounter",[ItemId.Plant]="PlantPot1",[ItemId.Lamp]="LampPost",
            [ItemId.Trophy]="Trophy",[ItemId.Net]="Net",[ItemId.Chart]="Chart",[ItemId.Jukebox]="Jukebox",[ItemId.DrinksFridge]="DrinksFridge"
        };
        // Until KitchenKit2 is in a build: the stand-ins those items used before.
        static readonly Dictionary<string,string> StandIn=new(){["Grill"]="Stove",["Steamer"]="SoupKettle",["Trophy"]="PlantPot2",["Net"]="PlantPot2",
            ["Chart"]="PlantPot2",["Jukebox"]="CoffeeBar",["DrinksFridge"]="FridgeV2",["BigFridge"]="FridgeV2",["ReliableStove"]="Stove"};
        // S8 upgrades show in the room: the big fridge and the reliable stove replace their stations' models.
        string ModelFor(ItemId id,string model)
        {
            if(id==ItemId.Fridge&&Layout.HasUpgrade("BigFridge"))model="BigFridge";
            if(id==ItemId.Stove&&Layout.HasUpgrade("ReliableStove"))model="ReliableStove";
            return Model(model)!=null||!StandIn.TryGetValue(model,out var old)?model:old;
        }
        GameObject Model(string name)=>ArtLibrary.Get()?.M("Restaurant_"+name);
        // Some kit pieces are authored with their doors/front on the wrong axis, so they face the back wall when
        // placed along it. A per-model yaw turns the front back toward the room (the crew), applied in the piece's frame.
        static readonly Dictionary<string,float> FacingYaw=new(){["FridgeV2"]=180,["BigFridge"]=180,["DrinksFridge"]=180};
        Transform Spawn(string name,Vector3 p,Quaternion rotation,Transform parent=null)
        {
            var prefab=Model(name);
            if(prefab==null)throw new InvalidOperationException("Restaurant asset missing: "+name+". Rebuild ArtLibrary after importing the Restaurant folder.");
            if(FacingYaw.TryGetValue(name,out var yaw))rotation*=Quaternion.Euler(0,yaw,0);
            // A model exported with its axis turn on the root keeps that turn under the layout's own (else it lies on its side).
            var spawned=ArtLibrary.Spawn(prefab,parent??RoomRoot,p,rotation*prefab.transform.localRotation).transform;
            Emissive(spawned);
            return spawned;
        }
        // Light fixtures carry their lit element on a separate *_Glow material; make it emit so the grade's bloom
        // reads it as warm lamplight (the atlas-shader room pieces glow via their B channel instead).
        void Emissive(Transform t)
        {
            foreach(var r in t.GetComponentsInChildren<Renderer>(true)){
                var mats=r.sharedMaterials;bool changed=false;
                for(int i=0;i<mats.Length;i++){
                    if(mats[i]==null||!mats[i].name.Contains("Glow"))continue;
                    var m=new Material(mats[i]);m.EnableKeyword("_EMISSION");
                    m.globalIlluminationFlags=MaterialGlobalIlluminationFlags.RealtimeEmissive;
                    if(m.HasProperty("_EmissionColor"))m.SetColor("_EmissionColor",new Color(1f,.72f,.42f)*2.6f);
                    guestMaterials.Add(m);mats[i]=m;changed=true;
                }
                if(changed)r.sharedMaterials=mats;
            }
        }
        // Tile x runs kitchen-to-door; the camera looks down -z, so world +x is screen left. The V4 room (kitchen left,
        // jetty right, like the mockups) is laid out that way, so tile x maps to -x.
        public Vector3 TileToWorld(Vector2 tile,float y=.04f)=>RoomRoot.TransformPoint(new Vector3(3.5f-tile.x,y,2-tile.y));
        static int guestStart=-7;
        public void Begin(RestaurantSim sim)
        {
            if(sim==null)throw new ArgumentNullException(nameof(sim));
            guestStart=(guestStart+7)%20; // night 1 opens with Ada, later nights bring the others (GUESTS-3 among them)
            Show(sim.Layout,sim);
        }
        // Arrange mode: the same dressed room and camera, empty of crew and guests.
        public void Show(RestaurantLayout layout,RestaurantSim sim=null)
        {
            if(layout==null)throw new ArgumentNullException(nameof(layout));
            End();Sim=sim;Layout=layout;Speed=1;animationTime=0;frameHalfWidth=7;cosyLamps.Clear();
            RoomRoot=new GameObject("Restaurant night (quay)").transform;
            RoomRoot.position=HarbourQuayOrigin;
            try {
                // Each stage's dressed room (Stage2Bistro.. from Codex 2), V4 until that stage's room is imported.
                roomName=StageRooms[Math.Max(1,Math.Min(4,layout.Stage.Stage))-1];
                var dressed=Resources.Load<GameObject>("Restaurant/"+roomName);
                if(dressed==null){roomName=StageRooms[0];dressed=Resources.Load<GameObject>("Restaurant/"+roomName);}
                Transform room=null;
                if(dressed!=null){
                    room=ArtLibrary.Spawn(dressed,RoomRoot,Vector3.zero,Quaternion.identity).transform;
                    foreach(var t in room.GetComponentsInChildren<Transform>(true))if(t!=room&&LayoutPlaced(t.name))t.gameObject.SetActive(false);
                }else Spawn("RoomShell",Vector3.zero,Quaternion.identity);
                // Codex 1's pier (RESTAURANT-PIER-1; Mo 10-28: "at the edge of a pier, not in the middle of the water"): the
                // stage's deck, the quay with its houses and lamps, moored boats and clutter. One Pier_S* deck shows at a time.
                var pierModel=Resources.Load<GameObject>("Restaurant/RestaurantPier");
                pier=null;
                if(pierModel!=null){
                    pier=ArtLibrary.Spawn(pierModel,RoomRoot,Vector3.zero,Quaternion.identity).transform;
                    string deck="Pier_S"+(Array.IndexOf(StageRooms,roomName)+1);
                    foreach(var t in pier.GetComponentsInChildren<Transform>(true))if(t.name.StartsWith("Pier_S"))t.gameObject.SetActive(t.name==deck);
                    // Codex 2's catch-of-the-day board out front beside the entrance, where the queue reads it (its first spot on
                    // the quay approach sat under the stock panel).
                    if(Model("CatchBoard")!=null)Spawn("CatchBoard",new Vector3(-4.75f,0,3.1f),Quaternion.identity);
                }
                foreach(var item in layout.Active){
                    if(!Models.TryGetValue(item.Id,out var model))continue;
                    model=ModelFor(item.Id,model);
                    float x=item.X+(item.Rotated?1:RestaurantData.Get(item.Id).Width)*.5f-.5f;
                    var pos=new Vector3(3.5f-x,.04f,2-item.Y);
                    var t=Spawn(model,pos,Quaternion.Euler(0,item.Rotated?-90:0,0));items.Add(item.Uid,t);
                    if(RestaurantData.Get(item.Id).Seats>0){var top=TableBounds(t);Spawn(Model("TableCandle")!=null?"TableCandle":"TableLantern",new Vector3(top.center.x,top.max.y,top.center.z),Quaternion.identity);
                        // Cosy lighting: a pendant over every table (base height from its footprint), lit warm below.
                        // Mo 10-27: a warm glowing pendant hangs over every table so the room reads as lit; the old
                        // cosy-lamp upgrade path remains only until the new PendantLamp is imported.
                        string pendant=Model("PendantLamp")!=null?"PendantLamp":(layout.HasUpgrade("CosyLighting")&&Model("CosyPendantLamp")!=null?"CosyPendantLamp":null);
                        if(pendant!=null){Spawn(pendant,new Vector3(top.center.x,pendant=="PendantLamp"?2.3f:1.65f,top.center.z),Quaternion.identity);cosyLamps.Add(new Vector3(top.center.x,1.6f,top.center.z));}}
                }
                // V4's own small dressing (plants, crates, lanterns) must not stand in a chair the layout put there.
                if(room!=null){
                    var placed=items.Values.SelectMany(t=>t.GetComponentsInChildren<Renderer>()).Select(r=>{var b=r.bounds;b.Expand(new Vector3(-.1f,0,-.1f));return b;}).ToList();
                    foreach(var r in room.GetComponentsInChildren<Renderer>()){var b=r.bounds;
                        if(b.size.x<1.5f&&b.size.z<1.5f&&placed.Any(p=>p.Intersects(b)))r.gameObject.SetActive(false);}
                }
                if(dressed==null){
                    Spawn("PassCounter",new Vector3(-.5f,.04f,0),Quaternion.Euler(0,90,0));
                    Spawn("TrashCan",new Vector3(-2.7f,.04f,2.05f),Quaternion.identity);
                    Spawn("PlantPot1",new Vector3(3.65f,.04f,-.5f),Quaternion.identity);
                }
                // The dressed room shares the kit's atlas; take the material from a kit piece the layout placed.
                if(room!=null){
                    Material kit=null;
                    foreach(var r in RoomRoot.GetComponentsInChildren<Renderer>())if(!r.transform.IsChildOf(room)){foreach(var m in r.sharedMaterials)if(m!=null&&m.shader.name=="Catchline/RestaurantAtlas"){kit=m;break;}if(kit!=null)break;}
                    if(kit!=null)foreach(var r in room.GetComponentsInChildren<Renderer>(true).Concat(pier!=null?pier.GetComponentsInChildren<Renderer>(true):Array.Empty<Renderer>())){var mats=r.sharedMaterials;for(int n=0;n<mats.Length;n++)mats[n]=kit;r.sharedMaterials=mats;}
                }
                CrewAnim.Fill(clips,ArtLibrary.Get().CrewClips);
                if(sim!=null)foreach(var staff in sim.Staff)actors[staff.Id]=MakeActor(staff.Id,false);
                ServiceCamera=new GameObject("Restaurant camera").AddComponent<Camera>();
                ServiceCamera.transform.SetParent(RoomRoot,false);
                ServiceCamera.clearFlags=CameraClearFlags.SolidColor;ServiceCamera.backgroundColor=new Color(.05f,.12f,.22f); // a deeper dusk sea so the warm room glows against it
                ServiceCamera.nearClipPlane=.1f;ServiceCamera.farClipPlane=70;ServiceCamera.cullingMask=1<<Layer;ServiceCamera.depth=30;
                // V3's camera study: 38 degree pitch, -2 degree yaw from the quay, 58mm equivalent.
                ServiceCamera.transform.localPosition=new Vector3(-.598f,13.359f,17.088f);
                ServiceCamera.transform.localRotation=Quaternion.Euler(38,178,0);
                // Stage 1 reads Codex 2's room-look recipe unmirrored (its lights were placed in the V4 room's own axes, verified r31).
                var stageLights=roomName==StageRooms[0]?RecipeLights(roomName,false):StageRecipe(roomName);
                ServiceCamera.orthographic=false;ServiceCamera.fieldOfView=21.9542f;
                // Match the sea/harbour cameras: SMAA and post so the room is not softer than the rest of the game.
                var camData=ServiceCamera.gameObject.AddComponent<UnityEngine.Rendering.Universal.UniversalAdditionalCameraData>();
                camData.renderPostProcessing=true;
                // The grade Volume and the room sit on the restaurant layer; the camera must read volumes there, not just Default.
                camData.volumeLayerMask=(1<<Layer)|1;camData.requiresDepthTexture=true;
                camData.antialiasing=UnityEngine.Rendering.Universal.AntialiasingMode.SubpixelMorphologicalAntiAliasing;
                camData.antialiasingQuality=UnityEngine.Rendering.Universal.AntialiasingQuality.High;
                ServiceCamera.allowMSAA=true;
                foreach(var c in Camera.allCameras)if(c!=ServiceCamera&&c.enabled){previousCameras.Add(c);c.enabled=false;}
                // Codex 2's V4 night recipe (Stage1V4/lighting.json): blue dusk over warm lanterns, window wash and the jetty lamp.
                AddLight(new Vector3(-4,9,6),new Color(.39f,.6f,1),.42f,true);
                foreach(var lamp in cosyLamps)AddLight(lamp,new Color(1,.78f,.48f),1.5f,false,3f); // room-look3: warm pools on the tables, bright enough for the grade's bloom
                if(stageLights!=null)foreach(var (pos,watts) in stageLights)AddLight(pos,new Color(1,.8f,.5f),Mathf.Clamp(watts/75f,.16f,1.15f),false,Mathf.Lerp(1.6f,5f,Mathf.InverseLerp(8,75,watts)));
                else foreach(var (x,y,z,watts) in NightLights)AddLight(new Vector3(x,y,z),new Color(1,.8f,.5f),Mathf.Clamp(watts/75f,.16f,1.15f),false,Mathf.Lerp(1.6f,5f,Mathf.InverseLerp(8,75,watts)));
                // The quay's lamp posts (Codex 1's recipe is already in the room's mirrored axes): warm pools along the quay behind the room.
                if(pier!=null)foreach(var (pos,watts) in RecipeLights("RestaurantPier",false)??new())AddLight(pos,new Color(1,.7f,.4f),.9f,false,4f);
                // The player build drops the material's atlas reference; bind the painted atlas from Resources.
                var atlas=Resources.Load<Texture2D>("RestaurantAtlas/Restaurant_BaseColor");var surface=Resources.Load<Texture2D>("RestaurantAtlas/Restaurant_Surface");
                foreach(var r in RoomRoot.GetComponentsInChildren<Renderer>(true))foreach(var m in r.sharedMaterials)
                    if(m!=null&&m.shader.name=="Catchline/RestaurantAtlas"&&m.GetTexture("_BaseMap")==null){m.SetTexture("_BaseMap",atlas);m.SetTexture("_SurfaceMap",surface);}
                AddSea();
                BuildMood();
                SetLayer(RoomRoot.gameObject);
                if(reflectionProbe!=null)reflectionProbe.RenderProbe();
                FrameCamera();Refresh(0);
            }catch{End();throw;}
        }
        // Mo 10-27: the room read flat and bland. An evening grade (filmic contrast, warm highlights over cool dusk shadows,
        // bloom on the lanterns, soft vignette and fine grain), shaped ambient and a reflection probe give it depth and life.
        void BuildMood()
        {
            // Shaped ambient the atlas shader samples (SampleSH), instead of the flat project default. Global, so saved and put back in End().
            savedAmbientMode=RenderSettings.ambientMode;savedAmbientSky=RenderSettings.ambientSkyColor;savedAmbientEquator=RenderSettings.ambientEquatorColor;
            savedAmbientGround=RenderSettings.ambientGroundColor;savedAmbientLight=RenderSettings.ambientLight;savedAmbientIntensity=RenderSettings.ambientIntensity;
            savedReflectionIntensity=RenderSettings.reflectionIntensity;savedReflectionMode=RenderSettings.defaultReflectionMode;ambientSaved=true;
            RenderSettings.ambientMode=AmbientMode.Trilight;
            RenderSettings.ambientSkyColor=new Color(.13f,.17f,.26f);     // dim dusk over the sea
            RenderSettings.ambientEquatorColor=new Color(.17f,.14f,.12f); // low warm bounce off the room
            RenderSettings.ambientGroundColor=new Color(.04f,.035f,.03f); // dark boards
            RenderSettings.ambientIntensity=1f;RenderSettings.reflectionIntensity=1f;

            // A realtime probe in the room centre so plates, glass, metal and polished wood catch the lanterns and the dusk.
            var probeGo=new GameObject("Room reflections");probeGo.transform.SetParent(RoomRoot,false);probeGo.transform.localPosition=new Vector3(0,1.6f,0);
            reflectionProbe=probeGo.AddComponent<ReflectionProbe>();
            reflectionProbe.mode=ReflectionProbeMode.Realtime;reflectionProbe.refreshMode=ReflectionProbeRefreshMode.ViaScripting;
            reflectionProbe.timeSlicingMode=ReflectionProbeTimeSlicingMode.NoTimeSlicing;reflectionProbe.cullingMask=1<<Layer;
            reflectionProbe.clearFlags=ReflectionProbeClearFlags.SolidColor;reflectionProbe.backgroundColor=new Color(.05f,.12f,.22f);
            reflectionProbe.size=new Vector3(26,10,20);reflectionProbe.boxProjection=false;reflectionProbe.resolution=128;reflectionProbe.hdr=true;reflectionProbe.intensity=1f;

            // The evening grade.
            postProfile=ScriptableObject.CreateInstance<VolumeProfile>();
            var tm=postProfile.Add<URP.Tonemapping>();tm.mode.Override(URP.TonemappingMode.Neutral);
            var ca=postProfile.Add<URP.ColorAdjustments>();ca.postExposure.Override(.12f);ca.contrast.Override(14f);ca.colorFilter.Override(new Color(1f,.965f,.9f));ca.saturation.Override(12f);
            var wb=postProfile.Add<URP.WhiteBalance>();wb.temperature.Override(10f);wb.tint.Override(2f);
            var sp=postProfile.Add<URP.SplitToning>();sp.shadows.Override(new Color(.26f,.38f,.56f));sp.highlights.Override(new Color(1f,.74f,.42f));sp.balance.Override(-8f);
            var bl=postProfile.Add<URP.Bloom>();bl.threshold.Override(.75f);bl.intensity.Override(1.15f);bl.scatter.Override(.72f);bl.tint.Override(new Color(1f,.86f,.66f));bl.highQualityFiltering.Override(true);
            var vg=postProfile.Add<URP.Vignette>();vg.intensity.Override(.34f);vg.smoothness.Override(.78f);vg.color.Override(new Color(.03f,.025f,.045f));
            var fg=postProfile.Add<URP.FilmGrain>();fg.type.Override(URP.FilmGrainLookup.Thin1);fg.intensity.Override(.16f);fg.response.Override(.8f);
            // (Depth of field removed: Mo 10-27 - it hazed the whole room, which sits farther from the camera than the sea estimate assumed.)

            var volGo=new GameObject("Evening grade");volGo.transform.SetParent(RoomRoot,false);
            var vol=volGo.AddComponent<Volume>();vol.isGlobal=true;vol.priority=100;vol.sharedProfile=postProfile;
        }
        readonly List<Vector3> cosyLamps=new();
        static readonly string[] StageRooms={"Stage1V4","Stage2Bistro","Stage3Restaurant","Stage4Seafood"};
        string roomName;
        Transform pier;
        float frameHalfWidth=7;
        [Serializable] class RecipeLight{public string name,type;public float[] position_unity_m;public float blender_power;}
        [Serializable] class Recipe{public RecipeLight[] lights;}
        [Serializable] class RecipeCamera{public string file;public float[] position_unity_m;}
        [Serializable] class RecipeCameras{public RecipeCamera[] c;}
        // A later stage's camera and practicals from Codex 2's final-cameras.json / lighting.json (copied beside the room
        // as <room>-cameras / <room>-lighting). Their "Unity" axes skip the FBX import's X mirror, so X flips here.
        List<(Vector3 pos,float watts)> StageRecipe(string room)
        {
            var cams=Resources.Load<TextAsset>("Restaurant/"+room+"-cameras");
            var cam=cams==null?null:JsonUtility.FromJson<RecipeCameras>("{\"c\":"+cams.text+"}").c.FirstOrDefault(c=>c.file.Contains("1440"));
            if(cam!=null){var p=cam.position_unity_m;ServiceCamera.transform.localPosition=new Vector3(-p[0],p[1],p[2]);
                frameHalfWidth=7*ServiceCamera.transform.localPosition.magnitude/new Vector3(-.598f,13.359f,17.088f).magnitude;}
            return RecipeLights(room,true);
        }
        List<(Vector3 pos,float watts)> RecipeLights(string room,bool mirrorX)
        {
            var lights=Resources.Load<TextAsset>("Restaurant/"+room+"-lighting");
            if(lights==null)return null;
            // Look3_TablePool* sit over V4's own tables; the layout places tables itself and lights each one (cosyLamps).
            return JsonUtility.FromJson<Recipe>(lights.text).lights.Where(l=>l.type=="POINT"&&l.position_unity_m?.Length==3&&!l.name.StartsWith("Look3_TablePool"))
                .Select(l=>(new Vector3(mirrorX?-l.position_unity_m[0]:l.position_unity_m[0],l.position_unity_m[1],l.position_unity_m[2]),l.blender_power)).ToList();
        }
        // V4 pieces that the layout places itself (stations, tables and what is set on them).
        static readonly string[] LayoutPieces={"PrepCounter","Stove","SoupKettle","KettleStand","FridgeV2","Oven","Fryer","SinkDishRack","CoffeeBar","ReceptionDesk",
            "Booth","DiningTwo_","DiningFour","TerraceTable","TerraceParasol","Candle_","PlaceSetting_","Glass_","V4_Plate_","V4_Glass_","PlateDirty","CoffeeCup","DinnerSoup","DinnerPlate"};
        static bool LayoutPlaced(string name){if(name.StartsWith("EXPORT_"))name=name.Substring(7);foreach(var p in LayoutPieces)if(name==p||(p.EndsWith("_")&&name.StartsWith(p)))return true;return false;}
        static readonly (float x,float y,float z,float watts)[] NightLights={
            (-3.35f,1.49f,-1.99f,74.8f),
            (-0.70f,1.49f,-1.99f,74.8f),
            (1.02f,1.49f,-1.99f,74.8f),
            (3.42f,1.49f,-1.99f,74.8f),
            (0.65f,0.98f,1.35f,8.1f),
            (2.25f,0.98f,1.35f,8.1f),
            (1.35f,0.98f,-0.48f,8.1f),
            (2.15f,0.98f,-1.74f,8.1f),
            (-2.85f,0.90f,3.48f,8.1f),
            (-3.78f,1.14f,-2.27f,32.2f),
            (0.15f,1.14f,-2.30f,32.2f),
            (3.70f,1.14f,-2.27f,32.2f),
            (3.82f,1.14f,1.10f,32.2f),
            (-3.83f,1.14f,2.40f,32.2f),
            (2.15f,1.14f,2.40f,32.2f),
            (-2.65f,0.60f,2.95f,32.2f),
            (-0.60f,0.60f,2.95f,32.2f),
            (1.45f,0.60f,2.95f,32.2f),
            (1.35f,1.34f,3.12f,74.8f)
        };
        void AddLight(Vector3 position,Color color,float intensity,bool sun,float range=6)
        {
            var go=new GameObject(sun?"Blue dusk":"Warm practical");go.transform.SetParent(RoomRoot,false);go.transform.localPosition=position;
            var l=go.AddComponent<Light>();l.type=sun?LightType.Directional:LightType.Point;l.color=color;l.intensity=intensity;l.range=range;l.cullingMask=1<<Layer;
            if(sun){go.transform.localRotation=Quaternion.Euler(42,-25,0);l.shadows=LightShadows.Soft;l.shadowStrength=.68f;}
        }
        // Codex 2's guest palettes (Guests/build-metrics.json: skin, hair, shirt, trousers). Spawning maps the guests' crew-named
        // materials onto the shared crew palette, which dressed every guest in deckhand teal; each guest gets its own colours back.
        static readonly string[,] GuestPalette={
            {"#C58C60","#7B4530","#BA5968","#253F58"},{"#8A5238","#292C2B","#F0DDAB","#254960"},{"#E5B38E","#C79842","#267879","#353E56"},
            {"#B87550","#4A302A","#596D89","#2C3D51"},{"#8E6049","#999C98","#B68542","#344F64"},{"#D6A477","#94603C","#364B6B","#8A6C50"}};
        static readonly string[] GuestSource={"#B9784B","#50392E","#168F9F","#173F57"}; // M_Skin, M_HairChestnut, M_SeaTeal, M_HullNavy
        readonly Dictionary<(int,int),Material> guestTints=new();
        void TintGuest(Transform rig,int index)
        {
            foreach(var r in rig.GetComponentsInChildren<Renderer>(true)){
                var mats=r.sharedMaterials;
                for(int n=0;n<mats.Length;n++){
                    if(mats[n]==null)continue;
                    // Spawning has already swapped in the shared palette material, so match on its colour.
                    int slot=-1;for(int k=0;k<GuestSource.Length;k++){ColorUtility.TryParseHtmlString(GuestSource[k],out var src);var have=mats[n].color;
                        if(Mathf.Abs(have.r-src.r)+Mathf.Abs(have.g-src.g)+Mathf.Abs(have.b-src.b)<.06f){slot=k;break;}}
                    if(slot<0)continue;
                    if(!guestTints.TryGetValue((index,slot),out var m)){
                        m=new Material(mats[n]);ColorUtility.TryParseHtmlString(GuestPalette[index,slot],out var c);m.color=c;guestTints[(index,slot)]=m;guestMaterials.Add(m);
                    }
                    mats[n]=m;
                }
                r.sharedMaterials=mats;
            }
        }
        // Codex 2's painted night sea (Restaurant/Sea, placed as in its V4 check): ripples at the water line, lantern streaks over them.
        void AddSea()
        {
            var shader=Resources.Load<Shader>("Restaurant/RestaurantSea");if(shader==null)return;
            Material Make(string tex,bool additive,float repeat,float gain,float shimmer){
                var m=new Material(shader);m.SetTexture("_BaseMap",Resources.Load<Texture2D>("Restaurant/"+tex));m.SetFloat("_Repeat",repeat);m.SetFloat("_Gain",gain);m.SetFloat("_Shimmer",shimmer);
                if(additive){m.SetFloat("_Src",(float)UnityEngine.Rendering.BlendMode.One);m.SetFloat("_Dst",(float)UnityEngine.Rendering.BlendMode.One);m.SetFloat("_ZWrite",0);m.SetVector("_Drift",Vector4.zero);m.renderQueue=3000;}
                guestMaterials.Add(m);return m;
            }
            void Quad(string name,Vector3 at,Vector2 size,Material m){
                var q=GameObject.CreatePrimitive(PrimitiveType.Quad);q.name=name;Destroy(q.GetComponent<Collider>());
                q.transform.SetParent(RoomRoot,false);q.transform.localPosition=at;q.transform.localRotation=Quaternion.Euler(90,0,0);q.transform.localScale=new Vector3(size.x,size.y,1);
                q.GetComponent<MeshRenderer>().sharedMaterial=m;
            }
            // sea1c is brighter than the old tile: lower gain keeps the room dominant (R3-02).
            Quad("Night sea",new Vector3(0,-.57f,0),new Vector2(90,90),Make("NightWater",false,8,.32f,0));
            // With the pier, the streaks lie on open water just past the deck's front edge (Unity Z 5.05), not under the planks.
            Quad("Lantern streaks",new Vector3(-.6f,-.558f,pier!=null?6.9f:4.5f),new Vector2(11.2f,3.3f),Make("LanternStreaks",true,0,.8f,.25f));
        }
        static void SetLayer(GameObject go){foreach(var t in go.GetComponentsInChildren<Transform>(true))t.gameObject.layer=Layer;}
        // Mo 10-26: classic restaurant clothes per job; women in dresses/tops, men in suits, Mira the best-dressed host.
        static readonly HashSet<string> Women=new(){"mira","noor","tess","rosa","ana","lise","ines","tove"};
        (string outfit,string hat) Wardrobe(string id)
        {
            var staff=Sim?.Staff.FirstOrDefault(s=>s.Id==id);
            if(id=="mira")return("Outfit_HostFormal","Hat_HairUpClip");
            switch(staff?.Job??Job.Helper){
                case Job.Reception:return(Women.Contains(id)?"Outfit_Host":"Outfit_HelperSuit",null);
                case Job.Cook:return("Outfit_CookWhites","Hat_Toque");
                case Job.Waiter:return(Women.Contains(id)?"Outfit_WaiterSkirt":"Outfit_WaiterSuit",null);
                case Job.Barista:return("Outfit_Barista",null);
                case Job.Handyman:return("Outfit_Handyman",null);
                default:return(id=="captain"||!Women.Contains(id)?"Outfit_HelperSuit":"Outfit_WaiterSkirt",null);
            }
        }
        // Codex 2's table dishes (Dishes/Restaurant_Dish_*.fbx, pivot at the table contact).
        // Codex 2's SERVICE-PROPS-1 plates (Dish_FishAndChips, _Platter, ...) where imported, else the nearest older plate.
        string DishModel(Dish d)
        {
            string own=d switch{Dish.FishAndChips=>"Dish_FishAndChips",Dish.Platter=>"Dish_Platter",Dish.Crab=>"Dish_Crab",Dish.Calamari=>"Dish_Calamari",
                Dish.Fries=>"Dish_Fries",Dish.Bread=>"Dish_Bread",Dish.Beer=>"Dish_Beer",Dish.Tea=>"Dish_Tea",Dish.IceCream=>"Dish_IceCream",_=>null};
            return own!=null&&Model(own)!=null?own:OldDishModel(d);
        }
        static string OldDishModel(Dish d)=>d switch{
            Dish.Soup=>"Dish_FishSoup",Dish.Coffee or Dish.Tea or Dish.Bread=>"Dish_CoffeeBiscuits",Dish.Lemonade or Dish.Beer=>"Dish_Lemonade",
            Dish.PanFish or Dish.Platter or Dish.FishAndChips or Dish.Fries=>"Dish_FilletsLemon",_=>"Dish_GrilledFish"};
        // Kit pivots sit off the mesh once rotated, so seats and plates go by the table's rendered bounds.
        static Bounds TableBounds(Transform table)
        {
            var rs=table.GetComponentsInChildren<Renderer>();if(rs.Length==0)return new Bounds(table.position,Vector3.zero);
            var b=rs[0].bounds;foreach(var r in rs)b.Encapsulate(r.bounds);return b;
        }
        // The kit tables seat guests front and back (the round chair back faces the camera), pairs side by side.
        static Vector3 Seat(int i)=>new Vector3((i/2)*.5f-(i>=2?.25f:0),0,i%2==0?.38f:-.38f);
        void PlaceDish(Actor a,Dish? dish,Transform table,int seat)
        {
            string name=dish==null||table==null?null:DishModel(dish.Value);
            if(name!=a.DishName){
                if(a.Dish!=null)Destroy(a.Dish.gameObject);a.Dish=null;a.DishName=name;
                if(name!=null&&Model(name)!=null){a.Dish=Spawn(name,Vector3.zero,Quaternion.identity,RoomRoot);SetLayer(a.Dish.gameObject);}
            }
            if(a.Dish==null)return;
            var b=TableBounds(table);
            var s=Seat(seat);a.Dish.position=new Vector3(b.center.x+s.x,b.max.y,b.center.z+s.z*.4f);
        }
        Actor MakeActor(string id,bool guest,bool critic=false)
        {
            var holder=new GameObject((guest?"Guest ":"Staff ")+id).transform;holder.SetParent(RoomRoot,false);
            var lib=ArtLibrary.Get();string[] civilians={"Ada","Ben","Cora","Dan","Edda","Finn","Gus","Hazel","Ivo","Jonas","Kai","Lena","Marta","Nils","Pia","Greta","Henrik","Zola","Vera","Anton"}; // GUESTS-3 bring their own colours
            int gi=(guests.Count+guestStart)%civilians.Length; // each night starts further along the roster
            // Staff wear their own Quaternius human puppet (file named after the crew id, e.g. mira.fbx); the
            // generic captain borrows Mira's. Guests, and any crew without a delivered puppet, fall back as before.
            string staffKey=id=="captain"?"mira":id;
            var staffPuppet=!guest?lib?.M(staffKey):null;
            var prefab=guest?(critic?lib?.M("Restaurant_Guest_Critic"):null)??lib?.M("Restaurant_Guest_"+civilians[gi]):staffPuppet??lib?.M("CrewRig_Restaurant")??lib?.M("CrewRig");
            bool boatMira=!guest&&staffPuppet==null; // old blob rig in use -> keep the legacy outfit/hat toggles
            if(prefab==null)throw new InvalidOperationException("Boat CrewRig is missing from ArtLibrary");
            var rig=ArtLibrary.Spawn(prefab,holder,Vector3.zero,Quaternion.identity).transform;
            if(!guest&&staffPuppet!=null)CrewAnim.FitHeight(rig.gameObject); // human puppet -> normalise to room height
            foreach(var a in rig.GetComponentsInChildren<Animation>())a.enabled=false;
            foreach(var a in rig.GetComponentsInChildren<Animator>())a.enabled=false;
            var (outfit,hat)=guest?(null,null):boatMira?("Outfit_Deckhand","Hat_Beanie"):Wardrobe(id);
            foreach(var t in rig.GetComponentsInChildren<Transform>(true)){
                if(!guest&&t.name.StartsWith("Outfit_"))t.gameObject.SetActive(t.name==outfit); // guests keep their own clothes
                if(t.name.StartsWith("Hat_"))t.gameObject.SetActive(!guest&&t.name==hat);
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
            // Gus..Lena have their own material names, so only the first six need their palette back.
            if(guest&&prefab.name.StartsWith("Restaurant_Guest_")&&gi<GuestPalette.GetLength(0))TintGuest(rig,gi);
            SetLayer(holder.gameObject);
            return new Actor{Root=holder,Rig=rig,Last=holder.position,Phase=actors.Count*.27f+guests.Count*.17f};
        }
        // The last leg starts after pickup/preparation; walking to the pass or the dirty table is empty handed.
        string CarryModel(RestaurantStaff s,Actor a)
        {
            if(a.CarryTask!=s.Task){
                a.CarryTask=s.Task;a.CarryTicket=null;
                if(s.Action=="Serve fish"&&s.Task!=null&&(s.Task.Current!=null||s.Task.Legs.Count>0)){
                    var target=s.Task.Legs.Count>0?s.Task.Legs.Last().Target:s.Task.Current.Target;
                    // Resolve once, before either runner delivers; recomputing Access from a moving tile can pick another side.
                    var group=Sim.Groups.FirstOrDefault(g=>g.TableUid!=0&&Layout.Cells(Layout.Active.First(i=>i.Uid==g.TableUid)).Any(c=>Mathf.Abs(c.x-target.x)+Mathf.Abs(c.y-target.y)==1)&&g.Tickets.Any(t=>t.Phase==TicketPhase.Serving&&!actors.Values.Any(other=>other!=a&&other.CarryTask!=null&&other.CarryTicket==t)));
                    if(group!=null)a.CarryTicket=group.Tickets.First(t=>t.Phase==TicketPhase.Serving&&!actors.Values.Any(other=>other!=a&&other.CarryTask!=null&&other.CarryTicket==t));
                }
            }
            if(s.Task?.Current==null||s.Task.Legs.Count!=0)return null;
            if(s.Action=="Clear table")return "PlateDirty";
            if(s.Action=="Serve coffee")return "CoffeeCup";
            if(s.Action=="Serve drinks")return "Dish_Lemonade";
            if(s.Action!="Serve fish")return null;
            if(s.Id=="captain"&&Cards.Contains("plate-rack")&&Model("PlateRack")!=null)return "PlateRack"; // the plate rack card: three plates a trip
            return a.CarryTicket==null?null:DishModel(a.CarryTicket.Dish);
        }
        void Carry(Actor a,string model)
        {
            if(a.PropName!=model){if(a.Prop!=null)Destroy(a.Prop.gameObject);a.Prop=null;a.PropName=model;
                if(model!=null){a.Prop=Spawn(model,new Vector3(0,.65f,.27f),Quaternion.identity,a.Root);SetLayer(a.Prop.gameObject);}}
        }
        void FrameCamera()=>FrameCamera(Screen.width,Screen.height);
        // Captures render at their own size, not the window's; they frame for that size first.
        public bool captureFraming;
        public void FrameCamera(int w,int h)
        {
            width=w;height=h;if(ServiceCamera==null)return;
            bool phone=width/(float)Math.Max(1,height)>1.9f;
            float top=phone?46f/390:78f/900,bottom=phone?72f/390:140f/900;
            // Full screen like the mockup (the sea runs under the HUD); a lens shift keeps the room between the bars.
            ServiceCamera.rect=new Rect(0,0,1,1);ServiceCamera.usePhysicalProperties=true;if(captureFraming)ServiceCamera.aspect=width/(float)Math.Max(1,height);
            ServiceCamera.gateFit=Camera.GateFitMode.Vertical;ServiceCamera.lensShift=new Vector2(0,(top-bottom)*.5f);
            // Preserve vertical framing when HUD reduces the viewport; widen for the full 8x5 shell.
            float aspect=width*(1-top-bottom)/Math.Max(1,height); // overridden below by actual viewport aspect
            aspect=width/(height*(1-top-bottom));
            // Like the mockup: the dressed V4 room with terrace and jetty (about 14 m) fills the width between the bars.
            float distance=ServiceCamera.transform.localPosition.magnitude;
            float inner=2*Mathf.Atan(frameHalfWidth/distance/aspect)*Mathf.Rad2Deg;
            ServiceCamera.fieldOfView=2*Mathf.Atan(Mathf.Tan(inner*.5f*Mathf.Deg2Rad)/(1-top-bottom))*Mathf.Rad2Deg;
            Debug.Log($"[Catchline] restaurant camera {width}x{height} fov {ServiceCamera.fieldOfView:F2} focal {ServiceCamera.focalLength:F1} sensor {ServiceCamera.sensorSize} dist {distance:F1}");
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
            if(Sim==null||!DriveSimulation)return;
            Sim.Tick(Time.unscaledDeltaTime*Speed);
            Refresh(Time.unscaledDeltaTime*Speed);
        }
        Vector3 StaffGoal(RestaurantStaff staff)
        {
            var p=TileToWorld(staff.DrawPosition(Sim.Alpha));var push=Vector3.zero;
            foreach(var other in Sim.Staff){if(other==staff)continue;var delta=p-TileToWorld(other.DrawPosition(Sim.Alpha));float gap=delta.magnitude;
                if(gap>=.5f)continue;
                if(gap<.001f){var travel=TileToWorld(staff.Target)-p;travel.y=0;
                    delta=travel.sqrMagnitude>.01f?Vector3.Cross(Vector3.up,travel.normalized):RoomRoot.right;
                    // The same axis for both people, independent of their opposing travel directions.
                    if(Vector3.Dot(delta,RoomRoot.right)<-.001f||Mathf.Abs(Vector3.Dot(delta,RoomRoot.right))<=.001f&&Vector3.Dot(delta,RoomRoot.forward)<0)delta=-delta;
                    delta*=string.CompareOrdinal(staff.Id,other.Id)<0?1:-1;
                }else delta/=gap;
                push+=delta*(.5f-gap)*.5f;
            }
            push=Vector3.ClampMagnitude(push,.24f);var target=p+push;var tile=WorldTile(target);
            return Layout.Walkable(Vector2Int.RoundToInt(tile))?target:p;
        }
        public void Refresh(float dt)
        {
            if(Sim==null)return;if(!captureFraming&&(width!=Screen.width||height!=Screen.height))FrameCamera();animationTime+=dt;
            foreach(var s in Sim.Staff){
                // A short chase rounds a tile corner without changing the rules' route or work clock.
                var a=actors[s.Id];var goal=StaffGoal(s);var from=a.Root.position;
                if(!a.Placed){a.Root.position=goal;a.Placed=true;a.Velocity=Vector3.zero;}
                else if(dt>0)a.Root.position=Vector3.SmoothDamp(from,goal,ref a.Velocity,.085f,Mathf.Max(GameData.WalkSpeed,s.WalkSpeed)*1.5f,dt);
                Vector3 dir=a.Root.position-from;dir.y=0;bool moving=dir.sqrMagnitude>.0000001f;
                if(moving)a.Root.rotation=Quaternion.Slerp(a.Root.rotation,Quaternion.LookRotation(dir),1-Mathf.Exp(-dt*18));
                string prop=CarryModel(s,a);bool carry=prop!=null;
                Carry(a,prop);Animate(a,moving?carry?"CarryPlate":"Walk":Pose(s,carry));a.Last=a.Root.position;
            }
            PassAndStations();
            var queueGroups=Sim.Groups.Where(g=>g.Phase==GroupPhase.Queue||g.Phase==GroupPhase.Seating&&(!guestWalks.TryGetValue(g.Id,out var w)||!w.Following)).OrderBy(g=>g.Arrival).ThenBy(g=>g.Id).ToList();
            foreach(var g in Sim.Groups){
                if(!guestWalks.TryGetValue(g.Id,out var walk)){walk=new GuestWalk();guestWalks[g.Id]=walk;}
                if(g.Phase==GroupPhase.Seating)Escort(g,walk);
                for(int i=0;i<g.Guests.Count;i++){
                    var order=g.Guests[i];bool active=g.Phase!=GroupPhase.NotArrived&&g.Phase!=GroupPhase.Gone;
                    if(!guests.TryGetValue(order.Id,out var a)){if(!active)continue;a=MakeActor(order.Id.ToString(),true,g.Critic);guests[order.Id]=a;}
                    a.Ahead=i>0&&guests.TryGetValue(g.Guests[i-1].Id,out var ahead)?ahead:null;
                    if(g.Phase==GroupPhase.Gone){if(!a.Departed)Leave(a,dt);continue;}
                    a.Root.gameObject.SetActive(active);if(!active)continue;
                    int row=Mathf.Max(0,queueGroups.IndexOf(g));
                    Vector3 queue=TileToWorld(Layout.Door)+RoomRoot.right*((i-(g.Count-1)*.5f)*.65f)+RoomRoot.forward*(.9f+row*.85f);
                    if(!a.Placed){a.Root.position=queue;a.Placed=true;}
                    bool seated=g.TableUid!=0&&g.Phase!=GroupPhase.Seating&&g.Phase!=GroupPhase.Queue;
                    Transform table=null;bool moving=false;
                    if(seated&&items.TryGetValue(g.TableUid,out table)){
                        var tb=TableBounds(table);var seat=new Vector3(tb.center.x,table.position.y,tb.center.z)+Seat(i);
                        if(a.RouteKey!=g.TableUid){
                            a.Route=GuestRoute(a.Root.position,seat,table);a.Waypoint=0;a.RouteKey=g.TableUid;walk.Routes[order.Id]=a.Route;}
                        moving=WalkGuest(a,a.Route,dt);a.Arrived=a.Route.Count>0&&a.Waypoint==a.Route.Count;
                        if(a.Arrived)a.Root.localRotation=Quaternion.Euler(0,i%2==0?180:0,0);
                    }else if(g.Phase==GroupPhase.Seating&&walk.Following){
                        var trail=Trailing(walk.Trail,.65f*(i+1));
                        if(a.RouteKey!=-1){a.Route=GuestRoute(a.Root.position,TileToWorld(Layout.Door));a.Waypoint=0;a.RouteKey=-1;}
                        var route=new List<Vector3>(a.Route);route.AddRange(trail.Skip(1));moving=WalkGuest(a,route,dt);
                    }else{
                        var from=a.Root.position;a.Root.position=Vector3.MoveTowards(from,queue,Mathf.Max(0,dt)*GameData.WalkSpeed);
                        var dir=a.Root.position-from;moving=dir.sqrMagnitude>.0000001f;if(moving)a.Root.rotation=Quaternion.LookRotation(dir);
                    }
                    Animate(a,moving?"Walk":seated&&a.Arrived?g.Phase==GroupPhase.Eating?"Eat":"Sit":"Idle");
                    var ticket=g.Tickets.FirstOrDefault(t=>t.Order.Id==order.Id);
                    // A round bought on the tap (Service v2 upsell) replaces the plates: the drinks or the dessert course.
                    Dish? course=g.UpsellCoins>0&&g.Phase==GroupPhase.Eating?g.Upsell:ticket?.Dish;
                    PlaceDish(a,seated&&a.Arrived&&ticket!=null&&ticket.Phase==TicketPhase.Delivered&&g.Phase!=GroupPhase.Payment&&g.Phase!=GroupPhase.Clearing?course:null,seated?table:null,i);
                    a.Last=a.Root.position;
                }
            }
            Snapshot.Hour=Sim.Hour;Snapshot.CoinsTonight=Sim.Result.NetCoins;Snapshot.Popularity=Mathf.Max(0,Popularity+Sim.Result.PopularityGain);Snapshot.Finished=Sim.Finished;
            Snapshot.Staff.Clear();foreach(var s in Sim.Staff)Snapshot.Staff.Add(new StaffSnapshot{Id=s.Id,PortraitKey=s.Id,Job=s.Job,Task=s.Action,Busy=s.BusyProgress});
            Snapshot.Orders.Clear();foreach(var g in Sim.Groups.Where(g=>g.TableUid!=0&&g.Phase!=GroupPhase.Gone))foreach(var t in g.Tickets)Snapshot.Orders.Add(new OrderSnapshot{TableId=g.TableUid,GroupId=g.Id,Dish=t.Dish,Phase=g.Phase,Patience=Sim.Patience(g)});
            Snapshot.Stock.Clear();foreach(var stock in Sim.Stock)foreach(var dish in RestaurantData.Dishes.Where(d=>!d.Staple&&d.Form==stock.Form&&Sim.Layout.CanCook(d.Id)))Snapshot.Stock.Add(new StockSnapshot{Dish=dish.Id,Species=stock.Species,Portions=stock.Count});
            Snapshot.BrokenAppliances.Clear();Snapshot.BrokenAppliances.AddRange(Sim.Broken.OrderBy(x=>x));
            var choice=Sim.Groups.SelectMany(g=>g.Tickets).FirstOrDefault(t=>t.Phase==TicketPhase.Choice);
            Snapshot.Question=choice==null?null:new QuestionSnapshot{GuestId=choice.Order.Id,Title="Offer fish soup instead?",Yes="Offer soup",No="Just drinks"};
        }
        // Codex 2's restaurant work clips (CrewRig_Restaurant); Animate falls back to Idle when a rig lacks one.
        string Pose(RestaurantStaff s,bool carry)
        {
            if(s.Walking)return carry?"CarryPlate":"Walk";
            if(!s.Busy)return"Idle";
            string label=s.Action;
            if(label.StartsWith("Cook ")){
                var at=Sim.Layout.Active.FirstOrDefault(i=>i.Uid==s.Task.Current?.Appliance);
                return at==null?"Idle":at.Id==ItemId.PrepCounter?"Chop":at.Id==ItemId.Sink?"Wash":"Cook";
            }
            if(label.StartsWith("Repair "))return"Repair";
            return label switch{"Take order"=>"TakeOrder","Take payment"=>"TakeOrder","Seat group"=>"Greet","Clear table"=>"Wipe",
                "Serve coffee" or "Serve drinks"=>"Pour",_=>"Idle"};
        }
        void Animate(Actor actor,string pose)
        {
            AnimationClip clip=null;
            var anim=actor.Rig.GetComponentInChildren<Animation>();
            if(anim!=null)foreach(AnimationState state in anim)if(state.name.Split('|').Last()==pose){clip=state.clip;break;}
            if(clip==null&&!clips.TryGetValue(pose,out clip)&&!clips.TryGetValue("Idle",out clip))return;
            clip.SampleAnimation(actor.Rig.gameObject,Mathf.Repeat(animationTime+actor.Phase,Mathf.Max(.01f,clip.length)));
        }
        // Arrange mode: the item being placed stands on its tiles over a lit footprint, green when it fits and red when not.
        Transform ghost,ghostSpot;ItemId ghostId;bool ghostRotated;
        public string PrefabTurn(ItemId id)=>Models.TryGetValue(id,out var m)&&Model(ModelFor(id,m)) is { } p?ModelFor(id,m)+" "+p.transform.localEulerAngles:"none";
        public void Ghost(ItemId? id,Vector2Int tile,bool rotated,bool fits)
        {
            if(RoomRoot==null)return;
            if(ghost!=null&&(id==null||ghostId!=id||ghostRotated!=rotated)){Destroy(ghost.gameObject);ghost=null;}
            if(id==null){if(ghostSpot!=null)ghostSpot.gameObject.SetActive(false);return;}
            var d=RestaurantData.Get(id.Value);int w=rotated?d.Height:d.Width,h=rotated?d.Width:d.Height;
            if(ghost==null&&Models.TryGetValue(id.Value,out var model)){
                ghost=Spawn(ModelFor(id.Value,model),Vector3.zero,Quaternion.Euler(0,rotated?-90:0,0));SetLayer(ghost.gameObject);ghostId=id.Value;ghostRotated=rotated;}
            float x=tile.x+(rotated?1:d.Width)*.5f-.5f;
            if(ghost!=null)ghost.localPosition=new Vector3(3.5f-x,.04f,2-tile.y);
            if(ghostSpot==null){
                var tex=ArtLibrary.Get()?.UiTex("rx-placement-highlight");if(tex==null)return;
                var go=new GameObject("Arrange spot");go.transform.SetParent(RoomRoot,false);go.layer=Layer;
                go.AddComponent<SpriteRenderer>().sprite=Sprite.Create(tex,new Rect(0,0,tex.width,tex.height),new Vector2(.5f,.5f),tex.width);
                ghostSpot=go.transform;ghostSpot.localRotation=Quaternion.Euler(90,0,0);}
            var tx=ghostSpot.GetComponent<SpriteRenderer>().sprite.texture;
            ghostSpot.gameObject.SetActive(true);
            ghostSpot.localPosition=new Vector3(3.5f-(tile.x+w*.5f-.5f),.06f,2-(tile.y+h*.5f-.5f));
            ghostSpot.localScale=new Vector3(w*1.1f,h*1.1f*tx.width/tx.height,1);
            // Codex 1's red footprint when it exists (same size as the green one), the green one tinted otherwise.
            var bad=ArtLibrary.Get()?.UiTex("rx-s1x-placement-invalid");var sr=ghostSpot.GetComponent<SpriteRenderer>();
            var want=!fits&&bad!=null?bad:ArtLibrary.Get()?.UiTex("rx-placement-highlight");
            if(want!=null&&sr.sprite.texture!=want)sr.sprite=Sprite.Create(want,new Rect(0,0,want.width,want.height),new Vector2(.5f,.5f),want.width);
            sr.color=fits||bad!=null?Color.white:new Color(1,.4f,.35f);
        }
        // Service: the table the captain was told to work first is lit on the floor (null clears it).
        Transform mark;
        public void Mark(RestaurantItem item)
        {
            if(RoomRoot==null)return;
            if(item==null){if(mark!=null)mark.gameObject.SetActive(false);return;}
            if(mark==null){
                var tex=ArtLibrary.Get()?.UiTex("rx-placement-highlight");if(tex==null)return;
                var go=new GameObject("Captain's table");go.transform.SetParent(RoomRoot,false);go.layer=Layer;
                go.AddComponent<SpriteRenderer>().sprite=Sprite.Create(tex,new Rect(0,0,tex.width,tex.height),new Vector2(.5f,.5f),tex.width);
                mark=go.transform;mark.localRotation=Quaternion.Euler(90,0,0);}
            var d=RestaurantData.Get(item.Id);int w=item.Rotated?d.Height:d.Width,h=item.Rotated?d.Width:d.Height;
            var t=mark.GetComponent<SpriteRenderer>().sprite.texture;
            mark.gameObject.SetActive(true);
            mark.localPosition=new Vector3(3.5f-(item.X+w*.5f-.5f),.06f,2-(item.Y+h*.5f-.5f));
            mark.localScale=new Vector3(w*1.1f,h*1.1f*t.width/t.height,1);
        }
        // A placed item lifted for moving hides until it is put down.
        public void Hide(int uid,bool hidden){if(items.TryGetValue(uid,out var t)&&t!=null)t.gameObject.SetActive(!hidden);}
        // Floor tile under a viewport point (0..1, bottom-left), and where a tile centre shows on the viewport.
        public bool TileAt(Vector2 viewport,out Vector2Int tile)
        {
            tile=default;if(ServiceCamera==null||RoomRoot==null)return false;
            var ray=ServiceCamera.ViewportPointToRay(viewport);var floor=new Plane(RoomRoot.up,RoomRoot.TransformPoint(new Vector3(0,.04f,0)));
            if(!floor.Raycast(ray,out var t))return false;
            var p=RoomRoot.InverseTransformPoint(ray.GetPoint(t));tile=new Vector2Int(Mathf.RoundToInt(3.5f-p.x),Mathf.RoundToInt(2-p.z));return true;
        }
        // Service markers (S15) anchor to the top of a placed item and above a staff member's head (viewport, z>0 in front).
        // Service v2: plates waiting on the pass (tap their table to carry them) and dishes cooking on their stations,
        // growing in as they cook. One prop per slot, swapped only when its dish changes.
        readonly Dictionary<string,(string model,Transform t,Vector3 size)> props=new();
        // Codex 2's SERVICE-PROPS-2 cooking props and their measured seat on each Pack station (station-local, metres).
        static readonly Dictionary<ItemId,(string model,Vector3 at)> CookProps=new(){
            [ItemId.Stove]=("Cook_Pan",new Vector3(.14625f,.8f,.138f)),[ItemId.Grill]=("Cook_Grill",new Vector3(-.005984f,.825f,-.015481f)),
            [ItemId.Fryer]=("Cook_FryerBasket",new Vector3(0,.91f,.093f)),[ItemId.Oven]=("Cook_OvenTray",new Vector3(0,1.2f,0)),
            [ItemId.Steamer]=("Cook_SteamPot",new Vector3(0,.92f,-.002086f)),[ItemId.SoupKettle]=("Cook_SoupLadle",new Vector3(-.05413f,.660388f,0)),
            [ItemId.PrepCounter]=("Cook_BreadBoard",new Vector3(-.14225f,.825f,.032365f))};
        // A point in the station's own upright frame: its yaw on the layout, ignoring any import turn on the FBX root.
        static Vector3 OnStation(Transform station,Vector3 local)=>station.position+Quaternion.Euler(0,station.eulerAngles.y,0)*local;
        void PassAndStations()
        {
            var want=new Dictionary<string,(string model,Vector3 at,float scale)>();var yaw=new Dictionary<string,float>();
            int k=Layout.Stage.KitchenWidth;var pass=TileToWorld(new Vector2(k,2),.98f);
            var ready=Sim.Groups.Where(g=>g.Phase==GroupPhase.Kitchen).SelectMany(g=>g.Tickets).Where(t=>t.Phase==TicketPhase.Ready).OrderBy(t=>t.ReadyAt).Take(6).ToList();
            for(int i=0;i<ready.Count;i++)want["pass"+i]=(DishModel(ready[i].Dish),pass+RoomRoot.forward*((i%3-1)*.3f)+RoomRoot.right*((i/3)*.28f),1);
            foreach(var (uid,dish,done,since) in Sim.OnStations){
                if(!items.TryGetValue(uid,out var st)||st==null)continue;
                var item=Layout.Active.FirstOrDefault(i=>i.Uid==uid);
                if(item!=null&&CookProps.TryGetValue(item.Id,out var cp)&&Model(cp.model)!=null){want["cook"+uid]=(cp.model,OnStation(st,cp.at),1);yaw["cook"+uid]=st.eulerAngles.y;continue;}
                var b=TableBounds(st);
                want["cook"+uid]=(DishModel(dish),new Vector3(b.center.x,b.max.y,b.center.z),Mathf.Lerp(.55f,1f,done));
            }
            // Kept gadgets stand in the room: the heat lamp at the far end of the pass, the brass bell on the reception desk;
            // on festival nights bunting runs along the back wall and over the pier's front.
            if(Cards.Contains("warming-lamp"))want["lamp"]=("WarmingLamp",pass-RoomRoot.forward*.75f,1);
            var desk=Layout.Active.FirstOrDefault(i=>i.Id==ItemId.Reception);
            if(Cards.Contains("service-bell")&&desk!=null&&items.TryGetValue(desk.Uid,out var dt)&&dt!=null){var b=TableBounds(dt);want["bell"]=("ServiceBell",new Vector3(b.center.x+.18f,b.max.y,b.center.z),1);}
            if(NightCard=="festival"){
                // The string runs toward screen-right from its pivot, so it hangs from the left (local +x) end.
                want["bunting-back"]=("Bunting",RoomRoot.TransformPoint(new Vector3(4f,2.15f,-2.7f)),1);
                want["bunting-front"]=("Bunting",RoomRoot.TransformPoint(new Vector3(4f,2.1f,4.2f)),1);
            }
            // Coins a paid table left (Codex 2's tip piles, the big one for a generous table) wait there until it is cleared.
            foreach(var g in Sim.Groups.Where(g=>g.Phase==GroupPhase.Clearing&&g.TipCoins>0&&g.ClearedAt<0)){
                if(!items.TryGetValue(g.TableUid,out var tt)||tt==null)continue;var b=TableBounds(tt);
                want["tip"+g.Id]=(g.TipCoins>=8?"TipCoins_L":"TipCoins_S",new Vector3(b.center.x+.12f,b.max.y,b.center.z),1);
            }
            // A burnt dish smokes on its station for a moment before the pan is scraped.
            if(Sim.LastBurntAt>=0&&Sim.Seconds-Sim.LastBurntAt<1.6f&&items.TryGetValue(Sim.LastBurntUid,out var bt)&&bt!=null&&Model("Cook_Burnt")!=null){
                var item=Layout.Active.FirstOrDefault(i=>i.Uid==Sim.LastBurntUid);
                yaw["burnt"]=bt.eulerAngles.y;want["burnt"]=("Cook_Burnt",OnStation(bt,item!=null&&CookProps.TryGetValue(item.Id,out var cp)?cp.at:new Vector3(0,TableBounds(bt).max.y-bt.position.y,0)),1);
            }
            // Service v2 gulls (Codex 2's two poses): one swoops onto a table, stands among the plates, flaps off when shooed or fed.
            float now=Sim.Seconds+Sim.Alpha*RestaurantTuning.TickSeconds;
            if(Sim.GullTable!=0&&items.TryGetValue(Sim.GullTable,out var gt)&&gt!=null){
                var b=TableBounds(gt);var top=new Vector3(b.center.x+.2f,b.max.y,b.center.z-.12f);float since=Mathf.Clamp01((now-Sim.GullLandedAt)/.5f);
                want["gull"]=since<1?("Gull_Flap",top+(Vector3.up*1.6f+RoomRoot.right*1.4f)*(1-since),1):("Gull_Stand",top,1);
            }
            float gone=now-Sim.GullLeftAt;
            if(Sim.GullLeftAt>=0&&gone<1.4f&&items.TryGetValue(Sim.GullLeftTable,out var lt)&&lt!=null){
                var b=TableBounds(lt);want["gullaway"]=("Gull_Flap",new Vector3(b.center.x+.2f,b.max.y,b.center.z-.12f)+Vector3.up*gone*2.4f-RoomRoot.right*gone*2.8f,1);
            }
            // The evening ferry (Codex 2's model) sails in bow first along the pier's right side, moors while its passengers
            // come up, then backs out to sea.
            if(Sim.FerryAt>=0&&Model("Ferry")!=null){
                float t=now-Sim.FerryAt,sail=8f,stay=RestaurantTuning.FerryStay;
                if(t>-sail&&t<stay+sail){
                    float away=t<0?Mathf.SmoothStep(0,1,-t/sail):t>stay?Mathf.SmoothStep(0,1,(t-stay)/sail):0;
                    want["ferry"]=("Ferry",RoomRoot.TransformPoint(new Vector3(-6.95f,-.57f+Mathf.Sin(now*1.3f)*.03f,Mathf.Lerp(.8f,19f,away))),1);yaw["ferry"]=-90;
                }
            }
            foreach(var key in props.Keys.Where(x=>!want.ContainsKey(x)).ToList()){if(props[key].t!=null)Destroy(props[key].t.gameObject);props.Remove(key);}
            foreach(var (key,w) in want){
                if(w.model==null||Model(w.model)==null)continue;
                if(!props.TryGetValue(key,out var p)||p.t==null||p.model!=w.model){
                    if(p.t!=null)Destroy(p.t.gameObject);
                    var t=Spawn(w.model,Vector3.zero,Quaternion.identity,RoomRoot);SetLayer(t.gameObject);p=(w.model,t,t.localScale);props[key]=p;
                }
                p.t.position=w.at;p.t.localScale=p.size*w.scale;
                if(yaw.TryGetValue(key,out var y))p.t.rotation=Quaternion.Euler(0,y,0)*Model(w.model).transform.localRotation;
            }
        }
        public bool ItemTop(int uid,out Vector3 vp)
        {
            vp=default;if(ServiceCamera==null||!items.TryGetValue(uid,out var t)||t==null||!t.gameObject.activeInHierarchy)return false;
            var b=TableBounds(t);vp=ServiceCamera.WorldToViewportPoint(new Vector3(b.center.x,b.max.y,b.center.z));return vp.z>0;
        }
        public bool StaffHead(string id,out Vector3 vp)
        {
            vp=default;if(ServiceCamera==null||!actors.TryGetValue(id,out var a)||a.Root==null)return false;
            var rs=a.Root.GetComponentsInChildren<SkinnedMeshRenderer>();float top=a.Root.position.y+1.7f;
            foreach(var r in rs)top=Mathf.Max(top,r.bounds.max.y);
            vp=ServiceCamera.WorldToViewportPoint(new Vector3(a.Root.position.x,top,a.Root.position.z));return vp.z>0;
        }
        public Vector3 ViewportOf(Vector2 tile,float y=.04f)=>ServiceCamera==null?Vector3.zero:ServiceCamera.WorldToViewportPoint(TileToWorld(tile,y));
        public void End()
        {
            ghost=ghostSpot=mark=null;props.Clear();
            foreach(var c in previousCameras)if(c!=null)c.enabled=true;previousCameras.Clear();
            if(RoomRoot!=null){if(Application.isPlaying)Destroy(RoomRoot.gameObject);else DestroyImmediate(RoomRoot.gameObject);}
            foreach(var m in guestMaterials)if(m!=null){if(Application.isPlaying)Destroy(m);else DestroyImmediate(m);}guestMaterials.Clear();guestTints.Clear();
            if(ambientSaved){RenderSettings.ambientMode=savedAmbientMode;RenderSettings.ambientSkyColor=savedAmbientSky;RenderSettings.ambientEquatorColor=savedAmbientEquator;RenderSettings.ambientGroundColor=savedAmbientGround;RenderSettings.ambientLight=savedAmbientLight;RenderSettings.ambientIntensity=savedAmbientIntensity;RenderSettings.reflectionIntensity=savedReflectionIntensity;RenderSettings.defaultReflectionMode=savedReflectionMode;ambientSaved=false;}
            if(postProfile!=null){if(Application.isPlaying)Destroy(postProfile);else DestroyImmediate(postProfile);postProfile=null;}
            reflectionProbe=null;
            items.Clear();actors.Clear();guests.Clear();guestWalks.Clear();clips.Clear();RoomRoot=null;ServiceCamera=null;Sim=null;Layout=null;
            Snapshot.Staff.Clear();Snapshot.Orders.Clear();Snapshot.Stock.Clear();Snapshot.BrokenAppliances.Clear();Snapshot.Question=null;
        }
        void OnDestroy()=>End();
    }
}

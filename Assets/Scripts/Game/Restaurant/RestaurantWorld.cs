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
        // The room being drawn: the night's layout, or the player's own while arranging (no sim, no people).
        public RestaurantLayout Layout {get;private set;}
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
            public Transform Root,Rig,Prop,Dish; public Vector3 Last; public float Phase; public string DishName;
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
        Transform Spawn(string name,Vector3 p,Quaternion rotation,Transform parent=null)
        {
            var prefab=Model(name);
            if(prefab==null)throw new InvalidOperationException("Restaurant asset missing: "+name+". Rebuild ArtLibrary after importing the Restaurant folder.");
            // A model exported with its axis turn on the root keeps that turn under the layout's own (else it lies on its side).
            return ArtLibrary.Spawn(prefab,parent??RoomRoot,p,rotation*prefab.transform.localRotation).transform;
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
                foreach(var item in layout.Active){
                    if(!Models.TryGetValue(item.Id,out var model))continue;
                    model=ModelFor(item.Id,model);
                    float x=item.X+(item.Rotated?1:RestaurantData.Get(item.Id).Width)*.5f-.5f;
                    var pos=new Vector3(3.5f-x,.04f,2-item.Y);
                    var t=Spawn(model,pos,Quaternion.Euler(0,item.Rotated?-90:0,0));items.Add(item.Uid,t);
                    if(RestaurantData.Get(item.Id).Seats>0){var top=TableBounds(t);Spawn(Model("TableCandle")!=null?"TableCandle":"TableLantern",new Vector3(top.center.x,top.max.y,top.center.z),Quaternion.identity);
                        // Cosy lighting: a pendant over every table (base height from its footprint), lit warm below.
                        if(layout.HasUpgrade("CosyLighting")&&Model("CosyPendantLamp")!=null){Spawn("CosyPendantLamp",new Vector3(top.center.x,1.65f,top.center.z),Quaternion.identity);cosyLamps.Add(new Vector3(top.center.x,1.6f,top.center.z));}}
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
                    if(kit!=null)foreach(var r in room.GetComponentsInChildren<Renderer>(true)){var mats=r.sharedMaterials;for(int n=0;n<mats.Length;n++)mats[n]=kit;r.sharedMaterials=mats;}
                }
                foreach(var clip in ArtLibrary.Get().CrewClips??Array.Empty<AnimationClip>())if(clip!=null){var n=clip.name.Split('|').Last();clips[n]=clip;}
                if(sim!=null)foreach(var staff in sim.Staff)actors[staff.Id]=MakeActor(staff.Id,false);
                ServiceCamera=new GameObject("Restaurant camera").AddComponent<Camera>();
                ServiceCamera.transform.SetParent(RoomRoot,false);
                ServiceCamera.clearFlags=CameraClearFlags.SolidColor;ServiceCamera.backgroundColor=new Color(.09f,.3f,.56f); // the mockup's evening sea
                ServiceCamera.nearClipPlane=.1f;ServiceCamera.farClipPlane=70;ServiceCamera.cullingMask=1<<Layer;ServiceCamera.depth=30;
                // V3's camera study: 38 degree pitch, -2 degree yaw from the quay, 58mm equivalent.
                ServiceCamera.transform.localPosition=new Vector3(-.598f,13.359f,17.088f);
                ServiceCamera.transform.localRotation=Quaternion.Euler(38,178,0);
                // Stage 1 reads Codex 2's room-look recipe unmirrored (its lights were placed in the V4 room's own axes, verified r31).
                var stageLights=roomName==StageRooms[0]?RecipeLights(roomName,false):StageRecipe(roomName);
                ServiceCamera.orthographic=false;ServiceCamera.fieldOfView=21.9542f;
                foreach(var c in Camera.allCameras)if(c!=ServiceCamera&&c.enabled){previousCameras.Add(c);c.enabled=false;}
                // Codex 2's V4 night recipe (Stage1V4/lighting.json): blue dusk over warm lanterns, window wash and the jetty lamp.
                AddLight(new Vector3(-4,9,6),new Color(.39f,.6f,1),.55f,true);
                foreach(var lamp in cosyLamps)AddLight(lamp,new Color(1,.78f,.48f),.6f,false,2.8f); // room-look3: warmer pools on the tables
                if(stageLights!=null)foreach(var (pos,watts) in stageLights)AddLight(pos,new Color(1,.8f,.5f),Mathf.Clamp(watts/110f,.12f,.7f),false,Mathf.Lerp(1.6f,5f,Mathf.InverseLerp(8,75,watts)));
                else foreach(var (x,y,z,watts) in NightLights)AddLight(new Vector3(x,y,z),new Color(1,.8f,.5f),Mathf.Clamp(watts/110f,.12f,.7f),false,Mathf.Lerp(1.6f,5f,Mathf.InverseLerp(8,75,watts)));
                // The player build drops the material's atlas reference; bind the painted atlas from Resources.
                var atlas=Resources.Load<Texture2D>("RestaurantAtlas/Restaurant_BaseColor");var surface=Resources.Load<Texture2D>("RestaurantAtlas/Restaurant_Surface");
                foreach(var r in RoomRoot.GetComponentsInChildren<Renderer>(true))foreach(var m in r.sharedMaterials)
                    if(m!=null&&m.shader.name=="Catchline/RestaurantAtlas"&&m.GetTexture("_BaseMap")==null){m.SetTexture("_BaseMap",atlas);m.SetTexture("_SurfaceMap",surface);}
                AddSea();
                SetLayer(RoomRoot.gameObject);FrameCamera();Refresh(0);
            }catch{End();throw;}
        }
        readonly List<Vector3> cosyLamps=new();
        static readonly string[] StageRooms={"Stage1V4","Stage2Bistro","Stage3Restaurant","Stage4Seafood"};
        string roomName;
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
            if(sun)go.transform.localRotation=Quaternion.Euler(42,-25,0);
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
            Quad("Night sea",new Vector3(0,-.57f,0),new Vector2(90,90),Make("NightWater",false,8,.46f,0));
            Quad("Lantern streaks",new Vector3(-.6f,-.558f,4.5f),new Vector2(11.2f,3.3f),Make("LanternStreaks",true,0,.8f,.25f));
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
        static string DishModel(Dish d)=>d switch{
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
        Actor MakeActor(string id,bool guest)
        {
            var holder=new GameObject((guest?"Guest ":"Staff ")+id).transform;holder.SetParent(RoomRoot,false);
            var lib=ArtLibrary.Get();string[] civilians={"Ada","Ben","Cora","Dan","Edda","Finn","Gus","Hazel","Ivo","Jonas","Kai","Lena","Marta","Nils","Pia","Greta","Henrik","Zola","Vera","Anton"}; // GUESTS-3 bring their own colours
            int gi=(guests.Count+guestStart)%civilians.Length; // each night starts further along the roster
            // Mo 10-27: Mira hosts in her boat model for now (the restaurant host rig read too big and wide).
            bool boatMira=!guest&&id=="mira"&&lib?.M("CrewRig")!=null;
            var prefab=boatMira?lib.M("CrewRig"):lib?.M(guest?"Restaurant_Guest_"+civilians[gi]:"CrewRig_Restaurant")??(guest?null:lib?.M("CrewRig"));
            if(prefab==null)throw new InvalidOperationException("Boat CrewRig is missing from ArtLibrary");
            var rig=ArtLibrary.Spawn(prefab,holder,Vector3.zero,Quaternion.identity).transform;
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
            var prop=Spawn("GrilledFishPlate",new Vector3(0,.65f,.27f),Quaternion.identity,holder);prop.gameObject.SetActive(false);
            SetLayer(holder.gameObject);
            return new Actor{Root=holder,Rig=rig,Prop=prop,Last=holder.position,Phase=actors.Count*.27f+guests.Count*.17f};
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
            ServiceCamera.rect=new Rect(0,0,1,1);ServiceCamera.usePhysicalProperties=true;
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
            if(Sim==null)return;
            if(DriveSimulation)Sim.Tick(Time.unscaledDeltaTime*Speed);
            Refresh(Time.unscaledDeltaTime*Speed);
        }
        public void Refresh(float dt)
        {
            if(Sim==null)return;if(!captureFraming&&(width!=Screen.width||height!=Screen.height))FrameCamera();animationTime+=dt;
            foreach(var s in Sim.Staff){
                // The body follows the rules' tile position smoothly (Mo 10-27: the captain skipped and glitched when the
                // rules snapped a walker back to its tile on a new task); a far jump (door, new night) still lands at once.
                var a=actors[s.Id];var goal=TileToWorld(s.Position);var from=a.Root.position;
                float gap=Vector3.Distance(from,goal);
                a.Root.position=gap>2.5f||a.Last==Vector3.zero?goal:Vector3.MoveTowards(from,goal,Mathf.Max(GameData.WalkSpeed*1.4f,gap*6)*Mathf.Max(.0001f,dt));
                Vector3 dir=a.Root.position-from;dir.y=0;bool moving=dir.sqrMagnitude>.0000004f;
                if(moving)a.Root.rotation=Quaternion.Slerp(a.Root.rotation,Quaternion.LookRotation(dir),1-Mathf.Exp(-dt*10));
                bool carry=s.Action.StartsWith("Serve")||s.Action=="Clear table";
                a.Prop.gameObject.SetActive(carry);Animate(a,moving&&gap>.05f?carry?"CarryPlate":"Walk":Pose(s,carry));a.Last=a.Root.position;
            }
            foreach(var g in Sim.Groups)for(int i=0;i<g.Guests.Count;i++){
                var order=g.Guests[i];bool active=g.Phase!=GroupPhase.NotArrived&&g.Phase!=GroupPhase.Gone;
                if(!guests.TryGetValue(order.Id,out var a)){if(!active)continue;a=MakeActor(order.Id.ToString(),true);guests[order.Id]=a;}
                a.Root.gameObject.SetActive(active);if(!active)continue;
                bool seated=g.TableUid!=0&&g.Phase!=GroupPhase.Seating&&g.Phase!=GroupPhase.Queue;
                Vector3 p=TileToWorld(new Vector2(Sim.Layout.Door.x,Sim.Layout.Door.y))+new Vector3(-(i%2)*.5f,0,.9f+(g.Id%4)*.45f);
                Transform table=null;if(seated&&items.TryGetValue(g.TableUid,out table)){var tb=TableBounds(table);p=new Vector3(tb.center.x,table.position.y,tb.center.z)+Seat(i);}
                if(a.Last==Vector3.zero||a.Root.position==RoomRoot.position)a.Root.position=p;
                a.Root.position=Vector3.MoveTowards(a.Root.position,p,Mathf.Max(.01f,dt)*GameData.WalkSpeed);
                a.Root.localRotation=Quaternion.Euler(0,seated?(i%2==0?180:0):180,0); // 0 faces the camera; the queue and front seats face into the room
                // Existing boat work loop is a placeholder for eating; knees are folded on the same skeleton.
                Animate(a,seated?g.Phase==GroupPhase.Eating?"Eat":"Sit":"Walk");
                var ticket=g.Tickets.FirstOrDefault(t=>t.Order.Id==order.Id);
                PlaceDish(a,seated&&ticket!=null&&ticket.Phase==TicketPhase.Delivered&&g.Phase==GroupPhase.Eating?ticket.Dish:null,seated?table:null,i);
                
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
            ghost=ghostSpot=mark=null;
            foreach(var c in previousCameras)if(c!=null)c.enabled=true;previousCameras.Clear();
            if(RoomRoot!=null){if(Application.isPlaying)Destroy(RoomRoot.gameObject);else DestroyImmediate(RoomRoot.gameObject);}
            foreach(var m in guestMaterials)if(m!=null){if(Application.isPlaying)Destroy(m);else DestroyImmediate(m);}guestMaterials.Clear();guestTints.Clear();
            items.Clear();actors.Clear();guests.Clear();clips.Clear();RoomRoot=null;ServiceCamera=null;Sim=null;Layout=null;
            Snapshot.Staff.Clear();Snapshot.Orders.Clear();Snapshot.Stock.Clear();Snapshot.BrokenAppliances.Clear();Snapshot.Question=null;
        }
        void OnDestroy()=>End();
    }
}

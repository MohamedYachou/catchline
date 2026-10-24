using System;
using System.Collections;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool SecondNetActive => State.SecondNetActive;
        public NetState SecondNet { get; private set; }
        readonly List<(Species species, float kg)> secondNetFish = new();
        Person secondNetWorker;
        int secondNetClaim;
        float secondNetTime, secondNetSoak;
        Transform secondNetFloats, secondNetDrum;
        LineRenderer[] secondNetRopes;
        int netGameRig;
        public float SecondNetRemaining => Mathf.Max(0, secondNetSoak - secondNetTime);
        public float SecondNetCatchKg => secondNetFish.Sum(f => f.kg);
        public bool AllNetsStowed => Net == NetState.Stowed && SecondNet == NetState.Stowed;
        Vector2Int SecondNetAccess => IsTier5 ? tier5SideNetAccess ?? new Vector2Int(65, 7) : State.HullDef.RodTiles[1];
        Vector3 SecondNetBasketLocal => IsTier5 ? Grid.GetLocal(SecondNetAccess)+new Vector3(0,.14f,-.58f) : Grid.GetLocal(SecondNetAccess) + new Vector3(.35f, .14f, .1f);
        Vector3 SecondNetAnchor => IsTier5 ? Grid.GetLocal(SecondNetAccess) + new Vector3(.55f,.35f,0) : new Vector3(2.8f,.35f,-.24f);
        public int UsableRodCount => Rods.Count(r => r.Unlocked);
        public int ExcessFishermen => IsTier5 ? 0 : Mathf.Max(0, State.Crew.Count(c => c.Role == CrewRole.Fisherman) - UsableRodCount);

        void MaybeCaptureSecondNet()
        {
            var args=Environment.GetCommandLineArgs();int flag=Array.IndexOf(args,"-capture-second-net");
            if(Application.isPlaying&&SessionOnly&&flag>=0&&flag+1<args.Length)
                StartCoroutine(CaptureSecondNetModule(Path.GetFullPath(args[flag+1])));
        }
        IEnumerator CaptureSecondNetModule(string directory)
        {
            yield return null;
            Directory.CreateDirectory(directory);Application.runInBackground=true;
            StartPrepBoatTrial();captureFreeze=true;Showcase(-1,0);State.Coins=2000;
            hudTab=HudTab.Chandlery;panelOpen=true;toastUntil=0;
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,FullScreenMode.Windowed);
                for(int i=0;i<16;i++)yield return null;
                yield return CaptureFrame(directory,"module-buy-"+size.x);
            }
            BuySecondNetModule();toastUntil=0;
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,FullScreenMode.Windowed);
                departureReady=departureCrewWarning=false;hudTab=HudTab.Chandlery;panelOpen=true;
                for(int i=0;i<16;i++)yield return null;
                yield return CaptureFrame(directory,"module-equipped-"+size.x);
                RequestDeparture();ConfirmDeparture();yield return null;
                yield return CaptureFrame(directory,"fisher-warning-"+size.x);
            }
            departureReady=departureCrewWarning=false;Showcase(0,0);toastUntil=0;
            var hands=People.Where(p=>p.Contract?.Role==CrewRole.Deckhand).ToArray();
            foreach(var h in hands){h.Stop();SetDeckhandWork(h.Contract,DeckhandWork.Nets);TryNetWork(h);}
            foreach(var h in hands)for(int i=0;i<3000&&!h.Idle;i++)h.Tick(.02f, Cam.transform.rotation);
            TickNet(10);TickSecondNet(17);
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,FullScreenMode.Windowed);
                for(int i=0;i<16;i++)yield return null;
                yield return CaptureFrame(directory,"two-nets-working-"+size.x);
            }
            Debug.Log("[Catchline] MODULE042 NATIVE CAPTURES COMPLETE");Application.Quit(0);
        }

        public bool BuySecondNetModule()
        {
            if (CurrentMode != Mode.Harbour || !State.BuySecondNetModule()) return false;
            RebuildBoat(false); SaveGame();
            return true;
        }
        public bool ToggleSecondNetModule()
        {
            if (CurrentMode != Mode.Harbour || !IsPrepFisher || !State.SecondNetOwned || !AllNetsStowed || NetBasketBlocked) return false;
            State.SecondNetEnabled = !State.SecondNetEnabled;
            RebuildBoat(false); SaveGame();
            return true;
        }
        int AvailableNetStock(int rig) => Mathf.Max(0, State.ActiveNetStock -
            (rig == 0 ? SecondNet != NetState.Stowed ? 1 : 0 : Net != NetState.Stowed ? 1 : 0));

        void BuildSecondNetModuleVisual(GameObject model)
        {
            if (!SecondNetActive) return;
            if (IsTier5) { secondNetDrum = model.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name.StartsWith("Module2_") && t.name.Contains("NetDrum"));
                var b=new GameObject("Net 2 catch basket").transform;b.SetParent(Boat,false);b.localPosition=SecondNetBasketLocal-Vector3.up*.12f;
                Visuals.Box("Basket floor",b,Vector3.zero,new Vector3(.36f,.025f,.48f),Palette.DeckWoodDark);
                foreach(float side in new[]{-1f,1f}) {Visuals.Box("Basket rim",b,new Vector3(side*.18f,.08f,0),new Vector3(.025f,.16f,.48f),Palette.DeckWood);Visuals.Box("Basket rim",b,new Vector3(0,.08f,side*.24f),new Vector3(.36f,.16f,.025f),Palette.DeckWood);} return; }
            var kit = new GameObject("Second net module - replaces two rods").transform;
            kit.SetParent(model.transform.parent, false);
            kit.localPosition = new Vector3(2.8f, .05f, -.24f);
            Visuals.Box("Module mount", kit, new Vector3(0,.12f,0), new Vector3(.54f,.24f,.34f), Palette.HullNavy);
            foreach (float side in new[]{-.22f,.22f})
                Visuals.Box("Roller frame", kit, new Vector3(side,.4f,0), new Vector3(.07f,.5f,.26f), Palette.Steel);
            secondNetDrum = Visuals.Prim(PrimitiveType.Cylinder,"Second net drum",kit,new Vector3(0,.43f,0),new Vector3(.32f,.22f,.32f),Palette.Hex("168F9F")).transform;
            secondNetDrum.localRotation = Quaternion.Euler(0,0,90);
            Visuals.Box("Second net handle",kit,new Vector3(.3f,.44f,0),new Vector3(.14f,.06f,.07f),Palette.Rubber);
            var basket = new GameObject("Net 2 catch basket").transform;
            basket.SetParent(Boat, false); basket.localPosition = SecondNetBasketLocal - Vector3.up * .12f;
            Visuals.Box("Basket floor",basket,Vector3.zero,new Vector3(.36f,.025f,.48f),Palette.DeckWoodDark);
            foreach(float side in new[]{-1f,1f})
            {
                Visuals.Box("Basket rim",basket,new Vector3(side*.18f,.08f,0),new Vector3(.025f,.16f,.48f),Palette.DeckWood);
                Visuals.Box("Basket rim",basket,new Vector3(0,.08f,side*.24f),new Vector3(.36f,.16f,.025f),Palette.DeckWood);
            }
        }
        void BuildSecondNetWater()
        {
            if (!SecondNetActive || netFloats == null) return;
            secondNetFloats = Instantiate(netFloats.gameObject, world).transform;
            secondNetFloats.name = "Second independent net in water";
            secondNetFloats.localPosition = new Vector3(0,0,-2.15f);
            secondNetRopes = secondNetFloats.GetComponentsInChildren<LineRenderer>(true);
            secondNetFloats.gameObject.SetActive(false);
        }
        void DestroySecondNetWater()
        {
            ResetSecondNet();
            if (secondNetFloats != null) Visuals.Kill(secondNetFloats.gameObject);
            secondNetFloats = secondNetDrum = null; secondNetRopes = null;
        }
        void TickSecondNet(float dt)
        {
            if (!SecondNetActive) return;
            if (secondNetFloats != null && secondNetFloats.gameObject.activeSelf)
            {
                secondNetFloats.localPosition = new Vector3(0,Mathf.Sin(SimTime*1.8f+.7f)*.025f,-2.15f);
                for (int i=0; i<(secondNetRopes?.Length??0); i++)
                {
                    float side=i==0 ? -.3f : .3f;
                    secondNetRopes[i].SetPosition(0,Boat.TransformPoint(SecondNetAnchor));
                    secondNetRopes[i].SetPosition(1,secondNetFloats.TransformPoint(new Vector3(netTowFront,WaterY+.06f,State.HullDef.Center.z+side)));
                }
            }
            if (SecondNet==NetState.Hauling && secondNetDrum!=null)
                secondNetDrum.Rotate(Vector3.up, dt*100,Space.Self);
            if (SecondNet!=NetState.Soaking) return;
            secondNetTime=Mathf.Min(secondNetSoak,secondNetTime+dt);
            if (secondNetTime<secondNetSoak) return;
            // Reuse the canonical local species/weight roller without stealing the
            // other net's catch. Synchronous operation: no callback can interleave.
            var primary=netFish.ToArray();
            try { RollCompactCatch(); secondNetFish.Clear();secondNetFish.AddRange(netFish); }
            finally { netFish.Clear();netFish.AddRange(primary); }
            SecondNet=NetState.Ready;
            Toast($"Net 2 ready: {SecondNetCatchKg:0.0} kg.");
        }

        public bool CaptainSecondNetAction()
        {
            if (!SecondNetActive || CurrentMode!=Mode.Fishing || !Captain.Idle || Captain.Carrying!=null
                || NetGameActive || NetUnloadActive || Manning?.State is RodState.Reeling or RodState.Flying) return false;
            var old=Manning; bool choice=AwaitingCast; Manning=null;AwaitingCast=false;
            bool result=StartSecondNet(Captain,SecondNet==NetState.Ready);
            if(!result){Manning=old;AwaitingCast=choice;}
            return result;
        }
        bool StartSecondNet(Person person,bool haul)
        {
            if (!SecondNetActive || CurrentMode!=Mode.Fishing || !person.Idle || person.Carrying!=null || secondNetWorker!=null
                || SecondNet!=(haul?NetState.Ready:NetState.Stowed) || RigBasketBlocked(1) || (!haul && (HoldFull||AvailableNetStock(1)<=0))) return false;
            secondNetWorker=person;int claim=++secondNetClaim;SecondNet=haul?NetState.Hauling:NetState.Setting;
            bool Owns()=>secondNetWorker==person&&secondNetClaim==claim;
            void Cancel(){if(!Owns())return;secondNetWorker=null;secondNetClaim++;SecondNet=haul?NetState.Ready:NetState.Stowed;}
            void Fail()
            {
                if(!Owns())return;
                if(DeepNetSelected)State.SpendDeepNetUse();else State.NetInventory=Mathf.Max(0,State.NetInventory-1);
                ResetSecondNet();Toast("Net 2 haul lost. Other net stays at work.");
            }
            void Complete()
            {
                if(!Owns())return;
                if(haul && !IsTier5 && !person.IsCaptain&&State.Rng.NextDouble()>=.8){Fail();return;}
                secondNetWorker=null;secondNetClaim++;
                if(!haul)
                {
                    SecondNet=NetState.Soaking;secondNetTime=0;secondNetSoak=DeepNetSelected?GameData.DeepNetSoakSeconds:GameData.ShallowNetSoakSeconds;
                    secondNetFish.Clear();if(secondNetFloats!=null)secondNetFloats.gameObject.SetActive(true);return;
                }
                if(DeepNetSelected)State.SpendDeepNetUse();
                foreach(var (species,kg) in secondNetFish)
                {
                    var fish=new DeckFish{Species=species,Kg=kg,Tile=SecondNetAccess,CaughtAt=SimTime,FromNetBasket=true};
                    fish.Root=DeckFish.BuildModel(species,kg,Boat);
                    int i=NetBasketCount;
                    fish.RestPos=SecondNetBasketLocal+new Vector3((i%2-.5f)*.1f,(i/2)*.012f,(i%3-1)*.08f);
                    fish.SpawnFrom=Grid.GetLocal(SecondNetAccess)+new Vector3(0,.5f,0);fish.Root.localPosition=fish.SpawnFrom;
                    OnDeck.Add(fish);Stats.Landed++;
                    RecordLanding(FlowTelemetry.Kind.Net, species, kg);
                }
                ResetSecondNet();if(!IsTier5 || person.IsCaptain)BeginNetUnload(person);
            }
            bool walking=person.WalkTo(Grid,SecondNetAccess,()=>
            {
                if(!Owns())return;person.Face(Vector3.back);
                if(person.IsCaptain)BeginNetGame(person,!haul,Complete,Cancel,Fail,1);
                else person.Do(haul?"Hauling net":"Setting net",haul?5f:2f,Complete,Cancel);
            },Cancel);
            if(!walking)Cancel();return walking;
        }
        void ResetNet()
        {
            ResetSecondNet(); ResetPrimaryNet(); ClearNetUnload();
        }

        void ResetSecondNet()
        {
            if(NetGameActive&&netGameRig==1)ResetNetHaulGame();
            var worker=secondNetWorker;secondNetWorker=null;secondNetClaim++;worker?.Stop();
            secondNetCycleMistakes = 0;
            SecondNet=NetState.Stowed;secondNetFish.Clear();secondNetTime=0;
            if(secondNetFloats!=null)secondNetFloats.gameObject.SetActive(false);
        }

        void ModuleButton(string id,Rect r,string label,Action action,bool primary=true,bool enabled=true)
        {
            Block(r);
            coastalUi.Button(id,r,label,action,primary?"button-primary-pressed":"button-secondary-pressed",enabled);
        }

        void InterfaceFisherWarning()
        {
            Block(new Rect(0,0,iw,ih));
            coastalUi.Box("depart/crew-warning/shade",new Rect(0,0,iw,ih),"chip-dark",new Color(1,1,1,.85f));
            var p=new Rect((iw-550)/2,(ih-300)/2,550,300);
            coastalUi.Box("depart/crew-warning/panel",p,"popup-panel");
            coastalUi.Label("depart/crew-warning/title",new Rect(p.x+22,p.y+14,506,40),"Some fishermen have no rod",26,Palette.Cream);
            int fishermen=State.Crew.Count(c=>c.Role==CrewRole.Fisherman);
            coastalUi.Label("depart/crew-warning/count",new Rect(p.x+22,p.y+64,506,32),$"{fishermen} fishermen / {UsableRodCount} usable rod{(UsableRodCount==1?"":"s")} / {(SecondNetActive?2:State.Hull>0?1:0)} nets",20);
            coastalUi.Label("depart/crew-warning/help",new Rect(p.x+22,p.y+106,506,76),
                $"{ExcessFishermen} will have no rod to use. Fishermen cannot run nets or prepare fish. Change crew or restore the rods, or sail anyway.",18,SeaInk);
            ModuleButton("depart/crew-warning/back",new Rect(p.x+22,p.y+218,238,54),"Back / change crew",()=>{departureCrewWarning=departureReady=false;hudTab=HudTab.CrewOffice;panelOpen=true;},false);
            ModuleButton("depart/crew-warning/proceed",new Rect(p.x+282,p.y+218,246,54),"Sail anyway",()=>{if(departureReady&&SailBlocker()==null){departureCrewWarning=false;SetSail();}});
        }

        void InterfaceSecondNet()
        {
            if(!SecondNetActive)return;
            var anchor=Boat.TransformPoint(SecondNetAnchor + Vector3.up*.55f);
            var view=Cam.WorldToViewportPoint(anchor);
            var r=new Rect(Mathf.Clamp(view.x*iw-34,14,iw-82),Mathf.Clamp((1-view.y)*ih-64,16,ih-114),68,64);
            Block(r);
            bool can=CurrentMode==Mode.Fishing&&Captain.Idle&&Captain.Carrying==null&&!NetGameActive&&!NetUnloadActive
                && (SecondNet==NetState.Ready||SecondNet==NetState.Stowed&&!HoldFull&&AvailableNetStock(1)>0);
            coastalUi.Button("net/second",r,"",()=>CaptainSecondNetAction(),SecondNet==NetState.Ready?"bubble-hot":"bubble-white",can);
            coastalUi.Art("net/second/icon",new Rect(r.x+16,r.y+12,36,36),"icon-net");
            string status=NetUnloadRig==1 ? "Net 2 / unloading" : SecondNet switch{NetState.Soaking=>$"Net 2 / {SecondNetRemaining:0}s",NetState.Ready=>$"Net 2 / {SecondNetCatchKg:0.0} kg",NetState.Setting=>"Net 2 / setting",NetState.Hauling=>"Net 2 / hauling",_=>"Net 2 / set"};
            var caption=new Rect(r.center.x-76,r.yMax+2,152,29);
            coastalUi.Box("net/second/status/back",caption,"chip-dark");
            coastalUi.Label("net/second/status",caption,status,15,Palette.Cream,TextAnchor.MiddleCenter);
        }
    }
}

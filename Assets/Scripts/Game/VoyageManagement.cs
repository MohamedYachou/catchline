using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public readonly FlowTelemetry Flow = new();
        public bool ManagementOpen { get; private set; }
        int managementTab = 1; // Income then Operations, as supplied by Mo.
        int dashboardDetail = -1;
        bool flowReturning;
        float flowWindow = 60;
        string flowCrewSignature;
        float flowNextReport, flowNextSignature;
        readonly float[] stageDemand = new float[4],stageCapacity = new float[4],stageOutput = new float[4];
        readonly int[] stageStatus = new int[4];
        readonly List<(float at,float[] values)> forecastHistory = new();
        float nextForecastSample;
        public void OpenManagement()
        {
            if(CurrentMode!=Mode.Fishing||MenuOpen)return;
            ManagementOpen=true;tier5OperationsOpen=netOrdersOpen=PrepOrdersOpen=false;toastUntil=0;flowNextReport=0;
        }
        public void CloseManagement(){ManagementOpen=false;dashboardDetail=-1;}
        void ResetManagement()
        {
            Flow.Reset();ManagementOpen=false;flowCrewSignature=null;flowNextReport=flowNextSignature=0;
            forecastSignature=null;forecastHistory.Clear();nextForecastSample=0;dashboardDetail=-1;
        }
        void TickManagement(float dt)
        {
            if(CurrentMode!=Mode.Fishing){ManagementOpen=false;return;}
            if(Flow.Clock>=flowNextSignature)
            {
                flowNextSignature=(float)Flow.Clock+1;
                string signature=string.Join("|",State.Crew.Select(c=>c.Name+":"+c.Role+":"+c.Grade+":"+c.WorkPreference+":"+c.FishingTasks+":"+c.BaitPolicy))+":"+State.Hull+":"+SecondNetActive;
                if(signature!=flowCrewSignature){Flow.ResetCarryLearning();flowCrewSignature=signature;}
                UpdateManagementForecast();
            }
            int busy=People.Count(p=>p==netUnloader||p.Carrying!=null||OnDeck.Any(f=>f.ClaimedBy==p));
            Flow.Tick(dt,busy);Flow.TickOutput(dt,outputClaims.Count);
            if(dt>0 && Flow.Clock>=nextForecastSample && Forecast.Length==4)
            {nextForecastSample=(float)Flow.Clock+5;forecastHistory.Add(((float)Flow.Clock,Forecast.Select(f=>f.ValuePerMinute).ToArray()));if(forecastHistory.Count>120)forecastHistory.RemoveAt(0);}
        }
        void RecordLanding(FlowTelemetry.Kind kind,Species species,float kg) { State.PendingXpKg += Mathf.Max(0, kg); Flow.Record(kind,kg,NominalValue(species,kg)); }
        bool CaptainHaulingIn => Captain!=null&&(Captain.Carrying!=null||Captain==netUnloader||OnDeck.Any(f=>f.ClaimedBy==Captain));
        bool CaptainHaulingOut => Captain!=null&&outputClaims.ContainsKey(Captain);
        int CarrierCount => State.Crew.Count(c=>c.Role==CrewRole.Deckhand && c.WorkPreference!=DeckhandWork.Prep);
        int ProcessorCount => IsPrepFisher?Mathf.Min(2,State.Crew.Count(c=>c.Role==CrewRole.Deckhand&&c.WorkPreference==DeckhandWork.Prep)):0;
        float WaitingDeckKg => OnDeck.Sum(f=>f.Kg)+People.Where(p=>p.Carrying!=null).Sum(p=>p.Carrying.Kg);
        void ReportManagement()
        {
            if(Flow.Clock<flowNextReport)return;flowNextReport=(float)Flow.Clock+.5f;UpdateManagementForecast();
            stageDemand[0]=Flow.CountRate(FlowTelemetry.Kind.Rod,flowWindow)+Flow.CountRate(FlowTelemetry.Kind.Net,flowWindow)+Flow.CountRate(FlowTelemetry.Kind.Trap,flowWindow)+Flow.CountRate(FlowTelemetry.Kind.DeepLine,flowWindow);
            stageOutput[0]=stageDemand[0];stageCapacity[0]=Forecast.Sum(f=>f.FishPerMinute);
            stageDemand[1]=stageDemand[0];stageOutput[1]=Flow.CountRate(IsPrepFisher?FlowTelemetry.Kind.PrepInput:FlowTelemetry.Kind.Stored,flowWindow);
            // Both carrying stages share crew; split learned capacity by observed worker time.
            float totalBusy=(float)(Flow.CarryBusySeconds+Flow.OutputBusySeconds);
            float share=totalBusy>1?Mathf.Clamp((float)Flow.CarryBusySeconds/totalBusy,.15f,.85f):.5f;
            int carriers=CarrierCount+(IsTier5?ProcessorCount:0);
            stageCapacity[1]=Flow.CarryFishPace*(carriers+(CaptainHaulingIn?1:0))*(IsPrepFisher?share:1);
            stageDemand[2]=Flow.CountRate(FlowTelemetry.Kind.PrepInput,flowWindow);stageOutput[2]=Flow.CountRate(FlowTelemetry.Kind.Sorted,flowWindow)+Flow.CountRate(FlowTelemetry.Kind.Chum,flowWindow);
            stageCapacity[2]=TableFishCapacity;
            stageDemand[3]=IsPrepFisher?Flow.CountRate(FlowTelemetry.Kind.Sorted,flowWindow):stageOutput[1];stageOutput[3]=Flow.CountRate(FlowTelemetry.Kind.Stored,flowWindow);
            stageCapacity[3]=IsPrepFisher?Flow.OutputFishPace*(carriers+(CaptainHaulingOut?1:0))*(1-share):stageCapacity[1];
            bool warm=Flow.Clock<15;
            stageStatus[0]=HoldFull||IsPrepFisher&&ProcessingFull?2:warm?-1:0; // Beating a forecast is good play, not an equipment overload.
            stageStatus[1]=FlowTelemetry.Pressure(stageDemand[1],stageCapacity[1],WaitingDeckKg>.01f&&(carriers==0&&!CaptainHaulingIn||HoldFull||IsPrepFisher&&ProcessingFull),warm);
            stageStatus[2]=IsPrepFisher?FlowTelemetry.Pressure(stageDemand[2],stageCapacity[2],ProcessingInput.Count>0&&(ProcessorCount==0||!ProcessingInput.Any(f=>State.PrepOrders.Allows(f,false)||State.Chum<State.PrepOrders.ChumTarget&&State.PrepOrders.Allows(f,true))),warm):-2;
            stageStatus[3]=FlowTelemetry.Pressure(stageDemand[3],stageCapacity[3],HoldFull||ProcessingOutput.Count>0&&carriers==0&&!CaptainHaulingOut,warm);
        }
        static Color DashInk => Palette.Hex("080D3E");
        static Color DashBody => Palette.Hex("426AA7");
        static Color DashTeal => Palette.Hex("007579");
        static Color DashColor(int s) => s==2?Palette.Hex("F53E4B"):s==1?Palette.Hex("FFB535"):s==0?Palette.Hex("00B892"):Palette.Hex("8AA1B7");
        static string DashStatus(int s) => s==2?"Bottleneck":s==1?"Near Capacity":s==0?"Healthy":s==-2?"Not fitted":"Measuring";
        string[] StageNames => new[]{"Fishing","Hauling In","Processing","Hauling to Hold"};
        int Bottleneck => Enumerable.Range(1,3).Where(i=>stageStatus[i]==2).DefaultIfEmpty(-1).First();
        string Recommendation => ProcessingInput.Count>0&&!ProcessingInput.Any(f=>State.PrepOrders.Allows(f,false)||State.Chum<State.PrepOrders.ChumTarget&&State.PrepOrders.Allows(f,true))?"Allow queued fish\nin processing orders.":HoldFull?"Head home\nto sell your haul.":Bottleneck==2?"Add a processor\nor reduce intake.":Bottleneck==1?"Assign hauling help\nor slow fishing.":Bottleneck==3?"Help carry fish\ninto the hold.":Flow.Clock<15?"Let a full cycle\nfinish to measure.":"Capacity is available.\nWatch the queues.";
        Rect FishingFooter(int column,int row=0) => new Rect(iw-208-column*204,ih-70-row*62,192,54);
        void ManagementEntry()
        {
            if(CurrentMode!=Mode.Fishing||ManagementOpen||netOrdersOpen||PrepOrdersOpen||baitSettingsCrew!=null||tier5OperationsOpen||NetGameActive)return;
            // UI v2: the voyage HUD draws the Ops and Crew entries (VoyageInterfaceVoyage.cs).
        }
        float dashScale,dashX,dashY;
        string dashArt;
        Rect DR(float x,float y,float w,float h) => new(dashX+x*dashScale,dashY+y*dashScale,w*dashScale,h*dashScale);
        void DText(string id,float x,float y,float w,float h,string value,float size=22,Color? color=null,bool bold=false,TextAnchor align=TextAnchor.MiddleLeft)
        {
            value=System.Text.RegularExpressions.Regex.Replace(value,@"<size=(\d+)>",m=>"<size="+Mathf.Max(1,Mathf.RoundToInt(int.Parse(m.Groups[1].Value)*dashScale))+">");
            coastalUi.DashboardText("management/"+id,DR(x,y,w,h),value,size*dashScale,color??DashInk,bold,align);
        }
        void DPatch(string id,float x,float y,float w,float h,float sx,float sy,float sw,float sh)
            => coastalUi.DashboardRegion("management/patch/"+id,DR(x,y,w,h),dashArt,new Rect(sx,sy,sw,sh));
        void DButton(string id,Rect source,Action action) => Block(coastalUi.ReferenceButton("management/"+id,DR(source.x,source.y,source.width,source.height),action));
        void DBar(string id,Rect source,float fill,Color color)
        {
            coastalUi.DashboardShape("management/"+id+"/track",DR(source.x,source.y,source.width,source.height),Palette.Hex("DDE7EF"));
            coastalUi.DashboardShape("management/"+id+"/fill",DR(source.x,source.y,source.width,source.height),color,fill);
        }
        void InterfaceManagement()
        {
            ReportManagement();Block(new Rect(0,0,iw,ih));
            dashScale=Mathf.Min(iw/1672,ih/941);dashX=(iw-1672*dashScale)/2;dashY=(ih-941*dashScale)/2;
            dashArt=managementTab==0?"DASH1":"DASH2";
            // Use Mo's original pixels unchanged. Native fields replace every example value/chart.
            coastalUi.DashboardRegion("management/backdrop",new Rect(0,0,iw,ih),dashArt,new Rect(0,0,72,941));
            coastalUi.DashboardRegion("management/reference",DR(0,0,1672,941),dashArt,new Rect(0,0,1672,941));
            DPatch("tabs",950,39,500,76,1550,85,40,8);
            string[] tabs={"Income","Operations","Crew"};
            for(int i=0;i<3;i++) { int tab=i; float x=950+i*165;
                coastalUi.DashboardShape("management/tab/plate/"+i,DR(x,42,158,69),managementTab==i?DashTeal:Palette.Cream);
                DText("tab/label/"+i,x,42,158,69,tabs[i],27,managementTab==i?Color.white:DashInk,true,TextAnchor.MiddleCenter);
                DButton("tab/"+tabs[i].ToLowerInvariant(),new Rect(x,42,158,107),()=>{managementTab=tab;dashboardDetail=-1;});
            }
            DPatch("boat/subtitle",253,73,680,27,900,73,20,27);
            DText("boat/subtitle",253,72,680,29,State.HullDef.Name+(managementTab==0?" · Expected catch value by method":managementTab==1?" · Live throughput and bottlenecks":" · Set up roles and bait"),22,DashBody);
            DPatch("clock",1480,41,138,53,1550,85,40,8);
            DText("voyage",1489,39,131,27,$"Voyage {State.Voyage}",19,DashBody);
            DText("clock",1489,66,130,30,$"{(int)Flow.Clock/60:00}:{(int)Flow.Clock%60:00}",23,DashBody,true);
            coastalUi.DashboardShape("management/back/plate",DR(87,39,43,43),new Color(1,1,1,.94f));
            DText("back/text",87,36,43,46,"‹",39,DashBody,true,TextAnchor.MiddleCenter);
            DButton("close",new Rect(87,39,43,43),CloseManagement);
            if(managementTab==0)DashboardIncome();else if(managementTab==1)DashboardOperations();else DashboardCrew();
            if(dashboardDetail>=0)DashboardDetails();
        }
        void DFill(string id,Rect rect,Color color)=>coastalUi.Box(id+"/rect",rect,"",color,blocks:false);
        int selectedManagementCrew;
        void DashboardCrew()
        {
            DFill("management/crew/surface",DR(96,140,1536,801),Palette.Hex("F4EFE3"));
            var crew=State.Crew.ToArray();
            if(crew.Length==0) { DText("crew/empty",150,250,1300,100,"Hire fishers and deckhands at the Crew Office.",32); return; }
            selectedManagementCrew=Mathf.Clamp(selectedManagementCrew,0,crew.Length-1);
            DText("crew/heading",135,163,420,56,"Crew · "+crew.Length+" / "+State.HullDef.CrewCap,34,DashInk,true);
            for(int i=0;i<crew.Length;i++)
            {
                int index=i;float y=230+i*108;bool on=i==selectedManagementCrew;
                DFill("management/crew/selected/"+i,DR(128,y,400,107),on?DashTeal:Color.white);
                DText("crew/name/"+i,148,y+5,360,36,crew[i].Name,29,on?Color.white:DashInk,true);
                DText("crew/role/"+i,148,y+42,360,30,crew[i].RoleName,22,on?Color.white:DashBody);
                DButton("crew/select/"+i,new Rect(128,y,400,107),()=>selectedManagementCrew=index);
            }
            var c=crew[selectedManagementCrew];
            DText("crew/selected",578,165,980,54,c.Name+" · Set up roles",36,DashInk,true);
            if(c.Role==CrewRole.Fisherman)
            {
                DText("crew/help",578,225,980,64,"Tick the work this fisher may do. Changes apply after the current job.",25,DashBody);
                var tasks=new[]{FisherTask.Rods,FisherTask.Nets,FisherTask.Crabs,FisherTask.DeepLines};
                var labels=new[]{"Rods","Nets","Crab cages","Deep lines"};
                for(int i=0;i<4;i++)
                {
                    var task=tasks[i];bool on=c.Allows(task);float x=578+i%2*490,y=300+i/2*121;
                    bool fitted=task==FisherTask.Rods?FittedRodCount>0:task==FisherTask.Nets?FittedNetCount>0:task==FisherTask.Crabs?FittedTrapCount>0:DeepLinesActive;
                    DFill("management/crew/task/plate/"+i,DR(x,y,468,107),Color.white);
                    DFill("management/crew/task/box/"+i,DR(x+18,y+20,40,40),on?DashTeal:Palette.Hex("DDE7EF"));
                    DText("crew/task/mark/"+i,x+18,y+16,40,44,on?"✓":"",32,Color.white,true,TextAnchor.MiddleCenter);
                    DText("crew/task/label/"+i,x+76,y+8,375,38,labels[i],29,DashInk,true);
                    DText("crew/task/status/"+i,x+76,y+45,375,28,fitted?on?"Enabled":"Off":"Not fitted · choice saved",20,DashBody);
                    DButton("crew/task/"+task,new Rect(x,y,468,107),()=>ToggleFisherTask(c,task));
                }
                DText("crew/priority",578,552,980,76,"Ready nets / cages → bait deep lines → rods.\nDeep lines need self-made chum; deckhands collect the catch.",23,DashBody);
                DText("crew/bait/title",578,631,980,48,"Allowed bait",30,DashInk,true);
                var baits=new[]{BaitPermission.Scraps,BaitPermission.Worms,BaitPermission.Squid,BaitPermission.Chum};
                for(int i=0;i<4;i++)
                {
                    var bait=baits[i];bool on=(c.BaitPolicy&bait)!=0;float x=578+i*245;
                    DFill("management/crew/bait/plate/"+i,DR(x,686,225,107),on?DashTeal:Color.white);
                    DText("crew/bait/label/"+i,x,686,225,107,(on?"✓ ":"")+bait,26,on?Color.white:DashInk,true,TextAnchor.MiddleCenter);
                    DButton("crew/bait/"+bait,new Rect(x,686,225,107),()=>ToggleCrewBait(c,bait));
                }
                DText("crew/bait/help",578,813,980,65,"Rod bait follows these ticks. Deep lines need Chum allowed and in stock.\nAlready deployed lines keep their chum.",23,DashBody);
            }
            else
            {
                DText("crew/hand/help",578,235,980,80,"Choose a duty. Deckhands collect and carry catch; fishers operate gear.",27,DashBody);
                var duties=new[]{DeckhandWork.Fish,DeckhandWork.Nets,DeckhandWork.Prep};
                var names=new[]{"Haul catch","Net baskets first","Table / chum"};
                var help=new[]{"Collect deck catch and carry prepared fish to the hold.","Collect net baskets, then help haul other catch.","Make chum or prepare fish using the table orders; haul while waiting."};
                for(int i=0;i<3;i++)
                {
                    var duty=duties[i];float y=345+i*130;bool on=c.WorkPreference==duty;
                    DFill("management/crew/duty/plate/"+i,DR(578,y,958,110),on?DashTeal:Color.white);
                    DText("crew/duty/name/"+i,600,y+8,910,43,(on?"✓ ":"")+names[i],29,on?Color.white:DashInk,true);
                    DText("crew/duty/help/"+i,600,y+54,910,43,help[i],23,on?Color.white:DashBody);
                    DButton("crew/duty/"+duty,new Rect(578,y,958,110),()=>SetDeckhandWork(c,duty));
                }
                IButton("management/crew/table-orders",DR(578,768,958,107),"Table orders / chum "+State.Chum,()=>{CloseManagement();PrepOrdersOpen=true;},false,IsPrepFisher);
                DText("crew/hand/footer",578,880,980,30,"White 1 · Green 2 · Blue 3 chum. Purple and above are protected.",24,DashBody);
            }
        }
        void DashboardIncome()
        {
            DPatch("income/subtitle",1072,195,530,29,1525,222,45,10);
            DText("income/subtitle",1073,195,530,28,"Nominal catch value. No assumed preparation bonus.",22,DashBody);
            DPatch("total",1071,235,528,97,1608,235,8,97);
            DText("total",1075,231,514,96,$"€{ForecastIncome:N0}<size=45> / min</size>",88,DashTeal,true);
            float total=Mathf.Max(.001f,ForecastIncome);var shares=ForecastShares;
            var colors=new[]{Palette.Hex("2CA6D1"),Palette.Hex("FFAA24"),Palette.Hex("FF665D"),Palette.Hex("8365B5")};
            DFill("management/income/methods",DR(160,229,772,475),Palette.Hex("F4EFE3"));
            for(int i=0;i<Forecast.Length;i++)
            {
                var f=Forecast[i];float y=235+i*116;
                DText("method/name/"+i,190,y,360,36,f.Name,30,DashInk,true);
                DText("method/value/"+i,190,y+38,400,40,$"€{f.ValuePerMinute:N0} / min",33,DashTeal,true);
                DText("method/percent/"+i,764,y,135,40,$"{shares[i]}%",30,DashInk,true,TextAnchor.MiddleRight);
                DText("method/availability/"+i,190,y+80,700,27,f.Availability,22,DashBody);
                DBar("method/bar/"+i,new Rect(630,y+51,268,21),f.ValuePerMinute/total,colors[i]);
                int method=i;DButton("method/"+i,new Rect(169,y,760,110),()=>dashboardDetail=method==3?8:method);
            }
            int best=Enumerable.Range(0,Forecast.Length).Where(i=>Forecast[i].ValuePerMinute>0).OrderByDescending(i=>Forecast[i].ValuePerMinute).DefaultIfEmpty(-1).First();
            int margin=Enumerable.Range(0,Forecast.Length).Where(i=>Forecast[i].ValuePerMinute>0).OrderByDescending(i=>Forecast[i].Margin).DefaultIfEmpty(-1).First();
            // Stability is measured from real landing events; no fabricated winner at startup.
            var samples=Flow.Snapshot();int stable=-1;float least=float.MaxValue;
            for(int i=0;i<Forecast.Length;i++)
            {
                if(Forecast[i].InstalledCount==0)continue;
                var bins=new float[6];foreach(var e in samples)if((i==3?e.Type==FlowTelemetry.Kind.DeepLine:(int)e.Type==i)&&e.At>Flow.Clock-60)bins[Mathf.Clamp((int)((e.At-(Flow.Clock-60))/10),0,5)]+=e.Value;
                float mean=bins.Average();if(Flow.Clock<60||mean<=0)continue;float cv=bins.Sum(v=>(v-mean)*(v-mean))/6/(mean*mean);if(cv<least){least=cv;stable=i;}
            }
            int[] winners={best,margin,stable};
            for(int i=0;i<3;i++)
            {
                float y=407+i*94;
                DPatch("insight/name/"+i,1109,y+39,226,36,1288,y+69,36,7);
                DText("insight/name/"+i,1112,y+38,221,39,winners[i]<0?i<2?"None active":"Measuring":Forecast[winners[i]].Name,31,DashInk,true);
                DPatch("insight/help/"+i,1375,y+8,216,70,1594,y+8,6,70);
                DText("insight/help/"+i,1375,y+9,211,68,i==0?"Highest expected\ncatch value per minute.":i==1?"Estimated value after\nallocated operating costs.":stable<0?"Observe a minute\nto compare stability.":"Steadiest landed value\nover the last minute.",22,DashBody);
            }
            DPatch("chart/subtitle",228,745,900,28,1100,740,100,25);
            DText("chart/subtitle",230,745,1000,28,"Estimated income per minute by method over this voyage. Tap a method for catch odds.",22,DashBody);
            // Replace source sample chart including axes; render only observed forecast history.
            DPatch("chart/plot",168,774,1125,135,1200,744,40,14);
            float max=Mathf.Max(1,Forecast.Max(f=>f.ValuePerMinute),forecastHistory.Count>0?forecastHistory.Max(h=>h.values.Max()):0)*1.15f;
            for(int tick=0;tick<=4;tick++)
            {
                float y=876-tick*23.5f;
                DText("chart/tick/"+tick,171,y-13,55,27,$"{max*tick/4:0}",17,DashBody,false,TextAnchor.MiddleRight);
                coastalUi.Box("management/chart/grid/"+tick,DR(238,y,1048,1),"",Palette.Hex("DCE7F1"),blocks:false);
            }
            float end=Mathf.Max(60,(float)Flow.Clock),start=Mathf.Max(0,end-600);
            for(int tick=0;tick<=4;tick++)DText("chart/time/"+tick,214+tick*256,885,96,25,TimeLabel(Mathf.Lerp(start,end,tick/4f)),17,DashBody,false,TextAnchor.MiddleCenter);
            for(int method=0;method<Forecast.Length;method++)
            {
                var points=forecastHistory.Where(h=>h.at>=start).Select(h=>new Vector2((h.at-start)/(end-start),h.values[method]/max)).ToArray();
                coastalUi.DashboardPlot("management/chart/line/"+method,DR(238,782,1048,94),colors[method],points);
                float y=769+method*37;
                DPatch("chart/legend/"+method,1323,y,285,36,1574,762,18,8);
                DText("chart/legend/"+method,1325,y,280,34,Forecast[method].Name+" · €"+Forecast[method].ValuePerMinute.ToString("N0"),20,colors[method],true);
            }
        }
        static string TimeLabel(float seconds) => $"{(int)seconds/60:00}:{(int)seconds%60:00}";
        void DashboardOperations()
        {
            DPatch("ops/description",115,180,1434,31,1428,204,95,8);
            DText("ops/description",115,179,1434,33,IsPrepFisher?"Catch → haul to processing → prepare → carry to main hold. Tap any stage for live queues.":"Catch → haul directly to main hold. This boat has no processing station.",22,DashBody);
            int[] crew={State.Crew.Count(c=>c.Role==CrewRole.Fisherman)+1,CarrierCount+(CaptainHaulingIn?1:0),ProcessorCount,CarrierCount+(CaptainHaulingOut?1:0)};
            int[] equip={FittedRodCount+FittedNetCount+FittedTrapCount+FittedDeepLineCount,State.Hull>0?SecondNetActive?2:1:0,IsPrepFisher?2:0,1};
            for(int i=0;i<4;i++)
            {
                float x=new[]{114f,489f,859f,1229f}[i];
                DPatch("ops/help/"+i,x+118,267,212,33,x+320,267,4,33);
                DText("ops/help/"+i,x+127,266,204,35,i==0?"Catch fish at sea.":i==1?IsPrepFisher?"Bring catch to processing.":"Bring catch into the hold.":i==2?IsPrepFisher?"Sort fish / make chum.":"Bypassed on this boat.":"Transfer to main storage.",21,DashBody);
                DPatch("ops/rate/"+i,x+20,337,300,39,x+280,363,20,12);
                string rate=i==2&&!IsPrepFisher?"— / —":stageCapacity[i]>0?$"{stageDemand[i]:0.#} / {stageCapacity[i]:0.#}":$"{stageDemand[i]:0.#} / —";
                DText("ops/rate/"+i,x+23,336,298,43,$"<color=#{ColorUtility.ToHtmlStringRGB(DashColor(stageStatus[i]))}>{rate}</color><size=22> fish/min</size>",32,DashInk,true);
                DBar("ops/bar/"+i,new Rect(x+22,309,295,23),stageCapacity[i]>0?stageDemand[i]/stageCapacity[i]:stageStatus[i]==2?1:0,DashColor(stageStatus[i]));
                DPatch("ops/status/"+i,x+18,376,265,46,x+320,376,4,46);
                coastalUi.DashboardShape("management/ops/status/bg/"+i,DR(x+21,378,195,41),Color.Lerp(DashColor(stageStatus[i]),Color.white,.86f));
                coastalUi.DashboardShape("management/ops/status/dot/"+i,DR(x+39,390,18,18),DashColor(stageStatus[i]));
                DText("ops/status/"+i,x+72,378,139,42,DashStatus(stageStatus[i]),23,stageStatus[i]==1?Palette.Hex("D87C00"):DashColor(stageStatus[i]),true);
                DPatch("ops/cost/"+i,x+125,430,193,34,x+300,430,4,34);
                DText("ops/cost/"+i,x+132,430,173,34,$"€{DashboardCosts[i]:0.#} / min",24,DashInk,true);
                DPatch("ops/crew/"+i,x+72,477,244,32,x+320,477,4,32);
                DText("ops/crew/"+i,x+74,474,234,35,$"Crew {crew[i]}  |  Equip {equip[i]}",22,DashBody);
                int stage=i;DButton("stage/"+i,new Rect(x,217,337,302),()=>dashboardDetail=3+stage);
            }
            DPatch("bottleneck",211,659,235,69,449,659,6,69);
            DText("bottleneck",213,659,234,40,Bottleneck>=0?StageNames[Bottleneck]:Flow.Clock<15?"Measuring":"None",30,DashInk,true);
            DText("bottleneck/help",213,698,234,32,Bottleneck>=0?"Limiting your catch flow.":"Watch queues as work changes.",20,DashBody);
            DPatch("cost/total",589,651,220,47,766,706,34,30);
            DText("cost/total",591,649,220,49,$"€{ForecastCost:0.#}<size=27> / min</size>",40,DashTeal,true);
            DPatch("profit",952,650,237,49,1184,650,6,49);
            DText("profit",956,649,231,49,$"€{ForecastIncome-ForecastCost:0.#}<size=27> / min</size>",40,ForecastIncome-ForecastCost<0?DashColor(2):DashTeal,true);
            DPatch("fix",1310,648,245,95,1507,618,31,20);
            DText("fix",1317,648,236,59,Recommendation,26,DashInk,true);
            DText("fix/help",1317,708,236,34,"Tap for crew duties and help.",19,DashBody);
            DButton("recommendation",new Rect(1212,615,352,131),()=>dashboardDetail=7);
            DPatch("cost/chart",114,815,849,112,880,788,48,18);
            float max=Mathf.Max(1,DashboardCosts.Max()*1.18f);
            for(int tick=0;tick<=4;tick++)
            {
                float y=901-tick*20;
                DText("cost/tick/"+tick,112,y-10,39,23,$"{max*tick/4:0.#}",15,DashBody,false,TextAnchor.MiddleRight);
                coastalUi.Box("management/cost/grid/"+tick,DR(159,y,800,1),"",Palette.Hex("DCE7F1"),blocks:false);
            }
            for(int i=0;i<4;i++)
            {
                float h=DashboardCosts[i]/max*78,x=188+i*186;
                if(DashboardCosts[i]>.001f)coastalUi.Box("management/cost/bar/"+i,DR(x,901-h,130,h),"",DashColor(stageStatus[i]),blocks:false);
                DText("cost/bar/label/"+i,x,875-h,130,25,$"€{DashboardCosts[i]:0.#}",20,DashInk,true,TextAnchor.MiddleCenter);
                DText("cost/bar/name/"+i,x-24,904,178,25,StageNames[i],18,DashBody,false,TextAnchor.MiddleCenter);
            }
            // Finished output / shared limiting capacity, never an arbitrary display constant.
            float capacity=IsPrepFisher?Mathf.Min(stageCapacity[1],stageCapacity[2],stageCapacity[3]):stageCapacity[1];
            float efficiency=capacity>0?Mathf.Clamp01(stageOutput[3]/capacity):0;
            DPatch("efficiency",1068,807,162,134,1459,780,39,19);
            coastalUi.DashboardShape("management/efficiency/track",DR(1084,806,136,136),Palette.Hex("BDCADA"),1,true);
            coastalUi.DashboardShape("management/efficiency/value",DR(1084,806,136,136),Palette.Hex("00AB97"),efficiency,true);
            DText("efficiency/percent",1101,842,103,42,capacity>0?$"{efficiency:P0}":"—",35,DashInk,true,TextAnchor.MiddleCenter);
            DText("efficiency/label",1105,883,100,24,"Efficiency",16,DashBody,false,TextAnchor.MiddleCenter);
            DPatch("efficiency/help",1273,828,287,102,1513,788,24,21);
            DText("efficiency/help",1277,827,283,104,capacity<=0?"Learning shared hauling capacity. Complete several deliveries to measure efficiency.":$"Your stored output uses {efficiency:P0} of measured pipeline capacity. {ProcessingInput.Count} fish await processing; {ProcessingOutput.Count} await carrying.",22,DashBody);
        }
        void DashboardDetails()
        {
            Block(new Rect(0,0,iw,ih));coastalUi.Box("management/detail/shade",new Rect(0,0,iw,ih),"",new Color(.02f,.1f,.2f,.66f));
            var p=new Rect((iw-Mathf.Min(760,iw-32))/2,24,Mathf.Min(760,iw-32),ih-48);
            coastalUi.Box("management/detail/panel",p,"card-white");
            IButton("management/detail/close",new Rect(p.xMax-88,p.y+10,70,54),"X",()=>dashboardDetail=-1,false);
            string title;string body;
            if(dashboardDetail<3||dashboardDetail==8)
            {
                var f=Forecast[dashboardDetail==8?3:dashboardDetail];title=f.Name+" · expected catch";
                string mix=string.Join("\n",f.SpeciesCounts.OrderByDescending(v=>v.Value).Select(v=>$"{GameData.Get(v.Key).Name}: {(dashboardDetail==0?v.Value*100:dashboardDetail==8?v.Value*f.CycleFish:v.Value):0.#} fish"));
                if(dashboardDetail==8)mix+="\n\nLocal class odds:\n"+string.Join("\n",f.ClassOdds.OrderBy(v=>v.Key).Select(v=>CatchPresentation.Label(v.Key)+": "+v.Value.ToString("P1")));
                body=$"{State.HullDef.Name} · {f.Availability}\n~€{f.ValuePerMinute:0.#}/min · {f.FishPerMinute:0.#} fish/min\n"+(dashboardDetail==0?$"Per 100 catches: ~€{f.CycleValue:0}.\n":$"Per {(dashboardDetail==1?"haul":dashboardDetail==8?"deep-line cycle":"recovery")}: {f.CycleFish:0.#} fish, ~€{f.CycleValue:0}.\n")+mix+"\n\nBased on local catch probabilities, current bait, haul capacity and nominal prices. No freshness or market depletion deduction. Raw nominal value only: preparation adds value when actually completed. Only fitted gear with an operator produces a forecast. Good play can beat this baseline; enabled methods share each fisher’s time. Deep lines use 5% white, 5% green, 10% blue, 75% purple, 3% gold and 2% red. Missing local classes redistribute among available classes. Supplies must remain available.";
            }
            else
            {
                int stage=dashboardDetail==7&&Bottleneck>=0?Bottleneck:Mathf.Clamp(dashboardDetail-3,0,3);title=dashboardDetail==7?"Manage your bottleneck":StageNames[stage];
                body=$"{Recommendation.Replace('\n',' ')}\n\nActual output: {stageOutput[stage]:0.#} fish/min\nIncoming workload: {stageDemand[stage]:0.#} fish/min\nCapacity: {(stageCapacity[stage]>0?stageCapacity[stage].ToString("0.#"):"measuring")} fish/min\n\nDeck / being carried: {WaitingDeckKg:0.#} kg\nProcessing input: {ProcessingInput.Count} fish\nProcessing output: {ProcessingOutput.Count} fish\nMain hold: {HoldKg:0.#} / {State.CoolerCapacity:0} kg\n\nGreen: below 80%. Orange: 80–100%. Red: incoming work exceeds capacity, or a queue is blocked. Hauling estimates share the same crew; fishing is a probability forecast, not guaranteed output. Costs allocate contract fees per voyage, bait, net uses and fuel; they are estimates, not new charges.";
            }
            coastalUi.Label("management/detail/title",new Rect(p.x+24,p.y+12,p.width-128,50),title,26,DashInk,TextAnchor.UpperLeft);
            var content=coastalUi.Scroll("management/detail/scroll",new Rect(p.x+24,p.y+76,p.width-48,p.height-160),1400);
            coastalUi.Label("management/detail/body",new Rect(0,0,p.width-70,1380),body,20,DashBody,TextAnchor.UpperLeft,parent:content);
            float by=p.yMax-72;
            IButton("management/duties",new Rect(p.x+20,by,190,54),"Crew duties",()=>{dashboardDetail=-1;managementTab=2;},false,IsNetFisher);
            IButton("management/orders",new Rect(p.x+220,by,220,54),"Processing orders",()=>{CloseManagement();PrepOrdersOpen=true;},false,IsPrepFisher);
            IButton("management/help",new Rect(p.x+450,by,p.width-470,54),"Help carry",()=>{CloseManagement();HelpCarryProcessed();},false,ProcessingOutput.Count>0&&!HoldFull);
        }
    }
}

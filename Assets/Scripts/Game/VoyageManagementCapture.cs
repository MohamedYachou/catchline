using System.Collections;
using System.IO;
using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        bool NativeClick104(string id)
        {
            Canvas.ForceUpdateCanvases();
            var button=GetComponentsInChildren<UnityEngine.UI.Button>().FirstOrDefault(b=>b.name==id&&b.gameObject.activeInHierarchy);
            if(button==null)return false;
            var pointer=new UnityEngine.EventSystems.PointerEventData(UnityEngine.EventSystems.EventSystem.current)
                {position=RectTransformUtility.WorldToScreenPoint(null,button.transform.TransformPoint(((RectTransform)button.transform).rect.center)),button=UnityEngine.EventSystems.PointerEventData.InputButton.Left};
            var hits=new System.Collections.Generic.List<UnityEngine.EventSystems.RaycastResult>();
            UnityEngine.EventSystems.EventSystem.current.RaycastAll(pointer,hits);
            if(hits.Count==0)return false;
            var target=UnityEngine.EventSystems.ExecuteEvents.GetEventHandler<UnityEngine.EventSystems.IPointerClickHandler>(hits[0].gameObject);
            if(target!=button.gameObject){Debug.LogError("DEEP104 pointer obstructed: "+id+" by "+hits[0].gameObject.name);return false;}
            UnityEngine.EventSystems.ExecuteEvents.Execute(target,pointer,UnityEngine.EventSystems.ExecuteEvents.pointerClickHandler);return true;
        }
        IEnumerator CaptureDeep104(string directory)
        {
            Application.runInBackground=true;Directory.CreateDirectory(directory);
            captureFreeze=true;showTitle=paused=false;
            for(int layout=0;layout<3;layout++)
            {
                StartTier5Trial();captureFreeze=true;
                if(layout>0){HeadHome();for(int n=0;n<3000&&CurrentMode!=Mode.Harbour;n++)Tick(.05f);}
                if(layout==1){State.Coins=5000;if(!State.TryBuy(UpgradeId.ThirdDeepLine)){Debug.LogError("DEEP104 upgrade purchase failed");Application.Quit(5);yield break;}SyncUpgrades();ActiveSpot=SelectedSpot=4;Showcase(4,0);}
                if(layout==2){ConfigureTier5NetTeam();Showcase(0,0);}
                for(int n=0;n<3600;n++)Tick(.05f);
                foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
                {
                    Screen.SetResolution(size.x,size.y,false);for(int n=0;n<20;n++)yield return null;
                    CloseManagement();toastUntil=0;PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                    yield return CaptureFrame(directory,$"layout{layout}-boat-{size.x}");
                    if(!InvokeInterface("management/open")){Debug.LogError("DEEP104 entry missing");Application.Quit(5);yield break;}
                    foreach(int tab in new[]{0,1,2})
                    {
                        managementTab=tab;dashboardDetail=-1;flowNextReport=0;
                        if(tab==2)selectedManagementCrew=State.Crew.ToList().FindIndex(c=>c.Role==CrewRole.Fisherman);
                        PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                        yield return CaptureFrame(directory,$"layout{layout}-tab{tab}-{size.x}");
                    }
                    var member=State.Crew.ElementAt(selectedManagementCrew);var original=member.FishingTasks;
                    if(!NativeClick104("management/crew/task/Nets")||member.FishingTasks!=(original^FisherTask.Nets))
                    {Debug.LogError("DEEP104 native task toggle failed");Application.Quit(5);yield break;}
                    ToggleFisherTask(member,FisherTask.Nets);
                    selectedManagementCrew=State.Crew.ToList().FindIndex(c=>c.Role==CrewRole.Deckhand);
                    PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                    yield return CaptureFrame(directory,$"layout{layout}-deckhand-{size.x}");
                    if(!NativeClick104("management/crew/table-orders")){Debug.LogError("DEEP104 table orders not reachable");Application.Quit(5);yield break;}
                    PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                    yield return CaptureFrame(directory,$"layout{layout}-chum-{size.x}");
                    if(!NativeClick104("prep/chum/classes")){Debug.LogError("DEEP104 chum dropdown failed");Application.Quit(5);yield break;}
                    PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                    var purple=GetComponentsInChildren<UnityEngine.UI.Button>().First(b=>b.name=="prep/classes/chum/3");
                    if(purple.interactable || (State.PrepOrders.ChumClasses&56)!=0){Debug.LogError("DEEP104 purple chum protection failed");Application.Quit(5);yield break;}
                    yield return CaptureFrame(directory,$"layout{layout}-chum-classes-{size.x}");
                    PrepOrdersOpen=false;prepClassDropdown=0;OpenManagement();PrepareInterface(size.x,size.y);
                    var keyboard=UnityEngine.InputSystem.Keyboard.current;
                    if(keyboard!=null)
                    {
                        UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState(UnityEngine.InputSystem.Key.Escape));
                        yield return null;yield return null;
                        UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState());
                        if(ManagementOpen){Debug.LogError("DEEP104 native Escape failed");Application.Quit(5);yield break;}
                    }
                }
                CloseManagement();
            }
            Debug.Log("[Catchline] DEEP104 NATIVE CAPTURES PASSED");Application.Quit(0);
        }
        IEnumerator CaptureDashboard087(string directory)
        {
            Application.runInBackground=true;Directory.CreateDirectory(directory);
            foreach(int hull in new[]{4,3,2,1,0})
            {
                if(hull==4)StartTier5Trial();else if(hull==3)StartPrepBoatTrial();else if(hull==2)StartNetBoatTrial();
                else {NewGame();State.Hull=hull;State.Fuel=State.FuelCapacity;RebuildBoat(false);Showcase(0,0);}
                captureFreeze=true;showTitle=paused=false;for(int n=0;n<600;n++)Tick(.05f);
                foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
                {
                    Screen.SetResolution(size.x,size.y,false);for(int n=0;n<16;n++)yield return null;
                    CloseManagement();PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                    yield return CaptureFrame(directory,$"hull{hull}-entry-{size.x}");
                    if(!InvokeInterface("management/open")){Debug.LogError("DASH087 entry failed");Application.Quit(3);yield break;}
                    managementTab=0;flowNextReport=0;PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                    if(hull<4&&Forecast[2].ValuePerMinute!=0){Debug.LogError("DASH087 phantom crab forecast");Application.Quit(3);yield break;}
                    yield return CaptureFrame(directory,$"hull{hull}-income-{size.x}");
                    managementTab=1;PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                    yield return CaptureFrame(directory,$"hull{hull}-operations-{size.x}");
                }
            }
            Debug.Log("[Catchline] DASH087 NATIVE CAPTURES PASSED");Application.Quit(0);
        }
        IEnumerator CaptureDashboard087Real(string directory)
        {
            Application.runInBackground=true;Directory.CreateDirectory(directory);captureFreeze=true;showTitle=paused=false;
            int loadedHull=State.Hull;Debug.Log($"[Catchline] DASH087 REAL LOAD hull={loadedHull} save={GameState.SavePath}");
            if(State.UnsoldCatch.Count>0)SellHaul();SelectedSpot=0;SetSail();
            for(int n=0;n<3000&&CurrentMode!=Mode.Fishing;n++)Tick(.05f);
            if(CurrentMode!=Mode.Fishing){Debug.LogError("DASH087 real departure failed");Application.Quit(4);yield break;}
            for(int n=0;n<600;n++)Tick(.05f);
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                Screen.SetResolution(size.x,size.y,false);for(int n=0;n<16;n++)yield return null;
                CloseManagement();PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                yield return CaptureFrame(directory,"real-entry-"+size.x);
                if(!InvokeInterface("management/open")){Debug.LogError("DASH087 real entry failed");Application.Quit(4);yield break;}
                managementTab=0;flowNextReport=0;PrepareInterface(size.x,size.y);Visual(0);for(int n=0;n<8;n++)yield return null;
                if(loadedHull<4&&(FittedTrapCount!=0||Forecast[2].ValuePerMinute!=0||ForecastShares[2]!=0)){Debug.LogError("DASH087 real phantom crab");Application.Quit(4);yield break;}
                yield return CaptureFrame(directory,"real-income-"+size.x);
            }
            CloseManagement();HeadHome();for(int n=0;n<3000&&CurrentMode!=Mode.Harbour;n++)Tick(.05f);
            if(CurrentMode!=Mode.Harbour||State.Hull!=loadedHull){Debug.LogError("DASH087 real return failed");Application.Quit(4);yield break;}
            SaveGame();Debug.Log("[Catchline] DASH087 REAL SAVE PROBE PASSED hull="+State.Hull);Application.Quit(0);
        }
        // Existing opt-in flag retained for backwards compatibility; entirely save-isolated.
        IEnumerator CaptureManagement(string directory)
        {
            Application.runInBackground=true;Directory.CreateDirectory(directory);
            foreach(var size in new[]{new Vector2Int(1672,941),new Vector2Int(1440,900),new Vector2Int(844,390),new Vector2Int(1024,768)})
            {
                StartTier5Trial();captureFreeze=true;Screen.SetResolution(size.x,size.y,false);
                for(int n=0;n<20;n++)yield return null;
                CloseManagement();Visual(0);for(int n=0;n<8;n++)yield return null;
                yield return CaptureFrame(directory,"entry-"+size.x);
                OpenManagement();managementTab=1;Visual(0);for(int n=0;n<8;n++)yield return null;
                yield return CaptureFrame(directory,"warmup-"+size.x);
                for(int n=0;n<1800;n++)Tick(.05f);
                OpenManagement();managementTab=1;flowNextReport=0;Visual(0);for(int n=0;n<8;n++)yield return null;
                yield return CaptureFrame(directory,"operations-"+size.x);
                managementTab=0;Visual(0);for(int n=0;n<8;n++)yield return null;
                yield return CaptureFrame(directory,"income-"+size.x);
                dashboardDetail=1;Visual(0);for(int n=0;n<8;n++)yield return null;
                yield return CaptureFrame(directory,"odds-"+size.x);
                dashboardDetail=-1;managementTab=1;
                if(size.x==1672||size.x==844)
                {
                    State.Deckhand=null;State.ExtraCrew.RemoveAll(c=>c.Role==CrewRole.Deckhand);SyncCrew();
                    foreach(var p in People)p.Stop();ClearPrepWork();LandFish(Rods[0],Species.Cod,4);
                    DeliverCatch(new CaughtFish{Species=Species.Cod,Kg=4,StowedAt=SimTime});
                    Tick(.1f);OpenManagement();flowNextReport=0;Visual(0);for(int n=0;n<8;n++)yield return null;
                    yield return CaptureFrame(directory,"blocked-"+size.x);
                    while(!HoldFull)TryStore(new CaughtFish{Species=Species.Cod,Kg=6,StowedAt=SimTime},false);
                    flowNextReport=0;Visual(0);for(int n=0;n<8;n++)yield return null;
                    yield return CaptureFrame(directory,"full-"+size.x);
                }
            }
            // Smaller boat routing is a separate real gameplay state.
            NewGame();Showcase(0,0);captureFreeze=true;Screen.SetResolution(1440,900,false);
            for(int n=0;n<20;n++)yield return null;
            OpenManagement();managementTab=1;Visual(0);for(int n=0;n<8;n++)yield return null;
            yield return CaptureFrame(directory,"small-boat-1440");
            Debug.Log("[Catchline] DASH082 NATIVE CAPTURES COMPLETE");Application.Quit(0);
        }
    }
}

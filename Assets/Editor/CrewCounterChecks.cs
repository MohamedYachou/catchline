using System;
using System.Reflection;
using System.Linq;
using Catchline.Game;
using UnityEngine;
using UnityEditor.SceneManagement;
namespace Catchline.EditorTools
{
    public static class CrewCounterChecks
    {
        static void Check(bool ok,string why){if(!ok)throw new Exception("CREW046: "+why);}
        public static void ValidateAndBuild()
        {
            ArtImport.BuildLibrary();EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("Crew counters isolated").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartPrepBoatTrial();g.Showcase(-1,0);
            g.State.Deckhand=null;g.State.ExtraCrew.Clear();g.State.Coins=1000;
            typeof(VoyageGame).GetField("hudTab",BindingFlags.Instance|BindingFlags.NonPublic).SetValue(g,VoyageGame.HudTab.CrewOffice);
            typeof(VoyageGame).GetField("panelOpen",BindingFlags.Instance|BindingFlags.NonPublic).SetValue(g,true);
            Action<CrewRole,string> click=(role,action)=>{g.PrepareInterface(844,390);Check(g.InvokeInterface("crew/count/"+role+"/"+action),"callback "+action);};
            int coins=g.State.Coins;click(CrewRole.Fisherman,"plus");Check(g.State.CrewCount==1 && g.State.Coins==coins-g.State.Crew.First().Fee,"hire exact fee");
            click(CrewRole.Fisherman,"minus");Check(g.State.CrewCount==0 && g.State.Coins==coins,"full refund");
            click(CrewRole.Deckhand,"plus");click(CrewRole.Fisherman,"plus");click(CrewRole.Deckhand,"plus");click(CrewRole.Fisherman,"plus");Check(g.State.CrewCount==4,"shared cap");
            var method=typeof(VoyageGame).GetMethod("ChangeCrewCounter",BindingFlags.Instance|BindingFlags.NonPublic);
            Check(!(bool)method.Invoke(g,new object[]{CrewRole.Fisherman,true}),"cannot exceed cap");
            for(int i=0;i<2;i++){click(CrewRole.Fisherman,"minus");click(CrewRole.Deckhand,"minus");}
            Check(g.State.Coins==coins && g.State.CrewCount==0,"both roles reversible");
            Check(!(bool)method.Invoke(g,new object[]{CrewRole.Deckhand,false}),"empty minus safe");
            g.State.Coins=0;Check(!(bool)method.Invoke(g,new object[]{CrewRole.Fisherman,true}),"no money no hire");
            UnityEngine.Object.DestroyImmediate(g.gameObject);Debug.Log("[Catchline] CREW046 CHECKS PASSED");PrepFisherChecks.BuildPreview();Debug.Log("[Catchline] Snapshot written to Logs/crew046");
        }
    }
}


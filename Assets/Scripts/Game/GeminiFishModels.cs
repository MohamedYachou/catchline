using UnityEngine;

namespace Catchline.Game
{
    // Fit the authored FBX using explicit nose/tail markers. Longest-axis fitting
    // turns wide ray wings and tall sunfish fins into the heading, so it is unsuitable here.
    public static class GeminiFishModels
    {
        public static bool Horizontal(Species species) => species is Species.SpottedEagleRay or Species.BlueSpottedStingray or Species.GiantDevilManta or Species.Monkfish;
        public static void Fit(GameObject model,float length,Species species)
        {
            var nose=ArtLibrary.Find(model,"Nose");var tail=ArtLibrary.Find(model,"TailEnd");
            if(nose==null||tail==null){ArtLibrary.AimAlong(model,Vector3.forward,length);return;}
            var heading=model.transform.InverseTransformVector(nose.position-tail.position);
            model.transform.localRotation=Quaternion.FromToRotation(heading,Vector3.forward);
            if(!Horizontal(species))model.transform.localRotation=Quaternion.Euler(0,0,90)*model.transform.localRotation;
            var toParent=model.transform.parent.worldToLocalMatrix;var bounds=new Bounds();bool any=false;
            foreach(var mf in model.GetComponentsInChildren<MeshFilter>())
            {
                var b=mf.sharedMesh.bounds;var matrix=toParent*mf.transform.localToWorldMatrix;
                for(int i=0;i<8;i++)
                {
                    var p=matrix.MultiplyPoint3x4(b.center+Vector3.Scale(b.extents,new Vector3((i&1)==0?-1:1,(i&2)==0?-1:1,(i&4)==0?-1:1)));
                    if(!any){bounds=new Bounds(p,Vector3.zero);any=true;}else bounds.Encapsulate(p);
                }
            }
            if(!any||bounds.size.z<.001f)return;
            float scale=length/bounds.size.z;model.transform.localScale=Vector3.one*scale;model.transform.localPosition=-bounds.center*scale;
        }
    }
}

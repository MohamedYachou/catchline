using UnityEngine;

namespace Catchline.Game
{
    // Sample imported transform clips on our explicit voyage clock, including paused capture clocks.
    sealed class RodViewAnimation
    {
        readonly RodViewArt art;
        readonly GameObject model;
        readonly Transform[] transforms;
        readonly Vector3[] bindPosition, shownPosition, fromPosition;
        readonly Quaternion[] bindRotation, shownRotation, fromRotation;
        readonly Transform[] bendBones = new Transform[8];
        readonly float[] bendDegrees = { .57f, 2.01f, 3.44f, 5.16f, 7.45f, 9.74f, 12.61f, 14.90f };
        AnimationClip previous;
        float transition;
        public readonly Transform Tip;

        public RodViewAnimation(RodViewArt data, GameObject instance)
        {
            art = data; model = instance;
            foreach (var animator in model.GetComponentsInChildren<Animator>()) animator.enabled = false;
            foreach (var animation in model.GetComponentsInChildren<Animation>()) animation.enabled = false;
            transforms = model.GetComponentsInChildren<Transform>(true);
            int n = transforms.Length;
            bindPosition = new Vector3[n]; shownPosition = new Vector3[n]; fromPosition = new Vector3[n];
            bindRotation = new Quaternion[n]; shownRotation = new Quaternion[n]; fromRotation = new Quaternion[n];
            for (int i = 0; i < n; i++)
            {
                bindPosition[i] = shownPosition[i] = transforms[i].localPosition;
                bindRotation[i] = shownRotation[i] = transforms[i].localRotation;
            }
            for (int i = 0; i < 8; i++) bendBones[i] = ArtLibrary.Find(instance, "Rod_0" + (i + 1));
            Tip = ArtLibrary.Find(instance, "LineTip");
        }
        public void Sample(Rod rod, float dt)
        {
            string name; float clock;
            if (rod.State == RodState.Flying) { name = "Cast"; clock = rod.CastAge / Rod.ViewCastSeconds * .9f; }
            else if (rod.ReadingResult == StrikeResult.Hooked)
            {
                float age = rod.ResultAge;
                if (age < .25f) { name = "Strike"; clock = age; }
                else if (age < rod.ThrashSeconds) { name = "Reel"; clock = Mathf.Repeat(age - .25f, .8f); }
                else { name = "Lift"; clock = Mathf.Clamp01((age - rod.ThrashSeconds) / Rod.LiftSeconds) * 1.2f; }
            }
            else if (rod.ReadingResult.HasValue) { name = "Hold"; clock = 0; }
            else if (rod.Reading.Phase == FishPhase.Nibble) { name = "Twitch"; clock = Mathf.Repeat(rod.Reading.PhaseTime, .4f); }
            else { name = rod.Reading.Phase == FishPhase.Approach ? "Idle" : "Hold"; clock = Mathf.Repeat(rod.CastAge, name == "Idle" ? 2 : 1); }
            var clip = art.Clip(name);
            if (clip == null) return;
            if (clip != previous)
            {
                for (int i = 0; i < transforms.Length; i++) { fromPosition[i] = shownPosition[i]; fromRotation[i] = shownRotation[i]; }
                transition = previous == null ? .12f : 0; previous = clip;
            }
            transition = Mathf.Min(.12f, transition + dt);
            for (int i = 0; i < transforms.Length; i++)
            { transforms[i].localPosition = bindPosition[i]; transforms[i].localRotation = bindRotation[i]; }
            clip.SampleAnimation(model, Mathf.Clamp(clock, 0, clip.length));
            float blend = Mathf.SmoothStep(0, 1, transition / .12f);
            for (int i = 0; i < transforms.Length; i++)
            {
                shownPosition[i] = Vector3.Lerp(fromPosition[i], transforms[i].localPosition, blend);
                shownRotation[i] = Quaternion.Slerp(fromRotation[i], transforms[i].localRotation, blend);
                transforms[i].localPosition = shownPosition[i]; transforms[i].localRotation = shownRotation[i];
            }
            for (int i = 0; i < 8; i++)
                if (bendBones[i] != null) bendBones[i].localRotation *= Quaternion.AngleAxis(bendDegrees[i] * rod.Reading.RodPull, Vector3.right);
        }
    }
}

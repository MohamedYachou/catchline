using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // Townsfolk (harbour plan to-do): two people from the town stroll the quay in front of the shops, stop now and then
    // to look at the boats, and turn back at the ends. They share the crew skeleton, so the crew's own Walk and Idle
    // clips drive them. Scenery only: no collision, no effect on play.
    public partial class VoyageGame
    {
        static readonly string[] Townsfolk = { "Town_OldWoman", "Town_Walker", "Town_Fisherman", "Town_Kid", "Town_Shopkeeper" };

        void DressTownsfolk(Transform root, ArtLibrary lib, float quayTop)
        {
            var prefab = lib.M("Townsfolk");
            if (prefab == null || lib.CrewClips == null) return;
            var clips = new Dictionary<string, AnimationClip>();
            foreach (var clip in lib.CrewClips) { var parts = clip.name.Split('|'); clips[parts[parts.Length - 1]] = clip; }
            if (!clips.ContainsKey("Walk") || !clips.ContainsKey("Idle")) return;
            // Lanes between the bollards (z 2.6) and the lamp posts (z 4); the west end stops short of the slipway beach.
            var lanes = new[] { (z: 3.05f, from: -26f, to: 9f), (z: 3.5f, from: -24f, to: 6.5f) };
            int first = Random.Range(0, Townsfolk.Length);
            for (int i = 0; i < lanes.Length; i++)
            {
                string who = Townsfolk[(first + i * 2) % Townsfolk.Length];
                // The clips key the rig's own root, so the walker turns a holder above it (as DeckActors does).
                var holder = new GameObject(who).transform; holder.SetParent(root, false);
                var go = ArtLibrary.Spawn(prefab, holder, Vector3.zero, Quaternion.identity);
                foreach (var child in go.GetComponentsInChildren<Transform>(true))
                    if (child.name.StartsWith("Town_")) child.gameObject.SetActive(child.name == who);
                var automatic = go.GetComponent<Animation>();
                if (automatic != null) automatic.enabled = false;
                var walker = holder.gameObject.AddComponent<TownWalker>();
                walker.Setup(go, clips["Walk"], clips["Idle"], quayTop, lanes[i].z, lanes[i].from, lanes[i].to, who == "Town_Kid" ? 1.15f : who == "Town_OldWoman" ? .75f : .95f, i);
            }
        }
    }

    public class TownWalker : MonoBehaviour
    {
        AnimationClip walk, idle;
        GameObject rig;
        float y, z, from, to, speed, x, target, pause, poseTime;
        bool stopped;
        Quaternion facing;
        System.Random rng;

        float R(float a, float b) => a + (float)rng.NextDouble() * (b - a);

        public void Setup(GameObject person, AnimationClip walkClip, AnimationClip idleClip, float quayTop, float lane, float west, float east, float pace, int seed)
        {
            rig = person; walk = walkClip; idle = idleClip; y = quayTop; z = lane; from = west; to = east; speed = pace;
            rng = new System.Random(seed * 7919 + System.Environment.TickCount);
            x = R(from, to); target = rng.NextDouble() < .5 ? from : to;
            facing = Quaternion.Euler(0, target > x ? 90 : -90, 0);
            Place(0);
        }

        void Update() => Place(Mathf.Min(Time.deltaTime, .1f));
        public void Tick(float dt) => Place(dt); // renders and checks
        public bool Stopped => stopped;

        void Place(float dt)
        {
            if (walk == null) return;
            if (stopped)
            {
                if ((pause -= dt) <= 0) { stopped = false; poseTime = 0; }
            }
            else
            {
                float step = speed * dt, gap = target - x;
                if (Mathf.Abs(gap) <= step)
                {
                    x = target; target = target == to ? from : to;
                    stopped = true; pause = R(2f, 4f); poseTime = 0;
                }
                else
                {
                    x += Mathf.Sign(gap) * step;
                    // Now and then they stop to look out at the boats.
                    if (rng.NextDouble() < dt / 9f) { stopped = true; pause = R(2.5f, 5.5f); poseTime = 0; }
                }
            }
            // Yaw 180 looks out over the water (south, -Z); 90 walks east.
            var want = Quaternion.Euler(0, stopped ? 180 : target > x ? 90 : -90, 0);
            facing = Quaternion.RotateTowards(facing, want, 240f * dt);
            transform.localPosition = new Vector3(x, y, z);
            transform.localRotation = facing;
            poseTime += dt * (stopped ? 1 : speed / .95f);
            var clip = stopped ? idle : walk;
            clip.SampleAnimation(rig, Mathf.Repeat(poseTime, clip.length));
        }
    }
}

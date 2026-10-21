using System;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public const float NetHaulRedTension = .85f;
        public bool NetGameActive => netGameComplete != null;
        public bool NetGameSetting { get; private set; }
        public float NetGamePhase => Mathf.PingPong(netGameAge * .8f, 1f);
        public float NetGameProgress { get; private set; }
        public float NetGameTension { get; private set; }
        public int NetGameDamage => netCycleMistakes;
        public bool NetGameHeld => netPullFlash > 0; // Visual pulse only, never held input.
        float netGameAge, netTapCooldown, netPullFlash;
        int primaryNetCycleMistakes, secondNetCycleMistakes;
        int netCycleMistakes { get => netGameRig == 1 ? secondNetCycleMistakes : primaryNetCycleMistakes; set { if (netGameRig == 1) secondNetCycleMistakes = value; else primaryNetCycleMistakes = value; } }
        bool netTapPending;
        Person netGamePerson;
        Action netGameComplete, netGameCancel, netGameFail;

        // A press queues one pull/cast. Holding generates no repeat input.
        public bool TapNetGame()
        {
            if (!NetGameActive || netTapPending || netTapCooldown > 0) return false;
            netTapPending = true;
            return true;
        }

        void BeginNetGame(Person person, bool setting, Action complete, Action cancel, Action fail, int rig = 0)
        {
            netGameRig = rig;
            netGamePerson = person; NetGameSetting = setting;
            netGameComplete = complete; netGameCancel = cancel; netGameFail = fail;
            NetGameProgress = 0; NetGameTension = .22f;
            netGameAge = netTapCooldown = netPullFlash = 0; netTapPending = false;
            person.Do(setting ? "Setting net" : "Winching net", float.MaxValue, null, () =>
            { if (NetGameActive && netGamePerson == person) CancelNetHaulGame(); });
        }

        public void CancelNetHaulGame()
        {
            if (!NetGameActive)
            {
                if ((Net is NetState.Hauling or NetState.Setting) && netWorker == Captain) Captain.Stop();
                else if ((SecondNet is NetState.Hauling or NetState.Setting) && secondNetWorker == Captain) Captain.Stop();
                return;
            }
            var person = netGamePerson; var cancel = netGameCancel;
            ClearNetHaulGame(); person?.Stop(); cancel?.Invoke();
        }

        void ClearNetHaulGame()
        {
            netGameComplete = netGameCancel = netGameFail = null; netGamePerson = null;
            netTapPending = false; NetGameSetting = false;
            NetGameProgress = NetGameTension = netGameAge = netTapCooldown = netPullFlash = 0;
        }

        void ResetNetHaulGame()
        {
            var person = netGamePerson; ClearNetHaulGame(); person?.Stop();
        }

        void FinishNetGame(bool torn)
        {
            var person = netGamePerson; var callback = torn ? netGameFail : netGameComplete;
            ClearNetHaulGame(); person?.Stop(); callback?.Invoke();
        }

        void TickNetHaulGame(float dt)
        {
            if (!NetGameActive) return;
            if (State.Hull == 0 || CurrentMode != Mode.Fishing || (netGameRig == 1 ? secondNetWorker : netWorker) != netGamePerson ||
                (netGameRig == 1 ? SecondNet : Net) != (NetGameSetting ? NetState.Setting : NetState.Hauling))
            { CancelNetHaulGame(); return; }
            while (dt > 0 && NetGameActive)
            {
                float step = Mathf.Min(.05f, dt); dt -= step;
                netGameAge += step;
                netTapCooldown = Mathf.Max(0, netTapCooldown - step);
                netPullFlash = Mathf.Max(0, netPullFlash - step);
                if (!NetGameSetting)
                {
                    NetGameTension = Mathf.Max(0, NetGameTension - .24f * step);
                    // Keep the line working: low-tension pecking cannot win.
                    float slip = NetGameTension >= NetHaulRedTension ? .36f :
                        Mathf.Lerp(.12f, .012f, Mathf.InverseLerp(.25f, .68f, NetGameTension));
                    NetGameProgress = Mathf.Max(0, NetGameProgress - slip * step);
                }
                if (!netTapPending) continue;
                netTapPending = false;
                netTapCooldown = NetGameSetting ? .45f : .12f;
                netPullFlash = .2f;
                if (NetGameSetting)
                {
                    if (NetGamePhase >= .35f && NetGamePhase <= .65f) NetGameProgress += 1f / 3;
                    else { netCycleMistakes++; NetGameProgress = Mathf.Max(0, NetGameProgress - 1f / 3); }
                }
                else
                {
                    NetGameTension = Mathf.Clamp01(NetGameTension + .18f);
                    if (NetGameTension >= NetHaulRedTension)
                    {
                        netCycleMistakes++;
                        NetGameProgress = Mathf.Max(0, NetGameProgress - .18f);
                    }
                    else NetGameProgress += Mathf.Lerp(.025f, .14f, Mathf.InverseLerp(.25f, .76f, NetGameTension));
                }
                if (netCycleMistakes >= 2) { FinishNetGame(true); continue; }
                if (NetGameProgress >= .999f) FinishNetGame(false);
            }
        }
    }
}

# Recovered night queue — 2026-10-15

The October14 runner incorrectly wrote DONE after two failed attempts. Logs show exit1 for tasks05–08; tasks06–08 exhausted usage limits immediately. Those markers were removed. The runner now stops with a nonzero status and creates no marker on failure. Isolated stub tests cover failure and success (`queue-validation.json`).

- Task05: recovered partial composition work, completed review sheets, validated 39 new sprites / 83 total. Original44, existing models, Scripts and Scenes unchanged. Complete.
- Task06: crew rig build and export validation in progress. No done marker until checked.
- Task07: not implemented; pending.
- Task08: not implemented; pending.

No queue process was restarted. Scoped commits are prepared for parent review; no push.

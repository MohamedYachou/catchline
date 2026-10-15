#!/usr/bin/env bash
# Runs Codex through the night queue. Only a zero exit status creates a done marker.
# Safe to restart: finished tasks are skipped. Log: Art/TASKS/queue.log
cd /mnt/c/Users/momoy/Projects/Catchline-art-style || exit 1
mkdir -p Art/TASKS/done
QUEUE="05-ui-pass-2 06-crew-rig 07-upgrade-visuals-and-world-polish 08-day-boat-and-textures"
for t in $QUEUE; do
  [ -f "Art/TASKS/done/$t" ] && continue
  echo "$(date '+%F %T') START $t" >> Art/TASKS/queue.log
  for attempt in 1 2; do
    codex exec --approve-for-me -c sandbox_workspace_write.network_access=true -C "$PWD" \
      "You are Catchline's art lead, continuing on branch art/style-pass (this worktree). Read Art/STYLE.md and the latest REPORT files, then do everything in Art/TASKS/$t.md. Blender for Windows: /mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe (headless Python is fine). Do not open Unity; do not touch Assets/Scripts or Assets/Scenes. Keep existing FBX names, part names and pivots. Commit and git push origin art/style-pass after each part. Finish with a short report: new files, new M_ names, anything unfinished." \
      > "Art/TASKS/$t-log.txt" 2>&1
    code=$?
    echo "$(date '+%F %T') $t attempt $attempt exit $code" >> Art/TASKS/queue.log
    [ $code -eq 0 ] && break
  done
  if [ "$code" -ne 0 ]; then
    echo "$(date '+%F %T') FAILED $t exit $code; queue stopped, task remains pending" >> Art/TASKS/queue.log
    exit "$code"
  fi
  printf 'completed=%s\nexit=0\n' "$(date -Iseconds)" > "Art/TASKS/done/$t"
  echo "$(date '+%F %T') DONE $t" >> Art/TASKS/queue.log
done
echo "$(date '+%F %T') QUEUE EMPTY" >> Art/TASKS/queue.log

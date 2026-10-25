#!/bin/bash
# Keeps Codex 2 (WSL) working: whenever no run is active, start a FRESH session (small context) with the
# standing CONTINUE order. A run that ends within 3 minutes means an empty quota or an error: wait 10 minutes.
# Stop: create /mnt/c/Users/momoy/Projects/Catchline/Art/Models/CrewV2/_STOP-WATCHDOGS
cd /mnt/c/Users/momoy/Projects/Catchline || exit 1
THREAD=01a13eac-e066-72e2-b226-f7f85c5cf5d4
LOG=Art/Models/CrewV2/_codex2-watchdog.log
while [ ! -f Art/Models/CrewV2/_STOP-WATCHDOGS ]; do
  if pgrep -f "_codex2-last-message" >/dev/null; then sleep 60; continue; fi
  # Model and effort are re-read every launch from docs/tools/codex-model.conf (Mo: Sol 6.1 medium).
  MODEL=$(sed -n 's/^MODEL=//p' docs/tools/codex-model.conf | tr -d '\r'); EFFORT=$(sed -n 's/^EFFORT=//p' docs/tools/codex-model.conf | tr -d '\r')
  start=$(date +%s); echo "$(date '+%F %T') launch $MODEL $EFFORT" >> "$LOG"
  /home/mo/.local/bin/codex exec -C /mnt/c/Users/momoy/Projects/Catchline ${MODEL:+-m "$MODEL"} -c model_reasoning_effort="\"${EFFORT:-high}\"" -c model_auto_compact_token_limit=100000 \
    -o Art/Models/CrewV2/_codex2-last-message.txt - < Art/Source/UIv2/CONTINUE-CODEX2.txt > /tmp/codex2-watchdog-run.log 2>&1
  code=$?; took=$(( $(date +%s) - start ))
  echo "$(date '+%F %T') exit $code after ${took}s: $(tail -c 300 /tmp/codex2-watchdog-run.log | tr '\n' ' ')" >> "$LOG"
  [ "$took" -lt 180 ] && sleep 600
done
echo "$(date '+%F %T') stop file found, watchdog exits" >> "$LOG"

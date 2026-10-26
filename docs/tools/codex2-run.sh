#!/bin/bash
# ONE Codex 2 (WSL) run: a FRESH session (small context) with the standing CONTINUE order. Mo (10-26): Codex never
# starts by itself, only a Claude starts it, with `team start codex2`. Nothing relaunches this run when it ends; the
# team guard reads the exit line below and rings the lead Claude, who reviews and decides whether to start the next.
cd /mnt/c/Users/momoy/Projects/Catchline || exit 1
LOG=Art/Models/CrewV2/_codex2-watchdog.log
if pgrep -f "_codex2-last-message" >/dev/null; then echo "codex2 is already running"; exit 1; fi
# Model and effort are re-read every launch from docs/tools/codex-model.conf (Mo: Sol 6.1 medium).
MODEL=$(sed -n 's/^MODEL=//p' docs/tools/codex-model.conf | tr -d '\r'); EFFORT=$(sed -n 's/^EFFORT=//p' docs/tools/codex-model.conf | tr -d '\r')
start=$(date +%s); echo "$(date '+%F %T') launch $MODEL $EFFORT (started by ${TEAM_STARTER:-a Claude})" >> "$LOG"
/home/mo/.local/bin/codex exec -C /mnt/c/Users/momoy/Projects/Catchline ${MODEL:+-m "$MODEL"} -c model_reasoning_effort="\"${EFFORT:-high}\"" -c model_auto_compact_token_limit=100000 \
  -o Art/Models/CrewV2/_codex2-last-message.txt - < Art/Source/UIv2/CONTINUE-CODEX2.txt > /tmp/codex2-watchdog-run.log 2>&1
code=$?; took=$(( $(date +%s) - start ))
echo "$(date '+%F %T') exit $code after ${took}s: $(tail -c 300 /tmp/codex2-watchdog-run.log | tr '\n' ' ')" >> "$LOG"

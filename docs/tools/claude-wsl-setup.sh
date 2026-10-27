#!/usr/bin/env bash
# Makes the WSL Claude (Claude L) share Claude W's instructions, memory and skills for Catchline, and report its
# plan usage into ClaudeCom.md through its status line. Safe to run again.
set -euo pipefail
WIN=/mnt/c/Users/momoy/.claude
PROJ=/mnt/c/Users/momoy/Projects/Catchline

# 1. Global instructions: import the Windows ones (SuperAI role, governance, backups).
grep -q "$WIN/CLAUDE.md" ~/.claude/CLAUDE.md 2>/dev/null || cat >> ~/.claude/CLAUDE.md <<EOF

# Shared with Claude W (Windows)
Mo's Windows-side global instructions apply here too (paths there are Windows paths; /mnt/c/... in WSL):
@$WIN/CLAUDE.md
EOF

# 2. Memory: the Catchline project memory is the same folder on both sides.
MEM=~/.claude/projects/-mnt-c-Users-momoy-Projects-Catchline
mkdir -p "$MEM"
if [ ! -L "$MEM/memory" ]; then
  [ -d "$MEM/memory" ] && mv "$MEM/memory" "$MEM/memory.wsl-backup"
  ln -s "$WIN/projects/C--Users-momoy-Projects-Catchline/memory" "$MEM/memory"
fi

# 3. Skills Claude W has and WSL lacks.
for s in "$WIN"/skills/*/; do
  name=$(basename "$s")
  [ -e ~/.claude/skills/"$name" ] || ln -s "$s" ~/.claude/skills/"$name"
done

# 4. Status line: the team usage bars (reads the team guard's cache; ClaudeCom.md is retired).
python3 - <<EOF
import json, os
p = os.path.expanduser("~/.claude/settings.json")
s = json.load(open(p))
s["statusLine"] = {"type": "command", "command": "/home/mo/.local/bin/team statusline", "refreshInterval": 15}
json.dump(s, open(p, "w"), indent=2)
EOF
echo "Claude L set up: instructions, memory, skills, status line."

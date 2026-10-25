"""ClaudeCom: the two Claude sessions (W = Windows desktop app, L = WSL) share ClaudeCom.md.

  python docs/tools/claudecom.py say "message"    append a chat line (keeps the last 12)
  python docs/tools/claudecom.py beat [state]     refresh own heartbeat (state: working/idle/out)
  python docs/tools/claudecom.py hook             Claude Code hook (SessionStart, UserPromptSubmit, PostToolUse)

The hook refreshes this side's heartbeat at most every 5 minutes, shows the other side's new chat lines, and says
when the other side has gone quiet with an open goal so this side takes over.
"""
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COM = os.path.join(ROOT, "ClaudeCom.md")
ME = "W" if sys.platform == "win32" else "L"
OTHER = "L" if ME == "W" else "W"
SEEN = os.path.join(ROOT, ".claude", f"claudecom-seen-{ME}.json")
FMT = "%Y-%m-%d %H:%M %z"
CHAT_KEEP = 12
BEAT_EVERY = 5 * 60
QUIET_AFTER = 25 * 60
NAG_EVERY = 30 * 60


def now():
    return dt.datetime.now().astimezone()


def read():
    with open(COM, encoding="utf-8") as f:
        return f.read()


def write(text):
    tmp = COM + f".{ME}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, COM)


def section(text, who):
    m = re.search(rf"^## Claude {who}\b.*?(?=^## |\Z)", text, re.S | re.M)
    return m.group(0) if m else ""


def field(block, name):
    m = re.search(rf"^{name}:\s*(.*)$", block, re.M)
    return m.group(1).strip() if m else ""


def set_beat(text, state=None):
    block = section(text, ME)
    if not block:
        return text
    new = re.sub(r"^Heartbeat:.*$", "Heartbeat: " + now().strftime(FMT), block, count=1, flags=re.M)
    if state:
        new = re.sub(r"^State:.*$", "State: " + state, new, count=1, flags=re.M)
    return text.replace(block, new)


def chat_lines(text):
    m = re.search(r"^## Chat.*?$\n(.*)", text, re.S | re.M)
    body = m.group(1) if m else ""
    return [l for l in body.splitlines() if l.startswith("- ")]


def say(msg):
    text = read()
    lines = chat_lines(text) + [f"- {now().strftime('%m-%d %H:%M')} {ME}: {msg.strip()}"]
    head = re.split(r"^## Chat.*$", text, flags=re.M)[0].rstrip()
    write(set_beat(head + "\n\n## Chat (newest last, last 12 kept)\n" + "\n".join(lines[-CHAT_KEEP:]) + "\n"))


def load_seen():
    try:
        with open(SEEN, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_seen(seen):
    os.makedirs(os.path.dirname(SEEN), exist_ok=True)
    with open(SEEN, "w", encoding="utf-8") as f:
        json.dump(seen, f)


def hook():
    try:
        event = json.load(sys.stdin).get("hook_event_name", "PostToolUse")
    except ValueError:
        event = "PostToolUse"
    if not os.path.exists(COM):
        return
    seen, t = load_seen(), now().timestamp()
    text = read()
    if t - seen.get("beat", 0) >= BEAT_EVERY:
        mine = section(text, ME)
        state = field(mine, "State")
        write(set_beat(text, "working" if state in ("", "out", "not started") else None))
        seen["beat"] = t
        text = read()
    notes = []
    theirs = [l for l in chat_lines(text) if re.match(rf"- \S+ \S+ {OTHER}:", l)]
    new = [l for l in theirs if l not in seen.get("chat", [])]
    if new and event != "SessionStart":
        notes.append(f"Claude {OTHER} wrote in ClaudeCom.md:\n" + "\n".join(new))
    seen["chat"] = theirs[-CHAT_KEEP:]
    other = section(text, OTHER)
    beat, state, goal = field(other, "Heartbeat"), field(other, "State"), field(other, "Goal")
    try:
        quiet = t - dt.datetime.strptime(beat, FMT).timestamp()
    except ValueError:
        quiet = None
    if (quiet is not None and quiet > QUIET_AFTER and state == "working" and goal not in ("", "-", "—")
            and t - seen.get("nag", 0) > NAG_EVERY):
        notes.append(f"Claude {OTHER} has been silent {int(quiet // 60)} min with an open goal ({goal}). Per ClaudeCom.md: "
                     f"set its State to out, move its goal and Next steps into your section, say TAKEOVER in Chat, continue.")
        seen["nag"] = t
    if event == "SessionStart":
        notes.insert(0, f"You are Claude {ME}. ClaudeCom.md now:\n" + text)
    save_seen(seen)
    if notes:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": "\n\n".join(notes)}}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "hook"
    if cmd == "say":
        say(" ".join(sys.argv[2:]))
    elif cmd == "beat":
        write(set_beat(read(), sys.argv[2] if len(sys.argv) > 2 else None))
    else:
        hook()

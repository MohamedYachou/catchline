# Generates Mira's tutorial voice lines with Kokoro (voice af_heart, Mo's pick 10-26).
# Run: /home/mo/.venvs/kokoro/bin/python docs/tools/mira_voice.py
# Each line is saved as Assets/Resources/Audio/Voice/Mira/<fnv1a32 of the shown text>.wav; VoyageTutorial plays it
# by the same hash, so editing a line only needs this script re-run. Model files: ~/.cache/kokoro-model/.
import re, os, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'Assets/Scripts/Game/VoyageTutorial.cs')
OUT = os.path.join(ROOT, 'Assets/Resources/Audio/Voice/Mira')
# Interpolations in the C# strings, as the player sees them.
VALUES = {'{GameData.SkiffCost:N0}': '500'}
def fnv(text):
    h = 0x811c9dc5
    for b in text.encode('utf-8'): h = ((h ^ b) * 0x01000193) & 0xffffffff
    return f'{h:08x}'
src = open(SRC, encoding='utf-8').read()
lines = []
for m in re.finditer(r'return \("(\w+)", \$?"((?:[^"\\]|\\.)*)"', src):
    text = m.group(2)
    for k, v in VALUES.items(): text = text.replace(k, v)
    if '{' in text: sys.exit('unresolved interpolation: ' + text)
    lines.append(text)
k = Kokoro(os.path.expanduser('~/.cache/kokoro-model/kokoro-v1.0.onnx'), os.path.expanduser('~/.cache/kokoro-model/voices-v1.0.bin'))
os.makedirs(OUT, exist_ok=True)
for text in lines:
    audio, sr = k.create(text, voice='af_heart', speed=1.0, lang='en-us')
    audio = audio / max(1e-6, np.abs(audio).max()) * .89  # -1 dBFS peak
    path = os.path.join(OUT, fnv(text) + '.wav'); sf.write(path, audio, sr, subtype='PCM_16')
    print(fnv(text), f'{len(audio)/sr:4.1f}s', text[:60])

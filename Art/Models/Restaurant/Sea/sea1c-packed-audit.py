import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'sea1c-V4-check.blend'))
expected=hashlib.sha256((O/'sea1-night-water-2048.png').read_bytes()).hexdigest();found=[]
for im in bpy.data.images:
 if 'sea1-night-water-2048' in im.name:
  actual=hashlib.sha256(im.packed_file.data).hexdigest();found.append({'image':im.name,'expected':expected,'packed':actual});assert actual==expected
assert found
(O/'sea1c-packed-audit.json').write_text(json.dumps({'pass':True,'images':found},indent=2));print('SEA1C PACKED TEXTURE PASS')

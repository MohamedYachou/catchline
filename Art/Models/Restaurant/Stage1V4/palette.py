"""Point picker receipt + regenerate V2 stroke grammar with V4 pigment values."""
from pathlib import Path
from PIL import Image
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];ref=R/'Art/Source/Restaurant/concepts/ui-service-desktop.png';im=Image.open(ref)
points={'shutter_blue':(610,556),'floor_lit':(786,404),'floor_midtone':(770,415),'stone_lit':(700,96),'stone_joint':(700,118),'booth_teal':(905,182),'booth_shadow':(1055,230),'sea_blue':(76,712),'sea_ripple':(720,705)}
rows=[{'part':n,'pixel_xy':p,'sRGB_hex':'#'+''.join(f'{c:02X}' for c in im.getpixel(p)[:3])} for n,p in points.items()]
# Reference pixels contain warm illumination. Cool unlit masonry and restrained navy are deliberate brief-directed adaptations.
replace={'173F57':'1D3B6E','2A6685':'1458A0','F3F0DC':'E8EDF0','E7D9BD':'A9B8CA','C58B50':'B66B32','DFB77A':'D89247','8C5A36':'653D2B','8FA6AC':'8395A8','28343B':'14263F','168F9F':'087B8D','657745':'356B32','E8DEC6':'D7E6EE','E5D5B7':'B6CEDF','EFE6D1':'ECF1ED','B0A48E':'8D9DAE','8F928D':'566C86','C7B79A':'B4C2D1','FFCB64':'FFD172','539651':'4C963B'}
src=(O.parent/'Stage1V2/paint_atlas.py').read_text()
for a,b in replace.items():src=src.replace("'"+a+"'","'"+b+"'")
exec(compile(src,str(O/'paint_atlas_v4.py'),'exec'),{'__file__':str(O/'paint_atlas_v4.py')})
(O/'palette.json').write_text(json.dumps({'reference':str(ref.relative_to(R)),'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'point_picker':rows,'adaptations':'Samples are final lit illustration pixels. Atlas base pigments are adapted to cool stone/navy per brief, not falsely claimed as direct unlit samples.','atlas_replacements':replace},indent=2))

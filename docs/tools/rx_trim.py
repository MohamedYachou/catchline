# Trims fully transparent margins off exact pieces whose canvas Codex padded (keeps the art untouched).
import sys
from PIL import Image
for p in sys.argv[1:]:
    im = Image.open(p); box = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    if box and box != (0, 0) + im.size: im.crop(box).save(p); print(p, im.size, '->', box)

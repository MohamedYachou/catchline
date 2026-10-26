# Codex 1's restaurant-outfit busts (clothes/2d/*-bust.png) -> square, bottom-centred rc-bust-*.png for the staff cards.
from PIL import Image; import glob, os, sys
src=r'C:\Users\momoy\Projects\Catchline\Art\Source\Restaurant\clothes\2d'; dst=r'C:\Users\momoy\Projects\Catchline\Assets\Art\UI'
for f in glob.glob(src+r'\*-bust.png'):
    im=Image.open(f).convert('RGBA'); s=max(im.size); c=Image.new('RGBA',(s,s),(0,0,0,0))
    c.paste(im,((s-im.width)//2,s-im.height),im)
    c.save(os.path.join(dst,'rc-bust-'+os.path.basename(f)[:-9]+'.png')); print(os.path.basename(f))

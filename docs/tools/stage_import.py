# Imports Codex 2's later restaurant rooms (Art/Models/Restaurant/Stage2Bistro..Stage4Seafood) into
# Assets/Resources/Restaurant as <room>.fbx (meta cloned from Stage1V4: same atlas material remap) plus
# <room>-cameras.json / <room>-lighting.json, which RestaurantWorld.StageRecipe reads. Usage: stage_import.py [room...]
import os, re, shutil, sys, uuid
R='/mnt/c/Users/momoy/Projects/Catchline/'
SRC=R+'Art/Models/Restaurant/'; DST=R+'Assets/Resources/Restaurant/'
tmpl=open(DST+'Stage1V4.fbx.meta',newline='').read()
def meta(path,body):
    if not os.path.exists(path+'.meta'):
        open(path+'.meta','w',newline='').write(re.sub(r'guid: [0-9a-f]{32}','guid: '+uuid.uuid4().hex,body,count=1))
def copy(src,dst):
    shutil.copyfile(src,dst+'.tmp'); os.replace(dst+'.tmp',dst)
flags=[a for a in sys.argv[1:] if a.startswith('--')]
for room in [a for a in sys.argv[1:] if not a.startswith('--')] or ['Stage2Bistro','Stage3Restaurant','Stage4Seafood']:
    copy(SRC+room+'/'+room+'.fbx',DST+room+'.fbx')
    # The FBX meta is V4's importer settings with this room's own guid. Rooms exported without FBX_SCALE_UNITS (the
    # first Stage2Bistro) need the file's scale: pass --file-scale.
    m=DST+room+'.fbx.meta'; guid=re.search(r'guid: ([0-9a-f]{32})',open(m).read()).group(1) if os.path.exists(m) else uuid.uuid4().hex
    body=re.sub(r'guid: [0-9a-f]{32}','guid: '+guid,tmpl,count=1)
    if '--file-scale' in flags: body=body.replace('useFileScale: 0','useFileScale: 1')
    open(m,'w',newline='').write(body)
    for src,suffix in (('final-cameras.json','-cameras'),('lighting.json','-lighting')):
        d=DST+room+suffix+'.json'; copy(SRC+room+'/'+src,d)
        meta(d,'fileFormatVersion: 2\nguid: 00000000000000000000000000000000\nTextScriptImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
    print('imported',room)

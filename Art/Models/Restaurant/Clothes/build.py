"""Restaurant workwear; unchanged source identity meshes and CrewRig skeleton/actions."""
import bpy,sys,math,json,hashlib,importlib.util,shutil
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('town',str(R/'Art/Source/Townsfolk/build.py'));T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T)
PALETTE={**T.P,'R_Navy':'#173F57','R_Ivory':'#F3F0DC','R_Teal':'#267F83','R_Gold':'#E6AD38','R_Black':'#28353D','R_Wine':'#793E49'}
JOBS=[('Host_Mira','Mira-sol','Mira','Reception','dress'),('Cook_Dirk','Dirk','Dirk','Cook','chef'),('Server_Ana','Ana','Ana','Waiter','skirt'),('Barista_Ines','Ines','Ines','Barista','skirt'),('Handyman_Olaf','Olaf','Olaf','Handyman','suit'),('Helper_Captain','Captain','Captain','Helper','suit'),('PrepCook_Dirk','Dirk','Dirk','Cook support, not a separate live enum','prep'),('Dishwasher_Olaf','Olaf','Olaf','Helper support, not a separate live enum','dish')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def signature(o):return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
def triangle(s,vs,col,bone='Spine'):
 s.part('add',vs,[(0,1,2)],col,bone=bone)
def build(row):
 name,folder,person,job,style=row;src=R/'Art/Models/CrewV2'/folder/(person+'.blend')
 bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.preferences.filepaths.save_version=0
 textures=[];tex=O/'textures';tex.mkdir(exist_ok=True)
 for im in bpy.data.images:
  if im.source!='FILE':continue
  original=Path(bpy.path.abspath(im.filepath));dest=tex/(person+'_'+original.name)
  if not original.is_file():original=src.parent/Path(im.filepath.replace('\\','/')).name
  assert original.is_file(),(person,im.name,str(original))
  shutil.copy2(original,dest);im.filepath=str(dest);im.reload();assert im.size[0]>0
  im.pack();textures.append({'image':im.name,'path':str(dest.relative_to(O)),'sha256':sha(dest),'dimensions':list(im.size),'packed':bool(im.packed_file)})
 rig=bpy.data.objects['CrewRig'];rig.animation_data_clear();rig.data.pose_position='REST'
 keep=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(person+'_Face') or 'Expression' in o.name or o.name.startswith(person+'_Hair'))]
 assert len(keep)==3,[o.name for o in keep]
 sig={o.name:signature(o) for o in keep}
 for o in list(bpy.data.objects):
  if o!=rig and o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 # Exact visible face/hair retained; only add a crown behind the original locks after removing sea hats.
 T.H.PALETTE.update(PALETTE);T.H.PALETTE['R_Hair']='#50392E'
 for n,c in T.H.PALETTE.items():T.H.MATERIALS[n]=T.H.material(n,c)
 skin=next(m for o in keep for m in o.data.materials if m and ('Skin' in m.name or 'Face' in m.name))
 # Source face textures are unchanged. Match hand colour to this character's existing body skin palette.
 SKIN={'Mira':'#D5A077','Dirk':'#C68F63','Ana':'#B67C52','Ines':'#D8AA87','Olaf':'#D4AB85','Captain':'#D0A176'}
 T.H.MATERIALS['M_Skin']=bpy.data.materials.get('M_SkinMira' if person=='Mira' else 'M_SkinCrew') or T.H.material('Restaurant_'+person+'_Hands', '#E3C3A4' if person=='Ana' else SKIN[person])
 haircols={'Mira':'#50392E','Dirk':'#684C35','Ana':'#332B29','Ines':'#C9C4A8','Olaf':'#A2AAA5','Captain':'#705035'}
 T.H.MATERIALS['R_Hair']=next(m for o in keep if o.name.startswith(person+'_Hair') for m in o.data.materials if m)
 s=T.Skin(rig);base='R_Navy' if style=='dress' else ('R_Ivory' if style in ['chef','prep','dish','skirt'] else 'R_Navy')
 # Continuous tailored torso: shared weights at waist instead of disconnected spheres.
 rows=[(.29,.128,.093,0),(.33,.135,.096,0),(.38,.12,.092,0),(.45,.14,.099,0),(.51,.14,.088,0),(.548,.075,.052,0)]
 seg=16;vs=[(rx*math.cos(i*math.tau/seg),cy+ry*math.sin(i*math.tau/seg),z) for z,rx,ry,cy in rows for i in range(seg)]
 fs=[(j*seg+i,j*seg+(i+1)%seg,(j+1)*seg+(i+1)%seg,(j+1)*seg+i) for j in range(len(rows)-1) for i in range(seg)]+[tuple(reversed(range(seg))),tuple(range((len(rows)-1)*seg,len(rows)*seg))]
 def bodyweights(p):
  if p.z<.43:return T.blend('Hips','Spine',(p.z-.31)/.09)
  return T.blend('Spine','Spine1',(p.z-.44)/.08)
 s.part('add',vs,fs,base,weights=bodyweights)
 female=style in ['dress','skirt']
 T.limbs(s,base,pants='M_Skin' if female else 'R_Navy',rolled=style in ['prep','dish'],boots=False)
 if not female:s.ell((0,0,.29),(.129,.088,.064),'R_Navy','Hips',seg=12,rings=4,smooth=False)
 s.ell((0,0,.566),(.048,.046,.051),'M_Skin','Neck',seg=10,rings=3)
 # Fill only the bare scalp left beneath a removed sea hat. Existing full buns need no cap.
 if person=='Ana':s.ell((0,.015,.882),(.15,.135,.078),'R_Hair','Head',seg=24,rings=8)
 if person!='Ana' and style not in ['chef','prep','dish']:
  if person=='Mira':T.H.MATERIALS['R_Hair']=next(m for o in keep if o.name.startswith(person+'_Hair') for m in o.data.materials if m)
  s.ell((0,.015,.883),(.174,.153,.088),'R_Hair','Head',seg=20,rings=7)
  # Asymmetric swept locks, following the dome rather than a row of inflated fingers.
  for k in range(3):
   z=.930+k*.009;y=-.079+k*.042
   s.part('tube',[(-.142,y,z-.023),(-.082,y-.022,z+.009),(.005,y-.011,z+.018),(.09,y+.02,z+.003),(.15,y+.06,z-.029)],[.009,.016,.020,.014,.004],8,'R_Hair',bone='Head',smooth=True)
 if style in ['dress','skirt']:
  # Hip-bound short skirt with leg-clearance; folds read at phone scale.
  color='R_Navy'
  s.lathe([(.175,.195,.19,0),(.24,.182,.16,0),(.30,.169,.111,0),(.377,.136,.104,0)],color,'Hips',segments=16)
  s.lathe([(.358,.14,.108,0),(.379,.14,.108,0)],'R_Gold' if style=='dress' else 'R_Teal','Hips',segments=16)
  for sign in [-1,1]:
   triangle(s,[(sign*.09,-.073,.527),(sign*.018,-.109,.478),(sign*.07,-.10,.447)],'R_Ivory')
  if style=='dress':
   # Gold edged tailored neckline, name pin, done-up rear bun and barrette.
   s.tube([(-.085,-.079,.522),(0,-.113,.476),(.085,-.079,.522)],[.004]*3,'R_Gold','Spine',sides=6)
   s.ell((0,.15,.91),(.073,.053,.073),'R_Hair','Head',seg=12,rings=5)
   s.box((0,.191,.92),(.087,.009,.012),'R_Gold','Head')
   for sign in [-1,1]:s.ell((sign*.173,-.012,.718),(.009,.009,.018),'R_Gold','Head',seg=8,rings=3)
  else:
   # Smart ivory blouse / navy waistcoat, no front-of-house apron.
   for sign in [-1,1]:triangle(s,[(sign*.123,-.059,.506),(sign*.021,-.111,.428),(sign*.122,-.079,.35)],'R_Navy')
   s.ell((0,-.115,.485),(.027,.012,.014),'R_Teal','Spine',seg=8,rings=3)
 elif style in ['chef','prep','dish']:
  # Broad double-breasted coat, white rolled cuffs and readable dark buttons.
  for x in [-.04,.04]:
   for z in [.395,.442,.486]:s.ell((x,-.101,z),(.006,.006,.006),'R_Navy','Spine',seg=6,rings=2)
  s.lathe([(.519,.06,.055,0),(.547,.058,.054,0)],'R_Ivory','Neck',segments=12)
  if style in ['chef','prep']:
   s.lathe([(.906,.153,.14,0),(.948,.153,.14,0),(.96,.15,.138,0)],'R_Ivory','Head',segments=16)
   s.ell((0,.005,1.008),(.161,.146,.087),'R_Ivory','Head',seg=12,rings=5)
   for x in [-.09,-.045,0,.045,.09]:s.tube([(x,-.13,.953),(x,-.125,1.033)],[.003,.003],'R_Navy','Head',sides=4)
  else:
   # Kitchen-only tidy cap, no tall toque for the washing-up role.
   s.ell((0,.01,.949),(.165,.145,.047),'R_Ivory','Head',seg=12,rings=4)
  if style in ['prep','dish']:
   s.box((0,-.106,.30),(.224,.014,.18),'R_Teal','Hips')
   s.box((0,-.107,.43),(.151,.016,.12),'R_Teal','Spine')
   for sign in [-1,1]:s.tube([(sign*.064,-.105,.46),(sign*.08,-.061,.523)],[.009,.009],'R_Teal','Spine',sides=5)
   s.box((0,-.118,.31),(.096,.009,.046),'R_Navy','Hips')
 else:
  # Jacket/waistcoat over ivory shirt and proper bow/tie. No utility overalls.
  s.ell((0,-.088,.458),(.057,.02,.075),'R_Ivory','Spine',seg=10,rings=3)
  for sign in [-1,1]:
   triangle(s,[(sign*.114,-.064,.515),(sign*.018,-.113,.409),(sign*.075,-.101,.465)],'R_Teal')
   triangle(s,[(sign*.052,-.097,.52),(0,-.115,.493),(sign*.029,-.116,.476)],'R_Ivory')
  s.ell((0,-.12,.481),(.029,.012,.013),'R_Wine','Spine',seg=8,rings=3)
  s.box((.074,-.094,.448),(.039,.009,.008),'R_Ivory','Spine')
 for z in [.386,.417]:s.ell((0,-.108,z),(.005,.005,.005),'R_Gold','Spine',seg=6,rings=2)
 s.box((-.074,-.091,.463),(.034,.008,.013),'R_Gold','Spine')
 outfit=s.finish(name+'_Outfit');outfit['job']=job;outfit['identity']=person
 uv=outfit.data.uv_layers.new(name='UVMap')
 for poly in outfit.data.polygons:
  for li in poly.loop_indices:
   co=outfit.data.vertices[outfit.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x+.20)/.40,(co.y+.20)/.40)
 objects=keep+[outfit];assert all(signature(o)==sig[o.name] for o in keep)
 rig['restaurant_job']=job;rig['source_identity']=person
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.context.scene.render.fps=24
 rig.animation_data_clear();rig.data.pose_position='REST'
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
 rig.data.pose_position='POSE';T.bind(rig,'Idle');bpy.context.scene.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects+[rig]:o.select_set(True)
 bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
 meshes=[]
 for o in objects:
  o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices]
  meshes.append({'name':o.name,'vertices':len(vs),'triangles':len(o.data.loop_triangles),'bounds_rest':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'weights_normalized':all(abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in o.data.vertices),'geometry_sha256':signature(o)})
 return {'asset':name,'person':person,'job':job,'style':style,'source':str(src.relative_to(R)),'source_sha256':sha(src),'textures':textures,'preserved_identity':sig,'meshes':meshes,'bones':{b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(v) for v in b.matrix_local]} for b in rig.data.bones},'actions':{a.name:list(a.frame_range) for a in bpy.data.actions},'fbx_sha256':sha(O/(name+'.fbx'))}
rows=[]
for row in JOBS:
 rows.append(build(row));print('CLOTHES EXPORTED',row[0],flush=True)
 (O/'build-metrics.json').write_text(json.dumps({'assets':rows,'metres':True,'blender_facing':'-Y','fbx_forward':'-Z','fbx_up':'Y'},indent=2))
print('CLOTHES BUILD PASS',flush=True)

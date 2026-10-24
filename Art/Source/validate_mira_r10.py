"""Independent r09 preservation, reusable female field and rear-texture audit.
Run headless after validate_mira_sol.py; writes only Mira-sol/r10-validation.json.
"""
import bpy, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/CrewV2/Mira-sol';BASE=OUT/'iterations/r09'
sys.path.insert(0,str(ROOT/'Art/Source'))
from crew_female_shape import female_shape,region_for_weights,VERSION
for name,sha in json.loads((BASE/'archive-sha256.json').read_text()).items():
    assert hashlib.sha256((BASE/name).read_bytes()).hexdigest()==sha, name

def weights(ob):
    return [[(ob.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in ob.data.vertices]
def components(me):
    adj=[set() for v in me.vertices]
    for e in me.edges:
        a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    left=set(range(len(adj)));out=[]
    while left:
        seed=min(left);stack=[seed];comp={seed};left.remove(seed)
        while stack:
            for i in adj[stack.pop()]:
                if i in left:left.remove(i);comp.add(i);stack.append(i)
        out.append(comp)
    return out

def canon(me,ids):
    vv=sorted(tuple(me.vertices[i].co) for i in ids)
    ff=sorted((tuple(sorted(tuple(me.vertices[i].co) for i in p.vertices)),me.materials[p.material_index].name)
              for p in me.polygons if p.vertices[0] in ids)
    return vv,ff
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Mira.blend'))
old={o.name:{'co':[tuple(v.co) for v in o.data.vertices],'weights':weights(o)} for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Mira_')}
ob=bpy.data.objects['Mira_HairSculpt'];islands=components(ob.data)
ids=set().union(*(islands[i] for i in [0]+list(range(2,17))))
front=canon(ob.data,ids);frontweights=sorted((tuple(ob.data.vertices[i].co),old[ob.name]['weights'][i]) for i in ids)
frontmats={ob.data.materials[p.material_index].name for p in ob.data.polygons if p.vertices[0] in ids}
mat_values={name:tuple(bpy.data.materials[name].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value) for name in frontmats}
oldface_sha=hashlib.sha256((BASE/'Mira_Face.png').read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Mira.blend'))
manifest=json.loads((OUT/'build-manifest.json').read_text())
assert bpy.data.objects['CrewRig']['female_shape_enabled'] is True
ob=bpy.data.objects['Mira_HairSculpt'];newids=set(range(len(ids)))
assert canon(ob.data,newids)==front,'Approved front vertex/face/material changed'
newweights=weights(ob)
assert sorted((tuple(ob.data.vertices[i].co),newweights[i]) for i in newids)==frontweights
for name,value in mat_values.items():
    assert tuple(bpy.data.materials[name].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value)==value
assert hashlib.sha256((OUT/'Mira_Face.png').read_bytes()).hexdigest()==oldface_sha
changes={};maxerror=0
for name,prior in old.items():
    if name=='Mira_HairSculpt':continue
    ob=bpy.data.objects[name];assert weights(ob)==prior['weights'],name
    assert len(ob.data.vertices)==len(prior['co'])
    count=0
    for v,co,ww in zip(ob.data.vertices,prior['co'],prior['weights']):
        expected=co
        if name in {'Mira_CoatHandsBoots','Mira_JewelleryBinoculars'}:
            region=region_for_weights(dict(ww))
            if region:expected=female_shape(co,True,region)
        error=max(abs(v.co[i]-expected[i]) for i in range(3));maxerror=max(maxerror,error)
        assert error<3e-8,(name,v.index,error)
        assert v.co.z==co[2]
        if max(abs(v.co[i]-co[i]) for i in range(3))>1e-8:count+=1
        assert female_shape(co,False)==co
    changes[name]=count
# Direct reusable envelope probes: same Z, narrower waist, wider/deeper hip,
# and modest added chest depth with no effect on male flag.
probes={}
for name,co,region in [('waist',(.10,-.08,.397),'torso'),('hip',(.10,-.08,.302),'torso'),('chest',(.052,-.08,.48),'torso'),('trouser_hip',(.065,-.035,.29),'hips')]:
    out=female_shape(co,True,region);assert out[2]==co[2]
    probes[name]={'male':co,'female':out}
assert probes['waist']['female'][0]<.10
assert probes['hip']['female'][0]>.10 and probes['hip']['female'][1]<-.08
assert probes['chest']['female'][1]<-.08
hair=bpy.data.objects['Mira_HairSculpt'];assert hair.data.uv_layers.active
mat=bpy.data.materials['Mira_Hair'];im=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
assert Path(bpy.path.abspath(im.filepath)).resolve()==(OUT/'Mira_Hair.png').resolve()
assert tuple(im.size)==(512,512)
assert len({tuple(v.co) for v in hair.data.vertices if v.index>=len(ids)})>1000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OUT/'Mira.fbx'),use_anim=True)
mat=bpy.data.materials['Mira_Hair'];im=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
assert Path(bpy.path.abspath(im.filepath)).is_file()
assert hashlib.sha256(Path(bpy.path.abspath(im.filepath)).read_bytes()).hexdigest()==hashlib.sha256((OUT/'Mira_Hair.png').read_bytes()).hexdigest()
assert bpy.data.objects['Mira_HairSculpt'].data.uv_layers.active
result={'revision':manifest['revision'],'r09_archive_hashes_exact':True,'front_geometry_material_colors_weights_exact':True,
'front_vertices':len(ids),'face_texture_exact':True,'all_nonhair_weights_exact':True,'female_shape':VERSION,
'female_field_max_error_m':maxerror,'changed_vertices':changes,'all_original_vertex_z_exact':True,
'male_flag_exact_identity':True,'silhouette_probes_m':probes,'rear_uv_texture_saved_and_actual_fbx_resolve':True,
'all_passed':True}
(OUT/'r10-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS r10 preservation, female field, UV texture source/actual FBX',flush=True)
